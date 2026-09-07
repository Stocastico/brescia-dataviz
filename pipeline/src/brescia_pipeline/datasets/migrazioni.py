"""Background migratorio per comune: l'asse «chi vive nel bresciano».

Dieci tavole del Censimento permanente che, messe insieme, permettono la
distinzione che quasi tutte le narrazioni pubbliche sbagliano: **stranieri
immigrati**, **stranieri nati in Italia** (seconde generazioni) e **italiani
per acquisizione**. Non sono tre modi di dire la stessa cosa, e tenerle
separate è il motivo per cui questo asse è nel brief (`BRIEF.md`, storia 3).

Le dieci tavole si distinguono per popolazione di partenza e per variabile di
incrocio; la dimensione territoriale è il comune, quindi tutte e 205 le righe
della provincia ci sono.

⚠️ `PREVOUS_CITIZEN` è scritto così nella struttura ISTAT, con il refuso.
Rinominarlo qui romperebbe la corrispondenza con la fonte, quindi resta.

## Tre tabelle, e perché non una

`migrazioni_comuni.csv` è la distribuzione congiunta completa: 1,8 milioni di
righe e 422 MB, **fuori da git** (`dati/SCARICHI-LOCALI.md`). Serve a capire, e
si rigenera con un comando.

Ma il progetto ha una regola che quel file rendeva impossibile rispettare:
**finché un dato non è nel repository, nessuna cifra pubblicata può dipendere da
lui.** Finché nessuna storia usava questo asse la regola non stringeva; nel
momento in cui una storia lo usa, stringe.

Da qui le due **marginali versionate**, che sono la seconda delle due strade
lasciate aperte in `PROSSIMI-PASSI.md` §2.1 — «solo le combinazioni che la
storia userà davvero» — scelta come quel documento chiedeva: **guardando la
storia**, non prima.

| tabella | grana | a cosa serve |
|---|---|---|
| `background_migratorio_comuni.csv` | comune × anno × indicatore | lo stock: italiani dalla nascita, acquisiti, stranieri, nati all'estero, e le seconde generazioni |
| `background_migratorio_istruzione.csv` | **provincia** × anno × gruppo × classe d'età × titolo | il titolo di studio, che a grana comunale sarebbe 55.000 righe per una tabella che nessuna storia legge per comune |

La congiunta resta l'unica che tiene gli incroci fini: le marginali non
sostituiscono l'analisi, la pubblicano.

⚠️ **Le due tabelle non si sommano fra loro.** La prima conta tutta la
popolazione, la seconda solo i **9 anni e più**, che è la popolazione su cui la
fonte pubblica il titolo di studio. Confrontare un totale della seconda con uno
della prima è l'errore che questa nota esiste per prevenire.
"""

from __future__ import annotations

from collections import defaultdict

from . import _censimento
from ..tidy import write_csv

# Le dieci tavole `_COM`, con un nome che dice di che popolazione parlano.
TAVOLE = {
    "italiani_stranieri_per_nascita_genitori": 1,
    "italiani_nati_in_italia": 2,
    "italiani_nati_all_estero": 3,
    "italiani_acquisizione_nati_in_italia": 4,
    "italiani_acquisizione_nati_all_estero": 5,
    "stranieri_nati_in_italia": 6,
    "stranieri_nati_all_estero": 7,
    "italiani_istruzione": 8,
    "italiani_acquisizione_istruzione": 9,
    "stranieri_istruzione": 10,
}

DIMENSIONI = [
    "GENDER",
    "AGE_CLASS",
    "CITIZENSHIP",
    "PREVOUS_CITIZEN",
    "PLACE_BIRTH_PAR",
    "EDU_ATTAIN",
]

COLUMNS = _censimento.colonne(DIMENSIONI)

COLUMNS_SINTESI = ["codice_istat", "comune", "anno", "indicatore", "valore"]
COLUMNS_ISTRUZIONE = ["anno", "gruppo", "classe_eta", "titolo", "valore"]


