"""Invarianti delle tabelle prodotte.

Girano solo se `dati/processed/` esiste: senza un build alle spalle vengono
saltati, così il repo resta testabile anche appena clonato.
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from brescia_pipeline.config import PROCESSED_DIR, PROVINCIA_BRESCIA_ISTAT

pytestmark = pytest.mark.skipif(
    not (PROCESSED_DIR / "comuni.csv").exists(),
    reason="nessun build eseguito: lanciare `python -m brescia_pipeline.build`",
)


def leggi(nome: str) -> list[dict[str, str]]:
    path = PROCESSED_DIR / nome
    if not path.exists():
        pytest.skip(f"{nome} non ancora costruito")
    with path.open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def codici_comuni() -> set[str]:
    return {r["codice_istat"] for r in leggi("comuni.csv")}


def test_la_provincia_ha_205_comuni() -> None:
    comuni = leggi("comuni.csv")
    assert len(comuni) == 205
    assert all(c["codice_istat"].startswith(PROVINCIA_BRESCIA_ISTAT) for c in comuni)
    assert sum(1 for c in comuni if c["capoluogo"] == "1") == 1


@pytest.mark.parametrize(
    "tabella",
    [
        "popolazione_comuni.csv",
        "imprese_classe_addetti.csv",
        "turismo_comuni_annuale.csv",
        "turismo_comuni_mensile.csv",
    ],
)
def test_ogni_codice_esiste_in_anagrafica(tabella: str) -> None:
    """Il join non deve mai perdere righe in silenzio."""
    validi = codici_comuni()
    orfani = {r["codice_istat"] for r in leggi(tabella)} - validi
    assert not orfani, f"{tabella}: codici assenti dall'anagrafica {sorted(orfani)[:5]}"


def test_popolazione_provinciale_plausibile() -> None:
    righe = [
        r
        for r in leggi("popolazione_comuni.csv")
        if r["anno"] == "2024" and r["indicatore"] == "popolazione_residente"
    ]
    totale = sum(float(r["valore"]) for r in righe)
    assert len(righe) == 205
    assert 1_200_000 < totale < 1_320_000, totale


def test_imprese_le_classi_sommano_al_totale() -> None:
    """Le quattro classi dimensionali devono ricostruire il totale."""
    righe = [
        r
        for r in leggi("imprese_classe_addetti.csv")
        if r["anno"] == "2023" and r["indicatore"] == "unita_locali"
    ]
    totale = sum(float(r["valore"]) for r in righe if r["classe_addetti"] == "totale")
    per_classe = sum(float(r["valore"]) for r in righe if r["classe_addetti"] != "totale")
    assert totale == pytest.approx(per_classe, rel=0.001)


def test_turismo_i_dati_riservati_restano_vuoti() -> None:
    """«Dato riservato» non deve mai diventare uno zero."""
    righe = [
        r
        for r in leggi("turismo_comuni_annuale.csv")
        if r["anno"] == "2024"
        and r["tipo_struttura"] == "Totale"
        and r["cittadinanza"] == "Totale"
    ]
    vuoti = [r for r in righe if r["presenze"] == ""]
    assert vuoti, "atteso almeno un comune con dato soppresso"
    assert all(r["stato"] == "riservato" for r in vuoti)
    # Nessuno zero puo' restare senza qualificazione: o e' misurato, o e'
    # calcolato su componenti soppresse ed e' marcato come tale.
    zeri = [r for r in righe if r["presenze"] == "0"]
    assert all(r["stato"] in {"osservato", "zero_fittizio"} for r in zeri)
    assert any(r["stato"] == "zero_fittizio" for r in zeri), (
        "atteso almeno uno zero fittizio: la fonte ne contiene (Gottolengo 2024)"
    )


def test_nessuna_tabella_e_vuota() -> None:
    for path in sorted(PROCESSED_DIR.glob("*.csv")):
        with path.open(encoding="utf-8") as handle:
            righe = sum(1 for _ in handle)
        assert righe > 1, f"{path.name} contiene solo l'intestazione"
