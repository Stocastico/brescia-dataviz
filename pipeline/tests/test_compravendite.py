"""Test dei volumi di compravendita OMI (NTN), senza rete.

Gli archivi veri stanno in `dati/input/omi/volumi/`; qui se ne costruisce uno
finto con la forma esatta: quattro CSV per anno, separatore `;`, encoding
latino, decimali con la virgola, e — la trappola vera — **la chiave non è il
codice ISTAT ma il codice catastale** (`A034` per Acquafredda), con il nome
della colonna che porta l'anno dentro (`2011_CodCom`, `NTN_2011_Uffici`).

Le cose che qui sbagliano davvero:

- la chiave catastale va tradotta in codice ISTAT, o non si incrocia niente;
- l'NTN è **frazionario** (`2,5`): sono transazioni normalizzate sulla quota di
  proprietà, non teste. Arrotondarle a intero perde metà del significato;
- il file residenziale porta le classi di superficie **e il totale**: sommare
  tutto conta due volte, come le righe «Totale» del turismo;
- i comuni soppressi arrivano col loro codice catastale, e scartarli
  sposterebbe in silenzio il territorio di chi li ha assorbiti.
"""

from __future__ import annotations

import csv
import zipfile
from pathlib import Path

import pytest

from brescia_pipeline.datasets import compravendite

# codice catastale -> codice ISTAT, come lo dà l'elenco ISTAT dei comuni
CATASTALI = {"A034": "017001", "B157": "017029", "A861": "017018"}
COMUNI = {"017001": "Acquafredda", "017029": "Brescia", "017018": "Bienno"}

FILE = {
    "VCN_1_2011_LISTA-COM.csv": [
        "AREA;Regione;prov;2011_CodCom;Comune",
        "Nord Ovest;Lombardia;BS;A034;ACQUAFREDDA",
        "Nord Ovest;Lombardia;BS;B157;BRESCIA",
        "Nord Ovest;Liguria;GE;A388;ARENZANO",
    ],
    "VCN_1_2011_VALORI-COM.csv": [
        "AREA;Regione;prov;2011_CodCom;NTN_2011_Uffici;NTN_2011_Negozi_Lab;"
        "NTN_2011_Depositi_Comm;NTN_2011_TCO_B04;NTN_2011_PRO;NTN_2011_AGR",
        "Nord Ovest;Lombardia;BS;B157;120,5;88,25;12;0;7,5;1",
        "Nord Ovest;Liguria;GE;A388;2;2,5;7,72;0;2;0",
    ],
    "VCN_1_2011_VALORI-PER.csv": [
        "AREA;Regione;prov;2011_CodCom;NTN_2011_Box;NTN_2011_Depositi_Pert",
        "Nord Ovest;Lombardia;BS;B157;900,33;41,5",
    ],
    "VCN_1_2011_VALORI-RES.csv": [
        "AREA;Regione;prov;2011_CodFitt;NTN 2011 fino a 50 mq;NTN 2011  50 -| 85 mq;"
        "NTN 2011  85 -| 115 mq;NTN 2011 115 -| 145 mq;NTN 2011 oltre 145 mq;NTN 2011",
        "Nord Ovest;Lombardia;BS;B157;300,5;700,25;400;150;50,25;1601",
        # comune soppresso: PRESTINE (G935) è territorio di Bienno dal 2016
        "Nord Ovest;Lombardia;BS;G935;5;10;3;1;0;19",
    ],
}


# Il 2017 è l'anno in cui l'intestazione cambia forma: la chiave perde l'anno e
# diventa `COD_COM`, i depositi commerciali diventano «Depositi_Comm_Autorimesse»
# — un'altra definizione, non solo un altro nome —, il totale residenziale si
# chiama `_TOTALE` e una classe di superficie perde il «mq». Su quindici anni di
# forniture l'intestazione cambia una dozzina di volte: il modulo deve reggerlo.
FILE_2017 = {
    "VCN_1_2017_VALORI-COM.csv": [
        "Area;Regione;prov;COD_COM;NTN_2017_Uffici;"
        "NTN_2017_Depositi_Comm_Autorimesse;NTN_2017_PRO",
        "Nord Ovest;Lombardia;BS;B157;130;20,5;9",
    ],
    "VCN_1_2017_VALORI-RES.csv": [
        "Area;Regione;prov;COD_COM;NTN 2017 fino a 50 mq;NTN  2017 oltre 145;"
        "NTN 2017_TOTALE",
        "Nord Ovest;Lombardia;BS;B157;310;60;370",
    ],
}


