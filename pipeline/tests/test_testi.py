"""La punteggiatura dei testi pubblicati.

Il sito è scritto in italiano, e l'italiano gli incisi li fa con le virgole,
i due punti o un punto fermo. La **lineetta lunga** (`—`, em dash) è un segno
d'uso inglese: usata come inciso rende la prosa uniforme e riconoscibile, e in
un testo che deve suonare scritto da qualcuno è precisamente l'effetto da
evitare. Fuori, quindi, da tutto ciò che un lettore vede.

Non è una regola di gusto soltanto. La lineetta lunga era arrivata a comparire
**settantasei volte** nella sola pagina delle storie, tre o quattro per
capoverso, ed è il genere di cosa che si nota tutta insieme e mai una alla
volta: senza un controllo torna al primo paragrafo aggiunto.

**Il trattino medio (`–`, en dash) resta**, ed è un segno diverso con un lavoro
diverso: separa gli estremi di un intervallo (`2004–2025`, `1991–2020`), che è
l'uso corretto anche in italiano. Il test lo lascia stare apposta.

Il controllo gira sui **modelli** e non sul sito costruito, così fallisce
mentre si scrive invece che dopo la costruzione, e non ha bisogno che il sito
sia stato costruito per girare.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from brescia_pipeline.web import WEB_DATA_DIR

MODELLI = Path(__file__).resolve().parents[2] / "sito" / "modelli"

LINEETTA_LUNGA = "—"  # —  em dash
TRATTINO_MEDIO = "–"  # –  en dash: legittimo, e non si tocca

PAGINE = ("racconto.html", "dati.html", "metodologia.html")


def righe_con(percorso: Path, segno: str) -> list[str]:
    """Le righe che contengono il segno, numerate come le vede un editor."""
    return [
        f"{percorso.name}:{numero}: {riga.strip()}"
        for numero, riga in enumerate(percorso.read_text(encoding="utf-8").splitlines(), 1)
        if segno in riga
    ]


@pytest.mark.parametrize("pagina", PAGINE)
def test_nessuna_lineetta_lunga_nelle_pagine(pagina: str) -> None:
    percorso = MODELLI / pagina
    if not percorso.exists():
        pytest.skip(f"manca {pagina}")
    colpevoli = righe_con(percorso, LINEETTA_LUNGA)
    assert not colpevoli, (
        "lineetta lunga (—) nel testo pubblicato: in italiano l'inciso si fa con "
        "le virgole, i due punti o un punto fermo.\n" + "\n".join(colpevoli)
    )


# Un estremo di intervallo: quattro cifre, oppure il segnaposto di una cifra
# ricalcolata in fase di costruzione — che è la forma in cui quasi tutti gli
# anni di questa pagina sono scritti, perché nessuna cifra è scritta a mano.
ESTREMO = r"(?:\d{4}|\{\{c:[a-z0-9_]+\}\})"


def test_il_trattino_medio_degli_intervalli_resta() -> None:
    """Il contrappeso: senza, «togliere le lineette» diventa toglierle tutte.

    Gli intervalli di anni del racconto (`2004–2025`, o `{{c:anno_i}}–{{c:anno_f}}`
    prima della costruzione) si scrivono con il trattino medio, ed è giusto
    così. Se un giorno qualcuno li appiattisce su un trattino d'unione, o li
    porta via insieme alle lineette lunghe, questo test lo dice.
    """
    racconto = MODELLI / "racconto.html"
    if not racconto.exists():
        pytest.skip("manca racconto.html")
    testo = racconto.read_text(encoding="utf-8")
    intervalli = re.findall(rf"{ESTREMO}{TRATTINO_MEDIO}{ESTREMO}", testo)
    assert intervalli, "nessun intervallo di anni scritto con il trattino medio"


# I modelli non sono l'unico posto da cui esce testo che il lettore legge. Sotto
# ogni grafico c'è una riga di provenienza, e le sue parole vengono dal registro
# degli indicatori, cioè dalla **pipeline**: `web.py`. Le lineette lunghe erano
# tornate esattamente da lì, dove nessuno le cercava perché non sono in un file
# di testo — e sono la scritta più ripetuta del sito, una per grafico.
CAMPI_LEGGIBILI = ("label", "unit", "source", "confidence")


@pytest.mark.skipif(
    not (WEB_DATA_DIR / "metrics.json").exists(),
    reason="nessun export per il sito: lanciare `python -m brescia_pipeline.build web`",
)
def test_nessuna_lineetta_lunga_nel_registro_degli_indicatori() -> None:
    registro = json.loads((WEB_DATA_DIR / "metrics.json").read_text(encoding="utf-8"))
    colpevoli = [
        f"{voce['id']}.{campo}: {voce[campo]}"
        for voce in registro
        for campo in CAMPI_LEGGIBILI
        if LINEETTA_LUNGA in str(voce.get(campo, ""))
    ] + [
        f"{voce['id']}.assumptions: {nota}"
        for voce in registro
        for nota in voce.get("assumptions", [])
        if LINEETTA_LUNGA in nota
    ]
    assert not colpevoli, (
        "lineetta lunga (—) nel registro degli indicatori: queste stringhe finiscono "
        "sotto i grafici, nella riga di provenienza.\n" + "\n".join(colpevoli)
    )
