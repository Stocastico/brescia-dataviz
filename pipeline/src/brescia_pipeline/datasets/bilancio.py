"""Da dove viene la variazione di popolazione: nascite, morti, chi arriva e chi va.

Fonte: ISTAT, **bilancio demografico mensile** (tavola `D7B` di
`demo.istat.it`), un file per anno con tutti i comuni italiani.

È la tabella che risponde alla domanda che la prima storia del sito dichiara di
non poter rispondere: *93 comuni su 205 perdono abitanti — perché?* Un comune
può svuotarsi perché ci muore più gente di quanta ne nasca, perché chi ci abita
se ne va in un altro comune, o perché smette di arrivare gente dall'estero, e
sono tre fenomeni diversi con tre risposte diverse.

## Perché questa fonte e non l'SDMX

`popolazione_comuni.csv` viene dal Censimento permanente e porta **gli stock**:
quanti abitanti al 31 dicembre. I flussi che li collegano stanno qui, e la cosa
che rende questa fonte utilizzabile senza mescolare due popolazioni diverse è
che **i due numeri sono lo stesso numero**: la riga «Popolazione censita al 31
dicembre» del bilancio coincide, comune per comune e anno per anno, con la
popolazione del censimento permanente. Verificato su tutti i 205 comuni e tutti
gli anni, allo zero. La decomposizione quindi **chiude**: non c'è un residuo da
attribuire alla differenza fra due fonti.

## Le quattro trappole di questo file

Sono tutte silenziose: nessuna dà errore, tutte danno un numero plausibile.

1. **La dimensione «Sesso» ha un totale.** Ogni osservazione compare tre volte:
   `Maschi`, `Femmine`, `Totale`. Sommare tutte le righe raddoppia la
   popolazione italiana, e 118 milioni di abitanti non stonano abbastanza da
   farsi notare in una tabella intermedia.
2. **Il codice comune vuoto non è un comune.** Le righe con `Codice comune`
   vuoto sono gli **aggregati provinciali** della fonte; quelle con anche
   `Codice provincia` vuoto sono l'aggregato nazionale. Qui gli aggregati
   provinciali non si buttano: diventano il **controllo** contro cui si verifica
   la somma dei comuni (`verifica_province`).
3. **I «mesi» sono quattordici.** Oltre ai dodici veri ci sono il **13**
   («Aggiustamento statistico») e il **15** («Popolazione censita al 31
   dicembre»). Non sono mesi e le loro colonne di flusso sono vuote: entrano
   nella somma come zeri, ma il loro contenuto sta nella colonna «Popolazione
   fine periodo», che per il 13 è *l'ammontare della rettifica* e non una
   popolazione.
4. **L'aggiustamento statistico non è un fenomeno demografico.** È la rettifica
   che riconcilia l'anagrafe con il censimento, e va tenuta separata dalle altre
   componenti invece di essere spalmata dentro: dire «questo comune ha perso
   trenta abitanti per emigrazione» quando venti sono rettifica anagrafica è un
   errore della stessa famiglia di MET-9, un titolo dato prima di decomporre.

## Cosa produce

- `bilancio_demografico_comuni.csv` — i 205 comuni, un anno per riga e
  indicatore;
- `bilancio_province.csv` — gli stessi indicatori per **tutte le 107 province**,
  che qui non costano un download in più: il file è nazionale. È il termine di
  paragone che allo spopolamento montano mancava — le imprese e i redditi ce
  l'hanno (`province.py`, `redditi_confronto.py`), la popolazione no.

⚠️ Come per `province.py`: gli aggregati provinciali **non sono un secondo
soggetto**. Servono a collocare Brescia, non a disegnare mappe fuori provincia.
"""

from __future__ import annotations

import csv
import io
import re
import zipfile
from collections import defaultdict
from collections.abc import Iterable, Iterator
from pathlib import Path

from ..config import BILANCIO_ANNI_URL, BILANCIO_FILE_URL, PRIMO_ANNO_BILANCIO
from ..fetch import fetch
from ..tidy import fmt, to_number, write_csv

