"""Lettura delle tabelle e statistica di base, condivise dagli script di analisi.

Non è un'analisi: è lo strato che le analisi hanno in comune, e per questo il
nome comincia con un trattino basso. Contiene le tre cose che ogni script
rifarebbe uguale — aprire un CSV di `dati/processed/`, ricavarne una serie per
comune e anno, e le due correlazioni che MET-6 impone di usare in coppia.

Due regole che questo modulo fa rispettare per costruzione:

- **le celle vuote sono dati mancanti, non zeri** (MET-3): `numero()` torna
  `None`, e le serie saltano la riga invece di scrivere uno zero;
- **il tasso annualizzato è composto**, non la variazione divisa per gli anni.
  Su undici anni la differenza fra i due è visibile a occhio nudo.

`verifica_cifre.py` **non** usa questo modulo, ed è voluto: un verificatore che
condivide il codice con ciò che verifica non verifica niente. Rilegge i CSV per
conto suo.
"""

from __future__ import annotations

import csv
import math
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
PROCESSED = RADICE / "dati" / "processed"
OUTPUT = Path(__file__).resolve().parent / "output"

CAPOLUOGO = "017029"
# Codici MEF dell'imponibile e dei contribuenti. Sono codici e non etichette
# per la ragione spiegata in `pipeline/datasets/redditi.py`: le etichette
# cambiano lingua.
IMPONIBILE = "AGGINCR"
PROVINCIA = "ITC47"

Serie = dict[str, dict[str, float]]  # codice comune -> anno -> valore

# I comuni **affacciati sul lago di Garda**, che MET-5 impone di togliere in un
# leave-one-out da qualunque correlazione tocchi il turismo — e i prezzi delle
# case lo toccano. La lista è geografica e sta scritta una volta sola (MET-13),
# **per nome**: i codici si risolvono dall'anagrafica, così una lista sbagliata
# fallisce invece di escludere in silenzio il comune sbagliato.
#
# ⚠️ Il nome non è il criterio: **Polpenazze del Garda**, **Puegnago del Garda**
# e **Soiano del Lago** portano il lago nel nome e non lo toccano; **Salò**,
# **Sirmione**, **Tignale** e **Gargnano** non lo portano e ci stanno sopra.
GARDESANI = (
    "Desenzano del Garda",
    "Gardone Riviera",
    "Gargnano",
    "Limone sul Garda",
    "Lonato del Garda",
    "Manerba del Garda",
    "Moniga del Garda",
    "Padenghe sul Garda",
    "Salò",
    "San Felice del Benaco",
    "Sirmione",
    "Tignale",
    "Toscolano-Maderno",
    "Tremosine sul Garda",
)


def codici_gardesani() -> set[str]:
    """I codici ISTAT dei comuni gardesani, risolti dall'anagrafica."""
    per_nome = {riga["comune"]: codice for codice, riga in anagrafica().items()}
    mancanti = [nome for nome in GARDESANI if nome not in per_nome]
    if mancanti:
        raise ValueError(f"comuni gardesani non trovati in anagrafica: {mancanti}")
    return {per_nome[nome] for nome in GARDESANI}




# --- lettura ------------------------------------------------------------


def leggi(nome: str) -> list[dict[str, str]]:
    with (PROCESSED / nome).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def numero(valore: str | None) -> float | None:
    """Le celle vuote sono dati mancanti, non zeri (MET-3)."""
    if valore is None or valore == "":
        return None
    return float(valore)


def anagrafica() -> dict[str, dict[str, str]]:
    return {riga["codice_istat"]: riga for riga in leggi("comuni.csv")}


def geometria() -> dict[str, dict[str, str]]:
    return {riga["codice_istat"]: riga for riga in leggi("comuni_geometria.csv")}


def sintesi() -> dict[str, dict[str, str]]:
    return {riga["codice_istat"]: riga for riga in leggi("comuni_sintesi.csv")}


def nome(codice: str) -> str:
    return anagrafica()[codice]["comune"]


# --- le serie per comune e anno -----------------------------------------


