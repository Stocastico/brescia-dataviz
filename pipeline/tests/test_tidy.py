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
    ("raw", "atteso"),
    [
        # Un punto solo seguito da tre cifre non dice quale convenzione sia:
        # qui vale come decimale, che è quella dell'SDMX. Il test la fissa
        # perché è una scelta, non una deduzione — e perché è la forma su cui
        # una fonte italiana sbaglierebbe di mille volte.
        ("702.557", 702.557),
        ("0.123", 0.123),
        ("3.900", 3.9),
    ],
)
def test_un_punto_solo_e_sempre_decimale(raw: str, atteso: float) -> None:
    assert to_number(raw) == pytest.approx(atteso)


def test_le_migliaia_col_punto_hanno_il_loro_parser_e_non_passano_di_qui() -> None:
    """La fonte che scrive `702.557` per settecentomila è l'INPS, e ha un
    parser suo. Se qualcuno un giorno la facesse passare da `to_number`, il
    numero uscirebbe mille volte più piccolo senza un errore: questo test
    tiene i due comportamenti visibili uno accanto all'altro."""
    from brescia_pipeline.datasets.inps import intero

    assert intero("702.557") == 702_557
    assert to_number("702.557") == pytest.approx(702.557)  # mille volte meno
    with pytest.raises(RuntimeError, match="forma non prevista"):
        intero("702,557")


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
