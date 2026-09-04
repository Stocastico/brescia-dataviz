"""Quotazioni immobiliari OMI: l'asse «casa e prezzi», in due grane.

Unico dataset del progetto che **non si scarica**: gli archivi dell'Agenzia
delle Entrate stanno dietro SPID, quindi vivono versionati in
`dati/input/omi/quotazioni/` e questo modulo li legge da lì con `zipfile`
(libreria standard, niente 7z, niente estrazione a mano). La provenienza è in
`dati/input/omi/PROVENIENZA.md`, e la citazione «Agenzia Entrate - OMI» è
obbligatoria per chiunque riusi le tabelle prodotte qui.

Due tabelle, perché le due domande hanno grane diverse:

- `quotazioni_zone.csv` — **una riga per record pubblicato** (semestre × zona ×
  tipologia × stato conservativo), come lo manda la fonte. È la grana per
  guardare *dentro* il capoluogo: **23 zone quotate** su 26 censite nel 2025/2,
  che è un dettaglio da quartiere;
- `quotazioni_comuni.csv` — **comune × semestre × tipologia × mercato**, la
  grana che serve a mappe e confronti fra i 205 comuni.

⚠️ Tre trappole della fonte, tutte già viste sui file veri:

1. `Comune_ISTAT` è `3017029`, non `017029`: davanti c'è la cifra della regione.
   Incrociarlo così com'è con le altre tabelle non dà errore, dà zero righe
   (MET-13);
2. **le zone si accorpano nel tempo** — 600 nel 2004/2, 436 nel 2025/2 — e i
   comuni presenti cambiano (206 nel 2004, 203 nel 2025, contro i 205 di oggi),
   perché l'elenco OMI segue il catasto. Una serie per zona su vent'anni non è a
   perimetro costante: `link_zona` permette di verificarlo, non di rimediarvi;
3. **€/m² su superficie lorda e su superficie netta non sono la stessa misura.**
   La fonte lo dice in `Sup_NL_compr` / `Sup_NL_loc`, un carattere per colonna,
   e mediare le due insieme produce un numero che non descrive nessun mercato:
   qui la base è una **dimensione** della tabella aggregata, non una nota a piè
   di pagina.

   Non è un'ipotesi di scuola: **negli affitti la base cambia nel 2025.** Dal
   2004 al 2024 le locazioni della provincia sono quotate su superficie
   **netta** (2.410 record su 2.420 nel 2024), nel 2025 su superficie **lorda**
   (tutti e 2.415). A Brescia città la media passa da 7,6 €/m² al mese nel 2024
   a 7,4 nel 2025 — e siccome la superficie lorda è più grande della netta, quel
   calo è la misura che è cambiata, non il mercato. Chi legge la colonna `media`
   senza guardare `base_superficie` racconta uno scalino inventato. Le
   compravendite, invece, sono su superficie lorda per tutti e 22 i semestri.

Sull'aggregazione comunale, che è l'unico punto dove questo modulo *decide*
qualcosa: si tengono solo i record dello **stato conservativo prevalente**
(`Stato_prev = P`), e la media è la media **non pesata** dei punti medi delle
zone. Non pesata perché non esiste, nei dati OMI, il numero di immobili per
zona: qualunque peso sarebbe inventato. È una media di zone, non di case, e va
detta così ovunque venga citata.
"""

from __future__ import annotations

import csv
import io
import re
import zipfile
from collections import defaultdict
from pathlib import Path

from ..config import INPUT_DIR
from ..tidy import fmt, to_number, write_csv

QUOTAZIONI_DIR = "omi/quotazioni"

# La prima riga dei CSV VALORI non è l'intestazione ma una didascalia:
# «Quotazioni Immobiliari : Valori di Mercato - Semestre 2015/2 - elaborazione
# del 04-SET-26». Il semestre si legge da lì e non dal nome del file, che è
# stato normalizzato a mano (vedi PROVENIENZA.md) e potrebbe mentire.
SEMESTRE = re.compile(r"Semestre\s+(\d{4})/(\d)")

# `Sup_NL_*`: L = superficie lorda, N = netta.
BASI = {"L": "lorda", "N": "netta"}

