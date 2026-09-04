"""Assembla il sito statico in `_site/`, con i dati dentro il file.

    python sito/costruisci.py               # -> _site/
    python sito/costruisci.py --uscita /tmp/prova

Tre proprietà, ereditate dal progetto Donostia (`PROSSIMI-PASSI.md` §6.1) e
mantenute qui apposta:

1. **Un solo file HTML autocontenuto.** I dati sono incorporati in una riga
   `window.DATI = {…}`, lo stile e il codice dei grafici sono in linea: nessuna
   `fetch()`, nessuna CDN, nessuna chiave. Il documento si apre da disco, si
   manda per email, si archivia e fra dieci anni funziona ancora.
2. **I grafici sono SVG disegnati a mano in JavaScript.** Sembra masochismo ed è
   il motivo per cui il punto 1 è possibile.
3. **Nessun numero è scritto a mano nel testo.** Ogni cifra del racconto è un
   segnaposto `{{c:nome}}` che questo script calcola dai JSON della pipeline. Se
   un dato cambia, il testo cambia con lui; se un segnaposto non ha un valore, la
   costruzione fallisce invece di pubblicare una frase con un buco. È la regola
   «ogni numero ha uno script dietro» (`BRIEF.md`) applicata al prodotto finale
   invece che ai documenti di lavoro.

Le date non si scrivono a mano per lo stesso motivo: `{{BUILD_DATE}}` viene da
oggi (o da `--data-build`, che il workflow di deploy passa dalla data del
commit) e `{{DATA_DATE}}` dall'**ultimo commit che ha toccato
`dati/processed/`**, cioè da quando i numeri sono cambiati davvero. Senza questo
meccanismo le date invecchiano in silenzio e il sito mente.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import subprocess
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

RADICE = Path(__file__).resolve().parent.parent
MODELLI = Path(__file__).resolve().parent / "modelli"
DATI_WEB = RADICE / "web" / "src" / "data"
PROCESSED = RADICE / "dati" / "processed"

CAPOLUOGO = "017029"

# Gli indicatori che finiscono nel documento. Tenerli espliciti invece di
# incorporare tutto: il file autocontenuto pesa quanto ci si mette dentro.
METRICHE_USATE = [
    "popolazione",
    "crescita_popolazione",
    "addetti",
    "crescita_addetti",
    "addetti_per_100_abitanti",
    "dimensione_media",
    "quota_micro",
    "reddito_medio",
    "crescita_reddito",
    "presenze_per_abitante",
    "quota_manifattura",
    "quota_alloggio_ristorazione",
    "specializzazione",
    "prezzo_case",
    "variazione_prezzo_reale",
]

PAGINE = {
    "racconto.html": "index.html",
    "metodologia.html": "metodologia.html",
    "dati.html": "dati.html",
}


# --- numeri in italiano --------------------------------------------------


def numero_it(valore: float, decimali: int = 0) -> str:
    """1234.5 -> «1.234,5». Il separatore delle migliaia è il punto."""
    testo = f"{valore:,.{decimali}f}"
    return testo.replace(",", "\x00").replace(".", ",").replace("\x00", ".")


def percento_it(valore: float, decimali: int = 1) -> str:
    return f"{numero_it(valore, decimali)} %"


# --- lettura dei JSON della pipeline ------------------------------------


def leggi_metrica(id_metrica: str) -> dict[str, Any] | None:
    path = DATI_WEB / f"metric_{id_metrica}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def valori(metrica: dict[str, Any], periodo: str | None = None) -> dict[str, float]:
    """I valori di un periodo (l'ultimo, se non specificato)."""
    scelto = periodo or metrica["periods"][-1]
    return {
        codice: per_comune[scelto]
        for codice, per_comune in metrica["values"].items()
        if scelto in per_comune and per_comune[scelto] is not None
    }


def mediana(valori_lista: list[float]) -> float:
    ordinati = sorted(valori_lista)
    meta = len(ordinati) // 2
    return ordinati[meta] if len(ordinati) % 2 else (ordinati[meta - 1] + ordinati[meta]) / 2


def pearson(x: list[float], y: list[float]) -> float:
    mx, my = sum(x) / len(x), sum(y) / len(y)
    num = sum((a - mx) * (b - my) for a, b in zip(x, y))
    dx = math.sqrt(sum((a - mx) ** 2 for a in x))
    dy = math.sqrt(sum((b - my) ** 2 for b in y))
    return num / (dx * dy) if dx and dy else 0.0


# --- due calcoli che il racconto cita e che nessun JSON contiene --------


def contiguita() -> dict[str, set[str]]:
    """Vicini per vertice condiviso, come in `analysis/autocorrelazione_spaziale.py`."""
    geo = json.loads((DATI_WEB / "comuni.geojson").read_text(encoding="utf-8"))
    per_vertice: dict[tuple[float, float], set[str]] = {}
    for feature in geo["features"]:
        codice = feature["properties"]["codice_istat"]
        for anello in feature["geometry"]["coordinates"]:
            for x, y in anello:
                per_vertice.setdefault((round(x, 5), round(y, 5)), set()).add(codice)
    adiacenze: dict[str, set[str]] = {f["properties"]["codice_istat"]: set() for f in geo["features"]}
    for condivisori in per_vertice.values():
        if len(condivisori) > 1:
            for uno in condivisori:
                adiacenze[uno] |= condivisori - {uno}
    return adiacenze


def moran(valori_indicatore: dict[str, float]) -> float:
    """Indice di Moran con pesi normalizzati per riga."""
    adiacenze = contiguita()
    codici = [c for c in valori_indicatore if adiacenze.get(c)]
    if not codici:
        return 0.0
    centro = sum(valori_indicatore[c] for c in codici) / len(codici)
    z = {c: valori_indicatore[c] - centro for c in codici}
    numeratore = 0.0
    for codice in codici:
        presenti = [z[v] for v in adiacenze[codice] if v in z]
        if presenti:
            numeratore += z[codice] * (sum(presenti) / len(presenti))
    denominatore = sum(v**2 for v in z.values())
    return numeratore / denominatore if denominatore else 0.0


def confronto_province() -> dict[str, Any]:
    """Dove sta Brescia fra le 107 province, sugli stessi indicatori.

    Come la scomposizione qui sotto, non è un indicatore comunale e non passa
    dal contratto del §6.2: è una tabella a un livello diverso, e piegarla a
    fingersi un `metric_*.json` peggiorerebbe entrambe le cose.
    """
    import csv

    path = PROCESSED / "imprese_province.csv"
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as handle:
        righe = list(csv.DictReader(handle))

    nomi: dict[str, str] = {}
    valori: dict[tuple[str, str, str, str, str], float] = {}
    for riga in righe:
        if not riga["valore"]:
            continue
        nomi[riga["codice_provincia"]] = riga["provincia"]
        valori[(riga["codice_provincia"], riga["anno"], riga["dimensione"],
                riga["modalita"], riga["indicatore"])] = float(riga["valore"])

    anni = sorted({c[1] for c in valori})
    primo, ultimo = anni[0], anni[-1]

    def quota(codice: str, sopra: tuple, sotto: tuple) -> float | None:
        alto = valori.get((codice, ultimo) + sopra)
        basso = valori.get((codice, ultimo) + sotto)
        return None if not basso else alto / basso * 100

    misure: dict[str, dict[str, float]] = {}
    for codice in nomi:
        totale_ul = valori.get((codice, ultimo, "classe_addetti", "totale", "unita_locali"))
        totale_add = valori.get((codice, ultimo, "classe_addetti", "totale", "addetti"))
        iniziale_add = valori.get((codice, primo, "classe_addetti", "totale", "addetti"))
        if not (totale_ul and totale_add and iniziale_add):
            continue
        misure.setdefault("ul_micro", {})[codice] = quota(
            codice, ("classe_addetti", "0-9", "unita_locali"),
            ("classe_addetti", "totale", "unita_locali"))
        misure.setdefault("addetti_micro", {})[codice] = quota(
            codice, ("classe_addetti", "0-9", "addetti"),
            ("classe_addetti", "totale", "addetti"))
        misure.setdefault("dimensione", {})[codice] = totale_add / totale_ul
        manifattura = valori.get((codice, ultimo, "sezione", "C", "addetti"))
        if manifattura is not None:
            misure.setdefault("manifattura", {})[codice] = manifattura / totale_add * 100
        durata = int(ultimo) - int(primo)
        misure.setdefault("crescita", {})[codice] = (
            (totale_add / iniziale_add) ** (1 / durata) - 1
        ) * 100

    def rango(nome_misura: str, codice: str) -> int:
        ordinati = sorted(misure[nome_misura].items(), key=lambda kv: -kv[1])
        return [c for c, _ in ordinati].index(codice) + 1

    return {
        "primo": primo,
        "ultimo": ultimo,
        "province": len(misure["dimensione"]),
        "misure": {
            nome_misura: {
                "brescia": per_provincia["017"],
                "bergamo": per_provincia.get("016"),
                "mediana": mediana(list(per_provincia.values())),
                "rango": rango(nome_misura, "017"),
                "estremo_basso": min(per_provincia.items(), key=lambda kv: kv[1]),
                "estremo_alto": max(per_provincia.items(), key=lambda kv: kv[1]),
                # I valori di tutte le province: sono 107 numeri, e servono a
                # disegnare la distribuzione invece di riassumerla.
                "valori": {codice: round(valore, 3) for codice, valore in sorted(per_provincia.items())},
            }
            for nome_misura, per_provincia in misure.items()
            if "017" in per_provincia
        },
        "nomi": nomi,
    }


def turismo_confronto() -> dict[str, Any]:
    """Il turismo bresciano fra le 107 province, e la serie lunga dal 2008.

    Stessa forma di `confronto_province()` — un `sciame` per indicatore — più
    due cose che quella non ha: una serie storica che comincia undici anni prima
    del resto del progetto, e lo scarto fra le **due fonti** che misurano lo
    stesso turismo bresciano (MET-17).

    ⚠️ Le righe con `stato` diverso da `osservato` non entrano: sono il 2025,
    che ha una definizione nuova dentro (MET-18), e la Sardegna prima del 2017,
    che ha un confine diverso. Escluderle qui una volta sola è MET-13: se lo
    facesse ogni indicatore per conto suo, uno se ne dimenticherebbe.
    """
    import csv

    path = PROCESSED / "turismo_province.csv"
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as handle:
        righe = list(csv.DictReader(handle))

    nomi: dict[str, str] = {}
    valori_prov: dict[tuple[str, str, str, str, str], float] = {}
    for riga in righe:
        if riga["livello"] != "provincia" or riga["stato"] != "osservato" or not riga["valore"]:
            continue
        nomi[riga["codice_provincia"]] = riga["territorio"]
        valori_prov[
            (riga["codice_provincia"], riga["anno"], riga["tipologia"],
             riga["residenza"], riga["indicatore"])
        ] = float(riga["valore"])

    if "017" not in nomi:
        return {}

    # ⚠️ Gli anni si contano sulla misura che il racconto usa, non su tutte le
    # righe: il 2025 c'è ancora per alberghiero e campeggi — che la definizione
    # nuova non tocca — ma non per il totale. Prendere `max` su tutto darebbe un
    # «ultimo anno» senza il numero che serve, e il grafico verrebbe vuoto senza
    # un errore.
    anni = sorted({
        chiave[1] for chiave in valori_prov
        if chiave[2] == "totale" and chiave[3] == "totale" and chiave[4] == "presenze"
    })
    if not anni:
        return {}
    ultimo = anni[-1]
    primo = anni[0]

    popolazione: dict[str, float] = {}
    bilancio = PROCESSED / "bilancio_province.csv"
    if bilancio.exists():
        with bilancio.open(encoding="utf-8") as handle:
            for riga in csv.DictReader(handle):
                if riga["indicatore"] == "popolazione_censita" and riga["anno"] == ultimo:
                    popolazione[riga["codice_provincia"]] = float(riga["valore"])

    def p(codice: str, anno: str, tipologia: str = "totale", residenza: str = "totale",
          indicatore: str = "presenze") -> float | None:
        return valori_prov.get((codice, anno, tipologia, residenza, indicatore))

    misure: dict[str, dict[str, float]] = {}
    for codice in nomi:
        totale = p(codice, ultimo)
        if not totale:
            continue
        misure.setdefault("presenze", {})[codice] = totale
        if popolazione.get(codice):
            misure.setdefault("per_abitante", {})[codice] = totale / popolazione[codice]
        estero = p(codice, ultimo, residenza="estero")
        if estero is not None:
            misure.setdefault("estera", {})[codice] = estero / totale * 100
        campeggi = p(codice, ultimo, tipologia="campeggi e villaggi")
        if campeggi is not None:
            misure.setdefault("campeggi", {})[codice] = campeggi / totale * 100
        arrivi = p(codice, ultimo, indicatore="arrivi")
        if arrivi:
            misure.setdefault("permanenza", {})[codice] = totale / arrivi
        prima = p(codice, "2019")
        if prima:
            misure.setdefault("ripresa", {})[codice] = (totale / prima - 1) * 100

    def rango(nome_misura: str, codice: str) -> int:
        ordinati = sorted(misure[nome_misura].items(), key=lambda kv: -kv[1])
        return [c for c, _ in ordinati].index(codice) + 1

    # La serie lunga di Brescia. Le due componenti vanno tenute in **notti** e
    # non come quota: sull'asse dei conteggi una percentuale non ci sta, e
    # mettercela sarebbe due unità sullo stesso asse. Disegnate come due linee
    # che partono vicine e si separano, dicono la stessa cosa della quota — e la
    # dicono meglio, perché si vede che a crescere è una sola delle due.
    serie = [
        {
            "anno": anno,
            "presenze": p("017", anno),
            "italia": p("017", anno, residenza="Italia"),
            "estero": p("017", anno, residenza="estero"),
            "estera": (p("017", anno, residenza="estero") / p("017", anno) * 100)
            if p("017", anno) else None,
        }
        for anno in anni
        if p("017", anno)
    ]

    # Lo scarto fra le due fonti, anno per anno: è il controllo di MET-17, e va
    # mostrato invece che raccontato.
    comunale = PROCESSED / "turismo_comuni_annuale.csv"
    fonti: list[dict[str, Any]] = []
    if comunale.exists():
        somme: dict[str, float] = {}
        with comunale.open(encoding="utf-8") as handle:
            for riga in csv.DictReader(handle):
                if riga["tipo_struttura"] != "Totale" or riga["cittadinanza"] != "Totale":
                    continue
                if riga["stato"] != "osservato" or not riga["presenze"]:
                    continue
                somme[riga["anno"]] = somme.get(riga["anno"], 0.0) + float(riga["presenze"])
        for anno in sorted(somme):
            provinciale = p("017", anno)
            if provinciale:
                fonti.append({
                    "anno": anno,
                    "istat": provinciale,
                    "regione": somme[anno],
                    "scarto": (somme[anno] / provinciale - 1) * 100,
                })

    return {
        "primo": primo,
        "ultimo": ultimo,
        "province": len(misure["presenze"]),
        "misure": {
            nome_misura: {
                "brescia": per_provincia["017"],
                "mediana": mediana(list(per_provincia.values())),
                "rango": rango(nome_misura, "017"),
                "valori": {c: round(v, 3) for c, v in sorted(per_provincia.items())},
            }
            for nome_misura, per_provincia in misure.items()
            if "017" in per_provincia
        },
        "serie": serie,
        "fonti": fonti,
        "nomi": nomi,
    }


def controllo_capoluoghi() -> dict[str, Any]:
    """La classe ≥250 nei comuni capoluogo: il controllo di MET-9."""
    import csv

    path = PROCESSED / "imprese_capoluoghi.csv"
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as handle:
        righe = list(csv.DictReader(handle))

    grandi: dict[str, dict[str, float]] = {}
    nomi: dict[str, str] = {}
    for riga in righe:
        if riga["indicatore"] != "addetti" or riga["classe_addetti"] != "250+" or not riga["valore"]:
            continue
        grandi.setdefault(riga["codice_istat"], {})[riga["anno"]] = float(riga["valore"])
        nomi[riga["codice_istat"]] = riga["capoluogo"]

    variazioni = []
    for codice, serie in grandi.items():
        anni = sorted(serie)
        iniziale, finale = serie[anni[0]], serie[anni[-1]]
        if iniziale < 2000:
            continue
        variazioni.append({"nome": nomi[codice], "variazione": (finale / iniziale - 1) * 100})
    variazioni.sort(key=lambda v: v["variazione"])
    return {
        "capoluoghi": variazioni,
        "mediana": mediana([v["variazione"] for v in variazioni]),
        "in_calo": sum(1 for v in variazioni if v["variazione"] < 0),
    }


def clima() -> dict[str, Any]:
    """Aria e clima per la sesta storia: centraline, non comuni.

    È il caso più netto di indicatore che **non** entra nel contratto del §6.2,
    e per una ragione di sostanza e non di comodità: la chiave di quel contratto
    è il codice ISTAT del comune, e qui l'unità osservata è la centralina. Un
    comune ne ha sei e centonovantotto non ne hanno nessuna; spalmare la
    centralina di Sarezzo su Sarezzo produrrebbe una coropletica con due comuni
    colorati e la fallacia ecologica in omaggio. Il brief lo diceva già: l'asse 4
    non è una mappa.

    Le due decisioni di metodo sono le stesse di `analysis/aria_e_clima.py` — il
    panel bilanciato e le anomalie — e sono **ricalcolate qui**, non importate.
    È la stessa duplicazione deliberata di `analysis/verifica_cifre.py`: se le
    due implementazioni divergono, le cifre di questa pagina e quelle dei
    documenti smettono di coincidere e il verificatore lo dice. È il meccanismo
    che ha fatto emergere MET-13.
    """
    import csv
    from collections import defaultdict

    percorsi = {n: PROCESSED / f"{n}.csv" for n in ("aria_mensile", "meteo_mensile", "stazioni_arpa")}
    if not all(p.exists() for p in percorsi.values()):
        return {}

    def righe(nome: str) -> list[dict[str, str]]:
        with percorsi[nome].open(encoding="utf-8") as handle:
            return list(csv.DictReader(handle))

    stazioni = {r["id_sensore"]: r for r in righe("stazioni_arpa")}

    def annuali(tabella: str, parametro: str, colonna: str, *, somma: bool = False):
        """`id_sensore -> anno -> valore`, dai soli mesi marcati `osservato`."""
        per_anno: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
        for riga in righe(tabella):
            if riga["parametro"] != parametro or riga["stato"] != "osservato" or not riga[colonna]:
                continue
            per_anno[riga["id_sensore"]][riga["mese"][:4]].append(float(riga[colonna]))
        minimo = 12 if somma else 10
        return {
            sensore: {
                anno: (sum(mesi) if somma else sum(mesi) / len(mesi))
                for anno, mesi in per_sensore.items()
                if len(mesi) >= minimo
            }
            for sensore, per_sensore in per_anno.items()
        }

    def panel(serie: dict[str, dict[str, float]], minimo: int = 3):
        """La finestra più lunga con almeno `minimo` stazioni presenti in tutti i suoi anni."""
        anni_tutti = [a for per_sensore in serie.values() for a in per_sensore]
        if not anni_tutti:
            return [], []
        primo, ultimo = int(min(anni_tutti)), int(max(anni_tutti))
        for inizio in range(primo, ultimo + 1):
            anni = [str(a) for a in range(inizio, ultimo + 1)]
            if len(anni) < 6:
                break
            sensori = [s for s, per_s in serie.items() if all(a in per_s for a in anni)]
            if len(sensori) >= minimo:
                return anni, sensori
        return [], []

    inquinanti = []
    for parametro in ("PM10 (SM2005)", "Biossido di Azoto", "Ozono"):
        serie = annuali("aria_mensile", parametro, "media")
        anni, sensori = panel(serie)
        if not anni:
            continue
        inizio = sum(serie[s][a] for s in sensori for a in anni[:3]) / (len(sensori) * 3)
        fine = sum(serie[s][a] for s in sensori for a in anni[-3:]) / (len(sensori) * 3)
        inquinanti.append({
            "parametro": parametro,
            "unita": stazioni[sensori[0]]["unita_misura"],
            "anni": anni,
            "stazioni": [stazioni[s]["stazione"] for s in sorted(sensori)],
            "serie": [round(sum(serie[s][a] for s in sensori) / len(sensori), 2) for a in anni],
            "inizio": round(inizio, 1),
            "fine": round(fine, 1),
            "variazione": round((fine / inizio - 1) * 100, 1),
        })

    base = [str(a) for a in range(2004, 2014)]
    recente = [str(a) for a in range(2016, 2026)]

    def due_finestre(serie: dict[str, dict[str, float]]):
        """Le stazioni che hanno **entrambe** le finestre abbastanza popolate."""
        coppie = {}
        for sensore, per_sensore in serie.items():
            b = [per_sensore[a] for a in base if a in per_sensore]
            r = [per_sensore[a] for a in recente if a in per_sensore]
            if len(b) >= 8 and len(r) >= 8:
                coppie[sensore] = (sum(b) / len(b), sum(r) / len(r))
        return coppie

    temperature = annuali("meteo_mensile", "Temperatura", "valore")
    coppie_t = due_finestre(temperature)
    scarti = sorted(
        (
            {
                "stazione": stazioni[s]["stazione"],
                "quota": int(stazioni[s]["quota"]),
                "base": round(b, 2),
                "recente": round(r, 2),
                "scarto": round(r - b, 2),
            }
            for s, (b, r) in coppie_t.items()
        ),
        key=lambda v: -v["quota"],
    )

    # Le anomalie annue: ogni stazione contro la propria base, mediate. Gli anni
    # con meno di metà del panel non entrano — le anomalie tolgono la quota, non
    # la variabilità, e una stazione sola in un anno caldo scalderebbe la
    # provincia intera.
    per_anno_anom: dict[str, list[float]] = defaultdict(list)
    for sensore, (b, _) in coppie_t.items():
        for anno, valore in temperature[sensore].items():
            per_anno_anom[anno].append(valore - b)
    soglia = max(2, len(coppie_t) // 2)
    anomalie = [
        {"anno": anno, "valore": round(sum(v) / len(v), 2), "stazioni": len(v)}
        for anno, v in sorted(per_anno_anom.items())
        if len(v) >= soglia
    ]

    # Quanti comuni hanno una centralina, e quante ne ha il capoluogo. Sono
    # cifre del testo, quindi si contano qui invece di scriverle a mano — e
    # scritte a mano erano sbagliate entrambe. Il conto è su **tutta la serie**,
    # non sulle stazioni oggi attive: il `BRIEF` ne cita sette perché conta
    # quelle vive, e sono due domande diverse.
    con_centralina: dict[str, set[str]] = defaultdict(set)
    sensori_aria = {r["id_sensore"] for r in righe("aria_mensile")}
    for riga in righe("stazioni_arpa"):
        if riga["id_sensore"] in sensori_aria and riga["comune"]:
            con_centralina[riga["comune"]].add(riga["stazione"])

    coppie_p = due_finestre(annuali("meteo_mensile", "Precipitazione", "valore", somma=True))
    variazioni_pioggia = sorted((r / b - 1) * 100 for b, r in coppie_p.values())

    scarti_t = [v["scarto"] for v in scarti]
    return {
        "inquinanti": inquinanti,
        "base": [base[0], base[-1]],
        "recente": [recente[0], recente[-1]],
        "temperatura": {
            "stazioni": scarti,
            "media": round(sum(scarti_t) / len(scarti_t), 2) if scarti_t else None,
            "in_aumento": sum(1 for v in scarti_t if v > 0),
            "quota_minima": min(v["quota"] for v in scarti) if scarti else None,
            "quota_massima": max(v["quota"] for v in scarti) if scarti else None,
            "anomalie": anomalie,
        },
        "rete": {
            "comuni": len(con_centralina),
            "capoluogo": len(con_centralina.get("Brescia", ())),
        },
        "pioggia": {
            "stazioni": len(variazioni_pioggia),
            "mediana": round(mediana(variazioni_pioggia), 1) if variazioni_pioggia else None,
            "in_aumento": sum(1 for v in variazioni_pioggia if v > 0),
        },
    }


def decomposizione() -> dict[str, Any]:
    """La scomposizione settore × classe del capoluogo, per la terza storia.

    Sta qui e non nei `metric_*.json` perché non è un indicatore comunale: è una
    tabella a due territori che serve a un racconto solo. Il contratto del §6.2
    resta quello che è — un indicatore per comune — e non va piegato.
    """
    import csv

    path = PROCESSED / "imprese_settore_classe.csv"
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as handle:
        righe = list(csv.DictReader(handle))

    dentro: dict[tuple[str, str, str, str], dict[str, float]] = {}
    etichette: dict[str, str] = {}
    for riga in righe:
        if not riga["valore"]:
            continue
        chiave = (riga["territorio"], riga["ateco"], riga["classe_addetti"], riga["indicatore"])
        dentro.setdefault(chiave, {})[riga["anno"]] = float(riga["valore"])
        etichette[riga["ateco"]] = riga["settore"]

    anni = sorted({a for serie in dentro.values() for a in serie})
    primo, ultimo = anni[0], anni[-1]

    def coppia(territorio: str, ateco: str, classe: str, indicatore: str = "addetti") -> tuple[float, float]:
        serie = dentro.get((territorio, ateco, classe, indicatore), {})
        return serie.get(primo, 0.0), serie.get(ultimo, 0.0)

    divisioni = sorted({
        a for (t, a, c, i) in dentro
        if t == CAPOLUOGO and c == "250+" and i == "addetti" and a != "0010"
    })
    variazioni = []
    for ateco in divisioni:
        iniziale, finale = coppia(CAPOLUOGO, ateco, "250+")
        variazioni.append({"ateco": ateco, "nome": etichette[ateco], "iniziale": iniziale,
                           "finale": finale, "variazione": finale - iniziale})
    variazioni.sort(key=lambda v: v["variazione"])

    manifattura = [f"{n:02d}" for n in range(10, 34)]
    grande_manifattura = [0.0, 0.0]
    for ateco in manifattura:
        iniziale, finale = coppia(CAPOLUOGO, ateco, "250+")
        grande_manifattura[0] += iniziale
        grande_manifattura[1] += finale

    return {
        "anni": anni,
        "primo": primo,
        "ultimo": ultimo,
        "serie_grandi": [dentro.get((CAPOLUOGO, "0010", "250+", "addetti"), {}).get(a) for a in anni],
        "serie_totale": [dentro.get((CAPOLUOGO, "0010", "totale", "addetti"), {}).get(a) for a in anni],
        "divisioni": variazioni[:8] + variazioni[-3:],
        "totale_grandi": coppia(CAPOLUOGO, "0010", "250+"),
        "totale_tutte": coppia(CAPOLUOGO, "0010", "totale"),
        "manifattura_grandi": grande_manifattura,
        "confronto": [
            {
                "ateco": ateco,
                "nome": etichette[ateco],
                "grandi_citta": coppia(CAPOLUOGO, ateco, "250+"),
                "totale_citta": coppia(CAPOLUOGO, ateco, "totale"),
                "unita_citta": coppia(CAPOLUOGO, ateco, "totale", "unita_locali"),
                "totale_provincia": coppia("ITC47", ateco, "totale"),
            }
            for ateco in [variazioni[0]["ateco"], variazioni[1]["ateco"]]
        ],
    }


def scomposizione_demografica() -> dict[str, Any]:
    """Da dove viene la variazione di popolazione, per la prima storia.

    Come `decomposizione()` e `confronto_province()`, legge il CSV invece di
    passare dai `metric_*.json`: le componenti del bilancio sono cinque numeri
    per comune e per anno, e il contratto del §6.2 è un indicatore per comune.
    Piegarlo a contenerle peggiorerebbe entrambe le cose.

    ⚠️ L'aggiustamento statistico resta una voce **separata**: è la rettifica che
    riconcilia l'anagrafe con il censimento, non un fenomeno demografico, e
    sommarlo dentro le migrazioni farebbe dire al sito che se ne sono andate
    persone che invece non sono mai esistite in anagrafe.
    """
    import csv

    path = PROCESSED / "bilancio_demografico_comuni.csv"
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as handle:
        righe = list(csv.DictReader(handle))

    per_comune: dict[str, dict[str, float]] = {}
    anni: set[str] = set()
    for riga in righe:
        if not riga["valore"]:
            continue
        anni.add(riga["anno"])
        conti = per_comune.setdefault(riga["codice_istat"], {})
        conti[riga["indicatore"]] = conti.get(riga["indicatore"], 0.0) + float(riga["valore"])

    def componenti(conti: dict[str, float]) -> dict[str, float]:
        return {
            "naturale": conti.get("nati", 0.0) - conti.get("morti", 0.0),
            "interna": conti.get("immigrati_interni", 0.0) - conti.get("emigrati_interni", 0.0),
            "estera": conti.get("immigrati_estero", 0.0) - conti.get("emigrati_estero", 0.0),
            "territorio": conti.get("variazioni_territoriali", 0.0),
            "aggiustamento": conti.get("aggiustamento_statistico", 0.0),
        }

    comuni = {codice: componenti(conti) for codice, conti in per_comune.items()}
    # La base è la popolazione a inizio del **primo** anno: `per_comune` somma
    # `popolazione_inizio` su tutti e sei, che è un numero senza significato.
    primo_anno = min(anni)
    base: dict[str, float] = {}
    for riga in righe:
        if riga["indicatore"] == "popolazione_inizio" and riga["anno"] == primo_anno:
            base[riga["codice_istat"]] = float(riga["valore"])

    chiavi = ("naturale", "interna", "estera", "territorio", "aggiustamento")
    provincia = {chiave: sum(c[chiave] for c in comuni.values()) for chiave in chiavi}
    provincia["totale"] = sum(provincia.values())
    provincia["base"] = sum(base.values())

    # I comuni che perdono abitanti, sommati **in persone**: le quote per mille
    # di comuni diversi hanno denominatori diversi e non si sommano fra loro.
    perdenti = [c for c, v in comuni.items() if sum(v.values()) < 0]
    in_calo = {chiave: sum(comuni[c][chiave] for c in perdenti) for chiave in chiavi}
    in_calo["quanti"] = len(perdenti)

    return {
        # Lo stock di partenza è quello di fine dell'anno prima del primo
        # bilancio: i flussi del 2019 portano dalla popolazione di fine 2018.
        "primo": str(int(primo_anno) - 1),
        "ultimo": max(anni),
        "provincia": provincia,
        "in_calo": in_calo,
        "comuni": {
            codice: {
                chiave: round(valore / base[codice] * 1000, 2)
                for chiave, valore in valori_comune.items()
            }
            for codice, valori_comune in comuni.items()
            if base.get(codice)
        },
        "province": scomposizione_province(),
    }


def scomposizione_province() -> dict[str, Any]:
    """Le stesse componenti su tutte le province: il paragone che mancava.

    Sulle imprese e sui redditi il termine di paragone c'è (ed è servito: MET-14
    è nata da lì); sullo spopolamento no, ed è una storia intera di questo sito.
    """
    import csv

    path = PROCESSED / "bilancio_province.csv"
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as handle:
        righe = list(csv.DictReader(handle))

    per_provincia: dict[str, dict[str, float]] = {}
    nomi: dict[str, str] = {}
    base: dict[str, float] = {}
    primo = min(r["anno"] for r in righe)
    for riga in righe:
        if not riga["valore"]:
            continue
        nomi[riga["codice_provincia"]] = riga["provincia"]
        conti = per_provincia.setdefault(riga["codice_provincia"], {})
        conti[riga["indicatore"]] = conti.get(riga["indicatore"], 0.0) + float(riga["valore"])
        if riga["indicatore"] == "popolazione_inizio" and riga["anno"] == primo:
            base[riga["codice_provincia"]] = float(riga["valore"])

    misure: dict[str, dict[str, float]] = {}
    for codice, conti in per_provincia.items():
        if not base.get(codice):
            continue
        mille = 1000 / base[codice]
        naturale = (conti.get("nati", 0.0) - conti.get("morti", 0.0)) * mille
        interna = (conti.get("immigrati_interni", 0.0) - conti.get("emigrati_interni", 0.0)) * mille
        estera = (conti.get("immigrati_estero", 0.0) - conti.get("emigrati_estero", 0.0)) * mille
        altro = (conti.get("variazioni_territoriali", 0.0)
                 + conti.get("aggiustamento_statistico", 0.0)) * mille
        misure.setdefault("naturale", {})[codice] = naturale
        misure.setdefault("interna", {})[codice] = interna
        misure.setdefault("estera", {})[codice] = estera
        misure.setdefault("totale", {})[codice] = naturale + interna + estera + altro

    def rango(nome_misura: str) -> int:
        ordinati = sorted(misure[nome_misura].items(), key=lambda kv: -kv[1])
        return [c for c, _ in ordinati].index("017") + 1

    return {
        "province": len(misure["totale"]),
        "misure": {
            nome_misura: {
                "brescia": valori_province["017"],
                "mediana": mediana(list(valori_province.values())),
                "rango": rango(nome_misura),
                "valori": {c: round(v, 2) for c, v in sorted(valori_province.items())},
            }
            for nome_misura, valori_province in misure.items()
        },
        "in_crescita": sum(1 for v in misure["totale"].values() if v > 0),
        "naturale_positivo": sum(1 for v in misure["naturale"].values() if v > 0),
        "nomi": nomi,
    }


def casa() -> dict[str, Any]:
    """L'asse casa per l'ottava storia: il capoluogo, le sue zone, la provincia.

    Le due serie del capoluogo — €/m² e volumi di compravendita — stanno in due
    tabelle diverse e in due unità diverse, e la storia le mette una accanto
    all'altra. Il ponte è il **deflatore** (MET-20): senza, il prezzo sembra
    fermo e la frase da scrivere non esiste.

    Ricalcolata qui e non importata da `analysis/casa_e_prezzi.py`, per la
    stessa ragione di `clima()`: due implementazioni che divergono si vedono,
    una sola non si controlla.
    """
    import csv
    from collections import defaultdict

    percorsi = {
        n: PROCESSED / f"{n}.csv"
        for n in ("quotazioni_comuni", "quotazioni_zone", "compravendite_comuni", "indice_prezzi")
    }
    if not all(percorso.exists() for percorso in percorsi.values()):
        return {}

    def righe(nome: str) -> list[dict[str, str]]:
        with percorsi[nome].open(encoding="utf-8") as handle:
            return list(csv.DictReader(handle))

    indice = {r["anno"]: float(r["indice"]) for r in righe("indice_prezzi")}
    base = max(indice)

    def reale(valore: float, anno: str) -> float:
        return valore * indice[base] / indice[anno]

    # Le tre condizioni sono quelle di `analysis/casa_e_prezzi.py`: tipologia,
    # mercato e base di superficie (MET-19).
    correnti = {
        r["anno"]: float(r["media"])
        for r in righe("quotazioni_comuni")
        if r["codice_istat"] == CAPOLUOGO
        and r["tipologia"] == "Abitazioni civili"
        and r["mercato"] == "vendita"
        and r["base_superficie"] == "lorda"
        and r["media"]
    }
    volumi: dict[str, float] = defaultdict(float)
    for r in righe("compravendite_comuni"):
        if (
            r["codice_istat"] == CAPOLUOGO
            and r["comparto"] == "residenziale"
            and r["segmento"] == "totale"
            and r["ntn"]
        ):
            volumi[r["anno"]] += float(r["ntn"])

    anni = sorted(correnti)
    # Le zone del capoluogo, sul panel bilanciato: nel 2024 la zonizzazione
    # cambia, dieci zone finiscono e dieci cominciano, e la media di «quelle che
    # ci sono» misurerebbe anche il cambio di perimetro (MET-16).
    per_zona: dict[str, dict[str, float]] = defaultdict(dict)
    nomi_zona: dict[str, str] = {}
    for r in righe("quotazioni_zone"):
        if (
            r["codice_istat"] != CAPOLUOGO
            or r["tipologia"] != "Abitazioni civili"
            or r["stato_prevalente"] != "P"
            or not r["vendita_min"]
            or not r["vendita_max"]
        ):
            continue
        per_zona[r["link_zona"]][r["anno"]] = (
            float(r["vendita_min"]) + float(r["vendita_max"])
        ) / 2
        nomi_zona[r["link_zona"]] = r["zona"]
    anni_zone = sorted({a for serie in per_zona.values() for a in serie})
    panel = {k: s for k, s in per_zona.items() if len(s) == len(anni_zone)}

    def forbice(anno: str, zone: dict[str, dict[str, float]]) -> float:
        valori_anno = [s[anno] for s in zone.values() if anno in s]
        return max(valori_anno) / min(valori_anno)

    anno_ntn_primo = min(volumi)
    fondo = min(volumi, key=lambda a: volumi[a])
    return {
        "anni": anni,
        "correnti": [round(correnti[a], 1) for a in anni],
        "reali": [round(reale(correnti[a], a), 1) for a in anni],
        "anni_ntn": sorted(volumi),
        "ntn": [round(volumi[a], 1) for a in sorted(volumi)],
        # Indicizzate al primo anno in cui esistono entrambe: due unità diverse
        # su un asse solo sarebbero due scale nascoste in un grafico.
        "indice_reale": [
            round(reale(correnti[a], a) / reale(correnti[anno_ntn_primo], anno_ntn_primo) * 100, 1)
            for a in sorted(volumi)
        ],
        "indice_ntn": [round(volumi[a] / volumi[anno_ntn_primo] * 100, 1) for a in sorted(volumi)],
        "anno_base_reale": base,
        "fondo_ntn": fondo,
        "zone": {
            "anni": anni_zone,
            "quante_panel": len(panel),
            "quante_ultimo": sum(1 for s in per_zona.values() if anni_zone[-1] in s),
            "forbice_panel": [round(forbice(a, panel), 3) for a in anni_zone],
            # Tre linee e non tredici: con tredici linee etichettate in fondo il
            # grafico diventa un pettine, e la cosa da vedere — che la distanza
            # fra l'alto e il basso si accorcia — sparisce dentro il pettine.
            "alta": [round(reale(max(s[a] for s in panel.values()), a), 1) for a in anni_zone],
            "mediana": [
                round(reale(mediana(sorted(s[a] for s in panel.values())), a), 1)
                for a in anni_zone
            ],
            "bassa": [round(reale(min(s[a] for s in panel.values()), a), 1) for a in anni_zone],
            "nomi": {k: nomi_zona[k] for k in panel},
        },
    }


# --- le cifre del racconto ----------------------------------------------


def cifre(metriche: dict[str, dict[str, Any]], comuni: dict[str, dict[str, str]]) -> dict[str, str]:
    """Ogni numero che compare nel testo, ricalcolato qui.

    Aggiungere una frase con un numero significa aggiungere una voce a questo
    dizionario: è la stessa disciplina di `analysis/verifica_cifre.py`, applicata
    in avanti invece che a posteriori.
    """
    fuori: dict[str, str] = {}

    popolazione = metriche["popolazione"]
    pop_ultimo = valori(popolazione)
    pop_primo = valori(popolazione, popolazione["periods"][0])
    anno_pop_i, anno_pop_f = popolazione["periods"][0], popolazione["periods"][-1]

    fuori["comuni"] = numero_it(len(comuni))
    fuori["anno_pop_iniziale"] = anno_pop_i
    fuori["anno_pop_finale"] = anno_pop_f
    fuori["popolazione_provinciale"] = numero_it(sum(pop_ultimo.values()))
    fuori["popolazione_capoluogo"] = numero_it(pop_ultimo[CAPOLUOGO])
    fuori["quota_capoluogo"] = percento_it(pop_ultimo[CAPOLUOGO] / sum(pop_ultimo.values()) * 100)
    fuori["popolazione_mediana"] = numero_it(mediana(list(pop_ultimo.values())))

    crescita_pop = valori(metriche["crescita_popolazione"])
    in_calo = [c for c, v in crescita_pop.items() if v < 0]
    fuori["comuni_in_calo"] = numero_it(len(in_calo))
    totale_i = sum(pop_primo.values())
    totale_f = sum(pop_ultimo.values())
    durata = int(anno_pop_f) - int(anno_pop_i)
    fuori["crescita_provinciale"] = f"{numero_it(((totale_f / totale_i) ** (1 / durata) - 1) * 100, 2)} %"
    peggiori = sorted(crescita_pop.items(), key=lambda kv: kv[1])[:5]
    fuori["cadute_peggiori"] = ", ".join(comuni[c]["comune"] for c, _ in peggiori)
    fuori["caduta_peggiore_comune"] = comuni[peggiori[0][0]]["comune"]
    fuori["caduta_peggiore_tasso"] = f"{numero_it(peggiori[0][1], 1)} %"

    addetti = metriche["addetti"]
    add_i = valori(addetti, addetti["periods"][0])
    add_f = valori(addetti)
    fuori["anno_asia_iniziale"] = addetti["periods"][0]
    fuori["anno_asia_finale"] = addetti["periods"][-1]
    fuori["addetti_provinciali"] = numero_it(sum(add_f.values()))
    fuori["addetti_guadagnati"] = numero_it(sum(add_f.values()) - sum(add_i.values()))
    fuori["addetti_capoluogo_variazione"] = numero_it(add_f[CAPOLUOGO] - add_i[CAPOLUOGO])
    fuori["quota_addetti_capoluogo"] = percento_it(add_f[CAPOLUOGO] / sum(add_f.values()) * 100)

    micro = valori(metriche["quota_micro"])
    fuori["quota_micro_mediana"] = percento_it(mediana(list(micro.values())))
    fuori["quota_micro_provinciale"] = percento_it(
        sum(add_f[c] * micro[c] / 100 for c in micro) / sum(add_f[c] for c in micro) * 100
    )

    reddito = metriche["reddito_medio"]
    red_i = valori(reddito, reddito["periods"][0])
    red_f = valori(reddito)
    fuori["anno_reddito_iniziale"] = reddito["periods"][0]
    fuori["anno_reddito_finale"] = reddito["periods"][-1]
    fuori["reddito_mediano"] = numero_it(mediana(list(red_f.values())))
    fuori["reddito_minimo"] = numero_it(min(red_f.values()))
    fuori["reddito_massimo"] = numero_it(max(red_f.values()))
    fuori["reddito_rapporto"] = numero_it(max(red_f.values()) / min(red_f.values()), 1)
    fuori["reddito_rapporto_iniziale"] = numero_it(max(red_i.values()) / min(red_i.values()), 1)

    def decili(valori: dict[str, float]) -> float:
        """p90/p10: la stessa domanda del rapporto fra gli estremi, ma senza
        farla decidere a due comuni su duecento."""
        ordinati = sorted(valori.values())
        return ordinati[int(len(ordinati) * 0.9)] / ordinati[int(len(ordinati) * 0.1)]

    fuori["reddito_decili"] = numero_it(decili(red_f), 2)
    fuori["reddito_decili_iniziale"] = numero_it(decili(red_i), 2)
    estremo_alto = max(red_f, key=lambda c: red_f[c])
    estremo_basso = min(red_f, key=lambda c: red_f[c])
    fuori["reddito_massimo_comune"] = comuni[estremo_alto]["comune"]
    fuori["reddito_minimo_comune"] = comuni[estremo_basso]["comune"]

    crescita_red = valori(metriche["crescita_reddito"])
    comuni_comuni = [c for c in crescita_red if c in red_i]
    fuori["convergenza_pearson"] = numero_it(
        pearson([red_i[c] for c in comuni_comuni], [crescita_red[c] for c in comuni_comuni]), 2
    )
    fuori["artefatto_pearson"] = numero_it(
        pearson([red_f[c] for c in comuni_comuni], [crescita_red[c] for c in comuni_comuni]), 2
    )
    fuori["crescita_reddito_mediana"] = f"{numero_it(mediana(list(crescita_red.values())), 2)} %"

    intensita = valori(metriche["addetti_per_100_abitanti"])
    ordinata = sorted(intensita.items(), key=lambda kv: kv[1], reverse=True)
    fuori["intensita_massima_comune"] = comuni[ordinata[0][0]]["comune"]
    fuori["intensita_massima"] = numero_it(ordinata[0][1], 1)
    fuori["intensita_seconda_comune"] = comuni[ordinata[1][0]]["comune"]
    fuori["intensita_seconda"] = numero_it(ordinata[1][1], 1)
    fuori["intensita_mediana"] = numero_it(mediana(list(intensita.values())), 1)

    demografia = scomposizione_demografica()
    if demografia:
        provinciale = demografia["provincia"]
        fuori["saldo_naturale_provinciale"] = numero_it(-provinciale["naturale"])
        fuori["migrazione_interna_provinciale"] = numero_it(provinciale["interna"])
        fuori["migrazione_estera_provinciale"] = numero_it(provinciale["estera"])
        fuori["aggiustamento_provinciale"] = numero_it(-provinciale["aggiustamento"])
        fuori["crescita_provinciale_assoluta"] = numero_it(provinciale["totale"])
        # Senza la migrazione estera la provincia perderebbe abitanti: è il modo
        # più diretto di dire da dove viene la crescita, e va detto con il
        # controfattuale esplicito, non lasciato dedurre dalle barre.
        fuori["perdita_senza_estero"] = numero_it(
            provinciale["estera"] - provinciale["totale"]
        )

        per_comune = demografia["comuni"]
        in_calo = {
            codice: valori_comune
            for codice, valori_comune in per_comune.items()
            if sum(valori_comune.values()) < 0
        }
        # La componente che **tira più giù**, non la più grande in valore
        # assoluto: in un comune che perde abitanti con la migrazione estera a
        # +59 ‰ la componente più grande è quella estera, e non è la ragione per
        # cui il comune si svuota.
        def piu_negativa(valori_comune: dict[str, float]) -> str:
            return min(("naturale", "interna", "estera"), key=lambda k: valori_comune[k])

        conteggio = {
            nome: sum(1 for v in in_calo.values() if piu_negativa(v) == nome)
            for nome in ("naturale", "interna", "estera")
        }
        fuori["comuni_calo_per_naturale"] = numero_it(conteggio["naturale"])
        fuori["comuni_calo_per_interna"] = numero_it(conteggio["interna"])
        fuori["comuni_saldo_naturale_negativo"] = numero_it(
            sum(1 for v in per_comune.values() if v["naturale"] < 0)
        )
        calanti = demografia["in_calo"]
        fuori["comuni_in_calo_naturale"] = numero_it(-calanti["naturale"])
        fuori["comuni_in_calo_interna"] = numero_it(-calanti["interna"])
        fuori["comuni_in_calo_estera"] = numero_it(calanti["estera"])

        confronto_prov = demografia["province"]
        if confronto_prov:
            misure = confronto_prov["misure"]
            fuori["province_confrontate"] = numero_it(confronto_prov["province"])
            fuori["province_in_crescita"] = numero_it(confronto_prov["in_crescita"])
            fuori["province_naturale_positivo"] = numero_it(confronto_prov["naturale_positivo"])
            fuori["rango_crescita_provincia"] = numero_it(misure["totale"]["rango"])
            fuori["rango_naturale_provincia"] = numero_it(misure["naturale"]["rango"])
            fuori["crescita_provinciale_mille"] = numero_it(misure["totale"]["brescia"], 1)
            fuori["mediana_province_mille"] = numero_it(-misure["totale"]["mediana"], 1)
            fuori["naturale_provinciale_mille"] = numero_it(-misure["naturale"]["brescia"], 1)
            fuori["mediana_naturale_mille"] = numero_it(-misure["naturale"]["mediana"], 1)

    scomposizione = decomposizione()
    if scomposizione:
        fuori["anno_asia_i"] = scomposizione["primo"]
        fuori["anno_asia_f"] = scomposizione["ultimo"]
        grandi = scomposizione["totale_grandi"]
        tutte = scomposizione["totale_tutte"]
        fuori["grandi_iniziale"] = numero_it(grandi[0])
        fuori["grandi_finale"] = numero_it(grandi[1])
        fuori["grandi_variazione"] = numero_it(grandi[1] - grandi[0])
        fuori["citta_variazione"] = numero_it(tutte[1] - tutte[0])
        prime = scomposizione["divisioni"][:2]
        fuori["divisione_prima"] = prime[0]["nome"]
        fuori["divisione_prima_variazione"] = numero_it(prime[0]["variazione"])
        fuori["divisione_seconda"] = prime[1]["nome"]
        fuori["divisione_seconda_variazione"] = numero_it(prime[1]["variazione"])
        fuori["due_divisioni_variazione"] = numero_it(prime[0]["variazione"] + prime[1]["variazione"])
        manifattura_grandi = scomposizione["manifattura_grandi"]
        fuori["manifattura_grandi_iniziale"] = numero_it(manifattura_grandi[0])
        fuori["manifattura_grandi_variazione"] = numero_it(manifattura_grandi[1] - manifattura_grandi[0])
        for indice, confronto in enumerate(scomposizione["confronto"], start=1):
            fuori[f"conf{indice}_nome"] = confronto["nome"]
            fuori[f"conf{indice}_grandi"] = numero_it(confronto["grandi_citta"][1] - confronto["grandi_citta"][0])
            fuori[f"conf{indice}_citta"] = numero_it(confronto["totale_citta"][1] - confronto["totale_citta"][0])
            fuori[f"conf{indice}_unita"] = numero_it(confronto["unita_citta"][1] - confronto["unita_citta"][0])
            fuori[f"conf{indice}_provincia"] = numero_it(confronto["totale_provincia"][1] - confronto["totale_provincia"][0])
            fuori[f"conf{indice}_provincia_quota"] = percento_it(
                (confronto["totale_provincia"][1] / confronto["totale_provincia"][0] - 1) * 100
                if confronto["totale_provincia"][0] else 0.0
            )

    # La convergenza dei redditi nella provincia di confronto: serve a dire se
    # il risultato più netto delle analisi sia bresciano (MET-14).
    percorso_confronto = PROCESSED / "redditi_comuni_confronto.csv"
    if percorso_confronto.exists():
        import csv as _csv

        imponibile_bg: dict[str, dict[str, float]] = {}
        contribuenti_bg: dict[str, dict[str, float]] = {}
        with percorso_confronto.open(encoding="utf-8") as handle:
            for riga in _csv.DictReader(handle):
                if not riga["valore"]:
                    continue
                deposito = imponibile_bg if riga["codice_indicatore"] == "AGGINCR" else contribuenti_bg
                anni = deposito.setdefault(riga["codice_istat"], {})
                anni[riga["anno"]] = anni.get(riga["anno"], 0.0) + float(riga["valore"])
        medi: dict[str, dict[str, float]] = {}
        for codice, per_anno in imponibile_bg.items():
            for anno, totale in per_anno.items():
                teste = contribuenti_bg.get(codice, {}).get(anno)
                if teste:
                    medi.setdefault(codice, {})[anno] = totale / teste
        anni_bg = sorted({a for v in medi.values() for a in v})
        primo_bg, ultimo_bg = anni_bg[0], anni_bg[-1]
        codici_bg = [c for c in medi if primo_bg in medi[c] and ultimo_bg in medi[c]]
        durata_bg = int(ultimo_bg) - int(primo_bg)
        fuori["convergenza_bergamo"] = numero_it(
            pearson(
                [medi[c][primo_bg] for c in codici_bg],
                [((medi[c][ultimo_bg] / medi[c][primo_bg]) ** (1 / durata_bg) - 1) * 100
                 for c in codici_bg],
            ),
            2,
        )
        fuori["comuni_bergamo"] = numero_it(len(codici_bg))

    confronto = confronto_province()
    if confronto:
        fuori["province_italiane"] = numero_it(confronto["province"])
        etichette = {
            "ul_micro": "ul_micro",
            "addetti_micro": "addetti_micro",
            "dimensione": "dimensione",
            "manifattura": "manifattura_confronto",
            "crescita": "crescita_confronto",
        }
        decimali = {"dimensione": 2}
        for chiave, prefisso in etichette.items():
            misura = confronto["misure"][chiave]
            quanti = decimali.get(chiave, 1)
            fuori[f"{prefisso}_brescia"] = numero_it(misura["brescia"], quanti)
            fuori[f"{prefisso}_mediana"] = numero_it(misura["mediana"], quanti)
            fuori[f"{prefisso}_rango"] = numero_it(misura["rango"])
            if misura["bergamo"] is not None:
                fuori[f"{prefisso}_bergamo"] = numero_it(misura["bergamo"], quanti)
            fuori[f"{prefisso}_max_nome"] = confronto["nomi"][misura["estremo_alto"][0]]
            fuori[f"{prefisso}_max"] = numero_it(misura["estremo_alto"][1], quanti)
            fuori[f"{prefisso}_min_nome"] = confronto["nomi"][misura["estremo_basso"][0]]
            fuori[f"{prefisso}_min"] = numero_it(misura["estremo_basso"][1], quanti)

    controllo = controllo_capoluoghi()
    if controllo:
        fuori["capoluoghi_confrontati"] = numero_it(len(controllo["capoluoghi"]))
        fuori["capoluoghi_in_calo"] = numero_it(controllo["in_calo"])
        fuori["capoluoghi_mediana"] = f"{numero_it(controllo['mediana'], 1)} %"
        posizione = [v["nome"] for v in controllo["capoluoghi"]].index("Brescia") + 1
        fuori["capoluoghi_rango_brescia"] = numero_it(posizione)
        fuori["capoluoghi_peggiori"] = ", ".join(
            f"{v['nome']} ({numero_it(v['variazione'], 0)} %)" for v in controllo["capoluoghi"][:4]
        )

    fuori["moran_crescita_popolazione"] = numero_it(moran(crescita_pop), 2)
    fuori["moran_reddito"] = numero_it(moran(red_f), 2)

    if "quota_manifattura" in metriche:
        manifattura = valori(metriche["quota_manifattura"])
        alloggio = valori(metriche["quota_alloggio_ristorazione"])
        fuori["manifattura_mediana"] = percento_it(mediana(list(manifattura.values())))
        fuori["manifattura_capoluogo"] = percento_it(manifattura[CAPOLUOGO])
        sopra = [c for c, v in manifattura.items() if v >= 50]
        fuori["comuni_manifatturieri"] = numero_it(len(sopra))
        turistici = [c for c, v in alloggio.items() if v >= 25]
        fuori["comuni_turistici"] = numero_it(len(turistici))
        top_alloggio = sorted(alloggio.items(), key=lambda kv: kv[1], reverse=True)[:5]
        fuori["comuni_turistici_top"] = ", ".join(comuni[c]["comune"] for c, _ in top_alloggio)
        top_manifattura = sorted(manifattura.items(), key=lambda kv: kv[1], reverse=True)[:5]
        fuori["comuni_manifatturieri_top"] = ", ".join(comuni[c]["comune"] for c, _ in top_manifattura)
        comuni_entrambi = [c for c in manifattura if c in alloggio]
        fuori["manifattura_alloggio_pearson"] = numero_it(
            pearson([manifattura[c] for c in comuni_entrambi], [alloggio[c] for c in comuni_entrambi]), 2
        )
        addetti_sezioni = {c: 0.0 for c in manifattura}
        fuori["manifattura_provinciale"] = percento_it(
            sum(manifattura[c] * add_f[c] for c in manifattura if c in add_f)
            / sum(add_f[c] for c in manifattura if c in add_f)
        )
        fuori["alloggio_provinciale"] = percento_it(
            sum(alloggio[c] * add_f[c] for c in alloggio if c in add_f)
            / sum(add_f[c] for c in alloggio if c in add_f)
        )
        del addetti_sezioni
        specializzazione = valori(metriche["specializzazione"])
        fuori["moran_specializzazione"] = numero_it(moran(specializzazione), 2)

    aria = clima()
    if aria:
        per_parametro = {i["parametro"]: i for i in aria["inquinanti"]}
        etichette = {
            "PM10 (SM2005)": "pm10",
            "Biossido di Azoto": "no2",
            "Ozono": "ozono",
        }
        for parametro, breve in etichette.items():
            misura = per_parametro.get(parametro)
            if not misura:
                continue
            fuori[f"{breve}_anno_i"] = misura["anni"][0]
            fuori[f"{breve}_anno_f"] = misura["anni"][-1]
            fuori[f"{breve}_stazioni"] = numero_it(len(misura["stazioni"]))
            fuori[f"{breve}_inizio"] = numero_it(misura["inizio"], 1)
            fuori[f"{breve}_fine"] = numero_it(misura["fine"], 1)
            # Il verbo lo decide il segno, non chi scrive la frase: sull'ozono
            # «−1,8 %» va detto come «non si muove», e se un domani si muovesse
            # il testo non deve continuare a dire di no.
            fuori[f"{breve}_variazione"] = f"{numero_it(misura['variazione'], 1)} %"
            fuori[f"{breve}_variazione_assoluta"] = f"{numero_it(abs(misura['variazione']), 1)} %"

        temperatura = aria["temperatura"]
        fuori["clima_base_i"], fuori["clima_base_f"] = aria["base"]
        fuori["clima_recente_i"], fuori["clima_recente_f"] = aria["recente"]
        fuori["temp_scarto"] = f"{numero_it(temperatura['media'], 2)} °C"
        fuori["temp_stazioni"] = numero_it(len(temperatura["stazioni"]))
        fuori["temp_in_aumento"] = numero_it(temperatura["in_aumento"])
        fuori["temp_quota_minima"] = numero_it(temperatura["quota_minima"])
        fuori["temp_quota_massima"] = numero_it(temperatura["quota_massima"])
        calde = sorted(temperatura["anomalie"], key=lambda v: -v["valore"])[:3]
        fuori["temp_anni_caldi"] = ", ".join(sorted(v["anno"] for v in calde))
        fuori["temp_anomalia_massima"] = f"{numero_it(calde[0]['valore'], 2)} °C"

        fuori["aria_comuni"] = numero_it(aria["rete"]["comuni"])
        fuori["aria_comuni_senza"] = numero_it(len(comuni) - aria["rete"]["comuni"])
        fuori["aria_stazioni_capoluogo"] = numero_it(aria["rete"]["capoluogo"])
        fuori["pioggia_stazioni"] = numero_it(aria["pioggia"]["stazioni"])
        fuori["pioggia_in_aumento"] = numero_it(aria["pioggia"]["in_aumento"])
        fuori["pioggia_in_calo"] = numero_it(
            aria["pioggia"]["stazioni"] - aria["pioggia"]["in_aumento"]
        )
        fuori["pioggia_mediana"] = f"{numero_it(aria['pioggia']['mediana'], 1)} %"

    # --- settima storia: il turismo fra le province ----------------------
    turismo = turismo_confronto()
    if turismo and turismo.get("misure"):
        misure_tur = turismo["misure"]
        fuori["tur_anno"] = turismo["ultimo"]
        fuori["tur_anno_primo"] = turismo["primo"]
        fuori["tur_province"] = numero_it(turismo["province"])

        def _tur(nome_misura: str, decimali: int, suffisso: str = "") -> None:
            misura = misure_tur.get(nome_misura)
            if not misura:
                return
            fuori[f"tur_{nome_misura}"] = numero_it(misura["brescia"], decimali) + suffisso
            fuori[f"tur_{nome_misura}_mediana"] = numero_it(misura["mediana"], decimali) + suffisso
            fuori[f"tur_{nome_misura}_rango"] = numero_it(misura["rango"])

        _tur("presenze", 0)
        _tur("per_abitante", 1)
        _tur("estera", 1, " %")
        _tur("campeggi", 1, " %")
        _tur("permanenza", 2)
        _tur("ripresa", 1, " %")

        # Le province davanti a Brescia per presenze: sono la frase «decima
        # dietro a queste», e vanno prese dai dati e non da una lista scritta.
        presenze = misure_tur["presenze"]["valori"]
        davanti = sorted(presenze, key=lambda c: -presenze[c])[: misure_tur["presenze"]["rango"] - 1]
        fuori["tur_davanti"] = ", ".join(turismo["nomi"][c] for c in davanti)
        fuori["tur_quante_davanti"] = numero_it(len(davanti))
        fuori["tur_volte_mediana"] = numero_it(
            misure_tur["presenze"]["brescia"] / misure_tur["presenze"]["mediana"], 1
        )

        estera = misure_tur["estera"]["valori"]
        sopra = sorted(
            (c for c in estera if estera[c] > estera["017"]), key=lambda c: -estera[c]
        )
        fuori["tur_estera_davanti"] = ", ".join(turismo["nomi"][c] for c in sopra)
        fuori["tur_estera_quante_davanti"] = numero_it(len(sopra))

        campeggi = misure_tur["campeggi"]["valori"]
        fuori["tur_campeggi_volte"] = numero_it(campeggi["017"] / misure_tur["campeggi"]["mediana"], 1)

        serie = {v["anno"]: v for v in turismo["serie"]}
        primo_anno, ultimo_anno = turismo["primo"], turismo["ultimo"]
        if primo_anno in serie and ultimo_anno in serie:
            iniziale, finale = serie[primo_anno]["presenze"], serie[ultimo_anno]["presenze"]
            durata_tur = int(ultimo_anno) - int(primo_anno)
            fuori["tur_crescita"] = (
                f"{numero_it(((finale / iniziale) ** (1 / durata_tur) - 1) * 100, 2)} %"
            )
            fuori["tur_presenze_primo"] = numero_it(iniziale)
            fuori["tur_estera_primo"] = percento_it(serie[primo_anno]["estera"])
            # Le due componenti separate: e' il numero che rende la frase
            # «l'internazionalizzazione e' la crescita» una misura invece che
            # un'impressione. Le notti italiane sono ferme, le estere no.
            for chiave in ("italia", "estero"):
                partenza, arrivo = serie[primo_anno][chiave], serie[ultimo_anno][chiave]
                fuori[f"tur_{chiave}_primo"] = numero_it(partenza)
                fuori[f"tur_{chiave}_finale"] = numero_it(arrivo)
                # Il segno esplicito: «2,3 %» accanto a «62,1 %» si legge come
                # due crescite simili, «+2,3 %» accanto a «+62,1 %» no.
                variazione = (arrivo / partenza - 1) * 100
                fuori[f"tur_{chiave}_variazione"] = (
                    f"{'+' if variazione > 0 else ''}{numero_it(variazione, 1)} %"
                )
        if "2020" in serie and "2019" in serie:
            fuori["tur_caduta_2020"] = (
                f"{numero_it((serie['2020']['presenze'] / serie['2019']['presenze'] - 1) * 100, 1)} %"
            )

        ripresa = misure_tur["ripresa"]["valori"]
        fuori["tur_sotto_il_2019"] = numero_it(sum(1 for v in ripresa.values() if v <= 0))

        if turismo["fonti"]:
            prima_fonte, ultima_fonte = turismo["fonti"][0], turismo["fonti"][-1]
            fuori["tur_fonti_anno_i"] = prima_fonte["anno"]
            fuori["tur_fonti_anno_f"] = ultima_fonte["anno"]
            fuori["tur_fonti_scarto_i"] = percento_it(prima_fonte["scarto"])
            fuori["tur_fonti_scarto_f"] = percento_it(ultima_fonte["scarto"])
            fuori["tur_fonti_istat"] = numero_it(ultima_fonte["istat"])
            fuori["tur_fonti_regione"] = numero_it(ultima_fonte["regione"])

    # --- l'ottava storia: la casa ---------------------------------------
    dati_casa = casa()
    if dati_casa:
        anni, correnti, reali = dati_casa["anni"], dati_casa["correnti"], dati_casa["reali"]
        fuori["casa_anno_primo"] = anni[0]
        fuori["casa_anno_ultimo"] = anni[-1]
        fuori["casa_anni"] = numero_it(int(anni[-1]) - int(anni[0]))
        fuori["casa_prezzo_primo"] = numero_it(correnti[0])
        fuori["casa_prezzo_ultimo"] = numero_it(correnti[-1])
        fuori["casa_prezzo_primo_reale"] = numero_it(reali[0])
        nominale = (correnti[-1] / correnti[0] - 1) * 100
        fuori["casa_nominale"] = f"{'+' if nominale > 0 else ''}{numero_it(nominale, 1)} %"
        fuori["casa_reale"] = percento_it((reali[-1] / reali[0] - 1) * 100)
        fuori["casa_inflazione"] = f"+{numero_it((reali[0] / correnti[0] - 1) * 100, 1)} %"

        volumi = dict(zip(dati_casa["anni_ntn"], dati_casa["ntn"]))
        fondo = dati_casa["fondo_ntn"]
        fuori["casa_ntn_fondo_anno"] = fondo
        fuori["casa_ntn_fondo"] = numero_it(volumi[fondo])
        fuori["casa_ntn_ultimo"] = numero_it(volumi[dati_casa["anni_ntn"][-1]])
        variazione_ntn = (volumi[dati_casa["anni_ntn"][-1]] / volumi[fondo] - 1) * 100
        fuori["casa_ntn_variazione"] = f"+{numero_it(variazione_ntn, 1)} %"
        fuori["casa_ntn_anno_primo"] = dati_casa["anni_ntn"][0]

        zone = dati_casa["zone"]
        fuori["casa_zone_panel"] = numero_it(zone["quante_panel"])
        fuori["casa_zone_ultimo"] = numero_it(zone["quante_ultimo"])
        fuori["casa_forbice_primo"] = numero_it(zone["forbice_panel"][0], 2)
        fuori["casa_forbice_ultimo"] = numero_it(zone["forbice_panel"][-1], 2)
        fuori["casa_zone_anno_rifatta"] = str(int(zone["anni"][-1]) - 1)
        # Le **annate**, non gli anni trascorsi: la serie OMI è un semestre per
        # anno, e ventidue annate coprono ventun anni di distanza.
        fuori["casa_zone_annate"] = numero_it(len(zone["anni"]))

    prezzi_comuni = valori(metriche["prezzo_case"])
    fuori["casa_comuni_quotati"] = numero_it(len(prezzi_comuni))
    fuori["casa_comuni_assenti"] = numero_it(len(comuni) - len(prezzi_comuni))
    ordinati_prezzo = sorted(prezzi_comuni.items(), key=lambda kv: -kv[1])
    fuori["casa_comune_caro"] = comuni[ordinati_prezzo[0][0]]["comune"]
    fuori["casa_prezzo_caro"] = numero_it(ordinati_prezzo[0][1])
    fuori["casa_comune_economico"] = comuni[ordinati_prezzo[-1][0]]["comune"]
    fuori["casa_prezzo_economico"] = numero_it(ordinati_prezzo[-1][1])
    fuori["casa_rapporto_estremi"] = numero_it(ordinati_prezzo[0][1] / ordinati_prezzo[-1][1], 1)
    fuori["casa_prezzo_capoluogo"] = numero_it(prezzi_comuni[CAPOLUOGO])
    fuori["casa_rango_capoluogo"] = numero_it(
        [c for c, _ in ordinati_prezzo].index(CAPOLUOGO) + 1
    )
    fuori["casa_prezzo_mediano"] = numero_it(mediana(list(prezzi_comuni.values())))

    variazione_reale = valori(metriche["variazione_prezzo_reale"])
    fuori["casa_comuni_variazione"] = numero_it(len(variazione_reale))
    fuori["casa_comuni_in_calo"] = numero_it(sum(1 for v in variazione_reale.values() if v < 0))
    fuori["casa_variazione_mediana"] = percento_it(mediana(list(variazione_reale.values())), 2)
    su = sorted(variazione_reale.items(), key=lambda kv: -kv[1])[:3]
    fuori["casa_comuni_in_crescita"] = ", ".join(comuni[c]["comune"] for c, _ in su)

    reddito_comuni = valori(metriche["reddito_medio"])
    condivisi = sorted(set(prezzi_comuni) & set(reddito_comuni))
    fuori["casa_correlazione_reddito"] = numero_it(
        pearson([prezzi_comuni[c] for c in condivisi], [reddito_comuni[c] for c in condivisi]), 2
    )

    return fuori


# --- assemblaggio --------------------------------------------------------


def geometria_compatta(precisione: int = 4) -> dict[str, Any]:
    """Il GeoJSON con le sole proprietà che servono e le coordinate arrotondate.

    Quattro decimali sono circa undici metri: su una provincia di 4.785 km²
    disegnata larga mille pixel, invisibili. Tolgono un quinto del peso.
    """
    geo = json.loads((DATI_WEB / "comuni.geojson").read_text(encoding="utf-8"))
    features = []
    for feature in geo["features"]:
        anelli = [
            [[round(x, precisione), round(y, precisione)] for x, y in anello]
            for anello in feature["geometry"]["coordinates"]
        ]
        features.append(
            {
                "c": feature["properties"]["codice_istat"],
                "g": anelli,
            }
        )
    return {"comuni": features}


def dati_incorporati(metriche: dict[str, dict[str, Any]], comuni: dict[str, dict[str, str]]) -> dict[str, Any]:
    return {
        "comuni": {
            codice: [riga["comune"], int(riga["capoluogo"])] for codice, riga in sorted(comuni.items())
        },
        "geo": geometria_compatta(),
        "decomposizione": decomposizione(),
        "demografia": scomposizione_demografica(),
        "confronto": confronto_province(),
        "turismo": turismo_confronto(),
        "clima": clima(),
        "capoluoghi": controllo_capoluoghi(),
        "casa": casa(),
        "metriche": {
            id_metrica: {
                "label": metrica["label"],
                "unit": metrica["unit"],
                "kind": metrica["kind"],
                "source": metrica["source"],
                "confidence": metrica["confidence"],
                "assumptions": metrica["assumptions"],
                "periods": metrica["periods"],
                "values": metrica["values"],
                "coverage": metrica["coverage"],
            }
            for id_metrica, metrica in metriche.items()
        },
    }


def sostituisci(testo: str, valori_cifre: dict[str, str], comuni_pagina: str) -> str:
    mancanti: list[str] = []

    def rimpiazza(match: re.Match[str]) -> str:
        nome = match.group(1)
        if nome not in valori_cifre:
            mancanti.append(nome)
            return match.group(0)
        return valori_cifre[nome]

    risultato = re.sub(r"\{\{c:([a-z0-9_]+)\}\}", rimpiazza, testo)
    if mancanti:
        raise SystemExit(
            f"{comuni_pagina}: segnaposto senza valore: {', '.join(sorted(set(mancanti)))}.\n"
            "Ogni cifra del racconto deve essere calcolata in costruisci.py, non scritta a mano."
        )
    return risultato


def data_dei_dati() -> str:
    """Quando le tabelle sono cambiate l'ultima volta.

    L'ultimo commit che ha toccato `dati/processed/`; fuori da un repository
    (un tarball, uno zip scaricato) si ripiega sulla data di modifica del file
    più recente, che è la migliore approssimazione disponibile.
    """
    try:
        uscita = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", "dati/processed"],
            cwd=RADICE, capture_output=True, text=True, timeout=10, check=True,
        )
        if uscita.stdout.strip():
            return uscita.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pass
    piu_recente = max(p.stat().st_mtime for p in PROCESSED.glob("*.csv"))
    return datetime.fromtimestamp(piu_recente, timezone.utc).date().isoformat()


def costruisci(uscita: Path, data_build: str | None) -> int:
    if not (DATI_WEB / "metrics.json").exists():
        print("manca web/src/data/: lanciare `python -m brescia_pipeline.build web`", file=sys.stderr)
        return 1

    import csv

    with (PROCESSED / "comuni.csv").open(encoding="utf-8") as handle:
        comuni = {r["codice_istat"]: r for r in csv.DictReader(handle)}

    metriche = {}
    for id_metrica in METRICHE_USATE:
        metrica = leggi_metrica(id_metrica)
        if metrica is not None:
            metriche[id_metrica] = metrica
    mancanti = [m for m in METRICHE_USATE if m not in metriche]
    if mancanti:
        print(f"  indicatori non ancora costruiti, il sito li salta: {', '.join(mancanti)}")

    manifesto = json.loads((DATI_WEB / "manifest.json").read_text(encoding="utf-8"))
    valori_cifre = cifre(metriche, comuni)

    stile = (MODELLI / "stile.css").read_text(encoding="utf-8")
    grafici = (MODELLI / "grafici.js").read_text(encoding="utf-8")
    dati = json.dumps(dati_incorporati(metriche, comuni), ensure_ascii=False, separators=(",", ":"))

    uscita.mkdir(parents=True, exist_ok=True)
    for modello, destinazione in PAGINE.items():
        sorgente = (MODELLI / modello).read_text(encoding="utf-8")
        pagina = sostituisci(sorgente, valori_cifre, modello)
        pagina = (
            pagina.replace("/*{{STILE}}*/", stile)
            .replace("/*{{GRAFICI}}*/", grafici)
            .replace("/*{{DATI}}*/", f"window.DATI={dati};")
            .replace("{{BUILD_DATE}}", data_build or date.today().isoformat())
            .replace("{{DATA_DATE}}", data_dei_dati())
            .replace("{{N_INDICATORI}}", str(manifesto["indicatori"]))
            .replace("{{N_TABELLE}}", str(len(manifesto["tabelle"])))
        )
        (uscita / destinazione).write_text(pagina, encoding="utf-8")
        peso = (uscita / destinazione).stat().st_size / 1024
        print(f"  {destinazione:20} {peso:8.0f} KB")

    tabelle = uscita / "dati" / "processed"
    tabelle.mkdir(parents=True, exist_ok=True)
    for csv_path in sorted(PROCESSED.glob("*.csv")):
        shutil.copyfile(csv_path, tabelle / csv_path.name)
    geo_uscita = uscita / "dati" / "geo"
    geo_uscita.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(RADICE / "dati" / "geo" / "comuni_brescia.geojson", geo_uscita / "comuni_brescia.geojson")
    print(f"  {len(list(tabelle.glob('*.csv')))} tabelle CSV copiate in {tabelle.relative_to(uscita)}/")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="costruisci")
    parser.add_argument("--uscita", type=Path, default=RADICE / "_site")
    parser.add_argument("--data-build", help="data da stampare nel sito (default: oggi)")
    args = parser.parse_args(argv)
    return costruisci(args.uscita, args.data_build)


if __name__ == "__main__":
    sys.exit(main())
