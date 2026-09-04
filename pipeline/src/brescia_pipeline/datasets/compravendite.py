"""Volumi di compravendita OMI (NTN) per comune, 2011-2025.

Il gemello di [`omi.py`](omi.py): stessa fornitura dell'Agenzia delle Entrate,
stessi archivi versionati in `dati/input/omi/` — qui la cartella `volumi/` —
stessa citazione obbligatoria «Agenzia Entrate - OMI». Ma i file hanno un'altra
forma, e per tre motivi che costano tempo se non li si sa prima.

**1. La chiave non è il codice ISTAT, è il codice catastale.** La colonna si
chiama `2011_CodCom` (o `2011_CodFitt` nel residenziale: due nomi per la stessa
cosa) e contiene `B157`, non `017029`. La traduzione viene dall'elenco ISTAT dei
comuni, che porta il *Codice Catastale* accanto al codice ISTAT: da lì
`comuni.csv` prende la colonna `codice_catastale`, e questo modulo la rilegge in
locale. Nessun crosswalk inventato, nessuna seconda geometria (§9 di
`PROSSIMI-PASSI.md`).

**2. L'NTN è frazionario, ed è il suo significato.** «Numero di Transazioni
Normalizzate»: una compravendita in cui si cede metà della proprietà conta 0,5.
`88,25` non è un errore di lettura né un numero da arrotondare — è la misura.

**3. Il residenziale porta le classi di superficie *e* il totale.** Sommare
tutti i segmenti conta due volte, esattamente come le righe «Totale» dei flussi
turistici. Qui il totale resta — è quello che pubblica la fonte — ma come
`segmento = "totale"`, così filtrarlo è una scelta esplicita e non una svista.

I file nazionali arrivano interi: il filtro sui 205 comuni è locale, e le righe
delle altre 106 province si scartano qui.
"""

from __future__ import annotations

import csv
import io
import re
import zipfile
from pathlib import Path

from ..config import INPUT_DIR, PROCESSED_DIR
from ..tidy import fmt, to_number, write_csv

VOLUMI_DIR = "omi/volumi"

COLUMNS = ["codice_istat", "comune", "anno", "comparto", "segmento", "ntn"]

# Un file per comparto, dentro ogni archivio annuale.
COMPARTI = {
    "VALORI-RES": "residenziale",
    "VALORI-COM": "non_residenziale",
    "VALORI-PER": "pertinenze",
}

# Le colonne non-dato: le prime tre, che cambiano capitalizzazione e nome da
# un anno all'altro (`prov`, `PROVINCIA`, `Provincia`), più la chiave, che si
# chiama `<anno>_CodCom`, `<anno>_CodFitt` o — nel 2017 e 2018 — `COD_COM`.
NON_DATO = {"area", "regione", "prov", "provincia"}
CHIAVE = re.compile(r"^(\d{4}_cod|cod_com)")

# L'anno sta nel nome dei file interni (`VCN_1424968_1_2017_VALORI-RES.csv`) ed
# è l'unico posto dove c'è sempre: nel 2017 e nel 2018 la colonna chiave lo
# perde, e nel 2018 il residenziale lo perde anche dalle intestazioni dei dati.
ANNO_NEL_NOME = re.compile(r"_(\d{4})_")

# Le intestazioni dei dati portano l'anno dentro (`NTN_2011_Uffici`, `NTN 2011
# fino a 50 mq`): togliendo `NTN` e l'anno resta il segmento, e questa mappa lo
# rende leggibile. Le sigle `TCO_*` sono categorie catastali dentro il terziario
# commerciale: restano codici perché la fonte non le scioglie, e scioglierle a
# intuito è il genere di invenzione che questo progetto evita (MET-13).
SEGMENTI = {
    "": "totale",
    "fino a 50 mq": "fino a 50 mq",
    "50 -| 85 mq": "50-85 mq",
    "85 -| 115 mq": "85-115 mq",
    "115 -| 145 mq": "115-145 mq",
    "oltre 145 mq": "oltre 145 mq",
    "totale": "totale",
    "oltre 145": "oltre 145 mq",  # nel 2014 e nel 2017 la fonte perde il «mq»
    "uffici": "uffici",
    "negozi lab": "negozi_laboratori",
    "depositi comm": "depositi_commerciali",
    # ⚠️ Dal 2017 la colonna diventa «Depositi_Comm_Autorimesse»: non è un
    # rinominare, è un perimetro più largo. Resta un segmento **distinto**, così
    # una serie 2011-2025 su «depositi commerciali» non nasce per sbaglio
    # incollando due definizioni diverse (è la lezione di MET-17).
    "depositi comm autorimesse": "depositi_commerciali_autorimesse",
    "tco b04": "tco_b04",
    "tco d02": "tco_d02",
    "tco d05": "tco_d05",
    "tco d08": "tco_d08",
    "pro": "produttivo",
    "agr": "agricolo",
    "box": "box",
    "depositi pert": "depositi_pertinenziali",
}

