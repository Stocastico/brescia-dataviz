"""Test dell'NTN provinciale e di capoluogo, senza rete.

Il gemello di `test_compravendite.py`, ma la fornitura è un'altra cosa: là il
dettaglio comunale annuale che si scarica a mano, qui la serie **trimestrale**
che l'Agenzia pubblica in chiaro. Cambiano la chiave, la forma e le trappole.

Le cose che qui sbagliano davvero:

- **la chiave è la sigla automobilistica**, non un codice. `province.py` lo dice
  da sempre — «la sigla non è una chiave stabile» — e qui si vede: la fornitura
  usa ancora `FO` e `PS`, sigle che l'elenco ISTAT non ha più. Tradurle a
  intuito dal nome è l'errore di MET-13 rifatto;
- **le colonne sono periodi**, e nei provvisori portano accanto la superficie
  normalizzata (`2025_1_PROVV_SUP_NORM`). Leggerla come se fosse un NTN
  mescolerebbe metri quadri e transazioni nella stessa colonna;
- **`cap` non è un comune**: è il capoluogo contro tutto il resto della
  provincia. Sommare le due righe dà la provincia, tenerne una sola dà una
  metà senza dirlo;
- l'NTN è **frazionario** anche qui;
- il definitivo e il provvisorio **non sono la stessa cifra**, e finiscono nella
  stessa tabella: senza `stato` una serie 2011-2026 nasce incollando due
  misure diverse (è la lezione di MET-17).
"""

from __future__ import annotations

import csv
import io
import zipfile
from pathlib import Path

import pytest

from brescia_pipeline.datasets import compravendite_province as cp

# sigla -> (codice provincia, nome, regione), come lo dà l'elenco ISTAT
PROVINCE = {
    "BS": ("017", "Brescia", "Lombardia"),
    "GE": ("010", "Genova", "Liguria"),
    "FC": ("040", "Forlì-Cesena", "Emilia-Romagna"),
}

DEFINITIVO = {
    "RES.csv": [
        "Area;Regione;prov;Cap;2011_1;2011_2",
        "Nord Ovest;Lombardia;BS;cap;472,63;510,5",
        "Nord Ovest;Lombardia;BS;NonCap;2423,88;2500",
        "Nord Ovest;Liguria;GE;cap;1619,97;1950,82",
        # sigla storica: la fornitura non ha mai smesso di usarla
        "Nord Est;Emilia-Romagna;FO;cap;300,25;310",
    ],
    "PER_BOX.csv": [
        "Area;Regione;prov;Cap;2011_1;2011_2",
        "Nord Ovest;Lombardia;BS;cap;818,57;902,73",
    ],
    "PER_DEPOSITI.csv": [
        "Area;Regione;prov;Cap;2011_1;2011_2",
        "Nord Ovest;Lombardia;BS;cap;201,31;280,95",
    ],
    # solo 2023-2024: non è una serie, e non deve entrare
    "RES_SUP.csv": [
        "Area;Regione;Prov;Cap;2023_1_SUP_NORM",
        "Nord Ovest;Lombardia;BS;cap;184383,2",
    ],
}

PROVVISORIO = {
    "RES.csv": [
        "Area;Regione;Prov;Cap;2025_1_PROVV_NTN;2025_1_PROVV_SUP_NORM",
        "Nord Ovest;Lombardia;BS;cap;727,24;95000,125",
    ],
}


def _zip(percorso: Path, file: dict[str, list[str]]) -> Path:
    percorso.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(percorso, "w") as zf:
        for nome, righe in file.items():
            zf.writestr(nome, "\n".join(righe).encode("latin-1"))
    return percorso


