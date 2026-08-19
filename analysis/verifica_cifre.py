"""Ricalcola dai CSV ogni cifra citata nei documenti del progetto.

    python analysis/verifica_cifre.py           # elenco delle verifiche
    python analysis/verifica_cifre.py --csv     # scrive analysis/output/verifica_cifre.csv

Il principio è in `BRIEF.md` («ogni numero citato ha uno script o una metrica
dietro») e in `PROSSIMI-PASSI.md` §5.4. Finché i numeri stavano solo nei testi
non erano verificabili, e infatti due erano sbagliati: la mediana della
popolazione comunale (2.000 invece di 3.671) e la crescita degli addetti nella
fascia 10–249 (13 mila invece di 23.840). Sono stati corretti nei documenti ad
agosto 2026 grazie a questo script, che da qui in avanti li tiene onesti.

Solo libreria standard: le tabelle sono piccole e la pipeline non ha pandas.
Ogni verifica dichiara il documento e la cifra attesa; l'uscita è 1 se anche
una sola diverge oltre la tolleranza, così lo script può stare in CI.
"""

from __future__ import annotations

import argparse
import csv
import statistics
import sys
from collections import defaultdict
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
PROCESSED = RADICE / "dati" / "processed"
OUTPUT = Path(__file__).resolve().parent / "output"

CAPOLUOGO = "017029"


def leggi(nome: str) -> list[dict[str, str]]:
    with (PROCESSED / nome).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def numero(valore: str | None) -> float | None:
    """Le celle vuote sono dati mancanti, non zeri (MET-3)."""
    if valore is None or valore == "":
        return None
    return float(valore)


# --- le fonti dei numeri ------------------------------------------------

sintesi = leggi("comuni_sintesi.csv")
geometria = leggi("comuni_geometria.csv")
imprese = leggi("imprese_classe_addetti.csv")
turismo = leggi("turismo_comuni_annuale.csv")
aria = leggi("aria_mensile.csv")
stazioni = leggi("stazioni_arpa.csv")


def addetti(anno: str, classe: str, indicatore: str = "addetti", comune: str | None = None) -> float:
    totale = 0.0
    for riga in imprese:
        if riga["anno"] != anno or riga["classe_addetti"] != classe:
            continue
        if riga["indicatore"] != indicatore:
            continue
        if comune is not None and riga["codice_istat"] != comune:
            continue
        valore = numero(riga["valore"])
        if valore is not None:
            totale += valore
    return totale


def presenze_2024() -> dict[str, float]:
    """Presenze per comune, 2024, con il doppio filtro Totale/Totale.

    Senza quel filtro le stesse notti si contano fino a tre volte
    (`dati/README.md`); le righe `zero_fittizio` restano fuori, perché quello
    zero è calcolato su celle soppresse, non misurato.
    """
    per_comune: dict[str, float] = {}
    for riga in turismo:
        if riga["anno"] != "2024" or riga["stato"] != "osservato":
            continue
        if riga["tipo_struttura"] != "Totale" or riga["cittadinanza"] != "Totale":
            continue
        valore = numero(riga["presenze"])
        if valore is not None:
            per_comune[riga["codice_istat"]] = valore
    return per_comune


def media_pm10_broletto(anno: str) -> float:
    """Media delle medie mensili PM10 alla stazione Brescia v.Broletto.

    ⚠️ È una media di medie mensili non pesata sui giorni: nel 2001 i mesi
    disponibili sono 11 su 12. Serve a riprodurre la cifra citata, non come
    media annua ufficiale.
    """
    sensori = {
        r["id_sensore"]
        for r in stazioni
        if "Broletto" in r["stazione"] and r["parametro"].startswith("PM10")
    }
    medie = [
        numero(r["media"])
        for r in aria
        if r["id_sensore"] in sensori and r["mese"].startswith(anno) and r["media"]
    ]
    valide = [m for m in medie if m is not None]
    return sum(valide) / len(valide)


# --- le verifiche -------------------------------------------------------
# (documento, cifra citata, valore atteso, funzione, tolleranza)