# --- le marginali versionate ---------------------------------------------

# La tavola 1 porta tutti i totali di stock, e li porta come **indicatori**
# distinti invece che come modalità di una dimensione: è il motivo per cui
# questa mappa cerca stringhe esatte e non prefissi.
STOCK = "italiani_stranieri_per_nascita_genitori"

# La chiave è `(tavola, indicatore, classe d'età)`. L'indicatore da solo non
# basta: la fonte pubblica la stessa popolazione due volte — una per classi
# decennali con un indicatore, e una sola riga «fino a 17 anni» con un
# indicatore **diverso**. Le due non si sovrappongono (dove una ha un valore
# l'altra non ha righe), quindi tenerle entrambe dà i minorenni senza sommare
# a mano e senza rischio di contarli due volte.
SINTESI = {
    (STOCK, "popolazione residente al 31 dicembre", "totale"): "popolazione_residente",
    (STOCK, "popolazione italiana residente al 31 dicembre", "totale"): "italiani",
    (STOCK, "popolazione straniera residente al 31 dicembre", "totale"): "stranieri",
    (STOCK, "italiani dalla nascita al 31 dicembre", "totale"): "italiani_dalla_nascita",
    (STOCK, "italiani acquisiti al 31 dicembre", "totale"): "italiani_acquisiti",
    (STOCK, "italiani dalla nascita nati in Italia al 31 dicembre",
     "totale"): "italiani_dalla_nascita_nati_in_italia",
    (STOCK, "italiani dalla nascita nati all estero (immigrati) al 31 dicembre",
     "totale"): "italiani_dalla_nascita_nati_all_estero",
    (STOCK, "italiani acquisiti nati in Italia al 31 dicembre",
     "totale"): "italiani_acquisiti_nati_in_italia",
    (STOCK, "italiani acquisiti nati all'estero (immigrati) al 31 dicembre",
     "totale"): "italiani_acquisiti_nati_all_estero",
    (STOCK, "stranieri/apolidi nati in Italia al 31 dicembre",
     "totale"): "stranieri_nati_in_italia",
    (STOCK, "stranieri/apolidi nati all estero (immigrati) al 31 dicembre",
     "totale"): "stranieri_nati_all_estero",
    ("stranieri_nati_in_italia",
     "stranieri/apolidi nati in Italia fino a 17 anni al 31 dicembre",
     "fino a 17 anni"): "stranieri_nati_in_italia_minorenni",
    ("italiani_acquisizione_nati_in_italia",
     "italiani acquisiti nati in Italia fino a 17 anni al 31 dicembre",
     "fino a 17 anni"): "italiani_acquisiti_nati_in_italia_minorenni",
}

# Le tre tavole del titolo di studio, col gruppo che rappresentano e il filtro
# che le tiene oneste. Il filtro non è cosmetico: `stranieri_istruzione`
# pubblica la stessa popolazione tre volte — il totale e i due sottoinsiemi UE
# ed extra-UE — quindi prendere tutte le righe la conterebbe due volte.
ISTRUZIONE = {
    "italiani_istruzione": ("italiani dalla nascita", "citizenship", "italiano-a"),
    "italiani_acquisizione_istruzione": ("italiani acquisiti", "prevous_citizen", "totale"),
    "stranieri_istruzione": ("stranieri", "citizenship", "straniero-a/apolide"),
}

# Il totale delle dimensioni che nelle marginali non entrano. ⚠️
# `place_birth_par` chiama il suo totale «tutte le voci» e non «totale»: è la
# trappola di questa famiglia di tavole, e cercare «totale» qui non dà un
# errore, dà zero righe.
TOTALI = {"gender": "totale", "place_birth_par": "tutte le voci"}

