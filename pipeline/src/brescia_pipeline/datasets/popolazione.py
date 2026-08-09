"""Popolazione residente e famiglie, per comune, 2018-2024.

Fonte: ISTAT Censimento permanente, `DF_DCSS_FAM_POP_TV_1`. Il censimento
permanente è annuale, non decennale: è la ragione per cui questo asse ha una
serie e non due fotografie.
"""

from __future__ import annotations

from ..fetch import sdmx_csv
from ..tidy import fmt, read_sdmx, split_code, to_number, write_csv

DATAFLOW = "DF_DCSS_FAM_POP_TV_1"

# Gli indicatori del dataflow, tradotti in nomi maneggevoli.
INDICATORI = {
    "RESPOP_AV": "popolazione_residente",
    "POPHH_AV": "popolazione_in_famiglia",
    "INST_RESPOP_AV": "popolazione_in_convivenza",
    "NPHH_AV": "famiglie",
}

COLUMNS = ["codice_istat", "comune", "anno", "indicatore", "valore"]


def build(comuni: dict[str, str]) -> None:
    # Il dataflow non si può filtrare per provincia (la dimensione è il comune),
    # e una chiave con 205 codici supera il limite di lunghezza dell'URL: si
    # scarica l'Italia intera una volta sola e si filtra qui.
    path = sdmx_csv(DATAFLOW, dest_name="istat_popolazione_comuni.csv")

    rows = []
    for record in read_sdmx(path):
        code, _ = split_code(record.get("REF_AREA", ""))
        if code not in comuni:
            continue
        indicator, _ = split_code(record.get("INDICATOR", ""))
        name = INDICATORI.get(indicator)
        if name is None:
            continue
        value = to_number(record.get("OBS_VALUE"))
        if value is None:
            continue
        rows.append(
            {
                "codice_istat": code,
                "comune": comuni[code],
                "anno": record.get("TIME_PERIOD", ""),
                "indicatore": name,
                "valore": fmt(value),
            }
        )

    rows.sort(key=lambda r: (r["codice_istat"], r["indicatore"], r["anno"]))
    write_csv("popolazione_comuni.csv", rows, COLUMNS)
