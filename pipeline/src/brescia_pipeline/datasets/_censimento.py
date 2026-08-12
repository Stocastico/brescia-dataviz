"""Parte comune alle tavole del Censimento permanente a grana comunale.

Le famiglie `DF_DCSS_*` condividono forma e trappole: chiave posizionale da
comporre leggendo la struttura, filtro territoriale impossibile lato server, e
dimensioni che cambiano da famiglia a famiglia ma **non** dentro la stessa
famiglia. Da qui una sola funzione parametrica invece di tre moduli quasi
identici.

Nota sulla forma tidy: qui ogni osservazione resta **una riga con tutte le sue
dimensioni in colonna**, non una riga per dimensione valorizzata come in
`lavoro.py`. Quella forma lì è imposta da tavole che cambiano dimensioni una
per una; qui le dimensioni sono fisse dentro la famiglia, e appiattirle
distruggerebbe la distribuzione congiunta — cioè proprio l'informazione per cui
queste tavole valgono la pena (quanti stranieri *e* nati in Italia *e* con
quale titolo di studio, non tre totali separati).
"""

from __future__ import annotations

from .. import sdmx
from ..fetch import sdmx_csv
from ..tidy import fmt, read_sdmx, split_code, to_number

BASE_COLUMNS = ["codice_istat", "comune", "anno", "tavola", "indicatore"]


def colonne(dimensioni: list[str]) -> list[str]:
    """Intestazione completa: chiavi, dimensioni della famiglia, valore."""
    return BASE_COLUMNS + [d.lower() for d in dimensioni] + ["valore"]


def tavola(
    dataflow: str,
    *,
    nome: str,
    dest_name: str,
    comuni: dict[str, str],
    dimensioni: list[str],
    decimali: int = 0,
) -> list[dict[str, str]]:
    """Righe di una tavola censuaria, filtrate sui comuni della provincia.

    Il dataflow non si può filtrare per provincia — la dimensione territoriale
    è il comune e il server rifiuta le chiavi con più valori (400, verificato
    anche con soli 50 codici). Si scarica l'Italia intera una volta e si filtra
    qui: è lo stesso patto di `popolazione.py`, e la cache di `dati/raw/` fa sì
    che il costo si paghi una volta sola.
    """
    key = sdmx.key(dataflow, {"FREQ": "A"})
    path = sdmx_csv(dataflow, key, dest_name=dest_name)

    rows: list[dict[str, str]] = []
    for record in read_sdmx(path):
        code, _ = split_code(record.get("REF_AREA", ""))
        if code not in comuni:
            continue
        value = to_number(record.get("OBS_VALUE"))
        if value is None:
            # Un valore soppresso non è uno zero: si omette la riga invece di
            # scrivere 0 (PROSSIMI-PASSI §9).
            continue

        row = {
            "codice_istat": code,
            "comune": comuni[code],
            "anno": record.get("TIME_PERIOD", ""),
            "tavola": nome,
            "indicatore": split_code(record.get("INDICATOR", ""))[1],
            "valore": fmt(value, decimali),
        }
        # Le modalità si riportano per etichetta: i codici SDMX (`N1`, `PROP`)
        # non dicono nulla a chi legge il CSV, e la tavola resta leggibile
        # anche se ISTAT ne aggiunge una.
        for dim in dimensioni:
            row[dim.lower()] = split_code(record.get(dim, ""))[1]
        rows.append(row)
    return rows


def ordina(rows: list[dict[str, str]], dimensioni: list[str]) -> None:
    chiavi = ["codice_istat", "tavola", "anno", "indicatore"] + [d.lower() for d in dimensioni]
    rows.sort(key=lambda r: tuple(r.get(k, "") for k in chiavi))
