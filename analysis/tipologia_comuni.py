"""Tipologia dei comuni: k-means con seme fisso, reimplementato a mano.

    python analysis/tipologia_comuni.py
    python analysis/tipologia_comuni.py --gruppi 6 --save

`PROSSIMI-PASSI.md` §5.2, terzo punto. Raggruppa i 205 comuni su poche variabili
strutturali e restituisce **profili descrittivi**, non una verità: k-means trova
gruppi anche in dati senza gruppi, e cambiare `k` cambia la storia. Ogni volta
che questi profili compaiono in un grafico devono comparire con questa
avvertenza attaccata.

**Le variabili** (tutte allo stesso anno dove possibile, tutte standardizzate
prima di raggruppare, perché altrimenti la densità in abitanti per km² dominerebbe
le quote in percentuale):

| Variabile | Perché |
|---|---|
| quota di addetti nella manifattura | l'asse produttivo del territorio |
| quota in alloggio e ristorazione | l'altra economia, quella del lago |
| addetti per unità locale | dimensione d'impresa: la domanda originaria del progetto |
| addetti ogni 100 abitanti | se un comune è un posto dove si lavora o dove si dorme |
| reddito per contribuente | il tenore economico |
| densità abitativa (logaritmo) | montagna contro pianura, in una variabile sola |

La densità entra in **logaritmo** perché va da 8 a 2.500 abitanti per km²: senza
logaritmo la standardizzazione la trasforma in un indicatore binario città/non
città e schiaccia tutto il resto.

**Niente scikit-learn**, come tutto il resto di questa cartella: k-means è
trenta righe, e in cambio il progetto resta installabile ovunque. L'inizializzazione
è k-means++ con seme fisso (MET-1), quindi due esecuzioni danno lo stesso
risultato — che è il minimo per poter citare un numero.

⚠️ **Gli outlier tirano i gruppi.** Un comune con 133 addetti ogni 100 abitanti
sta quattro scarti fuori su quella variabile, e k-means lo mette da qualche
parte comunque: finisce nel gruppo che minimizza la distanza, non in quello che
lo descrive. Lo script stampa in coda i comuni **più lontani dal proprio
centro**: sono quelli per cui l'etichetta di gruppo va ignorata.

Confidenza: `derivato` (MET-4).
"""

from __future__ import annotations

import argparse
import math
import random
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _tabelle import (  # noqa: E402
    CAPOLUOGO,
    RADICE,
    anagrafica,
    geometria,
    leggi,
    media,
    numero,
    scrivi_csv,
    serie_imprese,
    serie_popolazione,
    serie_reddito,
)

SEME = 20260819
VARIABILI = [
    "quota_manifattura",
    "quota_alloggio",
    "addetti_per_unita",
    "addetti_per_100_abitanti",
    "reddito",
    "log_densita",
]

COLONNE = ["codice_istat", "comune", "gruppo", "profilo", *VARIABILI]


def costruisci_tabella() -> tuple[list[str], dict[str, list[float]]]:
    sezioni = leggi("imprese_sezioni_comuni.csv")
    anno = max(r["anno"] for r in sezioni)

    per_sezione: dict[str, dict[str, float]] = defaultdict(dict)
    totale_sezioni: dict[str, float] = defaultdict(float)
    for riga in sezioni:
        if riga["anno"] != anno or riga["indicatore"] != "addetti":
            continue
        valore = numero(riga["valore"])
        if valore is None:
            continue
        per_sezione[riga["codice_istat"]][riga["sezione"]] = valore
        totale_sezioni[riga["codice_istat"]] += valore

    addetti = serie_imprese("addetti")
    unita = serie_imprese("unita_locali")
    popolazione = serie_popolazione()
    reddito = serie_reddito()
    geo = geometria()

    righe: dict[str, list[float]] = {}
    for codice, totale in totale_sezioni.items():
        anni_addetti = addetti.get(codice, {})
        anni_unita = unita.get(codice, {})
        anni_pop = popolazione.get(codice, {})
        anni_reddito = reddito.get(codice, {})
        if not (totale and anni_addetti and anni_unita and anni_pop and anni_reddito):
            continue
        ultimo_asia = max(anni_addetti)
        area = float(geo[codice]["area_kmq"])
        righe[codice] = [
            per_sezione[codice].get("C", 0.0) / totale * 100,
            per_sezione[codice].get("I", 0.0) / totale * 100,
            anni_addetti[ultimo_asia] / anni_unita[ultimo_asia],
            anni_addetti[ultimo_asia] / anni_pop[max(anni_pop)] * 100,
            anni_reddito[max(anni_reddito)],
            math.log10(anni_pop[max(anni_pop)] / area),
        ]
    return sorted(righe), righe