# (codice territorio, anno) -> indicatore -> valore
Totali = dict[tuple[str, str], dict[str, float]]

# Le colonne di flusso, sommate sui dodici mesi veri. I saldi che la fonte
# pubblica accanto (`Saldo naturale`, `Saldo migratorio interno`, …) non si
# riportano: sono differenze fra queste colonne, e una tabella che porta sia gli
# addendi sia la somma ha due verità appena una delle due si sbaglia a leggere.
FLUSSI = {
    "Nati vivi": "nati",
    "Morti": "morti",
    "Immigrati da altro comune": "immigrati_interni",
    "Emigrati per altro comune": "emigrati_interni",
    "Immigrati dall'estero": "immigrati_estero",
    "Emigrati per l'estero": "emigrati_estero",
    "Unità in più/meno dovute a variazioni territoriali": "variazioni_territoriali",
}

# Il verso con cui ogni flusso entra nell'identità contabile.
SEGNI = {
    "nati": +1, "morti": -1,
    "immigrati_interni": +1, "emigrati_interni": -1,
    "immigrati_estero": +1, "emigrati_estero": -1,
    "variazioni_territoriali": +1,
    "aggiustamento_statistico": +1,
}

MESE_AGGIUSTAMENTO = 13
MESE_CENSIMENTO = 15
SESSO_TOTALE = "Totale"

COLONNA_POP_INIZIO = "Popolazione inizio periodo"
COLONNA_POP_FINE = "Popolazione fine periodo"

INDICATORI = [
    "popolazione_inizio",
    *FLUSSI.values(),
    "popolazione_fine",
    "aggiustamento_statistico",
    "popolazione_censita",
]

COLUMNS = ["codice_istat", "comune", "anno", "indicatore", "valore"]
COLUMNS_PROVINCE = ["codice_provincia", "provincia", "regione", "anno", "indicatore", "valore"]


# --- gli anni disponibili -----------------------------------------------


def anni_disponibili(html: str) -> list[int]:
    """Gli anni pubblicati, letti dalla pagina indice della tavola.

    Si leggono invece di scriverli in una costante perché una costante invecchia
    in silenzio: l'anno dopo la pipeline continua a girare e produce una tabella
    ferma, senza che niente fallisca. Qui un anno nuovo entra da solo, e una
    pagina che non ne contiene nessuno è un errore — non una lista vuota che
    scriverebbe una tabella vuota.
    """
    anni = sorted({int(a) for a in re.findall(r"D7B(\d{4})\.csv\.zip", html)})
    tenuti = [a for a in anni if a >= PRIMO_ANNO_BILANCIO]
    if not tenuti:
        raise RuntimeError(
            f"nessun anno >= {PRIMO_ANNO_BILANCIO} in {BILANCIO_ANNI_URL}: "
            "la pagina è cambiata o la fonte è in manutenzione"
        )
    return tenuti


# --- lettura -------------------------------------------------------------


def leggi_csv(contenuto: bytes) -> Iterator[dict[str, str]]:
    """Le righe del CSV annuale. Separatore `;`, UTF-8 (non latin-1: è l'altro
    file ISTAT, l'elenco dei comuni, a esserlo)."""
    testo = contenuto.decode("utf-8")
    yield from csv.DictReader(io.StringIO(testo), delimiter=";")


def leggi_zip(path: Path) -> Iterator[dict[str, str]]:
    with zipfile.ZipFile(path) as archive:
        nomi = [n for n in archive.namelist() if n.lower().endswith(".csv")]
        if len(nomi) != 1:
            raise RuntimeError(f"{path.name}: attesi un CSV, trovati {nomi}")
        yield from leggi_csv(archive.read(nomi[0]))


def _valore(riga: dict[str, str], colonna: str) -> float:
    return to_number(riga.get(colonna)) or 0.0


