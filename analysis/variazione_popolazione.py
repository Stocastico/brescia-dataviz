"""Velocità di cambio della popolazione comunale, 2018–2024.

    python analysis/variazione_popolazione.py            # le due code, a schermo
    python analysis/variazione_popolazione.py --save     # + analysis/output/variazione_popolazione.csv
    python analysis/variazione_popolazione.py --tutti    # tutti i 205 comuni

Prima delle analisi previste da `PROSSIMI-PASSI.md` §5, e la più semplice:
tasso annualizzato di variazione della popolazione residente fra il primo e
l'ultimo anno della serie, per ciascuno dei 205 comuni. Serve a distinguere
**dov'è alto** da **dove sta cambiando in fretta** (MET-7), che sono due
domande diverse e vengono confuse quasi sempre.

Cosa questo numero **non** dice, e va scritto accanto a ogni grafico che lo usi:

- è una variazione **netta**: non distingue saldo naturale, migrazione interna
  e migrazione estera. La decomposizione è un'analisi a sé (§5), e richiede
  dati che qui non ci sono;
- copre il **2020–2021**, che spezza quasi tutte le serie (MET-8): il tasso
  annualizzato ci passa sopra come se nulla fosse, ed è esattamente il tipo di
  media che nasconde una discontinuità;
- sui comuni piccoli poche decine di persone fanno percentuali vistose. La
  colonna `popolazione_2018` serve a ricordarlo: sotto i mille abitanti il
  tasso va letto insieme al valore assoluto, mai da solo.

Confidenza: `derivato` (MET-4) — calcolato da `popolazione_residente`, che è
`osservato`.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
PROCESSED = RADICE / "dati" / "processed"
OUTPUT = Path(__file__).resolve().parent / "output"

COLONNE = [
    "codice_istat",
    "comune",
    "capoluogo",
    "anno_iniziale",
    "anno_finale",
    "popolazione_2018",
    "popolazione_2024",
    "variazione_assoluta",
    "variazione_percentuale",
    "tasso_annualizzato",
]


def serie_popolazione() -> dict[str, dict[str, int]]:
    """Popolazione residente per comune e anno."""
    per_comune: dict[str, dict[str, int]] = {}
    with (PROCESSED / "popolazione_comuni.csv").open(newline="", encoding="utf-8") as handle:
        for riga in csv.DictReader(handle):
            if riga["indicatore"] != "popolazione_residente" or not riga["valore"]:
                continue
            per_comune.setdefault(riga["codice_istat"], {})[riga["anno"]] = int(riga["valore"])
    return per_comune


def anagrafica() -> dict[str, dict[str, str]]:
    with (PROCESSED / "comuni.csv").open(newline="", encoding="utf-8") as handle:
        return {riga["codice_istat"]: riga for riga in csv.DictReader(handle)}


def calcola() -> list[dict[str, str]]:
    comuni = anagrafica()
    righe: list[dict[str, str]] = []

    for codice, serie in serie_popolazione().items():
        anni = sorted(serie)
        primo, ultimo = anni[0], anni[-1]
        iniziale, finale = serie[primo], serie[ultimo]
        durata = int(ultimo) - int(primo)
        # Tasso composto: (finale/iniziale)^(1/anni) - 1. Non è la variazione
        # percentuale divisa per gli anni, che su sei anni sbaglia già.
        tasso = ((finale / iniziale) ** (1 / durata) - 1) * 100

        righe.append(
            {
                "codice_istat": codice,
                "comune": comuni[codice]["comune"],
                "capoluogo": comuni[codice]["capoluogo"],
                "anno_iniziale": primo,
                "anno_finale": ultimo,
                "popolazione_2018": str(iniziale),
                "popolazione_2024": str(finale),
                "variazione_assoluta": str(finale - iniziale),
                "variazione_percentuale": f"{(finale / iniziale - 1) * 100:.2f}",
                "tasso_annualizzato": f"{tasso:.3f}",
            }
        )

    righe.sort(key=lambda r: float(r["tasso_annualizzato"]), reverse=True)
    return righe


def stampa(righe: list[dict[str, str]], quante: int | None) -> None:
    intestazione = f"{'comune':28} {'2018':>8} {'2024':>8} {'assoluta':>9} {'%/anno':>8}"

    def blocco(sotto: list[dict[str, str]]) -> None:
        for riga in sotto:
            print(
                f"{riga['comune'][:28]:28} {riga['popolazione_2018']:>8} "
                f"{riga['popolazione_2024']:>8} {riga['variazione_assoluta']:>9} "
                f"{riga['tasso_annualizzato']:>8}"
            )

    print(intestazione)
    print("-" * len(intestazione))
    if quante is None:
        blocco(righe)
    else:
        blocco(righe[:quante])
        print(f"{'…':^28}")
        blocco(righe[-quante:])
    print("-" * len(intestazione))

    totale_iniziale = sum(int(r["popolazione_2018"]) for r in righe)
    totale_finale = sum(int(r["popolazione_2024"]) for r in righe)
    print(
        f"{'provincia':28} {totale_iniziale:>8} {totale_finale:>8} "
        f"{totale_finale - totale_iniziale:>9} "
        f"{((totale_finale / totale_iniziale) ** (1 / 6) - 1) * 100:>8.3f}"
    )
    in_calo = sum(1 for r in righe if int(r["variazione_assoluta"]) < 0)
    print(f"\n{in_calo} comuni su {len(righe)} perdono popolazione fra il 2018 e il 2024.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="variazione_popolazione")
    parser.add_argument("--save", action="store_true", help="scrive il CSV in analysis/output/")
    parser.add_argument("--tutti", action="store_true", help="stampa tutti i comuni, non solo le code")
    parser.add_argument("--code", type=int, default=10, help="quanti comuni per coda (default 10)")
    args = parser.parse_args(argv)

    righe = calcola()
    stampa(righe, None if args.tutti else args.code)

    if args.save:
        OUTPUT.mkdir(parents=True, exist_ok=True)
        destinazione = OUTPUT / "variazione_popolazione.csv"
        with destinazione.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=COLONNE, lineterminator="\n")
            writer.writeheader()
            writer.writerows(righe)
        print(f"scritto {destinazione.relative_to(RADICE)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
