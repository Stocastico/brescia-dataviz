"""Test del lettore di shapefile e della riproiezione.

Girano **senza rete e senza build**: sono geometrie costruite a mano, e servono
proprio perché gli errori di questa parte sono silenziosi. Una riproiezione
sbagliata non solleva eccezioni, disegna la provincia nell'oceano; un verso di
anello sbagliato non rompe il GeoJSON, ci lascia dentro buchi che non esistono.
"""

from __future__ import annotations

import math
import struct

import pytest

from brescia_pipeline import geo

# --- riproiezione -------------------------------------------------------


def test_il_meridiano_centrale_torna_esatto() -> None:
    """A est=500.000 (falso est) la longitudine è quella della zona 32: 9°."""
    lon, _ = geo.utm32n_to_wgs84(500_000.0, 5_043_387.0)
    assert lon == pytest.approx(9.0, abs=1e-9)


def test_origine_della_zona() -> None:
    lon, lat = geo.utm32n_to_wgs84(500_000.0, 0.0)
    assert (lon, lat) == pytest.approx((9.0, 0.0), abs=1e-9)


@pytest.mark.parametrize(
    ("easting", "northing", "lon", "lat"),
    [
        # Punti di controllo con coordinate note nelle due proiezioni.
        (514_815.0, 5_034_533.0, 9.1895, 45.4642),  # Milano, Duomo
        (500_000.0, 4_649_776.0, 9.0000, 42.0000),  # meridiano centrale, 42°N
    ],
)
def test_punti_di_controllo(easting: float, northing: float, lon: float, lat: float) -> None:
    got_lon, got_lat = geo.utm32n_to_wgs84(easting, northing)
    # 1e-3 gradi ~ 100 m: i valori attesi sono arrotondati alla quarta cifra.
    assert got_lon == pytest.approx(lon, abs=1e-3)
    assert got_lat == pytest.approx(lat, abs=1e-3)


def test_la_provincia_cade_dove_deve() -> None:
    """Un punto nel bresciano non deve finire in mezzo al mare.

    È il test che coglie l'errore più grave e più facile: dimenticare la
    riproiezione e passare metri a una mappa che si aspetta gradi.
    """
    lon, lat = geo.utm32n_to_wgs84(603_000.0, 5_043_000.0)
    assert 9.8 < lon < 10.9
    assert 45.2 < lat < 46.4


# --- anelli e poligoni --------------------------------------------------


def quadrato(x: float, y: float, lato: float, antiorario: bool = False) -> geo.Ring:
    punti = [(x, y), (x + lato, y), (x + lato, y + lato), (x, y + lato)]
    # lo shapefile vuole gli anelli esterni in senso orario
    return punti if antiorario else punti[::-1]


def test_area_con_segno_distingue_il_verso() -> None:
    assert geo.signed_area(quadrato(0, 0, 10, antiorario=True)) == pytest.approx(100.0)
    assert geo.signed_area(quadrato(0, 0, 10)) == pytest.approx(-100.0)


def test_un_anello_orario_apre_un_poligono() -> None:
    polygons = geo.rings_to_polygons([quadrato(0, 0, 10)])
    assert len(polygons) == 1 and len(polygons[0]) == 1


def test_due_anelli_orari_sono_due_poligoni() -> None:
    """Un comune con exclave: due isole, non un poligono con un buco."""
    polygons = geo.rings_to_polygons([quadrato(0, 0, 10), quadrato(100, 100, 5)])
    assert [len(p) for p in polygons] == [1, 1]


def test_un_anello_antiorario_e_un_buco() -> None:
    polygons = geo.rings_to_polygons([quadrato(0, 0, 30), quadrato(10, 10, 5, antiorario=True)])
    assert len(polygons) == 1
    assert len(polygons[0]) == 2  # esterno + buco


def test_gli_anelli_degeneri_si_scartano() -> None:
    assert geo.rings_to_polygons([[(0.0, 0.0), (1.0, 1.0)]]) == []


# --- area e centroide ---------------------------------------------------


def test_area_e_centroide_di_un_quadrato() -> None:
    area, (cx, cy) = geo.polygon_area_centroid([[quadrato(0, 0, 10)]])
    assert area == pytest.approx(100.0)
    assert (cx, cy) == pytest.approx((5.0, 5.0))


