"""Volumi di compravendita (NTN) per provincia e capoluogo, trimestrali dal 2011.

Il terzo pezzo della fornitura OMI, e l'unico che **non passa da un login**:
[`omi.py`](omi.py) legge le quotazioni e [`compravendite.py`](compravendite.py)
il dettaglio comunale annuale, entrambi da archivi scaricati a mano e versionati
in `dati/input/omi/`. Qui la pagina pubblica *Volumi di compravendita*
distribuisce gli stessi numeri a grana **provinciale**, ma trimestrale e con il
capoluogo separato dal resto della provincia: è la serie più lunga e più fitta
che il progetto abbia sulla casa, e si scarica senza chiedere niente a nessuno.

Cosa costa sapere prima, in ordine di quanto fa male.

**1. La chiave è la sigla automobilistica, e non è una chiave.** La fornitura
scrive `BS`, non `017`. `province.py` lo dice da sempre — «la sigla non è una
chiave stabile e non esiste per tutti gli enti» — e qui la profezia si avvera
due volte: la fornitura usa ancora `FO` e `PS`, cioè Forlì e Pesaro, sigle che
l'elenco ISTAT non ha più da quando quelle province si chiamano Forlì-Cesena e
Pesaro e Urbino. Sono **due rinomine**, non due territori diversi, e stanno in
`SIGLE_STORICHE` invece che in un `if`. Una sigla che non si traduce ferma il
build: una provincia che sparisce in silenzio è peggio di un errore.

**2. Le province sono 99, non 107.** Mancano le quattro del sistema tavolare
(Bolzano, Trento, Gorizia, Trieste) e le quattro nate dopo il 2004, che qui
restano dentro la provincia madre: **Monza e Brianza è dentro Milano**, Fermo
dentro Ascoli, Barletta-Andria-Trani dentro Bari, Sud Sardegna dentro Cagliari.
Per un confronto lombardo la prima conta: «Milano» qui è Milano più Monza, e non
è la Milano delle altre tabelle del progetto.

**3. `cap` non è un comune.** È il capoluogo contro **tutto il resto** della
provincia, due righe che sommate danno la provincia. Tenerne una sola e chiamarla
«la provincia» è l'errore che questa colonna esiste per rendere impossibile.

**4. Definitivo e provvisorio non sono la stessa cifra.** La serie chiusa arriva
al 2024, i trimestri successivi sono provvisori e vengono ricalcolati. Finiscono
nella stessa tabella perché una serie spezzata in due file è peggio, ma con
`stato` accanto: incollare le due misure in un grafico dev'essere una scelta,
non una svista (MET-17).

**5. Nei provvisori le colonne sono due misure.** Accanto a
`2025_1_PROVV_NTN` c'è `2025_1_PROVV_SUP_NORM`, che sono **metri quadri**.
Leggere tutte le colonne che cominciano con un anno mescolerebbe superfici e
transazioni nella stessa colonna `ntn`, con numeri cento volte più grandi che
sembrano solo un anno buono.

**Il controllo che questa tabella permette, e il suo risultato.** Sommando
`capoluogo` + `resto_provincia` sul residenziale totale si ottiene la provincia,
che è la stessa cosa che dà `compravendite_comuni.csv` sommando i 203 comuni.
Sono **due forniture diverse dello stesso ente**, e sul **definitivo** — dal
2013 al 2024 — coincidono entro lo **0,05 %**, che è quanto ci si aspetta da un
arrotondamento; il provvisorio 2025 ci sta dentro anche lui, purché confrontato
col 2025 dell'altra fornitura, che è provvisorio a sua volta. Mescolare i due
`stato` dà uno scarto del 100 %, ed è l'errore che `verifica_cifre.py` ha preso
il giorno stesso in cui questa tabella è nata. Il 2011 e il 2012 no: la serie provinciale sta **1,3 % e 1,7 % più in alto**. Non è
copertura mancante (il conteggio dei comuni è 203 in tutti gli anni, costante):
è una **revisione** che ha toccato una fornitura e non l'altra. Resta dichiarata
qui e in `FONTI.md`, non aggiustata — una cifra che si corregge a mano è una
cifra di cui nessuno conosce più la storia, ed è lo stesso trattamento che il
progetto ha dato allo scarto fra le due fonti turistiche.

**Cosa resta fuori, e perché.** `RES_SUP.csv` e `RES_CLASSI_SUP.csv` (superficie
e classi di superficie) esistono **solo dal 2023**: due anni non sono una serie,
e questa tabella è qui per la lunghezza. Il non residenziale — ventuno file fra
uffici, negozi, capannoni e categorie catastali — non entra finché non c'è una
storia che lo usa: sarebbe una tabella di trecentomila righe che nessuno guarda.
Aggiungerlo è aggiungere due voci a `SEGMENTI` e l'archivio in `link_archivi`.

Obbligo di citazione: «Agenzia Entrate - OMI».
"""

from __future__ import annotations

