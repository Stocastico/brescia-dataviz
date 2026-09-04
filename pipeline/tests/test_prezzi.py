"""Test dell'indice dei prezzi al consumo, senza rete.

La cosa che qui sbaglia davvero è **la concatenazione**. ISTAT pubblica le medie
annue del NIC in tre basi diverse — 1995=100 fino al 2010, 2010=100 dal 2011 al
2015, 2015=100 dal 2016 — e le tre non si sovrappongono in nessun anno: prese
insieme e tirate su un grafico solo danno due crolli che non sono mai successi.
L'unico ponte fra una base e la successiva è la **variazione annua**, che ISTAT
calcola sul suo raccordo interno.

Quindi si prova che:

- attaccate con la variazione, le tre basi tornano una serie sola;
- la base finale è dichiarata e vale 100 nel suo anno;
- se manca la variazione dell'anno di giunzione, il modulo **si ferma** invece
  di attaccare due basi a caso;
- se fra due basi c'è un buco d'anni, lo stesso.
"""

from __future__ import annotations

import pytest

from brescia_pipeline.datasets import prezzi

# Tre basi finte con la forma esatta della fonte: la seconda riparte da ~100
# nell'anno in cui la prima finisce a ~140.
INDICI = {
    "2": {"2008": 130.0, "2009": 131.0, "2010": 140.0},
    "10": {"2011": 102.0, "2012": 105.0},
    "40": {"2013": 100.0, "2014": 102.0},
}
VARIAZIONI = {"2009": 0.8, "2010": 6.9, "2011": 2.0, "2012": 2.9, "2013": 1.0, "2014": 2.0}


def test_le_tre_basi_diventano_una_serie_sola():
    serie = prezzi.concatena(INDICI, VARIAZIONI, base="2013")

    # La giunzione 2010→2011 vale la variazione dichiarata, non il salto
    # 140 → 102 che le due basi mostrano da sole.
    assert serie["2011"] / serie["2010"] == pytest.approx(1.02, rel=1e-9)
    assert serie["2013"] / serie["2012"] == pytest.approx(1.01, rel=1e-9)
    # e dentro una base i livelli pubblicati restano quelli, rapporto compreso
    assert serie["2012"] / serie["2011"] == pytest.approx(105.0 / 102.0, rel=1e-9)
    assert serie["2009"] / serie["2008"] == pytest.approx(131.0 / 130.0, rel=1e-9)


def test_la_base_dichiarata_vale_cento():
    serie = prezzi.concatena(INDICI, VARIAZIONI, base="2013")
    assert serie["2013"] == pytest.approx(100.0, rel=1e-9)
    serie_2011 = prezzi.concatena(INDICI, VARIAZIONI, base="2011")
    assert serie_2011["2011"] == pytest.approx(100.0, rel=1e-9)
    # cambiare base non cambia i rapporti: è la stessa serie, letta da un altro zero
    assert serie["2014"] / serie["2008"] == pytest.approx(
        serie_2011["2014"] / serie_2011["2008"], rel=1e-9
    )


def test_senza_la_variazione_di_giunzione_si_ferma():
    monche = {anno: v for anno, v in VARIAZIONI.items() if anno != "2011"}
    with pytest.raises(ValueError, match="2011"):
        prezzi.concatena(INDICI, monche, base="2013")


def test_un_buco_fra_due_basi_si_ferma():
    bucate = {**INDICI, "10": {"2012": 105.0}}  # il 2011 non c'è più: 2010 → 2012
    with pytest.raises(ValueError, match="2011"):
        prezzi.concatena(bucate, VARIAZIONI, base="2013")


def test_una_base_che_non_esiste_si_ferma():
    with pytest.raises(ValueError, match="1999"):
        prezzi.concatena(INDICI, VARIAZIONI, base="1999")


def test_le_righe_portano_la_base_della_fonte_e_lo_stato():
    righe = prezzi.righe(INDICI, VARIAZIONI, basi={"2": "1995", "10": "2010", "40": "2013"},
                         base="2013")
    per_anno = {riga["anno"]: riga for riga in righe}
    assert per_anno["2008"]["base_fonte"] == "1995"
    assert per_anno["2008"]["stato"] == "concatenato"
    # gli anni già pubblicati nella base finale non sono stati riscalati
    assert per_anno["2014"]["base_fonte"] == "2013"
    assert per_anno["2014"]["stato"] == "osservato"
    assert per_anno["2014"]["variazione_annua"] == "2.0"
    assert float(per_anno["2013"]["indice"]) == pytest.approx(100.0)


def test_le_righe_conservano_il_livello_pubblicato_dalla_fonte():
    """La riga porta anche `indice_fonte`, cioè il numero **come la fonte lo
    pubblica**, nella sua base. Senza, la concatenazione è un'affermazione che
    si può solo credere: con, chiunque apra il CSV la può rifare."""
    righe = prezzi.righe(INDICI, VARIAZIONI, basi={"2": "1995", "10": "2010", "40": "2013"},
                         base="2013")
    per_anno = {riga["anno"]: riga for riga in righe}
    assert per_anno["2010"]["indice_fonte"] == "140.0"
    assert per_anno["2011"]["indice_fonte"] == "102.0"
    # e nella base finale i due coincidono, perché non c'è niente da riscalare
    # (come stringhe no: `indice_fonte` porta il decimale che la fonte pubblica,
    # `indice` i tre che servono a ritrovare una variazione dello 0,1 %)
    assert float(per_anno["2014"]["indice_fonte"]) == pytest.approx(
        float(per_anno["2014"]["indice"]), rel=1e-9
    )
    assert prezzi.COLUMNS == ["anno", "indice", "indice_fonte", "variazione_annua",
                              "base_fonte", "stato"]


# I valori SDMX arrivano come `codice: etichetta` (`labels=both`), e leggerli
# alla lettera fa cadere ogni riga senza un errore: la tabella esce vuota e il
# build dice «ok». È lo stesso modo di sbagliare della chiave posizionale.
RECORD = [
    {"DATA_TYPE": "2: indice base 1995", "MEASURE": "4: indice", "TIME_PERIOD": "2010",
     "OBS_VALUE": "139.8"},
    {"DATA_TYPE": "10: indice base 2010", "MEASURE": "4: indice", "TIME_PERIOD": "2011",
     "OBS_VALUE": "102.8"},
    {"DATA_TYPE": "10: indice base 2010", "MEASURE": "8: variazione", "TIME_PERIOD": "2011",
     "OBS_VALUE": "2.8"},
    {"DATA_TYPE": "2: indice base 1995", "MEASURE": "8: variazione", "TIME_PERIOD": "2010",
     "OBS_VALUE": "1.5"},
    {"DATA_TYPE": "2: indice base 1995", "MEASURE": "4: indice", "TIME_PERIOD": "",
     "OBS_VALUE": "1"},
]


def test_le_etichette_non_impediscono_di_leggere_i_codici():
    indici, variazioni = prezzi.leggi(RECORD)
    assert indici == {"2": {"2010": 139.8}, "10": {"2011": 102.8}}
    assert variazioni == {"2010": 1.5, "2011": 2.8}


def test_una_base_sconosciuta_ferma_il_build():
    ignota = [{"DATA_TYPE": "99: base nuova", "MEASURE": "4: indice",
               "TIME_PERIOD": "2031", "OBS_VALUE": "101"}]
    with pytest.raises(ValueError, match="99"):
        prezzi.leggi(ignota)
