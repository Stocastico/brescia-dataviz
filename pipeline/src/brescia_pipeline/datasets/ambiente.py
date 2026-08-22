"""Qualità dell'aria e clima dalle reti ARPA Lombardia.

Le serie orarie grezze sono enormi (decine di milioni di righe per finestra
storica), quindi non si scaricano: si chiede a Socrata di aggregarle
server-side per sensore e mese. Restano valori mensili — la granularità giusta
per raccontare trent'anni, e l'unica sostenibile da versionare.

## L'aggregazione non è sempre una media

È la trappola di questo modulo, ed è silenziosa. Una temperatura mensile è la
**media** delle rilevazioni; una precipitazione mensile è il loro **totale** —
i pluviometri registrano i millimetri caduti in ogni intervallo, e la loro media
è un numero plausibile che non significa niente («in gennaio è caduta una media
di 0,04 mm»). Per questo `SERIE_METEO` dichiara l'aggregazione accanto a ogni
parametro invece di lasciarla implicita, e la tabella prodotta porta una colonna
`aggregazione`: un valore che si legge senza sapere come è stato prodotto è un
valore che prima o poi viene sommato a quello sbagliato.

## Il clima non è tutto qui, e la tabella lo dice

L'anagrafica meteo di ARPA porta otto parametri — temperatura, precipitazione,
umidità, vento (velocità e direzione), radiazione, livello idrometrico, neve —
ma le serie storiche stanno in **un dataset per parametro**, non in uno solo.
Qui ne sono coperti due; per gli altri sei i sensori esistono in
`stazioni_arpa.csv` e le misure no.

Non è un difetto da nascondere: `build` **stampa** quali parametri restano
scoperti, invece di lasciare che l'assenza si deduca da una tabella che
semplicemente non li contiene. Aggiungerne uno costa tre righe in
`SERIE_METEO`, e i dataset si trovano cercando il nome del parametro nel
catalogo di `dati.lombardia.it` («Velocità del vento dal 2021» e simili).
"""

from __future__ import annotations

from ..config import SIGLA_PROVINCIA
from ..fetch import socrata_json
from ..tidy import fmt, read_socrata, to_number, write_csv

ANAGRAFICA_ARIA = "ib47-atvt"
ANAGRAFICA_METEO = "nf78-nj6b"

# Le misure sono spezzate per finestra temporale: ogni dataset e' un pezzo
# della stessa serie.
SERIE_ARIA = {
    "2000-2009": "cthp-zqrr",
    "2010-2017": "nr8w-tj77",
    "dal-2018": "g2hp-ar79",
}
# Un parametro -> (aggregazione, {finestra: risorsa Socrata}). L'aggregazione
# sta qui e non nella funzione apposta: è la decisione che, presa in due posti
# diversi, dà due numeri diversi per la stessa cosa (MET-13).
#
# ⚠️ I tre dataset della temperatura si chiamano «Temperatura fino al 2010» e
# così via: contengono **solo** i termometri. Passare loro un pluviometro non
# dà errore, dà zero righe — che è il modo in cui questo modulo ha prodotto per
# mesi una tabella di sole temperature mentre la documentazione ne prometteva
# quattro parametri.
SERIE_METEO: dict[str, tuple[str, dict[str, str]]] = {
    "Temperatura": (
        "media",
        {"fino-2010": "6eu4-4tja", "2011-2020": "d4kj-kbpj", "dal-2021": "w9wd-u6jh"},
    ),
    "Precipitazione": (
        "totale",
        {"fino-2010": "e7r2-7m84", "2011-2020": "2kar-pnuk", "dal-2021": "pstb-pga6"},
    ),
}

# Il nome dell'aggregazione nella tabella -> la funzione SoQL che la calcola.
AGGREGAZIONI = {"media": "avg", "totale": "sum"}

# ⚠️ L'alias del valore aggregato **non deve chiamarsi come una colonna della
# fonte**. Con `avg(valore) AS valore` il `WHERE valore > -100` risolve l'alias
# invece della colonna, e Socrata risponde `400 aggregate-in-ungrouped-context`.
# Costato mezz'ora, e senza il filtro sarebbero passate medie mensili negative
# — cioè i −999 di ARPA mescolati alle concentrazioni vere.
ALIAS_VALORE = "misura"
ALIAS_MASSIMO = "picco"

