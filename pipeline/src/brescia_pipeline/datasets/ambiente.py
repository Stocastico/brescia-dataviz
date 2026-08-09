"""Qualità dell'aria e clima dalle reti ARPA Lombardia.

Le serie orarie grezze sono enormi (decine di milioni di righe per finestra
storica), quindi non si scaricano: si chiede a Socrata di aggregarle
server-side per sensore e mese. Restano medie mensili — la granularità giusta
per raccontare trent'anni, e l'unica sostenibile da versionare.
"""

from __future__ import annotations

from ..config import SIGLA_PROVINCIA
from ..fetch import socrata_json
from ..tidy import fmt, read_socrata, to_number, write_csv

ANAGRAFICA_ARIA = "ib47-atvt"
ANAGRAFICA_METEO = "nf78-nj6b"

# Le misure sono spezzate per finestra temporale: ogni dataset e' un pezzo
# della stessa serie.
SERIE_ARIA = {
    "2000-2009": "cthp-zqrr",
    "2010-2017": "nr8w-tj77",
    "dal-2018": "g2hp-ar79",
}
SERIE_METEO = {
    "fino-2010": "6eu4-4tja",
    "2011-2020": "d4kj-kbpj",
    "dal-2021": "w9wd-u6jh",
}

STAZIONI_COLUMNS = [
    "id_sensore", "id_stazione", "stazione", "comune", "parametro", "unita_misura",
    "quota", "lat", "lng", "data_inizio", "data_fine",
]
MISURE_COLUMNS = ["id_sensore", "stazione", "parametro", "mese", "media", "n_misure"]

# ARPA marca i dati non validi con -9999: sommarli falserebbe ogni media.
VALIDO = "valore > -100"


def _stazioni_aria() -> list[dict[str, str]]:
    records = read_socrata(
        socrata_json(
            ANAGRAFICA_ARIA,
            dest_name="arpa_stazioni_aria_bs.json",
            where=f"provincia='{SIGLA_PROVINCIA}'",
        )
    )
    return [
        {
            "id_sensore": str(r.get("idsensore", "")),
            "id_stazione": str(r.get("idstazione", "")),
            "stazione": r.get("nomestazione", ""),
            "comune": r.get("comune", ""),
            "parametro": r.get("nometiposensore", ""),
            "unita_misura": r.get("unitamisura", ""),
            "quota": fmt(to_number(r.get("quota"))),
            "lat": r.get("lat", ""),
            "lng": r.get("lng", ""),
            "data_inizio": str(r.get("datastart", ""))[:10],
            "data_fine": str(r.get("datastop", ""))[:10],
        }
        for r in records
    ]


def _stazioni_meteo() -> list[dict[str, str]]:
    # L'anagrafica meteo non ha il campo `comune`: si filtra per provincia.
    records = read_socrata(
        socrata_json(
            ANAGRAFICA_METEO,
            dest_name="arpa_stazioni_meteo_bs.json",
            where=f"provincia='{SIGLA_PROVINCIA}'",
        )
    )
    return [
        {
            "id_sensore": str(r.get("idsensore", "")),
            "id_stazione": str(r.get("idstazione", "")),
            "stazione": r.get("nomestazione", ""),
            "comune": "",
            "parametro": r.get("tipologia", ""),
            "unita_misura": r.get("unit_dimisura", ""),
            "quota": fmt(to_number(r.get("quota"))),
            "lat": r.get("lat", ""),
            "lng": r.get("lng", ""),
            "data_inizio": str(r.get("datastart", ""))[:10],
            "data_fine": str(r.get("datastop", ""))[:10],
        }
        for r in records
    ]


def _medie_mensili(
    resource: str, sensori: list[dict[str, str]], etichetta: str
) -> list[dict[str, str]]:
    """Chiede a Socrata la media mensile per sensore, senza scaricare le orarie."""
    per_id = {s["id_sensore"]: s for s in sensori}
    if not per_id:
        return []

    rows: list[dict[str, str]] = []
    ids = sorted(per_id)
    # Un `IN (...)` con troppi elementi allunga l'URL fino al rifiuto: si va a
    # blocchi, come per le chiavi SDMX multi-comune.
    for start in range(0, len(ids), 20):
        blocco = ids[start : start + 20]
        elenco = ",".join(f"'{i}'" for i in blocco)
        path = socrata_json(
            resource,
            dest_name=f"arpa_{etichetta}_{resource}_{start:03d}.json",
            select="idsensore, date_trunc_ym(data) AS mese, avg(valore) AS media, count(*) AS n",
            where=f"idsensore IN ({elenco}) AND {VALIDO}",
            group="idsensore, date_trunc_ym(data)",
            limit=200_000,
        )
        for record in read_socrata(path):
            sensore = str(record.get("idsensore", ""))
            info = per_id.get(sensore)
            media = to_number(record.get("media"))
            if info is None or media is None:
                continue
            rows.append(
                {
                    "id_sensore": sensore,
                    "stazione": info["stazione"],
                    "parametro": info["parametro"],
                    "mese": str(record.get("mese", ""))[:7],
                    "media": fmt(media, 2),
                    "n_misure": fmt(to_number(record.get("n"))),
                }
            )
    return rows


def build(comuni: dict[str, str]) -> None:
    aria = _stazioni_aria()
    meteo = _stazioni_meteo()
    write_csv("stazioni_arpa.csv", aria + meteo, STAZIONI_COLUMNS)

    misure_aria: list[dict[str, str]] = []
    for etichetta, resource in SERIE_ARIA.items():
        misure_aria += _medie_mensili(resource, aria, f"aria_{etichetta}")
    misure_aria.sort(key=lambda r: (r["id_sensore"], r["mese"]))
    write_csv("aria_mensile.csv", misure_aria, MISURE_COLUMNS)

    misure_meteo: list[dict[str, str]] = []
    for etichetta, resource in SERIE_METEO.items():
        misure_meteo += _medie_mensili(resource, meteo, f"meteo_{etichetta}")
    misure_meteo.sort(key=lambda r: (r["id_sensore"], r["mese"]))
    write_csv("meteo_mensile.csv", misure_meteo, MISURE_COLUMNS)
