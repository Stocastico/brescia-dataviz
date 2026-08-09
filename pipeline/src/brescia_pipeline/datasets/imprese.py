"""Unità locali e addetti (ISTAT ASIA), per comune, 2018-2023.

È l'asse principale del progetto: risponde alla domanda se questo sia ancora
un territorio di microimprese, e permette il confronto città/provincia che
finora è la cosa più informativa emersa.

Due tabelle, per non versionare il prodotto cartesiano completo (205 comuni ×
88 divisioni Ateco × 5 classi × 6 anni × 2 indicatori):

- `imprese_classe_addetti.csv` — comune × anno × classe, totale dei settori.
  È quella che alimenta le mappe e il confronto dimensionale.
- `imprese_settore.csv` — comune × anno × divisione Ateco, totale delle classi.
  Serve a vedere *quale* settore si muove.

⚠️ Un'unità locale non è un'impresa: lo stabilimento di un gruppo con sede
altrove conta nel comune dove si trova. E gli addetti sono medie annue, quindi
con decimali.
"""

from __future__ import annotations

from ..config import COMUNE_BRESCIA, PROVINCIA_BRESCIA_SDMX
from .. import sdmx
from ..fetch import sdmx_csv
from ..tidy import fmt, read_sdmx, split_code, to_number, write_csv

DATAFLOW_COMUNI = "183_1163_DF_DICA_ASIAULP_TERRIFDATA_7"  # Ateco 2 cifre, comuni
DATAFLOW_PROVINCE = "183_1163_DF_DICA_ASIAULP_TERRIFDATA_6"  # Ateco 3 cifre, province

INDICATORI = {"LU": "unita_locali", "LUEMPDAA": "addetti"}
NACE_TOTALE = "0010"
CLASSE_TOTALE = "TOTAL"

CLASSI = {
    "TOTAL": "totale",
    "W0_9": "0-9",
    "W10_49": "10-49",
    "W50_249": "50-249",
    "W_GE250": "250+",
}

CLASSE_COLUMNS = ["codice_istat", "comune", "anno", "classe_addetti", "indicatore", "valore"]
SETTORE_COLUMNS = ["territorio", "nome_territorio", "anno", "ateco", "settore", "indicatore", "valore"]


def _decimali(indicator: str) -> int:
    return 1 if indicator == "LUEMPDAA" else 0


def build(comuni: dict[str, str]) -> None:
    per_classe: list[dict[str, str]] = []
    per_settore: list[dict[str, str]] = []

    for indicator, nome_indicatore in INDICATORI.items():
        # --- comuni × classe di addetti (totale dei settori) ---------------
        # Chiave con i 205 codici: l'URL sfora e il server risponde 400. Si
        # scarica l'Italia con il solo filtro NACE=totale e si filtra qui.
        path = sdmx_csv(
            DATAFLOW_COMUNI,
            sdmx.key(DATAFLOW_COMUNI, {"FREQ": "A", "DATA_TYPE": indicator,
                                       "ECON_ACTIVITY_NACE_2007": NACE_TOTALE}),
            dest_name=f"istat_asia_classe_{indicator.lower()}.csv",
        )
        for record in read_sdmx(path):
            code, _ = split_code(record.get("REF_AREA", ""))
            if code not in comuni:
                continue
            classe_code, _ = split_code(record.get("PERS_EMPL_SIZE_CLASS", ""))
            value = to_number(record.get("OBS_VALUE"))
            if value is None or classe_code not in CLASSI:
                continue
            per_classe.append(
                {
                    "codice_istat": code,
                    "comune": comuni[code],
                    "anno": record.get("TIME_PERIOD", ""),
                    "classe_addetti": CLASSI[classe_code],
                    "indicatore": nome_indicatore,
                    "valore": fmt(value, _decimali(indicator)),
                }
            )

        # --- settore Ateco, per la provincia e per il capoluogo -------------
        # Il dettaglio settoriale su tutti i comuni sarebbe un prodotto
        # cartesiano da milioni di righe: si prendono i due territori che
        # servono davvero, e il confronto fra i due e' la lettura interessante.
        for dataflow, territorio, nome in (
            (DATAFLOW_PROVINCE, PROVINCIA_BRESCIA_SDMX, "Provincia di Brescia"),
            (DATAFLOW_COMUNI, COMUNE_BRESCIA, "Brescia"),
        ):
            path = sdmx_csv(
                dataflow,
                sdmx.key(dataflow, {"FREQ": "A", "REF_AREA": territorio,
                                    "DATA_TYPE": indicator,
                                    "PERS_EMPL_SIZE_CLASS": CLASSE_TOTALE}),
                dest_name=f"istat_asia_settore_{territorio}_{indicator.lower()}.csv",
            )
            for record in read_sdmx(path):
                nace_code, nace_label = split_code(record.get("ECON_ACTIVITY_NACE_2007", ""))
                # Il dataflow provinciale scende a 3 cifre: si tiene la
                # divisione (2 cifre) per restare confrontabile col comunale.
                if nace_code == NACE_TOTALE or len(nace_code) != 2:
                    continue
                value = to_number(record.get("OBS_VALUE"))
                if value is None:
                    continue
                per_settore.append(
                    {
                        "territorio": territorio,
                        "nome_territorio": nome,
                        "anno": record.get("TIME_PERIOD", ""),
                        "ateco": nace_code,
                        "settore": nace_label,
                        "indicatore": nome_indicatore,
                        "valore": fmt(value, _decimali(indicator)),
                    }
                )

    per_classe.sort(key=lambda r: (r["codice_istat"], r["indicatore"], r["anno"], r["classe_addetti"]))
    per_settore.sort(key=lambda r: (r["territorio"], r["indicatore"], r["anno"], r["ateco"]))

    write_csv("imprese_classe_addetti.csv", per_classe, CLASSE_COLUMNS)
    write_csv("imprese_settore.csv", per_settore, SETTORE_COLUMNS)
