"""Test degli iscritti e dei laureati MUR, senza rete.

La fonte è un CKAN vero, ma le trappole non stanno nell'API: stanno nei CSV.

- **«Brescia» come ateneo non è «Brescia» come sede.** La Cattolica è **un solo
  ateneo** con codice milanese e quattro sedi, una delle quali è Brescia: chi
  conta gli iscritti per ateneo la perde tutta. È l'avvertenza che `FONTI.md`
  porta da mesi, e qui diventa una tabella;
- **i codici comune non hanno lo zero iniziale.** `17001`, non `017001`: un
  join fatto senza normalizzare non fallisce, restituisce zero righe;
- **Prestine esiste ancora**, come negli archivi OMI: comune soppresso nel 2016,
  che nella serie storica compare fino a quell'anno. Scartarlo sposta il suo
  territorio fuori dalla provincia in silenzio;
- **iscritti e laureati non contano lo stesso anno**: `2024/2025` è un anno
  accademico, `2025` è un anno solare. Nella stessa colonna senza dirlo sono un
  grafico sbagliato;
- l'encoding è **cp1252**, non UTF-8 e nemmeno latin-1: il trattino `–` di
  qualche denominazione è il byte `0x96`, che in latin-1 non è una lettera.
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from brescia_pipeline.datasets import universita

COMUNI = {"017001": "Acquafredda", "017029": "Brescia", "017018": "Bienno"}

FILE = {
    "iscritti_ateneo": [
        "AnnoA;AteneoNOME;AteneoCOD;SESSO;Isc",
        "2024/2025;Brescia;1701;F;8001",
        "2024/2025;Brescia;1701;M;8455",
        "2024/2025;Milano Cattolica;1504;F;27783",
        "2023/2024;Brescia;1701;F;7572",
    ],
    "immatricolati_ateneo": [
        "AnnoA;AteneoNOME;AteneoCOD;SESSO;Immatricolati",
        "2024/2025;Brescia;1701;F;1800",
        "2024/2025;Brescia;1701;M;1791",
        # la serie degli immatricolati comincia dieci anni prima delle altre
        "1998/1999;Brescia;1701;F;900",
    ],
    "laureati_ateneo": [
        "AnnoS;AteneoCOD;AteneoNOME;SESSO;Lau",
        "2025;1701;Brescia;F;1980",
        "2025;1701;Brescia;M;1750",
    ],
    "iscritti_gruppo": [
        "AnnoA;GruppoCOD;GruppoNOME;SESSO;Isc",
        "2024/2025;7;Economico                       ;M;146254",
        "2024/2025;12;Ingegneria industriale;M;184340",
    ],
    "iscritti_sede": [
        "AnnoA;AteneoCOD;AteneoNOME;SedeP;ResidenzaR;ResidenzaP;GruppoCODICE;Isc",
        "2024/2025;1701;Brescia;17;LOMBARDIA;BRESCIA;12;5000",
        "2024/2025;1504;Milano Cattolica;17;LOMBARDIA;BRESCIA;7;4288",
        # stesso ateneo, sede milanese: non è la Brescia che studia
        "2024/2025;1504;Milano Cattolica;15;LOMBARDIA;MILANO;7;20000",
    ],
    "iscritti_residenza": [
        "AnnoA;RegioneRES;ProvinciaRES;CODIstatProv;CODIstatComune;ComuneRES;SESSO;Isc",
        "2024/2025;LOMBARDIA;BRESCIA;17;17001;ACQUAFREDDA;F;21",
        "2024/2025;LOMBARDIA;BRESCIA;17;17029;BRESCIA;M;3500",
        # Prestine (017154), soppresso nel 2016: territorio di Bienno
        "2015/2016;LOMBARDIA;BRESCIA;17;17154;PRESTINE;F;7",
        "2015/2016;LOMBARDIA;BRESCIA;17;17018;BIENNO;F;30",
        "2024/2025;LAZIO;ROMA;58;58091;ROMA;F;40000",
    ],
}


@pytest.fixture()
def tabelle(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    from brescia_pipeline import tidy as tidy_mod

    percorsi = {}
    for nome, righe in FILE.items():
        p = tmp_path / f"{nome}.csv"
        p.write_bytes("\n".join(righe).encode("cp1252"))
        percorsi[nome] = p

    uscita = tmp_path / "processed"
    monkeypatch.setattr(universita, "risorse", lambda: percorsi)
    monkeypatch.setattr(tidy_mod, "PROCESSED_DIR", uscita)

    universita.build(dict(COMUNI))

    def leggi(nome: str):
        with (uscita / nome).open(encoding="utf-8") as handle:
            return list(csv.DictReader(handle))

    return leggi


def test_i_tre_indicatori_stanno_nella_stessa_tabella(tabelle) -> None:
    righe = tabelle("universita_atenei.csv")
    assert {r["indicatore"] for r in righe} == {"iscritti", "immatricolati", "laureati"}


def test_gli_immatricolati_hanno_la_serie_piu_lunga(tabelle) -> None:
    """Comincia nel 1998/99, dieci anni prima degli iscritti per ateneo.

    Chi mette i tre indicatori sullo stesso grafico deve partire dall'anno in
    cui esistono tutti, o la linea degli immatricolati sembra l'unica cosa che
    esisteva prima del 2000.
    """
    righe = tabelle("universita_atenei.csv")
    per_indicatore = {}
    for r in righe:
        per_indicatore.setdefault(r["indicatore"], set()).add(r["anno"])
    assert min(per_indicatore["immatricolati"]) < min(per_indicatore["iscritti"])
    assert "1998" in per_indicatore["immatricolati"]


def test_l_anno_accademico_e_dichiarato_diverso_da_quello_solare(tabelle) -> None:
    """`2024/2025` e `2025` non sono la stessa cosa e non vanno confrontati.

    Ridotti entrambi a un numero e messi nella stessa colonna diventerebbero
    una serie che sembra continua. La colonna `anno_tipo` è lì per rendere il
    confronto una scelta.
    """
    righe = tabelle("universita_atenei.csv")
    isc = [r for r in righe if r["indicatore"] == "iscritti"]
    imm = [r for r in righe if r["indicatore"] == "immatricolati"]
    lau = [r for r in righe if r["indicatore"] == "laureati"]
    assert {r["anno_tipo"] for r in isc} == {"accademico"}
    assert {r["anno_tipo"] for r in imm} == {"accademico"}
    assert {r["anno_tipo"] for r in lau} == {"solare"}
    assert {r["anno"] for r in isc} == {"2024", "2023"}
    assert {r["anno"] for r in lau} == {"2025"}


def test_la_cattolica_a_brescia_c_e_solo_nella_tabella_delle_sedi(tabelle) -> None:
    """L'avvertenza di `FONTI.md`, resa misurabile.

    Per ateneo la Cattolica è milanese e la Brescia che studia perde un quarto
    di sé. Per sede didattica no.
    """
    atenei = tabelle("universita_atenei.csv")
    assert not [r for r in atenei if r["ateneo"] == "Milano Cattolica" and r["anno"] == "2024"
                and r["indicatore"] == "iscritti" and r["ateneo_codice"] == "1701"]

    sedi = tabelle("universita_sedi_brescia.csv")
    cattolica = [r for r in sedi if r["ateneo_codice"] == "1504"]
    assert len(cattolica) == 1
    assert cattolica[0]["iscritti"] == "4288"


def test_le_sedi_fuori_provincia_non_entrano(tabelle) -> None:
    sedi = tabelle("universita_sedi_brescia.csv")
    assert not [r for r in sedi if r["iscritti"] == "20000"]


def test_il_codice_del_gruppo_ha_la_sua_etichetta(tabelle) -> None:
    """Il nome viene dalla fonte stessa, non da un'interpretazione del codice."""
    sedi = tabelle("universita_sedi_brescia.csv")
    gruppi = {r["gruppo_codice"]: r["gruppo"] for r in sedi}
    assert gruppi["7"] == "Economico"
    assert gruppi["12"] == "Ingegneria industriale"


