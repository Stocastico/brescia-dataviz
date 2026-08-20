"""Test dello scarico con cache, senza toccare la rete.

Due invarianti che sono costate tempo quando non c'erano:

- le richieste SDMX chiedono le etichette **in italiano**. Senza l'header
  `Accept-Language` ISTAT risponde in inglese e le legende dei grafici finiscono
  con `private households on 31st December` (`PROSSIMI-PASSI.md` §2.4);
- un file già in `dati/raw/` **non** viene riscaricato. È il patto su cui si
  regge la possibilità di rilanciare il build senza aspettare ore.
"""

from __future__ import annotations

import pytest

from brescia_pipeline import fetch as modulo_fetch


class RispostaFinta:
    def __init__(self, contenuto: bytes) -> None:
        self._contenuto = contenuto

    def raise_for_status(self) -> None:
        return None

    def iter_content(self, chunk_size: int = 0):
        yield self._contenuto


@pytest.fixture
def rete_finta(monkeypatch, tmp_path):
    """Sostituisce `requests.get` e `RAW_DIR`, e registra le chiamate."""
    chiamate: list[dict] = []

    def get_finto(url, headers=None, params=None, timeout=None, stream=None):
        chiamate.append({"url": url, "headers": headers or {}, "params": params})
        return RispostaFinta(b"DATAFLOW,FREQ\n")

    monkeypatch.setattr(modulo_fetch.requests, "get", get_finto)
    monkeypatch.setattr(modulo_fetch, "RAW_DIR", tmp_path)
    return chiamate


def test_le_richieste_sdmx_chiedono_le_etichette_in_italiano(rete_finta) -> None:
    modulo_fetch.sdmx_csv("DF_QUALUNQUE", "A.017029...", dest_name="prova.csv")
    assert rete_finta[0]["headers"]["Accept-Language"] == "it"


def test_le_richieste_sdmx_negoziano_il_csv_con_l_header(rete_finta) -> None:
    # Con `format=` nella query string ISTAT risponde con la sola intestazione.
    modulo_fetch.sdmx_csv("DF_QUALUNQUE", "A.017029...", dest_name="prova.csv")
    assert "vnd.sdmx.data+csv" in rete_finta[0]["headers"]["Accept"]
    assert rete_finta[0]["params"] is None


def test_un_file_gia_scaricato_non_si_riscarica(rete_finta) -> None:
    modulo_fetch.fetch("https://esempio.invalid/x", "prova.csv")
    modulo_fetch.fetch("https://esempio.invalid/x", "prova.csv")
    assert len(rete_finta) == 1


def test_force_riscarica_anche_se_il_file_c_e(rete_finta) -> None:
    # È l'unico modo per rimpiazzare una cache scaricata in inglese.
    modulo_fetch.fetch("https://esempio.invalid/x", "prova.csv")
    modulo_fetch.fetch("https://esempio.invalid/x", "prova.csv", force=True)
    assert len(rete_finta) == 2


def test_un_file_vuoto_non_conta_come_cache(rete_finta, tmp_path) -> None:
    (tmp_path / "prova.csv").write_bytes(b"")
    modulo_fetch.fetch("https://esempio.invalid/x", "prova.csv")
    assert len(rete_finta) == 1
