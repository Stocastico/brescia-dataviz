"""Velocità di cambio di addetti, unità locali e reddito, comune per comune.

    python analysis/velocita_di_cambio.py                  # le code dei tre indicatori
    python analysis/velocita_di_cambio.py addetti --tutti  # un indicatore solo, per intero
    python analysis/velocita_di_cambio.py --save           # + analysis/output/velocita_di_cambio.csv

Seguito diretto di `variazione_popolazione.py`, con lo stesso schema esteso ai
tre indicatori che restavano (`PROSSIMI-PASSI.md` §5.2): tasso annualizzato
composto fra il primo e l'ultimo anno di ciascuna serie, per ognuno dei 205
comuni. La domanda è sempre quella di MET-7: **dov'è alto** e **dove sta
cambiando in fretta** sono due mappe diverse, e la seconda è quasi sempre la
più interessante.

Le finestre non coincidono, e non vanno appiattite sulla più corta:

| Indicatore | Finestra | Fonte |
|---|---|---|
| addetti, unità locali | 2018–2023 | ISTAT — ASIA unità locali |
| reddito per contribuente | 2012–2023 | MEF — dichiarazioni dei redditi |

Cosa questi numeri **non** dicono:

- il reddito è in **euro correnti**, e questo script non lo deflaziona: fra 2012
  e 2023 buona parte della crescita è inflazione (21,4 %), e la mediana comunale
  passa da +2,23 % l'anno a +0,44 % in euro costanti. Il deflatore c'è da
  settembre 2026 — `_tabelle.in_euro_costanti()`, MET-20 — quindi qui la scelta
  di restare nominali è **una scelta**: questo script confronta serie diverse
  sulla stessa scala, e deflazionarne una sola le renderebbe incomparabili. Chi
  legge un tasso di crescita del reddito da qui deve toglierci l'inflazione;
- gli addetti sono delle **unità locali**, non delle imprese: una sede
  secondaria conta nel comune dove sta, e un trasferimento fra comuni si legge
  come crollo di uno e boom dell'altro;
- il tasso composto **passa sopra il 2020–2021** come se nulla fosse (MET-8):
  su questa finestra è una media che nasconde una discontinuità;
- sui comuni piccoli poche unità fanno percentuali vistose. La colonna del
  valore iniziale serve a ricordarlo.

Confidenza: `derivato` (MET-4).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _tabelle import (  # noqa: E402
    RADICE,
    SERIE_DISPONIBILI,
    anagrafica,
    scrivi_csv,
    tasso_annualizzato,
)

COLONNE = [
    "indicatore",
    "codice_istat",
    "comune",
    "capoluogo",
    "anno_iniziale",
    "anno_finale",
    "valore_iniziale",
    "valore_finale",
    "variazione_assoluta",
    "variazione_percentuale",
    "tasso_annualizzato",
]

INDICATORI = ["addetti", "unita_locali", "reddito"]


def calcola(indicatore: str) -> list[dict[str, str]]:
    etichetta, _, caricatore = SERIE_DISPONIBILI[indicatore]
    comuni = anagrafica()
    righe: list[dict[str, str]] = []

    for codice, serie in caricatore().items():
        anni = sorted(serie)
        primo, ultimo = anni[0], anni[-1]
        iniziale, finale = serie[primo], serie[ultimo]
        tasso = tasso_annualizzato(iniziale, finale, int(ultimo) - int(primo))
        if tasso is None:
            continue  # serie che parte o finisce a zero: nessun tasso definito
        righe.append(
            {
                "indicatore": indicatore,
                "codice_istat": codice,
                "comune": comuni[codice]["comune"],
                "capoluogo": comuni[codice]["capoluogo"],
                "anno_iniziale": primo,
                "anno_finale": ultimo,
                "valore_iniziale": f"{iniziale:.1f}",
                "valore_finale": f"{finale:.1f}",
                "variazione_assoluta": f"{finale - iniziale:.1f}",
                "variazione_percentuale": f"{(finale / iniziale - 1) * 100:.2f}",
                "tasso_annualizzato": f"{tasso:.3f}",
            }
        )

    righe.sort(key=lambda r: float(r["tasso_annualizzato"]), reverse=True)
    return righe


def stampa(indicatore: str, righe: list[dict[str, str]], quante: int | None) -> None:
    etichetta, unita, _ = SERIE_DISPONIBILI[indicatore]
    primo, ultimo = righe[0]["anno_iniziale"], righe[0]["anno_finale"]
    print(f"\n{etichetta} — {primo}–{ultimo} ({unita})")
    intestazione = f"{'comune':28} {primo:>10} {ultimo:>10} {'assoluta':>10} {'%/anno':>8}"
    print(intestazione)
    print("-" * len(intestazione))

    def blocco(sotto: list[dict[str, str]]) -> None:
        for riga in sotto:
            marchio = "*" if riga["capoluogo"] == "1" else " "
            print(
                f"{marchio}{riga['comune'][:27]:27} {riga['valore_iniziale']:>10} "
                f"{riga['valore_finale']:>10} {riga['variazione_assoluta']:>10} "
                f"{riga['tasso_annualizzato']:>8}"
            )

    if quante is None:
        blocco(righe)
    else:
        blocco(righe[:quante])
        print(f"{'…':^28}")
        blocco(righe[-quante:])
    print("-" * len(intestazione))

    iniziale = sum(float(r["valore_iniziale"]) for r in righe)
    finale = sum(float(r["valore_finale"]) for r in righe)
    durata = int(ultimo) - int(primo)
    if indicatore == "reddito":
        # Il reddito è un rapporto: sommarlo fra comuni non significa niente.
        # L'aggregato onesto è la mediana dei comuni.
        ordinati = sorted(float(r["tasso_annualizzato"]) for r in righe)
        mediano = ordinati[len(ordinati) // 2]
        print(f"{'mediana dei comuni':28} {'':>10} {'':>10} {'':>10} {mediano:>8.3f}")
    else:
        print(
            f"{'provincia':28} {iniziale:>10.1f} {finale:>10.1f} "
            f"{finale - iniziale:>10.1f} "
            f"{tasso_annualizzato(iniziale, finale, durata):>8.3f}"
        )

    in_calo = sum(1 for r in righe if float(r["variazione_assoluta"]) < 0)
    print(f"{in_calo} comuni su {len(righe)} in calo fra il {primo} e il {ultimo}.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="velocita_di_cambio")
    parser.add_argument(
        "indicatori",
        nargs="*",
        metavar="INDICATORE",
        help=f"quali indicatori calcolare fra {', '.join(INDICATORI)} (default: tutti)",
    )
    parser.add_argument("--save", action="store_true", help="scrive il CSV in analysis/output/")
    parser.add_argument("--tutti", action="store_true", help="stampa tutti i comuni, non solo le code")
    parser.add_argument("--code", type=int, default=10, help="quanti comuni per coda (default 10)")
    args = parser.parse_args(argv)

    scelti = args.indicatori or INDICATORI
    ignoti = [i for i in scelti if i not in INDICATORI]
    if ignoti:
        parser.error(f"indicatore sconosciuto: {', '.join(ignoti)}")
    tutte: list[dict[str, str]] = []
    for indicatore in scelti:
        righe = calcola(indicatore)
        stampa(indicatore, righe, None if args.tutti else args.code)
        tutte.extend(righe)

    if args.save:
        destinazione = scrivi_csv("velocita_di_cambio.csv", COLONNE, tutte)
        print(f"\nscritto {destinazione.relative_to(RADICE)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
