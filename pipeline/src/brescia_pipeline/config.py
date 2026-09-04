"""Costanti condivise: codici territoriali, endpoint, percorsi."""

from __future__ import annotations

from pathlib import Path

# --- Territorio ---------------------------------------------------------

COMUNE_BRESCIA = "017029"
PROVINCIA_BRESCIA_SDMX = "ITC47"  # codice NUTS3 usato da ISTAT nell'SDMX
PROVINCIA_BRESCIA_ISTAT = "017"  # codice provincia nell'elenco dei comuni
REGIONE_LOMBARDIA_SDMX = "ITC4"
SIGLA_PROVINCIA = "BS"

# --- Endpoint -----------------------------------------------------------

SDMX_BASE = "https://esploradati.istat.it/SDMXWS/rest"
SOCRATA_BASE = "https://www.dati.lombardia.it/resource"

ELENCO_COMUNI_URL = (
    "https://www.istat.it/storage/codici-unita-amministrative/Elenco-comuni-italiani.csv"
)
CONFINI_COMUNI_URL = (
    "https://www.istat.it/storage/cartografia/confini_amministrativi/"
    "generalizzati/2025/Limiti01012025_g.zip"
)

# --- Percorsi -----------------------------------------------------------

PACKAGE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_ROOT.parents[2]  # brescia/
RAW_DIR = PROJECT_ROOT / "dati" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "dati" / "processed"
# Gli input curati: i file che nessun URL restituisce e che quindi stanno
# versionati nel repository (oggi gli archivi OMI, dietro SPID).
INPUT_DIR = PROJECT_ROOT / "dati" / "input"


def ensure_dirs() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# --- Bilancio demografico (demo.istat.it, tavola D7B) --------------------

# La pagina indice porta un link per anno: gli anni si leggono da lì invece di
# scriverli in una costante che invecchia in silenzio.
BILANCIO_ANNI_URL = "https://demo.istat.it/app/?i=D7B&l=it"
BILANCIO_FILE_URL = "https://demo.istat.it/data/d7b/D7B{anno}.csv.zip"

# Il bilancio mensile riconciliato con il censimento permanente comincia con il
# 2019: gli anni precedenti stanno su un'altra tavola, con un'altra popolazione
# di riferimento, e mescolarli romperebbe la catena degli stock.
PRIMO_ANNO_BILANCIO = 2019
