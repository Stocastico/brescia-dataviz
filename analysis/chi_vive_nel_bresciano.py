"""Chi vive nel bresciano: stranieri, seconde generazioni, italiani acquisiti.

    python analysis/chi_vive_nel_bresciano.py           # tutto a schermo
    python analysis/chi_vive_nel_bresciano.py --save    # + tre CSV in analysis/output/
    python analysis/chi_vive_nel_bresciano.py --tutti   # tutti i 205 comuni

È l'asse 2 del brief, l'ultimo che non aveva né analisi né storia. Legge le due
marginali **versionate** (`background_migratorio_comuni.csv` e
`background_migratorio_istruzione.csv`) e non la congiunta da 422 MB: così ogni
cifra che finisce nel sito poggia su una tabella che sta nel repository, che è
la regola del progetto. La congiunta serve per gli incroci fini, e chi la vuole
la rigenera (`dati/SCARICHI-LOCALI.md`).

Quattro conti, in ordine di quanto cambiano la storia che il sito racconta oggi.

**1. La prima storia dice «la provincia cresce solo per la componente
estera», e lo dice sui flussi.** Il censimento dice la stessa cosa sullo
**stock**, e più duramente: fra il 2021 e il 2023 gli italiani *dalla nascita*
**calano** e gli italiani *per acquisizione* crescono di più di quanto la
popolazione totale cresca. Non sono due misure in disaccordo: sono la fotografia
e il film dello stesso fenomeno.

**2. «Gli stranieri sono fermi a 153 mila» è un numero giusto e una frase
falsa.** Lo stock straniero è quasi immobile fra il 2021 e il 2023, ma nello
stesso biennio decine di migliaia di persone lo hanno **lasciato** prendendo la
cittadinanza. Un serbatoio a livello costante con due rubinetti aperti non è un
serbatoio fermo: è la stessa lezione del working paper, su un dato nuovo.

**3. Le seconde generazioni sono la cifra più netta del dataset**, e sono
minorenni quasi per intero. Il conteggio delle persone nate in provincia che non
hanno la cittadinanza italiana non è una stima né una proiezione: è una riga di
censimento.

**4. Sul titolo di studio un numero solo non descrive niente.** Il divario
aggregato fra italiani dalla nascita e stranieri è di pochi punti; dentro le
classi d'età è di **tredici punti fra i 25 e i 49 anni** e ha il **segno
opposto** sopra i 65. La standardizzazione per età non salva la sintesi — la
sposta di mezzo punto — perché il problema non è la composizione: è che i
divari specifici hanno segno diverso, e quindi *nessuna* media li rappresenta.
Il rimedio è pubblicare le classi, non una standardizzata.

Confidenza: `osservato` per i conteggi (sono censimento), `derivato` per quote,
variazioni e tassi standardizzati.
"""

from __future__ import annotations

import argparse
import statistics
import sys

from _tabelle import leggi, nome, numero, scrivi_csv  # noqa: E402

PRIMO = "2021"
ULTIMO = "2023"
CAPOLUOGO = "017029"

# Le classi d'età su cui la fonte pubblica il titolo di studio. `9 anni e più`
# è il loro totale, non una quinta classe: tenerlo nella lista lo conterebbe
# due volte.
CLASSI = ["9-24 anni", "25-49 anni", "50-64 anni", "65 anni e più"]
TOTALE_CLASSI = "9 anni e più"
LAUREA = "titolo universitario o accademico"
NESSUN_TITOLO = "nessun titolo di studio"
GRUPPI = ["italiani dalla nascita", "italiani acquisiti", "stranieri"]


def stock() -> dict[tuple[str, str, str], float]:
    """`(codice, anno, indicatore) -> valore` dalla marginale comunale."""
    fuori: dict[tuple[str, str, str], float] = {}
    for riga in leggi("background_migratorio_comuni.csv"):
        valore = numero(riga["valore"])
        if valore is not None:
            fuori[(riga["codice_istat"], riga["anno"], riga["indicatore"])] = valore
    return fuori