def standardizza(codici: list[str], righe: dict[str, list[float]]) -> dict[str, list[float]]:
    quante = len(VARIABILI)
    medie = [media([righe[c][i] for c in codici]) for i in range(quante)]
    scarti = [
        math.sqrt(media([(righe[c][i] - medie[i]) ** 2 for c in codici])) or 1.0
        for i in range(quante)
    ]
    return {c: [(righe[c][i] - medie[i]) / scarti[i] for i in range(quante)] for c in codici}


def distanza(a: list[float], b: list[float]) -> float:
    return sum((x - y) ** 2 for x, y in zip(a, b))


def kmeans(punti: dict[str, list[float]], gruppi: int, iterazioni: int = 100) -> dict[str, int]:
    """k-means++ con seme fisso. Trenta righe, nessuna dipendenza."""
    rng = random.Random(SEME)
    codici = sorted(punti)
    centri = [punti[rng.choice(codici)]]
    while len(centri) < gruppi:
        # k-means++: il prossimo centro è estratto con probabilità proporzionale
        # alla distanza dal più vicino già scelto. Senza, due centri finiscono
        # nello stesso grumo e un gruppo resta vuoto.
        pesi = [min(distanza(punti[c], centro) for centro in centri) for c in codici]
        totale = sum(pesi)
        if totale == 0:
            centri.append(punti[rng.choice(codici)])
            continue
        soglia = rng.random() * totale
        corrente = 0.0
        for codice, peso in zip(codici, pesi):
            corrente += peso
            if corrente >= soglia:
                centri.append(punti[codice])
                break

    assegnazione: dict[str, int] = {}
    for _ in range(iterazioni):
        nuova = {
            c: min(range(gruppi), key=lambda g: distanza(punti[c], centri[g])) for c in codici
        }
        if nuova == assegnazione:
            break
        assegnazione = nuova
        for g in range(gruppi):
            dentro = [punti[c] for c in codici if assegnazione[c] == g]
            if dentro:
                centri[g] = [media([p[i] for p in dentro]) for i in range(len(VARIABILI))]
    return assegnazione


QUALIFICATORI = {
    2: ("con imprese grandi", "con imprese piccole"),
    3: ("dove si lavora", "dove si abita"),
    4: ("benestante", "con redditi bassi"),
    5: ("denso", "rado"),
}


def base_settoriale(centro: list[float]) -> str:
    manifattura, alloggio = centro[0], centro[1]
    if alloggio >= 25:
        return "turistico"
    if manifattura >= 45:
        return "manifatturiero"
    if manifattura >= 28:
        return "misto industriale"
    return "residenziale e terziario"


