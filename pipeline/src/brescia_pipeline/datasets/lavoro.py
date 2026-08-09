"""Lavoro e istruzione dal Censimento permanente, più il tasso di occupazione.

Grane diverse per necessità: il censimento arriva al comune, la rilevazione
sulle forze di lavoro si ferma alla provincia. Le tabelle restano separate
proprio per non far sembrare confrontabile ciò che non lo è.
"""

from __future__ import annotations

from ..config import COMUNE_BRESCIA, PROVINCIA_BRESCIA_SDMX
from .. import sdmx
from ..fetch import sdmx_csv
from ..tidy import fmt, read_sdmx, split_code, to_number, write_csv

# Censimento permanente, grana comune. Le dimensioni cambiano da tavola a
# tavola: la chiave la compone `sdmx.key` leggendo la struttura dal server.
CENSIMENTO = {
    "occupati_settore": "DF_DCSS_EMPLP_2_COM",
    "occupati_posizione": "DF_DCSS_EMPLP_1_COM",
    "condizione_professionale_eta": "DF_DCSS_ISTR_LAV_PEN_2_TV_3",
    "condizione_professionale_cittadinanza": "DF_DCSS_ISTR_LAV_PEN_2_TV_4",
    "istruzione_eta": "DF_DCSS_ISTR_LAV_PEN_2_TV_1",
    "istruzione_cittadinanza": "DF_DCSS_ISTR_LAV_PEN_2_TV_2",
    "pendolarismo": "DF_DCSS_ISTR_LAV_PEN_2_TV_5",
}

# Dimensioni da riportare come colonne, quando presenti nella tavola.
DIMENSIONI = [
    "GENDER",
    "AGE_CLASS",
    "AGE_NOCLASS",
    "CITIZENSHIP",
    "EDU_ATTAIN",
    "EMPLOYMENT_STATUS",
    "BRANCH_ECON_ACT",
    "PROF_STATUS",
    "CUR_ACT_STAT",
    "LOC_DEST",
    "REAS_COMMUTING",
]

CENSIMENTO_COLUMNS = ["tavola", "anno", "dimensione", "modalita", "codice_modalita", "valore"]
OCCUPAZIONE_COLUMNS = [
    "territorio", "anno", "indicatore", "sesso", "eta", "titolo_studio", "cittadinanza", "valore",
]

TASSO_OCCUPAZIONE = "150_915_DF_DCCV_TAXOCCU1_YOUTH_1"


def _censimento() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for tavola, dataflow in CENSIMENTO.items():
        chiave = sdmx.key(dataflow, {"FREQ": "A", "REF_AREA": COMUNE_BRESCIA})
        path = sdmx_csv(dataflow, chiave, dest_name=f"istat_cens_{tavola}.csv")
        for record in read_sdmx(path):
            value = to_number(record.get("OBS_VALUE"))
            if value is None:
                continue
            # Una riga per dimensione valorizzata: la tavola resta leggibile
            # anche se le dimensioni cambiano da una all'altra.
            for dim in DIMENSIONI:
                if dim not in record or not record[dim]:
                    continue
                code, label = split_code(record[dim])
                rows.append(
                    {
                        "tavola": tavola,
                        "anno": record.get("TIME_PERIOD", ""),
                        "dimensione": dim,
                        "modalita": label,
                        "codice_modalita": code,
                        "valore": fmt(value, 1),
                    }
                )
    return rows


def _tasso_occupazione() -> list[dict[str, str]]:
    path = sdmx_csv(TASSO_OCCUPAZIONE, dest_name="istat_tasso_occupazione.csv")
    rows = []
    for record in read_sdmx(path):
        area, _ = split_code(record.get("REF_AREA", ""))
        if area != PROVINCIA_BRESCIA_SDMX:
            continue
        value = to_number(record.get("OBS_VALUE"))
        if value is None:
            continue
        rows.append(
            {
                "territorio": area,
                "anno": record.get("TIME_PERIOD", ""),
                "indicatore": split_code(record.get("DATA_TYPE", ""))[1],
                "sesso": split_code(record.get("SEX", ""))[1],
                "eta": split_code(record.get("AGE", ""))[1],
                "titolo_studio": split_code(record.get("EDU_LEV_HIGHEST", ""))[1],
                "cittadinanza": split_code(record.get("CITIZENSHIP", ""))[1],
                "valore": fmt(value, 2),
            }
        )
    return rows


def build(comuni: dict[str, str]) -> None:
    censimento = _censimento()
    censimento.sort(key=lambda r: (r["tavola"], r["anno"], r["dimensione"], r["codice_modalita"]))
    write_csv("censimento_lavoro_brescia.csv", censimento, CENSIMENTO_COLUMNS)

    occupazione = _tasso_occupazione()
    occupazione.sort(key=lambda r: (r["anno"], r["indicatore"], r["sesso"], r["eta"]))
    write_csv("tasso_occupazione_provincia.csv", occupazione, OCCUPAZIONE_COLUMNS)
