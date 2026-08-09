"""Contribuenti e reddito complessivo per classi di importo, per comune.

Fonte: MEF — Dipartimento delle Finanze, distribuito da ISTAT via SDMX. Dà la
**distribuzione**, non solo la media: è ciò che permette di parlare di
disuguaglianza invece che di livello.
"""

from __future__ import annotations

from .. import sdmx
from ..fetch import sdmx_csv
from ..tidy import fmt, read_sdmx, split_code, to_number, write_csv

DATAFLOW = "30_1008_DF_MEF_REDDITIIRPEF_COM_2"

COLUMNS = [
    "codice_istat", "comune", "anno", "indicatore", "classe_reddito",
    "codice_classe", "valore",
]

CLASSE_DIM = "AMOUNT_CLASS"


# Quanti comuni per richiesta. La serie nazionale non filtrata supera il mezzo
# gigabyte e in pratica non arriva mai in fondo; una chiave con tutti e 205 i
# codici sfonda invece la lunghezza dell'URL (400). A blocchi si passa.
COMUNI_PER_RICHIESTA = 15


def _scarica(comuni: dict[str, str]):
    codici = sorted(comuni)
    for inizio in range(0, len(codici), COMUNI_PER_RICHIESTA):
        blocco = codici[inizio : inizio + COMUNI_PER_RICHIESTA]
        chiave = sdmx.key(DATAFLOW, {"FREQ": "A", "REF_AREA": "+".join(blocco)})
        path = sdmx_csv(
            DATAFLOW,
            chiave,
            dest_name=f"mef_redditi_{inizio:03d}.csv",
        )
        yield from read_sdmx(path)


def build(comuni: dict[str, str]) -> None:
    rows = []
    for record in _scarica(comuni):
        code, _ = split_code(record.get("REF_AREA", ""))
        if code not in comuni:
            continue
        value = to_number(record.get("OBS_VALUE"))
        if value is None:
            continue

        classe_code, classe_label = split_code(record.get(CLASSE_DIM, ""))

        rows.append(
            {
                "codice_istat": code,
                "comune": comuni[code],
                "anno": record.get("TIME_PERIOD", ""),
                "indicatore": split_code(record.get("DATA_TYPE", ""))[1],
                "classe_reddito": classe_label,
                "codice_classe": classe_code,
                "valore": fmt(value, 2),
            }
        )

    rows.sort(key=lambda r: (r["codice_istat"], r["anno"], r["indicatore"], r["codice_classe"]))
    write_csv("redditi_comuni.csv", rows, COLUMNS)
