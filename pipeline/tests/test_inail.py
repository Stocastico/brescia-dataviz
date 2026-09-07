"""Infortuni INAIL, senza rete.

Due cose qui non sono dettagli tecnici.

**Il mese va a due cifre.** Con `6` la fonte risponde «Dati non trovati», con
`06` risponde. Sembra una copertura mancante e non lo è: durante la
ricognizione questo errore ha fatto credere che esistessero solo ottobre,
novembre e dicembre, che sono gli unici mesi già a due cifre. Qui la funzione
rifiuta un mese di una cifra invece di mandarlo e ricevere un vuoto.

**L'aggregazione non è una comodità, è un impegno.** L'API dà microdati per
singolo caso; il sito dichiara che tutte le fonti del progetto sono aggregate.
Il modulo aggrega prima di scrivere, e questi test verificano che nel prodotto
non finisca niente di individuale.
"""

from __future__ import annotations

import json

import pytest

from brescia_pipeline.datasets import inail

CASI = [
    # Brescia, costruzioni, sopravvissuto
    {"LuogoAccadimento": "017", "SettoreAttivitaEconomica": "F 43390", "DataMorte": "None",
     "Eta": "44", "Genere": "M", "IdentificativoInfortunato": "979776"},
    # Brescia, manifattura, mortale
    {"LuogoAccadimento": "017", "SettoreAttivitaEconomica": "C 25620", "DataMorte": "03/05/2023",
     "Eta": "57", "Genere": "M", "IdentificativoInfortunato": "112233"},
    # Brescia, manifattura, sopravvissuto
    {"LuogoAccadimento": "017", "SettoreAttivitaEconomica": "C 24100", "DataMorte": "None",
     "Eta": "31", "Genere": "F", "IdentificativoInfortunato": "445566"},
    # Milano
    {"LuogoAccadimento": "015", "SettoreAttivitaEconomica": "G 47110", "DataMorte": "None",
     "Eta": "29", "Genere": "F", "IdentificativoInfortunato": "778899"},
    # settore non determinato
    {"LuogoAccadimento": "017", "SettoreAttivitaEconomica": "ND", "DataMorte": "None",
     "Eta": "50", "Genere": "M", "IdentificativoInfortunato": "990011"},
    # senza luogo: si scarta, non si inventa
    {"LuogoAccadimento": "-1", "SettoreAttivitaEconomica": "C 25620", "DataMorte": "None",
     "Eta": "40", "Genere": "M", "IdentificativoInfortunato": "223344"},
]


def test_il_mese_a_una_cifra_e_un_errore_esplicito() -> None:
    """Meglio un `ValueError` che una risposta vuota che sembra copertura."""
    with pytest.raises(ValueError, match="due cifre"):
        inail.scarica("Lombardia", "2023", "6")


def test_la_sezione_ateco_e_la_lettera() -> None:
    assert inail._sezione("F 43390") == "F"
    assert inail._sezione("C 25620") == "C"
    assert inail._sezione("ND") == "non determinato"
    assert inail._sezione("") == "non determinato"
    assert inail._sezione(None) == "non determinato"


def test_i_casi_diventano_conteggi_per_provincia_e_sezione() -> None:
    totali = inail.aggrega(CASI, "2023")
    assert totali[("017", "C", "denunce")] == 2
    assert totali[("017", "F", "denunce")] == 1
    assert totali[("017", "non determinato", "denunce")] == 1
    assert totali[("015", "G", "denunce")] == 1


def test_il_totale_provinciale_c_e_ed_e_la_somma() -> None:
    totali = inail.aggrega(CASI, "2023")
    per_sezione = sum(
        v for (prov, sez, ind), v in totali.items()
        if prov == "017" and ind == "denunce" and sez != "totale"
    )
    assert totali[("017", "totale", "denunce")] == per_sezione == 4


def test_i_casi_mortali_sono_un_sottoinsieme_delle_denunce() -> None:
    """Non una colonna da sommare accanto: un morto è anche un denunciato."""
    totali = inail.aggrega(CASI, "2023")
    assert totali[("017", "totale", "casi_mortali")] == 1
    assert totali[("017", "C", "casi_mortali")] == 1
    assert totali[("017", "totale", "casi_mortali")] <= totali[("017", "totale", "denunce")]


def test_datamorte_none_non_conta_come_morte() -> None:
    """La fonte scrive la stringa `'None'`, non un campo vuoto: leggerla come
    un valore presente conterebbe tutti i casi come mortali."""
    totali = inail.aggrega(
        [{"LuogoAccadimento": "017", "SettoreAttivitaEconomica": "C 1", "DataMorte": "None"}],
        "2023",
    )
    assert ("017", "totale", "casi_mortali") not in totali


