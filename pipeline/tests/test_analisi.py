"""I quindici script di `analysis/`, eseguiti davvero.

Non sono test di unità e non fingono di esserlo. Sono la rete che manca a
questo strato: quindici programmi che leggono trentuno CSV, fanno statistica e
stampano tabelle, e che finora nessuno eseguiva se non a mano. Un errore lì
non fa cadere il sito né la pipeline — fa cadere lo script quando qualcuno
prova a rilanciarlo sei mesi dopo, e a quel punto nessuno ricorda più cosa
faceva.

Cosa verificano davvero, oltre al fatto che non esplodono:

- **il codice di uscita è zero**, per tutti, anche con le opzioni;
- **stampano qualcosa di sostanzioso**, perché uno script che finisce senza
  scrivere niente è caduto in un ramo vuoto senza dirlo;
- **`--save` scrive dove dice**, in una cartella temporanea, e i CSV prodotti
  hanno un'intestazione e delle righe;
- **niente `nan`, `inf` o `None`** nell'uscita: sono i tre modi in cui un conto
  sbagliato si presenta come un numero.

E in fondo c'è il pezzo che vale più di tutti gli altri messi insieme:
`verifica_cifre.py`, che ricalcola dai CSV ogni cifra citata nei documenti e
nel sito. Girava solo in CI come comando a sé; qui diventa un test, quindi
fallisce anche in locale e insieme al resto.
"""

from __future__ import annotations

import importlib
import re
import shutil

import pytest

from conftest import servono_tabelle

pytestmark = servono_tabelle

# Nome del modulo -> argomenti con cui va lanciato almeno una volta. Dove ci
# sono più righe, lo script si esercita più volte: sono i rami che le opzioni
# aprono, ed è dove si nasconde il codice che nessuno ha più eseguito da mesi.
SCRIPT = {
    "aria_e_clima": [[]],
    "autocorrelazione_spaziale": [["--permutazioni", "19"]],
    "casa_e_prezzi": [[], ["--quanti", "3"]],
    "confronto_province": [[]],
    "confronto_turismo": [[]],
    "convergenza_confronto": [[]],
    "decomposizione_capoluogo": [[], ["--quante", "3"]],
    "decomposizione_popolazione": [[], ["--tutti"]],
    "dove_si_lavora": [[]],
    "due_economie": [[], ["--quanti", "3"]],
    "livelli_e_variazioni": [[], ["popolazione", "reddito"]],
    "rottura_covid": [[]],
    "tipologia_comuni": [["--gruppi", "3"]],
    "variazione_popolazione": [[], ["--tutti", "--code", "2"]],
    "velocita_di_cambio": [["addetti"], ["reddito", "--code", "2"]],
}

# `nan` e `inf` come parole intere: «Gargnano» contiene «nan» e non è un errore.
NUMERI_MALATI = re.compile(r"\b(nan|inf|-inf|None)\b", re.IGNORECASE)


def _lancia(modulo: str, argv: list[str], capsys) -> str:
    mod = importlib.import_module(modulo)
    assert mod.main(argv) == 0, f"{modulo} {argv} è uscito con un codice diverso da zero"
    uscita = capsys.readouterr().out
    assert len(uscita) > 200, f"{modulo} {argv} ha stampato {len(uscita)} caratteri"
    return uscita


@pytest.mark.parametrize(
    "modulo,argv",
    [(m, a) for m, opzioni in sorted(SCRIPT.items()) for a in opzioni],
    ids=lambda v: " ".join(v) if isinstance(v, list) else v,
)
def test_ogni_script_gira_e_stampa_qualcosa(modulo: str, argv: list[str], capsys) -> None:
    _lancia(modulo, argv, capsys)


@pytest.mark.parametrize("modulo", sorted(SCRIPT))
def test_nessuno_script_stampa_nan_o_none(modulo: str, capsys) -> None:
    """`nan`, `inf` e `None` sono i tre modi in cui un conto sbagliato si
    presenta come un numero, e in una tabella stampata passano inosservati."""
    uscita = _lancia(modulo, SCRIPT[modulo][0], capsys)
    malati = NUMERI_MALATI.findall(uscita)
    assert not malati, f"{modulo} stampa {sorted(set(malati))}"