# --- lo stato della misura ----------------------------------------------
#
# Stessa idea della colonna `stato` di `turismo_comuni_annuale.csv`: quando un
# valore c'è ma non è affidabile **non si cancella, si marca**. Cancellarlo
# produrrebbe un buco indistinguibile da un dato mai raccolto, e la regola del
# progetto è che i tre modi di essere assenti sono tre cose diverse.

STATO_OK = "osservato"
STATO_IMPLAUSIBILE = "lettura_implausibile"
STATO_COPERTURA = "copertura_scarsa"

# La lettura singola oltre la quale non è un dato ma un guasto. Solo dove il
# limite si può **dichiarare**: per gli inquinanti il progetto non sa fissarne
# uno difendibile, e allora non lo inventa — lì resta il solo controllo di
# copertura.
#
# 100 mm in un intervallo (dieci minuti, o un'ora nelle serie vecchie) è sopra
# qualunque evento lombardo mai registrato. Nella provincia di Brescia lo
# superano **cinque letture su ventiquattro milioni**, e tre di esse rovinano
# altrettanti totali mensili: il pluviometro di Caino segna 109.499 mm in un
# intervallo del maggio 2020, e il mese esce a 109.589 mm.
LETTURA_MASSIMA = {"Precipitazione": 100.0}

# Sotto questa frazione della risoluzione tipica **del sensore stesso** il mese
# è coperto male. La soglia si calibra sul sensore e non è un numero fisso
# perché le risoluzioni convivono: il PM10 si misura una volta al giorno, la
# temperatura ogni dieci minuti, e una soglia assoluta marcherebbe come scarso
# tutto il particolato.
COPERTURA_MINIMA = 2 / 3

STAZIONI_COLUMNS = [
    "id_sensore", "id_stazione", "stazione", "comune", "parametro", "unita_misura",
    "quota", "lat", "lng", "data_inizio", "data_fine",
]
MISURE_COLUMNS = [
    "id_sensore", "stazione", "parametro", "mese", "media", "lettura_massima",
    "n_misure", "stato",
]
METEO_COLUMNS = [
    "id_sensore", "stazione", "parametro", "mese", "aggregazione", "valore",
    "lettura_massima", "n_misure", "stato",
]

# ARPA marca i dati non validi con -999 (e in alcune serie -9999): sommarli
# falserebbe ogni media. Il controllo sul campo `stato` sarebbe equivalente —
# le righe `NA` portano tutte -999 — ma la soglia copre anche le serie vecchie,
# dove `stato` non c'è.
VALIDO = "valore > -100"


def _stazioni_aria() -> list[dict[str, str]]:
    records = read_socrata(
        socrata_json(
            ANAGRAFICA_ARIA,
            dest_name="arpa_stazioni_aria_bs.json",
            where=f"provincia='{SIGLA_PROVINCIA}'",
        )
    )
    return [
        {
            "id_sensore": str(r.get("idsensore", "")),
            "id_stazione": str(r.get("idstazione", "")),
            "stazione": r.get("nomestazione", ""),
            "comune": r.get("comune", ""),
            "parametro": r.get("nometiposensore", ""),
            "unita_misura": r.get("unitamisura", ""),
            "quota": fmt(to_number(r.get("quota"))),
            "lat": r.get("lat", ""),
            "lng": r.get("lng", ""),
            "data_inizio": str(r.get("datastart", ""))[:10],
            "data_fine": str(r.get("datastop", ""))[:10],
        }
        for r in records
    ]


