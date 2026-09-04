"""Scarico con cache su disco.

Ogni risposta finisce in `dati/raw/` con un nome stabile: il build successivo
riparte da lì invece di riscaricare. È lo stesso patto del progetto Donostia
(`--offline`), e qui serve ancora di più perché alcune serie ISTAT superano i
100 MB e impiegano minuti.
"""

from __future__ import annotations

import time
from pathlib import Path

import requests

from .config import RAW_DIR

# ISTAT restituisce l'intestazione CSV e zero righe se il formato si chiede con
# il parametro `format=` nella query string: va negoziato con l'header.
SDMX_CSV_ACCEPT = "application/vnd.sdmx.data+csv;version=1.0.0;labels=both"

# Senza questo header ISTAT risponde con le etichette in inglese: `private
# households on 31st December`, `4 and over`. Con l'header le stesse
# osservazioni tornano come `famiglie con tutti i componenti stranieri al 31
# dicembre` e `6 e più`. Non è una preferenza estetica: la decisione di tenere
# il progetto in italiano (`PROSSIMI-PASSI.md` §3.4) si applica ai dati come ai
# testi, e quelle stringhe finiscono nelle legende dei grafici.
#
# ⚠️ La cache di `dati/raw/` non porta traccia della lingua con cui è stata
# scaricata: un file già presente resta com'è. Le tabelle scaricate prima di
# questo header vanno riscaricate con `force=True` — o cancellando il file
# grezzo — se le si vuole in italiano.
SDMX_ACCEPT_LANGUAGE = "it"

DEFAULT_TIMEOUT = 300
RETRIES = 5

# Le attese fra i tentativi: 15, 30, 60, 120 secondi, quattro minuti in tutto.
# Erano 1, 2, 4 — sette secondi — e il 4 settembre 2026 non sono bastati: dopo
# quaranta blocchi di `migrazioni`, `esploradati.istat.it` ha smesso di
# accettare connessioni (timeout in *connessione*, non in lettura) mentre
# `demo.istat.it` e `www.istat.it`, che stanno nella stessa sottorete,
# rispondevano normalmente. Non era un guasto della fonte né della nostra rete:
# è una strozzatura per host, e dura qualche minuto. Con sette secondi di
# tentativi il dataset moriva dentro la strozzatura buttando venti minuti di
# scarico; con quattro la attraversa. La cache di `dati/raw/` fa il resto — un
# rilancio riparte dal blocco che manca.
PAUSA_INIZIALE = 15


def fetch(
    url: str,
    dest_name: str,
    *,
    headers: dict[str, str] | None = None,
    params: dict[str, str] | list[tuple[str, str]] | None = None,
    force: bool = False,
    timeout: int = DEFAULT_TIMEOUT,
) -> Path:
    """Scarica `url` in `dati/raw/<dest_name>`, riusando la cache se esiste."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    dest = RAW_DIR / dest_name
    if dest.exists() and dest.stat().st_size > 0 and not force:
        return dest

    last_error: Exception | None = None
    for attempt in range(RETRIES):
        try:
            response = requests.get(
                url,
                headers=headers or {},
                params=params,
                timeout=timeout,
                stream=True,
            )
            response.raise_for_status()
            tmp = dest.with_suffix(dest.suffix + ".part")
            with tmp.open("wb") as handle:
                for chunk in response.iter_content(chunk_size=1 << 16):
                    handle.write(chunk)
            tmp.replace(dest)
            return dest
        except Exception as error:  # rete: 502 sporadici dal proxy, timeout
            last_error = error
            if attempt < RETRIES - 1:
                time.sleep(PAUSA_INIZIALE * 2**attempt)

    # La causa va *dentro* il messaggio, non solo incatenata: `build.py` stampa
    # `str(errore)`, e senza il tipo dell'eccezione un 404 e una connessione
    # rifiutata sono la stessa riga di log.
    raise RuntimeError(
        f"download fallito dopo {RETRIES} tentativi: {url}"
        f" — {type(last_error).__name__}: {last_error}"
    ) from last_error


def sdmx_csv(dataflow: str, key: str = "", *, dest_name: str, force: bool = False) -> Path:
    """Scarica una tabella SDMX di ISTAT in CSV con etichette.

    `key` è posizionale: un campo per dimensione, separati da punti. Sbagliare
    il numero di punti restituisce zero righe *senza errore*, quindi conviene
    ricavarlo dal dataflow (`/dataflow/IT1/<id>?references=all`) invece che a
    intuito.
    """
    from .config import SDMX_BASE

    url = f"{SDMX_BASE}/data/IT1,{dataflow},1.0/{key}"
    return fetch(
        url,
        dest_name,
        headers={"Accept": SDMX_CSV_ACCEPT, "Accept-Language": SDMX_ACCEPT_LANGUAGE},
        force=force,
    )


def socrata_json(
    resource: str,
    *,
    dest_name: str,
    where: str | None = None,
    select: str | None = None,
    group: str | None = None,
    order: str | None = None,
    limit: int = 50_000,
    force: bool = False,
) -> Path:
    """Interroga un dataset Socrata di Regione Lombardia (SoQL, senza chiave)."""
    from .config import SOCRATA_BASE

    params: list[tuple[str, str]] = [("$limit", str(limit))]
    if where:
        params.append(("$where", where))
    if select:
        params.append(("$select", select))
    if group:
        params.append(("$group", group))
    if order:
        params.append(("$order", order))

    return fetch(
        f"{SOCRATA_BASE}/{resource}.json",
        dest_name,
        params=params,
        force=force,
    )