def test_il_codice_comune_prende_lo_zero_iniziale(tabelle) -> None:
    righe = tabelle("universita_residenza_comuni.csv")
    assert {r["codice_istat"] for r in righe} <= set(COMUNI)
    assert [r for r in righe if r["codice_istat"] == "017001"]


def test_il_comune_soppresso_si_somma_a_quello_di_oggi(tabelle) -> None:
    """Prestine (017154) è territorio di Bienno: 7 + 30 = 37, non due righe."""
    righe = tabelle("universita_residenza_comuni.csv")
    bienno = [r for r in righe if r["codice_istat"] == "017018" and r["anno"] == "2015"]
    assert len(bienno) == 1
    assert bienno[0]["iscritti"] == "37"


def test_le_altre_province_non_entrano_nella_tabella_comunale(tabelle) -> None:
    righe = tabelle("universita_residenza_comuni.csv")
    assert not [r for r in righe if r["iscritti"] == "40000"]


def test_il_nome_del_comune_e_quello_del_progetto(tabelle) -> None:
    """La fonte scrive `ACQUAFREDDA`; la tabella su cui tutto fa join no."""
    righe = tabelle("universita_residenza_comuni.csv")
    assert {r["comune"] for r in righe} <= set(COMUNI.values())


def test_le_intestazioni_sono_quelle_dichiarate(tabelle) -> None:
    for nome, colonne in [
        ("universita_atenei.csv", universita.COLUMNS_ATENEI),
        ("universita_sedi_brescia.csv", universita.COLUMNS_SEDI),
        ("universita_residenza_comuni.csv", universita.COLUMNS_RESIDENZA),
    ]:
        assert list(tabelle(nome)[0]) == colonne


def test_le_righe_sono_ordinate(tabelle) -> None:
    righe = tabelle("universita_residenza_comuni.csv")
    chiavi = [(r["codice_istat"], r["anno"], r["sesso"]) for r in righe]
    assert chiavi == sorted(chiavi)


# --- i pezzi puri ---------------------------------------------------------


def test_l_anno_accademico_diventa_l_anno_di_apertura() -> None:
    assert universita.anno_di("2024/2025") == "2024"
    assert universita.anno_di("2025") == "2025"


def test_un_anno_che_non_si_legge_ferma_il_build() -> None:
    with pytest.raises(RuntimeError, match="anno"):
        universita.anno_di("a.a. scorso")


def test_la_risorsa_si_cerca_per_nome_di_file() -> None:
    pacchetto = {
        "resources": [
            {"url": "https://x/download/01_iscrittixanno.csv"},
            {"url": "https://x/download/02_iscrittixateneo.csv"},
        ]
    }
    assert universita.url_risorsa(pacchetto, "02_iscrittixateneo.csv").endswith(
        "02_iscrittixateneo.csv"
    )


def test_una_risorsa_sparita_ferma_il_build() -> None:
    with pytest.raises(RuntimeError, match="99_inesistente.csv"):
        universita.url_risorsa({"resources": []}, "99_inesistente.csv")
