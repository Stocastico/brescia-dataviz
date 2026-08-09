"""Import ed export della Lombardia per settore e paese partner, dal 1991.

⚠️ **La grana è regionale, non provinciale, ed è un ripiego dichiarato.** Il
dato per provincia non è sul nodo SDMX principale (esistono dataflow
provinciali per il solo Lazio), il portale Coeweb storico è stato dismesso il
30/09/2025 e il suo sostituto è una single-page app senza endpoint pubblico
determinabile. Brescia è la seconda provincia manifatturiera lombarda: la
serie regionale è un contesto onesto, non un surrogato del dato provinciale, e
va etichettata come tale in qualunque grafico.
"""

from __future__ import annotations

from ..config import REGIONE_LOMBARDIA_SDMX
from .. import sdmx
from ..fetch import sdmx_csv
from ..tidy import fmt, read_sdmx, split_code, to_number, write_csv

DATAFLOW = "DF_DCSE_CPA_AT2007_COE_OPT_A_REG_ALL_REG"

FLUSSI = {"EV": "export", "IV": "import"}

COLUMNS = ["territorio", "anno", "flusso", "settore", "codice_settore", "partner", "codice_partner", "valore_euro"]

# Il totale mondo basta per la serie storica: i 320 partner singoli servono
# solo se si vuole la geografia delle destinazioni, e moltiplicano le righe.
PARTNER_TOTALE = "WORLD"


def build(comuni: dict[str, str]) -> None:
    rows = []
    for flusso_code, flusso in FLUSSI.items():
        chiave = sdmx.key(
            DATAFLOW,
            {
                "FREQ": "A",
                "REF_AREA": REGIONE_LOMBARDIA_SDMX,
                "DATA_TYPE": flusso_code,
                "PARTNER_COUNTRY": PARTNER_TOTALE,
            },
        )
        path = sdmx_csv(DATAFLOW, chiave, dest_name=f"istat_coe_lombardia_{flusso}.csv")
        for record in read_sdmx(path):
            value = to_number(record.get("OBS_VALUE"))
            if value is None:
                continue
            settore_code, settore_label = split_code(record.get("CPA_ATECO2007_COE", ""))
            partner_code, partner_label = split_code(record.get("PARTNER_COUNTRY", ""))
            rows.append(
                {
                    "territorio": REGIONE_LOMBARDIA_SDMX,
                    "anno": record.get("TIME_PERIOD", ""),
                    "flusso": flusso,
                    "settore": settore_label,
                    "codice_settore": settore_code,
                    "partner": partner_label,
                    "codice_partner": partner_code,
                    "valore_euro": fmt(value),
                }
            )

    rows.sort(key=lambda r: (r["flusso"], r["codice_settore"], r["anno"]))
    write_csv("commercio_estero_lombardia.csv", rows, COLUMNS)
