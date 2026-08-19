"""Il contratto fra la pipeline e il sito: JSON statico, una forma per tutti.

    python -m brescia_pipeline.build web      # dopo che le tabelle esistono

L'idea, ereditata dal progetto Donostia (`PROSSIMI-PASSI.md` §6.2), è che il
frontend **non conosca le fonti**: legge JSON dalla forma fissa e non ha alcuna
dipendenza a runtime da Python o dalle API di ISTAT. Aggiungere un indicatore
diventa «un JSON in più e una riga nel registro», senza toccare il codice della
mappa.

Cosa viene scritto in `web/src/data/`:

| File | Cosa contiene |
|---|---|
| `metrics.json` | il **registro**: i soli descrittori, così l'interfaccia costruisce il menù senza caricare i dati |
| `metric_<id>.json` | un indicatore: descrittore + `values[codice][periodo]` |
| `comuni.geojson` | la geometria dei 205 comuni, la stessa di `dati/geo/` |
| `manifest.json` | data del build, righe per tabella, elenco delle fonti |

Tre scelte che valgono più di quanto sembri:

- **La chiave è il codice ISTAT**, sempre e ovunque: nessuno slug, nessun join
  per nome (§9 del piano spiega perché è la regola che salva i progetti).
- **`null` significa assente, e non è zero.** Sulle presenze turistiche 2024
  mancano 73 comuni su 205 per tre motivi diversi (soppresso, non riportato,
  zero fittizio): il campo `missing` di ogni indicatore li conta, così
  l'interfaccia può dirlo invece di disegnare un buco.
- **Gli indicatori derivati dichiarano le assunzioni** nel proprio JSON, e
  arrivano fino al tooltip: la provenienza viaggia con il dato.
"""

from __future__ import annotations

import csv
import json
import shutil
from datetime import date
from pathlib import Path
from typing import Any, Callable

from .config import PROCESSED_DIR, PROJECT_ROOT
from .datasets.confini import GEOJSON_PATH
from .tidy import to_number

WEB_DATA_DIR = PROJECT_ROOT / "web" / "src" / "data"

# `values[codice][periodo] = numero | None`
Valori = dict[str, dict[str, float | None]]


# --- lettura delle tabelle ----------------------------------------------


def _leggi(nome: str) -> list[dict[str, str]]:
    path = PROCESSED_DIR / nome
    if not path.exists():
        raise FileNotFoundError(f"manca {nome}: lanciare prima `python -m brescia_pipeline.build`")
    with path.open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _serie(righe: list[dict[str, str]], filtro: Callable[[dict[str, str]], bool],
           colonna: str = "valore") -> Valori:
    valori: Valori = {}
    for riga in righe:
        if not filtro(riga):
            continue
        valori.setdefault(riga["codice_istat"], {})[riga["anno"]] = to_number(riga[colonna])
    return valori


def _rapporto(numeratore: Valori, denominatore: Valori, fattore: float = 1.0) -> Valori:
    """Rapporto anno per anno. Un anno presente da una parte sola non entra:
    mescolare due annate in un rapporto è il modo più facile di sbagliare."""
    risultato: Valori = {}
    for codice, per_anno in numeratore.items():
        for anno, valore in per_anno.items():
            sotto = denominatore.get(codice, {}).get(anno)
            if valore is None or not sotto:
                continue
            risultato.setdefault(codice, {})[anno] = valore / sotto * fattore
    return risultato


def _crescita(serie: Valori, etichetta_periodo: str) -> Valori:
    """Tasso annualizzato composto fra il primo e l'ultimo anno della serie."""
    risultato: Valori = {}
    for codice, per_anno in serie.items():
        anni = sorted(a for a, v in per_anno.items() if v is not None)
        if len(anni) < 2:
            continue
        iniziale, finale = per_anno[anni[0]], per_anno[anni[-1]]
        durata = int(anni[-1]) - int(anni[0])
        if not iniziale or not finale or iniziale <= 0 or finale <= 0 or durata <= 0:
            continue
        risultato[codice] = {etichetta_periodo: ((finale / iniziale) ** (1 / durata) - 1) * 100}
    return risultato


# --- gli indicatori ------------------------------------------------------

FONTE_ASIA = "ISTAT — ASIA, unità locali delle imprese attive"
FONTE_POP = "ISTAT — popolazione residente comunale"
FONTE_MEF = "MEF — dichiarazioni dei redditi delle persone fisiche"
FONTE_TURISMO = "Regione Lombardia — flussi turistici per comune"


