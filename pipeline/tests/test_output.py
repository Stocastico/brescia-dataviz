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


# --- coerenza fra tabelle diverse ----------------------------------------
#
# Questi controlli non guardano una tabella per volta: prendono due tabelle che
# devono raccontare la stessa cosa e le mettono a confronto. Sono nati come
# verifiche fatte a mano durante una revisione, e stanno qui perché una
# revisione che non lascia un test dietro di sé va rifatta da capo la volta
# dopo.


def somma(righe: list[dict[str, str]], chiave, colonna: str = "valore") -> dict:
    totali: dict = {}
    for riga in righe:
        if not riga[colonna]:
            continue
        totali[chiave(riga)] = totali.get(chiave(riga), 0.0) + float(riga[colonna])
    return totali


def test_la_provincia_nelle_imprese_e_la_somma_dei_suoi_comuni() -> None:
    """`imprese_province.csv` e `imprese_classe_addetti.csv` vengono dagli stessi
    file grezzi, aggregati due volte. Devono tornare."""
    comuni = somma(
        leggi("imprese_classe_addetti.csv"),
        lambda r: (r["anno"], r["classe_addetti"], r["indicatore"]),
    )
    province = {
        (r["anno"], r["modalita"], r["indicatore"]): float(r["valore"])
        for r in leggi("imprese_province.csv")
        if r["codice_provincia"] == PROVINCIA_BRESCIA_ISTAT
        and r["dimensione"] == "classe_addetti"
        and r["valore"]
    }
    assert province, "nessuna riga di Brescia in imprese_province.csv"
    for chiave, atteso in province.items():
        assert abs(comuni.get(chiave, 0.0) - atteso) < 1, chiave


def test_le_sezioni_ateco_coprono_quasi_tutto_il_totale_asia() -> None:
    """Non devono sommare *esattamente* al totale — ASIA sopprime le celle
    piccole — ma uno scarto grosso vorrebbe dire che mancano sezioni intere."""
    sezioni = somma(
        [r for r in leggi("imprese_sezioni_comuni.csv") if r["indicatore"] == "addetti"],
        lambda r: (r["codice_istat"], r["anno"]),
    )
    totali = {
        (r["codice_istat"], r["anno"]): float(r["valore"])
        for r in leggi("imprese_classe_addetti.csv")
        if r["indicatore"] == "addetti" and r["classe_addetti"] == "totale" and r["valore"]
    }
    rapporti = [sezioni[k] / totali[k] for k in sezioni if totali.get(k)]
    assert len(rapporti) > 1000
    assert min(rapporti) > 0.95, f"un comune-anno copre solo il {min(rapporti):.1%}"
    assert max(rapporti) < 1.05


def test_il_turismo_annuale_e_la_somma_dei_dodici_mesi() -> None:
    annuale = {
        (r["codice_istat"], r["anno"]): float(r["presenze"])
        for r in leggi("turismo_comuni_annuale.csv")
        if r["tipo_struttura"] == "Totale" and r["cittadinanza"] == "Totale" and r["presenze"]
    }
    mensile: dict = {}
    quanti: dict = {}
    for riga in leggi("turismo_comuni_mensile.csv"):
        if not riga["presenze"]:
            continue
        chiave = (riga["codice_istat"], riga["mese"][:4])
        mensile[chiave] = mensile.get(chiave, 0.0) + float(riga["presenze"])
        quanti[chiave] = quanti.get(chiave, 0) + 1

    # Solo dove i dodici mesi ci sono tutti: con una serie parziale lo scarto
    # sarebbe atteso, e il test direbbe una cosa diversa da quella che intende.
    completi = [k for k in annuale if quanti.get(k) == 12]
    assert len(completi) > 300
    for chiave in completi:
        assert abs(annuale[chiave] - mensile[chiave]) < 0.5, chiave


def test_la_sintesi_non_riscrive_i_numeri_delle_tabelle() -> None:
    """`comuni_sintesi.csv` è una vista, non una fonte: ogni sua cella deve
    coincidere con la tabella da cui viene."""
    sintesi = {r["codice_istat"]: r for r in leggi("comuni_sintesi.csv")}
    fonti = [
        ("popolazione_2024", "2024",
         [r for r in leggi("popolazione_comuni.csv") if r["indicatore"] == "popolazione_residente"]),
        ("addetti_2023", "2023",
         [r for r in leggi("imprese_classe_addetti.csv")
          if r["indicatore"] == "addetti" and r["classe_addetti"] == "totale"]),
        ("unita_locali_2023", "2023",
         [r for r in leggi("imprese_classe_addetti.csv")
          if r["indicatore"] == "unita_locali" and r["classe_addetti"] == "totale"]),
    ]
    for campo, anno, righe in fonti:
        atteso = {r["codice_istat"]: r["valore"] for r in righe if r["anno"] == anno}
        for codice, riga in sintesi.items():
            if riga[campo]:
                assert abs(float(riga[campo]) - float(atteso[codice])) < 0.05, (campo, codice)


def test_gli_addetti_per_100_abitanti_sono_il_rapporto_che_dichiarano() -> None:
    for riga in leggi("comuni_sintesi.csv"):
        if not (riga["addetti_per_100_abitanti"] and riga["addetti_2023"] and riga["popolazione_2024"]):
            continue
        atteso = float(riga["addetti_2023"]) / float(riga["popolazione_2024"]) * 100
        assert abs(atteso - float(riga["addetti_per_100_abitanti"])) < 0.06, riga["comune"]


def test_le_tabelle_ambientali_dichiarano_uno_stato_noto() -> None:
    ammessi = {"osservato", "copertura_scarsa", "lettura_implausibile"}
    for tabella in ("aria_mensile.csv", "meteo_mensile.csv"):
        stati = {r["stato"] for r in leggi(tabella)}
        assert stati <= ammessi, f"{tabella}: stati sconosciuti {stati - ammessi}"
        assert "osservato" in stati


def test_la_pioggia_e_un_totale_e_la_temperatura_una_media() -> None:
    """La colonna `aggregazione` non è decorativa: se un giorno la pioggia
    uscisse come media, i totali annui crollerebbero di tre ordini di grandezza
    senza che niente fallisca."""
    per_parametro = {
        (r["parametro"], r["aggregazione"]) for r in leggi("meteo_mensile.csv")
    }
    assert ("Precipitazione", "totale") in per_parametro
    assert ("Temperatura", "media") in per_parametro
    assert len({p for p, _ in per_parametro}) == len(per_parametro), "un parametro con due aggregazioni"


def test_i_totali_annui_di_pioggia_sono_plausibili() -> None:
    """Escludendo i mesi marcati, un anno completo sta fra 250 e 3.000 mm.

    È il controllo che ha reso visibile il pluviometro di Caino: con le letture
    corrotte dentro, il massimo era 110.895 mm.
    """
    annui: dict = {}
    mesi: dict = {}
    for riga in leggi("meteo_mensile.csv"):
        if riga["parametro"] != "Precipitazione" or riga["stato"] != "osservato":
            continue
        chiave = (riga["id_sensore"], riga["mese"][:4])
        annui[chiave] = annui.get(chiave, 0.0) + float(riga["valore"])
        mesi[chiave] = mesi.get(chiave, 0) + 1

    completi = [v for k, v in annui.items() if mesi[k] == 12]
    assert len(completi) > 300
    assert 250 < min(completi), f"un anno completo con soli {min(completi):.0f} mm"
    assert max(completi) < 3000, f"un anno completo con {max(completi):.0f} mm"