def _stazioni_meteo() -> list[dict[str, str]]:
    # L'anagrafica meteo non ha il campo `comune`: si filtra per provincia.
    records = read_socrata(
        socrata_json(
            ANAGRAFICA_METEO,
            dest_name="arpa_stazioni_meteo_bs.json",
            where=f"provincia='{SIGLA_PROVINCIA}'",
        )
    )
    return [
        {
            "id_sensore": str(r.get("idsensore", "")),
            "id_stazione": str(r.get("idstazione", "")),
            "stazione": r.get("nomestazione", ""),
            "comune": "",
            "parametro": r.get("tipologia", ""),
            "unita_misura": r.get("unit_dimisura", ""),
            "quota": fmt(to_number(r.get("quota"))),
            "lat": r.get("lat", ""),
            "lng": r.get("lng", ""),
            "data_inizio": str(r.get("datastart", ""))[:10],
            "data_fine": str(r.get("datastop", ""))[:10],
        }
        for r in records
    ]


def sensori_di(sensori: list[dict[str, str]], parametro: str) -> list[dict[str, str]]:
    """I soli sensori che misurano `parametro`.

    Serve perché ogni serie storica contiene un parametro solo: mandarle tutti
    i sensori della rete non dà errore, dà zero righe per quelli sbagliati.
    """
    return [s for s in sensori if s["parametro"] == parametro]


def parametri_scoperti(sensori: list[dict[str, str]]) -> list[str]:
    """I parametri presenti in anagrafica per cui non esiste una serie qui."""
    return sorted({s["parametro"] for s in sensori} - set(SERIE_METEO))


def _misure_mensili(
    resource: str, sensori: list[dict[str, str]], etichetta: str, aggregazione: str = "media"
) -> list[dict[str, str]]:
    """Chiede a Socrata il valore mensile per sensore, senza scaricare le orarie.

    `aggregazione` è una chiave di `AGGREGAZIONI`: decide sia la funzione SoQL
    sia l'etichetta che finisce nella tabella, così le due non possono divergere.
    """
    funzione = AGGREGAZIONI[aggregazione]
    per_id = {s["id_sensore"]: s for s in sensori}
    if not per_id:
        return []

    rows: list[dict[str, str]] = []
    ids = sorted(per_id)
    # Un `IN (...)` con troppi elementi allunga l'URL fino al rifiuto: si va a
    # blocchi, come per le chiavi SDMX multi-comune.
    for start in range(0, len(ids), 20):
        blocco = ids[start : start + 20]
        elenco = ",".join(f"'{i}'" for i in blocco)
        path = socrata_json(
            resource,
            dest_name=f"arpa_{etichetta}_{resource}_{start:03d}.json",
            select=f"idsensore, date_trunc_ym(data) AS mese, "
            f"{funzione}(valore) AS {ALIAS_VALORE}, "
            f"max(valore) AS {ALIAS_MASSIMO}, count(*) AS n",
            where=f"idsensore IN ({elenco}) AND {VALIDO}",
            group="idsensore, date_trunc_ym(data)",
            limit=200_000,
        )
        for record in read_socrata(path):
            sensore = str(record.get("idsensore", ""))
            info = per_id.get(sensore)
            valore = to_number(record.get(ALIAS_VALORE))
            if info is None or valore is None:
                continue
            rows.append(
                {
                    "id_sensore": sensore,
                    "stazione": info["stazione"],
                    "parametro": info["parametro"],
                    "mese": str(record.get("mese", ""))[:7],
                    "aggregazione": aggregazione,
                    "valore": fmt(valore, 2),
                    "lettura_massima": fmt(to_number(record.get(ALIAS_MASSIMO)), 2),
                    "n_misure": fmt(to_number(record.get("n"))),
                }
            )
    return rows


GIORNI_DEL_MESE = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)


def _giorni(mese: str) -> int:
    """Giorni del mese `AAAA-MM`, bisestili compresi."""
    anno, numero = int(mese[:4]), int(mese[5:7])
    if numero == 2 and (anno % 4 == 0 and (anno % 100 != 0 or anno % 400 == 0)):
        return 29
    return GIORNI_DEL_MESE[numero - 1]


def _mediana(valori: list[float]) -> float:
    ordinati = sorted(valori)
    meta = len(ordinati) // 2
    if len(ordinati) % 2:
        return ordinati[meta]
    return (ordinati[meta - 1] + ordinati[meta]) / 2


