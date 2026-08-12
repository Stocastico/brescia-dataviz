"""Famiglie per comune: numerosità e presenza di componenti stranieri.

Tre tavole del Censimento permanente: tutte le famiglie (`_TV_1`), quelle con
**almeno un** componente straniero (`_TV_2`) e quelle con **tutti** i
componenti stranieri (`_TV_3`).

La distinzione fra le ultime due è il punto. «Famiglie straniere» è
un'espressione che schiaccia due situazioni molto diverse — la famiglia mista e
quella interamente straniera — e la fonte le tiene separate: qui restano
separate anche nella tabella, con `_TV_1` a fare da denominatore quando serve
una quota.

`popolazione_comuni.csv` porta già il **numero** di famiglie per comune da
`DF_DCSS_FAM_POP_TV_1`; questa tabella ne è la scomposizione, non un doppione.
"""

from __future__ import annotations

from . import _censimento
from ..tidy import write_csv

TAVOLE = {
    "tutte": 1,
    "almeno_uno_straniero": 2,
    "tutti_stranieri": 3,
}

DIMENSIONI = ["NUM_MEMB", "NUM_FR_MENB"]

COLUMNS = _censimento.colonne(DIMENSIONI)


def build(comuni: dict[str, str]) -> None:
    rows: list[dict[str, str]] = []
    for nome, numero in TAVOLE.items():
        rows += _censimento.tavola(
            f"DF_DCSS_FAMIGLIE_TV_{numero}",
            nome=nome,
            dest_name=f"istat_famiglie_tv{numero}.csv",
            comuni=comuni,
            dimensioni=DIMENSIONI,
        )

    _censimento.ordina(rows, DIMENSIONI)
    write_csv("famiglie_comuni.csv", rows, COLUMNS)
