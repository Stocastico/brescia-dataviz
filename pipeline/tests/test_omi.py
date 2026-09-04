"""Test delle quotazioni OMI, senza rete e senza gli archivi veri.

Gli archivi dell'Agenzia stanno in `dati/input/omi/` e non si possono
riscaricare da un URL, quindi qui se ne costruisce uno finto con **la forma
esatta** di quelli veri: didascalia prima dell'intestazione, separatore `;`,
decimali con la virgola, encoding latino, `Comune_ISTAT` con la cifra della
regione davanti.

Le quattro cose che qui sbagliano davvero, e che il test copre:

- la chiave `3017029` va normalizzata in `017029`, o l'incrocio con tutte le
  altre tabelle del progetto non torna (è MET-13);
- `11,2` è undici virgola due, non centododici;
- l'aggregazione per comune tiene **solo lo stato conservativo prevalente**
  (`Stato_prev = P`): mediare «ottimo» e «scadente» della stessa zona produce un
  numero che non corrisponde a nessun immobile;
- €/m² su superficie **lorda** e su superficie **netta** non stanno nella stessa
  media: la base è una dimensione della tabella, non una nota.
"""

from __future__ import annotations

import csv
import zipfile
from pathlib import Path

import pytest

from brescia_pipeline.datasets import omi

COMUNI = {"017029": "Brescia", "017001": "Acquafredda", "017018": "Bienno"}

DIDASCALIA = (
    "Quotazioni Immobiliari : Valori di Mercato - Semestre 2015/2 - "
    "elaborazione del 04-SET-26"
)
INTESTAZIONE = (
    "Area_territoriale;Regione;Prov;Comune_ISTAT;Comune_cat;Sez;Comune_amm;"
    "Comune_descrizione;Fascia;Zona;LinkZona;Cod_Tip;Descr_Tipologia;Stato;"
    "Stato_prev;Compr_min;Compr_max;Sup_NL_compr;Loc_min;Loc_max;Sup_NL_loc;"
)

RIGHE = [
    # Brescia, zona B1: due stati conservativi, uno solo prevalente
    "NORD-OVEST;LOMBARDIA;BS;3017029;C3AA; ;B157;BRESCIA;B;B1;BS00000061;20;"
    "Abitazioni civili;NORMALE;P;2260;2540;L;11,2;13,5;L;",
    "NORD-OVEST;LOMBARDIA;BS;3017029;C3AA; ;B157;BRESCIA;B;B1;BS00000061;20;"
    "Abitazioni civili;OTTIMO;N;2800;3200;L;14,0;16,0;L;",
    # Brescia, zona D1: stessa tipologia, altra zona -> entra nella media
    "NORD-OVEST;LOMBARDIA;BS;3017029;C3AA; ;B157;BRESCIA;D;D1;BS00000062;20;"
    "Abitazioni civili;NORMALE;P;1500;1900;L;7,0;9,0;L;",
    # Brescia, box: altra tipologia -> non si mescola con le abitazioni
    "NORD-OVEST;LOMBARDIA;BS;3017029;C3AA; ;B157;BRESCIA;B;B1;BS00000061;13;"
    "Box;NORMALE;P;1100;1600;L;4,4;6,2;L;",
    # Acquafredda: base superficie NETTA -> media separata da quella lorda
    "NORD-OVEST;LOMBARDIA;BS;3017001;A052; ;A052;ACQUAFREDDA;R;R1;BS00000901;20;"
    "Abitazioni civili;NORMALE;P;800;1000;N;3,0;4,0;N;",
    # comune fuori provincia: deve sparire nel filtro
    "NORD-OVEST;LOMBARDIA;MI;3015146;A100; ;F205;MILANO;B;B1;MI00000001;20;"
    "Abitazioni civili;NORMALE;P;9000;9900;L;30,0;40,0;L;",
    # valore assente: non deve diventare uno zero
    "NORD-OVEST;LOMBARDIA;BS;3017001;A052; ;A052;ACQUAFREDDA;R;R2;BS00000902;20;"
    "Abitazioni civili;NORMALE;P;;;N;;;N;",
    # comune soppresso: PRESTINE è territorio di Bienno dal 2016
    "NORD-OVEST;LOMBARDIA;BS;3017154;G935; ;G935;PRESTINE;R;R1;BS00002858;20;"
    "Abitazioni civili;NORMALE;P;700;900;L;2,0;3,0;L;",
]