def _indicatori() -> list[dict[str, Any]]:
    imprese = _leggi("imprese_classe_addetti.csv")
    popolazione_righe = _leggi("popolazione_comuni.csv")
    redditi = _leggi("redditi_comuni.csv")
    turismo = _leggi("turismo_comuni_annuale.csv")
    geo = {r["codice_istat"]: r for r in _leggi("comuni_geometria.csv")}

    addetti = _serie(imprese, lambda r: r["indicatore"] == "addetti" and r["classe_addetti"] == "totale")
    unita = _serie(imprese, lambda r: r["indicatore"] == "unita_locali" and r["classe_addetti"] == "totale")
    micro = _serie(imprese, lambda r: r["indicatore"] == "addetti" and r["classe_addetti"] == "0-9")
    popolazione = _serie(popolazione_righe, lambda r: r["indicatore"] == "popolazione_residente")

    # Il reddito medio è un rapporto fra due totali, non la media delle medie.
    imponibile: Valori = {}
    contribuenti: Valori = {}
    for riga in redditi:
        valore = to_number(riga["valore"])
        if valore is None:
            continue
        deposito = imponibile if riga["indicatore"].startswith("income") else contribuenti
        anni = deposito.setdefault(riga["codice_istat"], {})
        anni[riga["anno"]] = (anni.get(riga["anno"]) or 0.0) + valore
    reddito = _rapporto(imponibile, contribuenti)

    presenze = _serie(
        turismo,
        lambda r: r["tipo_struttura"] == "Totale"
        and r["cittadinanza"] == "Totale"
        and r["stato"] == "osservato",
        colonna="presenze",
    )

    superficie: Valori = {
        codice: {anno: float(riga["area_kmq"]) for anno in popolazione.get(codice, {})}
        for codice, riga in geo.items()
    }

    return [
        {
            "id": "addetti",
            "label": "Addetti delle unità locali",
            "unit": "addetti",
            "kind": "sequential",
            "theme": "imprese",
            "source": FONTE_ASIA,
            "confidence": "osservato",
            "assumptions": [
                "Unità locali, non imprese: la sede secondaria conta nel comune dove sta",
                "Medie annue, quindi con decimali",
            ],
            "values": addetti,
        },
        {
            "id": "unita_locali",
            "label": "Unità locali attive",
            "unit": "unità locali",
            "kind": "sequential",
            "theme": "imprese",
            "source": FONTE_ASIA,
            "confidence": "osservato",
            "assumptions": ["Unità locali, non imprese"],
            "values": unita,
        },
        {
            "id": "addetti_per_100_abitanti",
            "label": "Addetti ogni 100 abitanti",
            "unit": "addetti/100 ab.",
            "kind": "sequential",
            "theme": "imprese",
            "source": f"{FONTE_ASIA}; {FONTE_POP}",
            "confidence": "derivato",
            "assumptions": [
                "Numeratore e denominatore presi allo stesso anno",
                "Misura dove si lavora, non dove lavorano i residenti: il pendolarismo non è tolto",
            ],
            "values": _rapporto(addetti, popolazione, 100),
        },
        {
            "id": "dimensione_media",
            "label": "Addetti per unità locale",
            "unit": "addetti",
            "kind": "sequential",
            "theme": "imprese",
            "source": FONTE_ASIA,
            "confidence": "derivato",
            "assumptions": ["Media aritmetica, molto sensibile a un solo grande stabilimento"],
            "values": _rapporto(addetti, unita),
        },
        {
            "id": "quota_micro",
            "label": "Quota di addetti in unità sotto i 10",
            "unit": "%",
            "kind": "sequential",
            "theme": "imprese",
            "source": FONTE_ASIA,
            "confidence": "derivato",
            "assumptions": ["Denominatore: il totale degli addetti del comune nello stesso anno"],
            "values": _rapporto(micro, addetti, 100),
        },
        {
            "id": "crescita_addetti",
            "label": "Crescita degli addetti, 2018–2023",
            "unit": "%/anno",
            "kind": "diverging",
            "theme": "imprese",
            "source": FONTE_ASIA,
            "confidence": "derivato",
            "assumptions": [
                "Tasso composto fra il primo e l'ultimo anno: passa sopra la rottura del 2020",
            ],
            "values": _crescita(addetti, "2018–2023"),
        },
        {
            "id": "popolazione",
            "label": "Popolazione residente",
            "unit": "abitanti",
            "kind": "sequential",
            "theme": "popolazione",
            "source": FONTE_POP,
            "confidence": "osservato",
            "assumptions": [],
            "values": popolazione,
        },
        {
            "id": "densita",
            "label": "Densità abitativa",
            "unit": "ab./km²",
            "kind": "sequential",
            "theme": "popolazione",
            "source": f"{FONTE_POP}; ISTAT — confini comunali generalizzati",
            "confidence": "derivato",
            "assumptions": ["Superficie amministrativa, lago compreso dove il confine ci entra"],
            "values": _rapporto(popolazione, superficie),
        },
        {
            "id": "crescita_popolazione",
            "label": "Crescita della popolazione, 2018–2024",
            "unit": "%/anno",
            "kind": "diverging",
            "theme": "popolazione",
            "source": FONTE_POP,
            "confidence": "derivato",
            "assumptions": [
                "Variazione netta: non distingue saldo naturale da migrazione",
            ],
            "values": _crescita(popolazione, "2018–2024"),
        },
        {
            "id": "reddito_medio",
            "label": "Reddito imponibile medio per contribuente",
            "unit": "euro correnti",
            "kind": "sequential",
            "theme": "redditi",
            "source": FONTE_MEF,
            "confidence": "derivato",
            "assumptions": [
                "Somma degli imponibili diviso somma dei contribuenti",
                "Euro correnti: fra il 2012 e il 2023 una parte della crescita è inflazione",
                "Contribuenti, non residenti: chi non dichiara non c'è",
            ],
            "values": reddito,
        },
        {
            "id": "crescita_reddito",
            "label": "Crescita del reddito medio, 2012–2023",
            "unit": "%/anno",
            "kind": "diverging",
            "theme": "redditi",
            "source": FONTE_MEF,
            "confidence": "derivato",
            "assumptions": ["Euro correnti, non deflazionati"],
            "values": _crescita(reddito, "2012–2023"),
        },
        {
            "id": "presenze_turistiche",
            "label": "Presenze turistiche",
            "unit": "presenze",
            "kind": "sequential",
            "theme": "turismo",
            "source": FONTE_TURISMO,
            "confidence": "osservato",
            "assumptions": [
                "Solo i valori osservati: i comuni con dato soppresso restano assenti, non a zero",
            ],
            "values": presenze,
        },
        {
            "id": "presenze_per_abitante",
            "label": "Presenze turistiche per abitante",
            "unit": "presenze/ab.",
            "kind": "sequential",
            "theme": "turismo",
            "source": f"{FONTE_TURISMO}; {FONTE_POP}",
            "confidence": "derivato",
            "assumptions": ["Rapporto fra due anni diversi quando la serie turistica si ferma prima"],
            "values": _rapporto(presenze, popolazione),
        },
    ]


