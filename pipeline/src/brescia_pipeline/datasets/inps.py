"""Retribuzioni e lavoratori dipendenti per provincia, dal 2008. Fonte: INPS.

**È l'unica fonte sui salari che questo progetto abbia.** Il registro delle
imprese dà addetti e unità locali, il MEF dà i redditi dichiarati (che
comprendono pensioni, affitti e lavoro autonomo, e sono per contribuente):
nessuna delle due dice quanto viene pagato chi lavora. Questa lo dice, per
**107 province** e **diciassette anni**, con la retribuzione media come
rapporto fra due conteggi della fonte e non come stima.

Le misure sono tre, e sono quelle che l'osservatorio pubblica:

| indicatore | cosa conta |
|---|---|
| `lavoratori` | dipendenti del settore privato non agricolo con almeno una giornata retribuita nell'anno |
| `retribuzione_totale` | la massa retributiva annua, in euro correnti |
| `giornate_retribuite` | le giornate retribuite, che sono il denominatore giusto per una retribuzione *giornaliera* |

La media annua è `retribuzione_totale / lavoratori`; quella giornaliera è
`retribuzione_totale / giornate_retribuite`. Le due rispondono a domande
diverse: la prima dice quanto ha incassato in un anno chi ha lavorato anche un
solo giorno, quindi il part-time e i contratti brevi la tirano giù; la seconda
no. Tenerle entrambe e non calcolarne nessuna qui è deliberato — la scelta sta
in `analysis/`, dove si legge.

## L'API, e le tre cose che la fanno sembrare rotta

Gli Osservatori statistici sono un'applicazione web, non un'API documentata:
`FONTI.md` diceva «il primo lavoro è trovare l'endpoint che l'applicazione
stessa chiama, e potrebbe non essercene uno stabile». L'endpoint c'è, è
`api/getDatiOsservatorio/` in POST, e **non chiede né sessione né cookie**. Ma
per arrivarci bisogna sapere tre cose, e ognuna fallisce in silenzio.

**1. Il corpo JSON non può avere spazi.** Con i separatori di default di
`json.dumps` — `", "` e `": "` — il server risponde «The input is not a valid
Base-64 string as it contains a non-base 64 character». Con `separators=(",",
":")` la stessa richiesta funziona. È il motivo per cui questo modulo serializza
a mano e passa i byte, invece di usare `json=` di `requests`: quel parametro
aggiunge gli spazi. Nessuna documentazione dice perché.

**2. La risposta è gzip anche senza chiederlo.** `requests` la decomprime da
sé; un client che legge i byte grezzi trova `\\x1f\\x8b` e un errore di UTF-8.

**3. Le dimensioni si chiamano col loro id interno.** `Provincia` e `Qualifica`
funzionano; `Sezione ATECO 2007`, che è l'etichetta mostrata nell'interfaccia,
risponde «Dati al momento non disponibili». L'id interno di quella dimensione
non è documentato e si trova solo intercettando l'applicazione mentre la
seleziona. **Per questo il taglio settoriale non c'è**: sarebbe la cosa più
interessante in una provincia manifatturiera, e resta la prima estensione da
fare. Non è un limite della fonte, è un id che non abbiamo.

## Gli id degli osservatori, e perché sono una costante

Quattro osservatori coprono i diciassette anni, uno per vintage della
classificazione Ateco. L'albero di navigazione che li elenca arriva da un altro
POST il cui corpo non è documentato, e la pagina HTML non li contiene (li
inietta il JavaScript): a differenza di `bilancio.py` e
`compravendite_province.py`, qui **non c'è una pagina da leggere**.

Quindi sono scritti qui, e per non farli invecchiare in silenzio il modulo
**verifica che l'osservatorio risponda per ogni anno che dichiara di coprire**.
Un anno che smette di rispondere ferma il build invece di accorciare la serie.

⚠️ La rottura fra il 2013 e il 2014 è di **classificazione dell'attività
economica**, non di popolazione: gli anni si concatenano senza problemi finché
il settore non entra nella tabella. Il giorno che entrerà, quella giunzione è
MET-19 da rifare.
"""

