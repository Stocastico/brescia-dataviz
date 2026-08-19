"""Le due economie del bresciano: manifattura e Garda, comune per comune.

    python analysis/due_economie.py
    python analysis/due_economie.py --save

Il terzo asse del brief, e quello che finora non si poteva disegnare: il
dettaglio settoriale esisteva solo per il capoluogo e per la provincia. Con
`imprese_sezioni_comuni.csv` esiste per tutti i 205 comuni, e la domanda
diventa misurabile: **quanto è vero che questa provincia sono due province?**

Tre letture, in ordine di forza:

1. la **quota di addetti** nella manifattura (sezione Ateco C) e in alloggio e
   ristorazione (sezione I), comune per comune;
2. la **specializzazione**, cioè la differenza fra le due quote: un solo numero
   che dice da che parte sta un comune;
3. il **quoziente di localizzazione**, che confronta la quota del comune con
   quella provinciale: dice se un comune è manifatturiero *in assoluto* o solo
   *rispetto agli altri*, e le due cose non coincidono.

⚠️ ASIA non copre agricoltura, pubblica amministrazione, istruzione pubblica e
servizi domestici. Il denominatore di ogni quota è **l'economia che il registro
osserva**, non tutta l'economia del comune: nella Bassa agricola questo conta,
e va detto ogni volta.

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
    pearson,
    scrivi_csv,
    spearman,
)

MANIFATTURA = "C"
ALLOGGIO = "I"

COLONNE = [
    "codice_istat",
    "comune",
    "anno",
    "addetti_totali",
    "quota_manifattura",
    "quota_alloggio",
    "specializzazione",
    "ql_manifattura",
    "ql_alloggio",
    "profilo",
]


def quote(anno: str) -> tuple[dict[str, float], dict[str, dict[str, float]]]:
    """Addetti per comune e sezione, più il totale delle sezioni osservate."""
    per_sezione: dict[str, dict[str, float]] = defaultdict(dict)
    totali: dict[str, float] = defaultdict(float)
    for riga in leggi("imprese_sezioni_comuni.csv"):
        if riga["anno"] != anno or riga["indicatore"] != "addetti":
            continue
        valore = numero(riga["valore"])
        if valore is None:
            continue
        per_sezione[riga["codice_istat"]][riga["sezione"]] = valore
        totali[riga["codice_istat"]] += valore
    return dict(totali), dict(per_sezione)


def profilo(quota_manifattura: float, quota_alloggio: float) -> str:
    """Un'etichetta descrittiva, non una classificazione ufficiale."""
    if quota_manifattura >= 50:
        return "manifatturiero"
    if quota_alloggio >= 25:
        return "turistico"
    if quota_manifattura >= 30:
        return "misto industriale"
    return "terziario o non specializzato"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="due_economie")
    parser.add_argument("--anno", default=None, help="anno da analizzare (default: l'ultimo)")
    parser.add_argument("--save", action="store_true", help="scrive il CSV in analysis/output/")
    parser.add_argument("--quanti", type=int, default=8, help="quanti comuni per coda")
    args = parser.parse_args(argv)

    righe_tabella = leggi("imprese_sezioni_comuni.csv")
    anno = args.anno or max(r["anno"] for r in righe_tabella)
    totali, per_sezione = quote(anno)
    comuni = anagrafica()

    totale_provinciale = sum(totali.values())
    manifattura_provinciale = sum(s.get(MANIFATTURA, 0.0) for s in per_sezione.values()) / totale_provinciale * 100
    alloggio_provinciale = sum(s.get(ALLOGGIO, 0.0) for s in per_sezione.values()) / totale_provinciale * 100

    righe: list[dict[str, str]] = []
    for codice, totale in totali.items():
        if totale <= 0:
            continue
        quota_m = per_sezione[codice].get(MANIFATTURA, 0.0) / totale * 100
        quota_a = per_sezione[codice].get(ALLOGGIO, 0.0) / totale * 100
        righe.append(
            {
                "codice_istat": codice,
                "comune": comuni[codice]["comune"],
                "anno": anno,
                "addetti_totali": f"{totale:.1f}",
                "quota_manifattura": f"{quota_m:.2f}",
                "quota_alloggio": f"{quota_a:.2f}",
                "specializzazione": f"{quota_m - quota_a:.2f}",
                "ql_manifattura": f"{quota_m / manifattura_provinciale:.3f}",
                "ql_alloggio": f"{quota_a / alloggio_provinciale:.3f}",
                "profilo": profilo(quota_m, quota_a),
            }
        )
    righe.sort(key=lambda r: float(r["specializzazione"]), reverse=True)

    print(f"Sezioni Ateco per comune, {anno} — {len(righe)} comuni")
    print(f"In provincia: manifattura {manifattura_provinciale:.1f} %, "
          f"alloggio e ristorazione {alloggio_provinciale:.1f} % degli addetti osservati da ASIA.\n")

    intestazione = f"  {'comune':26} {'addetti':>9} {'manif.':>8} {'alloggio':>9} {'specializz.':>12}"
    print("I due estremi della specializzazione")
    print(intestazione)
    print("  " + "-" * (len(intestazione) - 2))
    for riga in righe[: args.quanti] + [None] + righe[-args.quanti:]:
        if riga is None:
            print(f"  {'…':^26}")
            continue
        print(f"  {riga['comune'][:26]:26} {float(riga['addetti_totali']):>9,.0f} "
              f"{riga['quota_manifattura']:>8} {riga['quota_alloggio']:>9} {riga['specializzazione']:>12}")

    conteggi: dict[str, int] = defaultdict(int)
    for riga in righe:
        conteggi[riga["profilo"]] += 1
    print("\nProfili (etichette descrittive, non una classificazione ufficiale)")
    for nome_profilo, quanti in sorted(conteggi.items(), key=lambda kv: -kv[1]):
        quota_addetti = sum(
            float(r["addetti_totali"]) for r in righe if r["profilo"] == nome_profilo
        ) / totale_provinciale * 100
        print(f"  {nome_profilo:32} {quanti:>4} comuni   {quota_addetti:>5.1f} % degli addetti")

    x = [float(r["quota_manifattura"]) for r in righe]
    y = [float(r["quota_alloggio"]) for r in righe]
    print("\nLe due quote sono alternative?")
    print(f"  Pearson  {pearson(x, y):+.3f}")
    print(f"  Spearman {spearman(x, y):+.3f}")
    print("  Sono due quote dello stesso totale, quindi una correlazione negativa è")
    print("  in parte aritmetica: crescendo l'una l'altra ha meno spazio. Il numero")
    print("  dice quanto la sostituzione è netta, non che una causi l'altra.")

    if args.save:
        destinazione = scrivi_csv("due_economie.csv", COLONNE, righe)
        print(f"\nscritto {destinazione.relative_to(RADICE)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
