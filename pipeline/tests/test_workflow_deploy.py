"""Il deploy non deve poter partire da solo.

Un workflow non ha test, e per questo è il posto dove una riga cambiata di
soppiatto non se ne accorge nessuno finché il sito non è online. Qui si fissa
l'unica proprietà che conta per chi non ha ancora finito l'analisi:

    **nessun evento automatico può arrivare al job che pubblica.**

Costruire e verificare a ogni push serve e resta; pubblicare è una decisione, e
si prende a mano.

Il test si salta dove manca PyYAML, che non è una dipendenza della pipeline: in
CI viene installato accanto a pytest apposta per farlo girare.
"""

from __future__ import annotations

from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml", reason="PyYAML non installato: il controllo del workflow si salta")

WORKFLOW = Path(__file__).resolve().parents[2] / ".github" / "workflows" / "deploy-pages.yml"

# `on:` in YAML 1.1 è il booleano True, non la stringa "on". Con `safe_load` la
# chiave arriva come `True`, ed è il tipo di dettaglio che fa scrivere un test
# che passa sempre perché non trova mai niente.
CHIAVE_TRIGGER = True


@pytest.fixture(scope="module")
def workflow() -> dict:
    if not WORKFLOW.exists():
        pytest.skip(f"manca {WORKFLOW.name}")
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def pubblica(workflow: dict) -> dict:
    jobs = workflow["jobs"]
    assert "pubblica" in jobs, f"job «pubblica» sparito: ci sono {sorted(jobs)}"
    return jobs["pubblica"]


def test_il_workflow_si_puo_lanciare_a_mano(workflow: dict) -> None:
    """Senza `workflow_dispatch` non ci sarebbe modo di pubblicare affatto."""
    assert "workflow_dispatch" in workflow[CHIAVE_TRIGGER]


def test_solo_il_lancio_a_mano_arriva_al_job_che_pubblica(pubblica: dict) -> None:
    """La condizione del job deve nominare `workflow_dispatch`.

    È il cardine: qualunque altro evento — un push su `main`, uno schedule
    aggiunto un domani, un `repository_dispatch` — costruisce e si ferma.
    """
    condizione = str(pubblica.get("if", ""))
    assert "workflow_dispatch" in condizione, (
        "il job «pubblica» non è più ristretto al lancio manuale: "
        f"if = {condizione!r}"
    )
    assert "github.event_name" in condizione


def test_il_lancio_a_mano_chiede_una_conferma_scritta(workflow: dict, pubblica: dict) -> None:
    """Un clic su «Run workflow» è troppo poco per mandare online un sito.

    L'input va digitato, e il job lo controlla: le due metà servono entrambe,
    perché un input che nessuno legge è decorazione.
    """
    ingressi = workflow[CHIAVE_TRIGGER]["workflow_dispatch"]["inputs"]
    assert "conferma" in ingressi
    assert ingressi["conferma"]["required"] is True
    assert "conferma" in str(pubblica.get("if", ""))
    # Il valore preimpostato non deve essere quello che pubblica, altrimenti
    # «Run workflow» senza leggere manda online il sito.
    assert ingressi["conferma"].get("default") != "pubblica"


def test_le_due_condizioni_valgono_insieme_e_non_in_alternativa(pubblica: dict) -> None:
    """`&&`, non `||`.

    Con un `or` in mezzo la condizione resterebbe leggibile e sarebbe rovesciata:
    ogni push la soddisferebbe passando dalla seconda metà. È il modo più facile
    di rompere questo cancello senza che nessun altro test se ne accorga.
    """
    condizione = str(pubblica["if"])
    assert "&&" in condizione
    assert "||" not in condizione


def test_solo_il_job_che_pubblica_tocca_pages(workflow: dict) -> None:
    """`configure-pages` e `deploy-pages` non devono comparire nel job che gira
    a ogni push: sono gli unici passi che cambiano qualcosa fuori dal runner."""
    for nome, job in workflow["jobs"].items():
        if nome == "pubblica":
            continue
        azioni = " ".join(str(p.get("uses", "")) for p in job.get("steps", []))
        assert "deploy-pages" not in azioni, f"il job «{nome}» pubblica"
        assert "configure-pages" not in azioni, f"il job «{nome}» tocca le impostazioni di Pages"


def test_un_push_non_puo_annullare_una_pubblicazione_in_corso(workflow: dict) -> None:
    """`cancel-in-progress` è comodo fra due build e pericoloso su un deploy:
    un push che arriva a metà pubblicazione lascerebbe il sito a metà. I due
    generi di esecuzione stanno quindi in gruppi di concorrenza diversi."""
    gruppo = str(workflow["concurrency"]["group"])
    assert "github.event_name" in gruppo, (
        "build e pubblicazioni condividono il gruppo di concorrenza: "
        f"group = {gruppo!r}"
    )


def test_la_costruzione_gira_comunque_a_ogni_push(workflow: dict) -> None:
    """Togliere il deploy automatico non deve togliere i controlli: se una cifra
    citata smette di tornare, si vuole saperlo al push, non alla pubblicazione."""
    assert "push" in workflow[CHIAVE_TRIGGER]
    passi = " ".join(str(p.get("run", "")) for p in workflow["jobs"]["costruisci"]["steps"])
    assert "verifica_cifre" in passi
    assert "pytest" in passi