def _sezioni_disponibili() -> list[dict[str, Any]]:
    """Le quote settoriali, se `imprese_sezioni_comuni.csv` è stata costruita.

    Sta a parte perché è la tabella più recente e la più costosa da scaricare:
    il sito deve poter essere costruito anche senza, con gli indicatori
    dichiarati `planned` nel registro invece che rotti.
    """
    if not (PROCESSED_DIR / "imprese_sezioni_comuni.csv").exists():
        return []

    righe = _leggi("imprese_sezioni_comuni.csv")
    imprese = _leggi("imprese_classe_addetti.csv")
    totale = _serie(imprese, lambda r: r["indicatore"] == "addetti" and r["classe_addetti"] == "totale")

    def quota(sezione: str) -> Valori:
        parte = _serie(righe, lambda r: r["indicatore"] == "addetti" and r["sezione"] == sezione)
        return _rapporto(parte, totale, 100)

    nota = (
        "ASIA non copre agricoltura, pubblica amministrazione e servizi domestici: "
        "il denominatore è l'economia osservata dal registro, non tutta l'economia"
    )

    manifattura = quota("C")
    alloggio = quota("I")
    # La differenza fra le due quote: positiva dove il comune è manifatturiero,
    # negativa dove vive di alloggio e ristorazione, attorno a zero dove non è
    # né l'una né l'altra cosa. È l'unico modo di mettere le due economie in
    # una sola immagine senza inventare una scala bivariata.
    specializzazione: Valori = {}
    for codice, per_anno in manifattura.items():
        for anno, valore in per_anno.items():
            altro = alloggio.get(codice, {}).get(anno)
            if valore is None or altro is None:
                continue
            specializzazione.setdefault(codice, {})[anno] = valore - altro

    return [
        {
            "id": "quota_manifattura",
            "label": "Quota di addetti nella manifattura",
            "unit": "%",
            "kind": "sequential",
            "theme": "settori",
            "source": FONTE_ASIA,
            "confidence": "derivato",
            "assumptions": [nota, "Sezione Ateco C"],
            "values": quota("C"),
        },
        {
            "id": "quota_alloggio_ristorazione",
            "label": "Quota di addetti in alloggio e ristorazione",
            "unit": "%",
            "kind": "sequential",
            "theme": "settori",
            "source": FONTE_ASIA,
            "confidence": "derivato",
            "assumptions": [nota, "Sezione Ateco I"],
            "values": quota("I"),
        },
        {
            "id": "specializzazione",
            "label": "Manifattura meno alloggio e ristorazione",
            "unit": "punti percentuali",
            "kind": "diverging",
            "theme": "settori",
            "source": FONTE_ASIA,
            "confidence": "derivato",
            "assumptions": [
                nota,
                "Differenza fra due quote sullo stesso totale: positiva = manifatturiero, negativa = turistico",
                "Un comune vicino a zero può essere equilibrato oppure specializzato in un terzo settore",
            ],
            "values": specializzazione,
        },
        {
            "id": "quota_costruzioni",
            "label": "Quota di addetti nelle costruzioni",
            "unit": "%",
            "kind": "sequential",
            "theme": "settori",
            "source": FONTE_ASIA,
            "confidence": "derivato",
            "assumptions": [nota, "Sezione Ateco F"],
            "values": quota("F"),
        },
    ]


