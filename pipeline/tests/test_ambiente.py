"""Test delle misure ambientali ARPA, senza rete.

Coprono la cosa che qui sbaglia davvero e in silenzio: **l'aggregazione**. Una
temperatura mensile è una media, una precipitazione mensile è un totale, e
scrivere la media delle piogge orarie in una colonna chiamata `media` produce un
numero plausibile che non significa niente.
"""

from __future__ import annotations

import pytest

from brescia_pipeline.datasets import ambiente

SENSORI = [
    {"id_sensore": "1", "stazione": "Alfa", "parametro": "Temperatura", "comune": ""},
    {"id_sensore": "2", "stazione": "Beta", "parametro": "Precipitazione", "comune": ""},
    {"id_sensore": "3", "stazione": "Gamma", "parametro": "Umidità Relativa", "comune": ""},
]

RISPOSTA = [
    {"idsensore": "1", "mese": "2024-01-01T00:00:00.000", "misura": "4.5", "n": "744"},
    # un sensore che non è nel blocco richiesto: non deve comparire
    {"idsensore": "99", "mese": "2024-01-01T00:00:00.000", "misura": "9.9", "n": "10"},
    # valore assente: si omette la riga, non si scrive zero
    {"idsensore": "1", "mese": "2024-02-01T00:00:00.000", "misura": "", "n": "0"},
]


@pytest.fixture
def senza_rete(monkeypatch: pytest.MonkeyPatch):
    chiamate: list[dict] = []

    def finto_socrata(resource, **kwargs):
        chiamate.append({"resource": resource, **kwargs})
        return "finto.json"

    monkeypatch.setattr(ambiente, "socrata_json", finto_socrata)
    monkeypatch.setattr(ambiente, "read_socrata", lambda path: RISPOSTA)
    return chiamate


# --- il registro delle serie --------------------------------------------


def test_ogni_serie_dichiara_unaggregazione_nota() -> None:
    for parametro, (aggregazione, risorse) in ambiente.SERIE_METEO.items():
        assert aggregazione in ambiente.AGGREGAZIONI, parametro
        assert risorse, parametro


def test_la_temperatura_e_una_media_e_la_pioggia_un_totale() -> None:
    """La riga che vale il modulo intero: la media delle piogge non è la pioggia."""
    assert ambiente.SERIE_METEO["Temperatura"][0] == "media"
    assert ambiente.SERIE_METEO["Precipitazione"][0] == "totale"


# --- la selezione dei sensori -------------------------------------------


def test_i_sensori_si_filtrano_per_parametro() -> None:
    scelti = ambiente.sensori_di(SENSORI, "Precipitazione")
    assert [s["id_sensore"] for s in scelti] == ["2"]


def test_un_parametro_senza_serie_non_produce_richieste(senza_rete) -> None:
    """L'umidità esiste in anagrafica e non ha una serie storica: va detto,
    non lasciato dedurre da una tabella che semplicemente non la contiene."""
    assert "Umidità Relativa" not in ambiente.SERIE_METEO
    assert "Umidità Relativa" in ambiente.parametri_scoperti(SENSORI)
    assert ambiente.parametri_scoperti(SENSORI) == ["Umidità Relativa"]


# --- l'aggregazione -----------------------------------------------------


def test_laggregazione_finisce_nella_query_e_nella_riga(senza_rete) -> None:
    righe = ambiente._misure_mensili(
        "risorsa", ambiente.sensori_di(SENSORI, "Temperatura"), "prova", "media"
    )
    assert "avg(valore)" in senza_rete[0]["select"]
    assert righe[0]["aggregazione"] == "media"


def test_il_totale_chiede_una_somma(senza_rete) -> None:
    ambiente._misure_mensili(
        "risorsa", ambiente.sensori_di(SENSORI, "Precipitazione"), "prova", "totale"
    )
    assert "sum(valore)" in senza_rete[0]["select"]


def test_scarta_i_sensori_non_richiesti_e_i_valori_assenti(senza_rete) -> None:
    righe = ambiente._misure_mensili(
        "risorsa", ambiente.sensori_di(SENSORI, "Temperatura"), "prova", "media"
    )
    assert len(righe) == 1
    assert righe[0]["id_sensore"] == "1"
    assert righe[0]["mese"] == "2024-01"
    assert righe[0]["valore"] == "4.50"