@pytest.fixture
def archivio(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Un archivio OMI finto in una `dati/input/omi/quotazioni/` provvisoria."""
    cartella = tmp_path / "omi" / "quotazioni"
    cartella.mkdir(parents=True)
    contenuto = "\n".join([DIDASCALIA, INTESTAZIONE, *RIGHE]) + "\n"
    with zipfile.ZipFile(cartella / "QI_2015S2.zip", "w") as zf:
        zf.writestr("QI_1424949_1_20152_VALORI.csv", contenuto.encode("latin-1"))
        zf.writestr("QI_1424949_1_20152_ZONE.csv", b"Area_territoriale;Regione\n")
    monkeypatch.setattr(omi, "INPUT_DIR", tmp_path)
    return cartella


@pytest.fixture
def tabelle(archivio, tmp_path, monkeypatch):
    """Costruisce le due tabelle in una `dati/processed/` provvisoria."""
    import brescia_pipeline.tidy as tidy_mod

    uscita = tmp_path / "processed"
    uscita.mkdir()
    monkeypatch.setattr(tidy_mod, "PROCESSED_DIR", uscita)
    omi.build(COMUNI)
    return uscita


def _righe(uscita: Path, nome: str) -> list[dict[str, str]]:
    with (uscita / nome).open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_il_codice_comune_perde_la_cifra_della_regione(tabelle) -> None:
    zone = _righe(tabelle, "quotazioni_zone.csv")
    codici = {r["codice_istat"] for r in zone}
    # 017018 è Bienno, dove finisce la riga del soppresso Prestine (vedi in fondo)
    assert codici == {"017029", "017001", "017018"}, codici


def test_i_comuni_fuori_provincia_spariscono_nel_filtro(tabelle) -> None:
    zone = _righe(tabelle, "quotazioni_zone.csv")
    assert not [r for r in zone if r["comune"].upper() == "MILANO"]


def test_il_semestre_viene_dalla_didascalia(tabelle) -> None:
    zone = _righe(tabelle, "quotazioni_zone.csv")
    assert {r["anno"] for r in zone} == {"2015"}
    assert {r["semestre"] for r in zone} == {"2"}


def test_i_decimali_con_la_virgola_restano_decimali(tabelle) -> None:
    zone = _righe(tabelle, "quotazioni_zone.csv")
    riga = next(
        r for r in zone
        if r["codice_istat"] == "017029" and r["zona"] == "B1"
        and r["tipologia"] == "Abitazioni civili" and r["stato"] == "NORMALE"
    )
    assert riga["affitto_min"] == "11.2", riga
    assert riga["vendita_min"] == "2260"


def test_un_valore_assente_non_diventa_zero(tabelle) -> None:
    zone = _righe(tabelle, "quotazioni_zone.csv")
    vuote = [r for r in zone if r["zona"] == "R2"]
    assert vuote == [] or all(r["vendita_min"] == "" for r in vuote)
    comuni = _righe(tabelle, "quotazioni_comuni.csv")
    acqua = [r for r in comuni if r["codice_istat"] == "017001"]
    assert all(r["minimo"] != "0" for r in acqua), acqua


def test_la_media_comunale_usa_solo_lo_stato_prevalente(tabelle) -> None:
    comuni = _righe(tabelle, "quotazioni_comuni.csv")
    riga = next(
        r for r in comuni
        if r["codice_istat"] == "017029" and r["tipologia"] == "Abitazioni civili"
        and r["mercato"] == "vendita"
    )
    # zone prevalenti: B1 (2260-2540, punto medio 2400) e D1 (1500-1900, 1700).
    # La riga OTTIMO di B1 (Stato_prev = N) non entra.
    assert riga["zone"] == "2", riga
    assert riga["media"] == "2050", riga
    assert riga["minimo"] == "1500" and riga["massimo"] == "2540", riga


def test_le_tipologie_non_si_mescolano(tabelle) -> None:
    comuni = _righe(tabelle, "quotazioni_comuni.csv")
    tipologie = {r["tipologia"] for r in comuni if r["codice_istat"] == "017029"}
    assert tipologie == {"Abitazioni civili", "Box"}, tipologie


def test_superficie_lorda_e_netta_stanno_in_righe_diverse(tabelle) -> None:
    comuni = _righe(tabelle, "quotazioni_comuni.csv")
    basi = {(r["codice_istat"], r["base_superficie"]) for r in comuni}
    assert ("017029", "lorda") in basi
    assert ("017001", "netta") in basi
    # e nessuna riga mescola le due
    assert all(r["base_superficie"] in {"lorda", "netta"} for r in comuni)


def test_la_grana_zona_tiene_una_riga_per_record_pubblicato(tabelle) -> None:
    zone = _righe(tabelle, "quotazioni_zone.csv")
    chiavi = [
        (r["codice_istat"], r["anno"], r["semestre"], r["zona"], r["tipologia"], r["stato"])
        for r in zone
    ]
    assert len(chiavi) == len(set(chiavi)), "la grana zona ha righe duplicate"
    # sei record dei comuni della provincia, meno quello tutto vuoto
    assert len(zone) == 6, zone


def test_il_comune_soppresso_finisce_in_quello_di_oggi(tabelle) -> None:
    """PRESTINE (017154) esiste nell'OMI fino al 2015/2: dal 2016 è Bienno.

    Scartarlo perderebbe dodici semestri e renderebbe la serie di Bienno
    territorialmente incoerente — pre-2016 senza le sue zone, dal 2016 con —
    che è il modo silenzioso di sbagliare un confronto ventennale.
    """
    zone = _righe(tabelle, "quotazioni_zone.csv")
    prestine = [r for r in zone if r["link_zona"] == "BS00002858"]
    assert prestine, "le righe di Prestine sono state scartate"
    assert prestine[0]["codice_istat"] == "017018", prestine[0]
    assert prestine[0]["comune"] == "Bienno", prestine[0]
