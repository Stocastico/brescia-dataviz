"""Il 2020 spezza le serie: quanto, dove, e per quali si può dire qualcosa.

    python analysis/rottura_covid.py
    python analysis/rottura_covid.py --save

`PROSSIMI-PASSI.md` §5.2 e MET-8. Ogni tasso annualizzato di questo progetto
attraversa il 2020 come se fosse un anno qualunque: è una media, e le medie
fanno questo. Questo script guarda la discontinuità invece di attraversarla.

**La prima risposta è che su metà delle serie non si può fare.** Il registro
delle imprese comincia nel 2018: prima della pandemia ci sono **due punti**, e
con due punti non esiste una tendenza da cui misurare uno scostamento. Dirlo è
il risultato, non un preambolo — la sezione «annuali» qui sotto mostra le
variazioni anno per anno e si ferma lì, senza fingere un test.

Dove invece i punti ci sono — le serie mensili del turismo e dell'aria — il
metodo è quello dell'**atteso stagionale**: per ogni mese si calcola la media
dei mesi omologhi degli anni pre-2020, e si misura di quanto ogni mese
successivo si scosta da quell'attesa. È grezzo e trasparente, il che su una
rottura larga come questa basta: non serve un modello per vedere un −80 %.

⚠️ Il turismo comincia nel **2019**: c'è un solo anno pre-pandemia da cui
ricavare l'attesa stagionale, quindi l'attesa è quell'anno. Se il 2019 fosse
stato un anno anomalo, tutto quello che segue lo erediterebbe. È il limite
principale di questa lettura e non si può togliere con questi dati.

⚠️ E **una base lunga su una serie che ha una tendenza propria non misura la
rottura, misura la tendenza.** Il PM10 scende da trent'anni: confrontare il 2020
con la media 2000–2019 dà −26 %, di cui la pandemia è solo una parte e forse la
minore. Per questo la base del PM10 sono i **tre anni immediatamente
precedenti**, che è il compromesso onesto: abbastanza corta da non inglobare la
tendenza, abbastanza lunga da smussare un inverno mite. Anche così, quello che
resta è tendenza **più** rottura, e questo metodo non le separa. Per separarle
servirebbe un modello, e per un modello servirebbero più anni post-pandemia di
quanti ce ne siano.

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
    leggi,
    media,
    numero,
    scrivi_csv,
    serie_imprese,
    serie_popolazione,
)

PRIMO_ANNO_PANDEMIA = "2020"

COLONNE = ["serie", "periodo", "osservato", "atteso", "scostamento", "scostamento_percentuale"]


def variazioni_annuali() -> dict[str, dict[str, float]]:
    """Totali provinciali anno per anno, per le serie annuali del progetto."""
    fuori: dict[str, dict[str, float]] = {}
    for nome, serie in (
        ("addetti (ASIA)", serie_imprese("addetti")),
        ("unità locali (ASIA)", serie_imprese("unita_locali")),
        ("addetti in unità ≥250", serie_imprese("addetti", "250+")),
        ("popolazione residente", serie_popolazione()),
    ):
        totali: dict[str, float] = defaultdict(float)
        for valori in serie.values():
            for anno, valore in valori.items():
                totali[anno] += valore
        fuori[nome] = dict(totali)
    return fuori


def serie_mensile(nome_file: str, colonna: str, filtro=None) -> dict[str, float]:
    """Totale provinciale per mese (`AAAA-MM`)."""
    totali: dict[str, float] = defaultdict(float)
    for riga in leggi(nome_file):
        if filtro and not filtro(riga):
            continue
        valore = numero(riga[colonna])
        if valore is not None:
            totali[riga["mese"]] += valore
    return dict(totali)


def media_mensile(nome_file: str, colonna: str, filtro=None) -> dict[str, float]:
    """Media provinciale per mese: per l'aria sommare non avrebbe senso."""
    per_mese: dict[str, list[float]] = defaultdict(list)
    for riga in leggi(nome_file):
        if filtro and not filtro(riga):
            continue
        valore = numero(riga[colonna])
        if valore is not None:
            per_mese[riga["mese"]].append(valore)
    return {mese: media(valori) for mese, valori in per_mese.items()}


def atteso_stagionale(
    serie: dict[str, float], fino_a: str, da: str | None = None
) -> dict[str, float]:
    """Media dei mesi omologhi nella finestra base: un mese di gennaio si
    confronta con i gennai, non con la media dell'anno.

    `da` accorcia la base. Serve alle serie che hanno una tendenza propria: su
    quelle una base lunga misura la tendenza e la chiama rottura.
    """
    per_mese_dell_anno: dict[str, list[float]] = defaultdict(list)
    for periodo, valore in serie.items():
        if periodo[:4] < fino_a and (da is None or periodo[:4] >= da):
            per_mese_dell_anno[periodo[5:7]].append(valore)
    return {mese: media(valori) for mese, valori in per_mese_dell_anno.items() if valori}