def test_il_buco_si_sottrae_dall_area() -> None:
    poligono = [[quadrato(0, 0, 10), quadrato(2, 2, 4, antiorario=True)]]
    area, _ = geo.polygon_area_centroid(poligono)
    assert area == pytest.approx(100.0 - 16.0)


def test_il_centroide_di_due_isole_sta_in_mezzo() -> None:
    """Pesato per area: l'isola grande tira il centroide verso di sé."""
    area, (cx, _) = geo.polygon_area_centroid([[quadrato(0, 0, 10)], [quadrato(100, 0, 10)]])
    assert area == pytest.approx(200.0)
    assert cx == pytest.approx(55.0)  # (5*100 + 105*100) / 200


# --- lettura dei file ---------------------------------------------------


def shapefile_di_prova(rings: list[geo.Ring]) -> bytes:
    """Uno .shp minimo con un solo record poligonale."""
    parts, points = [], []
    for ring in rings:
        parts.append(len(points))
        points.extend(ring)

    body = struct.pack("<i", geo.SHAPE_POLYGON)
    body += struct.pack("<4d", 0, 0, 0, 0)
    body += struct.pack("<ii", len(parts), len(points))
    body += struct.pack(f"<{len(parts)}i", *parts)
    for x, y in points:
        body += struct.pack("<2d", x, y)

    header = b"\x00" * 100
    record = struct.pack(">ii", 1, len(body) // 2) + body
    return header + record


def test_lettura_di_un_poligono() -> None:
    ring = quadrato(0, 0, 10)
    (letti,) = list(geo.read_polygons(shapefile_di_prova([ring])))
    assert len(letti) == 1
    assert letti[0] == [(float(x), float(y)) for x, y in ring]


def test_lettura_di_piu_anelli() -> None:
    rings = [quadrato(0, 0, 10), quadrato(50, 50, 4)]
    (letti,) = list(geo.read_polygons(shapefile_di_prova(rings)))
    assert [len(r) for r in letti] == [4, 4]


def test_il_tipo_di_geometria_non_gestito_esplode() -> None:
    """Meglio un'eccezione che una geometria letta a caso."""
    dati = bytearray(shapefile_di_prova([quadrato(0, 0, 10)]))
    dati[108:112] = struct.pack("<i", 3)  # PolyLine
    with pytest.raises(ValueError, match="non gestito"):
        list(geo.read_polygons(bytes(dati)))


def dbf_di_prova(campi: list[tuple[str, int]], record: list[str]) -> bytes:
    header_len = 32 + 32 * len(campi) + 1
    record_len = 1 + sum(length for _, length in campi)
    out = bytearray(b"\x03" + b"\x00" * 3)
    out += struct.pack("<IHH", 1, header_len, record_len)
    out += b"\x00" * 20
    for nome, length in campi:
        campo = bytearray(b"\x00" * 32)
        campo[: len(nome)] = nome.encode("latin-1")
        campo[11] = ord("C")
        campo[16] = length
        out += campo
    out += b"\x0d"
    out += b" "  # flag di cancellazione
    for (_, length), valore in zip(campi, record):
        out += valore.encode("utf-8").ljust(length)[:length]
    return bytes(out)


def test_lettura_dbf_con_accenti() -> None:
    """I nomi ISTAT arrivano in UTF-8: `Agliè`, non `AgliÃ¨`."""
    campi = [("PRO_COM_T", 6), ("COMUNE", 20)]
    righe = geo.read_dbf(dbf_di_prova(campi, ["017029", "Brescia"]))
    assert righe == [{"PRO_COM_T": "017029", "COMUNE": "Brescia"}]

    righe = geo.read_dbf(dbf_di_prova(campi, ["001001", "Agliè"]))
    assert righe[0]["COMUNE"] == "Agliè"


def test_lettura_dbf_taglia_gli_spazi() -> None:
    righe = geo.read_dbf(dbf_di_prova([("COMUNE", 20)], ["Brescia"]))
    assert righe[0]["COMUNE"] == "Brescia"
