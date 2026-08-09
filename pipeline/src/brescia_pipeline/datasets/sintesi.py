"""Tabella di sintesi: una riga per comune, gli indicatori principali affiancati.

Non aggiunge informazione — la ricava dalle tabelle tidy già scritte — ma è la
vista che serve per aprire una mappa o un foglio di calcolo senza fare join.
Va costruita **dopo** gli altri dataset.

⚠️ Le colonne hanno anni diversi (ASIA si ferma al 2023, popolazione e turismo
arrivano al 2024): qualsiasi rapporto fra colonne mescola due annate e va
dichiarato.
"""

from __future__ import annotations

import csv

from ..config import PROCESSED_DIR
from ..tidy import fmt, to_number, write_csv

COLUMNS = [
    "codice_istat", "comune", "capoluogo",
    "popolazione_2024", "unita_locali_2023", "addetti_2023",
    "addetti_per_100_abitanti", "presenze_turistiche_2024",
]


def _leggi(nome: str) -> list[dict[str, str]]:
    path = PROCESSED_DIR / nome
    if not path.exists():
        raise FileNotFoundError(
            f"manca {nome}: costruire prima gli altri dataset "
            f"(`python -m brescia_pipeline.build`)"
        )
    with path.open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def build(comuni: dict[str, str]) -> None:
    anagrafica = {r["codice_istat"]: r for r in _leggi("comuni.csv")}

    popolazione = {
        r["codice_istat"]: to_number(r["valore"])
        for r in _leggi("popolazione_comuni.csv")
        if r["anno"] == "2024" and r["indicatore"] == "popolazione_residente"
    }

    imprese = _leggi("imprese_classe_addetti.csv")
    unita_locali = {
        r["codice_istat"]: to_number(r["valore"])
        for r in imprese
        if r["anno"] == "2023" and r["indicatore"] == "unita_locali" and r["classe_addetti"] == "totale"
    }
    addetti = {
        r["codice_istat"]: to_number(r["valore"])
        for r in imprese
        if r["anno"] == "2023" and r["indicatore"] == "addetti" and r["classe_addetti"] == "totale"
    }

    # Solo gli zeri misurati: quelli calcolati su componenti soppresse restano
    # fuori, altrimenti la mappa mostrerebbe «nessun turismo» dove il dato
    # semplicemente non c'e'.
    presenze = {
        r["codice_istat"]: to_number(r["presenze"])
        for r in _leggi("turismo_comuni_annuale.csv")
        if r["anno"] == "2024"
        and r["tipo_struttura"] == "Totale"
        and r["cittadinanza"] == "Totale"
        and r["stato"] == "osservato"
    }

    rows = []
    for code in sorted(comuni):
        pop = popolazione.get(code)
        add = addetti.get(code)
        densita = (add / pop * 100) if pop and add is not None else None
        rows.append(
            {
                "codice_istat": code,
                "comune": comuni[code],
                "capoluogo": anagrafica.get(code, {}).get("capoluogo", "0"),
                "popolazione_2024": fmt(pop),
                "unita_locali_2023": fmt(unita_locali.get(code)),
                "addetti_2023": fmt(add, 1),
                "addetti_per_100_abitanti": fmt(densita, 1),
                "presenze_turistiche_2024": fmt(presenze.get(code)),
            }
        )

    write_csv("comuni_sintesi.csv", rows, COLUMNS)
