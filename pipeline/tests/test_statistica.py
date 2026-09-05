"""La statistica condivisa dagli script di analisi (`analysis/_tabelle.py`).

È il posto dove un errore non si vede: un tasso annualizzato calcolato come
variazione diviso gli anni dà un numero plausibile e sbagliato, e nessun
controllo a valle se ne accorge perché tutto il resto della catena funziona.

I casi qui sono scelti perché hanno una risposta **nota a mano**, non perché
coprono righe: una correlazione su punti perfettamente allineati fa 1, i ranghi
di tre pari merito fanno tutti e tre la media delle loro posizioni, un raddoppio
in dieci anni fa il 7,177 % l'anno. Se un giorno una di queste cambia, è il
codice ad aver smesso di fare quello che dice.
"""

from __future__ import annotations

import math

import pytest

from conftest import servono_tabelle

import _tabelle as T


# --- il tasso composto ---------------------------------------------------


def test_il_tasso_e_composto_non_diviso_per_gli_anni() -> None:
    """Un raddoppio in dieci anni fa 7,177 % l'anno, non il 10 %."""
    assert T.tasso_annualizzato(100, 200, 10) == pytest.approx(7.1773, abs=1e-4)
    # e ricomponendo si torna al punto di partenza
    tasso = T.tasso_annualizzato(100, 200, 10)
    assert 100 * (1 + tasso / 100) ** 10 == pytest.approx(200)


def test_il_tasso_e_zero_quando_non_succede_niente() -> None:
    assert T.tasso_annualizzato(1234, 1234, 7) == pytest.approx(0.0)


@pytest.mark.parametrize(
    "iniziale,finale,anni",
    [
        (0, 100, 5),      # da zero non si annualizza: sarebbe una crescita infinita
        (100, 0, 5),      # e nemmeno verso zero
        (-10, 100, 5),    # né da un valore negativo
        (100, 200, 0),    # né su zero anni
        (100, 200, -3),
    ],
)
def test_il_tasso_indefinito_e_none_non_uno_zero(iniziale, finale, anni) -> None:
    """`None` e non `0.0`: uno zero si somma e si media, un `None` no."""
    assert T.tasso_annualizzato(iniziale, finale, anni) is None


# --- le due correlazioni -------------------------------------------------


def test_pearson_su_punti_allineati_fa_uno() -> None:
    x = [1.0, 2.0, 3.0, 4.0, 5.0]
    assert T.pearson(x, [2 * v + 7 for v in x]) == pytest.approx(1.0)
    assert T.pearson(x, [-3 * v + 1 for v in x]) == pytest.approx(-1.0)


def test_pearson_su_una_serie_costante_e_none() -> None:
    """Una serie senza varianza non ha correlazione: `None`, non zero."""
    assert T.pearson([1.0, 1.0, 1.0, 1.0], [1.0, 2.0, 3.0, 4.0]) is None


def test_pearson_rifiuta_serie_di_lunghezza_diversa_o_troppo_corte() -> None:
    assert T.pearson([1.0, 2.0], [1.0, 2.0]) is None          # meno di tre punti
    assert T.pearson([1.0, 2.0, 3.0], [1.0, 2.0]) is None      # lunghezze diverse


def test_spearman_vede_la_monotonia_dove_pearson_non_la_vede() -> None:
    """La ragione per cui MET-6 impone di riportarle in coppia.

    Su una relazione monotona ma molto curva, il rango è perfetto e la retta no.
    """
    x = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    y = [v**4 for v in x]
    assert T.spearman(x, y) == pytest.approx(1.0)
    assert T.pearson(x, y) < 0.95


def test_i_ranghi_mediano_i_pari_merito() -> None:
    """Tre valori uguali in prima, seconda e terza posizione prendono tutti 2."""
    assert T.ranghi([5.0, 5.0, 5.0, 9.0]) == [2.0, 2.0, 2.0, 4.0]
    assert T.ranghi([3.0, 1.0, 2.0]) == [3.0, 1.0, 2.0]
    # i pari merito in fondo
    assert T.ranghi([1.0, 7.0, 7.0]) == [1.0, 2.5, 2.5]


def test_la_media_e_quella_che_sembra() -> None:
    assert T.media([1.0, 2.0, 3.0]) == pytest.approx(2.0)


# --- il leave-one-out di MET-5 -------------------------------------------


def test_senza_toglie_le_posizioni_giuste() -> None:
    codici = ["017029", "017184", "017001"]
    assert T.senza(codici, {"017184"}) == [0, 2]
    assert T.senza(codici, set()) == [0, 1, 2]
    assert T.senza(codici, set(codici)) == []


