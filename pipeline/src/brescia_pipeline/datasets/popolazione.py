"""Popolazione residente e famiglie, per comune, 2018-2024.

Fonte: ISTAT Censimento permanente, `DF_DCSS_FAM_POP_TV_1`. Il censimento
permanente è annuale, non decennale: è la ragione per cui questo asse ha una
serie e non due fotografie.
"""

from __future__ import annotations

from .. import sdmx
from ..fetch import sdmx_csv
from ..tidy import fmt, read_sdmx, split_code, to_number, write_csv
from ._censimento import COMUNI_PER_RICHIESTA

DATAFLOW = "DF_DCSS_FAM_POP_TV_1"

# Gli indicatori del dataflow, tradotti in nomi maneggevoli.
INDICATORI = {
    "RESPOP_AV": "popolazione_residente",
    "POPHH_AV": "popolazione_in_famiglia",
    "INST_RESPOP_AV": "popolazione_in_convivenza",
    "NPHH_AV": "famiglie",
}

COLUMNS = ["codice_istat", "comune", "anno", "indicatore", "valore"]


def _scarica(codici: list[str]):
    for inizio in range(0, len(codici), COMUNI_PER_RICHIESTA):
        blocco = codici[inizio : inizio + COMUNI_PER_RICHIESTA]
        path = sdmx_csv(
            DATAFLOW,
            sdmx.key(DATAFLOW, {"FREQ": "A", "REF_AREA": "+".join(blocco)}),
            dest_name=f"istat_popolazione_comuni_{inizio:03d}.csv",
        )
        yield from read_sdmx(path)


def build(comuni: dict[str, str]) -> None:
    # I comuni si chiedono al server a blocchi. Questo modulo scaricava l'Italia
    # intera perché «una chiave con 205 codici supera il limite di lunghezza
    # dell'URL»: il limite esiste, ma quindici codici ci stanno comodamente, e
    # la diagnosi che aveva bloccato tutte le tavole censuarie era sbagliata
    # (`FONTI.md` §10 punto 6).
    codici = sorted(comuni)
    rows = []
    for record in _scarica(codici):
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
