"""Gli stessi redditi comunali per una o più **province di confronto**.

La convergenza dei redditi fra i comuni bresciani è il risultato più netto delle
analisi, e finora era anche il più fragile: era misurato contro sé stesso. Se i
comuni convergono in tutta Italia, «i redditi bresciani convergono» descrive
l'Italia e non Brescia — è lo stesso errore che MET-14 ha trovato sulla
frammentazione delle imprese, in un'altra fonte.

Qui non basta un filtro come per le imprese: le tavole MEF si scaricano per
blocchi di comuni, quindi ogni provincia di confronto costa i suoi download. Sono
piccoli — una ventina di richieste per provincia, qualche secondo l'una — ma non
sono gratis, e per questo la lista è **esplicita e corta** invece che «tutta
Italia».

La provincia di confronto naturale è **Bergamo** (`016`): stessa dimensione,
storia industriale parallela, stessa Capitale della cultura 2023, e sul registro
delle imprese risulta la più simile a Brescia su quasi ogni indicatore.

⚠️ Vale la stessa avvertenza di `province.py`: **non è un secondo soggetto.** La
tabella serve a dire se un risultato bresciano sia bresciano, e non entra in
nessuna mappa.
"""

from __future__ import annotations

import csv
import io

from ..config import ELENCO_COMUNI_URL
from ..fetch import fetch, sdmx_csv
from .. import sdmx
from ..tidy import fmt, read_sdmx, split_code, to_number, write_csv
from .redditi import CLASSE_DIM, COMUNI_PER_RICHIESTA, DATAFLOW

# Codici provincia ISTAT. Tenerli pochi: ogni voce costa una ventina di richieste.
PROVINCE_DI_CONFRONTO = {"016": "Bergamo"}

COLUMNS = [
    "codice_provincia",
    "provincia",
    "codice_istat",
    "comune",
    "anno",
    "codice_indicatore",
    "indicatore",
    "classe_reddito",
    "codice_classe",
    "valore",
]


def comuni_di(codice_provincia: str) -> dict[str, str]:
    path = fetch(ELENCO_COMUNI_URL, "istat_elenco_comuni.csv")
    text = path.read_bytes().decode("latin-1")
    reader = csv.reader(io.StringIO(text), delimiter=";")
    next(reader, None)
    return {
        row[4].strip(): row[6].strip()
        for row in reader
        if len(row) > 6 and row[2].strip() == codice_provincia and len(row[4].strip()) == 6
    }


def build(comuni: dict[str, str]) -> None:
    del comuni  # qui servono i comuni delle province di confronto
    rows: list[dict[str, str]] = []

    for codice_provincia, nome_provincia in PROVINCE_DI_CONFRONTO.items():
        elenco = comuni_di(codice_provincia)
        codici = sorted(elenco)
        print(f"  {nome_provincia}: {len(codici)} comuni")
        for inizio in range(0, len(codici), COMUNI_PER_RICHIESTA):
            blocco = codici[inizio : inizio + COMUNI_PER_RICHIESTA]
            path = sdmx_csv(
                DATAFLOW,
                sdmx.key(DATAFLOW, {"FREQ": "A", "REF_AREA": "+".join(blocco)}),
                dest_name=f"mef_redditi_{codice_provincia}_{inizio:03d}.csv",
            )
            for record in read_sdmx(path):
                code, _ = split_code(record.get("REF_AREA", ""))
                if code not in elenco:
                    continue
                valore = to_number(record.get("OBS_VALUE"))
                if valore is None:
                    continue
                classe_code, classe_label = split_code(record.get(CLASSE_DIM, ""))
                indicatore_code, indicatore_label = split_code(record.get("DATA_TYPE", ""))
                rows.append(
                    {
                        "codice_provincia": codice_provincia,
                        "provincia": nome_provincia,
                        "codice_istat": code,
                        "comune": elenco[code],
                        "anno": record.get("TIME_PERIOD", ""),
                        "codice_indicatore": indicatore_code,
                        "indicatore": indicatore_label,
                        "classe_reddito": classe_label,
                        "codice_classe": classe_code,
                        "valore": fmt(valore, 2),
                    }
                )

    rows.sort(key=lambda r: (r["codice_istat"], r["anno"], r["codice_indicatore"], r["codice_classe"]))
    write_csv("redditi_comuni_confronto.csv", rows, COLUMNS)
