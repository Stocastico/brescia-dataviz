"""Gli stessi indicatori ASIA per **tutte le province italiane**: il controllo.

È la tabella che risponde alla domanda che il progetto non poteva porsi: *tutto
quello che si è misurato su Brescia, è di Brescia o è dell'Italia?* Senza un
termine di paragone «il 92,7 % delle unità locali ha meno di dieci addetti» è un
numero che sembra dire qualcosa e non dice niente — potrebbe essere la media
nazionale, e allora non descrive Brescia, descrive il paese.

**Non costa un download.** I file grezzi che alimentano `imprese_classe_addetti`
e `imprese_sezioni_comuni` sono già nazionali: contengono tutti gli ottomila
comuni italiani, e il modulo li filtra su Brescia. Qui gli stessi file vengono
aggregati per provincia — le prime tre cifre del codice ISTAT — e il costo è il
tempo di rileggerli.

⚠️ **Restano aggregati provinciali**, non un secondo soggetto. Il progetto ha un
soggetto solo, e questa tabella serve a collocarlo: nessuna mappa, nessuna
classifica di comuni fuori dal bresciano. La regola di §9 del piano — una sola
geometria di riferimento — non si tocca.

Due tabelle:

- `imprese_province.csv` — aggregati provinciali per classe dimensionale e per
  sezione Ateco. Serve a collocare Brescia in una distribuzione invece che in un
  vuoto;
- `imprese_capoluoghi.csv` — gli stessi indicatori per i **comuni capoluogo**, e
  serve a una domanda sola ma importante: lo svuotamento della classe con almeno
  250 addetti nel comune di Brescia (MET-9) succede anche negli altri capoluoghi?
  Se succede ovunque non è un fatto bresciano, è un fatto del registro.

⚠️ Le province italiane sono cambiate nel tempo (province soppresse, città
metropolitane, nuovi enti). Qui si usa la ripartizione **corrente** dell'elenco
ISTAT applicata a tutti gli anni: per una finestra 2018–2023 è corretta, per
serie più lunghe non lo sarebbe.
"""

from __future__ import annotations

import csv
import io
from collections import defaultdict

from ..config import ELENCO_COMUNI_URL
from ..fetch import fetch
from ..tidy import fmt, read_sdmx, split_code, to_number, write_csv
from .imprese import CLASSI, DATAFLOW_COMUNI, INDICATORI, NACE_TOTALE
from .sezioni import SEZIONI

CAPOLUOGHI_COLUMNS = [
    "codice_istat",
    "capoluogo",
    "provincia",
    "anno",
    "classe_addetti",
    "indicatore",
    "valore",
]

COLUMNS = [
    "codice_provincia",
    "provincia",
    "regione",
    "anno",
    "dimensione",
    "modalita",
    "indicatore",
    "valore",
]


def capoluoghi_italiani() -> dict[str, str]:
    """`codice comune -> nome`, per i soli comuni capoluogo di provincia."""
    path = fetch(ELENCO_COMUNI_URL, "istat_elenco_comuni.csv")
    text = path.read_bytes().decode("latin-1")
    reader = csv.reader(io.StringIO(text), delimiter=";")
    next(reader, None)
    return {
        row[4].strip(): row[6].strip()
        for row in reader
        if len(row) > 13 and row[13].strip() == "1" and len(row[4].strip()) == 6
    }


def province_italiane() -> dict[str, tuple[str, str]]:
    """`codice provincia -> (nome, regione)`, dall'elenco ufficiale ISTAT.

    La chiave è il **codice comune a sei cifre troncato a tre**, non la sigla
    automobilistica: la sigla non è una chiave stabile e non esiste per tutti
    gli enti.
    """
    path = fetch(ELENCO_COMUNI_URL, "istat_elenco_comuni.csv")
    text = path.read_bytes().decode("latin-1")
    reader = csv.reader(io.StringIO(text), delimiter=";")
    next(reader, None)

    fuori: dict[str, tuple[str, str]] = {}
    for row in reader:
        if len(row) <= 11:
            continue
        codice = row[4].strip()
        if len(codice) != 6:
            continue
        fuori.setdefault(codice[:3], (row[11].strip(), row[10].strip()))
    return fuori


