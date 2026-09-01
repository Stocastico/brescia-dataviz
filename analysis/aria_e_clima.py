"""L'aria e il clima: due serie lunghe, e una domanda diversa per ciascuna.

    python analysis/aria_e_clima.py
    python analysis/aria_e_clima.py --save

L'asse 4 del brief è l'unico dei quattro portanti che non aveva una lettura, e
non perché mancassero i dati: ci sono da sempre, e sono le serie più lunghe del
progetto — l'aria dal 2000, la temperatura dal 1993. Mancava il modo di leggerle
senza raccontare una cosa falsa, e il modo costa due decisioni che questo script
prende esplicitamente.

**La prima: il panel bilanciato.** Le centraline aprono e chiudono. Fra il 2000
e il 2025 il PM10 passa da due stazioni a sette, e non sono le stesse: fare la
media di quelle che ci sono ogni anno significa misurare *anche* il cambio della
rete, e chiamarlo qualità dell'aria. È lo stesso errore di MET-12 in un'altra
forma — un artefatto del disegno scambiato per un risultato — e si evita
tenendo solo le stazioni osservate in **tutti** gli anni della finestra. Il
prezzo è che ne restano poche: tre per il PM10, quattro per il biossido di
azoto. Il conto ingenuo è stampato accanto, perché la differenza fra i due è
essa stessa un risultato.

**La seconda: le anomalie, non le medie.** Le stazioni di temperatura vanno dai
47 metri di Gambara ai 2.108 del Pantano d'Avio: la loro media aritmetica è un
numero che non descrive nessun luogo, e cambia se una stazione di montagna apre
o chiude. Ogni stazione si confronta quindi **con sé stessa** — con la propria
media 2004-2013 — e si media lo scostamento, che è la convenzione
climatologica e l'unica che regge a una rete che si muove.

**Cosa esce, in tre righe.** Il PM10 e il biossido di azoto sono crollati di
circa il 40 % e l'ozono no, unico fra i tre a non muoversi. La temperatura sale
di poco più di un grado fra le due finestre, e sale in **tutte** le stazioni del
panel, dalla Bassa al ghiacciaio. La pioggia non dà segnale: sette stazioni su
dodici in aumento e cinque in calo, che è il modo dei dati di dire «non lo so»,
e va scritto invece che nascosto in un arrotondamento.

⚠️ **Quello che questo script non fa, e non può fare.** Non attribuisce nessuna
di queste variazioni a una causa. Un'annata di aria buona può essere una
politica, un impianto chiuso, o un inverno ventoso: la meteorologia governa la
dispersione degli inquinanti tanto quanto le emissioni, e separare le due
richiederebbe una normalizzazione meteorologica che questi dati mensili non
sostengono. Vale anche al contrario per l'ozono, che è un inquinante secondario
con una chimica sua. Qui si misura **cosa hanno respirato le centraline**, non
perché.

Confidenza: `derivato` (MET-4).
"""

from __future__ import annotations

import argparse
import statistics
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _tabelle import leggi, numero, scrivi_csv  # noqa: E402

# I tre inquinanti con una serie abbastanza lunga da reggere un panel. Gli
# altri — PM2.5, benzene, i metalli — cominciano troppo tardi o hanno una sola
# stazione: compaiono nella tabella delle esclusioni invece che nel risultato.
INQUINANTI = ["PM10 (SM2005)", "Biossido di Azoto", "Ozono"]

# Un anno vale se ha almeno dieci mesi osservati: due buchi si tollerano, tre
# no. Sulla pioggia la soglia è dodici, perché un totale annuo a cui manca un
# mese non è un totale annuo — è un totale di undici mesi che sembra piccolo.
MESI_MINIMI_MEDIA = 10
MESI_MINIMI_TOTALE = 12

# La base delle anomalie. Dieci anni, scelti perché sono la finestra in cui la
# rete di temperatura è più popolata: prima ci sono quattro stazioni, dopo la
# metà di quelle che c'erano ha chiuso.
BASE = [str(anno) for anno in range(2004, 2014)]
RECENTE = [str(anno) for anno in range(2016, 2026)]
ANNI_MINIMI_FINESTRA = 8