# I comuni che l'OMI ha censito e che oggi non esistono più, ricondotti al
# comune che ne ha il territorio. Uno solo, e non viene da una lista scaricata
# — la lista ISTAT dei soppressi non è pubblicata a quell'indirizzo — ma dai
# file stessi: PRESTINE (`017154`) compare in dodici semestri, dal 2004/2 al
# 2015/2, e dal 2016/2 sparisce; nello stesso semestre Bienno passa da due zone
# a tre, con un codice zona nuovo (`BS00006062`) al posto dei due di Prestine.
# È la fusione del 2016.
#
# Perché ricondurlo invece di scartarlo: senza la mappa, la serie di Bienno
# cambia territorio a metà — prima del 2016 senza le zone di Prestine, dopo con
# — ed è il modo silenzioso di sbagliare un confronto ventennale. Il
# `link_zona` originale resta nella tabella, quindi la ricostruzione è
# verificabile.
COMUNI_SOPPRESSI = {"017154": "017018"}  # Prestine -> Bienno (2016)

ZONE_COLUMNS = [
    "codice_istat", "comune", "anno", "semestre", "fascia", "zona", "link_zona",
    "tipologia", "stato", "stato_prevalente",
    "vendita_min", "vendita_max", "base_vendita",
    "affitto_min", "affitto_max", "base_affitto",
]

COMUNI_COLUMNS = [
    "codice_istat", "comune", "anno", "semestre", "tipologia", "mercato",
    "base_superficie", "zone", "minimo", "massimo", "media",
]

# Decimali per mercato: le compravendite sono €/m² interi, gli affitti €/m² al
# mese con un decimale. È la precisione della fonte, non una scelta estetica.
DECIMALI = {"vendita": 0, "affitto": 1}


def build(comuni: dict[str, str]) -> None:
    archivi = sorted((INPUT_DIR / QUOTAZIONI_DIR).glob("QI_*.zip"))
    if not archivi:
        raise RuntimeError(
            f"nessun archivio in {INPUT_DIR / QUOTAZIONI_DIR}: "
            "le quotazioni OMI si scaricano a mano, vedi dati/SCARICHI-MANUALI.md §1"
        )

    zone: list[dict[str, str]] = []
    for archivio in archivi:
        zone += _leggi_archivio(archivio, comuni)

    zone.sort(key=lambda r: (r["codice_istat"], r["anno"], r["semestre"], r["zona"],
                             r["tipologia"], r["stato"]))
    write_csv("quotazioni_zone.csv", zone, ZONE_COLUMNS)
    write_csv("quotazioni_comuni.csv", _per_comune(zone), COMUNI_COLUMNS)


def _leggi_archivio(archivio: Path, comuni: dict[str, str]) -> list[dict[str, str]]:
    with zipfile.ZipFile(archivio) as zf:
        nomi = [n for n in zf.namelist() if "VALORI" in n.upper()]
        if not nomi:
            raise RuntimeError(f"{archivio.name}: nessun file VALORI nell'archivio")
        with zf.open(nomi[0]) as grezzo:
            # L'Agenzia manda encoding latino e separatore `;`.
            testo = io.TextIOWrapper(grezzo, encoding="latin-1", newline="")
            didascalia = testo.readline()
            anno, semestre = _semestre(didascalia, archivio)
            return _righe(csv.DictReader(testo, delimiter=";"), comuni, anno, semestre)


def _semestre(didascalia: str, archivio: Path) -> tuple[str, str]:
    trovato = SEMESTRE.search(didascalia)
    if not trovato:
        raise RuntimeError(
            f"{archivio.name}: la prima riga non porta il semestre "
            f"({didascalia.strip()[:80]!r})"
        )
    return trovato.group(1), trovato.group(2)