def _uscita_temporanea(mod, monkeypatch):
    """Dirotta l'uscita di uno script in una cartella usa-e-getta.

    Sta **dentro** `analysis/output/`, che è già in `.gitignore`, e non in
    `tmp_path`, per una ragione che ho scoperto sbagliando: gli script stampano
    il percorso scritto come `relative_to(RADICE)`, quindi una destinazione
    fuori dal repository fa esplodere quella riga. Spostare anche `RADICE` non
    è la via d'uscita: alcuni script la usano anche per **leggere** (il GeoJSON
    dei confini), e con la radice finta cadono prima di scrivere.

    Si patcha quindi solo `OUTPUT`, e la destinazione resta sotto la radice
    vera. La cartella viene cancellata alla fine del test.
    """
    import _tabelle

    uscita = _tabelle.OUTPUT / f".test-{mod.__name__}"
    for bersaglio in (_tabelle, mod):
        if hasattr(bersaglio, "OUTPUT"):
            monkeypatch.setattr(bersaglio, "OUTPUT", uscita)
    return uscita


@pytest.mark.parametrize("modulo", sorted(SCRIPT))
def test_save_scrive_csv_leggibili(modulo: str, monkeypatch, capsys) -> None:
    """`--save` non deve scrivere in `analysis/output/` durante i test, e
    quello che scrive deve essere un CSV con un'intestazione e delle righe."""
    mod = importlib.import_module(modulo)
    uscita = _uscita_temporanea(mod, monkeypatch)
    try:
        assert mod.main(SCRIPT[modulo][0] + ["--save"]) == 0
        capsys.readouterr()

        scritti = sorted(uscita.glob("*.csv")) if uscita.exists() else []
        assert scritti, f"{modulo} --save non ha scritto nessun CSV in {uscita}"
        for csv in scritti:
            righe = csv.read_text(encoding="utf-8").splitlines()
            assert len(righe) >= 2, f"{csv.name}: solo {len(righe)} righe"
            assert "," in righe[0], f"{csv.name}: l'intestazione non ha colonne"
    finally:
        shutil.rmtree(uscita, ignore_errors=True)


# --- il verificatore delle cifre -----------------------------------------


def test_ogni_cifra_citata_nei_documenti_torna(capsys) -> None:
    """Il test che vale per tutti gli altri.

    `verifica_cifre.py` ricalcola dalle tabelle ogni numero scritto nei
    documenti e nel sito, con una seconda implementazione che **non condivide
    codice** con quella verificata. Girava solo come comando in CI; da qui
    fallisce anche in locale, insieme al resto della suite.
    """
    import verifica_cifre

    assert verifica_cifre.main([]) == 0
    uscita = capsys.readouterr().out
    coda = uscita.strip().splitlines()[-1]
    assert coda.endswith("0 divergenti"), coda
    quante = int(coda.split()[0])
    assert quante >= 150, f"solo {quante} verifiche: ne è sparita qualcuna"
    assert "DIVERGE" not in uscita


def test_il_verificatore_sa_anche_scrivere_il_csv(monkeypatch, capsys) -> None:
    import verifica_cifre

    uscita = _uscita_temporanea(verifica_cifre, monkeypatch)
    try:
        assert verifica_cifre.main(["--csv"]) == 0
        capsys.readouterr()
        scritto = uscita / "verifica_cifre.csv"
        assert scritto.exists()
        righe = scritto.read_text(encoding="utf-8").splitlines()
        assert righe[0].startswith("documento,cifra")
        assert len(righe) > 150
    finally:
        shutil.rmtree(uscita, ignore_errors=True)


def test_una_cifra_che_diverge_fa_uscire_con_errore(monkeypatch, capsys) -> None:
    """Il controllo del controllo: se il verificatore non fallisse mai, il suo
    «0 divergenti» non vorrebbe dire niente."""
    import verifica_cifre

    monkeypatch.setattr(
        verifica_cifre,
        "VERIFICHE",
        [("prova", "un numero che non torna", 1.0, lambda: 999.0, 0.0)],
    )
    assert verifica_cifre.main([]) != 0
    assert "DIVERGE" in capsys.readouterr().out