def _accumula(totali: Totali, chiave: tuple[str, str], riga: dict[str, str]) -> None:
    mese = int(riga["Mese"])
    conti = totali.setdefault(chiave, defaultdict(float))

    if mese == MESE_AGGIUSTAMENTO:
        conti["aggiustamento_statistico"] += _valore(riga, COLONNA_POP_FINE)
        return
    if mese == MESE_CENSIMENTO:
        conti["popolazione_censita"] += _valore(riga, COLONNA_POP_FINE)
        return

    for colonna, nome in FLUSSI.items():
        conti[nome] += _valore(riga, colonna)
    if mese == 1:
        conti["popolazione_inizio"] += _valore(riga, COLONNA_POP_INIZIO)
    conti["popolazione_fine"] = _valore(riga, COLONNA_POP_FINE)


def aggrega(righe: Iterable[dict[str, str]]) -> Totali:
    """I dodici mesi sommati in un anno, per **comune**.

    Tiene solo le righe `Sesso = Totale` (trappola 1) e i codici comune a sei
    cifre (trappola 2): gli aggregati territoriali della fonte hanno il codice
    vuoto e vanno letti con `controllo_province`, non sommati insieme ai comuni.
    """
    totali: Totali = {}
    for riga in righe:
        if riga.get("Sesso") != SESSO_TOTALE:
            continue
        codice = (riga.get("Codice comune") or "").strip()
        if len(codice) != 6:
            continue
        _accumula(totali, (codice, riga["Anno"]), riga)
    return totali


def controllo_province(righe: Iterable[dict[str, str]]) -> Totali:
    """Gli aggregati provinciali **pubblicati dalla fonte**, per confronto.

    Sono le righe con il codice comune vuoto e il codice provincia valorizzato.
    Non entrano nella tabella: servono a verificare che la somma dei comuni
    torni, che è il controllo più economico che questa fonte offra.
    """
    totali: Totali = {}
    for riga in righe:
        if riga.get("Sesso") != SESSO_TOTALE:
            continue
        if (riga.get("Codice comune") or "").strip():
            continue
        provincia = (riga.get("Codice provincia") or "").strip()
        if not provincia:
            continue  # l'aggregato nazionale
        _accumula(totali, (provincia, riga["Anno"]), riga)
    return totali


def nomi_province(righe: Iterable[dict[str, str]]) -> dict[str, tuple[str, str]]:
    """`codice provincia -> (provincia, regione)`, presi dalla fonte stessa.

    La provenienza viaggia con il dato: i nomi arrivano dallo stesso file dei
    numeri invece che da un secondo scarico da riallineare.
    """
    nomi: dict[str, tuple[str, str]] = {}
    for riga in righe:
        codice = (riga.get("Codice provincia") or "").strip()
        if codice:
            nomi.setdefault(codice, (riga.get("Provincia", ""), riga.get("Regione", "")))
    return nomi


# --- i controlli ---------------------------------------------------------


TOLLERANZA = 0.5  # sono conteggi di persone: la somma è esatta o è rotta


def verifica_identita(totali: Totali) -> None:
    """Popolazione iniziale + flussi + aggiustamento = popolazione censita.

    Se non torna, la decomposizione non è una decomposizione: c'è un residuo che
    andrebbe attribuito a qualcosa, e attribuirlo in silenzio è il modo in cui si
    pubblica una spiegazione sbagliata. Meglio un build fallito.
    """
    scarti = []
    for (codice, anno), conti in sorted(totali.items()):
        atteso = conti.get("popolazione_censita")
        if atteso is None or "popolazione_inizio" not in conti:
            continue
        ricostruito = conti["popolazione_inizio"] + sum(
            segno * conti.get(nome, 0.0) for nome, segno in SEGNI.items()
        )
        if abs(ricostruito - atteso) > TOLLERANZA:
            scarti.append(f"{codice}/{anno}: ricostruito {ricostruito:.0f}, censito {atteso:.0f}")
    if scarti:
        raise RuntimeError(
            "l'identità del bilancio non chiude su "
            f"{len(scarti)} casi: {'; '.join(scarti[:5])}"
        )