def serie_popolazione(indicatore: str = "popolazione_residente") -> Serie:
    per_comune: Serie = {}
    for riga in leggi("popolazione_comuni.csv"):
        if riga["indicatore"] != indicatore:
            continue
        valore = numero(riga["valore"])
        if valore is None:
            continue
        per_comune.setdefault(riga["codice_istat"], {})[riga["anno"]] = valore
    return per_comune


def serie_imprese(indicatore: str, classe: str = "totale") -> Serie:
    """`indicatore` è `addetti` o `unita_locali`; `classe` una fascia ASIA."""
    per_comune: Serie = {}
    for riga in leggi("imprese_classe_addetti.csv"):
        if riga["indicatore"] != indicatore or riga["classe_addetti"] != classe:
            continue
        valore = numero(riga["valore"])
        if valore is None:
            continue
        per_comune.setdefault(riga["codice_istat"], {})[riga["anno"]] = valore
    return per_comune


def serie_reddito(nome_file: str = "redditi_comuni.csv", provincia: str | None = None) -> Serie:
    """Reddito imponibile medio per contribuente, **in euro correnti**.

    Somma degli imponibili diviso somma dei contribuenti, su tutte le classi di
    importo. È un rapporto fra due totali, non la media delle medie di classe.

    Con `nome_file` e `provincia` legge la stessa cosa da una tabella di
    confronto (`redditi_comuni_confronto.csv`), che ha le stesse colonne più il
    territorio: serve a chiedersi se un risultato bresciano sia bresciano.

    ⚠️ **Nominale**, e adesso si può fare di meglio. Le tabelle MEF non portano
    un deflatore, ma dal settembre 2026 il progetto ne ha uno: `in_euro_costanti()`
    qui sotto, dall'indice ISTAT dei prezzi (MET-20). Vale la pena usarlo, perché
    la differenza non è una sfumatura — fra 2012 e 2023 l'inflazione è del 21,4 %,
    e la mediana comunale passa da +2,23 % l'anno a +0,44 %. Il confronto *fra
    comuni* nello stesso anno regge nominale; il confronto *fra anni* no.
    """
    imponibile: dict[str, dict[str, float]] = {}
    contribuenti: dict[str, dict[str, float]] = {}
    for riga in leggi(nome_file):
        if provincia is not None and riga.get("codice_provincia") != provincia:
            continue
        valore = numero(riga["valore"])
        if valore is None:
            continue
        # Sul **codice**, non sull'etichetta: l'etichetta cambia lingua con
        # l'header della richiesta, e una tabella scaricata ieri e una scaricata
        # oggi non si somigliano più (vedi `datasets/redditi.py`).
        deposito = imponibile if riga["codice_indicatore"] == IMPONIBILE else contribuenti
        chiave = deposito.setdefault(riga["codice_istat"], {})
        chiave[riga["anno"]] = chiave.get(riga["anno"], 0.0) + valore

    per_comune: Serie = {}
    for codice, per_anno in imponibile.items():
        for anno, totale in per_anno.items():
            teste = contribuenti.get(codice, {}).get(anno)
            if not teste:
                continue
            per_comune.setdefault(codice, {})[anno] = totale / teste
    return per_comune


# --- il deflatore -------------------------------------------------------

# L'anno in cui si esprimono gli euro costanti. È l'ultimo della serie dei
# prezzi, così «euro costanti» vuol dire «euro di oggi» e non richiede al
# lettore di immaginare quanto valesse un euro del 2015.
ANNO_EURO_COSTANTI = "2025"


def indice_prezzi() -> dict[str, float]:
    """`anno -> indice dei prezzi al consumo`, base 2015 = 100 (MET-20).

    È l'indice **nazionale**: deflazionare una serie bresciana con l'inflazione
    italiana è un'assunzione dichiarata, non una misura. Ogni testo che usi
    questa serie deve dirlo.
    """
    return {riga["anno"]: float(riga["indice"]) for riga in leggi("indice_prezzi.csv")}


