"""L'orchestratore (`build.py`) e l'export per il sito (`web.py`).

Sono i due estremi della pipeline: uno decide **cosa gira e in che ordine**,
l'altro produce il contratto che il sito legge. `test_web.py` verifica già i
cinque invarianti sui JSON *già scritti*; qui si verifica il codice che li
scrive, e il codice che decide di scriverli.

Niente rete: `build.py` si esercita con dataset finti, e `web.build` legge le
tabelle versionate in `dati/processed/` e scrive in una cartella temporanea.
"""

from __future__ import annotations

import csv
import json

import pytest

from conftest import servono_tabelle

from brescia_pipeline import build as B
from brescia_pipeline import web as W


# --- l'orchestratore -----------------------------------------------------


def test_lelenco_dei_dataset_si_stampa_e_esce_bene(capsys) -> None:
    assert B.main(["--list"]) == 0
    uscita = capsys.readouterr().out
    assert "dataset disponibili" in uscita
    for nome in B.DATASETS:
        assert nome in uscita


def test_un_dataset_sconosciuto_e_un_errore_non_un_silenzio(capsys) -> None:
    """Un nome sbagliato deve fermare il build, non farlo girare a vuoto."""
    with pytest.raises(SystemExit):
        B.main(["questo_non_esiste"])
    assert "dataset sconosciuti" in capsys.readouterr().err


def test_lordine_dei_dataset_mette_in_coda_chi_legge_gli_altri() -> None:
    """`sintesi` e `web` leggono le tabelle prodotte dagli altri: se risalissero
    nell'elenco leggerebbero quelle del giorno prima, e nessuno se ne
    accorgerebbe perché il file c'è comunque."""
    nomi = list(B.DATASETS)
    assert nomi[-1] == "web"
    assert nomi[-2] == "sintesi"
    assert nomi[0] == "confini", "la geometria di riferimento apre la fila"


@pytest.fixture
def build_finto(monkeypatch):
    """`build.main` con tutti i dataset sostituiti da funzioni che registrano."""
    chiamati: list[str] = []

    def finto(nome: str):
        def costruisci(comuni):
            assert comuni, f"{nome} è stato chiamato senza comuni"
            chiamati.append(nome)

        return costruisci

    monkeypatch.setattr(B, "DATASETS", {n: finto(n) for n in B.DATASETS})
    monkeypatch.setattr(B.anagrafica, "build", lambda solo_locale=False: {"017029": "Brescia"})
    return chiamati


def test_senza_argomenti_gira_tutto_nellordine_dichiarato(build_finto, capsys) -> None:
    assert B.main([]) == 0
    assert build_finto == list(B.DATASETS)
    assert "build completo" in capsys.readouterr().out


def test_con_dei_nomi_gira_solo_quelli(build_finto, capsys) -> None:
    assert B.main(["prezzi", "omi"]) == 0
    assert build_finto == ["prezzi", "omi"]
    capsys.readouterr()


def test_un_dataset_rotto_non_ferma_gli_altri_ma_fa_fallire_il_build(monkeypatch, capsys) -> None:
    """La regola scritta nel codice: «un dataset rotto non deve fermare gli
    altri». Deve però risultare, altrimenti la CI passa su una tabella mancante.
    """
    fatti: list[str] = []

    def esplode(comuni):
        raise RuntimeError("la fonte non risponde")

    def funziona(nome):
        def costruisci(comuni):
            fatti.append(nome)

        return costruisci

    monkeypatch.setattr(
        B, "DATASETS", {"uno": funziona("uno"), "rotto": esplode, "tre": funziona("tre")}
    )
    monkeypatch.setattr(B.anagrafica, "build", lambda solo_locale=False: {"017029": "Brescia"})

    assert B.main([]) == 1
    uscita = capsys.readouterr().out
    assert fatti == ["uno", "tre"], "un dataset rotto ha fermato quelli dopo"
    assert "FALLITO: la fonte non risponde" in uscita
    assert "dataset falliti: rotto" in uscita


def test_offline_lo_dice_allanagrafica(monkeypatch, capsys) -> None:
    """`--offline` esiste perché la CI non tocchi la rete: se non arrivasse fino
    all'anagrafica, la CI proverebbe comunque a scaricare."""
    visto: dict[str, bool] = {}
    monkeypatch.setattr(B, "DATASETS", {})
    monkeypatch.setattr(
        B.anagrafica, "build",
        lambda solo_locale=False: visto.setdefault("solo_locale", solo_locale) and {} or {"017029": "B"},
    )
    assert B.main(["--offline"]) == 0
    assert visto["solo_locale"] is True
    capsys.readouterr()


