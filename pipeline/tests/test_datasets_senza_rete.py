"""I dataset che scaricano, esercitati con risposte finte.

Sono i moduli che la CI non tocca mai: girano solo quando qualcuno rifà lo
scarico, cioè ogni molti mesi, e nel frattempo un filtro sbagliato o un codice
rinominato non fa rumore. Il guaio, quando arriva, non è un errore: è una
tabella con dentro **meno righe di quante dovrebbe**, che passa tutti i
controlli a valle perché è ben formata.

Qui la rete non si tocca. Si sostituiscono i tre punti di contatto —
`sdmx.key` (che leggerebbe la struttura del dataflow), `sdmx_csv` (che
scaricherebbe) e `read_sdmx` (che leggerebbe il file) — con una risposta
costruita a mano, e si guarda cosa il modulo ne ricava.

Le risposte finte non sono generiche: ognuna riproduce la forma reale del
dataflow di quel modulo, codici SDMX compresi (`017029: Brescia`), perché è
proprio sulla forma che questi moduli sbagliano.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from brescia_pipeline import fetch, sdmx
from brescia_pipeline.datasets import imprese, province, turismo_confronto

COMUNI = {"017029": "Brescia", "017184": "Sirmione"}


@pytest.fixture
def scritte(monkeypatch):
    """Cattura le chiamate a `write_csv` invece di scrivere in processed/."""
    catturate: dict[str, tuple[list[dict[str, str]], list[str]]] = {}

    def finto(nome, righe, colonne):
        catturate[nome] = (list(righe), colonne)
        return Path(nome)

    for modulo in (imprese, province, turismo_confronto):
        monkeypatch.setattr(modulo, "write_csv", finto)
    return catturate


def _niente_rete(monkeypatch, modulo, risposte):
    """`risposte` è una funzione `dest_name -> lista di record`.

    Il patch va messo in due posti perché i moduli importano in due modi:
    `imprese` e `turismo_confronto` prendono `sdmx_csv` nel proprio spazio dei
    nomi, `province` lo importa **dentro** `build()` e quindi lo cerca nel
    modulo di origine. Patchare entrambi copre i due casi senza doverli
    distinguere qui.
    """
    chieste: list[str] = []

    def finto_sdmx_csv(dataflow, key="", *, dest_name, force=False):
        chieste.append(dest_name)
        return Path(dest_name)

    def finta_chiave(dataflow, fixed):
        return ""

    monkeypatch.setattr(fetch, "sdmx_csv", finto_sdmx_csv)
    monkeypatch.setattr(sdmx, "key", finta_chiave)
    monkeypatch.setattr(modulo, "sdmx_csv", finto_sdmx_csv, raising=False)
    monkeypatch.setattr(modulo, "read_sdmx", lambda path: risposte(path.name), raising=False)
    return chieste


# --- imprese: comuni x classe dimensionale -------------------------------


def _record_asia(ref_area, classe, valore, anno="2023", nace="0010"):
    return {
        "REF_AREA": ref_area,
        "PERS_EMPL_SIZE_CLASS": classe,
        "ECON_ACTIVITY_NACE_2007": nace,
        "TIME_PERIOD": anno,
        "OBS_VALUE": valore,
    }


def test_imprese_tiene_solo_i_comuni_della_provincia(monkeypatch, scritte) -> None:
    """Il file nazionale si scarica intero e si filtra qui: se il filtro
    cadesse, la tabella comunale conterrebbe l'Italia."""
    risposta = [
        _record_asia("017029: Brescia", "TOTAL: totale", "100"),
        _record_asia("017184: Sirmione", "W0_9: 0-9", "10"),
        _record_asia("015146: Milano", "TOTAL: totale", "9999"),   # fuori provincia
        _record_asia("017029: Brescia", "ZZZ: ignota", "5"),        # classe sconosciuta
        _record_asia("017029: Brescia", "TOTAL: totale", ""),       # valore assente
    ]
    _niente_rete(monkeypatch, imprese, lambda nome: risposta if "classe" in nome else [])
    imprese.build(COMUNI)

    righe, colonne = scritte["imprese_classe_addetti.csv"]
    assert colonne == imprese.CLASSE_COLUMNS
    codici = {r["codice_istat"] for r in righe}
    assert codici == {"017029", "017184"}, "il filtro territoriale non ha filtrato"
    assert all(r["classe_addetti"] in set(imprese.CLASSI.values()) for r in righe)
    assert not [r for r in righe if r["valore"] == ""], "un valore assente è diventato una riga"


def test_imprese_traduce_i_codici_in_nomi_maneggevoli(monkeypatch, scritte) -> None:
    """I codici, non le etichette: le etichette cambiano lingua con l'header
    della richiesta (MET-13). La traduzione deve avvenire qui, una volta sola."""
    risposta = [_record_asia("017029: Brescia", "W_GE250: 250 e più", "42")]
    _niente_rete(monkeypatch, imprese, lambda nome: risposta if "classe" in nome else [])
    imprese.build(COMUNI)

    righe, _ = scritte["imprese_classe_addetti.csv"]
    assert {r["classe_addetti"] for r in righe} == {"250+"}
    assert {r["indicatore"] for r in righe} == set(imprese.INDICATORI.values())
    assert {r["comune"] for r in righe} == {"Brescia"}


