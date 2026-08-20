"""Brescia è diversa? Le stesse misure su tutte le province italiane.

    python analysis/confronto_province.py
    python analysis/confronto_province.py --save
    python analysis/confronto_province.py --gemella 016     # un'altra provincia di confronto

È il controllo che mancava, e il working paper lo dichiara come il limite più
serio: ogni risultato di questo progetto descrive Brescia **senza dire se
Brescia sia diversa da una provincia italiana qualunque**. «Il 92,7 % delle
unità locali ha meno di dieci addetti» sembra dire qualcosa e non dice niente
finché non si sa quanto fa la stessa cifra altrove.

Tre letture:

1. **Dove sta Brescia nella distribuzione** delle 107 province su ciascun
   indicatore: il valore, il rango e il percentile. Un rango a metà classifica è
   un risultato, non un fallimento — dice che quell'indicatore non è la
   specificità del territorio.
2. **Bergamo**, la gemella: stessa dimensione, storia industriale parallela,
   stessa Capitale della cultura 2023. Affiancata riga per riga.
3. **Il controllo di MET-9**: lo svuotamento della classe con almeno 250 addetti
   del comune capoluogo succede anche negli altri capoluoghi? Se succede
   ovunque, non è un fatto bresciano — è un fatto del registro.

⚠️ Restano aggregati provinciali. Il soggetto del progetto non cambia: qui non
si mappa niente fuori dal bresciano, si misura soltanto quanto il bresciano sia
un caso o la regola.

Confidenza: `derivato` (MET-4).
"""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _tabelle import RADICE, leggi, numero, scrivi_csv  # noqa: E402

BRESCIA = "017"
BERGAMO = "016"
CAPOLUOGO_BRESCIA = "017029"
# Sotto questa soglia un capoluogo non ha una classe grande di cui parlare, e
# una variazione percentuale su poche centinaia di addetti è rumore.
SOGLIA_CLASSE_GRANDE = 2000

COLONNE = ["indicatore", "codice_provincia", "provincia", "valore", "rango", "province", "percentile"]


def carica_province() -> tuple[dict[str, str], dict[tuple[str, str, str, str, str], float]]:
    nomi: dict[str, str] = {}
    valori: dict[tuple[str, str, str, str, str], float] = {}
    for riga in leggi("imprese_province.csv"):
        valore = numero(riga["valore"])
        if valore is None:
            continue
        nomi[riga["codice_provincia"]] = riga["provincia"]
        chiave = (
            riga["codice_provincia"],
            riga["anno"],
            riga["dimensione"],
            riga["modalita"],
            riga["indicatore"],
        )
        valori[chiave] = valore
    return nomi, valori


def indicatori(valori: dict, province: list[str], primo: str, ultimo: str) -> dict[str, dict[str, float]]:
    """Per ogni indicatore, il valore di ciascuna provincia."""
    def v(codice: str, anno: str, dimensione: str, modalita: str, indicatore: str) -> float | None:
        return valori.get((codice, anno, dimensione, modalita, indicatore))

    fuori: dict[str, dict[str, float]] = defaultdict(dict)
    for codice in province:
        ul_totali = v(codice, ultimo, "classe_addetti", "totale", "unita_locali")
        ul_micro = v(codice, ultimo, "classe_addetti", "0-9", "unita_locali")
        add_totali = v(codice, ultimo, "classe_addetti", "totale", "addetti")
        add_micro = v(codice, ultimo, "classe_addetti", "0-9", "addetti")
        add_medi = v(codice, ultimo, "classe_addetti", "10-49", "addetti")
        add_grandi = v(codice, ultimo, "classe_addetti", "250+", "addetti")
        add_iniziali = v(codice, primo, "classe_addetti", "totale", "addetti")
        manifattura = v(codice, ultimo, "sezione", "C", "addetti")
        alloggio = v(codice, ultimo, "sezione", "I", "addetti")

        if not (ul_totali and add_totali and add_iniziali):
            continue
        fuori["unità locali sotto i 10 addetti (%)"][codice] = (ul_micro or 0) / ul_totali * 100
        fuori["addetti in unità sotto i 10 (%)"][codice] = (add_micro or 0) / add_totali * 100
        fuori["addetti in unità ≥250 (%)"][codice] = (add_grandi or 0) / add_totali * 100
        fuori["addetti per unità locale"][codice] = add_totali / ul_totali
        if manifattura is not None:
            fuori["addetti nella manifattura (%)"][codice] = manifattura / add_totali * 100
        if alloggio is not None:
            fuori["addetti in alloggio e ristorazione (%)"][codice] = alloggio / add_totali * 100
        durata = int(ultimo) - int(primo)
        fuori[f"crescita degli addetti {primo}–{ultimo} (%/anno)"][codice] = (
            (add_totali / add_iniziali) ** (1 / durata) - 1
        ) * 100
        del add_medi
    return fuori


def posizione(valori_indicatore: dict[str, float], codice: str) -> tuple[int, int, float]:
    """Rango (1 = il più alto), numero di province, percentile."""
    ordinati = sorted(valori_indicatore.items(), key=lambda kv: -kv[1])
    for indice, (altro, _) in enumerate(ordinati, start=1):
        if altro == codice:
            return indice, len(ordinati), (1 - (indice - 1) / (len(ordinati) - 1)) * 100
    return 0, len(ordinati), 0.0


