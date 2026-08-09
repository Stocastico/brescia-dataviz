"""Lettura delle risposte grezze e scrittura delle tabelle tidy."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any, Iterable, Iterator

from .config import PROCESSED_DIR

csv.field_size_limit(min(sys.maxsize, 2**31 - 1))

# Valori che le fonti usano per dire "non disponibile". Non sono zeri: un
# comune con «Dato riservato» sulle presenze turistiche non e' un comune senza
# turisti, e trattarlo come 0 disegna buchi che sembrano assenza del fenomeno.
MISSING_TOKENS = {"", "..", "...", "n.d.", "nd", "dato riservato", "-"}


def to_number(raw: Any) -> float | None:
    """Converte in numero riconoscendo il separatore delle migliaia.

    Le fonti mescolano due convenzioni: l'SDMX di ISTAT scrive numeri nudi
    (`100939.25`), Socrata usa la virgola per le migliaia (`1,406,590`). Una
    conversione ingenua legge `567,391` come 567,391 e sbaglia di tre ordini di
    grandezza — errore silenzioso, perché il risultato resta un numero
    plausibile. Qui il separatore decimale è, per definizione, l'ultimo fra
    virgola e punto; l'altro è separatore di migliaia e va rimosso.
    """
    if raw is None:
        return None
    text = str(raw).strip().replace(" ", "").replace(" ", "")
    if text.lower() in MISSING_TOKENS:
        return None

    has_comma, has_dot = "," in text, "." in text
    if has_comma and has_dot:
        decimal = "," if text.rfind(",") > text.rfind(".") else "."
        thousands = "." if decimal == "," else ","
        text = text.replace(thousands, "").replace(decimal, ".")
    elif has_comma:
        head, _, tail = text.rpartition(",")
        # una sola virgola seguita da un gruppo diverso da 3 cifre e' decimale
        # ("3,9"); tutto il resto e' separatore di migliaia ("1,406,590").
        text = text.replace(",", "") if (len(tail) == 3 or "," in head) else f"{head}.{tail}"
    elif text.count(".") > 1:
        text = text.replace(".", "")  # "1.406.590"

    try:
        return float(text)
    except ValueError:
        return None


def split_code(labelled: str) -> tuple[str, str]:
    """Separa `"017029: Brescia"` in `("017029", "Brescia")`."""
    text = (labelled or "").strip()
    code, _, label = text.partition(": ")
    return (code.strip(), label.strip()) if label else (text, text)


def read_sdmx(path: Path) -> Iterator[dict[str, str]]:
    """Righe di un CSV SDMX, con le colonne rinominate al solo codice dimensione.

    Le intestazioni arrivano come `REF_AREA: Territory`; qui restano `REF_AREA`,
    mentre il valore conserva la forma `codice: etichetta`.
    """
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            return
        renamed = {name: name.split(":")[0].strip() for name in reader.fieldnames}
        for row in reader:
            yield {renamed[k]: v for k, v in row.items() if k in renamed}


def read_socrata(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if isinstance(payload, dict) and payload.get("error"):
        raise RuntimeError(f"errore Socrata in {path.name}: {payload.get('message')}")
    return payload


def write_csv(name: str, rows: Iterable[dict[str, Any]], columns: list[str]) -> Path:
    """Scrive una tabella tidy in `dati/processed/`, ordinata e riproducibile."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    dest = PROCESSED_DIR / name
    materialised = list(rows)
    with dest.open("w", newline="", encoding="utf-8") as handle:
        # csv scrive CRLF di default: qui i file nascono gia' con fine riga LF.
        writer = csv.DictWriter(
            handle, fieldnames=columns, extrasaction="ignore", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(materialised)
    print(f"  scritto {name}: {len(materialised):,} righe")
    return dest


def fmt(value: float | None, decimals: int = 0) -> str:
    """Numero pronto per il CSV: vuoto se assente, senza decimali inutili."""
    if value is None:
        return ""
    if decimals == 0 and abs(value - round(value)) < 1e-9:
        return str(int(round(value)))
    return f"{value:.{decimals}f}"