# Il codice catastale dei comuni che oggi non esistono più, ricondotto al comune
# che ne ha il territorio. `G935` è Prestine, dal 2016 territorio di Bienno: la
# prova sta in `omi.py`, dove il caso si vede semestre per semestre.
CATASTALI_SOPPRESSI = {"G935": "017018"}


def catastali() -> dict[str, str]:
    """Mappa `codice catastale -> codice ISTAT`, letta da `comuni.csv`.

    Locale di proposito: questo dataset non tocca la rete, e un build offline
    deve poterlo rifare.
    """
    percorso = PROCESSED_DIR / "comuni.csv"
    if not percorso.exists():
        raise FileNotFoundError(
            f"manca {percorso.name}: serve la colonna codice_catastale per "
            "tradurre la chiave delle compravendite"
        )
    with percorso.open(encoding="utf-8") as handle:
        righe = list(csv.DictReader(handle))
    if not righe or "codice_catastale" not in righe[0]:
        raise RuntimeError(
            "comuni.csv non porta codice_catastale: rilancia `build confini` "
            "(o `build` senza argomenti) per rigenerarlo"
        )
    return {r["codice_catastale"]: r["codice_istat"] for r in righe if r["codice_catastale"]}


def build(comuni: dict[str, str]) -> None:
    archivi = sorted((INPUT_DIR / VOLUMI_DIR).glob("VCN_*.zip"))
    if not archivi:
        raise RuntimeError(
            f"nessun archivio in {INPUT_DIR / VOLUMI_DIR}: i volumi di "
            "compravendita si scaricano a mano, vedi dati/SCARICHI-MANUALI.md §1"
        )

    mappa = catastali() | CATASTALI_SOPPRESSI
    righe: list[dict[str, str]] = []
    for archivio in archivi:
        righe += _leggi_archivio(archivio, comuni, mappa)

    righe.sort(key=lambda r: (r["codice_istat"], r["anno"], r["comparto"], r["segmento"]))
    write_csv("compravendite_comuni.csv", righe, COLUMNS)


def _leggi_archivio(
    archivio: Path, comuni: dict[str, str], mappa: dict[str, str]
) -> list[dict[str, str]]:
    righe: list[dict[str, str]] = []
    with zipfile.ZipFile(archivio) as zf:
        for nome in sorted(zf.namelist()):
            comparto = next((c for k, c in COMPARTI.items() if k in nome.upper()), None)
            if comparto is None:
                continue  # LISTA-COM: è l'anagrafica, la chiave la abbiamo già
            trovato = ANNO_NEL_NOME.search(nome)
            if not trovato:
                raise RuntimeError(f"{nome}: il nome non porta l'anno")
            with zf.open(nome) as grezzo:
                testo = io.TextIOWrapper(grezzo, encoding="latin-1", newline="")
                righe += _righe(
                    csv.DictReader(testo, delimiter=";"),
                    comuni, mappa, comparto, trovato.group(1),
                )
    if not righe:
        raise RuntimeError(f"{archivio.name}: nessuna riga dei 205 comuni")
    return righe


def _righe(
    reader: csv.DictReader,
    comuni: dict[str, str],
    mappa: dict[str, str],
    comparto: str,
    anno: str,
) -> list[dict[str, str]]:
    campi = reader.fieldnames or []
    chiave = next((c for c in campi if CHIAVE.match((c or "").strip().lower())), None)
    if chiave is None:
        raise RuntimeError(f"colonna chiave del comune non trovata fra {campi}")
    candidate = [
        c for c in campi
        if c and c.strip() and c.strip().lower() not in NON_DATO and c != chiave
    ]
    dati = {c: SEGMENTI[_segmento(c, anno)] for c in candidate if _segmento(c, anno) in SEGMENTI}
    ignoti = [c for c in candidate if c not in dati]
    for colonna in ignoti:
        print(f"  ⚠️  colonna {colonna!r} non è in SEGMENTI: ignorata")

    righe: list[dict[str, str]] = []
    for record in reader:
        code = mappa.get((record.get(chiave) or "").strip())
        if code not in comuni:
            continue
        for colonna, segmento in dati.items():
            valore = to_number(record.get(colonna))
            if valore is None:
                # L'NTN assente non è zero: sono comuni per cui la fonte non
                # pubblica quel segmento.
                continue
            righe.append({
                "codice_istat": code,
                "comune": comuni[code],
                "anno": anno,
                "comparto": comparto,
                "segmento": segmento,
                "ntn": fmt(valore, 2),
            })
    return righe


def _segmento(colonna: str, anno: str) -> str:
    """`NTN_2011_Negozi_Lab` -> `negozi lab`; `NTN 2011` -> `` (il totale)."""
    testo = (colonna or "").strip().lower().replace("_", " ")
    testo = testo.replace("ntn", " ").replace(anno, " ")
    return re.sub(r"\s+", " ", testo).strip()
