"""Gli elenchi che promettono di essere completi.

Questo repository ha già speso due commit sulla stessa lezione — «un elenco che
promette di essere completo e non lo è vale meno di nessun elenco» — e l'ha
imparata due volte a mano. La terza è stata la tabella dei dataset in
`pipeline/README.md`, che ne elencava venti su ventiquattro: mancavano `omi`,
`compravendite`, `prezzi` e `turismo_confronto`, cioè proprio quelli aggiunti
più tardi. Nessuno se n'era accorto perché niente lo controllava.

Adesso lo controlla questo file. Non verifica *cosa* dice la riga — quello resta
lavoro di chi scrive — ma che una riga ci sia per ogni dataset registrato, e che
non ce ne siano per dataset che non esistono più.
"""

from __future__ import annotations

import re
from pathlib import Path

from brescia_pipeline.build import DATASETS

README = Path(__file__).resolve().parents[1] / "README.md"

# Le righe della tabella cominciano con il nome del dataset fra backtick,
# eventualmente seguito dal ⏳ di «modulo scritto, tabella non ancora prodotta».
RIGA = re.compile(r"^\| `([a-z_]+)`", re.MULTILINE)


def elencati() -> set[str]:
    return set(RIGA.findall(README.read_text(encoding="utf-8")))


def test_ogni_dataset_ha_la_sua_riga_nel_readme() -> None:
    mancanti = sorted(set(DATASETS) - elencati())
    assert not mancanti, (
        f"dataset registrati ma non elencati in {README.name}: {mancanti}. "
        "Aggiungere un modulo a DATASETS senza aggiungerlo alla tabella rende "
        "la tabella una promessa non mantenuta"
    )


def test_il_readme_non_elenca_dataset_che_non_esistono() -> None:
    fantasmi = sorted(elencati() - set(DATASETS))
    assert not fantasmi, (
        f"righe in {README.name} senza un dataset dietro: {fantasmi}. "
        "Un dataset rimosso va tolto anche da qui"
    )


def test_l_ordine_della_tabella_e_quello_del_build() -> None:
    """L'ordine non è estetico: è la sequenza in cui i dataset girano.

    `sintesi` e `web` devono restare in coda perché rileggono ciò che gli altri
    hanno scritto, e una tabella che li mette altrove racconta un build che non
    esiste.
    """
    ordine_readme = [n for n in RIGA.findall(README.read_text(encoding="utf-8"))]
    assert ordine_readme == list(DATASETS)