import csv
import io
import re
import zipfile
from pathlib import Path
from urllib.parse import urlsplit

from ..config import ELENCO_COMUNI_URL
from ..fetch import fetch
from ..tidy import fmt, to_number, write_csv

PAGINA_VOLUMI = (
    "https://www.agenziaentrate.gov.it/portale/schede/fabbricatiterreni/omi/"
    "banche-dati/volumi-di-compravendita"
)

COLUMNS = [
    "codice_provincia", "provincia", "regione", "ambito",
    "anno", "trimestre", "comparto", "segmento", "ntn", "stato",
]

# I due archivi che servono, e il modo di riconoscerli in una pagina che non
# porta id stabili. Lo `/` davanti a `RESIDENZIALE_` non è ornamentale: senza,
# la stessa espressione prende anche `NON_RESIDENZIALE_…`.
ARCHIVI = {
    "definitivo": re.compile(r'href="([^"]*/RESIDENZIALE_DEFINITIVO_\d{4}_\d{4}\.zip/[^"]*)"'),
    "provvisorio": re.compile(r'href="([^"]*/RESIDENZIALE_\d{4}_\d{4}_PROVV\.zip/[^"]*)"'),
}

# Un file per segmento, dentro ogni archivio. Le etichette sono le stesse di
# `compravendite.py`: due tabelle sullo stesso fenomeno che chiamano `box` due
# cose con due nomi diversi sono due tabelle che non si confrontano.
SEGMENTI = {
    "RES.csv": ("residenziale", "totale"),
    "PER_BOX.csv": ("pertinenze", "box"),
    "PER_DEPOSITI.csv": ("pertinenze", "depositi_pertinenziali"),
}

AMBITI = {"cap": "capoluogo", "noncap": "resto_provincia"}

# Le sigle che la fornitura non ha mai aggiornato. Sono **rinomine**, verificate
# una per una: stesso territorio, nome nuovo. Non è un crosswalk fra perimetri
# diversi — quello sarebbe il caso pericoloso di §9 di `PROSSIMI-PASSI.md`.
SIGLE_STORICHE = {"FO": "FC", "PS": "PU"}

# `2011_1` nel definitivo, `2025_1_PROVV_NTN` nel provvisorio. La coda è quella
# che separa le transazioni dai metri quadri: `_SUP_NORM` non è un NTN.
PERIODO = re.compile(r"^(\d{4})_([1-4])(?:_PROVV)?(?:_(NTN|SUP_NORM))?$", re.IGNORECASE)


def periodo(colonna: str) -> tuple[str, str] | None:
    """`2011_1` -> `("2011", "1")`; una colonna di superficie -> `None`."""
    trovato = PERIODO.match((colonna or "").strip())
    if not trovato or (trovato.group(3) or "NTN").upper() != "NTN":
        return None
    return trovato.group(1), trovato.group(2)


def link_archivi(html: str) -> dict[str, str]:
    """Gli URL dei due archivi, letti dalla pagina.

    Non sono scrivibili in una costante: portano un UUID e un `?t=` che cambiano
    a ogni ripubblicazione, e il nome porta gli anni. Una costante qui è una
    pipeline che un giorno scarica un 404 o, peggio, resta ferma su una
    fornitura vecchia senza che niente fallisca — è la lezione di
    `bilancio.anni_disponibili`.
    """
    fuori: dict[str, str] = {}
    for stato, espressione in ARCHIVI.items():
        trovati = sorted(set(espressione.findall(html)))
        if not trovati:
            raise RuntimeError(
                f"nessun archivio {stato} in {PAGINA_VOLUMI}: la pagina è "
                "cambiata o la fonte è in manutenzione"
            )
        if len(trovati) > 1:
            raise RuntimeError(
                f"{len(trovati)} archivi {stato} nella pagina: "
                f"{[nome_in_cache(t) for t in trovati]}. Quale sia quello buono "
                "va deciso guardando, non indovinando"
            )
        fuori[stato] = trovati[0]
    return fuori


def nome_in_cache(url: str) -> str:
    """`…/RESIDENZIALE_DEFINITIVO_2011_2024.zip/bb?t=2` -> il nome in `raw/`.

    Il nome del file porta gli anni della fornitura, quindi una fornitura nuova
    non riusa per sbaglio la cache di quella vecchia.
    """
    pezzi = [p for p in urlsplit(url).path.split("/") if p.lower().endswith(".zip")]
    if not pezzi:
        raise RuntimeError(f"l'URL non porta un nome di archivio: {url}")
    return f"omi_ntn_{pezzi[-1]}"


def scarica_archivi() -> dict[str, Path]:
    """I due archivi in `dati/raw/`, scaricati o riletti dalla cache."""
    pagina = fetch(PAGINA_VOLUMI, "agenzia_volumi_compravendita.html", force=True)
    link = link_archivi(pagina.read_bytes().decode("utf-8", errors="replace"))
    return {stato: fetch(url, nome_in_cache(url)) for stato, url in link.items()}


