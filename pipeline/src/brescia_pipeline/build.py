"""Orchestratore: scarica le fonti verificate e scrive le tabelle tidy.

    python -m brescia_pipeline.build              # tutti i dataset
    python -m brescia_pipeline.build imprese      # solo alcuni
    python -m brescia_pipeline.build --list

Le risposte grezze restano in `dati/raw/` (non versionata): rieseguire il build
non riscarica nulla finché quei file esistono.
"""

from __future__ import annotations

import argparse
import sys
import time
from collections.abc import Callable

from . import web
from .config import PROCESSED_DIR, RAW_DIR, ensure_dirs
from .datasets import (
    abitazioni,
    ambiente,
    anagrafica,
    bilancio,
    commercio_estero,
    confini,
    famiglie,
    imprese,
    lavoro,
    migrazioni,
    popolazione,
    province,
    redditi,
    redditi_confronto,
    sezioni,
    sicurezza,
    sintesi,
    turismo,
    turismo_confronto,
)

# Ogni voce riceve la mappa dei comuni della provincia e scrive in processed/.
DATASETS: dict[str, Callable[[dict[str, str]], None]] = {
    # apre la fila: e' la geometria di riferimento su cui tutto il resto mappa
    "confini": confini.build,
    "popolazione": popolazione.build,
    "bilancio": bilancio.build,
    "imprese": imprese.build,
    "sezioni": sezioni.build,
    "province": province.build,
    "turismo": turismo.build,
    "turismo_confronto": turismo_confronto.build,
    "lavoro": lavoro.build,
    "migrazioni": migrazioni.build,
    "abitazioni": abitazioni.build,
    "famiglie": famiglie.build,
    "sicurezza": sicurezza.build,
    "ambiente": ambiente.build,
    "redditi": redditi.build,
    "redditi_confronto": redditi_confronto.build,
    "commercio_estero": commercio_estero.build,
    # devono restare in coda: leggono le tabelle prodotte dagli altri
    "sintesi": sintesi.build,
    "web": web.build,
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="brescia_pipeline.build")
    parser.add_argument("datasets", nargs="*", help="dataset da costruire (default: tutti)")
    parser.add_argument("--list", action="store_true", help="elenca i dataset disponibili")
    parser.add_argument(
        "--offline",
        action="store_true",
        help="non tocca la rete: usa le tabelle già in dati/processed/ "
        "(serve a chi ricostruisce solo l'export per il sito, e alla CI)",
    )
    args = parser.parse_args(argv)

    if args.list:
        print("dataset disponibili:")
        for name in DATASETS:
            print(f"  {name}")
        return 0

    unknown = [name for name in args.datasets if name not in DATASETS]
    if unknown:
        parser.error(f"dataset sconosciuti: {', '.join(unknown)}")

    selected = args.datasets or list(DATASETS)

    ensure_dirs()
    print(f"raw:       {RAW_DIR}")
    print(f"processed: {PROCESSED_DIR}\n")

    print("anagrafica dei comuni")
    comuni = anagrafica.build(solo_locale=args.offline)
    print(f"  {len(comuni)} comuni nella provincia di Brescia\n")

    failures: list[str] = []
    for name in selected:
        print(name)
        started = time.monotonic()
        try:
            DATASETS[name](comuni)
        except Exception as error:  # un dataset rotto non deve fermare gli altri
            failures.append(name)
            print(f"  FALLITO: {error}")
        else:
            print(f"  ok in {time.monotonic() - started:.1f}s")
        print()

    if failures:
        print(f"dataset falliti: {', '.join(failures)}")
        return 1

    print("build completo")
    return 0


if __name__ == "__main__":
    sys.exit(main())
