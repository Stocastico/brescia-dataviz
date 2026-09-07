"""La pagina che esplora, e il patto che ha con il registro degli indicatori.

`esplora.html` è il secondo dei due artefatti previsti da `PROSSIMI-PASSI.md`
§6.1: il racconto sceglie le storie, questa pagina lascia scegliere al lettore.
Non è scritta in React e non usa maplibre — usa lo stesso `grafici.js` del
racconto, per la stessa ragione per cui il racconto non usa librerie.

I test qui sopra tengono una promessa che il codice da solo non tiene: la pagina
mostra **tutti** gli indicatori del registro, non i quindici che il racconto ha
scelto di raccontare. È la condizione che rende vera la riga «aggiungere un
dataset = un JSON in più e una riga nel registro»: se domani la pipeline
esporta un indicatore nuovo, deve comparire qui senza che nessuno tocchi il
costruttore, e se non compare questo test lo dice.
"""

from __future__ import annotations

import json
import re

import pytest

from conftest import servono_tabelle

import costruisci as C

pytestmark = servono_tabelle

SEGNAPOSTO = re.compile(r"\{\{(c:[a-z0-9_]+|BUILD_DATE|DATA_DATE|N_[A-Z]+|STILE|GRAFICI|DATI)\}\}")


def registro() -> list[dict]:
    return json.loads((C.DATI_WEB / "metrics.json").read_text(encoding="utf-8"))


def id_vivi() -> set[str]:
    return {voce["id"] for voce in registro() if voce["status"] == "live"}


@pytest.fixture(scope="module")
def contesto():
    """Le stesse due cose che `costruisci()` mette in mano a `dati_incorporati`,
    ma con tutti gli indicatori: qui si guarda la pagina che li mostra tutti."""
    import csv

    with (C.PROCESSED / "comuni.csv").open(encoding="utf-8") as handle:
        comuni = {r["codice_istat"]: r for r in csv.DictReader(handle)}
    metriche = {}
    for id_metrica in C.metriche_esplora():
        metrica = C.leggi_metrica(id_metrica)
        if metrica is not None:
            metriche[id_metrica] = metrica
    return metriche, comuni


# --- il patto con il registro --------------------------------------------


def test_la_pagina_esplora_e_fra_quelle_costruite() -> None:
    assert "esplora.html" in C.PAGINE
    assert (C.MODELLI / "esplora.html").exists()


def test_esplora_prende_tutti_gli_indicatori_vivi_del_registro() -> None:
    """Il racconto ne usa quindici perché racconta otto storie; qui il lettore
    sceglie, quindi ci devono essere tutti."""
    assert C.metriche_esplora() == sorted(id_vivi())


def test_esplora_non_mostra_meno_del_racconto() -> None:
    """Il contrappeso del test sopra: se un giorno la lista si restringesse a
    mano, un indicatore già raccontato sparirebbe dalla mappa esplorabile."""
    assert set(C.METRICHE_USATE) <= set(C.metriche_esplora())


def test_ogni_indicatore_incorporato_porta_il_suo_tema(contesto) -> None:
    """Il menù è raggruppato per tema: senza il tema nei dati, il raggruppamento
    andrebbe scritto a mano nel modello, cioè fuori dal registro."""
    dati = C.dati_incorporati(*contesto)
    for id_metrica, metrica in dati["metriche"].items():
        assert metrica.get("theme"), id_metrica


# --- la pagina costruita --------------------------------------------------


@pytest.fixture(scope="module")
def sito_costruito(tmp_path_factory):
    uscita = tmp_path_factory.mktemp("sito-esplora")
    assert C.main(["--uscita", str(uscita), "--data-build", "2026-09-07"]) == 0
    return uscita


@pytest.fixture(scope="module")
def esplora(sito_costruito) -> str:
    return (sito_costruito / "esplora.html").read_text(encoding="utf-8")


def test_esplora_e_autocontenuta_come_le_altre(esplora: str) -> None:
    assert "window.DATI=" in esplora
    assert "window.GRAFICI" in esplora
    assert "--seq-1" in esplora, "lo stile non è stato incorporato"
    assert "http://" not in esplora.replace("http://www.w3.org", ""), "una dipendenza esterna"
    assert not SEGNAPOSTO.findall(esplora)


def test_esplora_incorpora_i_valori_di_tutti_gli_indicatori(esplora: str) -> None:
    """Non basta che il menù li nomini: i valori devono essere nella pagina,
    perché non c'è nessuna `fetch()` che li vada a prendere dopo."""
    dati = json.loads(re.search(r"window\.DATI=(\{.*?\});", esplora, re.S).group(1))
    assert set(dati["metriche"]) == id_vivi()
    for id_metrica, metrica in dati["metriche"].items():
        assert metrica["values"], id_metrica


def test_ogni_pagina_rimanda_all_esplorazione() -> None:
    """Una pagina che non è nel menù è una pagina che nessuno trova."""
    for modello in C.PAGINE:
        sorgente = (C.MODELLI / modello).read_text(encoding="utf-8")
        assert "esplora.html" in sorgente, modello


def test_esplora_rimanda_indietro_al_racconto() -> None:
    sorgente = (C.MODELLI / "esplora.html").read_text(encoding="utf-8")
    for pagina in ("index.html", "metodologia.html", "dati.html"):
        assert pagina in sorgente, pagina


def test_la_pagina_dei_dati_elenca_quanti_indicatori_dice_di_avere(esplora, sito_costruito) -> None:
    """Un errore vecchio, trovato costruendo la pagina che esplora.

    `dati.html` scrive «gli N indicatori» prendendo N dal manifesto, e subito
    sotto ne elenca la tabella costruendola da `window.DATI.metriche`. Finché i
    dati incorporati erano i quindici del racconto, la pagina prometteva
    diciannove righe e ne mostrava quindici: nessuno dei due numeri era
    sbagliato, la frase falsa nasceva dal metterli vicini.
    """
    manifesto = json.loads((C.DATI_WEB / "manifest.json").read_text(encoding="utf-8"))
    testo = (sito_costruito / "dati.html").read_text(encoding="utf-8")
    dati = json.loads(re.search(r"window\.DATI=(\{.*?\});", testo, re.S).group(1))
    assert len(dati["metriche"]) == manifesto["indicatori"]
