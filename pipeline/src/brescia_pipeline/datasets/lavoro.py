"""Lavoro e istruzione dal Censimento permanente, più il tasso di occupazione.

Grane diverse per necessità: il censimento arriva al comune, la rilevazione
sulle forze di lavoro si ferma alla provincia. Le tabelle restano separate
proprio per non far sembrare confrontabile ciò che non lo è.
"""

from __future__ import annotations

from ..config import COMUNE_BRESCIA, PROVINCIA_BRESCIA_SDMX
from .. import sdmx
from ..fetch import sdmx_csv
from ..tidy import fmt, read_sdmx, split_code, to_number, write_csv

# Censimento permanente, grana comune. Le dimensioni cambiano da tavola a
# tavola: la chiave la compone `sdmx.key` leggendo la struttura dal server.
CENSIMENTO = {
    "occupati_settore": "DF_DCSS_EMPLP_2_COM",
    "occupati_posizione": "DF_DCSS_EMPLP_1_COM",
    "condizione_professionale_eta": "DF_DCSS_ISTR_LAV_PEN_2_TV_3",
    "condizione_professionale_cittadinanza": "DF_DCSS_ISTR_LAV_PEN_2_TV_4",
    "istruzione_eta": "DF_DCSS_ISTR_LAV_PEN_2_TV_1",
    "istruzione_cittadinanza": "DF_DCSS_ISTR_LAV_PEN_2_TV_2",
    "pendolarismo": "DF_DCSS_ISTR_LAV_PEN_2_TV_5",
}

# Le dimensioni delle sette tavole e il nome della colonna che le riporta. È
# l'unione: ciascuna tavola ne valorizza un sottoinsieme, e le altre restano
# celle vuote. I nomi sono quelli che `tasso_occupazione_provincia.csv` usa già
# per gli stessi concetti — `citizenship` accanto a `cittadinanza` nello stesso
# modulo sarebbe un dizionario da tenere a mente per leggere due file.
DIMENSIONI = {
    "GENDER": "sesso",
    "AGE_CLASS": "classe_eta",
    "AGE_NOCLASS": "eta",
    "CITIZENSHIP": "cittadinanza",
    "EDU_ATTAIN": "titolo_studio",
    "EMPLOYMENT_STATUS": "posizione_professionale",
    "BRANCH_ECON_ACT": "settore_attivita",
    "CUR_ACT_STAT": "condizione_professionale",
    "LOC_DEST": "luogo_destinazione",
    "REAS_COMMUTING": "motivo_spostamento",
}

# Le dimensioni che non diventano una colonna omonima: `FREQ` e `REF_AREA` sono
# fissate dalla chiave (annuale, comune di Brescia), `INDICATOR` finisce in
# `indicatore`. Tutto il resto va dichiarato in `DIMENSIONI`, o il build si
# ferma: in forma larga una dimensione non riportata non sparisce, appiattisce
# osservazioni diverse su righe identiche.
DIMENSIONI_FUORI_COLONNA = {"FREQ", "REF_AREA", "INDICATOR"}

CENSIMENTO_COLUMNS = ["tavola", "anno", "indicatore"] + list(DIMENSIONI.values()) + ["valore"]
OCCUPAZIONE_COLUMNS = [
    "territorio", "anno", "indicatore", "sesso", "eta", "titolo_studio", "cittadinanza", "valore",
]

TASSO_OCCUPAZIONE = "150_915_DF_DCCV_TAXOCCU1_YOUTH_1"


def _censimento() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for tavola, dataflow in CENSIMENTO.items():
        chiave = sdmx.key(dataflow, {"FREQ": "A", "REF_AREA": COMUNE_BRESCIA})
        ignote = set(sdmx.dimensions(dataflow)) - DIMENSIONI_FUORI_COLONNA - set(DIMENSIONI)
        if ignote:
            raise RuntimeError(
                f"{tavola}: dimensioni non dichiarate {sorted(ignote)}. "
                "Aggiungerle a DIMENSIONI, o le loro modalità si appiattiscono "
                "su righe indistinguibili"
            )
        path = sdmx_csv(dataflow, chiave, dest_name=f"istat_cens_{tavola}.csv")
        for record in read_sdmx(path):
            value = to_number(record.get("OBS_VALUE"))
            if value is None:
                continue
            row = {
                "tavola": tavola,
                "anno": record.get("TIME_PERIOD", ""),
                # Non è decorazione: `occupati_settore` conta occupati, le
                # tavole ISTR_LAV la popolazione residente, `pendolarismo` chi
                # si sposta ogni giorno. Senza, le sette tavole sembrano
                # contare la stessa cosa.
                "indicatore": split_code(record.get("INDICATOR", ""))[1],
                "valore": fmt(value, 1),
            }
            # Una riga per osservazione, con le sue dimensioni in colonna: le
            # modalità per etichetta, come nelle altre tavole censuarie, e le
            # colonne che questa tavola non usa restano vuote.
            for dim, colonna in DIMENSIONI.items():
                row[colonna] = split_code(record.get(dim, ""))[1]
            rows.append(row)
    return rows


def _tasso_occupazione() -> list[dict[str, str]]:
    path = sdmx_csv(TASSO_OCCUPAZIONE, dest_name="istat_tasso_occupazione.csv")
    rows = []
    for record in read_sdmx(path):
        area, _ = split_code(record.get("REF_AREA", ""))
        if area != PROVINCIA_BRESCIA_SDMX:
            continue
        value = to_number(record.get("OBS_VALUE"))
        if value is None:
            continue
        rows.append(
            {
                "territorio": area,
                "anno": record.get("TIME_PERIOD", ""),
                "indicatore": split_code(record.get("DATA_TYPE", ""))[1],
                "sesso": split_code(record.get("SEX", ""))[1],
                "eta": split_code(record.get("AGE", ""))[1],
                "titolo_studio": split_code(record.get("EDU_LEV_HIGHEST", ""))[1],
                "cittadinanza": split_code(record.get("CITIZENSHIP", ""))[1],
                "valore": fmt(value, 2),
            }
        )
    return rows


def build(comuni: dict[str, str]) -> None:
    censimento = _censimento()
    chiavi = ["tavola", "anno", "indicatore"] + list(DIMENSIONI.values())
    censimento.sort(key=lambda r: tuple(r[k] for k in chiavi))
    write_csv("censimento_lavoro_brescia.csv", censimento, CENSIMENTO_COLUMNS)

    occupazione = _tasso_occupazione()
    occupazione.sort(key=lambda r: (r["anno"], r["indicatore"], r["sesso"], r["eta"]))
    write_csv("tasso_occupazione_provincia.csv", occupazione, OCCUPAZIONE_COLUMNS)