def _provincia_di(codice_comune: str) -> str:
    return codice_comune[:3]


def build(comuni: dict[str, str]) -> None:
    del comuni  # qui servono tutte le province, non i comuni di Brescia
    from ..fetch import sdmx_csv
    from .. import sdmx

    province = province_italiane()
    capoluoghi = capoluoghi_italiani()
    # (codice provincia, anno, dimensione, modalità, indicatore) -> somma
    totali: dict[tuple[str, str, str, str, str], float] = defaultdict(float)
    per_capoluogo: list[dict[str, str]] = []

    for indicator, nome_indicatore in INDICATORI.items():
        # --- classi dimensionali, dal file nazionale già scaricato ----------
        path = sdmx_csv(
            DATAFLOW_COMUNI,
            sdmx.key(DATAFLOW_COMUNI, {"FREQ": "A", "DATA_TYPE": indicator,
                                       "ECON_ACTIVITY_NACE_2007": NACE_TOTALE}),
            dest_name=f"istat_asia_classe_{indicator.lower()}.csv",
        )
        for record in read_sdmx(path):
            code, _ = split_code(record.get("REF_AREA", ""))
            if len(code) != 6 or _provincia_di(code) not in province:
                continue
            classe_code, _ = split_code(record.get("PERS_EMPL_SIZE_CLASS", ""))
            valore = to_number(record.get("OBS_VALUE"))
            if valore is None or classe_code not in CLASSI:
                continue
            chiave = (
                _provincia_di(code),
                record.get("TIME_PERIOD", ""),
                "classe_addetti",
                CLASSI[classe_code],
                nome_indicatore,
            )
            totali[chiave] += valore
            if code in capoluoghi:
                per_capoluogo.append(
                    {
                        "codice_istat": code,
                        "capoluogo": capoluoghi[code],
                        "provincia": province[_provincia_di(code)][0],
                        "anno": record.get("TIME_PERIOD", ""),
                        "classe_addetti": CLASSI[classe_code],
                        "indicatore": nome_indicatore,
                        "valore": fmt(valore, 1 if nome_indicatore == "addetti" else 0),
                    }
                )

        # --- sezioni Ateco, dagli stessi file per sezione --------------------
        for sezione in SEZIONI:
            path = sdmx_csv(
                DATAFLOW_COMUNI,
                sdmx.key(DATAFLOW_COMUNI, {"FREQ": "A", "DATA_TYPE": indicator,
                                           "ECON_ACTIVITY_NACE_2007": sezione,
                                           "PERS_EMPL_SIZE_CLASS": "TOTAL"}),
                dest_name=f"istat_asia_sezione_{sezione}_{indicator.lower()}.csv",
            )
            for record in read_sdmx(path):
                code, _ = split_code(record.get("REF_AREA", ""))
                if len(code) != 6 or _provincia_di(code) not in province:
                    continue
                valore = to_number(record.get("OBS_VALUE"))
                if valore is None:
                    continue
                chiave = (
                    _provincia_di(code),
                    record.get("TIME_PERIOD", ""),
                    "sezione",
                    sezione,
                    nome_indicatore,
                )
                totali[chiave] += valore

    decimali = {"addetti": 1, "unita_locali": 0}
    rows = [
        {
            "codice_provincia": codice,
            "provincia": province[codice][0],
            "regione": province[codice][1],
            "anno": anno,
            "dimensione": dimensione,
            "modalita": modalita,
            "indicatore": indicatore,
            "valore": fmt(valore, decimali[indicatore]),
        }
        for (codice, anno, dimensione, modalita, indicatore), valore in totali.items()
    ]
    rows.sort(key=lambda r: (r["codice_provincia"], r["indicatore"], r["dimensione"],
                             r["anno"], r["modalita"]))
    write_csv("imprese_province.csv", rows, COLUMNS)

    per_capoluogo.sort(key=lambda r: (r["codice_istat"], r["indicatore"], r["anno"],
                                      r["classe_addetti"]))
    write_csv("imprese_capoluoghi.csv", per_capoluogo, CAPOLUOGHI_COLUMNS)
