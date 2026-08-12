"""Test della trasformazione delle tavole censuarie, senza rete.

Il CSV di prova riproduce la forma reale della risposta SDMX di ISTAT — colonne
`CODICE: Etichetta`, valori `codice: etichetta`, righe di altre province — così
il test copre le tre cose che qui sbagliano davvero: il filtro territoriale, la
lettura delle intestazioni e il trattamento dei valori assenti.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from brescia_pipeline.datasets import _censimento

COMUNI = {"017029": "Brescia", "017001": "Acquafredda"}
DIMENSIONI = ["NUM_MEMB", "NUM_FR_MENB"]

INTESTAZIONE = (
    "DATAFLOW,FREQ: Frequency,REF_AREA: Territory,INDICATOR: Indicator,"
    "NUM_MEMB: Number of members,NUM_FR_MENB: Number of foreign members,"
    "TIME_PERIOD: Year,OBS_VALUE,OBS_STATUS: Observation status"
)

RIGHE = [
    "IT1:DF(1.0),A: annual,017029: Brescia,NFPHH: famiglie,N1: 1,N1: 1,2021,1234,",
    "IT1:DF(1.0),A: annual,017029: Brescia,NFPHH: famiglie,N2: 2,N1: 1,2021,567,",
    "IT1:DF(1.0),A: annual,017001: Acquafredda,NFPHH: famiglie,N1: 1,N1: 1,2021,18,",
    # altra provincia: deve sparire nel filtro
    "IT1:DF(1.0),A: annual,015146: Milano,NFPHH: famiglie,N1: 1,N1: 1,2021,99999,",
    # valore soppresso: non deve diventare uno zero
    "IT1:DF(1.0),A: annual,017001: Acquafredda,NFPHH: famiglie,N2: 2,N1: 1,2021,,C",
]


@pytest.fixture
def tavola(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    csv_path = tmp_path / "prova.csv"
    csv_path.write_text("\n".join([INTESTAZIONE, *RIGHE]) + "\n", encoding="utf-8")

    # Niente rete: la chiave non si compone dal server e il file è già lì.
    monkeypatch.setattr(_censimento.sdmx, "key", lambda dataflow, fixed: "A......")
    monkeypatch.setattr(_censimento, "sdmx_csv", lambda *a, **k: csv_path)

    return _censimento.tavola(
        "DF_DCSS_FAMIGLIE_TV_2",
        nome="almeno_uno_straniero",
        dest_name="prova.csv",
        comuni=COMUNI,
        dimensioni=DIMENSIONI,
    )


def test_tiene_solo_i_comuni_della_provincia(tavola) -> None:
    assert {r["codice_istat"] for r in tavola} == {"017029", "017001"}


def test_i_valori_soppressi_non_diventano_zeri(tavola) -> None:
    # La riga di Acquafredda con OBS_VALUE vuoto non deve comparire come 0.
    acquafredda = [r for r in tavola if r["codice_istat"] == "017001"]
    assert len(acquafredda) == 1
    assert all(r["valore"] != "0" for r in tavola)


def test_le_dimensioni_diventano_colonne_per_etichetta(tavola) -> None:
    riga = next(r for r in tavola if r["codice_istat"] == "017029" and r["num_memb"] == "2")
    assert riga["valore"] == "567"
    assert riga["indicatore"] == "famiglie"
    assert riga["tavola"] == "almeno_uno_straniero"
    assert riga["comune"] == "Brescia"
    assert riga["anno"] == "2021"


def test_le_colonne_coprono_tutte_le_chiavi(tavola) -> None:
    colonne = set(_censimento.colonne(DIMENSIONI))
    assert colonne == {
        "codice_istat", "comune", "anno", "tavola", "indicatore",
        "num_memb", "num_fr_menb", "valore",
    }
    for riga in tavola:
        assert set(riga) == colonne


def test_ordina_e_deterministico(tavola) -> None:
    prima = list(tavola)
    _censimento.ordina(prima, DIMENSIONI)
    seconda = list(tavola)
    _censimento.ordina(seconda, DIMENSIONI)
    assert prima == seconda
    assert [r["codice_istat"] for r in prima] == sorted(r["codice_istat"] for r in prima)