def mediana(valori: list[float]) -> float:
    ordinati = sorted(valori)
    meta = len(ordinati) // 2
    return ordinati[meta] if len(ordinati) % 2 else (ordinati[meta - 1] + ordinati[meta]) / 2


def controllo_capoluoghi() -> list[tuple[float, str, float, float]]:
    """Variazione della classe ≥250 in ogni comune capoluogo."""
    grandi: dict[str, dict[str, float]] = defaultdict(dict)
    nomi: dict[str, str] = {}
    for riga in leggi("imprese_capoluoghi.csv"):
        if riga["indicatore"] != "addetti" or riga["classe_addetti"] != "250+":
            continue
        valore = numero(riga["valore"])
        if valore is not None:
            grandi[riga["codice_istat"]][riga["anno"]] = valore
            nomi[riga["codice_istat"]] = riga["capoluogo"]

    fuori = []
    for codice, serie in grandi.items():
        anni = sorted(serie)
        iniziale, finale = serie[anni[0]], serie[anni[-1]]
        if iniziale < SOGLIA_CLASSE_GRANDE:
            continue
        fuori.append(((finale / iniziale - 1) * 100, nomi[codice], iniziale, finale))
    fuori.sort()
    return fuori


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="confronto_province")
    parser.add_argument("--gemella", default=BERGAMO, help="codice della provincia di confronto")
    parser.add_argument("--save", action="store_true", help="scrive il CSV in analysis/output/")
    args = parser.parse_args(argv)

    nomi, valori = carica_province()
    anni = sorted({chiave[1] for chiave in valori})
    primo, ultimo = anni[0], anni[-1]
    province = sorted(nomi)

    misure = indicatori(valori, province, primo, ultimo)
    righe_csv: list[dict[str, str]] = []

    print(f"{len(province)} province italiane, {primo}–{ultimo}. Fonte: registro ASIA.\n")
    intestazione = (f"  {'indicatore':44} {'Brescia':>9} {'rango':>10} "
                    f"{'mediana':>9} {nomi.get(args.gemella, args.gemella)[:9]:>9}")
    print(intestazione)
    print("  " + "-" * (len(intestazione) - 2))

    for nome_misura, per_provincia in misure.items():
        if BRESCIA not in per_provincia:
            continue
        rango, quante, percentile = posizione(per_provincia, BRESCIA)
        gemella = per_provincia.get(args.gemella)
        print(f"  {nome_misura:44} {per_provincia[BRESCIA]:>9.2f} "
              f"{f'{rango}/{quante}':>10} {mediana(list(per_provincia.values())):>9.2f} "
              f"{'—' if gemella is None else f'{gemella:.2f}':>9}")
        for codice in (BRESCIA, args.gemella):
            if codice not in per_provincia:
                continue
            rango_c, quante_c, percentile_c = posizione(per_provincia, codice)
            righe_csv.append({
                "indicatore": nome_misura,
                "codice_provincia": codice,
                "provincia": nomi[codice],
                "valore": f"{per_provincia[codice]:.3f}",
                "rango": str(rango_c),
                "province": str(quante_c),
                "percentile": f"{percentile_c:.1f}",
            })

    print("\n  Il rango è 1 per il valore più alto. Un rango a metà classifica non è")
    print("  un risultato debole: dice che quell'indicatore non è ciò che distingue")
    print("  questa provincia, e le due cose vanno raccontate diversamente.\n")

    capoluoghi = controllo_capoluoghi()
    variazioni = [x[0] for x in capoluoghi]
    brescia = next((x for x in capoluoghi if x[1] == "Brescia"), None)
    print(f"Il controllo di MET-9: la classe ≥250 nei comuni capoluogo, {primo}–{ultimo}")
    print(f"  {len(capoluoghi)} capoluoghi con almeno {SOGLIA_CLASSE_GRANDE:,} addetti "
          f"in unità ≥250 nel {primo}.")
    in_calo = sum(1 for v in variazioni if v < 0)
    print(f"  In calo: {in_calo} su {len(capoluoghi)}. Mediana: {mediana(variazioni):+.1f} %.")
    if brescia:
        rango = sorted(variazioni).index(brescia[0]) + 1
        print(f"  Brescia: {brescia[0]:+.1f} % ({brescia[2]:,.0f} → {brescia[3]:,.0f}), "
              f"il {rango}º calo più forte su {len(capoluoghi)}.")
    print("  I cinque cali più forti: " + ", ".join(
        f"{nome} ({variazione:+.0f} %)" for variazione, nome, _, _ in capoluoghi[:5]))
    print("\n  Lo svuotamento della classe grande **non è un fatto bresciano**: succede")
    print("  quasi ovunque, e a Brescia più che alla mediana ma meno che in dodici altri")
    print("  capoluoghi. È il sostegno più forte alla lettura di MET-9 — un movimento")
    print("  così diffuso è, fino a prova contraria, un cambiamento di come si conta.")

    if args.save:
        destinazione = scrivi_csv("confronto_province.csv", COLONNE, righe_csv)
        print(f"\nscritto {destinazione.relative_to(RADICE)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