def test_il_filtro_di_validita_e_sempre_nella_query(senza_rete) -> None:
    """ARPA marca i dati non validi con −999: senza filtro entrano nelle medie."""
    ambiente._misure_mensili("risorsa", ambiente.sensori_di(SENSORI, "Temperatura"), "p", "media")
    assert ambiente.VALIDO in senza_rete[0]["where"]


def test_lalias_del_valore_non_collide_con_una_colonna_della_fonte(senza_rete) -> None:
    """Il bug che ha rotto il modulo contro l'API viva.

    Con `avg(valore) AS valore`, il `WHERE valore > -100` risolve l'**alias**
    invece della colonna e Socrata risponde `400
    aggregate-in-ungrouped-context`. Senza quel filtro passerebbero le medie
    mensili costruite sui −999 con cui ARPA marca i dati non validi, cioè
    concentrazioni negative.
    """
    ambiente._misure_mensili("risorsa", ambiente.sensori_di(SENSORI, "Temperatura"), "p", "media")
    query = senza_rete[0]
    colonne_fonte = {"valore", "data", "idsensore", "stato", "idoperatore"}
    assert ambiente.ALIAS_VALORE not in colonne_fonte
    assert f"AS {ambiente.ALIAS_VALORE}" in query["select"]
    # e la colonna vera resta interrogabile nel filtro
    assert "valore >" in query["where"]


# --- lo stato delle misure ----------------------------------------------


def righe_finte(coppie: list[tuple[str, int, float]]) -> list[dict[str, str]]:
    """`(mese, n_misure, lettura massima)` -> righe come le scrive il modulo."""
    return [
        {
            "id_sensore": "1", "stazione": "Alfa", "parametro": "Precipitazione",
            "mese": mese, "aggregazione": "totale", "valore": "10",
            "lettura_massima": str(massimo), "n_misure": str(n),
        }
        for mese, n, massimo in coppie
    ]


def test_una_lettura_impossibile_marca_il_mese() -> None:
    """Un solo valore corrotto fa saltare il totale di un mese intero.

    Il caso vero: il pluviometro di Caino registra 109.499 mm in un intervallo
    di dieci minuti nel maggio 2020, e il totale del mese diventa 109.589 mm.
    La fonte non marca quella riga, e il filtro sui −999 non la vede.
    """
    righe = righe_finte([("2020-04", 4320, 12.0), ("2020-05", 4463, 109499.4)])
    ambiente.marca_stato(righe)
    assert righe[0]["stato"] == ambiente.STATO_OK
    assert righe[1]["stato"] == ambiente.STATO_IMPLAUSIBILE


def test_un_mese_quasi_vuoto_e_marcato_ma_non_cancellato() -> None:
    """Una «media mensile» su otto letture non è una media mensile.

    La soglia si calibra sul sensore stesso: la risoluzione cambia da sensore a
    sensore (oraria, dieci minuti, giornaliera per il PM10) e una soglia fissa
    marcherebbe come scarso tutto il particolato.
    """
    righe = righe_finte(
        [("2020-01", 4464, 5.0), ("2020-02", 4176, 5.0), ("2020-03", 4464, 5.0), ("2020-04", 8, 5.0)]
    )
    ambiente.marca_stato(righe)
    assert [r["stato"] for r in righe[:3]] == [ambiente.STATO_OK] * 3
    assert righe[3]["stato"] == ambiente.STATO_COPERTURA
    # marcato, non rimosso: la riga c'è ancora e porta il suo valore
    assert righe[3]["valore"] == "10"


def test_una_risoluzione_bassa_ma_costante_non_e_copertura_scarsa() -> None:
    """Il PM10 si misura una volta al giorno: trenta letture al mese sono
    copertura piena, non copertura scarsa."""
    righe = righe_finte([("2024-01", 31, 5.0), ("2024-02", 29, 5.0), ("2024-03", 30, 5.0)])
    ambiente.marca_stato(righe)
    assert {r["stato"] for r in righe} == {ambiente.STATO_OK}


def test_un_parametro_senza_soglia_dichiarata_non_viene_marcato() -> None:
    """Non si inventano soglie: dove il progetto non sa dichiarare un limite
    fisico, il controllo è solo quello sulla copertura."""
    righe = righe_finte([("2024-01", 744, 999999.0)])
    for riga in righe:
        riga["parametro"] = "Biossido di Azoto"
    ambiente.marca_stato(righe)
    assert "Biossido di Azoto" not in ambiente.LETTURA_MASSIMA
    assert righe[0]["stato"] == ambiente.STATO_OK
