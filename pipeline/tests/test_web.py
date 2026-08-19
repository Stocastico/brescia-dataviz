"""Gli invarianti del contratto fra pipeline e sito.

Sono i cinque di `PROSSIMI-PASSI.md` §6.2, scritti come test perché è l'unico
modo in cui un contratto resta vero: il frontend non ha modo di accorgersi che
un codice comune non esiste nella geometria — disegna semplicemente un comune
in meno, e nessuno se ne accorge per mesi.

Girano solo se `web/src/data/` è stata costruita (`build web`).
"""

from __future__ import annotations

import json

import pytest

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


def test_il_manifesto_elenca_le_tabelle() -> None:
    manifesto = json.loads((WEB_DATA_DIR / "manifest.json").read_text(encoding="utf-8"))
    assert manifesto["comuni"] == 205
    assert "comuni_sintesi.csv" in manifesto["tabelle"]
    assert manifesto["indicatori"] == len(registro())
