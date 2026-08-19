"""Assembla il sito statico in `_site/`, con i dati dentro il file.

    python sito/costruisci.py               # -> _site/
    python sito/costruisci.py --uscita /tmp/prova

Tre proprietà, ereditate dal progetto Donostia (`PROSSIMI-PASSI.md` §6.1) e
mantenute qui apposta:

1. **Un solo file HTML autocontenuto.** I dati sono incorporati in una riga
   `window.DATI = {…}`, lo stile e il codice dei grafici sono in linea: nessuna
   `fetch()`, nessuna CDN, nessuna chiave. Il documento si apre da disco, si
   manda per email, si archivia e fra dieci anni funziona ancora.
2. **I grafici sono SVG disegnati a mano in JavaScript.** Sembra masochismo ed è
   il motivo per cui il punto 1 è possibile.
3. **Nessun numero è scritto a mano nel testo.** Ogni cifra del racconto è un
   segnaposto `{{c:nome}}` che questo script calcola dai JSON della pipeline. Se
   un dato cambia, il testo cambia con lui; se un segnaposto non ha un valore, la
   costruzione fallisce invece di pubblicare una frase con un buco. È la regola
   «ogni numero ha uno script dietro» (`BRIEF.md`) applicata al prodotto finale
   invece che ai documenti di lavoro.

Le date non si scrivono a mano per lo stesso motivo: `{{BUILD_DATE}}` viene da
oggi (o da `--data-build`, che il workflow di deploy passa dal commit) e
`{{DATA_DATE}}` dal `manifest.json` scritto dalla pipeline.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import sys
from datetime import date
from pathlib import Path
from typing import Any

RADICE = Path(__file__).resolve().parent.parent
MODELLI = Path(__file__).resolve().parent / "modelli"
DATI_WEB = RADICE / "web" / "src" / "data"
PROCESSED = RADICE / "dati" / "processed"

CAPOLUOGO = "017029"

# Gli indicatori che finiscono nel documento. Tenerli espliciti invece di
# incorporare tutto: il file autocontenuto pesa quanto ci si mette dentro.
METRICHE_USATE = [
    "popolazione",
    "crescita_popolazione",
    "addetti",
    "crescita_addetti",
    "addetti_per_100_abitanti",
    "dimensione_media",
    "quota_micro",
    "reddito_medio",
    "crescita_reddito",
    "presenze_per_abitante",
    "quota_manifattura",
    "quota_alloggio_ristorazione",
]

PAGINE = {
    "racconto.html": "index.html",
    "metodologia.html": "metodologia.html",
    "dati.html": "dati.html",
}


# --- numeri in italiano --------------------------------------------------


def numero_it(valore: float, decimali: int = 0) -> str:
    """1234.5 -> «1.234,5». Il separatore delle migliaia è il punto."""
    testo = f"{valore:,.{decimali}f}"
    return testo.replace(",", "\x00").replace(".", ",").replace("\x00", ".")


def percento_it(valore: float, decimali: int = 1) -> str:
    return f"{numero_it(valore, decimali)} %"


# --- lettura dei JSON della pipeline ------------------------------------


def leggi_metrica(id_metrica: str) -> dict[str, Any] | None:
    path = DATI_WEB / f"metric_{id_metrica}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def valori(metrica: dict[str, Any], periodo: str | None = None) -> dict[str, float]:
    """I valori di un periodo (l'ultimo, se non specificato)."""
    scelto = periodo or metrica["periods"][-1]
    return {
        codice: per_comune[scelto]
        for codice, per_comune in metrica["values"].items()
        if scelto in per_comune and per_comune[scelto] is not None
    }


def mediana(valori_lista: list[float]) -> float:
    ordinati = sorted(valori_lista)
    meta = len(ordinati) // 2
    return ordinati[meta] if len(ordinati) % 2 else (ordinati[meta - 1] + ordinati[meta]) / 2


def pearson(x: list[float], y: list[float]) -> float:
    mx, my = sum(x) / len(x), sum(y) / len(y)
    num = sum((a - mx) * (b - my) for a, b in zip(x, y))
    dx = math.sqrt(sum((a - mx) ** 2 for a in x))
    dy = math.sqrt(sum((b - my) ** 2 for b in y))
    return num / (dx * dy) if dx and dy else 0.0


# --- le cifre del racconto ----------------------------------------------


def cifre(metriche: dict[str, dict[str, Any]], comuni: dict[str, dict[str, str]]) -> dict[str, str]:
    """Ogni numero che compare nel testo, ricalcolato qui.

    Aggiungere una frase con un numero significa aggiungere una voce a questo
    dizionario: è la stessa disciplina di `analysis/verifica_cifre.py`, applicata
    in avanti invece che a posteriori.
    """
    fuori: dict[str, str] = {}

    popolazione = metriche["popolazione"]
    pop_ultimo = valori(popolazione)
    pop_primo = valori(popolazione, popolazione["periods"][0])
    anno_pop_i, anno_pop_f = popolazione["periods"][0], popolazione["periods"][-1]

    fuori["comuni"] = numero_it(len(comuni))
    fuori["anno_pop_iniziale"] = anno_pop_i
    fuori["anno_pop_finale"] = anno_pop_f
    fuori["popolazione_provinciale"] = numero_it(sum(pop_ultimo.values()))
    fuori["popolazione_capoluogo"] = numero_it(pop_ultimo[CAPOLUOGO])
    fuori["quota_capoluogo"] = percento_it(pop_ultimo[CAPOLUOGO] / sum(pop_ultimo.values()) * 100)
    fuori["popolazione_mediana"] = numero_it(mediana(list(pop_ultimo.values())))

    crescita_pop = valori(metriche["crescita_popolazione"])
    in_calo = [c for c, v in crescita_pop.items() if v < 0]
    fuori["comuni_in_calo"] = numero_it(len(in_calo))
    totale_i = sum(pop_primo.values())
    totale_f = sum(pop_ultimo.values())
    durata = int(anno_pop_f) - int(anno_pop_i)
    fuori["crescita_provinciale"] = f"{numero_it(((totale_f / totale_i) ** (1 / durata) - 1) * 100, 2)} %"
    peggiori = sorted(crescita_pop.items(), key=lambda kv: kv[1])[:5]
    fuori["cadute_peggiori"] = ", ".join(comuni[c]["comune"] for c, _ in peggiori)
    fuori["caduta_peggiore_comune"] = comuni[peggiori[0][0]]["comune"]
    fuori["caduta_peggiore_tasso"] = f"{numero_it(peggiori[0][1], 1)} %"

    addetti = metriche["addetti"]
    add_i = valori(addetti, addetti["periods"][0])
    add_f = valori(addetti)
    fuori["anno_asia_iniziale"] = addetti["periods"][0]
    fuori["anno_asia_finale"] = addetti["periods"][-1]
    fuori["addetti_provinciali"] = numero_it(sum(add_f.values()))
    fuori["addetti_guadagnati"] = numero_it(sum(add_f.values()) - sum(add_i.values()))
    fuori["addetti_capoluogo_variazione"] = numero_it(add_f[CAPOLUOGO] - add_i[CAPOLUOGO])
    fuori["quota_addetti_capoluogo"] = percento_it(add_f[CAPOLUOGO] / sum(add_f.values()) * 100)

    micro = valori(metriche["quota_micro"])
    fuori["quota_micro_mediana"] = percento_it(mediana(list(micro.values())))
    fuori["quota_micro_provinciale"] = percento_it(
        sum(add_f[c] * micro[c] / 100 for c in micro) / sum(add_f[c] for c in micro) * 100
    )

    reddito = metriche["reddito_medio"]
    red_i = valori(reddito, reddito["periods"][0])
    red_f = valori(reddito)
    fuori["anno_reddito_iniziale"] = reddito["periods"][0]
    fuori["anno_reddito_finale"] = reddito["periods"][-1]
    fuori["reddito_mediano"] = numero_it(mediana(list(red_f.values())))
    fuori["reddito_minimo"] = numero_it(min(red_f.values()))
    fuori["reddito_massimo"] = numero_it(max(red_f.values()))
    fuori["reddito_rapporto"] = numero_it(max(red_f.values()) / min(red_f.values()), 1)
    rapporto_iniziale = max(red_i.values()) / min(red_i.values())
    fuori["reddito_rapporto_iniziale"] = numero_it(rapporto_iniziale, 1)

    crescita_red = valori(metriche["crescita_reddito"])
    comuni_comuni = [c for c in crescita_red if c in red_i]
    fuori["convergenza_pearson"] = numero_it(
        pearson([red_i[c] for c in comuni_comuni], [crescita_red[c] for c in comuni_comuni]), 2
    )
    fuori["artefatto_pearson"] = numero_it(
        pearson([red_f[c] for c in comuni_comuni], [crescita_red[c] for c in comuni_comuni]), 2
    )
    fuori["crescita_reddito_mediana"] = f"{numero_it(mediana(list(crescita_red.values())), 2)} %"

    intensita = valori(metriche["addetti_per_100_abitanti"])
    ordinata = sorted(intensita.items(), key=lambda kv: kv[1], reverse=True)
    fuori["intensita_massima_comune"] = comuni[ordinata[0][0]]["comune"]
    fuori["intensita_massima"] = numero_it(ordinata[0][1], 1)
    fuori["intensita_seconda_comune"] = comuni[ordinata[1][0]]["comune"]
    fuori["intensita_seconda"] = numero_it(ordinata[1][1], 1)
    fuori["intensita_mediana"] = numero_it(mediana(list(intensita.values())), 1)

    if "quota_manifattura" in metriche:
        manifattura = valori(metriche["quota_manifattura"])
        alloggio = valori(metriche["quota_alloggio_ristorazione"])
        fuori["manifattura_mediana"] = percento_it(mediana(list(manifattura.values())))
        fuori["manifattura_capoluogo"] = percento_it(manifattura[CAPOLUOGO])
        sopra = [c for c, v in manifattura.items() if v >= 50]
        fuori["comuni_manifatturieri"] = numero_it(len(sopra))
        top_alloggio = sorted(alloggio.items(), key=lambda kv: kv[1], reverse=True)[:5]
        fuori["comuni_turistici_top"] = ", ".join(comuni[c]["comune"] for c, _ in top_alloggio)
        comuni_entrambi = [c for c in manifattura if c in alloggio]
        fuori["manifattura_alloggio_pearson"] = numero_it(
            pearson([manifattura[c] for c in comuni_entrambi], [alloggio[c] for c in comuni_entrambi]), 2
        )

    return fuori


# --- assemblaggio --------------------------------------------------------


def geometria_compatta(precisione: int = 4) -> dict[str, Any]:
    """Il GeoJSON con le sole proprietà che servono e le coordinate arrotondate.

    Quattro decimali sono circa undici metri: su una provincia di 4.785 km²
    disegnata larga mille pixel, invisibili. Tolgono un quinto del peso.
    """
    geo = json.loads((DATI_WEB / "comuni.geojson").read_text(encoding="utf-8"))
    features = []
    for feature in geo["features"]:
        anelli = [
            [[round(x, precisione), round(y, precisione)] for x, y in anello]
            for anello in feature["geometry"]["coordinates"]
        ]
        features.append(
            {
                "c": feature["properties"]["codice_istat"],
                "g": anelli,
            }
        )
    return {"comuni": features}


def dati_incorporati(metriche: dict[str, dict[str, Any]], comuni: dict[str, dict[str, str]]) -> dict[str, Any]:
    return {
        "comuni": {
            codice: [riga["comune"], int(riga["capoluogo"])] for codice, riga in sorted(comuni.items())
        },
        "geo": geometria_compatta(),
        "metriche": {
            id_metrica: {
                "label": metrica["label"],
                "unit": metrica["unit"],
                "kind": metrica["kind"],
                "source": metrica["source"],
                "confidence": metrica["confidence"],
                "assumptions": metrica["assumptions"],
                "periods": metrica["periods"],
                "values": metrica["values"],
                "coverage": metrica["coverage"],
            }
            for id_metrica, metrica in metriche.items()
        },
    }


def sostituisci(testo: str, valori_cifre: dict[str, str], comuni_pagina: str) -> str:
    mancanti: list[str] = []

    def rimpiazza(match: re.Match[str]) -> str:
        nome = match.group(1)
        if nome not in valori_cifre:
            mancanti.append(nome)
            return match.group(0)
        return valori_cifre[nome]

    risultato = re.sub(r"\{\{c:([a-z0-9_]+)\}\}", rimpiazza, testo)
    if mancanti:
        raise SystemExit(
            f"{comuni_pagina}: segnaposto senza valore: {', '.join(sorted(set(mancanti)))}.\n"
            "Ogni cifra del racconto deve essere calcolata in costruisci.py, non scritta a mano."
        )
    return risultato


def costruisci(uscita: Path, data_build: str | None) -> int:
    if not (DATI_WEB / "metrics.json").exists():
        print("manca web/src/data/: lanciare `python -m brescia_pipeline.build web`", file=sys.stderr)
        return 1

    import csv

    with (PROCESSED / "comuni.csv").open(encoding="utf-8") as handle:
        comuni = {r["codice_istat"]: r for r in csv.DictReader(handle)}

    metriche = {}
    for id_metrica in METRICHE_USATE:
        metrica = leggi_metrica(id_metrica)
        if metrica is not None:
            metriche[id_metrica] = metrica
    mancanti = [m for m in METRICHE_USATE if m not in metriche]
    if mancanti:
        print(f"  indicatori non ancora costruiti, il sito li salta: {', '.join(mancanti)}")

    manifesto = json.loads((DATI_WEB / "manifest.json").read_text(encoding="utf-8"))
    valori_cifre = cifre(metriche, comuni)

    stile = (MODELLI / "stile.css").read_text(encoding="utf-8")
    grafici = (MODELLI / "grafici.js").read_text(encoding="utf-8")
    dati = json.dumps(dati_incorporati(metriche, comuni), ensure_ascii=False, separators=(",", ":"))

    uscita.mkdir(parents=True, exist_ok=True)
    for modello, destinazione in PAGINE.items():
        sorgente = (MODELLI / modello).read_text(encoding="utf-8")
        pagina = sostituisci(sorgente, valori_cifre, modello)
        pagina = (
            pagina.replace("/*{{STILE}}*/", stile)
            .replace("/*{{GRAFICI}}*/", grafici)
            .replace("/*{{DATI}}*/", f"window.DATI={dati};")
            .replace("{{BUILD_DATE}}", data_build or date.today().isoformat())
            .replace("{{DATA_DATE}}", manifesto["costruito_il"])
            .replace("{{N_INDICATORI}}", str(manifesto["indicatori"]))
            .replace("{{N_TABELLE}}", str(len(manifesto["tabelle"])))
        )
        (uscita / destinazione).write_text(pagina, encoding="utf-8")
        peso = (uscita / destinazione).stat().st_size / 1024
        print(f"  {destinazione:20} {peso:8.0f} KB")

    tabelle = uscita / "dati" / "processed"
    tabelle.mkdir(parents=True, exist_ok=True)
    for csv_path in sorted(PROCESSED.glob("*.csv")):
        shutil.copyfile(csv_path, tabelle / csv_path.name)
    geo_uscita = uscita / "dati" / "geo"
    geo_uscita.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(RADICE / "dati" / "geo" / "comuni_brescia.geojson", geo_uscita / "comuni_brescia.geojson")
    print(f"  {len(list(tabelle.glob('*.csv')))} tabelle CSV copiate in {tabelle.relative_to(uscita)}/")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="costruisci")
    parser.add_argument("--uscita", type=Path, default=RADICE / "_site")
    parser.add_argument("--data-build", help="data da stampare nel sito (default: oggi)")
    args = parser.parse_args(argv)
    return costruisci(args.uscita, args.data_build)


if __name__ == "__main__":
    sys.exit(main())