def _scrivi(cartella: Path, nome_zip: str, file: dict[str, list[str]]) -> None:
    with zipfile.ZipFile(cartella / nome_zip, "w") as zf:
        for nome, righe in file.items():
            zf.writestr(nome, ("\n".join(righe) + "\n").encode("latin-1"))


@pytest.fixture
def tabella(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    volumi = tmp_path / "omi" / "volumi"
    volumi.mkdir(parents=True)
    _scrivi(volumi, "VCN_2011.zip", FILE)
    _scrivi(volumi, "VCN_2017.zip", FILE_2017)

    import brescia_pipeline.tidy as tidy_mod

    uscita = tmp_path / "processed"
    uscita.mkdir()
    monkeypatch.setattr(compravendite, "INPUT_DIR", tmp_path)
    monkeypatch.setattr(compravendite, "catastali", lambda: dict(CATASTALI))
    monkeypatch.setattr(tidy_mod, "PROCESSED_DIR", uscita)
    compravendite.build(COMUNI)

    with (uscita / "compravendite_comuni.csv").open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _riga(righe, comparto, segmento, code="017029"):
    return next(
        r for r in righe
        if r["codice_istat"] == code and r["comparto"] == comparto
        and r["segmento"] == segmento
    )


def test_la_chiave_catastale_diventa_codice_istat(tabella) -> None:
    codici = {r["codice_istat"] for r in tabella}
    # A388 è ARENZANO, in provincia di Genova: fuori dai 205
    assert codici == {"017029", "017018"}, codici
    assert _riga(tabella, "non_residenziale", "uffici")["comune"] == "Brescia"


def test_l_ntn_resta_frazionario(tabella) -> None:
    # 88,25 transazioni normalizzate: arrotondare a 88 perde la quota di proprietà
    assert _riga(tabella, "non_residenziale", "negozi_laboratori")["ntn"] == "88.25"
    assert _riga(tabella, "pertinenze", "box")["ntn"] == "900.33"


def test_le_classi_di_superficie_hanno_etichette_leggibili(tabella) -> None:
    segmenti = {r["segmento"] for r in tabella if r["comparto"] == "residenziale"}
    assert segmenti == {
        "fino a 50 mq", "50-85 mq", "85-115 mq", "115-145 mq", "oltre 145 mq", "totale",
    }, segmenti


def test_il_totale_residenziale_c_e_ed_e_dichiarato(tabella) -> None:
    """Il totale della fonte resta, ma come segmento a sé: sommare tutto raddoppia."""
    del2011 = [r for r in tabella if r["anno"] == "2011"]
    totale = float(_riga(del2011, "residenziale", "totale")["ntn"])
    classi = sum(
        float(r["ntn"]) for r in del2011
        if r["codice_istat"] == "017029" and r["comparto"] == "residenziale"
        and r["segmento"] != "totale"
    )
    assert totale == pytest.approx(classi, abs=0.6), (totale, classi)


def test_il_comune_soppresso_finisce_in_quello_di_oggi(tabella) -> None:
    bienno = [r for r in tabella if r["codice_istat"] == "017018"]
    assert bienno, "le righe di Prestine sono state scartate"
    assert bienno[0]["comune"] == "Bienno"


def test_l_anno_c_e_anche_quando_la_chiave_non_lo_porta(tabella) -> None:
    """Nel 2017 la colonna chiave è `COD_COM`: l'anno va preso dal nome del file."""
    assert {r["anno"] for r in tabella} == {"2011", "2017"}


def test_il_drift_delle_intestazioni_non_perde_colonne(tabella) -> None:
    segmenti = {
        (r["comparto"], r["segmento"]) for r in tabella if r["anno"] == "2017"
    }
    assert segmenti == {
        ("non_residenziale", "uffici"),
        # cambia il nome *e* la definizione: dal 2017 i depositi commerciali
        # comprendono le autorimesse, quindi è un segmento diverso
        ("non_residenziale", "depositi_commerciali_autorimesse"),
        ("non_residenziale", "produttivo"),
        ("residenziale", "fino a 50 mq"),
        ("residenziale", "oltre 145 mq"),   # la fonte scrive «oltre 145», senza mq
        ("residenziale", "totale"),         # e chiama il totale «_TOTALE»
    }, segmenti


def test_i_due_depositi_commerciali_restano_distinti(tabella) -> None:
    """Prima e dopo il 2017 non sono la stessa misura: due segmenti, non uno."""
    nomi = {r["segmento"] for r in tabella if r["comparto"] == "non_residenziale"}
    assert "depositi_commerciali" in nomi              # 2011-2016
    assert "depositi_commerciali_autorimesse" in nomi  # dal 2017
