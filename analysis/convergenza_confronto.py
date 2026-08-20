"""La convergenza dei redditi è bresciana o è italiana?

    python analysis/convergenza_confronto.py
    python analysis/convergenza_confronto.py --save

MET-14 applicata al risultato più netto delle analisi. Fra il 2012 e il 2023 il
reddito per contribuente dei comuni bresciani converge — chi partiva sotto
cresce più in fretta, con una correlazione di −0,45 fra livello iniziale e
crescita — e finché quel numero sta da solo non si sa che cosa descriva. La
convergenza fra comuni potrebbe essere un fatto italiano, e allora «i redditi
bresciani convergono» racconta il paese.

Il confronto qui è con **Bergamo**: stessa dimensione, storia industriale
parallela, e sul registro delle imprese la provincia più simile a Brescia su
quasi ogni indicatore. Non è «l'Italia» — per quella servirebbe scaricare i
redditi di tutti gli ottomila comuni, che la fonte non lascia fare in un colpo
solo — ma è il controllo che costa venti richieste invece di un giorno.

Ogni correlazione è riportata in coppia (MET-6) e calcolata sul livello
**iniziale** (MET-12), con accanto la versione sbagliata per mostrare che
l'artefatto si comporta allo stesso modo nelle due province.

Confidenza: `derivato` (MET-4).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _tabelle import (  # noqa: E402
    RADICE,
    pearson,
    scrivi_csv,
    serie_reddito,
    spearman,
    tasso_annualizzato,
)

CONFRONTO = "redditi_comuni_confronto.csv"

COLONNE = [
    "territorio",
    "comuni",
    "anno_iniziale",
    "anno_finale",
    "reddito_mediano_iniziale",
    "reddito_mediano_finale",
    "crescita_mediana",
    "rapporto_max_min_iniziale",
    "rapporto_max_min_finale",
    "convergenza_pearson",
    "convergenza_spearman",
    "artefatto_pearson",
]


def mediana(valori: list[float]) -> float:
    ordinati = sorted(valori)
    meta = len(ordinati) // 2
    return ordinati[meta] if len(ordinati) % 2 else (ordinati[meta - 1] + ordinati[meta]) / 2


def misura(nome: str, serie: dict[str, dict[str, float]]) -> dict[str, str]:
    codici = sorted(serie)
    anni = sorted({a for valori in serie.values() for a in valori})
    primo, ultimo = anni[0], anni[-1]
    codici = [c for c in codici if primo in serie[c] and ultimo in serie[c]]

    iniziali = [serie[c][primo] for c in codici]
    finali = [serie[c][ultimo] for c in codici]
    crescite = [
        tasso_annualizzato(serie[c][primo], serie[c][ultimo], int(ultimo) - int(primo))
        for c in codici
    ]

    return {
        "territorio": nome,
        "comuni": str(len(codici)),
        "anno_iniziale": primo,
        "anno_finale": ultimo,
        "reddito_mediano_iniziale": f"{mediana(iniziali):.0f}",
        "reddito_mediano_finale": f"{mediana(finali):.0f}",
        "crescita_mediana": f"{mediana(crescite):.2f}",
        "rapporto_max_min_iniziale": f"{max(iniziali) / min(iniziali):.2f}",
        "rapporto_max_min_finale": f"{max(finali) / min(finali):.2f}",
        "convergenza_pearson": f"{pearson(iniziali, crescite):.3f}",
        "convergenza_spearman": f"{spearman(iniziali, crescite):.3f}",
        "artefatto_pearson": f"{pearson(finali, crescite):.3f}",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="convergenza_confronto")
    parser.add_argument("--save", action="store_true", help="scrive il CSV in analysis/output/")
    args = parser.parse_args(argv)

    if not (RADICE / "dati" / "processed" / CONFRONTO).exists():
        print(f"manca {CONFRONTO}: lanciare `python -m brescia_pipeline.build redditi_confronto`",
              file=sys.stderr)
        return 1

    righe = [
        misura("Brescia", serie_reddito()),
        misura("Bergamo", serie_reddito(CONFRONTO, provincia="016")),
    ]

    campi = [
        ("comuni", "comuni"),
        ("reddito_mediano_iniziale", "reddito mediano iniziale"),
        ("reddito_mediano_finale", "reddito mediano finale"),
        ("crescita_mediana", "crescita mediana (%/anno)"),
        ("rapporto_max_min_iniziale", "rapporto ricco/povero iniziale"),
        ("rapporto_max_min_finale", "rapporto ricco/povero finale"),
        ("convergenza_pearson", "convergenza, Pearson"),
        ("convergenza_spearman", "convergenza, Spearman"),
        ("artefatto_pearson", "…sul livello finale (l'artefatto)"),
    ]

    print(f"Reddito per contribuente, {righe[0]['anno_iniziale']}–{righe[0]['anno_finale']}\n")
    intestazione = f"  {'':34} {righe[0]['territorio']:>12} {righe[1]['territorio']:>12}"
    print(intestazione)
    print("  " + "-" * (len(intestazione) - 2))
    for chiave, etichetta in campi:
        print(f"  {etichetta:34} {righe[0][chiave]:>12} {righe[1][chiave]:>12}")

    bs = float(righe[0]["convergenza_pearson"])
    bg = float(righe[1]["convergenza_pearson"])
    print("\nCome si legge")
    if bs < -0.2 and bg < -0.2:
        print("  Convergono entrambe, e con forza simile: la convergenza dei redditi comunali")
        print("  **non è un fatto bresciano**. Nel testo va scritta come una cosa che a Brescia")
        print("  succede, non come una cosa che a Brescia succede a differenza di altrove.")
    elif bs < -0.2:
        print("  Brescia converge e la provincia di confronto no: qui il risultato è")
        print("  effettivamente bresciano, ed è un caso su due province — non una prova.")
    else:
        print("  Nessuna delle due converge in modo apprezzabile.")
    print("  In ogni caso due province non sono l'Italia: questo controllo esclude che il")
    print("  risultato sia un artefatto locale, non stabilisce che sia generale.")

    if args.save:
        destinazione = scrivi_csv("convergenza_confronto.csv", COLONNE, righe)
        print(f"\nscritto {destinazione.relative_to(RADICE)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
