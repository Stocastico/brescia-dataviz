"""Livelli contro variazioni: i quattro quadranti, comune per comune.

    python analysis/livelli_e_variazioni.py             # i tre indicatori
    python analysis/livelli_e_variazioni.py reddito     # uno solo
    python analysis/livelli_e_variazioni.py --save      # + analysis/output/livelli_e_variazioni.csv

`PROSSIMI-PASSI.md` §5.2, secondo punto. Il livello sull'asse x, la velocità di
cambio sull'asse y: i comuni si dividono in quattro quadranti rispetto alle due
mediane, e la domanda «chi sta alto» smette di confondersi con «chi sta
salendo» (MET-7).

| Quadrante | Lettura |
|---|---|
| alto e in crescita | si allontana verso l'alto |
| basso e in crescita | recupera |
| alto e in calo | scende dal punto più alto |
| basso e in calo | resta indietro e peggiora |

I nomi dei quadranti sono descrizioni di posizione, non giudizi: un comune
turistico «in calo» sulle presenze può semplicemente tornare alla normalità
dopo un picco.

**La domanda vera è il segno della correlazione fra livello e variazione.**
Negativa significa convergenza — chi partiva sotto cresce più in fretta;
positiva significa divergenza, cioè polarizzazione. Il numero si riporta in
coppia, Pearson e Spearman (MET-6), e ricalcolato senza gli outlier noti
(MET-5): il capoluogo, che è un ordine di grandezza sopra tutti, e i comuni a
forte vocazione turistica.

⚠️ **Con quale livello.** Il quadrante usa il livello **finale**, perché
descrive il presente: dov'è alto *oggi* e dove sta salendo. La correlazione no.
Correlare il livello finale con la crescita è un artefatto: il livello finale
*contiene* la crescita, e chi è cresciuto di più finisce meccanicamente più in
alto. Il test di convergenza si fa sul livello **iniziale**, ed è l'unico dei
due che risponda alla domanda. Lo script stampa entrambi proprio perché la
differenza fra i due numeri è il punto: quando divergono, il primo è
l'artefatto.

**Come sono definiti i turistici**, perché non è una lista presa altrove: sono
i comuni con **almeno 25 presenze turistiche per abitante** nel 2024, calcolate
dalle tabelle del progetto. Ne risultano 21, il Garda più l'alta Valle Camonica
e il lago d'Idro. La soglia è arbitraria come tutte le soglie: serve a vedere se
un risultato dipende da loro, non a definire una categoria.

Confidenza: `derivato` (MET-4).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _tabelle import (  # noqa: E402
    CAPOLUOGO,
    RADICE,
    anagrafica,
    numero,
    pearson,
    scrivi_csv,
    serie_imprese,
    serie_popolazione,
    serie_reddito,
    sintesi,
    spearman,
    tasso_annualizzato,
)

PRESENZE_PER_ABITANTE_TURISTICO = 25.0

COLONNE = [
    "indicatore",
    "codice_istat",
    "comune",
    "capoluogo",
    "turistico",
    "anno_iniziale",
    "anno_finale",
    "livello_iniziale",
    "livello_finale",
    "tasso_annualizzato",
    "quadrante",
]


def comuni_turistici() -> set[str]:
    """Definiti dai dati, non da una lista esterna: vedi il docstring."""
    turistici = set()
    for codice, riga in sintesi().items():
        presenze = numero(riga["presenze_turistiche_2024"])
        abitanti = numero(riga["popolazione_2024"])
        if presenze and abitanti and presenze / abitanti >= PRESENZE_PER_ABITANTE_TURISTICO:
            turistici.add(codice)
    return turistici


def coppie(indicatore: str) -> tuple[str, str, dict[str, tuple[str, str, float, float, float]]]:
    """Per comune: (anno iniziale, anno finale, livello iniziale, finale, tasso)."""
    if indicatore == "addetti":
        etichetta, unita = "Addetti ogni 100 abitanti", "addetti/100 ab."
        serie = serie_imprese("addetti")
        popolazione = serie_popolazione()

        def livello(codice: str, anno: str, valore: float) -> float | None:
            # Il rapporto va preso **allo stesso anno** su entrambi i termini,
            # altrimenti la variazione del denominatore entra nel numeratore.
            abitanti = popolazione.get(codice, {}).get(anno)
            return None if not abitanti else valore / abitanti * 100

    elif indicatore == "reddito":
        etichetta, unita = "Reddito medio per contribuente", "euro correnti"
        serie = serie_reddito()

        def livello(codice: str, anno: str, valore: float) -> float | None:
            return valore

    elif indicatore == "popolazione":
        etichetta, unita = "Popolazione residente", "abitanti"
        serie = serie_popolazione()

        def livello(codice: str, anno: str, valore: float) -> float | None:
            return valore

    else:  # pragma: no cover - il parser filtra prima
        raise ValueError(indicatore)

    risultato: dict[str, tuple[str, str, float, float, float]] = {}
    for codice, valori in serie.items():
        anni = sorted(valori)
        primo, ultimo = anni[0], anni[-1]
        iniziale = livello(codice, primo, valori[primo])
        finale = livello(codice, ultimo, valori[ultimo])
        tasso = tasso_annualizzato(valori[primo], valori[ultimo], int(ultimo) - int(primo))
        if iniziale is None or finale is None or tasso is None:
            continue
        risultato[codice] = (primo, ultimo, iniziale, finale, tasso)
    return etichetta, unita, risultato


def mediana(valori: list[float]) -> float:
    ordinati = sorted(valori)
    meta = len(ordinati) // 2
    if len(ordinati) % 2:
        return ordinati[meta]
    return (ordinati[meta - 1] + ordinati[meta]) / 2


def quadrante(livello: float, tasso: float, x0: float, y0: float) -> str:
    alto = "alto" if livello >= x0 else "basso"
    verso = "in crescita" if tasso >= y0 else "in calo"
    return f"{alto} e {verso}"


def correlazioni(punti: list[tuple[float, float]]) -> tuple[float | None, float | None]:
    x = [p[0] for p in punti]
    y = [p[1] for p in punti]
    return pearson(x, y), spearman(x, y)


def formatta(valore: float | None) -> str:
    return "n.d." if valore is None else f"{valore:+.3f}"


def analizza(indicatore: str, quanti: int) -> list[dict[str, str]]:
    etichetta, unita, dati = coppie(indicatore)
    comuni = anagrafica()
    turistici = comuni_turistici()

    x0 = mediana([finale for _, _, _, finale, _ in dati.values()])
    y0 = mediana([tasso for _, _, _, _, tasso in dati.values()])

    righe: list[dict[str, str]] = []
    for codice, (primo, ultimo, iniziale, finale, tasso) in dati.items():
        righe.append(
            {
                "indicatore": indicatore,
                "codice_istat": codice,
                "comune": comuni[codice]["comune"],
                "capoluogo": comuni[codice]["capoluogo"],
                "turistico": "1" if codice in turistici else "0",
                "anno_iniziale": primo,
                "anno_finale": ultimo,
                "livello_iniziale": f"{iniziale:.2f}",
                "livello_finale": f"{finale:.2f}",
                "tasso_annualizzato": f"{tasso:.3f}",
                "quadrante": quadrante(finale, tasso, x0, y0),
            }
        )
    righe.sort(key=lambda r: float(r["tasso_annualizzato"]), reverse=True)

    primo, ultimo = righe[0]["anno_iniziale"], righe[0]["anno_finale"]
    print(f"\n{etichetta} — {primo}–{ultimo} ({unita})")
    print(f"mediane sul {ultimo}: livello {x0:,.1f} · tasso {y0:+.3f} %/anno")

    conteggi: dict[str, list[str]] = {}
    for riga in righe:
        conteggi.setdefault(riga["quadrante"], []).append(riga["comune"])
    for nome_quadrante in (
        "alto e in crescita",
        "basso e in crescita",
        "alto e in calo",
        "basso e in calo",
    ):
        dentro = conteggi.get(nome_quadrante, [])
        esempi = ", ".join(sorted(dentro)[:quanti])
        print(f"  {nome_quadrante:20} {len(dentro):>4} comuni   {esempi}…")

    insiemi = {
        "tutti i comuni": righe,
        "senza il capoluogo": [r for r in righe if r["codice_istat"] != CAPOLUOGO],
        "senza capoluogo e turistici": [
            r for r in righe if r["codice_istat"] != CAPOLUOGO and r["turistico"] == "0"
        ],
    }

    for colonna, titolo in (
        ("livello_iniziale", f"convergenza — livello {primo} contro crescita (il test vero)"),
        ("livello_finale", f"livello {ultimo} contro crescita (artefatto: il livello contiene la crescita)"),
    ):
        print(f"  {titolo}")
        print(f"    {'':34} {'Pearson':>8} {'Spearman':>10}")
        for nome_insieme, sotto in insiemi.items():
            p, sp = correlazioni([(float(r[colonna]), float(r["tasso_annualizzato"])) for r in sotto])
            print(f"    {nome_insieme:34} {formatta(p):>8} {formatta(sp):>10}   (n={len(sotto)})")

    return righe


def main(argv: list[str] | None = None) -> int:
    indicatori = ["addetti", "reddito", "popolazione"]
    parser = argparse.ArgumentParser(prog="livelli_e_variazioni")
    parser.add_argument("indicatori", nargs="*", metavar="INDICATORE",
                        help=f"quali analizzare fra {', '.join(indicatori)} (default: tutti)")
    parser.add_argument("--save", action="store_true", help="scrive il CSV in analysis/output/")
    parser.add_argument("--esempi", type=int, default=4, help="quanti comuni citare per quadrante")
    args = parser.parse_args(argv)

    scelti = args.indicatori or indicatori
    ignoti = [i for i in scelti if i not in indicatori]
    if ignoti:
        parser.error(f"indicatore sconosciuto: {', '.join(ignoti)}")

    tutte: list[dict[str, str]] = []
    for indicatore in scelti:
        tutte.extend(analizza(indicatore, args.esempi))

    if args.save:
        destinazione = scrivi_csv("livelli_e_variazioni.csv", COLONNE, tutte)
        print(f"\nscritto {destinazione.relative_to(RADICE)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