def deflatore(base: str = ANNO_EURO_COSTANTI) -> dict[str, float]:
    """`anno -> fattore` che porta un euro di quell'anno in euro di `base`."""
    indice = indice_prezzi()
    if base not in indice:
        raise ValueError(f"l'anno {base} non è nella serie dei prezzi")
    return {anno: indice[base] / valore for anno, valore in indice.items()}


def in_euro_costanti(serie: dict[str, float], base: str = ANNO_EURO_COSTANTI) -> dict[str, float]:
    """La stessa serie `anno -> valore`, in euro di `base`.

    Gli anni fuori dalla serie dei prezzi **spariscono** invece di passare
    indeformati: un valore non deflazionato in mezzo a valori deflazionati è
    peggio di un valore mancante, perché non si vede.
    """
    fattori = deflatore(base)
    return {anno: valore * fattori[anno] for anno, valore in serie.items() if anno in fattori}


def quote_sezioni(anno: str | None = None) -> tuple[str, dict[str, dict[str, float]]]:
    """Quota di addetti per sezione Ateco, comune per comune.

    Restituisce `(anno, {codice: {sezione: quota}})`. Due decisioni che vanno
    prese qui una volta sola, perché prese in due modi diversi in due script
    producono due numeri diversi per la stessa cosa — ed è successo:

    - **il denominatore è il totale ASIA riportato** (`classe_addetti = totale`
      in `imprese_classe_addetti.csv`), non la somma delle sezioni. In pratica i
      due coincidono a meno dello 0,01 %, ma il totale riportato è quello che la
      fonte dichiara e non dipende da quali sezioni siano presenti;
    - **una sezione assente resta assente**, non diventa zero (MET-3). ASIA non
      pubblica la sezione di un comune quando la cella è troppo piccola, e
      «nessun addetto nella manifattura» è un'affermazione diversa da «non lo
      sappiamo». Chi usa queste quote deve decidere cosa fare dei `None`, e
      dichiararlo: gli script del progetto **escludono** il comune.
    """
    righe = leggi("imprese_sezioni_comuni.csv")
    scelto = anno or max(r["anno"] for r in righe)

    per_comune: dict[str, dict[str, float]] = {}
    for riga in righe:
        if riga["anno"] != scelto or riga["indicatore"] != "addetti":
            continue
        valore = numero(riga["valore"])
        if valore is not None:
            per_comune.setdefault(riga["codice_istat"], {})[riga["sezione"]] = valore

    totali = {
        riga["codice_istat"]: numero(riga["valore"])
        for riga in leggi("imprese_classe_addetti.csv")
        if riga["anno"] == scelto
        and riga["indicatore"] == "addetti"
        and riga["classe_addetti"] == "totale"
    }

    return scelto, {
        codice: {sezione: valore / totali[codice] * 100 for sezione, valore in sezioni.items()}
        for codice, sezioni in per_comune.items()
        if totali.get(codice)
    }


SERIE_DISPONIBILI = {
    "popolazione": ("Popolazione residente", "abitanti", serie_popolazione),
    "addetti": ("Addetti delle unità locali", "addetti", lambda: serie_imprese("addetti")),
    "unita_locali": ("Unità locali attive", "unità locali", lambda: serie_imprese("unita_locali")),
    "reddito": ("Reddito imponibile medio per contribuente", "euro correnti", serie_reddito),
}


# --- statistica ---------------------------------------------------------


def tasso_annualizzato(iniziale: float, finale: float, anni: int) -> float | None:
    """Tasso composto in percentuale. `None` se non è definito.

    Non è la variazione percentuale divisa per gli anni: su serie lunghe le due
    divergono, e la seconda è sbagliata.
    """
    if anni <= 0 or iniziale <= 0 or finale <= 0:
        return None
    return ((finale / iniziale) ** (1 / anni) - 1) * 100


def media(valori: list[float]) -> float:
    return sum(valori) / len(valori)


def pearson(x: list[float], y: list[float]) -> float | None:
    """Correlazione lineare. `None` se una delle due serie è costante."""
    if len(x) != len(y) or len(x) < 3:
        return None
    mx, my = media(x), media(y)
    num = sum((a - mx) * (b - my) for a, b in zip(x, y))
    dx = math.sqrt(sum((a - mx) ** 2 for a in x))
    dy = math.sqrt(sum((b - my) ** 2 for b in y))
    if dx == 0 or dy == 0:
        return None
    return num / (dx * dy)


