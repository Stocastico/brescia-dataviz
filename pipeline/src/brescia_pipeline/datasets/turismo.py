"""Flussi turistici nei comuni della provincia (Regione Lombardia, 2019-2024).

Asse minore per la città, centrale per la provincia: il Garda concentra la gran
parte delle presenze e il capoluogo pesa poco.

⚠️ Due trappole nella fonte, entrambe già costate un errore:
1. le righe esistono per ogni combinazione di `tipo_struttura` e
   `cittadinanza_turisti`, totali inclusi: sommare senza filtrare conta fino a
   tre volte le stesse notti;
2. i comuni con poche strutture riportano «Dato riservato» invece del numero.
   È un dato mancante, non uno zero.
"""

from __future__ import annotations

from ..config import SIGLA_PROVINCIA
from ..fetch import socrata_json
from ..tidy import fmt, read_socrata, to_number, write_csv

RESOURCE_ANNUALE = "vyxt-7jdx"
RESOURCE_MENSILE = "mzxz-sz25"

MESI = {
    "Gennaio": "01", "Febbraio": "02", "Marzo": "03", "Aprile": "04",
    "Maggio": "05", "Giugno": "06", "Luglio": "07", "Agosto": "08",
    "Settembre": "09", "Ottobre": "10", "Novembre": "11", "Dicembre": "12",
}

ANNUALE_COLUMNS = [
    "codice_istat", "comune", "anno", "tipo_struttura", "cittadinanza",
    "arrivi", "presenze", "permanenza_media", "stato",
]

# Stati della riga, in `stato`:
#   osservato     - valore dichiarato dalla fonte
#   riservato     - la fonte sopprime il dato per riservatezza statistica
#   zero_fittizio - la riga «Totale» dichiara 0 ma tutte le sue componenti sono
#                   riservate: e' uno zero calcolato su celle soppresse, non una
#                   misura. Va escluso dai grafici, non disegnato come «nessun
#                   turismo». Riguarda un solo comune (Gottolengo, 2024).
STATO_OSSERVATO = "osservato"
STATO_RISERVATO = "riservato"
STATO_ZERO_FITTIZIO = "zero_fittizio"
MENSILE_COLUMNS = ["codice_istat", "comune", "mese", "arrivi", "presenze", "permanenza_media"]


def _codice_istat(record: dict) -> str | None:
    """Il campo Socrata è il codice a 5 cifre senza lo zero iniziale."""
    raw = str(record.get("codice_istat", "")).strip()
    if not raw:
        return None
    return raw.zfill(6)


def build(comuni: dict[str, str]) -> None:
    annuale = read_socrata(
        socrata_json(
            RESOURCE_ANNUALE,
            dest_name="lombardia_turismo_annuale_bs.json",
            where=f"provincia='{SIGLA_PROVINCIA}'",
        )
    )

    # La fonte si contraddice: per qualche comune le righe di dettaglio sono
    # tutte «Dato riservato» ma la riga «Totale» dichiara 0. E' uno zero
    # calcolato su celle soppresse, non una misura, e in una mappa diventerebbe
    # «nessun turismo». Si individua confrontando totale e componenti.
    componenti_riservate: dict[tuple[str, str, str], bool] = {}
    for record in annuale:
        if record.get("tipo_struttura") == "Totale":
            continue
        chiave = (
            str(record.get("codice_istat", "")),
            str(record.get("anno", "")),
            str(record.get("cittadinanza_turisti", "")),
        )
        osservata = to_number(record.get("presenze")) is not None
        componenti_riservate[chiave] = componenti_riservate.get(chiave, True) and not osservata

    rows = []
    for record in annuale:
        code = _codice_istat(record)
        if code not in comuni:
            continue

        presenze = to_number(record.get("presenze"))
        if presenze is None:
            stato = STATO_RISERVATO
        elif (
            presenze == 0
            and record.get("tipo_struttura") == "Totale"
            and componenti_riservate.get(
                (
                    str(record.get("codice_istat", "")),
                    str(record.get("anno", "")),
                    str(record.get("cittadinanza_turisti", "")),
                ),
                False,
            )
        ):
            stato = STATO_ZERO_FITTIZIO
        else:
            stato = STATO_OSSERVATO

        rows.append(
            {
                "codice_istat": code,
                "comune": comuni[code],
                "anno": record.get("anno", ""),
                "tipo_struttura": record.get("tipo_struttura", ""),
                "cittadinanza": record.get("cittadinanza_turisti", ""),
                "arrivi": fmt(to_number(record.get("arrivi"))),
                "presenze": fmt(presenze),
                "permanenza_media": fmt(to_number(record.get("permanenza_media")), 2),
                "stato": stato,
            }
        )
    rows.sort(key=lambda r: (r["codice_istat"], r["anno"], r["tipo_struttura"], r["cittadinanza"]))
    write_csv("turismo_comuni_annuale.csv", rows, ANNUALE_COLUMNS)

    mensile = read_socrata(
        socrata_json(
            RESOURCE_MENSILE,
            dest_name="lombardia_turismo_mensile_bs.json",
            where=f"provincia='{SIGLA_PROVINCIA}'",
        )
    )

    monthly = []
    for record in mensile:
        code = _codice_istat(record)
        if code not in comuni:
            continue
        mese = MESI.get(str(record.get("mese", "")).strip())
        anno = str(record.get("anno", "")).strip()
        if not mese or not anno:
            continue
        monthly.append(
            {
                "codice_istat": code,
                "comune": comuni[code],
                "mese": f"{anno}-{mese}",
                "arrivi": fmt(to_number(record.get("arrivi"))),
                "presenze": fmt(to_number(record.get("presenze"))),
                "permanenza_media": fmt(to_number(record.get("permanenza_media")), 2),
            }
        )
    monthly.sort(key=lambda r: (r["codice_istat"], r["mese"]))
    write_csv("turismo_comuni_mensile.csv", monthly, MENSILE_COLUMNS)