def test_gli_addetti_hanno_un_decimale_e_le_unita_locali_no(monkeypatch, scritte) -> None:
    """Gli addetti sono **medie annue**, quindi con decimali; le unità locali
    si contano. Scriverli con lo stesso formato perde o inventa precisione."""
    risposta = [_record_asia("017029: Brescia", "TOTAL: totale", "123.4")]
    _niente_rete(monkeypatch, imprese, lambda nome: risposta if "classe" in nome else [])
    imprese.build(COMUNI)

    righe, _ = scritte["imprese_classe_addetti.csv"]
    per_indicatore = {r["indicatore"]: r["valore"] for r in righe}
    assert per_indicatore["addetti"] == "123.4"
    assert per_indicatore["unita_locali"] == "123"


def test_imprese_scarta_il_totale_e_le_ateco_a_tre_cifre(monkeypatch, scritte) -> None:
    """Il dataflow provinciale scende a tre cifre: si tiene la divisione a due,
    per restare confrontabili col comunale."""
    def risposte(nome):
        if "settore" not in nome:
            return []
        return [
            _record_asia("ITC47: Brescia", "TOTAL: totale", "50", nace="25: metallo"),
            _record_asia("ITC47: Brescia", "TOTAL: totale", "10", nace="251: strutture"),
            _record_asia("ITC47: Brescia", "TOTAL: totale", "99", nace="0010: totale"),
        ]

    _niente_rete(monkeypatch, imprese, risposte)
    imprese.build(COMUNI)

    righe, _ = scritte["imprese_settore.csv"]
    assert {r["ateco"] for r in righe} == {"25"}


# --- province: la somma dei comuni fa la provincia -----------------------


ELENCO_ISTAT = (
    "intestazione;che;il;lettore;salta;e;non;conta;niente;per;il;test;perche;si\n"
    # colonne che il modulo legge: 4 = codice comune, 6 = nome, 10 = regione,
    # 11 = provincia, 13 = «1» se capoluogo
    "a;b;c;d;017029;f;Brescia;h;i;j;Lombardia;Brescia;m;1;o\n"
    "a;b;c;d;017184;f;Sirmione;h;i;j;Lombardia;Brescia;m;0;o\n"
    "a;b;c;d;016024;f;Bergamo;h;i;j;Lombardia;Bergamo;m;1;o\n"
)


@pytest.fixture
def elenco_finto(monkeypatch, tmp_path):
    percorso = tmp_path / "istat_elenco_comuni.csv"
    percorso.write_bytes(ELENCO_ISTAT.encode("latin-1"))
    monkeypatch.setattr(province, "fetch", lambda url, nome: percorso)
    return percorso


def test_lelenco_istat_da_province_e_capoluoghi(elenco_finto) -> None:
    assert province.province_italiane() == {
        "017": ("Brescia", "Lombardia"),
        "016": ("Bergamo", "Lombardia"),
    }
    # capoluogo è la colonna 13 a 1, non il nome uguale a quello della provincia
    assert province.capoluoghi_italiani() == {"017029": "Brescia", "016024": "Bergamo"}


def test_la_provincia_e_la_somma_dei_suoi_comuni(monkeypatch, elenco_finto, scritte) -> None:
    """Il conto che regge la quinta storia: Brescia contro le altre 106.
    Se l'aggregazione perdesse un comune, il confronto sarebbe fra numeri
    diversi da quelli dichiarati e nessun controllo a valle lo vedrebbe."""
    def risposte(nome):
        if "classe" not in nome:
            return []
        return [
            _record_asia("017029: Brescia", "TOTAL: totale", "100"),
            _record_asia("017184: Sirmione", "TOTAL: totale", "40"),
            _record_asia("016024: Bergamo", "TOTAL: totale", "70"),
            _record_asia("999999: altrove", "TOTAL: totale", "1"),  # provincia ignota
        ]

    _niente_rete(monkeypatch, province, risposte)
    province.build({})

    righe, colonne = scritte["imprese_province.csv"]
    assert colonne == province.COLUMNS
    per_provincia = {
        (r["codice_provincia"], r["indicatore"]): r["valore"]
        for r in righe
        if r["dimensione"] == "classe_addetti"
    }
    assert per_provincia[("017", "unita_locali")] == "140"   # 100 + 40
    assert per_provincia[("016", "unita_locali")] == "70"
    assert "999" not in {r["codice_provincia"] for r in righe}