def province_per_sigla() -> dict[str, tuple[str, str, str]]:
    """`sigla -> (codice provincia, nome, regione)`, dall'elenco ISTAT.

    Il codice è quello del comune troncato a tre cifre, come in `province.py`:
    è la stessa chiave con cui il resto del progetto scrive le province, e le
    due tabelle si incrociano solo se la chiave è la stessa.
    """
    path = fetch(ELENCO_COMUNI_URL, "istat_elenco_comuni.csv")
    reader = csv.reader(io.StringIO(path.read_bytes().decode("latin-1")), delimiter=";")
    next(reader, None)

    fuori: dict[str, tuple[str, str, str]] = {}
    for row in reader:
        if len(row) <= 14:
            continue
        codice, sigla = row[4].strip(), row[14].strip()
        if len(codice) != 6 or not sigla:
            continue
        fuori.setdefault(sigla, (codice[:3], row[11].strip(), row[10].strip()))
    return fuori


def build(comuni: dict[str, str]) -> None:
    del comuni  # tabella nazionale: qui servono tutte le province

    province = province_per_sigla()
    righe: list[dict[str, str]] = []
    ignote: set[str] = set()
    for stato, archivio in scarica_archivi().items():
        nuove, mancanti = _leggi_archivio(archivio, stato, province)
        righe += nuove
        ignote |= mancanti

    if ignote:
        raise RuntimeError(
            f"sigle non tradotte in codice di provincia: {sorted(ignote)}. "
            "Sono province che sparirebbero dalla tabella senza dirlo: "
            "vanno aggiunte a SIGLE_STORICHE dopo aver verificato che siano "
            "rinomine e non territori diversi"
        )
    if not righe:
        raise RuntimeError("nessuna riga letta dagli archivi NTN provinciali")

    righe.sort(key=lambda r: (
        r["codice_provincia"], r["ambito"], r["anno"], r["trimestre"], r["segmento"]
    ))
    write_csv("compravendite_province.csv", righe, COLUMNS)


def _leggi_archivio(
    archivio: Path, stato: str, province: dict[str, tuple[str, str, str]]
) -> tuple[list[dict[str, str]], set[str]]:
    righe: list[dict[str, str]] = []
    ignote: set[str] = set()
    with zipfile.ZipFile(archivio) as zf:
        for nome in sorted(zf.namelist()):
            if nome not in SEGMENTI:
                continue  # superfici e non residenziale: vedi il docstring
            comparto, segmento = SEGMENTI[nome]
            with zf.open(nome) as grezzo:
                testo = io.TextIOWrapper(grezzo, encoding="latin-1", newline="")
                nuove, mancanti = _righe(
                    csv.DictReader(testo, delimiter=";"), province, comparto, segmento, stato
                )
            righe += nuove
            ignote |= mancanti
    if not righe:
        raise RuntimeError(f"{archivio.name}: nessuno dei file attesi {sorted(SEGMENTI)}")
    return righe, ignote


def _righe(
    reader: csv.DictReader,
    province: dict[str, tuple[str, str, str]],
    comparto: str,
    segmento: str,
    stato: str,
) -> tuple[list[dict[str, str]], set[str]]:
    campi = reader.fieldnames or []
    # `prov` nel definitivo, `Prov` nei provvisori: la stessa colonna con due
    # capitalizzazioni, come i `2011_CodCom`/`COD_COM` di `compravendite.py`.
    chiave = _colonna(campi, "prov")
    ambito = _colonna(campi, "cap")
    periodi = {c: p for c in campi if c and (p := periodo(c))}
    if not periodi:
        raise RuntimeError(f"nessuna colonna di periodo fra {campi}")

    righe: list[dict[str, str]] = []
    ignote: set[str] = set()
    for record in reader:
        sigla = (record.get(chiave) or "").strip()
        sigla = SIGLE_STORICHE.get(sigla, sigla)
        if sigla not in province:
            ignote.add(sigla)
            continue
        codice, nome, regione = province[sigla]
        dove = AMBITI.get((record.get(ambito) or "").strip().lower())
        if dove is None:
            raise RuntimeError(f"ambito non riconosciuto: {record.get(ambito)!r}")
        for colonna, (anno, trimestre) in periodi.items():
            valore = to_number(record.get(colonna))
            if valore is None:
                # L'NTN assente non è zero: è un trimestre che la fonte non
                # pubblica per quella provincia.
                continue
            righe.append({
                "codice_provincia": codice,
                "provincia": nome,
                "regione": regione,
                "ambito": dove,
                "anno": anno,
                "trimestre": trimestre,
                "comparto": comparto,
                "segmento": segmento,
                "ntn": fmt(valore, 2),
                "stato": stato,
            })
    return righe, ignote


def _colonna(campi: list[str], atteso: str) -> str:
    trovata = next((c for c in campi if (c or "").strip().lower() == atteso), None)
    if trovata is None:
        raise RuntimeError(f"colonna {atteso!r} non trovata fra {campi}")
    return trovata
