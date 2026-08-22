"""Perché 93 comuni perdono abitanti: nascite, morti, partenze, arrivi.

    python analysis/decomposizione_popolazione.py           # tutto a schermo
    python analysis/decomposizione_popolazione.py --save    # + due CSV in analysis/output/
    python analysis/decomposizione_popolazione.py --tutti   # tutti i 205 comuni

È il seguito che la prima storia del sito dichiarava di non poter scrivere.
`variazione_popolazione.py` misura **quanto** cambia la popolazione di ogni
comune; qui si misura **da dove viene** quel cambiamento, scomponendolo nelle
tre componenti che lo producono più le due voci che componenti non sono:

    variazione = saldo naturale + migrazione interna + migrazione estera
                 + variazioni territoriali + aggiustamento statistico

La scomposizione **chiude allo zero**, comune per comune e anno per anno: non è
un modello, è la contabilità della fonte (`pipeline/datasets/bilancio.py`), e la
pipeline fallisce se non torna. La popolazione da cui parte e a cui arriva è la
stessa di `popolazione_comuni.csv` — la riga «Popolazione censita al 31
dicembre» del bilancio *è* la popolazione del censimento permanente — quindi non
si stanno mescolando due popolazioni diverse.

Due avvertenze che vanno ripetute accanto a ogni grafico che usi questi numeri:

- **l'aggiustamento statistico non è un fenomeno.** È la rettifica che
  riconcilia l'anagrafe con il censimento, e in provincia vale −4.558 persone in
  sei anni: abbastanza da cambiare il segno di un comune piccolo. Qui resta una
  colonna a sé, e nessuna frase del progetto deve attribuirla alla demografia;
- **la migrazione interna non dice dove**. Il bilancio conta chi entra e chi
  esce da ogni comune, non la coppia origine-destinazione: «chi lascia la Valle
  Camonica va a Brescia» è un'affermazione che questi dati **non** sostengono.

Confidenza: `osservato` per le componenti (sono conteggi della fonte),
`derivato` per i rapporti per mille.
"""

from __future__ import annotations

import argparse
import sys

import _tabelle as t

# Il periodo: gli stessi estremi della prima storia del sito. Il bilancio
# comincia con il 2019 perché è l'anno in cui la serie mensile si riconcilia con
# il censimento permanente, e i flussi del 2019 sono quelli che portano dalla
# popolazione di fine 2018 a quella di fine 2019.
PRIMO_STOCK = "2018"
ULTIMO_STOCK = "2024"

ETICHETTE = {
    "saldo_naturale": "saldo naturale",
    "saldo_migratorio_interno": "migrazione interna",
    "saldo_migratorio_estero": "migrazione estera",
    "variazioni_territoriali": "variazioni territoriali",
    "aggiustamento_statistico": "aggiustamento statistico",
}
DEMOGRAFICHE = ["saldo_naturale", "saldo_migratorio_interno", "saldo_migratorio_estero"]

COLONNE = [
    "codice_istat", "comune", "capoluogo",
    "popolazione_2018", "popolazione_2024", "variazione",
    *t.COMPONENTI, *t.NON_DEMOGRAFICHE,
    "componente_dominante", "componente_piu_negativa",
]
COLONNE_PROVINCE = [
    "codice_provincia", "provincia", "regione", "popolazione_2018", "variazione_per_mille",
    *[f"{c}_per_mille" for c in t.COMPONENTI], "aggiustamento_per_mille", "rango_variazione",
]


def mila(valore: float, segno: bool = False) -> str:
    """Numero con il punto come separatore delle migliaia.

    Serve un helper e non un `.replace(",", ".")` sulla stringa formattata: il
    replace prende anche le virgole della prosa attorno al numero, e la frase
    esce con i punti in mezzo alle parole. È successo.
    """
    return f"{valore:{'+' if segno else ''},.0f}".replace(",", ".")


def dominante(scomposizione: dict[str, float]) -> str:
    """La componente demografica che pesa di più, in valore assoluto.

    Solo fra le tre demografiche: dire che il calo di un comune è «dovuto
    all'aggiustamento statistico» è vero come contabilità e falso come
    spiegazione.
    """
    return max(DEMOGRAFICHE, key=lambda nome: abs(scomposizione[nome]))


def piu_negativa(scomposizione: dict[str, float]) -> str:
    """La componente che tira più giù. **Non** è la stessa cosa di `dominante`.

    Sono due domande diverse e confonderle è facile: in un comune che perde
    abitanti con il saldo naturale a −20 ‰ e la migrazione estera a +59 ‰ la
    componente più grande è quella estera, ma il comune non sta perdendo
    abitanti *per* l'immigrazione. Alla domanda «perché questo comune si
    svuota» risponde la componente più negativa; a «cosa muove di più questo
    comune» risponde quella più grande in valore assoluto.
    """
    return min(DEMOGRAFICHE, key=lambda nome: scomposizione[nome])


# --- i comuni ------------------------------------------------------------


