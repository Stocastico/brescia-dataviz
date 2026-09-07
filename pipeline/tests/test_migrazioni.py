"""Le marginali del background migratorio, senza rete.

La congiunta completa (`migrazioni_comuni.csv`) non è versionata, quindi le due
marginali sono le **uniche** su cui una cifra pubblicata può poggiare: se
sbagliano, sbaglia la storia. E una ha sbagliato.

**Il bug che questo file esiste per non far tornare.** Le due righe dei
minorenni venivano **esattamente il doppio** — 50.204 stranieri nati in Italia
sotto i 18 anni invece di 25.102 — perché nelle tavole 4 e 6 la cittadinanza
porta il **totale e i due sottoinsiemi** (UE ed extra-UE) come modalità della
stessa dimensione, e sommarle tutte conta la stessa persona due volte. Nella
tavola 1, da cui vengono tutti gli altri indicatori, quella dimensione è fissa:
i totali di stock tornavano all'unità contro `popolazione_comuni.csv`, e la
tabella sembrava giusta. Il doppio si vedeva solo confrontando i minorenni col
totale di cui sono un sottoinsieme — che è il controllo qui sotto.

Le altre cose che qui sbagliano davvero:

- **il totale di `place_birth_par` si chiama «tutte le voci»**, non «totale».
  Cercare «totale» non dà un errore: dà zero righe, e una tabella vuota;
- gli indicatori si cercano **per stringa esatta**, quindi un cambio di
  etichetta alla fonte deve fermare il build invece di produrre una marginale
  a cui manca una voce;
- la somma provinciale del titolo di studio salta le **celle soppresse** e non
  le tratta come zeri (MET-3).
"""

from __future__ import annotations

import pytest

from brescia_pipeline.datasets import migrazioni

STOCK = "italiani_stranieri_per_nascita_genitori"


def riga(**campi: str) -> dict[str, str]:
    """Una riga della congiunta, con tutte le dimensioni ai loro totali."""
    base = {
        "codice_istat": "017029",
        "comune": "Brescia",
        "anno": "2023",
        "tavola": STOCK,
        "indicatore": "popolazione residente al 31 dicembre",
        "gender": "totale",
        "age_class": "totale",
        "citizenship": "totale",
        "prevous_citizen": "totale",
        "place_birth_par": "tutte le voci",
        "edu_attain": "totale",
        "valore": "100",
    }
    return base | campi


# --- la sintesi per comune -----------------------------------------------


def test_gli_indicatori_prendono_il_nome_corto() -> None:
    fuori = migrazioni.sintesi([
        riga(indicatore="popolazione residente al 31 dicembre", valore="1000"),
        riga(indicatore="popolazione straniera residente al 31 dicembre", valore="120"),
    ])
    assert {r["indicatore"] for r in fuori} == {"popolazione_residente", "stranieri"}


def test_i_minorenni_non_si_contano_due_volte() -> None:
    """Il bug del doppio, fissato.

    Le tre righe sono la stessa popolazione: il totale e i due sottoinsiemi che
    lo partizionano. Solo la prima deve entrare.
    """
    minorenni = "stranieri/apolidi nati in Italia fino a 17 anni al 31 dicembre"
    fuori = migrazioni.sintesi([
        riga(tavola="stranieri_nati_in_italia", indicatore=minorenni,
             age_class="fino a 17 anni", citizenship="straniero-a/apolide", valore="25102"),
        riga(tavola="stranieri_nati_in_italia", indicatore=minorenni,
             age_class="fino a 17 anni", citizenship="di paese dell'Unione europea a 27",
             valore="4000"),
        riga(tavola="stranieri_nati_in_italia", indicatore=minorenni,
             age_class="fino a 17 anni",
             citizenship="di paese extra Unione europea a 27 paesi", valore="21102"),
    ])
    assert len(fuori) == 1
    assert fuori[0]["valore"] == "25102"


def test_lo_stesso_vale_per_gli_italiani_acquisiti() -> None:
    minorenni = "italiani acquisiti nati in Italia fino a 17 anni al 31 dicembre"
    fuori = migrazioni.sintesi([
        riga(tavola="italiani_acquisizione_nati_in_italia", indicatore=minorenni,
             age_class="fino a 17 anni", prevous_citizen="totale", valore="18131"),
        riga(tavola="italiani_acquisizione_nati_in_italia", indicatore=minorenni,
             age_class="fino a 17 anni",
             prevous_citizen="di paese extra Unione europea a 27 paesi", valore="15000"),
    ])
    assert len(fuori) == 1
    assert fuori[0]["valore"] == "18131"