def ranghi(valori: list[float]) -> list[float]:
    """Ranghi con media sui pari merito, come vuole Spearman."""
    ordinati = sorted(range(len(valori)), key=lambda i: valori[i])
    risultato = [0.0] * len(valori)
    i = 0
    while i < len(ordinati):
        j = i
        while j + 1 < len(ordinati) and valori[ordinati[j + 1]] == valori[ordinati[i]]:
            j += 1
        rango = (i + j) / 2 + 1
        for k in range(i, j + 1):
            risultato[ordinati[k]] = rango
        i = j + 1
    return risultato


def spearman(x: list[float], y: list[float]) -> float | None:
    """Correlazione di rango. Va sempre riportata **accanto** a Pearson (MET-6):
    quando le due divergono molto, il numero lo fanno pochi comuni."""
    if len(x) != len(y) or len(x) < 3:
        return None
    return pearson(ranghi(x), ranghi(y))


def senza(codici: list[str], escludi: set[str]) -> list[int]:
    """Indici delle posizioni da tenere: il leave-one-out di MET-5."""
    return [i for i, codice in enumerate(codici) if codice not in escludi]


# --- uscita -------------------------------------------------------------


def scrivi_csv(nome_file: str, colonne: list[str], righe: list[dict[str, str]]) -> Path:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    destinazione = OUTPUT / nome_file
    with destinazione.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=colonne, lineterminator="\n")
        writer.writeheader()
        writer.writerows(righe)
    return destinazione


# --- il bilancio demografico --------------------------------------------

# Le componenti della variazione di popolazione, definite **una volta sola**
# (MET-13). Ogni voce è una differenza fra due flussi lordi della tavola D7B.
COMPONENTI = {
    "saldo_naturale": ("nati", "morti"),
    "saldo_migratorio_interno": ("immigrati_interni", "emigrati_interni"),
    "saldo_migratorio_estero": ("immigrati_estero", "emigrati_estero"),
}

# Le due voci che **non** sono componenti demografiche e vanno tenute separate
# invece di essere spalmate dentro le altre: attribuire una rettifica anagrafica
# all'emigrazione è dare un titolo prima di decomporre.
NON_DEMOGRAFICHE = ["variazioni_territoriali", "aggiustamento_statistico"]


def bilancio(nome_file: str = "bilancio_demografico_comuni.csv", chiave: str = "codice_istat"):
    """`territorio -> anno -> indicatore -> valore`, dal bilancio demografico.

    Con `nome_file="bilancio_province.csv"` e `chiave="codice_provincia"` legge
    la stessa cosa per tutte le 107 province: è il termine di paragone.
    """
    fuori: dict[str, dict[str, dict[str, float]]] = {}
    for riga in leggi(nome_file):
        valore = numero(riga["valore"])
        if valore is None:
            continue
        fuori.setdefault(riga[chiave], {}).setdefault(riga["anno"], {})[riga["indicatore"]] = valore
    return fuori


def scomponi(per_anno: dict[str, dict[str, float]], anni: list[str] | None = None):
    """Le componenti sommate sul periodo, più il totale che devono ricostruire.

    Il totale è la somma delle componenti, non la differenza fra due stock: le
    due coincidono per costruzione (lo verifica la pipeline), e derivarlo da qui
    tiene la scomposizione internamente coerente anche su sottoperiodi.
    """
    scelti = sorted(anni or per_anno)
    somma = {nome: 0.0 for nome in list(COMPONENTI) + NON_DEMOGRAFICHE}
    for anno in scelti:
        conti = per_anno.get(anno, {})
        for nome, (piu, meno) in COMPONENTI.items():
            somma[nome] += conti.get(piu, 0.0) - conti.get(meno, 0.0)
        for nome in NON_DEMOGRAFICHE:
            somma[nome] += conti.get(nome, 0.0)
    somma["totale"] = sum(v for k, v in somma.items() if k != "totale")
    return somma