def comuni() -> list[dict[str, object]]:
    anagrafica = t.anagrafica()
    popolazione = t.serie_popolazione()
    bilanci = t.bilancio()

    righe: list[dict[str, object]] = []
    for codice, per_anno in bilanci.items():
        scomposizione = t.scomponi(per_anno)
        iniziale = popolazione[codice][PRIMO_STOCK]
        finale = popolazione[codice][ULTIMO_STOCK]
        # Il controllo che rende leggibile tutto il resto: se la somma delle
        # componenti non è la variazione degli stock, la scomposizione non
        # scompone niente. La pipeline lo verifica già; qui si rifà su un'altra
        # tabella, che è il punto di un controllo.
        if abs(scomposizione["totale"] - (finale - iniziale)) > 0.5:
            raise SystemExit(
                f"{codice}: le componenti sommano {scomposizione['totale']:.0f}, "
                f"gli stock dicono {finale - iniziale:.0f}"
            )
        righe.append(
            {
                "codice_istat": codice,
                "comune": anagrafica[codice]["comune"],
                "capoluogo": anagrafica[codice]["capoluogo"],
                "popolazione_2018": iniziale,
                "popolazione_2024": finale,
                "variazione": finale - iniziale,
                **scomposizione,
                "componente_dominante": dominante(scomposizione),
                "componente_piu_negativa": piu_negativa(scomposizione),
            }
        )
    righe.sort(key=lambda r: r["variazione"] / r["popolazione_2018"])
    return righe


def stampa_provincia(righe: list[dict[str, object]]) -> None:
    totali = {nome: sum(r[nome] for r in righe) for nome in ETICHETTE}
    iniziale = sum(r["popolazione_2018"] for r in righe)
    variazione = sum(r["variazione"] for r in righe)

    print(f"La provincia fra il {PRIMO_STOCK} e il {ULTIMO_STOCK}: "
          f"{mila(variazione, segno=True)} abitanti su {mila(iniziale)}")
    print()
    for nome, etichetta in ETICHETTE.items():
        print(f"  {etichetta:26} {mila(totali[nome], segno=True):>9}   "
              f"{totali[nome] / iniziale * 1000:+7.1f} ‰")
    print(f"  {'-' * 26} {'-' * 9}")
    print(f"  {'variazione':26} {mila(variazione, segno=True):>9}")
    print()
    senza_estero = variazione - totali["saldo_migratorio_estero"]
    print(f"Senza la migrazione estera la provincia perderebbe {mila(-senza_estero)} abitanti.")


def stampa_comuni_in_calo(righe: list[dict[str, object]]) -> None:
    in_calo = [r for r in righe if r["variazione"] < 0]
    print(f"\n{len(in_calo)} comuni su {len(righe)} perdono abitanti. Perché:\n")

    # La componente **più negativa**, non la più grande: vedi `piu_negativa`.
    conteggio = {nome: sum(1 for r in in_calo if r["componente_piu_negativa"] == nome)
                 for nome in DEMOGRAFICHE}
    for nome in DEMOGRAFICHE:
        print(f"  {ETICHETTE[nome]:26} è la componente che tira più giù "
              f"in {conteggio[nome]:3} comuni")

    print(f"\n  Sommando i {len(in_calo)} comuni in calo:")
    for nome in ETICHETTE:
        print(f"    {ETICHETTE[nome]:24} {mila(sum(r[nome] for r in in_calo), segno=True):>8}")
    interna = sum(r["saldo_migratorio_interno"] for r in in_calo)
    naturale = sum(r["saldo_naturale"] for r in in_calo)
    print(f"\n  La migrazione interna, sommata, vale {mila(interna, segno=True)} contro "
          f"{mila(naturale, segno=True)}")
    print("  del saldo naturale: questi comuni non si svuotano perché la gente se ne")
    print("  va, si svuotano perché ci muore più gente di quanta ne nasca.")

    negativi = {nome: sum(1 for r in righe if r[nome] < 0) for nome in DEMOGRAFICHE}
    print()
    for nome in DEMOGRAFICHE:
        print(f"  {ETICHETTE[nome]:26} è negativo in {negativi[nome]:3} comuni su {len(righe)}")


def stampa_code(righe: list[dict[str, object]], quante: int | None) -> None:
    testa = f"\n{'comune':24}{'pop 18':>8}{'%/anno':>8}" + "".join(
        f"{ETICHETTE[n].split()[-1][:9]:>10}" for n in DEMOGRAFICHE) + f"{'agg.':>8}"
    print(testa)
    print("  (componenti per mille abitanti del 2018, sull'intero periodo)")
    print("-" * len(testa))

    def blocco(sotto: list[dict[str, object]]) -> None:
        for r in sotto:
            base = r["popolazione_2018"]
            anni = int(ULTIMO_STOCK) - int(PRIMO_STOCK)
            tasso = ((r["popolazione_2024"] / base) ** (1 / anni) - 1) * 100
            print(f"{r['comune'][:24]:24}{mila(base):>8}{tasso:>8.2f}"
                  + "".join(f"{r[n] / base * 1000:>10.1f}" for n in DEMOGRAFICHE)
                  + f"{r['aggiustamento_statistico'] / base * 1000:>8.1f}")

    if quante is None:
        blocco(righe)
    else:
        blocco(righe[:quante])
        print(f"{'…':^24}")
        blocco(righe[-quante:])


