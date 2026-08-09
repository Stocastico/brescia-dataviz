"""Sicurezza: reati denunciati (provincia) e percezione (comune).

Le due facce arrivano a grane e finestre diverse — reati provinciali dal 2006,
percezione comunale dal 2022 — e non esiste alcun dato per quartiere. Restano
in due tabelle distinte proprio per non suggerire un confronto diretto che i
dati non reggono.
"""

from __future__ import annotations

from ..config import COMUNE_BRESCIA, PROVINCIA_BRESCIA_SDMX
from ..fetch import sdmx_csv
from ..tidy import fmt, read_sdmx, split_code, to_number, write_csv

REATI = "73_67_DF_DCCV_DELITTIPS_9"  # tasso di delittuosità, province
PERCEZIONE = {
    "sicurezza_al_buio": "DF_DCSS_BEST_PPC_6_GC",
    "rischio_criminalita": "DF_DCSS_BEST_PPC_1_GC",
    "soddisfazione_vita": "DF_DCSS_BEST_PPC_2_GC",
}

REATI_COLUMNS = ["territorio", "anno", "indicatore", "tipo_reato", "codice_reato", "valore"]
PERCEZIONE_COLUMNS = ["tavola", "territorio", "anno", "sesso", "modalita", "codice_modalita", "valore"]

# La dimensione che porta la risposta cambia da tavola a tavola.
MODALITA = ["PERC_SAF_WAD", "PERC_CRIME_RISK", "LIFE_SATISF"]


def _reati() -> list[dict[str, str]]:
    # Serie nazionale: supera i 120 MB, quindi la cache di `dati/raw/` qui
    # vale piu' che altrove.
    path = sdmx_csv(REATI, dest_name="istat_reati_province.csv")
    rows = []
    for record in read_sdmx(path):
        area, _ = split_code(record.get("REF_AREA", ""))
        if area != PROVINCIA_BRESCIA_SDMX:
            continue
        value = to_number(record.get("OBS_VALUE"))
        if value is None:
            continue
        reato_code, reato_label = split_code(record.get("TYPE_CRIME", ""))
        rows.append(
            {
                "territorio": area,
                "anno": record.get("TIME_PERIOD", ""),
                "indicatore": split_code(record.get("DATA_TYPE", ""))[1],
                "tipo_reato": reato_label,
                "codice_reato": reato_code,
                "valore": fmt(value, 2),
            }
        )
    return rows


def _percezione() -> list[dict[str, str]]:
    rows = []
    for tavola, dataflow in PERCEZIONE.items():
        path = sdmx_csv(dataflow, dest_name=f"istat_percezione_{tavola}.csv")
        for record in read_sdmx(path):
            area, _ = split_code(record.get("REF_AREA", ""))
            if area not in (COMUNE_BRESCIA, PROVINCIA_BRESCIA_SDMX):
                continue
            value = to_number(record.get("OBS_VALUE"))
            if value is None:
                continue
            for dim in MODALITA:
                if dim not in record or not record[dim]:
                    continue
                code, label = split_code(record[dim])
                rows.append(
                    {
                        "tavola": tavola,
                        "territorio": area,
                        "anno": record.get("TIME_PERIOD", ""),
                        "sesso": split_code(record.get("GENDER", ""))[1],
                        "modalita": label,
                        "codice_modalita": code,
                        "valore": fmt(value, 1),
                    }
                )
    return rows


def build(comuni: dict[str, str]) -> None:
    reati = _reati()
    reati.sort(key=lambda r: (r["anno"], r["indicatore"], r["codice_reato"]))
    write_csv("reati_provincia.csv", reati, REATI_COLUMNS)

    percezione = _percezione()
    percezione.sort(key=lambda r: (r["tavola"], r["territorio"], r["anno"], r["codice_modalita"]))
    write_csv("percezione_sicurezza.csv", percezione, PERCEZIONE_COLUMNS)
