"""Abitazioni per comune: stock, occupazione e titolo di godimento.

Due tavole del Censimento permanente:

- `_TV_1` — abitazioni occupate e non occupate;
- `_TV_2` — abitazioni occupate per **proprietà, affitto, altro titolo**.

La seconda è quella che conta. Risponde alla domanda «quante case in affitto»
**senza passare per i prezzi**, che nel progetto Donostia sono stati la fonte
di ogni guaio metodologico e che qui restano dietro il login OMI. Il titolo di
godimento è misurato, non stimato: è un `osservato` nella scheda di confidenza,
mentre qualunque proxy sui prezzi sarebbe un `proxy`.
"""

from __future__ import annotations

from . import _censimento
from ..tidy import write_csv

TAVOLE = {
    "occupate_e_non_occupate": 1,
    "titolo_di_godimento": 2,
}

DIMENSIONI = [
    "OWNERSHIP_TYPE",
    "NUMB_ROOM",
    "USE_FLOOR_SPACEGROUP",
    "HEATING_SYSTEM_TYPE",
    "ACCESS_BUILDING",
    "TYPE_OF_BUILDING",
]

COLUMNS = _censimento.colonne(DIMENSIONI)


def build(comuni: dict[str, str]) -> None:
    rows: list[dict[str, str]] = []
    for nome, numero in TAVOLE.items():
        rows += _censimento.tavola(
            f"DF_DCSS_ABITAZIONI_TV_{numero}",
            nome=nome,
            dest_name=f"istat_abitazioni_tv{numero}.csv",
            comuni=comuni,
            dimensioni=DIMENSIONI,
        )

    _censimento.ordina(rows, DIMENSIONI)
    write_csv("abitazioni_comuni.csv", rows, COLUMNS)
