"""Il crollo delle grandi unità locali del capoluogo, scomposto (MET-9).

    python analysis/decomposizione_capoluogo.py
    python analysis/decomposizione_capoluogo.py --save

È la questione aperta più importante del progetto, e l'origine della regola
MET-9: *nessun titolo su una variazione aggregata prima di averla scomposta*.
Il fatto di partenza è vero e vistoso — fra il 2018 e il 2023 le unità locali
con almeno 250 addetti del comune di Brescia perdono più di seimila addetti —
e il titolo facile («la grande industria bresciana se ne va») è falso.

Finora la scomposizione si fermava a metà, perché mancava la tabella:
`imprese_settore.csv` incrocia settore e territorio ma non la classe
dimensionale. Con `imprese_settore_classe.csv` — quattro richieste piccole,
territorio fissato — si può fare la domanda giusta.

**Le tre domande, in ordine.**

1. *Quali divisioni* fanno il calo della classe 250+?
2. Per ognuna: il calo si vede anche nel **totale della divisione** nello stesso
   comune, o solo nella classe grande? Se solo nella classe grande, gli addetti
   non sono spariti: sono passati a unità più piccole, e la variazione è una
   ricomposizione societaria, non una perdita di lavoro.
3. Lo stesso movimento si vede in **provincia**? Se sì, il fenomeno non è del
   capoluogo, e attribuirglielo sarebbe un errore di scala.

Confidenza: `osservato` per i conteggi, `derivato` per le differenze (MET-4).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _tabelle import CAPOLUOGO, PROVINCIA, RADICE, leggi, numero, scrivi_csv  # noqa: E402

CLASSE_GRANDE = "250+"
TOTALE_SETTORI = "0010"
# Le divisioni della manifattura secondo la sezione C dell'Ateco 2007.
MANIFATTURA = {f"{n:02d}" for n in range(10, 34)}

COLONNE = [
    "territorio",
    "ateco",
    "settore",
    "classe_addetti",
    "anno_iniziale",
    "anno_finale",
    "valore_iniziale",
    "valore_finale",
    "variazione",
]


def carica() -> dict[tuple[str, str, str, str], dict[str, float]]:
    """(territorio, ateco, classe, indicatore) -> anno -> valore."""
    dentro: dict[tuple[str, str, str, str], dict[str, float]] = {}
    etichette: dict[str, str] = {}
    for riga in leggi("imprese_settore_classe.csv"):
        valore = numero(riga["valore"])
        if valore is None:
            continue
        chiave = (riga["territorio"], riga["ateco"], riga["classe_addetti"], riga["indicatore"])
        dentro.setdefault(chiave, {})[riga["anno"]] = valore
        etichette[riga["ateco"]] = riga["settore"]
    carica.etichette = etichette  # type: ignore[attr-defined]
    return dentro


def estremi(serie: dict[str, float] | None, primo: str, ultimo: str) -> tuple[float, float]:
    """Una classe che sparisce non ha un valore: vale zero addetti **in quella
    classe**, che è diverso dal dato mancante di un comune non rilevato."""
    if serie is None:
        return 0.0, 0.0
    return serie.get(primo, 0.0), serie.get(ultimo, 0.0)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="decomposizione_capoluogo")
    parser.add_argument("--save", action="store_true", help="scrive il CSV in analysis/output/")
    parser.add_argument("--quante", type=int, default=8, help="quante divisioni mostrare")
    args = parser.parse_args(argv)

    dati = carica()
    etichette: dict[str, str] = carica.etichette  # type: ignore[attr-defined]
    anni = sorted({anno for serie in dati.values() for anno in serie})
    primo, ultimo = anni[0], anni[-1]

    def addetti(territorio: str, ateco: str, classe: str) -> tuple[float, float]:
        return estremi(dati.get((territorio, ateco, classe, "addetti")), primo, ultimo)

    def unita(territorio: str, ateco: str, classe: str) -> tuple[float, float]:
        return estremi(dati.get((territorio, ateco, classe, "unita_locali")), primo, ultimo)

    righe_csv: list[dict[str, str]] = []

    def registra(territorio: str, ateco: str, classe: str, coppia: tuple[float, float]) -> None:
        righe_csv.append(
            {
                "territorio": territorio,
                "ateco": ateco,
                "settore": etichette.get(ateco, ""),
                "classe_addetti": classe,
                "anno_iniziale": primo,
                "anno_finale": ultimo,
                "valore_iniziale": f"{coppia[0]:.1f}",
                "valore_finale": f"{coppia[1]:.1f}",
                "variazione": f"{coppia[1] - coppia[0]:.1f}",
            }
        )

    # --- 1. il fatto di partenza ----------------------------------------
    grande = addetti(CAPOLUOGO, TOTALE_SETTORI, CLASSE_GRANDE)
    tutto = addetti(CAPOLUOGO, TOTALE_SETTORI, "totale")
    registra(CAPOLUOGO, TOTALE_SETTORI, CLASSE_GRANDE, grande)
    registra(CAPOLUOGO, TOTALE_SETTORI, "totale", tutto)

    print(f"Comune di Brescia, {primo}–{ultimo}")
    print(f"  addetti in unità locali ≥250:  {grande[0]:>10,.0f} → {grande[1]:>10,.0f}   "
          f"({grande[1] - grande[0]:+,.0f})")
    print(f"  addetti in tutte le classi:    {tutto[0]:>10,.0f} → {tutto[1]:>10,.0f}   "
          f"({tutto[1] - tutto[0]:+,.0f})")
    print("  Il primo numero è spettacolare, il secondo è fermo. La differenza fra i due")
    print("  è tutta la questione.\n")

    # --- 2. quali divisioni ---------------------------------------------
    divisioni = sorted(
        {ateco for (terr, ateco, classe, _), _ in dati.items()
         if terr == CAPOLUOGO and classe == CLASSE_GRANDE and ateco != TOTALE_SETTORI}
    )
    variazioni = []
    for ateco in divisioni:
        iniziale, finale = addetti(CAPOLUOGO, ateco, CLASSE_GRANDE)
        variazioni.append((finale - iniziale, ateco, iniziale, finale))
    variazioni.sort()

    print(f"Le divisioni che fanno il calo della classe ≥250 nel capoluogo")
    intestazione = f"  {'div':>4} {'settore':44} {primo:>9} {ultimo:>9} {'var.':>9}"
    print(intestazione)
    print("  " + "-" * (len(intestazione) - 2))
    for variazione, ateco, iniziale, finale in variazioni[: args.quante]:
        print(f"  {ateco:>4} {etichette.get(ateco, '')[:44]:44} {iniziale:>9,.0f} {finale:>9,.0f} {variazione:>+9,.0f}")
        registra(CAPOLUOGO, ateco, CLASSE_GRANDE, (iniziale, finale))
    in_crescita = [v for v in variazioni if v[0] > 0]
    print(f"  … e {len(in_crescita)} divisioni in crescita, per {sum(v[0] for v in in_crescita):+,.0f} addetti")

    prime_due = [v[1] for v in variazioni[:2]]
    print(f"\n  Le prime due divisioni valgono {sum(v[0] for v in variazioni[:2]):+,.0f} addetti "
          f"su {grande[1] - grande[0]:+,.0f}: il resto della classe, nel complesso, tiene.")

    # --- 3. sparito o ricomposto? ---------------------------------------
    print(f"\nSparito o ricomposto? Per ogni divisione: la classe ≥250 contro il totale")
    intestazione = (f"  {'div':>4} {'≥250 capoluogo':>16} {'totale capoluogo':>18} "
                    f"{'unità locali':>14} {'totale provincia':>18}")
    print(intestazione)
    print("  " + "-" * (len(intestazione) - 2))
    for ateco in prime_due:
        grande_com = addetti(CAPOLUOGO, ateco, CLASSE_GRANDE)
        totale_com = addetti(CAPOLUOGO, ateco, "totale")
        unita_com = unita(CAPOLUOGO, ateco, "totale")
        totale_prov = addetti(PROVINCIA, ateco, "totale")
        registra(CAPOLUOGO, ateco, "totale", totale_com)
        registra(PROVINCIA, ateco, "totale", totale_prov)
        print(f"  {ateco:>4} {grande_com[1] - grande_com[0]:>+16,.0f} {totale_com[1] - totale_com[0]:>+18,.0f} "
              f"{unita_com[1] - unita_com[0]:>+14,.0f} {totale_prov[1] - totale_prov[0]:>+18,.0f}")
        print(f"       {etichette.get(ateco, '')[:70]}")

    # --- 4. la manifattura ----------------------------------------------
    print("\nE la manifattura grande, quella del titolo?")
    manifattura_grande = [0.0, 0.0]
    manifattura_totale = [0.0, 0.0]
    for ateco in divisioni:
        if ateco not in MANIFATTURA:
            continue
        iniziale, finale = addetti(CAPOLUOGO, ateco, CLASSE_GRANDE)
        manifattura_grande[0] += iniziale
        manifattura_grande[1] += finale
        iniziale, finale = addetti(CAPOLUOGO, ateco, "totale")
        manifattura_totale[0] += iniziale
        manifattura_totale[1] += finale
    registra(CAPOLUOGO, "C", CLASSE_GRANDE, (manifattura_grande[0], manifattura_grande[1]))
    registra(CAPOLUOGO, "C", "totale", (manifattura_totale[0], manifattura_totale[1]))
    print(f"  divisioni 10–33, classe ≥250:  {manifattura_grande[0]:>10,.0f} → {manifattura_grande[1]:>10,.0f}   "
          f"({manifattura_grande[1] - manifattura_grande[0]:+,.0f})")
    print(f"  divisioni 10–33, tutte:        {manifattura_totale[0]:>10,.0f} → {manifattura_totale[1]:>10,.0f}   "
          f"({manifattura_totale[1] - manifattura_totale[0]:+,.0f})")

    # --- 5. quando ------------------------------------------------------
    print("\nQuando succede (addetti nella classe ≥250, capoluogo)")
    serie = dati.get((CAPOLUOGO, TOTALE_SETTORI, CLASSE_GRANDE, "addetti"), {})
    for anno in anni:
        valore = serie.get(anno)
        barra = "█" * int((valore or 0) / 500)
        print(f"  {anno}  {valore if valore is None else format(valore, ',.0f'):>10}  {barra}")
    print("  La rottura è nel 2020, non una discesa lenta: qualunque tasso annualizzato")
    print("  su questa serie descrive un movimento che non è mai avvenuto (MET-8).")

    if args.save:
        destinazione = scrivi_csv("decomposizione_capoluogo.csv", COLONNE, righe_csv)
        print(f"\nscritto {destinazione.relative_to(RADICE)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