# --- l'export per il sito ------------------------------------------------


def test_le_utilita_di_web_fanno_quello_che_dicono() -> None:
    righe = [
        {"codice_istat": "017029", "anno": "2020", "valore": "10"},
        {"codice_istat": "017029", "anno": "2021", "valore": "20"},
        {"codice_istat": "017001", "anno": "2020", "valore": ""},
    ]
    serie = W._serie(righe, lambda r: True)
    assert serie["017029"] == {"2020": 10.0, "2021": 20.0}
    # MET-3, e qui la forma conta: la cella vuota resta nella serie come `None`,
    # non come `0.0` e non sparendo. Arriva così fino al JSON (`null`), e il
    # grafico la salta; uno zero invece si colorerebbe come «non si muove».
    assert serie["017001"]["2020"] is None


def test_il_rapporto_salta_i_denominatori_nulli() -> None:
    """Dividere per zero non deve produrre un infinito né un'eccezione: la
    coppia semplicemente non esiste."""
    numeratore = {"a": {"2020": 10.0}, "b": {"2020": 5.0}}
    denominatore = {"a": {"2020": 100.0}, "b": {"2020": 0.0}}
    fuori = W._rapporto(numeratore, denominatore, 100.0)
    assert fuori["a"]["2020"] == pytest.approx(10.0)
    assert not fuori.get("b")


def test_la_crescita_e_composta_e_su_un_periodo_solo() -> None:
    serie = {"x": {"2018": 100.0, "2024": 200.0}}
    fuori = W._crescita(serie, "2018–2024")
    assert list(fuori["x"]) == ["2018–2024"]
    assert fuori["x"]["2018–2024"] == pytest.approx(12.246, abs=1e-3)


def test_la_crescita_non_si_calcola_su_un_anno_solo_o_da_zero() -> None:
    assert W._crescita({"x": {"2020": 100.0}}, "p") == {}
    assert W._crescita({"x": {"2018": 0.0, "2024": 10.0}}, "p") == {}


def test_i_periodi_escono_ordinati_e_senza_ripetizioni() -> None:
    valori = {"a": {"2021": 1.0, "2019": 2.0}, "b": {"2019": 3.0, "2020": 4.0}}
    assert W._periodi(valori) == ["2019", "2020", "2021"]


def test_larrotondamento_lascia_stare_i_valori_assenti() -> None:
    """Tre decimali: bastano a qualunque grafico e dimezzano il peso dei file.
    Un `None` resta `None` e non diventa uno zero arrotondato."""
    assert W._arrotonda(None) is None
    assert W._arrotonda(1.23456) == 1.235
    assert W._arrotonda(-0.0004) == -0.0


@servono_tabelle
def test_nessuna_fonte_dichiarata_porta_una_lineetta_lunga() -> None:
    """Le costanti `FONTE_*` finiscono nella riga di provenienza sotto ogni
    grafico: sono la scritta più ripetuta del sito."""
    fonti = [v for k, v in vars(W).items() if k.startswith("FONTE_") and isinstance(v, str)]
    assert fonti
    assert not [f for f in fonti if "—" in f]


@servono_tabelle
def test_ogni_indicatore_dichiara_i_campi_del_contratto() -> None:
    for indicatore in W._indicatori():
        for campo in ("id", "label", "unit", "kind", "source", "confidence", "values"):
            assert campo in indicatore, f"{indicatore.get('id')}: manca {campo}"
        assert indicatore["kind"] in {"sequential", "diverging", "categorical"}
        assert indicatore["confidence"] in {"osservato", "derivato", "proxy"}
        assert indicatore["values"], f"{indicatore['id']} non ha nessun valore"


@servono_tabelle
def test_gli_id_degli_indicatori_sono_unici() -> None:
    ids = [i["id"] for i in W._indicatori()]
    assert len(ids) == len(set(ids)), "due indicatori con lo stesso id"