from __future__ import annotations

import json
import re

import requests

from ..fetch import DEFAULT_TIMEOUT
from ..tidy import write_csv
from .province import province_italiane

API = "https://servizi2.inps.it/servizi/osservatoristatistici/api/getDatiOsservatorio/"

COLUMNS = ["codice_provincia", "provincia", "regione", "anno", "indicatore", "valore"]

# `id osservatorio -> anni coperti`. Vedi il docstring: sono una costante che si
# controlla, non una costante che si spera.
OSSERVATORI = {
    "348": [str(a) for a in range(2008, 2014)],  # Ateco 2002
    "347": [str(a) for a in range(2014, 2019)],  # Ateco 2007
    "492": [str(a) for a in range(2019, 2024)],
    "525": ["2024"],
}

# Le misure dell'osservatorio, col nome che prendono nella tabella.
MISURE = {
    "lav_annoSUM": "lavoratori",
    "RRSUM": "retribuzione_totale",
    "GGSUM": "giornate_retribuite",
}

# I nomi che l'INPS scrive diversamente dall'elenco ISTAT. Sono cinque, e sono
# tutti la stessa cosa scritta in un altro modo: due province autonome col
# titolo davanti, la Valle d'Aosta chiamata col capoluogo, un accento reso con
# l'apostrofo e una preposizione in meno. Nessuna è un territorio diverso.
NOMI_INPS = {
    "Aosta": "Valle d'Aosta/Vallée d'Aoste",
    "Provincia Autonoma di Bolzano/Bozen": "Bolzano/Bozen",
    "Provincia Autonoma di Trento": "Trento",
    "Forli'-Cesena": "Forlì-Cesena",
    "Reggio Emilia": "Reggio nell'Emilia",
}

# ⚠️ `Totale:` è la riga di totale che l'osservatorio aggiunge perché la
# richiesta porta `totalRow`. Tenerla raddoppierebbe l'Italia, ed è la stessa
# trappola delle righe «Totale» dei flussi turistici. `Estero` non è una
# provincia: sono i lavoratori con sede di lavoro fuori dall'Italia, e
# `Non ripartibili` quelli che la fonte non sa collocare.
#
# `Non ripartibili` **non compare nel 2024** e compare negli anni più vecchi:
# l'ha trovato la guardia sui nomi ignoti al primo build vero, che è
# esattamente il lavoro per cui esiste. Un elenco costruito guardando un anno
# solo è un elenco incompleto.
NON_PROVINCE = {"Totale:", "Estero", "Non ripartibili"}

# I valori arrivano col punto come separatore delle migliaia e **mai** con
# decimali: `702.557` lavoratori, `19.069.749.042` euro.
INTERO_INPS = re.compile(r"^\d{1,3}(?:\.\d{3})*$")


def intero(testo: str | None) -> int | None:
    """`'702.557'` -> `702557`. Il punto è separatore di migliaia, sempre.

    ⚠️ **Non si può usare `tidy.to_number` qui, e la ragione costa mille
    volte.** Quella funzione decide il separatore decimale guardando la
    stringa, e su `702.557` — un punto solo, tre cifre dopo — non ha modo di
    sapere se sono settecentomila lavoratori o settecento virgola cinque. Legge
    `702.557` e restituisce 702,557: un numero plausibile, un ordine di
    grandezza sbagliato, nessun errore. In un solo anno **106 valori su 321**
    hanno quella forma, Torino compreso.

    Qui l'ambiguità non esiste, perché il formato della fonte non ha decimali:
    quindi il punto si toglie e basta. Una stringa che non ha quella forma è un
    errore, non un valore da indovinare.
    """
    if testo is None:
        return None
    ripulito = testo.strip()
    if not ripulito or ripulito == "-":
        return None
    if not INTERO_INPS.match(ripulito):
        raise RuntimeError(
            f"valore INPS in una forma non prevista: {testo!r}. Il formato "
            "atteso è a gruppi di tre separati dal punto e senza decimali; se "
            "la fonte ha cambiato formato va guardata, non arrotondata"
        )
    return int(ripulito.replace(".", ""))