# Le medie di confronto si prendono su tre anni e non su uno: un singolo anno
# terminale può essere un inverno mite o una siccità, e la storia non deve
# poggiare su di lui.
AMPIEZZA_TRIENNIO = 3

COLONNE = ["serie", "grandezza", "unita", "periodo", "stazioni", "valore"]


# --- lettura ------------------------------------------------------------


def stazioni() -> dict[str, dict[str, str]]:
    return {riga["id_sensore"]: riga for riga in leggi("stazioni_arpa.csv")}


def medie_annue(
    nome_file: str, parametro: str, colonna: str, *, somma: bool = False
) -> dict[str, dict[str, float]]:
    """`id_sensore -> anno -> valore annuo`, dai mesi marcati `osservato`.

    Gli altri stati — `copertura_scarsa`, `lettura_implausibile` — sono esclusi
    e non sostituiti: un mese con poche misure non è un mese basso, è un mese
    che non sappiamo (MET-3).
    """
    per_anno: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for riga in leggi(nome_file):
        if riga["parametro"] != parametro or riga["stato"] != "osservato":
            continue
        valore = numero(riga[colonna])
        if valore is not None:
            per_anno[riga["id_sensore"]][riga["mese"][:4]].append(valore)

    minimo = MESI_MINIMI_TOTALE if somma else MESI_MINIMI_MEDIA
    return {
        sensore: {
            anno: (sum(mesi) if somma else statistics.mean(mesi))
            for anno, mesi in per_sensore.items()
            if len(mesi) >= minimo
        }
        for sensore, per_sensore in per_anno.items()
    }


# --- il panel bilanciato ------------------------------------------------


def panel(serie: dict[str, dict[str, float]], minimo: int = 3) -> tuple[list[str], list[str]]:
    """La finestra più lunga con almeno `minimo` stazioni osservate in tutti i suoi anni.

    Si parte dall'inizio più remoto possibile e si avanza finché il panel non è
    abbastanza popolato: è il compromesso fra «lungo» e «poggiato su qualcosa».
    Restituisce `(anni, sensori)`, o due liste vuote se non esiste.
    """
    ultimo = max((anno for per_sensore in serie.values() for anno in per_sensore), default=None)
    if ultimo is None:
        return [], []
    primo = min(anno for per_sensore in serie.values() for anno in per_sensore)

    for inizio in range(int(primo), int(ultimo) + 1):
        anni = [str(anno) for anno in range(inizio, int(ultimo) + 1)]
        if len(anni) < 2 * AMPIEZZA_TRIENNIO:
            break
        sensori = [s for s, per_sensore in serie.items() if all(a in per_sensore for a in anni)]
        if len(sensori) >= minimo:
            return anni, sensori
    return [], []


def triennio(serie: dict[str, dict[str, float]], sensori: list[str], anni: list[str]) -> float:
    return statistics.mean(serie[s][a] for s in sensori for a in anni)


def media_del_panel(serie: dict[str, dict[str, float]], sensori: list[str], anno: str) -> float:
    return statistics.mean(serie[s][anno] for s in sensori)


def media_ingenua(serie: dict[str, dict[str, float]], anno: str) -> tuple[float, int]:
    """Il conto che si farebbe senza pensarci: tutte le stazioni disponibili."""
    valori = [per_sensore[anno] for per_sensore in serie.values() if anno in per_sensore]
    return (statistics.mean(valori) if valori else float("nan")), len(valori)


# --- le anomalie --------------------------------------------------------


def finestra(per_sensore: dict[str, float], anni: list[str]) -> float | None:
    presenti = [per_sensore[a] for a in anni if a in per_sensore]
    return statistics.mean(presenti) if len(presenti) >= ANNI_MINIMI_FINESTRA else None


def scostamenti(serie: dict[str, dict[str, float]]) -> dict[str, tuple[float, float]]:
    """`id_sensore -> (media base, media recente)`, per le sole stazioni che hanno
    entrambe le finestre abbastanza popolate.

    È il panel bilanciato applicato a due blocchi invece che anno per anno: una
    stazione può avere un buco nel 2015 e restare confrontabile con sé stessa.
    """
    fuori = {}
    for sensore, per_sensore in serie.items():
        base, recente = finestra(per_sensore, BASE), finestra(per_sensore, RECENTE)
        if base is not None and recente is not None:
            fuori[sensore] = (base, recente)
    return fuori