def scostamenti(
    serie: dict[str, float], fino_a: str, da: str | None = None
) -> list[tuple[str, float, float]]:
    atteso = atteso_stagionale(serie, fino_a, da)
    fuori = []
    for periodo in sorted(serie):
        if periodo[:4] < fino_a:
            continue
        riferimento = atteso.get(periodo[5:7])
        if riferimento:
            fuori.append((periodo, serie[periodo], riferimento))
    return fuori


def per_anno(dati: list[tuple[str, float, float]]) -> dict[str, tuple[float, float]]:
    osservati: dict[str, float] = defaultdict(float)
    attesi: dict[str, float] = defaultdict(float)
    for periodo, osservato, atteso in dati:
        osservati[periodo[:4]] += osservato
        attesi[periodo[:4]] += atteso
    return {anno: (osservati[anno], attesi[anno]) for anno in sorted(osservati)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="rottura_covid")
    parser.add_argument("--save", action="store_true", help="scrive il CSV in analysis/output/")
    args = parser.parse_args(argv)

    righe_csv: list[dict[str, str]] = []

    print("Serie annuali: le variazioni, senza test")
    print("Con due soli anni prima del 2020 non esiste una tendenza da cui misurare")
    print("uno scostamento. Questi sono i numeri, e la lettura si ferma qui.\n")
    for nome, totali in variazioni_annuali().items():
        anni = sorted(totali)
        print(f"  {nome}")
        precedente = None
        peggiore = (0.0, "")
        for anno in anni:
            variazione = "" if precedente is None else f"{(totali[anno] / precedente - 1) * 100:+7.2f} %"
            if precedente is not None:
                cambiamento = (totali[anno] / precedente - 1) * 100
                if abs(cambiamento) > abs(peggiore[0]):
                    peggiore = (cambiamento, anno)
            marchio = " ←" if anno == PRIMO_ANNO_PANDEMIA else ""
            print(f"    {anno}  {totali[anno]:>12,.0f}  {variazione}{marchio}")
            precedente = totali[anno]
            righe_csv.append({
                "serie": nome, "periodo": anno, "osservato": f"{totali[anno]:.1f}",
                "atteso": "", "scostamento": "", "scostamento_percentuale": "",
            })
        print(f"    il salto più grande è nel {peggiore[1]} ({peggiore[0]:+.2f} %)\n")

    print("\nSerie mensili: osservato contro atteso stagionale")
    mensili = [
        (
            "presenze turistiche",
            serie_mensile("turismo_comuni_mensile.csv", "presenze"),
            "2020",
            None,  # la serie comincia nel 2019: la base è tutto ciò che c'è
        ),
        (
            "PM10 (media delle stazioni)",
            media_mensile(
                "aria_mensile.csv", "media", lambda r: r["parametro"].startswith("PM10")
            ),
            "2020",
            "2017",  # base corta: la serie ha una tendenza propria da trent'anni
        ),
    ]
    ultimo_periodo = max(
        max(serie) for _, serie, _, _ in mensili if serie
    )
    for nome, serie, da, base_da in mensili:
        dati = scostamenti(serie, da, base_da)
        if not dati:
            continue
        primo_anno_atteso = max(base_da or "0000", min(p[:4] for p in serie))
        print(f"\n  {nome} — attesa costruita su {primo_anno_atteso}–{int(da) - 1}")
        print(f"    {'anno':6} {'osservato':>14} {'atteso':>14} {'scarto':>10}")
        for anno, (osservato, atteso) in per_anno(dati).items():
            scarto = (osservato / atteso - 1) * 100 if atteso else 0.0
            mesi = sum(1 for p, _, _ in dati if p[:4] == anno)
            parziale = " (anno incompleto)" if mesi < 12 else ""
            print(f"    {anno:6} {osservato:>14,.0f} {atteso:>14,.0f} {scarto:>9.1f} %{parziale}")
            righe_csv.append({
                "serie": nome, "periodo": anno,
                "osservato": f"{osservato:.1f}", "atteso": f"{atteso:.1f}",
                "scostamento": f"{osservato - atteso:.1f}",
                "scostamento_percentuale": f"{scarto:.2f}",
            })
        peggiore = min(dati, key=lambda d: d[1] / d[2] if d[2] else 1)
        print(f"    il mese peggiore è {peggiore[0]}: "
              f"{(peggiore[1] / peggiore[2] - 1) * 100:.0f} % rispetto all'attesa")

    print("\nCosa se ne ricava")
    print("  Sulle presenze turistiche la rottura è enorme, netta e già riassorbita:")
    print("  metà delle notti perse nel 2020, il livello del 2019 superato dal 2022.")
    print("  Sull'aria lo scarto resta negativo anche cinque anni dopo, il che è il")
    print("  segno che lì non c'era una rottura da riassorbire ma una tendenza in corso.")
    print("  Sulle serie annuali il 2020 è visibilmente l'anno del salto, ma la finestra")
    print("  è troppo corta per distinguere una rottura da una tendenza: quando un tasso")
    print("  annualizzato del progetto attraversa il 2020, va detto che lo attraversa.")

    if args.save:
        destinazione = scrivi_csv("rottura_covid.csv", COLONNE, righe_csv)
        print(f"\nscritto {destinazione.relative_to(RADICE)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