def _corpo(osservatorio: str, anno: str) -> bytes:
    """Il POST, serializzato **senza spazi**: con gli spazi il server rifiuta.

    Vedi il punto 1 del docstring. Non è una micro-ottimizzazione: è la
    differenza fra 109 righe e un errore che parla di Base-64.
    """
    richiesta = {
        "id_osservatorio": osservatorio,
        "nome_osservatorio": "",
        "language": "",
        "totalRow": True,
        "totalColumn": True,
        "subtotalRow": True,
        "subtotalColumn": True,
        "selections": {
            "rows": [{
                "id": "Provincia", "label": "Provincia", "order": 1,
                "aggregate": True, "expand": "", "hide": False,
            }],
            "cols": [],
            "measures": [
                {"id": misura, "label": misura, "order": 0, "statistic": "SUM"}
                for misura in MISURE
            ],
            "filters": [{"id": "acomp", "label": "Anno", "values": [anno]}],
        },
    }
    return json.dumps(richiesta, separators=(",", ":")).encode("utf-8")


def scarica(osservatorio: str, anno: str) -> list[dict]:
    """Le righe per provincia di un anno. Un anno vuoto è un errore.

    Non passa da `fetch()` perché quella cache è per URL e qui l'URL è sempre
    lo stesso: la richiesta sta nel corpo. Sono diciassette chiamate da qualche
    decina di KB, quindi la cache non serve.
    """
    risposta = requests.post(
        API,
        data=_corpo(osservatorio, anno),
        headers={"Content-Type": "application/json"},
        timeout=DEFAULT_TIMEOUT,
    )
    risposta.raise_for_status()
    dati = risposta.json()
    valori = dati.get("values")
    if not valori:
        raise RuntimeError(
            f"osservatorio {osservatorio} non risponde per il {anno}: "
            f"{dati.get('error', 'nessun valore')}. Gli id in OSSERVATORI sono "
            "cambiati, oppure la serie si è accorciata: va guardato, non aggirato"
        )
    return valori


def build(comuni: dict[str, str]) -> None:
    del comuni  # tabella nazionale: qui servono le province

    province = {nome: (codice, regione) for codice, (nome, regione) in province_italiane().items()}
    righe: list[dict[str, str]] = []
    ignoti: set[str] = set()

    for osservatorio, anni in OSSERVATORI.items():
        for anno in anni:
            for voce in scarica(osservatorio, anno):
                nome = (voce.get("value") or "").strip()
                if nome in NON_PROVINCE:
                    continue
                nome = NOMI_INPS.get(nome, nome)
                if nome not in province:
                    ignoti.add(nome)
                    continue
                codice, regione = province[nome]
                for misura in voce.get("measures", []):
                    indicatore = MISURE.get(misura.get("label"))
                    valore = intero(misura.get("value"))
                    if indicatore is None or valore is None:
                        continue
                    righe.append({
                        "codice_provincia": codice,
                        "provincia": nome,
                        "regione": regione,
                        "anno": anno,
                        "indicatore": indicatore,
                        "valore": str(valore),
                    })

    if ignoti:
        raise RuntimeError(
            f"nomi di provincia non tradotti: {sorted(ignoti)}. Sono province "
            "che spariscono dalla tabella senza dirlo: vanno aggiunte a "
            "NOMI_INPS dopo aver verificato che siano la stessa cosa scritta "
            "diversamente e non un territorio diverso"
        )
    if not righe:
        raise RuntimeError("nessuna riga dagli osservatori INPS")

    righe.sort(key=lambda r: (r["codice_provincia"], r["anno"], r["indicatore"]))
    write_csv("retribuzioni_province.csv", righe, COLUMNS)