def verifica_province(somma: Totali, controllo: Totali) -> None:
    """La somma dei comuni contro gli aggregati che la fonte pubblica."""
    scarti = []
    for chiave, atteso in sorted(controllo.items()):
        calcolato = somma.get(chiave)
        if calcolato is None:
            scarti.append(f"{chiave[0]}/{chiave[1]}: nessun comune sommato")
            continue
        for indicatore, valore in atteso.items():
            if abs(calcolato.get(indicatore, 0.0) - valore) > TOLLERANZA:
                scarti.append(
                    f"{chiave[0]}/{chiave[1]} {indicatore}: "
                    f"somma {calcolato.get(indicatore, 0.0):.0f}, fonte {valore:.0f}"
                )
    if scarti:
        raise RuntimeError(
            f"la somma dei comuni non torna con gli aggregati della fonte su "
            f"{len(scarti)} casi: {'; '.join(scarti[:5])}"
        )


# --- aggregazione provinciale --------------------------------------------


def per_provincia(totali: Totali) -> Totali:
    """Somma i comuni per provincia: le prime tre cifre del codice ISTAT."""
    fuori: Totali = {}
    for (codice, anno), conti in totali.items():
        destinazione = fuori.setdefault((codice[:3], anno), defaultdict(float))
        for indicatore, valore in conti.items():
            destinazione[indicatore] += valore
    return fuori


# --- build ---------------------------------------------------------------


def _righe_tabella(
    totali: Totali,
    etichette: dict[str, tuple[str, ...]],
    chiavi: tuple[str, ...],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for (codice, anno), conti in totali.items():
        for indicatore in INDICATORI:
            if indicatore not in conti:
                continue
            riga = dict(zip(chiavi, (codice, *etichette[codice])))
            riga.update({"anno": anno, "indicatore": indicatore, "valore": fmt(conti[indicatore])})
            rows.append(riga)
    rows.sort(key=lambda r: (r[chiavi[0]], r["indicatore"], r["anno"]))
    return rows


def build(comuni: dict[str, str]) -> None:
    pagina = fetch(BILANCIO_ANNI_URL, "istat_bilancio_d7b_indice.html", force=True)
    anni = anni_disponibili(pagina.read_text(encoding="utf-8", errors="replace"))
    print(f"  anni pubblicati: {anni[0]}-{anni[-1]}")

    totali: Totali = {}
    controllo: Totali = {}
    etichette_province: dict[str, tuple[str, str]] = {}

    for anno in anni:
        path = fetch(BILANCIO_FILE_URL.format(anno=anno), f"istat_bilancio_d7b_{anno}.zip")
        righe = list(leggi_zip(path))
        totali.update(aggrega(righe))
        controllo.update(controllo_province(righe))
        etichette_province.update(nomi_province(righe))

    verifica_identita(totali)
    province = per_provincia(totali)
    verifica_province(province, controllo)

    orfani = {c for c, _ in totali if c.startswith(comuni_prefisso(comuni))} - set(comuni)
    if orfani:
        raise RuntimeError(f"comuni bresciani non in anagrafica: {sorted(orfani)}")

    del_provincia = {k: v for k, v in totali.items() if k[0] in comuni}
    write_csv(
        "bilancio_demografico_comuni.csv",
        _righe_tabella(
            del_provincia,
            {codice: (nome,) for codice, nome in comuni.items()},
            ("codice_istat", "comune"),
        ),
        COLUMNS,
    )

    write_csv(
        "bilancio_province.csv",
        _righe_tabella(province, etichette_province, ("codice_provincia", "provincia", "regione")),
        COLUMNS_PROVINCE,
    )


def comuni_prefisso(comuni: dict[str, str]) -> str:
    """Le tre cifre della provincia, ricavate dall'anagrafica invece che scritte
    a mano: se un giorno il soggetto cambia, questo modulo segue."""
    prefissi = {codice[:3] for codice in comuni}
    if len(prefissi) != 1:
        raise RuntimeError(f"attesa una sola provincia in anagrafica, trovate {sorted(prefissi)}")
    return prefissi.pop()