def marca_stato(righe: list[dict[str, str]]) -> None:
    """Aggiunge la colonna `stato` a ogni riga, in loco.

    Due controlli, entrambi dichiarati e nessuno dei quali cancella una riga:

    - **letture impossibili** (`LETTURA_MASSIMA`), che la fonte non marca e che
      il filtro sui −999 non vede: una sola basta a rovinare il totale di un
      mese;
    - **copertura scarsa** (`COPERTURA_MINIMA`), calibrata sul sensore stesso:
      una «media mensile» calcolata su otto letture non è una media mensile, e
      nella tabella non si distingue da una calcolata su quattromila.
    """
    per_sensore: dict[str, list[float]] = {}
    for riga in righe:
        giorni = _giorni(riga["mese"])
        per_sensore.setdefault(riga["id_sensore"], []).append(
            float(riga["n_misure"] or 0) / giorni
        )
    tipica = {sensore: _mediana(valori) for sensore, valori in per_sensore.items()}

    for riga in righe:
        soglia = LETTURA_MASSIMA.get(riga["parametro"])
        massimo = to_number(riga.get("lettura_massima"))
        al_giorno = float(riga["n_misure"] or 0) / _giorni(riga["mese"])
        attesa = tipica[riga["id_sensore"]]
        if soglia is not None and massimo is not None and massimo > soglia:
            riga["stato"] = STATO_IMPLAUSIBILE
        elif attesa and al_giorno < attesa * COPERTURA_MINIMA:
            riga["stato"] = STATO_COPERTURA
        else:
            riga["stato"] = STATO_OK


def build(comuni: dict[str, str]) -> None:
    aria = _stazioni_aria()
    meteo = _stazioni_meteo()
    write_csv("stazioni_arpa.csv", aria + meteo, STAZIONI_COLUMNS)

    misure_aria: list[dict[str, str]] = []
    for etichetta, resource in SERIE_ARIA.items():
        misure_aria += _misure_mensili(resource, aria, f"aria_{etichetta}")
    marca_stato(misure_aria)
    misure_aria.sort(key=lambda r: (r["id_sensore"], r["mese"]))
    # `aria_mensile.csv` chiama `media` la sua colonna e lo è davvero: per gli
    # inquinanti la concentrazione mensile è una media di concentrazioni. La
    # tabella del meteo non può fare lo stesso perché lì convivono medie e
    # totali, e la traduzione avviene qui invece di portarsi due chiavi
    # equivalenti in giro per il modulo.
    write_csv(
        "aria_mensile.csv",
        [dict(r, media=r["valore"]) for r in misure_aria],
        MISURE_COLUMNS,
    )

    misure_meteo: list[dict[str, str]] = []
    for parametro, (aggregazione, risorse) in SERIE_METEO.items():
        scelti = sensori_di(meteo, parametro)
        for etichetta, resource in risorse.items():
            misure_meteo += _misure_mensili(
                resource, scelti, f"meteo_{parametro.lower()}_{etichetta}", aggregazione
            )
        con_dati = {r["id_sensore"] for r in misure_meteo if r["parametro"] == parametro}
        print(f"  {parametro}: {len(con_dati)} sensori con misure su {len(scelti)}")

    marca_stato(misure_meteo)
    misure_meteo.sort(key=lambda r: (r["parametro"], r["id_sensore"], r["mese"]))
    write_csv("meteo_mensile.csv", misure_meteo, METEO_COLUMNS)
    for tabella, righe in (("aria", misure_aria), ("meteo", misure_meteo)):
        sospette = [r for r in righe if r["stato"] != STATO_OK]
        if sospette:
            print(f"  {tabella}: {len(sospette)} mesi marcati su {len(righe)}")

    # Nessuna assenza in silenzio: i parametri che l'anagrafica dichiara e che
    # questa tabella non copre si stampano, invece di lasciare che il lettore
    # deduca dal file quali dati non ci sono.
    scoperti = parametri_scoperti(meteo)
    if scoperti:
        print(f"  parametri meteo senza serie storica qui: {', '.join(scoperti)}")