@pytest.fixture()
def tabella(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    from brescia_pipeline import tidy as tidy_mod

    archivi = {
        "definitivo": _zip(tmp_path / "def.zip", DEFINITIVO),
        "provvisorio": _zip(tmp_path / "provv.zip", PROVVISORIO),
    }
    uscita = tmp_path / "processed"
    monkeypatch.setattr(cp, "province_per_sigla", lambda: dict(PROVINCE))
    monkeypatch.setattr(cp, "scarica_archivi", lambda: archivi)
    monkeypatch.setattr(tidy_mod, "PROCESSED_DIR", uscita)

    cp.build({})
    with (uscita / "compravendite_province.csv").open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _righe(righe, **filtri):
    return [r for r in righe if all(r[k] == v for k, v in filtri.items())]


def test_la_sigla_diventa_codice_di_provincia(tabella) -> None:
    riga = _righe(tabella, codice_provincia="017", ambito="capoluogo", anno="2011",
                  trimestre="1", segmento="totale")
    assert len(riga) == 1
    assert riga[0]["provincia"] == "Brescia"
    assert riga[0]["regione"] == "Lombardia"


def test_la_sigla_storica_finisce_nella_provincia_di_oggi(tabella) -> None:
    """`FO` non esiste più nell'elenco ISTAT: è Forlì-Cesena, e va tradotta.

    Scartarla perderebbe una provincia intera in silenzio; tradurla dal nome
    sarebbe un crosswalk inventato. La mappa è esplicita e piccola.
    """
    riga = _righe(tabella, codice_provincia="040", anno="2011", trimestre="1")
    assert riga and riga[0]["provincia"] == "Forlì-Cesena"


def test_capoluogo_e_resto_provincia_sono_due_righe(tabella) -> None:
    ambiti = {r["ambito"] for r in _righe(tabella, codice_provincia="017", anno="2011",
                                          trimestre="1", segmento="totale")}
    assert ambiti == {"capoluogo", "resto_provincia"}


def test_la_colonna_periodo_diventa_anno_e_trimestre(tabella) -> None:
    trimestri = {r["trimestre"] for r in _righe(tabella, codice_provincia="017",
                                                anno="2011", ambito="capoluogo",
                                                segmento="totale")}
    assert trimestri == {"1", "2"}


def test_l_ntn_resta_frazionario(tabella) -> None:
    riga = _righe(tabella, codice_provincia="017", ambito="capoluogo", anno="2011",
                  trimestre="1", segmento="totale")
    assert riga[0]["ntn"] == "472.63"


def test_le_pertinenze_sono_segmenti_distinti(tabella) -> None:
    segmenti = {r["segmento"] for r in _righe(tabella, codice_provincia="017",
                                              ambito="capoluogo", anno="2011")}
    assert segmenti == {"totale", "box", "depositi_pertinenziali"}


def test_il_provvisorio_e_dichiarato(tabella) -> None:
    riga = _righe(tabella, anno="2025", trimestre="1", segmento="totale")
    assert len(riga) == 1
    assert riga[0]["stato"] == "provvisorio"
    assert riga[0]["ntn"] == "727.24"
    assert all(r["stato"] == "definitivo" for r in _righe(tabella, anno="2011"))


def test_la_superficie_normalizzata_non_entra(tabella) -> None:
    """`2025_1_PROVV_SUP_NORM` sono metri quadri, non transazioni.

    Il valore finto è `95000,125`: se finisse fra gli NTN si vedrebbe subito,
    ed è il punto — sono due misure nella stessa riga di intestazione.
    """
    assert not [r for r in tabella if r["ntn"].startswith("95000")]
    assert not _righe(tabella, anno="2023")


def test_una_sigla_ignota_ferma_il_build(tmp_path: Path, monkeypatch) -> None:
    """Meglio un errore che una provincia sparita dalla tabella."""
    from brescia_pipeline import tidy as tidy_mod

    archivi = {"definitivo": _zip(tmp_path / "d.zip", DEFINITIVO)}
    monkeypatch.setattr(cp, "province_per_sigla", lambda: {"BS": PROVINCE["BS"]})
    monkeypatch.setattr(cp, "scarica_archivi", lambda: archivi)
    monkeypatch.setattr(tidy_mod, "PROCESSED_DIR", tmp_path / "out")

    with pytest.raises(RuntimeError, match="GE"):
        cp.build({})


# --- i link, che sono l'altra metà del problema ---------------------------

PAGINA = """
<a href="https://x/documents/20143/9812824/NON_RESIDENZIALE_DEFINITIVO_2011_2024.zip/aa?t=1">nr</a>
<a href="https://x/documents/20143/9812824/RESIDENZIALE_DEFINITIVO_2011_2024.zip/bb?t=2">r</a>
<a href="https://x/documents/20143/10125294/RESIDENZIALE_2025_2026_PROVV.zip/cc?t=3">p</a>
<a href="https://x/documents/20143/9812824/Terreni_Superfici_Scambiate_2023_2024.csv/dd?t=4">t</a>
"""


def test_i_link_si_leggono_dalla_pagina() -> None:
    """Gli URL portano un UUID e un `?t=` che cambiano a ogni ripubblicazione.

    Scriverli in una costante vuol dire una pipeline che smette di funzionare
    senza dirlo, il giorno che l'Agenzia ricarica il file. È la stessa ragione
    per cui `bilancio.py` legge gli anni dalla pagina indice.
    """
    link = cp.link_archivi(PAGINA)
    assert set(link) == {"definitivo", "provvisorio"}
    assert "RESIDENZIALE_DEFINITIVO_2011_2024.zip" in link["definitivo"]
    assert "NON_RESIDENZIALE" not in link["definitivo"]
    assert "RESIDENZIALE_2025_2026_PROVV.zip" in link["provvisorio"]


def test_il_nome_del_file_diventa_il_nome_in_cache() -> None:
    """Il nome porta gli anni, quindi una fornitura nuova non riusa la cache."""
    assert cp.nome_in_cache(
        "https://x/documents/20143/9812824/RESIDENZIALE_DEFINITIVO_2011_2024.zip/bb?t=2"
    ) == "omi_ntn_RESIDENZIALE_DEFINITIVO_2011_2024.zip"


def test_una_pagina_senza_link_e_un_errore() -> None:
    with pytest.raises(RuntimeError, match="definitivo"):
        cp.link_archivi("<html><body>manutenzione</body></html>")


def test_solo_le_colonne_ntn_sono_periodi() -> None:
    assert cp.periodo("2011_1") == ("2011", "1")
    assert cp.periodo("2025_3_PROVV_NTN") == ("2025", "3")
    assert cp.periodo("2025_3_PROVV_SUP_NORM") is None
    assert cp.periodo("2023_1_SUP_NORM") is None
    assert cp.periodo("Regione") is None


def test_le_righe_sono_ordinate_e_deterministiche(tabella) -> None:
    chiavi = [
        (r["codice_provincia"], r["ambito"], r["anno"], r["trimestre"], r["segmento"])
        for r in tabella
    ]
    assert chiavi == sorted(chiavi)


def test_il_csv_non_perde_le_province_diverse_da_brescia(tabella) -> None:
    """La tabella è nazionale, come `bilancio_province.csv`: serve il confronto."""
    assert {r["codice_provincia"] for r in tabella} >= {"010", "017", "040"}


def test_l_intestazione_e_quella_dichiarata(tmp_path: Path, monkeypatch) -> None:
    from brescia_pipeline import tidy as tidy_mod

    monkeypatch.setattr(cp, "province_per_sigla", lambda: dict(PROVINCE))
    monkeypatch.setattr(cp, "scarica_archivi", lambda: {"definitivo": _zip(tmp_path / "d.zip", DEFINITIVO)})
    monkeypatch.setattr(tidy_mod, "PROCESSED_DIR", tmp_path / "out")
    cp.build({})
    testa = (tmp_path / "out" / "compravendite_province.csv").read_text(encoding="utf-8")
    assert next(iter(csv.reader(io.StringIO(testa)))) == cp.COLUMNS