# --- scrittura -----------------------------------------------------------


def _periodi(valori: Valori) -> list[str]:
    return sorted({periodo for per_comune in valori.values() for periodo in per_comune})


def _arrotonda(valore: float | None) -> float | None:
    if valore is None:
        return None
    # Tre decimali bastano a qualunque grafico e dimezzano il peso dei file.
    return round(valore, 3)


def _scrivi_json(path: Path, contenuto: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(contenuto, ensure_ascii=False, sort_keys=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    return path


def build(comuni: dict[str, str]) -> None:
    indicatori = _indicatori() + _sezioni_disponibili()
    registro: list[dict[str, Any]] = []

    for indicatore in indicatori:
        valori = indicatore.pop("values")
        periodi = _periodi(valori)
        completi = {
            codice: {periodo: _arrotonda(per_comune.get(periodo)) for periodo in periodi
                     if per_comune.get(periodo) is not None}
            for codice, per_comune in sorted(valori.items())
        }
        presenti = sum(1 for per_comune in completi.values() for _ in per_comune)
        documento = {
            **indicatore,
            "livello": "comune",
            "periods": periodi,
            "coverage": {
                "comuni": len(completi),
                "attesi": len(comuni),
                "osservazioni": presenti,
                "mancanti": len(comuni) * len(periodi) - presenti,
            },
            "values": completi,
        }
        _scrivi_json(WEB_DATA_DIR / f"metric_{indicatore['id']}.json", documento)
        registro.append(
            {
                "id": indicatore["id"],
                "label": indicatore["label"],
                "unit": indicatore["unit"],
                "kind": indicatore["kind"],
                "theme": indicatore["theme"],
                "livello": "comune",
                "timeGrain": "year",
                "source": indicatore["source"],
                "confidence": indicatore["confidence"],
                "periods": periodi,
                "status": "live",
            }
        )

    _scrivi_json(WEB_DATA_DIR / "metrics.json", registro)

    if GEOJSON_PATH.exists():
        shutil.copyfile(GEOJSON_PATH, WEB_DATA_DIR / "comuni.geojson")

    tabelle = sorted(p.name for p in PROCESSED_DIR.glob("*.csv"))
    _scrivi_json(
        WEB_DATA_DIR / "manifest.json",
        {
            "progetto": "brescia-dataviz",
            "costruito_il": date.today().isoformat(),
            "comuni": len(comuni),
            "indicatori": len(registro),
            "tabelle": tabelle,
            "fonti": sorted({r["source"] for r in registro}),
        },
    )
    print(f"  scritti {len(registro) + 3} file in web/src/data/")
