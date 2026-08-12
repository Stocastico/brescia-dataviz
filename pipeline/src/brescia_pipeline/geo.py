"""Lettura di shapefile e riproiezione, con la sola libreria standard.

Serve per un unico file — i confini comunali generalizzati di ISTAT — e per
questo non vale una dipendenza in più: `pyshp` leggerebbe lo shapefile, ma il
patto del progetto è «stdlib + requests, niente build step», lo stesso che in
`PROSSIMI-PASSI.md` §5 porta a reimplementare k-means invece di installare
scikit-learn. Il formato shapefile è pubblico e stabile dal 1998; quello che
segue ne copre la parte che ci riguarda (poligoni e tabella DBF).

⚠️ I confini ISTAT si chiamano `_WGS84` ma **non sono in gradi**: il `.prj`
dichiara `WGS_1984_UTM_Zone_32N`, cioè metri proiettati (EPSG:32632). Passarli
a una mappa web senza riproiettare disegna la provincia da qualche parte
nell'oceano al largo dell'Africa, e l'errore è silenzioso perché i numeri
restano numeri. `utm32n_to_wgs84` fa la trasformazione inversa.
"""

from __future__ import annotations

import math
import struct
from typing import Iterator

# --- DBF ----------------------------------------------------------------

DBF_HEADER_END = 0x0D


def read_dbf(data: bytes) -> list[dict[str, str]]:
    """Record di un DBF come dizionari di stringhe già ripulite.

    Non converte i numeri: chi chiama sa quali campi gli servono e con quale
    tipo. I nomi ISTAT contengono accenti in UTF-8.
    """
    count, header_len, record_len = struct.unpack("<IHH", data[4:12])

    fields: list[tuple[str, int]] = []
    offset = 32
    while data[offset] != DBF_HEADER_END:
        raw = data[offset : offset + 32]
        name = raw[:11].split(b"\x00")[0].decode("latin-1")
        fields.append((name, raw[16]))
        offset += 32

    rows: list[dict[str, str]] = []
    for index in range(count):
        start = header_len + index * record_len
        record = data[start : start + record_len]
        if not record or record[:1] == b"*":  # record cancellato
            continue
        position = 1  # il primo byte è il flag di cancellazione
        row: dict[str, str] = {}
        for name, length in fields:
            chunk = record[position : position + length]
            try:
                text = chunk.decode("utf-8")
            except UnicodeDecodeError:
                text = chunk.decode("latin-1")
            row[name] = text.strip()
            position += length
        rows.append(row)
    return rows


# --- SHP ----------------------------------------------------------------

Ring = list[tuple[float, float]]

SHAPE_NULL = 0
SHAPE_POLYGON = 5


def read_polygons(data: bytes) -> Iterator[list[Ring]]:
    """Anelli di ogni record poligonale, nell'ordine del file.

    Restituisce una lista di anelli per record, ancora nelle coordinate
    native del file e nell'orientamento dello shapefile (anelli esterni in
    senso orario, isole interne in senso antiorario). Un record nullo dà una
    lista vuota, così la corrispondenza posizionale con il DBF non si rompe.
    """
    offset = 100  # header di file
    end = len(data)
    while offset < end:
        _, content_len = struct.unpack(">ii", data[offset : offset + 8])
        body = offset + 8
        offset = body + content_len * 2  # la lunghezza è in parole da 16 bit

        (shape_type,) = struct.unpack("<i", data[body : body + 4])
        if shape_type == SHAPE_NULL:
            yield []
            continue
        if shape_type != SHAPE_POLYGON:
            raise ValueError(f"tipo di geometria non gestito: {shape_type}")

        num_parts, num_points = struct.unpack("<ii", data[body + 36 : body + 44])
        parts_at = body + 44
        points_at = parts_at + num_parts * 4
        parts = struct.unpack(f"<{num_parts}i", data[parts_at:points_at])
        coords = struct.unpack(f"<{num_points * 2}d", data[points_at : points_at + num_points * 16])

        rings: list[Ring] = []
        bounds = list(parts) + [num_points]
        for start, stop in zip(bounds, bounds[1:]):
            rings.append([(coords[i * 2], coords[i * 2 + 1]) for i in range(start, stop)])
        yield rings


def signed_area(ring: Ring) -> float:
    """Area con segno (formula del laccio). Positiva se antioraria."""
    total = 0.0
    for (x1, y1), (x2, y2) in zip(ring, ring[1:] + ring[:1]):
        total += x1 * y2 - x2 * y1
    return total / 2.0