# ⚠️ E il totale della cittadinanza si chiama in tre modi diversi a seconda
# della tavola, che è il modo in cui questa marginale è nata sbagliata: le due
# righe dei minorenni venivano **esattamente il doppio** (50.204 invece di
# 25.102) perché in quelle tavole `citizenship` porta il totale *e* i due
# sottoinsiemi UE ed extra-UE, e sommarli tutti conta la stessa persona due
# volte. Nella tavola 1 la dimensione è fissa e il problema non c'è — ed è
# proprio per questo che i totali di stock tornavano e nessuno sospettava
# niente. Il controllo che l'ha trovato è in `test_migrazioni.py`.
FILTRI = {
    "stranieri_nati_in_italia": ("citizenship", "straniero-a/apolide"),
    "italiani_acquisizione_nati_in_italia": ("prevous_citizen", "totale"),
}


def build(comuni: dict[str, str]) -> None:
    rows: list[dict[str, str]] = []
    for nome, numero in TAVOLE.items():
        rows += _censimento.tavola(
            f"DF_DCSS_MIGR_BACKG_PAR_TV_{numero}_COM",
            nome=nome,
            dest_name=f"istat_migr_backg_tv{numero}.csv",
            comuni=comuni,
            dimensioni=DIMENSIONI,
        )

    _censimento.ordina(rows, DIMENSIONI)
    write_csv("migrazioni_comuni.csv", rows, COLUMNS)

    # Le marginali vengono dalle stesse righe: nessuna richiesta in piu'.
    write_csv("background_migratorio_comuni.csv", sintesi(rows), COLUMNS_SINTESI)
    write_csv("background_migratorio_istruzione.csv", istruzione(rows), COLUMNS_ISTRUZIONE)


def _e_totale(riga: dict[str, str]) -> bool:
    return all(riga[dimensione] == modalita for dimensione, modalita in TOTALI.items())


def sintesi(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    """Lo stock per comune: una riga per comune × anno × indicatore."""
    fuori: list[dict[str, str]] = []
    for riga in rows:
        if not _e_totale(riga) or riga["valore"] == "":
            continue
        nome = SINTESI.get((riga["tavola"], riga["indicatore"], riga["age_class"]))
        if nome is None:
            continue
        filtro = FILTRI.get(riga["tavola"])
        if filtro is not None and riga[filtro[0]] != filtro[1]:
            continue
        fuori.append({
            "codice_istat": riga["codice_istat"],
            "comune": riga["comune"],
            "anno": riga["anno"],
            "indicatore": nome,
            "valore": riga["valore"],
        })
    if not fuori:
        raise RuntimeError(
            "nessuna riga di sintesi: le etichette degli indicatori sono "
            "cambiate, e SINTESI le cerca per stringa esatta"
        )

    fuori.sort(key=lambda r: (r["codice_istat"], r["anno"], r["indicatore"]))
    return fuori


def istruzione(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    """Il titolo di studio, aggregato sui 205 comuni: la provincia.

    L'aggregazione e' una somma di conteggi, non una media, quindi non ha pesi
    da sbagliare. Le celle vuote — la fonte sopprime i numeri piccoli —
    restano fuori dalla somma e **non** diventano zeri (MET-3): il totale
    provinciale e' quindi il minimo osservato, non una stima.
    """
    totali: dict[tuple[str, str, str, str], float] = defaultdict(float)
    for riga in rows:
        atteso = ISTRUZIONE.get(riga["tavola"])
        if atteso is None or riga["valore"] == "":
            continue
        gruppo, dimensione, modalita = atteso
        if riga[dimensione] != modalita or not _e_totale(riga):
            continue
        chiave = (riga["anno"], gruppo, riga["age_class"], riga["edu_attain"])
        totali[chiave] += float(riga["valore"])
    if not totali:
        raise RuntimeError("nessuna riga di istruzione: le tre tavole sono cambiate")

    return [
        {
            "anno": anno,
            "gruppo": gruppo,
            "classe_eta": eta,
            "titolo": titolo,
            "valore": _intero(valore),
        }
        for (anno, gruppo, eta, titolo), valore in sorted(totali.items())
    ]


def _intero(valore: float) -> str:
    """I conteggi censuari sono interi: la somma in virgola mobile no."""
    return str(int(round(valore)))
