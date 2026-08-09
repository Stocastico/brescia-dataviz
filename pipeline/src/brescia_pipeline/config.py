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


def ensure_dirs() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