def _righe(
    reader: csv.DictReader, comuni: dict[str, str], anno: str, semestre: str
) -> list[dict[str, str]]:
    righe: list[dict[str, str]] = []
    ignoti: dict[str, int] = defaultdict(int)
    for record in reader:
        code = _codice_istat(record.get("Comune_ISTAT", ""))
        code = COMUNI_SOPPRESSI.get(code, code)
        if code not in comuni:
            # Una fusione futura arriverebbe esattamente così: un codice che
            # non c'è più. Scartarlo in silenzio è come non averlo mai avuto.
            ignoti[code] += 1
            continue

        vendita = (to_number(record.get("Compr_min")), to_number(record.get("Compr_max")))
        affitto = (to_number(record.get("Loc_min")), to_number(record.get("Loc_max")))
        if all(v is None for v in vendita + affitto):
            # Riga senza nessuna quotazione: la fonte la pubblica comunque, ma
            # un intervallo assente non è un prezzo zero (PROSSIMI-PASSI §9).
            continue

        righe.append({
            "codice_istat": code,
            "comune": comuni[code],
            "anno": anno,
            "semestre": semestre,
            "fascia": (record.get("Fascia") or "").strip(),
            "zona": (record.get("Zona") or "").strip(),
            "link_zona": (record.get("LinkZona") or "").strip(),
            "tipologia": (record.get("Descr_Tipologia") or "").strip(),
            "stato": (record.get("Stato") or "").strip(),
            "stato_prevalente": (record.get("Stato_prev") or "").strip(),
            "vendita_min": fmt(vendita[0]),
            "vendita_max": fmt(vendita[1]),
            "base_vendita": BASI.get((record.get("Sup_NL_compr") or "").strip(), ""),
            "affitto_min": fmt(affitto[0], 1),
            "affitto_max": fmt(affitto[1], 1),
            "base_affitto": BASI.get((record.get("Sup_NL_loc") or "").strip(), ""),
        })

    for code, quante in sorted(ignoti.items()):
        print(
            f"  ⚠️  {anno}/{semestre}: {quante} righe del comune {code}, che non è "
            "fra i 205 di oggi — se è una fusione va aggiunto a COMUNI_SOPPRESSI"
        )
    return righe


def _codice_istat(grezzo: str) -> str:
    """`3017029` -> `017029`: via la cifra della regione, sei cifre con lo zero.

    Sette caratteri: una cifra di regione (1-20) e sei di comune. Le regioni a
    due cifre danno otto caratteri, e la regola resta «gli ultimi sei».
    """
    testo = (grezzo or "").strip()
    return testo[-6:] if len(testo) > 6 else testo


def _per_comune(zone: list[dict[str, str]]) -> list[dict[str, str]]:
    """Aggrega per comune tenendo solo lo stato conservativo prevalente."""
    gruppi: dict[tuple[str, ...], list[tuple[float, float]]] = defaultdict(list)
    nomi: dict[str, str] = {}

    for riga in zone:
        if riga["stato_prevalente"] != "P":
            continue
        nomi[riga["codice_istat"]] = riga["comune"]
        for mercato in ("vendita", "affitto"):
            minimo = to_number(riga[f"{mercato}_min"])
            massimo = to_number(riga[f"{mercato}_max"])
            if minimo is None or massimo is None:
                continue
            chiave = (
                riga["codice_istat"], riga["anno"], riga["semestre"],
                riga["tipologia"], mercato, riga[f"base_{mercato}"],
            )
            gruppi[chiave].append((minimo, massimo))

    righe: list[dict[str, str]] = []
    for chiave in sorted(gruppi):
        code, anno, semestre, tipologia, mercato, base = chiave
        intervalli = gruppi[chiave]
        decimali = DECIMALI[mercato]
        # La media è la media dei punti medi delle zone, senza pesi: nei dati
        # OMI non c'è il numero di immobili per zona.
        media = sum((a + b) / 2 for a, b in intervalli) / len(intervalli)
        righe.append({
            "codice_istat": code,
            "comune": nomi[code],
            "anno": anno,
            "semestre": semestre,
            "tipologia": tipologia,
            "mercato": mercato,
            "base_superficie": base,
            "zone": str(len(intervalli)),
            "minimo": fmt(min(a for a, _ in intervalli), decimali),
            "massimo": fmt(max(b for _, b in intervalli), decimali),
            "media": fmt(media, decimali),
        })
    return righe
