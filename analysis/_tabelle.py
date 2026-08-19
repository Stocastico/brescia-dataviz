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
PROVINCIA = "ITC47"

Serie = dict[str, dict[str, float]]  # codice comune -> anno -> valore


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


def serie_reddito() -> Serie:
    """Reddito imponibile medio per contribuente, **in euro correnti**.

    Somma degli imponibili diviso somma dei contribuenti, su tutte le classi di
    importo. È un rapporto fra due totali, non la media delle medie di classe.

    ⚠️ **Nominale.** Le tabelle MEF non portano un deflatore e il progetto non
    ne ha scaricato uno: fra 2012 e 2023 una parte della crescita è inflazione,
    e ogni testo che usi questa serie deve dirlo. Il confronto *fra comuni* nello
    stesso anno non ne soffre; il confronto *fra anni* sì.
    """
    imponibile: dict[str, dict[str, float]] = {}
    contribuenti: dict[str, dict[str, float]] = {}
    for riga in leggi("redditi_comuni.csv"):
        valore = numero(riga["valore"])
        if valore is None:
            continue
        deposito = imponibile if riga["indicatore"].startswith("income") else contribuenti
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
