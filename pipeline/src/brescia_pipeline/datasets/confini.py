"""Confini dei 205 comuni: la base geografica di ogni coropletica.

Fonte: ISTAT, limiti amministrativi generalizzati al 1º gennaio 2025. Il file
copre gli 7.896 comuni italiani; qui si tiene la sola provincia di Brescia.

Produce due cose:

- `dati/geo/comuni_brescia.geojson` — la geometria, in gradi WGS84, pronta da
  dare a una mappa. È l'unica geometria di riferimento del progetto
  (`BRIEF.md`, principio «una sola geometria»): la chiave è il codice ISTAT a
  sei cifre, non uno slug inventato.
- `dati/processed/comuni_geometria.csv` — superficie e centroide per comune.
  Serve alle densità (abitanti o addetti per km²) senza dover ricaricare la
  geometria, e rende verificabile il contenuto del GeoJSON con un CSV tidy
  come tutte le altre tabelle.

⚠️ Le coordinate native sono metri UTM 32N, non gradi: vedi `geo.py`.
"""

from __future__ import annotations

import json
import zipfile

from ..config import CONFINI_COMUNI_URL, PROJECT_ROOT, PROVINCIA_BRESCIA_ISTAT
from ..fetch import fetch
from .. import geo
from ..tidy import fmt, write_csv

LAYER = "Com01012025_g/Com01012025_g_WGS84"
GEOJSON_PATH = PROJECT_ROOT / "dati" / "geo" / "comuni_brescia.geojson"

COLUMNS = ["codice_istat", "comune", "area_kmq", "centroide_lon", "centroide_lat"]

# Cinque decimali sono circa un metro: oltre si versionano megabyte di rumore
# su confini che la fonte dichiara già generalizzati.
PRECISIONE = 5


def _leggi_layer() -> tuple[list[dict[str, str]], list[list[geo.Ring]]]:
    path = fetch(CONFINI_COMUNI_URL, "istat_limiti_2025.zip")
    with zipfile.ZipFile(path) as archive:
        attributi = geo.read_dbf(archive.read(f"{LAYER}.dbf"))
        geometrie = list(geo.read_polygons(archive.read(f"{LAYER}.shp")))

    if len(attributi) != len(geometrie):
        raise RuntimeError(
            f"DBF e SHP disallineati: {len(attributi)} record contro {len(geometrie)} geometrie"
        )
    return attributi, geometrie


def _anello_geojson(ring: geo.Ring, inverti: bool) -> list[list[float]]:
    """Anello riproiettato e chiuso, nel verso richiesto da RFC 7946.

    Lo shapefile orienta gli anelli esterni in senso orario; il GeoJSON vuole
    l'opposto (regola della mano destra), quindi il verso si inverte.
    """
    punti = [geo.utm32n_to_wgs84(x, y) for x, y in ring]
    if inverti:
        punti.reverse()
    coords = [[round(lon, PRECISIONE), round(lat, PRECISIONE)] for lon, lat in punti]
    if coords[0] != coords[-1]:
        coords.append(coords[0])
    return coords


def build(comuni: dict[str, str]) -> None:
    attributi, geometrie = _leggi_layer()

    features: list[dict] = []
    misure: list[dict[str, str]] = []
    visti: set[str] = set()

    for record, rings in zip(attributi, geometrie):
        codice = record.get("PRO_COM_T", "").strip()
        if not codice.startswith(PROVINCIA_BRESCIA_ISTAT) or not rings:
            continue

        # L'anagrafica resta la fonte di verità sui nomi: la geometria porta
        # il codice, il nome viene da `comuni.csv`. Un codice che la geometria
        # ha e l'anagrafica no e' un errore, non una riga da scartare in
        # silenzio (PROSSIMI-PASSI §9).
        if codice not in comuni:
            raise RuntimeError(f"{codice} presente nella geometria ma non nell'anagrafica")
        visti.add(codice)

        poligoni = geo.rings_to_polygons(rings)
        area_m2, (cx, cy) = geo.polygon_area_centroid(poligoni)
        lon, lat = geo.utm32n_to_wgs84(cx, cy)

        anelli = [
            [_anello_geojson(anello, inverti=indice == 0) for indice, anello in enumerate(gruppo)]
            for gruppo in poligoni
        ]
        # Un comune con exclave non e' un poligono con un buco: va tenuto come
        # MultiPolygon, altrimenti la mappa lo disegna unito alla terraferma.
        if len(anelli) == 1:
            geometria = {"type": "Polygon", "coordinates": anelli[0]}
        else:
            geometria = {"type": "MultiPolygon", "coordinates": anelli}

        features.append(
            {
                "type": "Feature",
                "id": codice,
                "properties": {
                    "codice_istat": codice,
                    "comune": comuni[codice],
                    "capoluogo": codice == "017029",
                    "area_kmq": round(area_m2 / 1e6, 3),
                },
                "geometry": geometria,
            }
        )
        misure.append(
            {
                "codice_istat": codice,
                "comune": comuni[codice],
                "area_kmq": fmt(area_m2 / 1e6, 3),
                "centroide_lon": fmt(lon, 5),
                "centroide_lat": fmt(lat, 5),
            }
        )

    mancanti = set(comuni) - visti
    if mancanti:
        raise RuntimeError(f"comuni senza geometria: {sorted(mancanti)}")

    features.sort(key=lambda f: f["id"])
    misure.sort(key=lambda r: r["codice_istat"])

    GEOJSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    with GEOJSON_PATH.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(
            {
                "type": "FeatureCollection",
                "name": "comuni_brescia",
                "crs": "EPSG:4326",
                "fonte": "ISTAT — limiti amministrativi generalizzati 01/01/2025",
                "features": features,
            },
            handle,
            ensure_ascii=False,
            separators=(",", ":"),
        )
        handle.write("\n")
    peso = GEOJSON_PATH.stat().st_size
    print(f"  scritto {GEOJSON_PATH.relative_to(PROJECT_ROOT)}: {len(features)} comuni, {peso:,} byte")

    write_csv("comuni_geometria.csv", misure, COLUMNS)
