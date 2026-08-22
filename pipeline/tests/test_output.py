"""Invarianti delle tabelle prodotte.

Girano solo se `dati/processed/` esiste: senza un build alle spalle vengono
saltati, così il repo resta testabile anche appena clonato.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from brescia_pipeline.config import PROCESSED_DIR, PROVINCIA_BRESCIA_ISTAT
from brescia_pipeline.datasets.confini import GEOJSON_PATH

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
        "famiglie_comuni.csv",
        "abitazioni_comuni.csv",
        "migrazioni_comuni.csv",
        "bilancio_demografico_comuni.csv",
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


def test_ogni_comune_ha_la_sua_geometria() -> None:
    """Invariante 1 di PROSSIMI-PASSI §6.2: nessun codice senza geometria."""
    geojson = GEOJSON_PATH
    if not geojson.exists():
        pytest.skip("confini non ancora costruiti")
    features = json.loads(geojson.read_text(encoding="utf-8"))["features"]
    assert {f["id"] for f in features} == codici_comuni()
    assert len(features) == 205


def test_la_geometria_e_in_gradi_e_cade_nel_bresciano() -> None:
    """Metri UTM passati per gradi disegnerebbero la provincia nell'oceano."""
    righe = leggi("comuni_geometria.csv")
    lon = [float(r["centroide_lon"]) for r in righe]
    lat = [float(r["centroide_lat"]) for r in righe]
    assert 9.7 < min(lon) and max(lon) < 11.0
    assert 45.1 < min(lat) and max(lat) < 46.5


def test_la_superficie_provinciale_e_quella_nota() -> None:
    """La provincia misura 4.785,6 km²: uno scarto grosso è un errore di area."""
    totale = sum(float(r["area_kmq"]) for r in leggi("comuni_geometria.csv"))
    assert totale == pytest.approx(4785.6, rel=0.001)


def test_nessuna_area_e_nulla_o_negativa() -> None:
    for riga in leggi("comuni_geometria.csv"):
        assert float(riga["area_kmq"]) > 0, riga["comune"]


def test_nessuna_tabella_e_vuota() -> None:
    for path in sorted(PROCESSED_DIR.glob("*.csv")):
        with path.open(encoding="utf-8") as handle:
            righe = sum(1 for _ in handle)
        assert righe > 1, f"{path.name} contiene solo l'intestazione"


# --- il bilancio demografico --------------------------------------------


def componenti_bilancio(righe: list[dict[str, str]], chiave: str) -> dict[str, dict[str, float]]:
    conti: dict[str, dict[str, float]] = {}
    for riga in righe:
        if not riga["valore"]:
            continue
        per_territorio = conti.setdefault(riga[chiave], {})
        indicatore = riga["indicatore"]
        per_territorio[indicatore] = per_territorio.get(indicatore, 0.0) + float(riga["valore"])
    return conti


def test_il_bilancio_ricostruisce_la_popolazione_del_censimento() -> None:
    """L'identità contabile, verificata sulla tabella scritta e non solo in memoria.

    È il controllo che rende la scomposizione una scomposizione: se non chiude,
    resta un residuo che qualcuno prima o poi attribuirà a un fenomeno.
    """
    righe = leggi("bilancio_demografico_comuni.csv")
    for codice, conti in componenti_bilancio(righe, "codice_istat").items():
        ricostruito = (
            conti["popolazione_inizio"]
            + conti["nati"] - conti["morti"]
            + conti["immigrati_interni"] - conti["emigrati_interni"]
            + conti["immigrati_estero"] - conti["emigrati_estero"]
            + conti.get("variazioni_territoriali", 0.0)
            + conti["aggiustamento_statistico"]
        )
        assert abs(ricostruito - conti["popolazione_censita"]) < 0.5, codice


def test_la_popolazione_censita_del_bilancio_e_quella_del_censimento() -> None:
    """Le due tabelle parlano della stessa popolazione, non di due popolazioni.

    È la condizione che permette di scomporre `popolazione_comuni.csv` con i
    flussi di un'altra fonte senza inventare un residuo.
    """
    censimento = {
        (r["codice_istat"], r["anno"]): float(r["valore"])
        for r in leggi("popolazione_comuni.csv")
        if r["indicatore"] == "popolazione_residente" and r["valore"]
    }
    confrontate = 0
    for riga in leggi("bilancio_demografico_comuni.csv"):
        if riga["indicatore"] != "popolazione_censita" or not riga["valore"]:
            continue
        atteso = censimento.get((riga["codice_istat"], riga["anno"]))
        if atteso is None:
            continue
        assert abs(float(riga["valore"]) - atteso) < 0.5, riga
        confrontate += 1
    assert confrontate > 1000, f"solo {confrontate} confronti: la finestra non si sovrappone"


def test_le_province_del_bilancio_sono_tutte_e_107() -> None:
    righe = leggi("bilancio_province.csv")
    codici = {r["codice_provincia"] for r in righe}
    assert len(codici) == 107
    assert all(len(c) == 3 for c in codici)


def test_la_provincia_di_brescia_e_la_somma_dei_suoi_comuni() -> None:
    """Le due tabelle si controllano a vicenda: stessa fonte, due aggregazioni."""
    comuni = componenti_bilancio(leggi("bilancio_demografico_comuni.csv"), "codice_istat")
    province = componenti_bilancio(leggi("bilancio_province.csv"), "codice_provincia")
    for indicatore in ("nati", "morti", "immigrati_estero", "popolazione_censita"):
        somma = sum(c[indicatore] for c in comuni.values())
        assert abs(somma - province[PROVINCIA_BRESCIA_ISTAT][indicatore]) < 0.5, indicatore


def test_i_conteggi_del_bilancio_non_sono_negativi() -> None:
    """I flussi lordi sono conteggi. I saldi sarebbero negativi, ma la tabella
    non li porta: se un `nati` esce negativo, si è letta la colonna sbagliata."""
    lordi = {"nati", "morti", "immigrati_interni", "emigrati_interni",
             "immigrati_estero", "emigrati_estero", "popolazione_inizio",
             "popolazione_fine", "popolazione_censita"}
    for tabella in ("bilancio_demografico_comuni.csv", "bilancio_province.csv"):
        for riga in leggi(tabella):
            if riga["indicatore"] in lordi and riga["valore"]:
                assert float(riga["valore"]) >= 0, f"{tabella}: {riga}"