def test_i_casi_senza_luogo_si_scartano() -> None:
    totali = inail.aggrega(CASI, "2023")
    assert not [k for k in totali if k[0] == "-1"]
    assert sum(v for (_, sez, ind), v in totali.items()
               if sez == "totale" and ind == "denunce") == 5


@pytest.fixture()
def tabella(tmp_path, monkeypatch):
    from brescia_pipeline import tidy as tidy_mod

    monkeypatch.setattr(inail, "REGIONI", ["Lombardia"])
    monkeypatch.setattr(inail, "ANNI", ["2023", "2024"])
    monkeypatch.setattr(inail, "MESI", ["01"])
    monkeypatch.setattr(
        inail, "scarica",
        lambda regione, anno, mese: CASI if anno == "2023" else [],
    )
    monkeypatch.setattr(tidy_mod, "PROCESSED_DIR", tmp_path)

    inail.build({})
    import csv

    with (tmp_path / "infortuni_province.csv").open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_nel_prodotto_non_finisce_niente_di_individuale(tabella) -> None:
    """L'impegno del docstring, verificato: né età, né sesso, né date, né id."""
    assert list(tabella[0]) == inail.COLUMNS
    vietate = {"eta", "genere", "datamorte", "dataaccadimento", "identificativoinfortunato"}
    assert not vietate & {c.lower().replace("_", "") for c in tabella[0]}
    # e nessun valore è un identificativo della fonte
    assert "979776" not in {r["valore"] for r in tabella}


def test_un_anno_senza_dati_non_entra(tabella) -> None:
    """La finestra della fonte scorre: un anno vuoto si salta, non ferma."""
    assert {r["anno"] for r in tabella} == {"2023"}


def test_la_provincia_prende_il_nome(tabella) -> None:
    nomi = {r["codice_provincia"]: r["provincia"] for r in tabella}
    assert nomi["017"] == "Brescia"


def test_le_righe_sono_ordinate(tabella) -> None:
    chiavi = [(r["codice_provincia"], r["anno"], r["sezione_ateco"], r["indicatore"])
              for r in tabella]
    assert chiavi == sorted(chiavi)


def test_una_fonte_muta_ferma_il_build(tmp_path, monkeypatch) -> None:
    from brescia_pipeline import tidy as tidy_mod

    monkeypatch.setattr(inail, "ANNI", ["2023"])
    monkeypatch.setattr(inail, "MESI", ["01"])
    monkeypatch.setattr(inail, "scarica", lambda regione, anno, mese: [])
    monkeypatch.setattr(tidy_mod, "PROCESSED_DIR", tmp_path)

    with pytest.raises(RuntimeError, match="due cifre|nessun infortunio"):
        inail.build({})


class _Risposta:
    def __init__(self, stato: int, testo: str) -> None:
        self.status_code = stato
        self.text = testo
        self.content = testo.encode()

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise AssertionError(f"raise_for_status chiamato su {self.status_code}")


def test_un_mese_inesistente_e_una_lista_vuota_non_un_guasto(tmp_path, monkeypatch) -> None:
    """Il 500 con «Dati non trovati» è **una risposta**, non un errore di rete.

    Passandolo a `fetch()` diventavano cinque tentativi e quattro minuti di
    attese per un mese che non esiste, e alla fine un'eccezione. Qui deve
    tornare vuoto e subito, senza nemmeno scrivere in cache.
    """
    monkeypatch.setattr(inail, "RAW_DIR", tmp_path)
    monkeypatch.setattr(
        inail.requests, "get",
        lambda *a, **k: _Risposta(500, json.dumps({"error": "Dati non trovati"})),
    )
    assert inail.scarica("Lombardia", "2019", "06") == []
    assert not list(tmp_path.glob("*.json")), "un mese inesistente non va messo in cache"


def test_un_cinquecento_diverso_resta_un_guasto(tmp_path, monkeypatch) -> None:
    """Solo quel messaggio è una risposta: un 500 qualsiasi deve fallire."""
    monkeypatch.setattr(inail, "RAW_DIR", tmp_path)
    monkeypatch.setattr(
        inail.requests, "get", lambda *a, **k: _Risposta(503, "Service Unavailable")
    )
    with pytest.raises(AssertionError, match="503"):
        inail.scarica("Lombardia", "2023", "06")


def test_la_cache_si_rilegge_senza_rete(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(inail, "RAW_DIR", tmp_path)
    (tmp_path / "inail_infortuni_lombardia_2023_06.json").write_text(
        json.dumps({inail.CHIAVE: CASI}), encoding="utf-8"
    )
    # nessun monkeypatch su requests: se toccasse la rete, il guardiano scatta
    assert len(inail.scarica("Lombardia", "2023", "06")) == len(CASI)