def rings_to_polygons(rings: list[Ring]) -> list[list[Ring]]:
    """Raggruppa gli anelli in poligoni, separando le isole dai buchi.

    Nello shapefile l'appartenenza non è dichiarata: si deduce dal verso. Un
    anello orario (area negativa) apre un poligono nuovo, uno antiorario è un
    buco del poligono corrente. È la regola dello standard, ed è il motivo per
    cui i comuni con exclave — nel bresciano ce ne sono — non vanno trattati
    come un anello solo.
    """
    polygons: list[list[Ring]] = []
    for ring in rings:
        if len(ring) < 4:  # un anello valido è chiuso: almeno 3 punti + ritorno
            continue
        if signed_area(ring) < 0 or not polygons:
            polygons.append([ring])
        else:
            polygons[-1].append(ring)
    return polygons


# --- Riproiezione UTM 32N -> WGS84 --------------------------------------

_A = 6378137.0  # semiasse maggiore WGS84
_F = 1 / 298.257223563
_K0 = 0.9996
_FALSE_EASTING = 500_000.0
_LON_ORIGIN = math.radians(9.0)  # meridiano centrale della zona 32

_E2 = _F * (2 - _F)
_EP2 = _E2 / (1 - _E2)
_E1 = (1 - math.sqrt(1 - _E2)) / (1 + math.sqrt(1 - _E2))


def utm32n_to_wgs84(easting: float, northing: float) -> tuple[float, float]:
    """Da metri UTM 32N a `(longitudine, latitudine)` in gradi.

    Serie inversa di Snyder, troncata all'ordine che dà l'errore sotto il
    millimetro dentro la zona: molto più della precisione di confini
    generalizzati, e senza dipendenze.
    """
    m = northing / _K0
    mu = m / (_A * (1 - _E2 / 4 - 3 * _E2**2 / 64 - 5 * _E2**3 / 256))

    phi1 = (
        mu
        + (3 * _E1 / 2 - 27 * _E1**3 / 32) * math.sin(2 * mu)
        + (21 * _E1**2 / 16 - 55 * _E1**4 / 32) * math.sin(4 * mu)
        + (151 * _E1**3 / 96) * math.sin(6 * mu)
        + (1097 * _E1**4 / 512) * math.sin(8 * mu)
    )

    sin_phi1, cos_phi1, tan_phi1 = math.sin(phi1), math.cos(phi1), math.tan(phi1)
    c1 = _EP2 * cos_phi1**2
    t1 = tan_phi1**2
    n1 = _A / math.sqrt(1 - _E2 * sin_phi1**2)
    r1 = _A * (1 - _E2) / (1 - _E2 * sin_phi1**2) ** 1.5
    d = (easting - _FALSE_EASTING) / (n1 * _K0)

    lat = phi1 - (n1 * tan_phi1 / r1) * (
        d**2 / 2
        - (5 + 3 * t1 + 10 * c1 - 4 * c1**2 - 9 * _EP2) * d**4 / 24
        + (61 + 90 * t1 + 298 * c1 + 45 * t1**2 - 252 * _EP2 - 3 * c1**2) * d**6 / 720
    )
    lon = _LON_ORIGIN + (
        d
        - (1 + 2 * t1 + c1) * d**3 / 6
        + (5 - 2 * c1 + 28 * t1 - 3 * c1**2 + 8 * _EP2 + 24 * t1**2) * d**5 / 120
    ) / cos_phi1

    return math.degrees(lon), math.degrees(lat)


# --- Misure sulla geometria proiettata ----------------------------------


def polygon_area_centroid(polygons: list[list[Ring]]) -> tuple[float, tuple[float, float]]:
    """Area netta (buchi sottratti) e centroide, in unità della proiezione.

    Si calcolano **prima** di riproiettare: in UTM le coordinate sono metri e
    l'area è una moltiplicazione, mentre in gradi non lo è — un errore comune
    e silenzioso, perché un'area in gradi quadrati resta un numero plausibile.
    """
    # Si sommano le aree *con segno*: gli anelli esterni arrivano orari e i
    # buchi antiorari, quindi i buchi si sottraggono da soli senza doverli
    # riconoscere di nuovo. Il segno complessivo si semplifica nella divisione.
    area_signed = 0.0
    cx = cy = 0.0
    for rings in polygons:
        for ring in rings:
            sx = sy = 0.0
            for (x1, y1), (x2, y2) in zip(ring, ring[1:] + ring[:1]):
                cross = x1 * y2 - x2 * y1
                sx += (x1 + x2) * cross
                sy += (y1 + y2) * cross
            # il centroide dell'anello sarebbe sx/(6A): pesarlo per A per la
            # media fra anelli lascia proprio sx/6, e A non serve calcolarla.
            cx += sx / 6.0
            cy += sy / 6.0
            area_signed += signed_area(ring)

    if area_signed == 0:
        return 0.0, (0.0, 0.0)
    return abs(area_signed), (cx / area_signed, cy / area_signed)