# --- le province ---------------------------------------------------------


def province() -> list[dict[str, object]]:
    """Le stesse componenti su tutte e 107 le province: il termine di paragone.

    Sullo spopolamento montano il confronto mancava, mentre imprese e redditi
    ce l'hanno già (MET-14 è nata proprio da lì). La base è la popolazione a
    inizio 2019, cioè lo stock di fine 2018.
    """
    anagrafiche = {
        r["codice_provincia"]: (r["provincia"], r["regione"])
        for r in t.leggi("bilancio_province.csv")
    }
    bilanci = t.bilancio("bilancio_province.csv", "codice_provincia")

    righe: list[dict[str, object]] = []
    for codice, per_anno in bilanci.items():
        base = per_anno[min(per_anno)]["popolazione_inizio"]
        scomposizione = t.scomponi(per_anno)
        nome, regione = anagrafiche[codice]
        righe.append(
            {
                "codice_provincia": codice,
                "provincia": nome,
                "regione": regione,
                "popolazione_2018": base,
                "variazione_per_mille": scomposizione["totale"] / base * 1000,
                **{f"{c}_per_mille": scomposizione[c] / base * 1000 for c in t.COMPONENTI},
                "aggiustamento_per_mille": scomposizione["aggiustamento_statistico"] / base * 1000,
            }
        )
    righe.sort(key=lambda r: -r["variazione_per_mille"])
    for posizione, riga in enumerate(righe, start=1):
        riga["rango_variazione"] = posizione
    return righe


def mediana(valori: list[float]) -> float:
    ordinati = sorted(valori)
    meta = len(ordinati) // 2
    if len(ordinati) % 2:
        return ordinati[meta]
    return (ordinati[meta - 1] + ordinati[meta]) / 2


def stampa_province(righe: list[dict[str, object]]) -> None:
    brescia = next(r for r in righe if r["codice_provincia"] == "017")
    print(f"\n\nBrescia fra le {len(righe)} province, {PRIMO_STOCK}–{ULTIMO_STOCK}")
    print("  (per mille abitanti; il rango 1 è la provincia che cresce di più)\n")
    print(f"{'':28}{'Brescia':>10}{'rango':>8}{'mediana':>10}")

    voci = [("variazione_per_mille", "variazione")] + [
        (f"{c}_per_mille", ETICHETTE[c]) for c in t.COMPONENTI
    ]
    for chiave, etichetta in voci:
        ordinate = sorted(righe, key=lambda r: -r[chiave])
        rango = next(i for i, r in enumerate(ordinate, 1) if r["codice_provincia"] == "017")
        print(f"{etichetta:28}{brescia[chiave]:>+10.1f}{rango:>8}"
              f"{mediana([r[chiave] for r in righe]):>+10.1f}")

    positive = sum(1 for r in righe if r["saldo_naturale_per_mille"] > 0)
    crescono = sum(1 for r in righe if r["variazione_per_mille"] > 0)
    print(f"\n  {crescono} province su {len(righe)} crescono; in {positive} il saldo naturale")
    print("  è positivo. Il calo demografico non è montano né bresciano: è italiano,")
    print("  e quello che distingue Brescia è quanta gente arriva.")


# --- uscita --------------------------------------------------------------


def salva(righe: list[dict[str, object]], righe_province: list[dict[str, object]]) -> None:
    for nome_file, colonne, dati in (
        ("decomposizione_popolazione.csv", COLONNE, righe),
        ("decomposizione_province.csv", COLONNE_PROVINCE, righe_province),
    ):
        formattate = [
            {c: (f"{r[c]:.2f}" if isinstance(r[c], float) else r[c]) for c in colonne}
            for r in dati
        ]
        print(f"scritto {t.scrivi_csv(nome_file, colonne, formattate).relative_to(t.RADICE)}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="decomposizione_popolazione")
    parser.add_argument("--save", action="store_true", help="scrive i CSV in analysis/output/")
    parser.add_argument("--tutti", action="store_true", help="stampa tutti i comuni")
    parser.add_argument("--code", type=int, default=10, help="quanti comuni per coda (default 10)")
    args = parser.parse_args(argv)

    righe = comuni()
    righe_province = province()

    stampa_provincia(righe)
    stampa_comuni_in_calo(righe)
    stampa_code(righe, None if args.tutti else args.code)
    stampa_province(righe_province)

    if args.save:
        print()
        salva(righe, righe_province)
    return 0


if __name__ == "__main__":
    sys.exit(main())