VERIFICHE: list[tuple[str, str, float, object, float]] = [
    (
        "BRIEF §Unità di analisi",
        "205 comuni nella provincia",
        205,
        lambda: len(sintesi),
        0,
    ),
    (
        "dati/README §La geometria",
        "superficie provinciale 4.785,3 km²",
        4785.3,
        lambda: sum(float(r["area_kmq"]) for r in geometria),
        0.1,
    ),
    (
        "BRIEF §Unità di analisi / METODOLOGIA MET-2",
        "popolazione del capoluogo 2024: 199.853",
        199853,
        lambda: next(int(r["popolazione_2024"]) for r in sintesi if r["codice_istat"] == CAPOLUOGO),
        0,
    ),
    (
        "METODOLOGIA MET-2, MET-5",
        "mediana della popolazione comunale: 3.671",
        3671,
        lambda: statistics.median(int(r["popolazione_2024"]) for r in sintesi),
        0,
    ),
    (
        "METODOLOGIA MET-2",
        "il capoluogo è il 16 % della popolazione provinciale",
        15.8,
        lambda: next(int(r["popolazione_2024"]) for r in sintesi if r["codice_istat"] == CAPOLUOGO)
        / sum(int(r["popolazione_2024"]) for r in sintesi)
        * 100,
        0.1,
    ),
    (
        "FONTI §1-bis",
        "unità locali in provincia, 2023: 119.565",
        119565,
        lambda: addetti("2023", "totale", "unita_locali"),
        1,
    ),
    (
        "FONTI §1-bis / WORKING-PAPER §7",
        "addetti in provincia, 2023: 479.418",
        479418,
        lambda: addetti("2023", "totale"),
        1,
    ),
    (
        "BRIEF §Storie / WORKING-PAPER §7",
        "unità locali sotto i 10 addetti, 2023: 92,7 %",
        92.7,
        lambda: addetti("2023", "0-9", "unita_locali") / addetti("2023", "totale", "unita_locali") * 100,
        0.05,
    ),
    (
        "BRIEF §Storie / WORKING-PAPER §7",
        "addetti in unità sotto i 10, 2023: 42,9 %",
        42.9,
        lambda: addetti("2023", "0-9") / addetti("2023", "totale") * 100,
        0.05,
    ),
    (
        "FONTI §1-bis / METODOLOGIA MET-8",
        "la provincia guadagna 29.421 addetti fra 2018 e 2023",
        29421,
        lambda: addetti("2023", "totale") - addetti("2018", "totale"),
        2,
    ),
    (
        "BRIEF §Storie / WORKING-PAPER §7",
        "addetti in unità 10–249: +23.840 fra 2018 e 2023",
        23840,
        lambda: (addetti("2023", "10-49") + addetti("2023", "50-249"))
        - (addetti("2018", "10-49") + addetti("2018", "50-249")),
        2,
    ),
    (
        "FONTI §1-bis / WORKING-PAPER §6.1",
        "il capoluogo è fermo: −197 addetti fra 2018 e 2023",
        -197,
        lambda: addetti("2023", "totale", comune=CAPOLUOGO)
        - addetti("2018", "totale", comune=CAPOLUOGO),
        1,
    ),
    (
        "FONTI §1-bis / WORKING-PAPER §6.1",
        "addetti in unità ≥250 nel capoluogo: −6.335",
        -6335,
        lambda: addetti("2023", "250+", comune=CAPOLUOGO) - addetti("2018", "250+", comune=CAPOLUOGO),
        1,
    ),
    (
        "FONTI §1-bis",
        "unità locali ≥250 nel capoluogo: 35 → 28",
        28,
        lambda: addetti("2023", "250+", "unita_locali", comune=CAPOLUOGO),
        0,
    ),
    (
        "FONTI §1-bis",
        "il capoluogo vale il 21 % degli addetti provinciali",
        21.1,
        lambda: addetti("2023", "totale", comune=CAPOLUOGO) / addetti("2023", "totale") * 100,
        0.1,
    ),
    (
        "FONTI §1-bis",
        "quota degli addetti in unità ≥250, città: 13,6 %",
        13.6,
        lambda: addetti("2023", "250+", comune=CAPOLUOGO)
        / addetti("2023", "totale", comune=CAPOLUOGO)
        * 100,
        0.05,
    ),
    (
        "README / BRIEF §Storie / WORKING-PAPER §7",
        "presenze turistiche provinciali 2024: 12.246.854",
        12246854,
        lambda: sum(presenze_2024().values()),
        1,
    ),
    (
        "README / BRIEF §Storie",
        "i primi dieci comuni fanno il 68,8 % delle presenze",
        68.8,
        lambda: sum(sorted(presenze_2024().values(), reverse=True)[:10])
        / sum(presenze_2024().values())
        * 100,
        0.05,
    ),
    (
        "WORKING-PAPER §7",
        "Brescia città: 883.531 presenze, il 7,2 % del totale",
        7.2,
        lambda: presenze_2024()[CAPOLUOGO] / sum(presenze_2024().values()) * 100,
        0.05,
    ),
    (
        "METODOLOGIA MET-3",
        "45 comuni su 178 hanno le presenze 2024 soppresse",
        45,
        lambda: sum(
            1
            for r in turismo
            if r["anno"] == "2024"
            and r["tipo_struttura"] == "Totale"
            and r["cittadinanza"] == "Totale"
            and r["stato"] == "riservato"
        ),
        0,
    ),
    (
        "dati/README §Territorio",
        "Odolo: 89,6 addetti ogni 100 abitanti",
        89.6,
        lambda: next(float(r["addetti_per_100_abitanti"]) for r in sintesi if r["comune"] == "Odolo"),
        0.05,
    ),
    (
        "PROSSIMI-PASSI §4",
        "Limone sul Garda: 133 addetti ogni 100 abitanti",
        133.0,
        lambda: next(
            float(r["addetti_per_100_abitanti"]) for r in sintesi if r["comune"] == "Limone sul Garda"
        ),
        0.05,
    ),
    (
        "WORKING-PAPER §7",
        "PM10 a Brescia v.Broletto, 2001: 45,5 µg/m³",
        45.5,
        lambda: media_pm10_broletto("2001"),
        0.05,
    ),
    (
        "WORKING-PAPER §7",
        "PM10 a Brescia v.Broletto, 2024: 27,3 µg/m³",
        27.3,
        lambda: media_pm10_broletto("2024"),
        0.05,
    ),
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="verifica_cifre")
    parser.add_argument("--csv", action="store_true", help="scrive anche analysis/output/verifica_cifre.csv")
    args = parser.parse_args(argv)

    righe: list[dict[str, str]] = []
    divergenti = 0

    print(f"{'esito':6} {'cifra citata':62} {'atteso':>14} {'calcolato':>14}")
    print("-" * 100)
    for documento, cifra, atteso, calcola, tolleranza in VERIFICHE:
        ottenuto = float(calcola())
        ok = abs(ottenuto - atteso) <= tolleranza
        divergenti += not ok
        print(f"{'ok' if ok else 'DIVERGE':6} {cifra[:62]:62} {atteso:>14,.2f} {ottenuto:>14,.2f}")
        righe.append(
            {
                "documento": documento,
                "cifra": cifra,
                "atteso": f"{atteso:.4f}",
                "calcolato": f"{ottenuto:.4f}",
                "tolleranza": f"{tolleranza:.4f}",
                "esito": "ok" if ok else "diverge",
            }
        )

    print("-" * 100)
    print(f"{len(VERIFICHE)} verifiche, {divergenti} divergenti")

    if args.csv:
        OUTPUT.mkdir(parents=True, exist_ok=True)
        destinazione = OUTPUT / "verifica_cifre.csv"
        with destinazione.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=["documento", "cifra", "atteso", "calcolato", "tolleranza", "esito"],
                lineterminator="\n",
            )
            writer.writeheader()
            writer.writerows(righe)
        print(f"scritto {destinazione.relative_to(RADICE)}")

    return 1 if divergenti else 0


if __name__ == "__main__":
    sys.exit(main())