def descrivi(centri: list[list[float]], centri_z: list[list[float]]) -> list[str]:
    """Etichette leggibili: il settore prevalente più il tratto più distintivo.

    Il tratto si sceglie guardando quale variabile standardizzata è più lontana
    dalla media provinciale. Se due gruppi arrivano allo stesso nome si passa al
    tratto successivo, finché non si distinguono: un'etichetta ripetuta non
    descrive niente, e con k-means capita che due gruppi differiscano su una
    variabile sola.
    """
    fuori: list[str] = []
    for gruppo, centro in enumerate(centri):
        base = base_settoriale(centro)
        candidati = sorted(QUALIFICATORI, key=lambda i: -abs(centri_z[gruppo][i]))
        for indice in candidati:
            alto, basso = QUALIFICATORI[indice]
            proposta = f"{base}, {alto if centri_z[gruppo][indice] >= 0 else basso}"
            if proposta not in fuori:
                break
        fuori.append(proposta)
    return fuori


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tipologia_comuni")
    parser.add_argument("--gruppi", type=int, default=5, help="quanti gruppi (default 5)")
    parser.add_argument("--save", action="store_true", help="scrive il CSV in analysis/output/")
    parser.add_argument("--esempi", type=int, default=6, help="quanti comuni citare per gruppo")
    args = parser.parse_args(argv)

    codici, righe = costruisci_tabella()
    punti = standardizza(codici, righe)
    assegnazione = kmeans(punti, args.gruppi)
    comuni = anagrafica()

    print(f"{len(codici)} comuni, {args.gruppi} gruppi, seme {SEME}")
    print("I profili sono descrizioni dei gruppi trovati, non categorie esistenti:")
    print("con un k diverso i gruppi cambiano, e nessuno di essi è «vero».\n")

    intestazione = (f"  {'gruppo':37} {'n':>4} {'manif.':>8} {'allogg.':>8} "
                    f"{'add./UL':>8} {'add./100':>9} {'reddito':>9} {'ab./km²':>9}")
    print(intestazione)
    print("  " + "-" * (len(intestazione) - 2))

    lontananza: dict[str, float] = {}
    ordine = sorted(
        range(args.gruppi),
        key=lambda g: -media([righe[c][0] for c in codici if assegnazione[c] == g] or [0]),
    )
    membri = {g: [c for c in codici if assegnazione[c] == g] for g in ordine}
    centri = {
        g: [media([righe[c][i] for c in membri[g]]) for i in range(len(VARIABILI))] for g in ordine
    }
    centri_z = {
        g: [media([punti[c][i] for c in membri[g]]) for i in range(len(VARIABILI))] for g in ordine
    }
    nomi = descrivi([centri[g] for g in ordine], [centri_z[g] for g in ordine])
    etichette: dict[int, str] = {g: nomi[i] for i, g in enumerate(ordine)}

    for posizione, gruppo in enumerate(ordine, start=1):
        dentro = membri[gruppo]
        centro = centri[gruppo]
        centro_z = centri_z[gruppo]
        print(f"  {posizione}. {etichette[gruppo]:34} {len(dentro):>4} {centro[0]:>8.1f} "
              f"{centro[1]:>8.1f} {centro[2]:>8.1f} {centro[3]:>9.1f} "
              f"{centro[4]:>9,.0f} {10 ** centro[5]:>9,.0f}")
        # Gli esempi sono i comuni **più vicini al centro**, cioè i più tipici:
        # ordinarli per una variabile qualunque mette in vetrina gli outlier.
        for codice in dentro:
            lontananza[codice] = math.sqrt(distanza(punti[codice], centro_z))
        esempi = sorted(dentro, key=lambda c: lontananza[c])[: args.esempi]
        print(f"     {', '.join(comuni[c]['comune'] for c in esempi)}")

    gruppo_capoluogo = etichette[assegnazione[CAPOLUOGO]]
    print(f"\nIl capoluogo sta nel gruppo «{gruppo_capoluogo}», "
          f"a {lontananza[CAPOLUOGO]:.1f} scarti dal centro.")

    print("\nI comuni che nessun gruppo descrive bene (i più lontani dal proprio centro)")
    for codice in sorted(codici, key=lambda c: -lontananza[c])[:6]:
        print(f"  {comuni[codice]['comune'][:26]:26} {lontananza[codice]:>5.1f}   "
              f"gruppo «{etichette[assegnazione[codice]]}»")

    if args.save:
        fuori = [
            {
                "codice_istat": codice,
                "comune": comuni[codice]["comune"],
                "gruppo": str(ordine.index(assegnazione[codice]) + 1),
                "profilo": etichette[assegnazione[codice]],
                **{nome: f"{righe[codice][i]:.3f}" for i, nome in enumerate(VARIABILI)},
            }
            for codice in codici
        ]
        destinazione = scrivi_csv("tipologia_comuni.csv", COLONNE, fuori)
        print(f"scritto {destinazione.relative_to(RADICE)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
