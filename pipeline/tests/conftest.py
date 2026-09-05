"""I tre pezzi di codice del progetto, raggiungibili da un `import`.

`brescia_pipeline` è un pacchetto installato e si importa da sé. Gli altri due
non lo sono, di proposito: `analysis/` sono script da riga di comando e
`sito/costruisci.py` è un programma, non una libreria, e nessuno dei due va
distribuito. Ma sono **codice del progetto**, quindi vanno testati come il
resto, e per testarli bisogna poterli importare.

Da qui, e non con un `sys.path.insert` ripetuto in cima a ogni file di test:
scritto una volta sola vale per tutti e si sposta in un posto solo il giorno
che le cartelle cambiano nome.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

RADICE = Path(__file__).resolve().parents[2]
ANALISI = RADICE / "analysis"
SITO = RADICE / "sito"
PROCESSED = RADICE / "dati" / "processed"

for cartella in (ANALISI, SITO):
    if str(cartella) not in sys.path:
        sys.path.insert(0, str(cartella))


# Le tabelle sono versionate, quindi ci sono quasi sempre; ma un checkout
# parziale o un clone superficiale può non averle, e un test che esplode con
# `FileNotFoundError` non dice niente a chi lo legge. Meglio saltare e dire
# perché.
def _mancano_le_tabelle() -> bool:
    return not PROCESSED.exists() or not any(PROCESSED.glob("*.csv"))


servono_tabelle = pytest.mark.skipif(
    _mancano_le_tabelle(),
    reason=f"mancano le tabelle in {PROCESSED}: `python -m brescia_pipeline.build --offline`",
)


@pytest.fixture(scope="session")
def radice() -> Path:
    return RADICE


# --- il guardiano della rete ---------------------------------------------


class ReteVietata(BaseException):
    """Un test ha provato a uscire in rete.

    Deriva da `BaseException` di proposito: il codice della pipeline cattura
    `Exception` per ritentare sui guasti di rete, e un'eccezione ordinaria
    finirebbe dentro quel `try` invece di fermare il test.
    """


@pytest.fixture(autouse=True)
def nessuna_rete(monkeypatch, request):
    """Nessun test tocca la rete, e chi ci prova fallisce subito.

    Non è zelo: è una lezione. Un test scritto in questa stessa sessione
    chiamava `province_per_nome()`, che sotto sotto fa `fetch()`. In locale
    passava in un millisecondo perché `dati/raw/` aveva già il file; in CI, dove
    quella cartella non è versionata e quindi non esiste, partiva un download da
    ISTAT con tre tentativi e attese crescenti. Il risultato non era un test
    rosso: era un job **appeso**, che è molto peggio perché non dice niente.

    `requests.get` alzato a errore trasforma quel caso in un fallimento
    immediato con scritto sopra quale test e quale URL. I moduli che scaricano
    si esercitano con risposte finte (`test_datasets_senza_rete.py`), e chi ha
    davvero bisogno della rete non esiste in questa suite.

    ⚠️ L'eccezione deriva da `BaseException` e non da `Exception`, ed è la
    seconda metà della lezione. Con un `AssertionError` normale il guardiano
    scattava e **`fetch` lo catturava**: il suo `except Exception` è largo
    apposta (i 502 sporadici del proxy), quindi lo prendeva per un guasto di
    rete e ritentava cinque volte con attese crescenti. Il test restava appeso
    per quattro minuti esattamente come prima, e il guardiano sembrava non
    funzionare. Da `BaseException` non lo cattura nessuno.
    """
    import requests

    def vietato(*args, **kwargs):
        url = args[0] if args else kwargs.get("url", "?")
        raise ReteVietata(
            f"{request.node.name} ha provato a scaricare {url}.\n"
            "I test non toccano la rete: usa una risposta finta, oppure salta "
            "il test se il file di cache non c'è."
        )

    monkeypatch.setattr(requests, "get", vietato)
    monkeypatch.setattr(requests, "post", vietato, raising=False)


def cache_o_salta(nome_file: str):
    """Il percorso di un file in `dati/raw/`, o `pytest.skip` se non c'è.

    `dati/raw/` non è versionata: quello che c'è in locale può non esserci in
    CI, e un test che lo assume passa qui e appende là.
    """
    percorso = RADICE / "dati" / "raw" / nome_file
    if not percorso.exists():
        pytest.skip(f"manca la cache {percorso.relative_to(RADICE)}: si scarica col build")
    return percorso
