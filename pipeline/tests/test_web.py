"""Gli invarianti del contratto fra pipeline e sito.

Sono i cinque di `PROSSIMI-PASSI.md` §6.2, scritti come test perché è l'unico
modo in cui un contratto resta vero: il frontend non ha modo di accorgersi che
un codice comune non esiste nella geometria — disegna semplicemente un comune
in meno, e nessuno se ne accorge per mesi.

Girano solo se `web/src/data/` è stata costruita (`build web`).
"""

from __future__ import annotations

import csv
import json

import pytest

from brescia_pipeline.config import PROCESSED_DIR, TABELLE_NON_VERSIONATE
from brescia_pipeline.datasets.confini import GEOJSON_PATH
from brescia_pipeline.web import WEB_DATA_DIR

pytestmark = pytest.mark.skipif(
    not (WEB_DATA_DIR / "metrics.json").exists(),
    reason="nessun export per il sito: lanciare `python -m brescia_pipeline.build web`",
)

KIND_AMMESSI = {"sequential", "diverging", "categorical"}
CONFIDENZE_AMMESSE = {"osservato", "derivato", "proxy"}
# Indicatori che possono essere negativi per costruzione: sono variazioni.
NEGATIVI_LECITI = {"diverging"}


def registro() -> list[dict]:
    return json.loads((WEB_DATA_DIR / "metrics.json").read_text(encoding="utf-8"))


def indicatore(id_metrica: str) -> dict:
    return json.loads((WEB_DATA_DIR / f"metric_{id_metrica}.json").read_text(encoding="utf-8"))


def codici_geometria() -> set[str]:
    geo = json.loads(GEOJSON_PATH.read_text(encoding="utf-8"))
    return {f["properties"]["codice_istat"] for f in geo["features"]}


def ids() -> list[str]:
    return [r["id"] for r in registro()]


@pytest.fixture(params=ids())
def metrica(request) -> dict:
    return indicatore(request.param)


def test_ogni_codice_esiste_nella_geometria(metrica) -> None:
    # Invariante 1. Un codice senza geometria è un comune che la mappa perde
    # in silenzio, ed è il modo classico di sbagliare un join.
    assert set(metrica["values"]) <= codici_geometria()


def test_ogni_indicatore_live_ha_il_suo_file() -> None:
    # Invariante 2, primo verso.
    for riga in registro():
        if riga["status"] != "live":
            continue
        assert (WEB_DATA_DIR / f"metric_{riga['id']}.json").exists()


def test_ogni_file_e_nel_registro() -> None:
    # Invariante 2, secondo verso: un file orfano è un indicatore che nessuno
    # può selezionare, cioè lavoro buttato.
    su_disco = {p.stem.removeprefix("metric_") for p in WEB_DATA_DIR.glob("metric_*.json")}
    assert su_disco == set(ids())


def test_i_periodi_sono_ordinati_e_senza_duplicati(metrica) -> None:
    # Invariante 3.
    periodi = metrica["periods"]
    assert periodi == sorted(periodi)
    assert len(periodi) == len(set(periodi))


def test_i_conteggi_non_sono_negativi(metrica) -> None:
    # Invariante 4, ristretto a ciò che non può esserlo: una variazione
    # negativa è normale, un conteggio negativo è un errore di lettura.
    if metrica["kind"] in NEGATIVI_LECITI:
        pytest.skip("è una variazione: il segno negativo ha senso")
    for per_comune in metrica["values"].values():
        for valore in per_comune.values():
            assert valore is None or valore >= 0


def test_le_chiavi_dei_valori_stanno_nei_periodi(metrica) -> None:
    # Invariante 5.
    periodi = set(metrica["periods"])
    for per_comune in metrica["values"].values():
        assert set(per_comune) <= periodi


def test_il_descrittore_e_completo(metrica) -> None:
    for campo in ("id", "label", "unit", "kind", "livello", "theme", "source", "confidence"):
        assert metrica[campo], f"manca {campo}"
    assert metrica["kind"] in KIND_AMMESSI
    assert metrica["confidence"] in CONFIDENZE_AMMESSE
    # Un derivato senza assunzioni dichiarate è un derivato che finge di essere
    # un'osservazione: la provenienza deve viaggiare col dato (§9 del piano).
    if metrica["confidence"] != "osservato":
        assert metrica["assumptions"]


def test_la_copertura_dichiarata_e_quella_vera(metrica) -> None:
    osservazioni = sum(len(v) for v in metrica["values"].values())
    assert metrica["coverage"]["osservazioni"] == osservazioni
    assert metrica["coverage"]["comuni"] == len(metrica["values"])


