"""Test del bilancio demografico comunale, senza rete.

Il CSV di prova riproduce la forma reale di `demo.istat.it`: separatore `;`,
tre righe per sesso di cui una è il **totale** (sommarle tutte e tre raddoppia
la popolazione), righe di aggregato provinciale e nazionale con il codice
comune vuoto, e due «mesi» che mesi non sono — il 13 è l'aggiustamento
statistico, il 15 la popolazione censita.

Sono esattamente le quattro trappole di questa fonte, e ognuna produce un
errore silenzioso e plausibile se non la si conosce.
"""

from __future__ import annotations

import csv
import io

import pytest

from brescia_pipeline.datasets import bilancio

COLONNE = [
    "Anno", "Mese", "Nome mese", "Sesso", "Popolazione inizio periodo",
    "Nati vivi", "Morti", "Saldo naturale", "Immigrati da altro comune",
    "Emigrati per altro comune", "Saldo migratorio interno",
    "Immigrati dall'estero", "Emigrati per l'estero",
    "Saldo migratorio con l'estero",
    "Unità in più/meno dovute a variazioni territoriali",
    "Popolazione fine periodo", "Codice comune", "Comune", "Codice provincia",
    "Provincia", "Codice regione", "Regione", "Codice ripartizione",
    "Ripartizione", "Codice nazione", "Nazione",
]


def riga(**campi: object) -> dict[str, str]:
    base = dict.fromkeys(COLONNE, "")
    base.update(
        {
            "Anno": "2024",
            "Sesso": "Totale",
            "Codice provincia": "017",
            "Provincia": "Brescia",
            "Codice regione": "03",
            "Regione": "Lombardia",
        }
    )
    base.update({k: str(v) for k, v in campi.items()})
    return base


def mese(numero: int, nome: str, **campi: object) -> dict[str, str]:
    return riga(Mese=numero, **{"Nome mese": nome}, **campi)


def comune(codice: str, nome: str, mesi: list[dict[str, str]]) -> list[dict[str, str]]:
    return [dict(m, **{"Codice comune": codice, "Comune": nome}) for m in mesi]


# Un comune completo: due mesi di flussi, l'aggiustamento e la popolazione
# censita. 1000 + (5-3) + (10-6) + (4-1) + 0 = 1009, più 1 di aggiustamento.
ACQUAFREDDA = comune(
    "017001",
    "Acquafredda",
    [
        mese(
            1, "Gennaio",
            **{
                "Popolazione inizio periodo": 1000, "Nati vivi": 3, "Morti": 1,
                "Immigrati da altro comune": 6, "Emigrati per altro comune": 4,
                "Immigrati dall'estero": 2, "Emigrati per l'estero": 1,
                "Unità in più/meno dovute a variazioni territoriali": 0,
                "Popolazione fine periodo": 1005,
            },
        ),
        mese(
            12, "Dicembre",
            **{
                "Popolazione inizio periodo": 1005, "Nati vivi": 2, "Morti": 2,
                "Immigrati da altro comune": 4, "Emigrati per altro comune": 2,
                "Immigrati dall'estero": 2, "Emigrati per l'estero": 0,
                "Unità in più/meno dovute a variazioni territoriali": 0,
                "Popolazione fine periodo": 1009,
            },
        ),
        mese(13, "Aggiustamento statistico", **{"Popolazione fine periodo": 1}),
        mese(15, "Popolazione censita al 31 dicembre", **{"Popolazione fine periodo": 1010}),
    ],
)

# Le righe per sesso: se entrano nell'aggregazione i conteggi raddoppiano.
PER_SESSO = [
    dict(r, Sesso=sesso) for r in ACQUAFREDDA for sesso in ("Maschi", "Femmine")
]

# Aggregato provinciale della fonte: codice comune vuoto. È il controllo, non
# un comune.
AGGREGATO_PROVINCIA = [
    dict(m, **{"Codice comune": "", "Comune": ""})
    for m in [
        mese(15, "Popolazione censita al 31 dicembre", **{"Popolazione fine periodo": 1010}),
    ]
]

# Aggregato nazionale: anche il codice provincia è vuoto.
AGGREGATO_ITALIA = [
    dict(m, **{"Codice comune": "", "Comune": "", "Codice provincia": "", "Provincia": ""})
    for m in [
        mese(15, "Popolazione censita al 31 dicembre", **{"Popolazione fine periodo": 99999}),
    ]
]

# Un comune di un'altra provincia: serve alla tabella provinciale, non a quella
# comunale.
MILANO = comune(
    "015146",
    "Milano",
    [
        mese(
            1, "Gennaio",
            **{
                "Popolazione inizio periodo": 500, "Nati vivi": 1, "Morti": 1,
                "Immigrati da altro comune": 0, "Emigrati per altro comune": 0,
                "Immigrati dall'estero": 0, "Emigrati per l'estero": 0,
                "Unità in più/meno dovute a variazioni territoriali": 0,
                "Popolazione fine periodo": 500,
            },
        ),
        mese(15, "Popolazione censita al 31 dicembre", **{"Popolazione fine periodo": 500}),
    ],
)
MILANO = [dict(r, **{"Codice provincia": "015", "Provincia": "Milano"}) for r in MILANO]