def istruzione() -> dict[tuple[str, str, str, str], float]:
    """`(anno, gruppo, classe, titolo) -> valore`, già provinciale."""
    fuori: dict[tuple[str, str, str, str], float] = {}
    for riga in leggi("background_migratorio_istruzione.csv"):
        valore = numero(riga["valore"])
        if valore is not None:
            fuori[(riga["anno"], riga["gruppo"], riga["classe_eta"], riga["titolo"])] = valore
    return fuori


def provinciale(dati, anno: str, indicatore: str) -> float:
    return sum(v for (_, a, i), v in dati.items() if a == anno and i == indicatore)


def comuni_con(dati) -> list[str]:
    return sorted({c for (c, _, _) in dati})


# --- 1. lo stock, e da dove viene la crescita ----------------------------


def scomposizione(dati) -> list[dict[str, str]]:
    """La variazione dello stock fra i tre gruppi, in provincia."""
    voci = ["popolazione_residente", "italiani_dalla_nascita", "italiani_acquisiti", "stranieri"]
    righe = []
    for voce in voci:
        primo = provinciale(dati, PRIMO, voce)
        ultimo = provinciale(dati, ULTIMO, voce)
        righe.append({
            "voce": voce,
            "primo": f"{primo:.0f}",
            "ultimo": f"{ultimo:.0f}",
            "variazione": f"{ultimo - primo:+.0f}",
            "quota_finale": f"{ultimo / provinciale(dati, ULTIMO, 'popolazione_residente') * 100:.1f}",
            "stato": "osservato",
        })
    return righe


def mostra_scomposizione(righe) -> None:
    print(f"\n=== 1. Lo stock, {PRIMO}-{ULTIMO}: chi cresce e chi cala ===\n")
    print(f"{'voce':34} {PRIMO:>12} {ULTIMO:>12} {'variazione':>12} {'quota':>7}")
    for r in righe:
        print(f"{r['voce']:34} {int(r['primo']):>12,} {int(r['ultimo']):>12,} "
              f"{int(r['variazione']):>+12,} {r['quota_finale']:>6}%")

    per_voce = {r["voce"]: int(r["variazione"]) for r in righe}
    print(f"\n  La popolazione cresce di {per_voce['popolazione_residente']:+,}, ma gli")
    print(f"  italiani dalla nascita fanno {per_voce['italiani_dalla_nascita']:+,} e gli acquisiti")
    print(f"  {per_voce['italiani_acquisiti']:+,}: la crescita degli acquisiti vale")
    quanto = per_voce["italiani_acquisiti"] / per_voce["popolazione_residente"]
    print(f"  {quanto:.1f} volte la crescita totale della provincia.")


# --- 2. il serbatoio che sembra fermo ------------------------------------


def serbatoio(dati) -> None:
    print("\n=== 2. «Gli stranieri sono fermi»: numero giusto, frase falsa ===\n")
    primo = provinciale(dati, PRIMO, "stranieri")
    ultimo = provinciale(dati, ULTIMO, "stranieri")
    usciti = provinciale(dati, ULTIMO, "italiani_acquisiti") - provinciale(
        dati, PRIMO, "italiani_acquisiti"
    )
    print(f"  stranieri {PRIMO}: {primo:>12,.0f}")
    print(f"  stranieri {ULTIMO}: {ultimo:>12,.0f}   ({ultimo - primo:+,.0f})")
    print(f"  nuovi italiani per acquisizione nel biennio: {usciti:+,.0f}")
    print(f"\n  Lo stock si muove di {ultimo - primo:+,.0f} mentre {usciti:,.0f} persone ne")
    print("  escono per cittadinanza: l'ingresso implicito è di almeno")
    print(f"  {usciti + (ultimo - primo):,.0f} persone in due anni.")
    print("\n  ⚠️ «Almeno», e non «esattamente»: nascite, morte e migrazione in")
    print("  uscita muovono lo stesso stock, e questa tabella non le separa.")
    print("  Per la scomposizione dei flussi c'è decomposizione_popolazione.py.")


# --- 3. le seconde generazioni ------------------------------------------