# --- il deflatore (MET-20) -----------------------------------------------


@servono_tabelle
def test_il_deflatore_dellanno_base_vale_uno() -> None:
    """Nell'anno base non c'è niente da scontare, e il fattore deve dirlo."""
    fattori = T.deflatore()
    assert fattori[T.ANNO_EURO_COSTANTI] == pytest.approx(1.0)


@servono_tabelle
def test_il_deflatore_del_passato_e_maggiore_di_uno() -> None:
    """Con inflazione positiva, un euro di ieri vale più di un euro di oggi."""
    fattori = T.deflatore()
    anni = sorted(fattori)
    assert fattori[anni[0]] > fattori[anni[-1]]
    assert fattori[anni[0]] > 1.0


@servono_tabelle
def test_il_deflatore_su_un_anno_base_inesistente_esplode() -> None:
    with pytest.raises(ValueError, match="non è nella serie dei prezzi"):
        T.deflatore(base="1720")


@servono_tabelle
def test_gli_anni_fuori_serie_spariscono_invece_di_passare_indeformati() -> None:
    """Un valore non deflazionato in mezzo a valori deflazionati non si vede."""
    serie = {"2020": 100.0, "1066": 100.0}
    fuori = T.in_euro_costanti(serie)
    assert "1066" not in fuori
    assert fuori["2020"] > 100.0


# --- la scomposizione demografica ----------------------------------------


def test_scomponi_somma_le_componenti_e_ricostruisce_il_totale() -> None:
    per_anno = {
        "2019": {"nati": 10, "morti": 4, "immigrati_interni": 7, "emigrati_interni": 5,
                 "immigrati_estero": 3, "emigrati_estero": 1, "aggiustamento_statistico": 2},
        "2020": {"nati": 8, "morti": 9, "immigrati_interni": 6, "emigrati_interni": 6,
                 "immigrati_estero": 4, "emigrati_estero": 2, "variazioni_territoriali": -1},
    }
    somma = T.scomponi(per_anno)
    assert somma["saldo_naturale"] == (10 - 4) + (8 - 9)
    assert somma["saldo_migratorio_interno"] == (7 - 5) + (6 - 6)
    assert somma["saldo_migratorio_estero"] == (3 - 1) + (4 - 2)
    assert somma["aggiustamento_statistico"] == 2
    assert somma["variazioni_territoriali"] == -1
    # il totale è la somma di tutto il resto, e non si conta due volte
    assert somma["totale"] == sum(v for k, v in somma.items() if k != "totale")


def test_scomponi_su_un_sottoperiodo_guarda_solo_quegli_anni() -> None:
    per_anno = {
        "2019": {"nati": 10, "morti": 0},
        "2020": {"nati": 100, "morti": 0},
    }
    assert T.scomponi(per_anno, anni=["2019"])["saldo_naturale"] == 10


def test_una_voce_assente_non_diventa_un_errore_ma_nemmeno_un_numero() -> None:
    """Le celle che la fonte non pubblica non fanno esplodere la somma."""
    somma = T.scomponi({"2019": {"nati": 5}})
    assert somma["saldo_naturale"] == 5
    assert somma["saldo_migratorio_estero"] == 0


def test_le_voci_non_demografiche_restano_separate() -> None:
    """Attribuire una rettifica anagrafica all'emigrazione è dare un titolo."""
    assert set(T.NON_DEMOGRAFICHE).isdisjoint(T.COMPONENTI)


# --- le celle vuote (MET-3) ----------------------------------------------


def test_una_cella_vuota_e_un_dato_mancante_non_uno_zero() -> None:
    assert T.numero("") is None
    assert T.numero(None) is None
    assert T.numero("0") == 0.0
    assert T.numero("3,5" .replace(",", ".")) == 3.5


# --- le tabelle vere -----------------------------------------------------


@servono_tabelle
def test_i_comuni_gardesani_si_risolvono_tutti_dallanagrafica() -> None:
    """La lista è per nome apposta: un nome sbagliato deve fallire, non escludere
    in silenzio il comune sbagliato."""
    codici = T.codici_gardesani()
    assert len(codici) == len(T.GARDESANI)
    assert all(c in T.anagrafica() for c in codici)


@servono_tabelle
def test_i_comuni_col_lago_nel_nome_non_sono_il_criterio() -> None:
    """Polpenazze del Garda porta il lago nel nome e non lo tocca; Salò no e sì."""
    per_nome = {r["comune"]: c for c, r in T.anagrafica().items()}
    gardesani = T.codici_gardesani()
    assert per_nome["Salò"] in gardesani
    assert per_nome["Polpenazze del Garda"] not in gardesani


