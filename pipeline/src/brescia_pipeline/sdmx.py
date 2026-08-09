"""Costruzione delle chiavi SDMX a partire dalla struttura del dataflow.

La chiave di ISTAT è posizionale: un campo per dimensione, separati da punti.
Sbagliare il numero di punti non produce un errore, produce **zero righe** —
un dataset pieno che sembra vuoto. Contarli a mano dalla documentazione è
esattamente il modo in cui ci si sbaglia, quindi qui le dimensioni si leggono
dal server e la chiave si compone da un dizionario.
"""

from __future__ import annotations

import re

from .fetch import fetch

# `\s` dopo il nome del tag e' obbligatorio: senza, il pattern cattura anche
# <structure:DimensionList id="DimensionDescriptor"> e la chiave nasce con un
# campo di troppo. TimeDimension resta fuori: non fa parte della chiave.
_DIMENSION_RE = re.compile(r'<structure:Dimension\s[^>]*\bid="([^"]+)"')
_cache: dict[str, list[str]] = {}


def dimensions(dataflow: str) -> list[str]:
    """Nomi delle dimensioni del dataflow, nell'ordine posizionale della chiave."""
    if dataflow in _cache:
        return _cache[dataflow]

    from .config import SDMX_BASE

    # `references=datastructure` basta e avanza: serve l'elenco ordinato delle
    # dimensioni, non l'albero delle codelist. Con `references=all` la stessa
    # risposta pesa una decina di MB per dataflow.
    path = fetch(
        f"{SDMX_BASE}/dataflow/IT1/{dataflow}?references=datastructure",
        f"sdmx_struct_{dataflow}.xml",
        headers={"Accept": "application/vnd.sdmx.structure+xml;version=2.1"},
    )
    text = path.read_text(encoding="utf-8", errors="replace")
    dims = _DIMENSION_RE.findall(text)
    if not dims:
        raise RuntimeError(f"nessuna dimensione trovata per {dataflow}")

    _cache[dataflow] = dims
    return dims


def key(dataflow: str, fixed: dict[str, str]) -> str:
    """Chiave SDMX con i valori indicati e il resto libero.

    >>> key("DF_DCSS_EMPLP_2_COM", {"FREQ": "A", "REF_AREA": "017029"})
    'A.017029.....'
    """
    dims = dimensions(dataflow)
    unknown = set(fixed) - set(dims)
    if unknown:
        raise ValueError(
            f"{dataflow}: dimensioni inesistenti {sorted(unknown)}; disponibili {dims}"
        )
    return ".".join(fixed.get(dim, "") for dim in dims)