def seconde_generazioni(dati) -> None:
    print("\n=== 3. Nati qui, e la cittadinanza ===\n")
    stranieri = provinciale(dati, ULTIMO, "stranieri_nati_in_italia")
    minori_str = provinciale(dati, ULTIMO, "stranieri_nati_in_italia_minorenni")
    acquisiti = provinciale(dati, ULTIMO, "italiani_acquisiti_nati_in_italia")
    minori_acq = provinciale(dati, ULTIMO, "italiani_acquisiti_nati_in_italia_minorenni")
    print(f"  nati in Italia, cittadinanza straniera: {stranieri:>9,.0f}"
          f"  di cui minorenni {minori_str:>8,.0f}  ({minori_str / stranieri * 100:.1f}%)")
    print(f"  nati in Italia, cittadinanza acquisita: {acquisiti:>9,.0f}"
          f"  di cui minorenni {minori_acq:>8,.0f}  ({minori_acq / acquisiti * 100:.1f}%)")
    print(f"\n  In tutto {stranieri + acquisiti:,.0f} persone nate in Italia da genitori")
    print(f"  stranieri: {stranieri / (stranieri + acquisiti) * 100:.0f}% non ha la cittadinanza,")
    print(f"  e di questi il {minori_str / stranieri * 100:.1f}% è minorenne.")


# --- 4. il titolo di studio, e perché una media non basta ---------------


def divari(istr) -> list[dict[str, str]]:
    righe = []
    for classe in CLASSI + [TOTALE_CLASSI]:
        for gruppo in GRUPPI:
            totale = istr.get((ULTIMO, gruppo, classe, "totale"))
            if not totale:
                continue
            righe.append({
                "classe_eta": classe,
                "gruppo": gruppo,
                "popolazione": f"{totale:.0f}",
                "quota_laurea": f"{istr.get((ULTIMO, gruppo, classe, LAUREA), 0) / totale * 100:.1f}",
                "quota_nessun_titolo":
                    f"{istr.get((ULTIMO, gruppo, classe, NESSUN_TITOLO), 0) / totale * 100:.1f}",
                "stato": "derivato",
            })
    return righe


def standardizzato(istr, gruppo: str, titolo: str = LAUREA) -> float:
    """Tasso diretto standardizzato sull'età della popolazione provinciale 9+.

    La popolazione standard è la somma dei tre gruppi, cioè la provincia stessa:
    così il tasso standardizzato di un gruppo è confrontabile col grezzo
    provinciale e non con una popolazione inventata.
    """
    standard = {
        classe: sum(istr.get((ULTIMO, g, classe, "totale"), 0) for g in GRUPPI)
        for classe in CLASSI
    }
    peso = sum(standard.values())
    somma = 0.0
    for classe in CLASSI:
        totale = istr.get((ULTIMO, gruppo, classe, "totale"))
        if not totale:
            continue
        somma += standard[classe] * istr.get((ULTIMO, gruppo, classe, titolo), 0) / totale
    return somma / peso * 100


def mostra_divari(istr, righe) -> None:
    print(f"\n=== 4. Il titolo di studio, {ULTIMO} ===\n")
    print(f"{'classe':16} {'gruppo':24} {'popolazione':>12} {'laurea':>8} {'nessun tit.':>12}")
    for r in righe:
        print(f"{r['classe_eta']:16} {r['gruppo']:24} {int(r['popolazione']):>12,} "
              f"{r['quota_laurea']:>7}% {r['quota_nessun_titolo']:>11}%")

    print(f"\n  {'gruppo':24} {'grezzo':>8} {'standardizzato':>16}")
    for gruppo in GRUPPI:
        totale = istr.get((ULTIMO, gruppo, TOTALE_CLASSI, "totale"))
        grezzo = istr.get((ULTIMO, gruppo, TOTALE_CLASSI, LAUREA), 0) / totale * 100
        print(f"  {gruppo:24} {grezzo:>7.1f}% {standardizzato(istr, gruppo):>15.1f}%")

    def quota(gruppo, classe):
        totale = istr[(ULTIMO, gruppo, classe, "totale")]
        return istr.get((ULTIMO, gruppo, classe, LAUREA), 0) / totale * 100

    giovani = quota("italiani dalla nascita", "25-49 anni") - quota("stranieri", "25-49 anni")
    anziani = quota("italiani dalla nascita", "65 anni e più") - quota("stranieri", "65 anni e più")
    print("\n  Divario italiani dalla nascita - stranieri:")
    print(f"    25-49 anni:    {giovani:+.1f} punti")
    print(f"    65 anni e più: {anziani:+.1f} punti")
    print("\n  I due hanno segno opposto, quindi nessuna media li rappresenta: la")
    print("  standardizzazione sposta l'aggregato di mezzo punto e non racconta")
    print("  né l'uno né l'altro. Vanno pubblicate le classi.")