@servono_tabelle
def test_la_lista_gardesana_sbagliata_fallisce_invece_di_tacere(monkeypatch) -> None:
    monkeypatch.setattr(T, "GARDESANI", ("Comune Che Non Esiste",))
    with pytest.raises(ValueError, match="non trovati in anagrafica"):
        T.codici_gardesani()


@servono_tabelle
@pytest.mark.parametrize("chiave", sorted(T.SERIE_DISPONIBILI))
def test_ogni_serie_disponibile_si_legge_e_ha_dei_comuni(chiave: str) -> None:
    etichetta, unita, costruisci = T.SERIE_DISPONIBILI[chiave]
    serie = costruisci()
    assert etichetta and unita
    assert len(serie) > 100, f"{chiave}: solo {len(serie)} comuni"
    for anni in serie.values():
        assert anni
        assert all(isinstance(v, float) and math.isfinite(v) for v in anni.values())


@servono_tabelle
def test_il_reddito_e_un_rapporto_fra_totali_non_una_media_di_medie() -> None:
    """Somma degli imponibili diviso somma dei contribuenti: i valori devono
    stare in un intervallo plausibile per un reddito medio dichiarato."""
    serie = T.serie_reddito()
    valori = [v for anni in serie.values() for v in anni.values()]
    assert 5_000 < min(valori) < 60_000
    assert 10_000 < max(valori) < 200_000


@servono_tabelle
def test_le_quote_di_sezione_stanno_attorno_a_cento() -> None:
    """Il denominatore è il totale ASIA riportato, non la somma delle sezioni.

    I due non coincidono esattamente, e la soglia larga qui è la misura di
    quanto: la fonte arrotonda le celle per sezione e sopprime le più piccole,
    quindi la somma delle quote sfiora il 101 % in un comune e scende sotto il
    99 % in un altro. La mediana è 100 esatto. Il test tiene la banda entro un
    punto e mezzo: se un giorno si allarga, è cambiato il denominatore.
    """
    anno, per_comune = T.quote_sezioni()
    assert anno.isdigit()
    assert len(per_comune) > 100
    for codice, sezioni in per_comune.items():
        totale = sum(sezioni.values())
        assert 98.5 <= totale <= 101.5, f"{codice}: {totale}"


@servono_tabelle
def test_una_sezione_assente_resta_assente_e_uno_zero_pubblicato_resta_zero() -> None:
    """MET-3, e qui si vede che la distinzione è viva nel dato.

    ASIA sopprime le celle troppo piccole: quelle sezioni **non compaiono**.
    Ma pubblica anche degli zeri veri (la sezione D, energia e gas, in
    ventisette comuni), e quello zero è un'informazione. Se il modulo
    riempisse i buchi con zeri, i due casi diventerebbero indistinguibili e
    questo test non troverebbe più nessun comune con sezioni mancanti.
    """
    _, per_comune = T.quote_sezioni()
    tutte = {s for sezioni in per_comune.values() for s in sezioni}
    incomplete = [c for c, s in per_comune.items() if set(s) != tutte]
    assert incomplete, "nessun comune con sezioni mancanti: i buchi sono stati riempiti"
    zeri = [(c, s) for c, ss in per_comune.items() for s, v in ss.items() if v == 0]
    assert zeri, "nessuno zero pubblicato: gli zeri veri sono stati scambiati per buchi"


@servono_tabelle
def test_il_bilancio_si_legge_per_comune_e_per_provincia() -> None:
    comuni = T.bilancio()
    assert len(comuni) > 100
    province = T.bilancio("bilancio_province.csv", chiave="codice_provincia")
    assert len(province) > 100
    somma = T.scomponi(next(iter(comuni.values())))
    assert set(somma) == set(T.COMPONENTI) | set(T.NON_DEMOGRAFICHE) | {"totale"}


@servono_tabelle
def test_le_letture_di_base_tornano_i_205_comuni() -> None:
    assert len(T.anagrafica()) == 205
    assert len(T.geometria()) == 205
    assert len(T.sintesi()) == 205
    assert T.nome(T.CAPOLUOGO) == "Brescia"


@servono_tabelle
def test_scrivi_csv_scrive_quello_che_gli_si_da(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(T, "OUTPUT", tmp_path / "uscita")
    destinazione = T.scrivi_csv("prova.csv", ["a", "b"], [{"a": "1", "b": "2"}])
    assert destinazione.read_text(encoding="utf-8") == "a,b\n1,2\n"
