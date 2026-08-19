"""Addetti e unità locali per **sezione Ateco e comune**, 2018–2023.

È la tabella che mancava, e senza la quale l'asse 3 del brief — «le due
economie», manifattura e Garda — non era disegnabile sui 205 comuni:
`imprese_settore.csv` porta il dettaglio settoriale solo per il capoluogo e per
la provincia, perché il prodotto cartesiano completo (comuni × 88 divisioni)
è ingestibile.

**Come si aggira.** Il vincolo noto è sulla dimensione territoriale: una chiave
con 205 codici in `REF_AREA` riceve `400` comunque la si scriva
(`FONTI.md` §10). Ma con `REF_AREA` **libero** e la sezione Ateco **fissa**, la
richiesta passa: una risposta per sezione, tutta Italia, una dozzina di MB e
una ventina di secondi. Diciassette sezioni per due indicatori sono trentaquattro
richieste — un quarto d'ora, contro le ore delle tavole censuarie — e il filtro
sui comuni della provincia si fa qui.

La sezione è la grana giusta per questa domanda: distingue manifattura,
costruzioni, alloggio e ristorazione, commercio, e basta a definire un profilo
comunale. Il dettaglio di divisione (25 «prodotti in metallo», che è la Val
Trompia) resta disponibile a richiesta con la stessa ricetta, un codice al posto
della lettera.

⚠️ ASIA non copre l'agricoltura (sezione `A`), la pubblica amministrazione
(`O`), i servizi domestici (`T`) e gli organismi extraterritoriali (`U`): sono
assenti dalla fonte, non dal filtro. In un territorio con la Bassa agricola
questo va detto ogni volta che si somma per settore: **il totale delle sezioni
non è l'economia del comune**, è la parte che ASIA osserva.
"""

from __future__ import annotations

from .. import sdmx
from ..fetch import sdmx_csv
from ..tidy import fmt, read_sdmx, split_code, to_number, write_csv

DATAFLOW = "183_1163_DF_DICA_ASIAULP_TERRIFDATA_7"  # comuni

INDICATORI = {"LU": "unita_locali", "LUEMPDAA": "addetti"}
CLASSE_TOTALE = "TOTAL"

# Le sezioni presenti nel registro ASIA, verificate una per una sul capoluogo.
# A, O, T, U non ci sono: vedi l'avvertenza in testa al modulo.
SEZIONI = list("BCDEFGHIJKLMNPQRS")

COLUMNS = ["codice_istat", "comune", "anno", "sezione", "nome_sezione", "indicatore", "valore"]


def _decimali(indicator: str) -> int:
    return 1 if indicator == "LUEMPDAA" else 0


def build(comuni: dict[str, str]) -> None:
    rows: list[dict[str, str]] = []

    for indicator, nome_indicatore in INDICATORI.items():
        for sezione in SEZIONI:
            path = sdmx_csv(
                DATAFLOW,
                sdmx.key(
                    DATAFLOW,
                    {
                        "FREQ": "A",
                        "DATA_TYPE": indicator,
                        "ECON_ACTIVITY_NACE_2007": sezione,
                        "PERS_EMPL_SIZE_CLASS": CLASSE_TOTALE,
                    },
                ),
                dest_name=f"istat_asia_sezione_{sezione}_{indicator.lower()}.csv",
            )
            for record in read_sdmx(path):
                code, _ = split_code(record.get("REF_AREA", ""))
                if code not in comuni:
                    continue
                nace_code, nace_label = split_code(record.get("ECON_ACTIVITY_NACE_2007", ""))
                value = to_number(record.get("OBS_VALUE"))
                if value is None:
                    continue
                rows.append(
                    {
                        "codice_istat": code,
                        "comune": comuni[code],
                        "anno": record.get("TIME_PERIOD", ""),
                        "sezione": nace_code,
                        "nome_sezione": nace_label,
                        "indicatore": nome_indicatore,
                        "valore": fmt(value, _decimali(indicator)),
                    }
                )

    rows.sort(key=lambda r: (r["codice_istat"], r["indicatore"], r["anno"], r["sezione"]))
    write_csv("imprese_sezioni_comuni.csv", rows, COLUMNS)