# --- la mappa: il background per comune ---------------------------------


def per_comune(dati) -> list[dict[str, str]]:
    righe = []
    for codice in comuni_con(dati):
        totale = dati.get((codice, ULTIMO, "popolazione_residente"))
        if not totale:
            continue
        stranieri = dati.get((codice, ULTIMO, "stranieri"), 0)
        acquisiti = dati.get((codice, ULTIMO, "italiani_acquisiti"), 0)
        nati_estero = sum(
            dati.get((codice, ULTIMO, i), 0)
            for i in ("stranieri_nati_all_estero", "italiani_acquisiti_nati_all_estero",
                      "italiani_dalla_nascita_nati_all_estero")
        )
        righe.append({
            "codice_istat": codice,
            "comune": nome(codice),
            "popolazione": f"{totale:.0f}",
            "quota_stranieri": f"{stranieri / totale * 100:.2f}",
            "quota_background": f"{(stranieri + acquisiti) / totale * 100:.2f}",
            "quota_nati_estero": f"{nati_estero / totale * 100:.2f}",
            "stato": "derivato",
        })
    righe.sort(key=lambda r: -float(r["quota_background"]))
    return righe


def mostra_comuni(righe, tutti: bool) -> None:
    quote = [float(r["quota_background"]) for r in righe]
    provincia_tot = sum(int(r["popolazione"]) for r in righe)
    pesata = sum(int(r["popolazione"]) * float(r["quota_background"]) for r in righe) / provincia_tot
    print(f"\n=== Il background migratorio per comune, {ULTIMO} ===\n")
    print(f"  provincia {pesata:.1f}%   mediana comunale {statistics.median(quote):.1f}%"
          f"   da {min(quote):.1f}% a {max(quote):.1f}%")
    print(f"\n{'comune':28} {'popolazione':>12} {'stranieri':>10} {'background':>11}")
    mostrati = righe if tutti else righe[:12] + righe[-8:]
    precedente = None
    for r in mostrati:
        if precedente is not None and r is righe[-8]:
            print("  ...")
        print(f"{r['comune']:28} {int(r['popolazione']):>12,} "
              f"{r['quota_stranieri']:>9}% {r['quota_background']:>10}%")
        precedente = r
    capoluogo = next((r for r in righe if r["codice_istat"] == CAPOLUOGO), None)
    if capoluogo:
        print(f"\n  capoluogo: {capoluogo['quota_background']}% di background migratorio "
              f"({capoluogo['quota_stranieri']}% stranieri)")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="chi_vive_nel_bresciano")
    parser.add_argument("--save", action="store_true", help="scrive i CSV in analysis/output/")
    parser.add_argument("--tutti", action="store_true", help="mostra tutti i 205 comuni")
    args = parser.parse_args(argv)

    dati = stock()
    istr = istruzione()
    if not dati or not istr:
        print(
            "mancano le marginali del background migratorio: si producono con\n"
            "  python -m brescia_pipeline.build migrazioni\n"
            "(venti minuti, vedi dati/SCARICHI-LOCALI.md)",
            file=sys.stderr,
        )
        return 1

    righe_stock = scomposizione(dati)
    mostra_scomposizione(righe_stock)
    serbatoio(dati)
    seconde_generazioni(dati)
    righe_divari = divari(istr)
    mostra_divari(istr, righe_divari)
    righe_comuni = per_comune(dati)
    mostra_comuni(righe_comuni, args.tutti)

    if args.save:
        scrivi_csv("background_scomposizione.csv",
                   ["voce", "primo", "ultimo", "variazione", "quota_finale", "stato"],
                   righe_stock)
        scrivi_csv("background_istruzione.csv",
                   ["classe_eta", "gruppo", "popolazione", "quota_laurea",
                    "quota_nessun_titolo", "stato"],
                   righe_divari)
        scrivi_csv("background_comuni.csv",
                   ["codice_istat", "comune", "popolazione", "quota_stranieri",
                    "quota_background", "quota_nati_estero", "stato"],
                   righe_comuni)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