def test_i_valori_assenti_non_diventano_zeri() -> None:
    # Sulle presenze 2024 mancano 73 comuni su 205 per tre motivi diversi
    # (MET-3): devono restare fuori dal JSON, non entrarci come zero.
    metrica = indicatore("presenze_turistiche")
    con_dato_2024 = [c for c, v in metrica["values"].items() if "2024" in v]
    assert len(con_dato_2024) == 132


# Gli indicatori di crescita portano l'intervallo **nel nome** — «Crescita
# degli addetti, 2018–2023» — e quel nome è scritto a mano in `web.py` mentre
# l'intervallo lo decidono i dati. Sono la stessa cosa detta due volte, quindi
# possono divergere: il giorno che ASIA pubblica il 2024, l'etichetta continua
# a dire 2023 e nessuno se ne accorge, perché la mappa si disegna lo stesso.
CRESCITE = ("crescita_addetti", "crescita_popolazione", "crescita_reddito",
            "variazione_prezzo_reale")


@pytest.mark.parametrize("id_metrica", CRESCITE)
def test_letichetta_di_una_crescita_dice_gli_anni_che_copre(id_metrica: str) -> None:
    metrica = indicatore(id_metrica)
    # Il periodo di una crescita è uno solo, ed è l'intervallo: «2018–2023».
    assert len(metrica["periods"]) == 1
    intervallo = metrica["periods"][0]
    assert intervallo in metrica["label"], (
        f"{id_metrica}: l'etichetta dice {metrica['label']!r} e i dati coprono {intervallo!r}"
    )

    # E l'intervallo dichiarato deve essere quello che i comuni hanno davvero:
    # un comune che entra o esce dalla fonte a metà accorcerebbe il suo tasso
    # senza che il nome cambi.
    primo, ultimo = intervallo.replace("\u2013", "-").split("-")
    fonte = indicatore(SORGENTE_DELLE_CRESCITE[id_metrica])
    anni_veri = sorted(
        anno
        for per_comune in fonte["values"].values()
        for anno, valore in per_comune.items()
        if valore is not None
    )
    assert (anni_veri[0], anni_veri[-1]) == (primo, ultimo)


# Da quale serie di livello si ricava ciascuna crescita.
SORGENTE_DELLE_CRESCITE = {
    "crescita_addetti": "addetti",
    "crescita_popolazione": "popolazione",
    "crescita_reddito": "reddito_medio",
    "variazione_prezzo_reale": "prezzo_case",
}


def test_il_manifesto_elenca_le_tabelle() -> None:
    manifesto = json.loads((WEB_DATA_DIR / "manifest.json").read_text(encoding="utf-8"))
    assert manifesto["comuni"] == 205
    assert "comuni_sintesi.csv" in manifesto["tabelle"]
    assert manifesto["indicatori"] == len(registro())


def test_il_manifesto_versionato_elenca_le_tabelle_versionate() -> None:
    """Il conto «N tabelle» che il sito stampa in nove punti deve valere per
    chi clona, non per chi costruisce.

    `manifest.json` è versionato e il suo elenco si ricava da
    `dati/processed/`, che però può contenere anche l'unica tabella che git
    non porta (`config.TABELLE_NON_VERSIONATE`). Costruito sulla macchina di
    chi l'ha rigenerata il manifesto ne contava una in più, e il sito
    scriveva «40 tabelle» accanto a una cartella che ne conteneva 39. È il
    genere di divergenza che nessun test coglieva, perché quelli sul
    manifesto lo rigenerano prima di guardarlo.
    """
    manifesto = json.loads((WEB_DATA_DIR / "manifest.json").read_text(encoding="utf-8"))
    sul_disco = sorted(
        percorso.name
        for percorso in PROCESSED_DIR.glob("*.csv")
        if percorso.name not in TABELLE_NON_VERSIONATE
    )
    assert manifesto["tabelle"] == sul_disco
    assert not (set(manifesto["tabelle"]) & TABELLE_NON_VERSIONATE)


def test_le_due_liste_delle_tabelle_non_versionate_coincidono() -> None:
    """`sito/costruisci.py` è di sola libreria standard e non importa la
    pipeline, quindi la lista sta scritta due volte. Due liste che divergono
    sono peggio di una sola sbagliata: questo test le tiene insieme."""
    import costruisci as C

    assert C.TABELLE_NON_VERSIONATE == TABELLE_NON_VERSIONATE