def test_i_capoluoghi_escono_a_parte_e_solo_loro(monkeypatch, elenco_finto, scritte) -> None:
    def risposte(nome):
        if "classe" not in nome:
            return []
        return [
            _record_asia("017029: Brescia", "TOTAL: totale", "100"),
            _record_asia("017184: Sirmione", "TOTAL: totale", "40"),
        ]

    _niente_rete(monkeypatch, province, risposte)
    province.build({})

    righe, colonne = scritte["imprese_capoluoghi.csv"]
    assert colonne == province.CAPOLUOGHI_COLUMNS
    assert {r["codice_istat"] for r in righe} == {"017029"}
    assert {r["provincia"] for r in righe} == {"Brescia"}


def test_le_sezioni_ateco_si_sommano_su_una_dimensione_diversa(
    monkeypatch, elenco_finto, scritte
) -> None:
    """Classi e sezioni sono due tagli dello stesso totale: se finissero nella
    stessa dimensione, sommarli conterebbe due volte gli stessi addetti."""
    def risposte(nome):
        if "sezione_C_" in nome:
            return [_record_asia("017029: Brescia", "TOTAL: totale", "60")]
        return []

    _niente_rete(monkeypatch, province, risposte)
    province.build({})

    righe, _ = scritte["imprese_province.csv"]
    dimensioni = {r["dimensione"] for r in righe}
    assert dimensioni == {"sezione"}
    assert {r["modalita"] for r in righe} == {"C"}


# --- turismo confrontato fra le province ---------------------------------


def _record_turismo(area, anno, valore, indicatore="ARRIVAL", esercizio="TOTAL"):
    return {
        "REF_AREA": area,
        "TIME_PERIOD": anno,
        "OBS_VALUE": valore,
        "DATA_TYPE": indicatore,
        "TYPE_ACCOMMODATION_ESTAB": esercizio,
    }


def test_il_turismo_si_ferma_se_non_aggancia_tutte_le_province(monkeypatch, scritte) -> None:
    """Il pregio migliore di questo modulo, e il test che lo tiene.

    Le province si agganciano **per nome**, non per codice, perché la fonte non
    porta il codice ISTAT. Se un nome cambia forma, quella provincia sparisce e
    la tabella resta ben formata con 106 righe invece di 107 — il modo perfetto
    di sbagliare in silenzio. Il modulo alza le mani invece di scriverla, e
    questo test verifica che lo faccia davvero.
    """
    campioni = [
        _record_turismo("ITC47: Brescia", "2019", "1000"),
        _record_turismo("ITC46: Bergamo", "2019", "500"),
    ]
    _niente_rete(monkeypatch, turismo_confronto, lambda nome: campioni)
    with pytest.raises(RuntimeError, match="invece di 107"):
        turismo_confronto.build(COMUNI)
    assert not scritte, "ha scritto una tabella incompleta prima di accorgersene"


def test_i_nomi_bilingui_si_normalizzano_verso_lelenco_istat() -> None:
    """Le uniche differenze fra la fonte e l'elenco ISTAT sono gli spazi attorno
    alla barra dei nomi bilingui e due alias: è la riga su cui l'aggancio per
    nome sta in piedi."""
    assert turismo_confronto._normalizza("Bolzano / Bozen") == "Bolzano/Bozen"
    assert turismo_confronto._normalizza("  Brescia  ") == "Brescia"
    for sbagliato, giusto in turismo_confronto.ALIAS.items():
        assert turismo_confronto._normalizza(sbagliato) == giusto


def test_lo_stato_marca_gli_anni_che_non_si_possono_confrontare() -> None:
    """MET-18: dal 2025 la voce «alloggi in affitto» cambia definizione, e le
    province sarde cambiano confine prima del riordino. Due cose diverse, due
    stati diversi, e nessuna delle due è un dato mancante."""
    tipologia_toccata = next(iter(turismo_confronto.TIPOLOGIE_TOCCATE))
    assert turismo_confronto._stato(tipologia_toccata, "Lombardia", "2025") == \
        turismo_confronto.STATO_DEFINIZIONE
    assert turismo_confronto._stato(tipologia_toccata, "Lombardia", "2019") == \
        turismo_confronto.STATO_OSSERVATO
    assert turismo_confronto._stato("XX", turismo_confronto.REGIONE_SARDEGNA, "2015") == \
        turismo_confronto.STATO_CONFINE
    # un anno illeggibile non deve esplodere né inventare uno stato
    assert turismo_confronto._stato("XX", "Lombardia", "") == turismo_confronto.STATO_OSSERVATO


def test_le_107_province_si_leggono_per_nome_dallelenco_ufficiale() -> None:
    """Senza rete: `province_per_nome` legge lo stesso elenco che la pipeline
    ha già scaricato. Se non ci fosse, il test si salta invece di fallire."""
    try:
        per_nome = turismo_confronto.province_per_nome()
    except (FileNotFoundError, OSError) as errore:
        pytest.skip(f"elenco ISTAT non in cache: {errore}")
    assert len(per_nome) == 107
    assert per_nome["Brescia"][0] == "017"
    assert "Bolzano/Bozen" in per_nome
