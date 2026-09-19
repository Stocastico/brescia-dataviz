"""Il deploy parte da `main`, e da nient'altro.

Un workflow non ha test, e per questo è il posto dove una riga cambiata di
soppiatto non se ne accorge nessuno finché il sito non è online. Finché
l'analisi era in corso la proprietà fissata qui era che *nessun* evento
automatico arrivasse al job che pubblica. Adesso che il sito è online quella
regola è caduta apposta, e al suo posto ne restano tre:

    **pubblica `main`, e soltanto `main`** — non un altro ramo, non un lancio
    a mano distratto;
    **pubblica solo ciò che è verde** — `pubblica` dipende da `costruisci`, che
    esegue test e ricalcolo delle cifre citate;
    **niente si annulla a metà** — una pubblicazione partita arriva in fondo.

Il cancello non è sparito: si è spostato da «qualcuno lo chiede a mano» a
«la costruzione è verde».

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


def test_un_push_arriva_al_job_che_pubblica(pubblica: dict) -> None:
    """La condizione del job deve nominare l'evento `push`.

    È il cardine di adesso: un merge su `main` manda il sito online senza che
    nessuno debba andare in Actions. Se questa riga sparisce, il sito smette di
    aggiornarsi e non se ne accorge nessuno, perché la CI resta verde.
    """
    condizione = str(pubblica.get("if", ""))
    assert "push" in condizione, (
        "il job «pubblica» non si attiva più sui push: "
        f"if = {condizione!r}"
    )
    assert "github.event_name" in condizione


def test_pubblica_solo_main(workflow: dict) -> None:
    """L'altra metà: `push` senza filtro pubblicherebbe ogni ramo.

    Un ramo di lavoro spinto in remoto metterebbe online un sito a metà, e lo
    farebbe in silenzio. Il filtro sui rami è ciò che rende «push» sinonimo di
    «main».
    """
    push = workflow[CHIAVE_TRIGGER]["push"]
    assert push and "branches" in push, (
        f"il trigger push non filtra i rami: push = {push!r}"
    )
    assert list(push["branches"]) == ["main"], (
        f"pubblicano anche rami diversi da main: {push['branches']!r}"
    )


def test_si_pubblica_solo_cio_che_e_verde(pubblica: dict) -> None:
    """Il cancello che ha preso il posto della conferma a mano.

    `needs: costruisci` è l'unica cosa che impedisce a un push rosso — un test
    rotto, una cifra citata che non torna più — di finire online. Senza,
    «pubblica a ogni push» diventa «pubblica qualunque cosa».
    """
    needs = pubblica.get("needs")
    needs = [needs] if isinstance(needs, str) else list(needs or [])
    assert "costruisci" in needs, (
        f"il job «pubblica» non dipende più dalla costruzione: needs = {needs!r}"
    )


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


def test_il_lancio_a_mano_resta_una_via_per_costruire_senza_pubblicare(pubblica: dict) -> None:
    """La condizione è un `||`, e le due metà non sono intercambiabili.

    Il push pubblica da solo; il lancio a mano no, gli serve la conferma
    scritta. È ciò che tiene in piedi «Run workflow» come modo di provare una
    build da un ramo senza mandarla online — e se qualcuno un domani
    semplificasse la condizione a `true`, quella via sparirebbe in silenzio.
    """
    condizione = str(pubblica["if"])
    assert "||" in condizione, (
        f"le due vie non sono più distinte: if = {condizione!r}"
    )
    prima, seconda = (m.strip() for m in condizione.split("||", 1))
    assert "push" in prima and "conferma" not in prima
    assert "conferma" in seconda, (
        f"il lancio a mano non chiede più la conferma: {seconda!r}"
    )


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
    """`cancel-in-progress` è comodo fra due build e pericoloso su un deploy.

    Finché pubblicava solo il lancio a mano, bastava tenere i due generi di
    esecuzione in gruppi di concorrenza diversi: le build si annullavano fra
    loro e le pubblicazioni stavano per conto proprio. Adesso che **ogni**
    esecuzione su `main` può arrivare al deploy quella separazione non esiste
    più, e l'unica forma sicura è non annullare niente che sia già partito.

    I push che arrivano durante una pubblicazione si accodano invece di
    ucciderla; fra due in attesa GitHub tiene la più recente.
    """
    concorrenza = workflow["concurrency"]
    assert concorrenza.get("cancel-in-progress") is False, (
        "una pubblicazione può essere annullata a metà e lasciare il sito "
        f"monco: cancel-in-progress = {concorrenza.get('cancel-in-progress')!r}"
    )


def test_la_costruzione_gira_comunque_a_ogni_push(workflow: dict) -> None:
    """I controlli stanno prima del deploy, non accanto.

    Adesso che il push pubblica, questi due passi sono l'unica cosa che separa
    un commit sbagliato dal sito online: se una cifra citata smette di tornare,
    `costruisci` è rosso e `pubblica` non parte."""
    assert "push" in workflow[CHIAVE_TRIGGER]
    passi = " ".join(str(p.get("run", "")) for p in workflow["jobs"]["costruisci"]["steps"])
    assert "verifica_cifre" in passi
    assert "pytest" in passi


# --- i due workflow non si pestano i piedi -------------------------------

VERIFICA = WORKFLOW.parent / "verifica.yml"


@pytest.fixture(scope="module")
def verifica() -> dict:
    if not VERIFICA.exists():
        pytest.skip(f"manca {VERIFICA.name}")
    return yaml.safe_load(VERIFICA.read_text(encoding="utf-8"))


# Il lancio a mano non conta come sovrapposizione, e la ragione e' che non e'
# un evento del repository: e' una voce di menu che si sceglie una per volta.
# Che entrambi i workflow lo accettino non fa girare niente due volte — fa che
# «Verifica» si possa lanciare su un ramo senza PR, che e' proprio cio' che
# serve da quando i push non la attivano piu'.
A_MANO = {"workflow_dispatch"}


def eventi(workflow: dict, automatici: bool = True) -> set[str]:
    """Gli eventi che attivano un workflow, come nomi."""
    trigger = workflow[CHIAVE_TRIGGER]
    if isinstance(trigger, str):
        nomi = {trigger}
    else:
        nomi = set(trigger)
    return nomi - A_MANO if automatici else nomi


def test_i_due_workflow_non_girano_sullo_stesso_evento(workflow: dict, verifica: dict) -> None:
    """La suite gira una volta per ciclo, non quattro.

    I due workflow eseguono **gli stessi sei passi** — checkout, python,
    install, `build --offline web`, `pytest --cov`, `verifica_cifre.py` — e
    «Pubblica il sito» ci aggiunge la costruzione e l'artefatto. Finché non si
    attivano sullo stesso evento, ogni percorso è controllato una volta sola:
    la PR da «Verifica», `main` e il lancio a mano da «Pubblica il sito».

    Quando invece si sovrapponevano, un ciclo PR→merge faceva girare la stessa
    suite quattro volte per trentadue minuti: `push:` senza filtri contava sia
    per il ramo della PR (dove `pull_request` già la faceva girare) sia per
    `main` (dove la fa girare il workflow che pubblica).

    Se un giorno «Verifica» deve tornare a girare sui push, la scelta è
    legittima ma va fatta togliendo i test da «Pubblica il sito», non
    lasciandoli in due posti: questo test è lì per rendere la sovrapposizione
    una decisione invece di una svista."""
    comuni = eventi(verifica) & eventi(workflow)
    assert not comuni, (
        "«Verifica» e «Pubblica il sito» si attivano entrambi su "
        f"{sorted(comuni)}, e girano la stessa suite: un evento, un'esecuzione."
    )


def test_la_verifica_gira_sulle_pull_request(verifica: dict) -> None:
    """L'altra metà del vincolo. Senza questa riga il test qui sopra si
    soddisferebbe anche svuotando i trigger di «Verifica», che è il modo più
    silenzioso di non avere CI."""
    assert "pull_request" in eventi(verifica), "le PR non sono più controllate"


def test_la_verifica_si_puo_lanciare_a_mano(verifica: dict) -> None:
    """Il ripiego di quando i push non la attivano: su un ramo senza PR
    aperta il controllo si chiede da Actions, e senza questa riga non ci
    sarebbe modo di averlo."""
    assert "workflow_dispatch" in eventi(verifica, automatici=False)