RIGHE = ACQUAFREDDA + PER_SESSO + AGGREGATO_PROVINCIA + AGGREGATO_ITALIA + MILANO


@pytest.fixture
def csv_annuale(tmp_path):
    path = tmp_path / "Bilancio_demografico_mensile_2024.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLONNE, delimiter=";")
        writer.writeheader()
        writer.writerows(RIGHE)
    return path


@pytest.fixture
def totali():
    return bilancio.aggrega(RIGHE)


# --- gli anni disponibili ------------------------------------------------


PAGINA = """
<ul>
  <li><a href="../data/d7b/D7B2018.csv.zip">2018</a></li>
  <li><a href="../data/d7b/D7B2019.csv.zip">2019</a></li>
  <li><a href="../data/d7b/D7B2024.csv.zip">2024</a></li>
  <li><a href="../data/altro/ALTRO2025.csv.zip">non è il D7B</a></li>
</ul>
"""


def test_gli_anni_si_leggono_dalla_pagina_indice() -> None:
    # 2018 sta sotto il primo anno della serie: non entra.
    assert bilancio.anni_disponibili(PAGINA) == [2019, 2024]


def test_una_pagina_senza_anni_e_un_errore_non_una_lista_vuota() -> None:
    with pytest.raises(RuntimeError):
        bilancio.anni_disponibili("<html>manutenzione</html>")


# --- l'aggregazione ------------------------------------------------------


def test_somma_solo_le_righe_del_totale_per_sesso(totali) -> None:
    """Maschi + Femmine + Totale è il doppio della popolazione vera."""
    assert totali[("017001", "2024")]["nati"] == 5
    assert totali[("017001", "2024")]["popolazione_inizio"] == 1000


def test_gli_aggregati_territoriali_non_sono_comuni(totali) -> None:
    assert all(len(codice) == 6 for codice, _ in totali)


def test_il_mese_13_e_laggiustamento_statistico(totali) -> None:
    assert totali[("017001", "2024")]["aggiustamento_statistico"] == 1


def test_il_mese_15_e_la_popolazione_censita(totali) -> None:
    """Ed è il ponte con `popolazione_comuni.csv`, che è la stessa cosa."""
    assert totali[("017001", "2024")]["popolazione_censita"] == 1010
    assert totali[("017001", "2024")]["popolazione_fine"] == 1009


def test_i_mesi_speciali_non_entrano_nei_flussi(totali) -> None:
    """Il 13 e il 15 hanno le colonne dei flussi vuote: non devono sommarsi."""
    assert totali[("017001", "2024")]["morti"] == 3
    assert totali[("017001", "2024")]["immigrati_interni"] == 10


def test_tiene_le_altre_province(totali) -> None:
    assert ("015146", "2024") in totali


# --- l'identità contabile ------------------------------------------------


def test_lidentita_chiude(totali) -> None:
    bilancio.verifica_identita(totali)


def test_unidentita_rotta_e_un_errore_rumoroso(totali) -> None:
    rotti = {k: dict(v) for k, v in totali.items()}
    rotti[("017001", "2024")]["nati"] += 7
    with pytest.raises(RuntimeError, match="017001"):
        bilancio.verifica_identita(rotti)


# --- le province ---------------------------------------------------------


def test_le_province_sono_la_somma_dei_loro_comuni(totali) -> None:
    per_provincia = bilancio.per_provincia(totali)
    assert per_provincia[("017", "2024")]["popolazione_censita"] == 1010
    assert per_provincia[("015", "2024")]["popolazione_censita"] == 500


def test_il_controllo_provinciale_della_fonte_viene_confrontato(totali) -> None:
    """La fonte pubblica i suoi totali provinciali: se non tornano, si sa."""
    controllo = bilancio.controllo_province(RIGHE)
    assert controllo[("017", "2024")]["popolazione_censita"] == 1010
    bilancio.verifica_province(bilancio.per_provincia(totali), controllo)


def test_un_totale_provinciale_che_non_torna_e_un_errore(totali) -> None:
    controllo = bilancio.controllo_province(RIGHE)
    controllo[("017", "2024")]["popolazione_censita"] = 1234
    with pytest.raises(RuntimeError, match="017"):
        bilancio.verifica_province(bilancio.per_provincia(totali), controllo)


# --- la lettura del file -------------------------------------------------


def test_legge_il_csv_con_il_punto_e_virgola(csv_annuale) -> None:
    righe = list(bilancio.leggi_csv(csv_annuale.read_bytes()))
    assert len(righe) == len(RIGHE)
    assert righe[0]["Comune"] == "Acquafredda"


def test_i_nomi_dei_territori_vengono_dalla_fonte() -> None:
    nomi = bilancio.nomi_province(RIGHE)
    assert nomi["017"] == ("Brescia", "Lombardia")
    assert "" not in nomi
