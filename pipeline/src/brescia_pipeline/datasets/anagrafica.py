"""I 205 comuni della provincia: codici, nomi, flag capoluogo.

È la tabella su cui tutto il resto fa join. Il codice ISTAT a sei cifre è la
chiave nativa di quasi ogni fonte italiana, quindi non serve inventare slug.
"""

from __future__ import annotations

import csv
import io

from ..config import ELENCO_COMUNI_URL, PROCESSED_DIR, PROVINCIA_BRESCIA_ISTAT
from ..fetch import fetch
from ..tidy import write_csv

COLUMNS = ["codice_istat", "comune", "sigla_provincia", "capoluogo"]


def comuni_provincia() -> dict[str, str]:
    """Mappa `codice_istat -> denominazione` per i comuni della provincia."""
    path = fetch(ELENCO_COMUNI_URL, "istat_elenco_comuni.csv")
    # Il file ISTAT e' in latin-1 con separatore ';': letto come UTF-8 esplode.
    text = path.read_bytes().decode("latin-1")
    rows = csv.reader(io.StringIO(text), delimiter=";")
    next(rows, None)
    return {
        row[4].strip(): row[6].strip()
        for row in rows
        if len(row) > 6 and row[2].strip() == PROVINCIA_BRESCIA_ISTAT
    }


def build(solo_locale: bool = False) -> dict[str, str]:
    """Con `solo_locale` rilegge `comuni.csv` invece di interrogare ISTAT.

    Serve a ricostruire i JSON per il sito — e a far girare la CI — senza che il
    risultato dipenda dal fatto che `istat.it` risponda quel giorno. La tabella
    è versionata, quindi c'è sempre; se manca, l'errore lo dice.
    """
    if solo_locale:
        locale = PROCESSED_DIR / "comuni.csv"
        if not locale.exists():
            raise FileNotFoundError(
                f"manca {locale.name}: con --offline serve la tabella già costruita"
            )
        with locale.open(encoding="utf-8") as handle:
            return {r["codice_istat"]: r["comune"] for r in csv.DictReader(handle)}

    path = fetch(ELENCO_COMUNI_URL, "istat_elenco_comuni.csv")
    text = path.read_bytes().decode("latin-1")
    reader = csv.reader(io.StringIO(text), delimiter=";")
    next(reader, None)

    out: list[dict[str, str]] = []
    for row in reader:
        if len(row) <= 14 or row[2].strip() != PROVINCIA_BRESCIA_ISTAT:
            continue
        out.append(
            {
                "codice_istat": row[4].strip(),
                "comune": row[6].strip(),
                "sigla_provincia": row[14].strip(),
                "capoluogo": "1" if row[13].strip() == "1" else "0",
            }
        )

    out.sort(key=lambda r: r["codice_istat"])
    write_csv("comuni.csv", out, COLUMNS)
    return {r["codice_istat"]: r["comune"] for r in out}
