"""Test del parsing numerico e delle utilità di trasformazione.

`to_number` merita test propri perché il suo modo di sbagliare è silenzioso:
leggere `567,391` come 567,391 restituisce un numero perfettamente plausibile,
sbagliato di tre ordini di grandezza. È già successo una volta.
"""

from __future__ import annotations

import pytest

from brescia_pipeline.tidy import fmt, split_code, to_number


@pytest.mark.parametrize(
    ("raw", "atteso"),
    [
        # Socrata: virgola come separatore di migliaia
        ("1,406,590", 1_406_590.0),
        ("567,391", 567_391.0),
        ("1,234.56", 1234.56),
        # SDMX di ISTAT: numeri nudi
        ("100939.25", 100939.25),
        ("82", 82.0),
        ("3.90", 3.9),
        # formato italiano
        ("1.406.590", 1_406_590.0),
        ("1.234,56", 1234.56),
        ("3,9", 3.9),
        # negativi e spazi
        ("-9999", -9999.0),
        (" 1 234 ", 1234.0),
    ],
)
def test_to_number_riconosce_i_separatori(raw: str, atteso: float) -> None:
    assert to_number(raw) == pytest.approx(atteso)


@pytest.mark.parametrize(
    "raw",
    ["", "  ", "Dato riservato", "n.d.", "..", "-", None, "non un numero"],
)
def test_to_number_restituisce_none_sui_mancanti(raw: str | None) -> None:
    # Mai zero: un comune con «Dato riservato» non e' un comune senza turisti.
    assert to_number(raw) is None


def test_split_code_separa_codice_ed_etichetta() -> None:
    assert split_code("017029: Brescia") == ("017029", "Brescia")
    assert split_code("W_GE250: 250 and over") == ("W_GE250", "250 and over")


def test_split_code_tollera_valori_senza_etichetta() -> None:
    assert split_code("2024") == ("2024", "2024")
    assert split_code("") == ("", "")


def test_fmt_non_inventa_decimali() -> None:
    assert fmt(82.0) == "82"
    assert fmt(100939.25, 1) == "100939.2"  # arrotondamento bancario di Python
    assert fmt(None) == ""