@servono_tabelle
def test_build_scrive_il_registro_e_un_file_per_indicatore(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.setattr(W, "WEB_DATA_DIR", tmp_path)
    W.build({"017029": "Brescia"})
    capsys.readouterr()

    registro = json.loads((tmp_path / "metrics.json").read_text(encoding="utf-8"))
    assert registro
    for voce in registro:
        file_metrica = tmp_path / f"metric_{voce['id']}.json"
        assert file_metrica.exists(), voce["id"]
        contenuto = json.loads(file_metrica.read_text(encoding="utf-8"))
        assert contenuto["id"] == voce["id"]
        assert contenuto["values"]

    manifesto = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    assert manifesto["indicatori"] == len(registro)
    assert manifesto["tabelle"]


@servono_tabelle
def test_il_registro_non_porta_i_valori_e_i_file_si(tmp_path, monkeypatch, capsys) -> None:
    """Il registro si legge tutto in una volta e deve restare piccolo: i valori
    stanno nei file per indicatore, che il sito carica solo quando servono."""
    monkeypatch.setattr(W, "WEB_DATA_DIR", tmp_path)
    W.build({"017029": "Brescia"})
    capsys.readouterr()
    registro = json.loads((tmp_path / "metrics.json").read_text(encoding="utf-8"))
    assert all("values" not in voce for voce in registro)
    assert (tmp_path / "metrics.json").stat().st_size < 60_000


@servono_tabelle
def test_il_geojson_dei_comuni_e_copiato_accanto_ai_json(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.setattr(W, "WEB_DATA_DIR", tmp_path)
    W.build({"017029": "Brescia"})
    capsys.readouterr()
    geo = tmp_path / "comuni.geojson"
    assert geo.exists()
    contenuto = json.loads(geo.read_text(encoding="utf-8"))
    assert len(contenuto["features"]) == 205


@servono_tabelle
def test_le_sezioni_disponibili_escono_dalla_tabella_vera() -> None:
    sezioni = W._sezioni_disponibili()
    assert sezioni
    ids = {s["id"] for s in sezioni}
    # le tre che la quarta storia disegna
    assert {"quota_manifattura", "quota_alloggio_ristorazione", "specializzazione"} <= ids
    for sezione in sezioni:
        assert sezione["values"], sezione["id"]


@servono_tabelle
def test_la_specializzazione_e_la_differenza_fra_le_due_quote() -> None:
    """È il valore che colora la mappa delle due economie: rosso manifatturiero,
    blu turistico. Se non fosse la differenza, il segno non vorrebbe dire
    quello che la didascalia dice."""
    per_id = {s["id"]: s["values"] for s in W._sezioni_disponibili()}
    manifattura = per_id["quota_manifattura"]
    alloggio = per_id["quota_alloggio_ristorazione"]
    specializzazione = per_id["specializzazione"]
    controllati = 0
    for codice, per_anno in specializzazione.items():
        for anno, valore in per_anno.items():
            uno = manifattura.get(codice, {}).get(anno)
            altro = alloggio.get(codice, {}).get(anno)
            if uno is None or altro is None:
                continue
            assert valore == pytest.approx(uno - altro, abs=0.01), codice
            controllati += 1
    assert controllati > 100, f"solo {controllati} comuni confrontati"


def test_scrivi_json_e_deterministico(tmp_path) -> None:
    """Due scritture dello stesso contenuto devono dare lo stesso file, se no
    ogni build sporca il diff di `web/src/data/` senza motivo."""
    destinazione = tmp_path / "prova.json"
    W._scrivi_json(destinazione, {"b": 1, "a": 2})
    prima = destinazione.read_bytes()
    W._scrivi_json(destinazione, {"b": 1, "a": 2})
    assert destinazione.read_bytes() == prima


def test_una_tabella_mancante_esplode_e_dice_cosa_lanciare() -> None:
    """`_leggi` non ripiega su una lista vuota, e fa bene: un export costruito
    su una tabella assente sarebbe un sito con un grafico vuoto invece di un
    build fallito. Chi vuole una tabella facoltativa controlla prima che ci sia,
    come fa `_sezioni_disponibili`."""
    with pytest.raises(FileNotFoundError, match="brescia_pipeline.build"):
        W._leggi("questa_tabella_non_esiste.csv")


def test_una_tabella_facoltativa_assente_non_rompe_lexport(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(W, "PROCESSED_DIR", tmp_path)
    assert W._sezioni_disponibili() == []


@servono_tabelle
def test_le_tabelle_del_manifesto_esistono_davvero(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.setattr(W, "WEB_DATA_DIR", tmp_path)
    W.build({"017029": "Brescia"})
    capsys.readouterr()
    manifesto = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    for voce in manifesto["tabelle"]:
        nome = voce if isinstance(voce, str) else voce.get("nome", voce.get("file", ""))
        assert (W.PROCESSED_DIR / nome).exists(), nome
        with (W.PROCESSED_DIR / nome).open(encoding="utf-8") as handle:
            assert next(csv.reader(handle)), f"{nome} è vuota"
