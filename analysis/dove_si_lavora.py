"""Dove si lavora e dove si abita: addetti ogni 100 abitanti, e perché.

    python analysis/dove_si_lavora.py
    python analysis/dove_si_lavora.py --save

`PROSSIMI-PASSI.md` §4. Il rapporto fra addetti e residenti separa i comuni dove
si va a lavorare da quelli da cui si esce la mattina, e in questa provincia i
due estremi sono lontanissimi: si va da meno di tre addetti ogni cento abitanti
a più di cento.

La parte interessante è che **gli estremi alti hanno cause opposte**, e senza il
dettaglio settoriale sembrerebbero lo stesso fenomeno: c'è il comune con
l'acciaieria e c'è il comune con gli alberghi. Da quando esistono le sezioni
Ateco per comune la distinzione si può mostrare invece che raccontare.

⚠️ **Non è un tasso di occupazione.** Il numeratore sono i posti di lavoro nel
comune, il denominatore le persone che ci risiedono: sono due popolazioni
diverse, e il rapporto misura il pendolarismo tanto quanto l'economia. Un comune
può avere pochi addetti ogni cento abitanti ed essere pienamente occupato — solo
altrove.

Confidenza: `derivato` (MET-4).
"""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _tabelle import (  # noqa: E402
    RADICE,
    anagrafica,
    leggi,
    numero,
    scrivi_csv,
    serie_imprese,
    serie_popolazione,
)

COLONNE = [
    "codice_istat",
    "comune",
    "addetti",
    "abitanti",
    "addetti_per_100_abitanti",
    "sezione_prevalente",
    "quota_sezione_prevalente",
]


def sezione_prevalente(anno: str) -> dict[str, tuple[str, str, float]]:
    """Per comune: (codice sezione, nome, quota) della sezione con più addetti."""
    per_comune: dict[str, dict[tuple[str, str], float]] = defaultdict(dict)
    for riga in leggi("imprese_sezioni_comuni.csv"):
        if riga["anno"] != anno or riga["indicatore"] != "addetti":
            continue
        valore = numero(riga["valore"])
        if valore is not None:
            per_comune[riga["codice_istat"]][(riga["sezione"], riga["nome_sezione"])] = valore

    fuori: dict[str, tuple[str, str, float]] = {}
    for codice, sezioni in per_comune.items():
        totale = sum(sezioni.values())
        if totale <= 0:
            continue
        (sezione, nome), valore = max(sezioni.items(), key=lambda kv: kv[1])
        fuori[codice] = (sezione, nome, valore / totale * 100)
    return fuori


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="dove_si_lavora")
    parser.add_argument("--save", action="store_true", help="scrive il CSV in analysis/output/")
    parser.add_argument("--quanti", type=int, default=10, help="quanti comuni per coda")
    args = parser.parse_args(argv)

    addetti = serie_imprese("addetti")
    popolazione = serie_popolazione()
    comuni = anagrafica()
    anno_asia = max(max(serie) for serie in addetti.values())
    prevalente = sezione_prevalente(anno_asia)

    righe: list[dict[str, str]] = []
    for codice, serie in addetti.items():
        abitanti_serie = popolazione.get(codice)
        if not abitanti_serie:
            continue
        occupati = serie[max(serie)]
        abitanti = abitanti_serie[max(abitanti_serie)]
        sezione, nome_sezione, quota = prevalente.get(codice, ("", "", 0.0))
        righe.append(
            {
                "codice_istat": codice,
                "comune": comuni[codice]["comune"],
                "addetti": f"{occupati:.1f}",
                "abitanti": f"{abitanti:.0f}",
                "addetti_per_100_abitanti": f"{occupati / abitanti * 100:.1f}",
                "sezione_prevalente": nome_sezione,
                "quota_sezione_prevalente": f"{quota:.1f}",
            }
        )
    righe.sort(key=lambda r: float(r["addetti_per_100_abitanti"]), reverse=True)

    print(f"Addetti ({anno_asia}) ogni 100 abitanti, {len(righe)} comuni")
    intestazione = f"  {'comune':24} {'add./100':>9} {'addetti':>9}  {'settore prevalente':38} {'quota':>6}"
    print(intestazione)
    print("  " + "-" * (len(intestazione) - 2))
    for riga in righe[: args.quanti] + [None] + righe[-args.quanti:]:
        if riga is None:
            print(f"  {'…':^24}")
            continue
        print(f"  {riga['comune'][:24]:24} {riga['addetti_per_100_abitanti']:>9} "
              f"{float(riga['addetti']):>9,.0f}  {riga['sezione_prevalente'][:38]:38} "
              f"{riga['quota_sezione_prevalente']:>6}")

    print("\nGli estremi alti non sono lo stesso fenomeno")
    for riga in righe[:3]:
        print(f"  {riga['comune']}: {riga['addetti_per_100_abitanti']} addetti ogni 100 abitanti, "
              f"{riga['quota_sezione_prevalente']} % in «{riga['sezione_prevalente']}»")
    print("  Un comune con l'acciaieria e un comune con gli alberghi arrivano allo stesso")
    print("  rapporto per strade opposte: senza il settore, la mappa li dipinge uguali.")

    valori = [float(r["addetti_per_100_abitanti"]) for r in righe]
    valori.sort()
    print(f"\n  mediana {valori[len(valori) // 2]:.1f} · "
          f"primo decile {valori[len(valori) // 10]:.1f} · "
          f"ultimo decile {valori[-len(valori) // 10]:.1f}")

    if args.save:
        destinazione = scrivi_csv("dove_si_lavora.csv", COLONNE, righe)
        print(f"\nscritto {destinazione.relative_to(RADICE)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
