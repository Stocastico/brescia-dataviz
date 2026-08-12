"""Background migratorio per comune: l'asse «chi vive nel bresciano».

Dieci tavole del Censimento permanente che, messe insieme, permettono la
distinzione che quasi tutte le narrazioni pubbliche sbagliano: **stranieri
immigrati**, **stranieri nati in Italia** (seconde generazioni) e **italiani
per acquisizione**. Non sono tre modi di dire la stessa cosa, e tenerle
separate è il motivo per cui questo asse è nel brief (`BRIEF.md`, storia 3).

Le dieci tavole si distinguono per popolazione di partenza e per variabile di
incrocio; la dimensione territoriale è il comune, quindi tutte e 205 le righe
della provincia ci sono.

⚠️ `PREVOUS_CITIZEN` è scritto così nella struttura ISTAT, con il refuso.
Rinominarlo qui romperebbe la corrispondenza con la fonte, quindi resta.
"""

from __future__ import annotations

from . import _censimento
from ..tidy import write_csv

# Le dieci tavole `_COM`, con un nome che dice di che popolazione parlano.
TAVOLE = {
    "italiani_stranieri_per_nascita_genitori": 1,
    "italiani_nati_in_italia": 2,
    "italiani_nati_all_estero": 3,
    "italiani_acquisizione_nati_in_italia": 4,
    "italiani_acquisizione_nati_all_estero": 5,
    "stranieri_nati_in_italia": 6,
    "stranieri_nati_all_estero": 7,
    "italiani_istruzione": 8,
    "italiani_acquisizione_istruzione": 9,
    "stranieri_istruzione": 10,
}

DIMENSIONI = [
    "GENDER",
    "AGE_CLASS",
    "CITIZENSHIP",
    "PREVOUS_CITIZEN",
    "PLACE_BIRTH_PAR",
    "EDU_ATTAIN",
]

COLUMNS = _censimento.colonne(DIMENSIONI)


def build(comuni: dict[str, str]) -> None:
    rows: list[dict[str, str]] = []
    for nome, numero in TAVOLE.items():
        rows += _censimento.tavola(
            f"DF_DCSS_MIGR_BACKG_PAR_TV_{numero}_COM",
            nome=nome,
            dest_name=f"istat_migr_backg_tv{numero}.csv",
            comuni=comuni,
            dimensioni=DIMENSIONI,
        )

    _censimento.ordina(rows, DIMENSIONI)
    write_csv("migrazioni_comuni.csv", rows, COLUMNS)
