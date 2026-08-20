"""Parte comune alle tavole del Censimento permanente a grana comunale.

Le famiglie `DF_DCSS_*` condividono forma e trappole: chiave posizionale da
comporre leggendo la struttura, e dimensioni che cambiano da famiglia a famiglia
ma **non** dentro la stessa famiglia. Da qui una sola funzione parametrica
invece di tre moduli quasi identici.

> ## Il filtro territoriale funziona, e per mesi abbiamo creduto di no
>
> Questo modulo scaricava **l'Italia intera** per ogni tavola — la prima delle
> dieci tavole sulle migrazioni pesa 866 MB e impiega quasi un'ora — perché una
> nota del progetto diceva che il server rifiuta le chiavi con più codici
> territoriali: «`REF_AREA` con 50 codici riceve `400` esattamente come con
> 205».
>
> **Non è vero.** Quel `400` era una chiave con il numero di campi sbagliato.
> Questi dataflow hanno nove dimensioni, e una chiave con otto punti riceve
> `422 Not enough key values in query, expecting 9 got 8` — che con un client
> meno esplicito diventa un `400` e sembra un rifiuto della sintassi
> `codice+codice`. Con il numero giusto di campi, quindici comuni per richiesta
> passano: **1,6 MB e nove secondi**.
>
> Le stesse dieci tavole passano così da circa otto gigabyte e nove ore a
> **duecento megabyte e venti minuti**. È il caso più caro di una diagnosi
> plausibile e sbagliata che il progetto abbia incontrato, ed è per questo che
> sta scritto qui e non in una nota a piè di pagina.

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

# Quanti comuni per richiesta. Quindici è il valore già collaudato sulle tavole
# MEF: sta largamente dentro la lunghezza massima dell'URL e tiene le risposte
# sotto i due megabyte. Alzarlo fa risparmiare richieste e avvicina il limite
# della chiave, che è il modo in cui si torna a credere che il filtro non
# funzioni.
COMUNI_PER_RICHIESTA = 15


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
    """Righe di una tavola censuaria, chieste al server già filtrate.

    I comuni della provincia si mandano a blocchi nella chiave: il server li
    accetta, e la differenza rispetto allo scarico nazionale è di due ordini di
    grandezza (vedi il riquadro in testa al modulo). `dest_name` diventa il
    prefisso dei file grezzi, uno per blocco.
    """
    codici = sorted(comuni)
    rows: list[dict[str, str]] = []

    for inizio in range(0, len(codici), COMUNI_PER_RICHIESTA):
        blocco = codici[inizio : inizio + COMUNI_PER_RICHIESTA]
        key = sdmx.key(dataflow, {"FREQ": "A", "REF_AREA": "+".join(blocco)})
        path = sdmx_csv(
            dataflow,
            key,
            dest_name=f"{dest_name.removesuffix('.csv')}_{inizio:03d}.csv",
        )
        rows.extend(_righe(path, nome, comuni, dimensioni, decimali))

    return rows


def _righe(
    path,
    nome: str,
    comuni: dict[str, str],
    dimensioni: list[str],
    decimali: int,
) -> list[dict[str, str]]:
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