def serie_di_anomalie(
    serie: dict[str, dict[str, float]], sensori: list[str]
) -> dict[str, tuple[float, int]]:
    """`anno -> (anomalia media, stazioni)`: ogni stazione contro la propria base.

    Gli anni in cui è presente **meno di metà** del panel non escono. Le
    anomalie tolgono la quota, non la variabilità: una stazione sola in un anno
    caldo dà `+1,3 °C` alla provincia intera, e negli anni Novanta di questa
    rete ce n'è letteralmente una. Il grafico che ne uscirebbe comincerebbe
    caldo per poi raffreddarsi, il che è il contrario di quello che i dati
    dicono e ha come sola causa chi c'era.
    """
    per_anno: dict[str, list[float]] = defaultdict(list)
    for sensore in sensori:
        base = finestra(serie[sensore], BASE)
        if base is None:
            continue
        for anno, valore in serie[sensore].items():
            per_anno[anno].append(valore - base)

    minimo = max(2, len(sensori) // 2)
    return {
        anno: (statistics.mean(v), len(v))
        for anno, v in sorted(per_anno.items())
        if len(v) >= minimo
    }


# --- le tre letture -----------------------------------------------------


def aria(righe_csv: list[dict[str, str]]) -> None:
    print("L'aria: il panel bilanciato contro il conto ingenuo")
    print("Le centraline aprono e chiudono. La media di quelle che ci sono ogni anno")
    print("misura anche il cambio della rete; il panel tiene solo chi c'è sempre.\n")

    catalogo = stazioni()
    for parametro in INQUINANTI:
        serie = medie_annue("aria_mensile.csv", parametro, "media")
        anni, sensori = panel(serie)
        if not anni:
            print(f"  {parametro}: nessun panel abbastanza popolato\n")
            continue

        primi, ultimi = anni[:AMPIEZZA_TRIENNIO], anni[-AMPIEZZA_TRIENNIO:]
        inizio, fine = triennio(serie, sensori, primi), triennio(serie, sensori, ultimi)
        variazione = (fine / inizio - 1) * 100

        print(f"  {parametro} — panel {anni[0]}–{anni[-1]}, {len(sensori)} stazioni")
        for sensore in sorted(sensori, key=lambda s: catalogo[s]["stazione"]):
            scheda = catalogo[sensore]
            print(f"      {scheda['stazione']:34s} {scheda['comune'] or '—':22s} {scheda['quota']:>5s} m")
        unita = catalogo[sensori[0]]["unita_misura"]
        print(f"    {primi[0]}–{primi[-1]}: {inizio:6.1f} {unita}")
        print(f"    {ultimi[0]}–{ultimi[-1]}: {fine:6.1f} {unita}   {variazione:+.1f} %")

        ingenuo_i, n_i = media_ingenua(serie, anni[0])
        ingenuo_f, n_f = media_ingenua(serie, anni[-1])
        differenza = (ingenuo_f / ingenuo_i - 1) * 100
        print(
            f"    conto ingenuo, per confronto: {ingenuo_i:.1f} ({n_i} staz.) → "
            f"{ingenuo_f:.1f} ({n_f} staz.), {differenza:+.1f} %"
        )
        print()

        for anno in anni:
            righe_csv.append({
                "serie": parametro, "grandezza": "media annua del panel", "unita": unita,
                "periodo": anno, "stazioni": str(len(sensori)),
                "valore": f"{media_del_panel(serie, sensori, anno):.2f}",
            })

    print("  Due crolli e un immobile: è il risultato di questa sezione, e la parte")
    print("  interessante è la terza riga. L'ozono non è un inquinante primario —")
    print("  non esce da un tubo di scappamento, si forma in aria — e questo script")
    print("  può dire che non scende, non perché.\n")


def temperatura(righe_csv: list[dict[str, str]]) -> None:
    print("\nLa temperatura: anomalie, perché le quote vanno dai 47 ai 2.108 metri")
    print(f"Ogni stazione contro la propria media {BASE[0]}–{BASE[-1]}.\n")

    catalogo = stazioni()
    serie = medie_annue("meteo_mensile.csv", "Temperatura", "valore")
    coppie = scostamenti(serie)
    if not coppie:
        print("  nessuna stazione ha entrambe le finestre\n")
        return

    differenze = []
    for sensore, (base, recente) in sorted(
        coppie.items(), key=lambda kv: -float(catalogo[kv[0]]["quota"] or 0)
    ):
        scheda = catalogo[sensore]
        differenze.append(recente - base)
        print(
            f"  {scheda['stazione']:34s} {scheda['quota']:>5s} m   "
            f"{base:5.2f} → {recente:5.2f} °C   {recente - base:+.2f}"
        )

    in_aumento = sum(1 for d in differenze if d > 0)
    print(
        f"\n  {len(differenze)} stazioni, media {statistics.mean(differenze):+.2f} °C, "
        f"mediana {statistics.median(differenze):+.2f} °C"
    )
    print(f"  in aumento: {in_aumento} su {len(differenze)}")
    if in_aumento == len(differenze):
        print("  Nessuna eccezione, ed è la parte che conta: il segno è lo stesso in")
        print("  pianura, in valle e sul ghiacciaio, cioè non lo fa una stazione sola.")

    print("\n  La serie delle anomalie, anno per anno:")
    for anno, (anomalia, quante) in serie_di_anomalie(serie, list(coppie)).items():
        barra = "·" * round(abs(anomalia) * 12)
        segno = "+" if anomalia >= 0 else "−"
        print(f"    {anno}  n={quante}  {anomalia:+.2f} °C  {segno}{barra}")
        righe_csv.append({
            "serie": "Temperatura", "grandezza": f"anomalia sulla base {BASE[0]}–{BASE[-1]}",
            "unita": "°C", "periodo": anno, "stazioni": str(quante), "valore": f"{anomalia:+.2f}",
        })
    print()


def pioggia(righe_csv: list[dict[str, str]]) -> None:
    print("\nLa pioggia: il caso in cui la risposta è «non lo so»")
    print("Stesso metodo, stessa fonte, stessa provincia. Non tutte le domande")
    print("hanno una risposta, e la differenza fra le due va scritta.\n")

    catalogo = stazioni()
    serie = medie_annue("meteo_mensile.csv", "Precipitazione", "valore", somma=True)
    coppie = scostamenti(serie)
    if not coppie:
        print("  nessuna stazione ha entrambe le finestre\n")
        return

    variazioni = []
    for sensore, (base, recente) in sorted(
        coppie.items(), key=lambda kv: -float(catalogo[kv[0]]["quota"] or 0)
    ):
        scheda = catalogo[sensore]
        variazione = (recente / base - 1) * 100
        variazioni.append(variazione)
        print(
            f"  {scheda['stazione']:34s} {scheda['quota']:>5s} m   "
            f"{base:6.0f} → {recente:6.0f} mm   {variazione:+5.1f} %"
        )
        righe_csv.append({
            "serie": "Precipitazione", "grandezza": "variazione fra le due finestre",
            "unita": "%", "periodo": f"{BASE[0]}–{BASE[-1]} → {RECENTE[0]}–{RECENTE[-1]}",
            "stazioni": "1", "valore": f"{variazione:+.1f}",
        })

    in_aumento = sum(1 for v in variazioni if v > 0)
    print(
        f"\n  {len(variazioni)} stazioni, mediana {statistics.median(variazioni):+.1f} %, "
        f"in aumento {in_aumento} su {len(variazioni)}"
    )
    print("  Il segno non è concorde e la mediana è mezzo punto: con questa rete e")
    print("  questa finestra la pioggia non dice niente. Che è un risultato, e va")
    print("  tenuto accanto al grado di temperatura invece che tolto di mezzo —")
    print("  una serie con un segnale e una senza, dalla stessa fonte, sono anche")
    print("  la prova che il segnale della prima non è un artefatto del metodo.\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="aria_e_clima")
    parser.add_argument("--save", action="store_true", help="scrive il CSV in analysis/output/")
    args = parser.parse_args(argv)

    righe_csv: list[dict[str, str]] = []
    aria(righe_csv)
    temperatura(righe_csv)
    pioggia(righe_csv)

    if args.save:
        print(f"scritto {scrivi_csv('aria_e_clima.csv', COLONNE, righe_csv)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