def test_il_totale_di_place_birth_par_si_chiama_tutte_le_voci() -> None:
    """Con «totale» al posto di «tutte le voci» la tabella nasce vuota."""
    with pytest.raises(RuntimeError, match="nessuna riga di sintesi"):
        migrazioni.sintesi([riga(place_birth_par="totale")])


def test_le_righe_per_sesso_non_entrano() -> None:
    fuori = migrazioni.sintesi([
        riga(valore="1000"),
        riga(gender="femmine", valore="510"),
        riga(gender="maschi", valore="490"),
    ])
    assert len(fuori) == 1
    assert fuori[0]["valore"] == "1000"


def test_un_etichetta_cambiata_ferma_il_build() -> None:
    with pytest.raises(RuntimeError, match="stringa esatta"):
        migrazioni.sintesi([riga(indicatore="popolazione residente")])


def test_le_celle_vuote_non_entrano() -> None:
    fuori = migrazioni.sintesi([riga(valore="1000"), riga(codice_istat="017001", valore="")])
    assert len(fuori) == 1


def test_la_sintesi_e_ordinata() -> None:
    fuori = migrazioni.sintesi([
        riga(codice_istat="017029", anno="2023",
             indicatore="popolazione straniera residente al 31 dicembre", valore="1"),
        riga(codice_istat="017001", anno="2021", valore="2"),
        riga(codice_istat="017029", anno="2021", valore="3"),
    ])
    chiavi = [(r["codice_istat"], r["anno"], r["indicatore"]) for r in fuori]
    assert chiavi == sorted(chiavi)


# --- il titolo di studio -------------------------------------------------


def test_l_istruzione_si_somma_sui_comuni() -> None:
    laurea = "titolo universitario o accademico"
    fuori = migrazioni.istruzione([
        riga(tavola="italiani_istruzione", citizenship="italiano-a",
             age_class="25-49 anni", edu_attain=laurea, valore="100"),
        riga(tavola="italiani_istruzione", citizenship="italiano-a", codice_istat="017001",
             age_class="25-49 anni", edu_attain=laurea, valore="50"),
    ])
    assert len(fuori) == 1
    assert fuori[0] == {
        "anno": "2023", "gruppo": "italiani dalla nascita",
        "classe_eta": "25-49 anni", "titolo": laurea, "valore": "150",
    }


def test_i_sottoinsiemi_ue_ed_extra_ue_non_si_sommano_al_totale() -> None:
    """Anche qui la stessa popolazione è pubblicata tre volte."""
    laurea = "titolo universitario o accademico"
    fuori = migrazioni.istruzione([
        riga(tavola="stranieri_istruzione", citizenship="straniero-a/apolide",
             age_class="25-49 anni", edu_attain=laurea, valore="11048"),
        riga(tavola="stranieri_istruzione", citizenship="di paese dell'Unione europea a 27",
             age_class="25-49 anni", edu_attain=laurea, valore="2373"),
        riga(tavola="stranieri_istruzione",
             citizenship="di paese extra Unione europea a 27 paesi",
             age_class="25-49 anni", edu_attain=laurea, valore="8675"),
    ])
    assert len(fuori) == 1
    assert fuori[0]["valore"] == "11048"


def test_i_conteggi_restano_interi() -> None:
    """La somma in virgola mobile no: `150.00000000000003` non è un conteggio."""
    fuori = migrazioni.istruzione([
        riga(tavola="italiani_istruzione", citizenship="italiano-a", valore="0.1"),
        riga(tavola="italiani_istruzione", citizenship="italiano-a",
             codice_istat="017001", valore="0.2"),
    ])
    assert fuori[0]["valore"] == "0"


def test_le_tre_tavole_cambiate_fermano_il_build() -> None:
    with pytest.raises(RuntimeError, match="le tre tavole sono cambiate"):
        migrazioni.istruzione([riga(tavola="italiani_istruzione", citizenship="italiano-a",
                                    place_birth_par="totale")])
