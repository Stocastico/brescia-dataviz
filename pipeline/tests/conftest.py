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