def test_i_prezzi_delle_case_ci_sono_e_dichiarano_le_due_assenze() -> None:
    """L'asse casa entra nel contratto con due indicatori, e con l'unica
    copertura del progetto che non è di 205 comuni: **203**. Magasa e
    Valvestino non sono nella fonte OMI dal 2016, e l'interfaccia deve poterlo
    dire invece di disegnare due buchi (MET-3)."""
    # Niente skip: `quotazioni_comuni.csv` è versionata nel repository, quindi
    # se questo indicatore manca è un errore, non una tabella non costruita.
    assert "prezzo_case" in [riga["id"] for riga in registro()]

    prezzo = indicatore("prezzo_case")
    assert prezzo["unit"] == "euro/m²"
    assert prezzo["confidence"] == "osservato"
    ultimo = prezzo["periods"][-1]
    quotati = [c for c, anni in prezzo["values"].items() if anni.get(ultimo) is not None]
    assert len(quotati) == 203
    for codice in quotati:
        assert prezzo["values"][codice][ultimo] > 0

    # e l'assunzione che senza si legge il numero sbagliato (MET-19) è scritta
    assert any("lorda" in a for a in prezzo["assumptions"])

    reale = indicatore("variazione_prezzo_reale")
    assert reale["kind"] == "diverging"
    # gli stessi 203: una variazione su undici anni non sta sulla mappa di una
    # su ventuno (MET-8), quindi i due comuni usciti nel 2016 restano fuori
    assert len(reale["values"]) == 203
    assert reale["confidence"] == "derivato"
    assert any("nazionale" in a for a in reale["assumptions"])
    # ventun anni di inflazione: nel capoluogo la variazione reale è negativa
    valori = list(reale["values"]["017029"].values())
    assert valori and valori[0] < 0


def test_il_background_migratorio_e_nel_registro() -> None:
    """La decima storia disegna una coropletica, e una coropletica di questo
    progetto legge il registro: l'indicatore non è un accessorio della storia,
    è la sua condizione. Niente skip — `background_migratorio_comuni.csv` è
    versionata, quindi se manca è un errore e non una tabella non costruita."""
    assert "quota_background" in [riga["id"] for riga in registro()]

    quota = indicatore("quota_background")
    assert quota["unit"] == "%"
    assert quota["confidence"] == "derivato"
    # Tre anni, e sono quelli del censimento permanente: la finestra corta è
    # dichiarata nella storia, e qui è fissata perché non si allarghi per
    # sbaglio con una tabella rigenerata male.
    assert quota["periods"] == ["2021", "2022", "2023"]
    assert len(quota["values"]) == 205

    # La quota è stranieri più italiani per acquisizione sulla popolazione: sta
    # fra zero e cento per costruzione, e se ne esce il numeratore ha preso
    # dentro una voce che non doveva.
    for codice, per_anno in quota["values"].items():
        for anno, valore in per_anno.items():
            assert valore is not None, (codice, anno)
            assert 0.0 <= valore <= 100.0, (codice, anno, valore)


def test_le_tre_componenti_del_background_sommano_al_totale() -> None:
    """L'identità che regge `quota_background`, controllata sulla tabella e non
    sull'indicatore.

    Italiani dalla nascita più stranieri più italiani per acquisizione fa la
    popolazione residente, su **ogni** coppia comune-anno. Nove coppie hanno una
    componente non pubblicata, e l'identità chiude anche lì: quindi lì
    l'assenza è uno zero, non un valore soppresso, ed è quello che autorizza
    `web.py` a ricavare il numeratore per sottrazione.

    Se un giorno la fonte cominciasse a sopprimere i valori piccoli l'identità
    si romperebbe e la quota diventerebbe sbagliata **in silenzio**, perché
    resterebbe fra zero e cento. Questo test è l'allarme."""
    path = PROCESSED_DIR / "background_migratorio_comuni.csv"

    per_coppia: dict[tuple[str, str], dict[str, str]] = {}
    with path.open(encoding="utf-8") as handle:
        for riga in csv.DictReader(handle):
            per_coppia.setdefault((riga["codice_istat"], riga["anno"]), {})[riga["indicatore"]] = riga["valore"]

    assert per_coppia, "tabella vuota"
    rotte = []
    for chiave, voci in per_coppia.items():
        totale = voci.get("popolazione_residente")
        if not totale:
            continue
        parti = ("italiani_dalla_nascita", "stranieri", "italiani_acquisiti")
        somma = sum(int(voci[p]) for p in parti if voci.get(p))
        if somma != int(totale):
            rotte.append((chiave, totale, {p: voci.get(p) for p in parti}))
    assert not rotte, f"l'identità non chiude su {len(rotte)} coppie: {rotte[:5]}"
