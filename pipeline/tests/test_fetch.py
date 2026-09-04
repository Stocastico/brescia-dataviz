"""Test dello scarico con cache, senza toccare la rete.

Quattro invarianti che sono costate tempo quando non c'erano:

- le richieste SDMX chiedono le etichette **in italiano**. Senza l'header
  `Accept-Language` ISTAT risponde in inglese e le legende dei grafici finiscono
  con `private households on 31st December` (`PROSSIMI-PASSI.md` §2.4);
- un file già in `dati/raw/` **non** viene riscaricato. È il patto su cui si
  regge la possibilità di rilanciare il build senza aspettare ore;
- quando lo scarico fallisce, **l'errore vero finisce nel messaggio**. Il 4
  settembre 2026 il build di `migrazioni` è morto dopo quaranta blocchi con
  «download fallito: <url>» e nient'altro: la causa (`ConnectTimeout`) era
  incatenata all'eccezione ma il build stampa solo `str(errore)`, quindi per
  sapere cos'era è servito rifare la richiesta a mano;
- **le attese fra i tentativi durano minuti, non secondi.** Nello stesso
  episodio `esploradati.istat.it` ha smesso di accettare connessioni mentre
  `demo.istat.it` e `www.istat.it` — stessa sottorete — rispondevano: non un
  guasto, una strozzatura per host che dura qualche minuto. Con la vecchia
  progressione (1+2+4 secondi) i quattro tentativi si consumavano dentro la
  strozzatura, e venti minuti di scarico andavano persi.
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


def test_l_errore_vero_finisce_nel_messaggio(monkeypatch, tmp_path) -> None:
    """Senza la causa nel messaggio, un guasto di rete è indistinguibile da un 404."""

    class Timeout(Exception):
        pass

    def get_che_fallisce(url, headers=None, params=None, timeout=None, stream=None):
        raise Timeout("connessione scaduta")

    monkeypatch.setattr(modulo_fetch.requests, "get", get_che_fallisce)
    monkeypatch.setattr(modulo_fetch, "RAW_DIR", tmp_path)
    monkeypatch.setattr(modulo_fetch.time, "sleep", lambda _: None)

    with pytest.raises(RuntimeError) as errore:
        modulo_fetch.fetch("https://esempio.invalid/x", "prova.csv")

    messaggio = str(errore.value)
    assert "Timeout" in messaggio, messaggio
    assert "connessione scaduta" in messaggio, messaggio


def test_le_attese_fra_i_tentativi_reggono_una_strozzatura(monkeypatch, tmp_path) -> None:
    """Una strozzatura per host dura minuti: i tentativi devono coprirli."""
    attese: list[float] = []

    def get_che_fallisce(url, headers=None, params=None, timeout=None, stream=None):
        raise OSError("niente")

    monkeypatch.setattr(modulo_fetch.requests, "get", get_che_fallisce)
    monkeypatch.setattr(modulo_fetch, "RAW_DIR", tmp_path)
    monkeypatch.setattr(modulo_fetch.time, "sleep", attese.append)

    with pytest.raises(RuntimeError):
        modulo_fetch.fetch("https://esempio.invalid/x", "prova.csv")

    assert sum(attese) >= 120, f"attesa totale {sum(attese)}s: troppo poco per una strozzatura"
    assert attese == sorted(attese), f"le attese non crescono: {attese}"
