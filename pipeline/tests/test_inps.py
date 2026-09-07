"""Retribuzioni INPS per provincia, senza rete.

Questa fonte ha un'API che non è documentata da nessuna parte, e tre modi di
fallire in silenzio. I test li fissano tutti e tre, perché ognuno è costato
tempo a trovarlo.

**Il più caro è il parsing dei numeri.** L'INPS scrive `702.557` per
settecentomiladuecentocinquantasette, e `tidy.to_number` — che è la funzione
che tutto il resto del progetto usa — legge quella stringa come *settecento
virgola cinque*. Non fallisce: restituisce un numero plausibile con l'ordine di
grandezza sbagliato. In un anno solo, **106 valori su 321** hanno quella forma.
È il motivo per cui questo modulo ha un parser suo.
"""

from __future__ import annotations

import json

import pytest

from brescia_pipeline.datasets import inps


# --- il parser dei numeri, che è il punto ------------------------------


def test_il_punto_e_separatore_di_migliaia() -> None:
    assert inps.intero("702.557") == 702557
    assert inps.intero("19.069.749.042") == 19069749042
    assert inps.intero("447.884") == 447884
    assert inps.intero("909") == 909


def test_non_e_quello_che_farebbe_to_number() -> None:
    """Il contro-test che dà il senso a tutto il resto.

    Se un giorno qualcuno «semplificasse» questo modulo usando l'helper
    condiviso, questa asserzione dice cosa succede: Torino passerebbe da
    settecentomila lavoratori a settecento.
    """
    from brescia_pipeline.tidy import to_number

    assert to_number("702.557") == pytest.approx(702.557)
    assert inps.intero("702.557") == 702557
    assert inps.intero("702.557") == round(1000 * to_number("702.557"))


def test_una_forma_inattesa_ferma_il_build() -> None:
    """Meglio un errore che un numero arrotondato a caso."""
    for sbagliato in ("1.23", "12.3456", "1,5", "abc", "1.234.56"):
        with pytest.raises(RuntimeError, match="forma non prevista"):
            inps.intero(sbagliato)


def test_i_vuoti_sono_dati_mancanti_non_zeri() -> None:
    assert inps.intero(None) is None
    assert inps.intero("") is None
    assert inps.intero("-") is None


# --- il corpo della richiesta -------------------------------------------


def test_il_corpo_non_contiene_spazi() -> None:
    """Con gli spazi il server risponde parlando di Base-64.

    È la trappola numero uno del modulo: `json=` di `requests` aggiunge `", "`
    e `": "`, e la richiesta smette di funzionare senza dire perché.
    """
    corpo = inps._corpo("525", "2024")
    assert b", " not in corpo
    assert b": " not in corpo
    assert corpo == json.dumps(json.loads(corpo), separators=(",", ":")).encode()


def test_il_corpo_chiede_la_provincia_e_le_tre_misure() -> None:
    richiesta = json.loads(inps._corpo("492", "2021"))
    assert richiesta["id_osservatorio"] == "492"
    assert richiesta["selections"]["filters"][0]["values"] == ["2021"]
    assert [r["id"] for r in richiesta["selections"]["rows"]] == ["Provincia"]
    assert {m["id"] for m in richiesta["selections"]["measures"]} == set(inps.MISURE)


# --- la traduzione dei nomi --------------------------------------------


def _voce(nome: str, lavoratori: str = "1.000", retribuzione: str = "30.000.000",
          giornate: str = "250.000") -> dict:
    return {
        "value": nome,
        "measures": [
            {"label": "lav_annoSUM", "value": lavoratori},
            {"label": "RRSUM", "value": retribuzione},
            {"label": "GGSUM", "value": giornate},
        ],
    }


@pytest.fixture()
def tabella(tmp_path, monkeypatch):
    from brescia_pipeline import tidy as tidy_mod

    monkeypatch.setattr(inps, "OSSERVATORI", {"525": ["2024"]})
    monkeypatch.setattr(inps, "province_italiane", lambda: {
        "017": ("Brescia", "Lombardia"),
        "040": ("Forlì-Cesena", "Emilia-Romagna"),
        "021": ("Bolzano/Bozen", "Trentino-Alto Adige/Südtirol"),
    })
    monkeypatch.setattr(inps, "scarica", lambda oss, anno: [
        _voce("Brescia", "447.884", "11.384.000.000", "112.000.000"),
        _voce("Forli'-Cesena"),
        _voce("Provincia Autonoma di Bolzano/Bozen"),
        _voce("Estero"),
        _voce("Totale:", "20.000.000", "500.000.000.000", "5.000.000.000"),
    ])
    monkeypatch.setattr(tidy_mod, "PROCESSED_DIR", tmp_path)

    inps.build({})
    import csv

    with (tmp_path / "retribuzioni_province.csv").open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_il_totale_non_diventa_una_provincia(tabella) -> None:
    """`Totale:` arriva perché la richiesta porta `totalRow`.

    Tenerlo raddoppierebbe l'Italia: è la stessa trappola delle righe «Totale»
    dei flussi turistici.
    """
    assert not [r for r in tabella if r["valore"] == "20000000"]
    assert {r["codice_provincia"] for r in tabella} == {"017", "040", "021"}


def test_l_estero_non_e_una_provincia(tabella) -> None:
    assert "Estero" not in {r["provincia"] for r in tabella}


def test_i_nomi_dell_inps_diventano_quelli_istat(tabella) -> None:
    """L'apostrofo al posto dell'accento, e il titolo davanti alla provincia."""
    nomi = {r["codice_provincia"]: r["provincia"] for r in tabella}
    assert nomi["040"] == "Forlì-Cesena"
    assert nomi["021"] == "Bolzano/Bozen"


def test_un_nome_ignoto_ferma_il_build(tmp_path, monkeypatch) -> None:
    from brescia_pipeline import tidy as tidy_mod

    monkeypatch.setattr(inps, "OSSERVATORI", {"525": ["2024"]})
    monkeypatch.setattr(inps, "province_italiane", lambda: {"017": ("Brescia", "Lombardia")})
    monkeypatch.setattr(inps, "scarica", lambda oss, anno: [_voce("Provincia di Atlantide")])
    monkeypatch.setattr(tidy_mod, "PROCESSED_DIR", tmp_path)

    with pytest.raises(RuntimeError, match="Atlantide"):
        inps.build({})


def test_le_tre_misure_diventano_tre_righe(tabella) -> None:
    brescia = {r["indicatore"]: r["valore"] for r in tabella if r["codice_provincia"] == "017"}
    assert brescia == {
        "lavoratori": "447884",
        "retribuzione_totale": "11384000000",
        "giornate_retribuite": "112000000",
    }


def test_la_retribuzione_media_e_un_rapporto_fra_conteggi(tabella) -> None:
    """Non è calcolata qui, e questo test dice che si può calcolare: la fonte
    dà numeratore e denominatore, quindi la media non è una stima."""
    brescia = {r["indicatore"]: int(r["valore"]) for r in tabella if r["codice_provincia"] == "017"}
    media = brescia["retribuzione_totale"] / brescia["lavoratori"]
    assert 25000 < media < 26000


def test_le_righe_sono_ordinate(tabella) -> None:
    chiavi = [(r["codice_provincia"], r["anno"], r["indicatore"]) for r in tabella]
    assert chiavi == sorted(chiavi)


def test_l_intestazione_e_quella_dichiarata(tabella) -> None:
    assert list(tabella[0]) == inps.COLUMNS
