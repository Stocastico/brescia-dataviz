"""Iscritti e laureati dall'open data del MUR (USTAT).

Tre tabelle, e la ragione per cui sono tre sta in un'avvertenza che questo
progetto porta scritta da mesi: **Brescia ha due atenei**, la statale e la sede
bresciana della Cattolica, e la statale da sola sottostima la popolazione
universitaria. Finché si contava «per ateneo» quella frase restava una nota a
piè di pagina, perché la Cattolica è **un solo ateneo** con codice milanese
(1504) e quattro sedi: dal lato ateneo la Brescia che studia non è separabile.

La fornitura però ha anche il taglio per **provincia della sede didattica**, e
da lì la nota diventa una misura: nel 2024/2025 gli iscritti con sede didattica
in provincia di Brescia sono **19.873** — 15.424 alla statale, 4.288 alla
Cattolica, 161 alla Statale di Milano — contro i 16.456 che si leggono
contando l'ateneo «Brescia». Un quinto della popolazione universitaria stava
fuori dal conto. Le tre tabelle rispondono a tre domande diverse:

| tabella | domanda |
|---|---|
| `universita_atenei.csv` | quanto è grande ogni ateneo italiano, e come cambia: iscritti, immatricolati, laureati |
| `universita_sedi_brescia.csv` | **chi studia in provincia**, per ateneo e disciplina, e da dove viene |
| `universita_residenza_comuni.csv` | **quanti studiano i residenti**, comune per comune |

Le trappole, in ordine di quanto costano.

**1. Il codice del comune non ha lo zero iniziale.** La fornitura scrive
`17001`, il progetto `017001`. Un join fatto senza normalizzare non fallisce:
restituisce **zero righe**, che è il modo peggiore di sbagliare. Qui il codice
si riempie di zeri a sei cifre, ed è la stessa lezione di MET-13.

**2. Prestine c'è ancora.** Soppresso nel 2016, territorio di Bienno, compare
nella serie storica fino a quell'anno — esattamente come negli archivi OMI, dove
arrivava col codice catastale `G935`. Le sue righe si **sommano** a Bienno:
scartarle sposterebbe un pezzo di Valle Camonica fuori dalla provincia senza
dirlo.

**3. Iscritti e laureati non contano lo stesso anno.** `2024/2025` è un anno
accademico, `2025` è un anno solare. Ridotti tutti e due a un numero e messi
nella stessa colonna diventano una serie che *sembra* continua; la colonna
`anno_tipo` esiste perché confrontarli sia una scelta e non una svista (MET-17).

**4. L'encoding è cp1252**, non UTF-8 e nemmeno latin-1: qualche denominazione
porta il trattino `–` come byte `0x96`, che in latin-1 non è una lettera e in
UTF-8 non è nemmeno un byte valido.

**5. Il sesso porta anche un `9`.** Sono due righe in tutta la fornitura, e il
codice resta com'è: la fonte non lo scioglie, e scioglierlo a intuito è
l'invenzione che questo progetto evita.

**Cosa resta fuori, e perché.** Gli **immatricolati** sono entrati (settembre
2026): stessa forma, `RISORSE` più lungo, e la serie più lunga delle tre —
comincia nel **1998/99**. I **fuori corso** no, e la ragione è che non hanno la
dimensione ateneo: `19_iscrittixfuoricorso.csv` è **solo nazionale**, quindi in
un progetto provinciale è un numero senza territorio. Restano fuori anche gli
internazionali per paese e i corsi di studio, per la ragione ordinaria: nessuna
storia li usa. La prossima estensione utile è
`12_immatricolatixresidenzasedecorsogruppo.csv`, che è il gemello per sede
didattica di quello che qui alimenta `universita_sedi_brescia.csv`: darebbe gli
**ingressi** in provincia e non solo lo stock.

Le etichette dei gruppi
disciplinari vengono da `03_iscrittixgruppo.csv`, cioè dalla fonte stessa, e non
dal foglio `gruppidisciplinari.xlsx`: questo progetto non apre XLSX, di
proposito.

Licenza: **IODL 2.0** (attribuzione). Citazione: «MUR — USTAT».
"""

from __future__ import annotations

import csv
import io
import json
import re
from collections import defaultdict
from pathlib import Path

from ..fetch import fetch
from ..tidy import write_csv

CKAN = "https://dati-ustat.mur.gov.it/api/3/action/package_show"

# `chiave interna -> (pacchetto CKAN, nome del file nella risorsa)`. Il nome del
# file è la chiave meno instabile che questa API offra: gli UUID delle risorse
# cambiano quando il MUR ne ripubblica una, il nome no.
RISORSE = {
    "iscritti_ateneo": ("iscritti", "02_iscrittixateneo.csv"),
    "immatricolati_ateneo": ("immatricolati", "02_immatricolatixateneo.csv"),
    "iscritti_gruppo": ("iscritti", "03_iscrittixgruppo.csv"),
    "iscritti_sede": ("iscritti", "14a_iscrittixresidenzasedecorsogruppo.csv"),
    "iscritti_residenza": ("iscritti", "07_iscrittixresidenza.csv"),
    "laureati_ateneo": ("laureati", "02_laureatixateneo.csv"),
}

COLUMNS_ATENEI = ["anno", "anno_tipo", "ateneo_codice", "ateneo", "sesso", "indicatore", "valore"]
COLUMNS_SEDI = [
    "anno", "ateneo_codice", "ateneo", "gruppo_codice", "gruppo",
    "regione_residenza", "provincia_residenza", "iscritti",
]
COLUMNS_RESIDENZA = ["codice_istat", "comune", "anno", "sesso", "iscritti"]

# Il codice provincia della sede didattica arriva senza zeri (`17`, non `017`).
PROVINCIA_BRESCIA = "017"

# Come `CATASTALI_SOPPRESSI` in `compravendite.py`, con la stessa storia dietro:
# Prestine è territorio di Bienno dal 2016.
COMUNI_SOPPRESSI = {"017154": "017018"}

ANNO = re.compile(r"^(\d{4})(?:/\d{4})?$")


def anno_di(testo: str) -> str:
    """`2024/2025` -> `2024`; `2025` -> `2025`.

    L'anno accademico si riduce a quello di **apertura**, che è la convenzione
    con cui il resto del progetto scrive gli anni. Un formato inatteso è un
    errore: una serie con un anno vuoto in mezzo è peggio di un build rosso.
    """
    trovato = ANNO.match((testo or "").strip())
    if not trovato:
        raise RuntimeError(f"anno non riconosciuto: {testo!r}")
    return trovato.group(1)


def url_risorsa(pacchetto: dict, nome_file: str) -> str:
    """L'URL della risorsa che finisce con `nome_file`."""
    for risorsa in pacchetto.get("resources", []):
        if (risorsa.get("url") or "").endswith(nome_file):
            return risorsa["url"]
    raise RuntimeError(
        f"{nome_file} non è più fra le risorse del pacchetto: "
        "il MUR l'ha rinominata o ritirata, e va guardato prima di indovinare"
    )


def risorse() -> dict[str, Path]:
    """I cinque CSV in `dati/raw/`, scaricati o riletti dalla cache."""
    pacchetti: dict[str, dict] = {}
    fuori: dict[str, Path] = {}
    for chiave, (pacchetto, nome_file) in RISORSE.items():
        if pacchetto not in pacchetti:
            path = fetch(
                CKAN, f"mur_ckan_{pacchetto}.json", params={"id": pacchetto}, force=True
            )
            pacchetti[pacchetto] = json.loads(path.read_text(encoding="utf-8"))["result"]
        url = url_risorsa(pacchetti[pacchetto], nome_file)
        fuori[chiave] = fetch(url, f"mur_{nome_file}")
    return fuori


def _righe(percorso: Path) -> list[dict[str, str]]:
    testo = percorso.read_bytes().decode("cp1252")
    return list(csv.DictReader(io.StringIO(testo), delimiter=";"))


def build(comuni: dict[str, str]) -> None:
    file = risorse()
    _atenei(file)
    _sedi(file)
    _residenza(file, comuni)


def _atenei(file: dict[str, Path]) -> None:
    righe: list[dict[str, str]] = []
    for chiave, indicatore, colonna, anno_tipo in [
        ("iscritti_ateneo", "iscritti", "Isc", "accademico"),
        # Gli immatricolati sono la porta d'ingresso, e la loro serie è la più
        # lunga delle tre: comincia nel 1998/99, dieci anni prima degli
        # iscritti per ateneo. Chi confronta i tre indicatori sullo stesso
        # grafico deve partire dall'anno in cui esistono tutti.
        ("immatricolati_ateneo", "immatricolati", "Immatricolati", "accademico"),
        ("laureati_ateneo", "laureati", "Lau", "solare"),
    ]:
        for record in _righe(file[chiave]):
            anno = record.get("AnnoA") or record.get("AnnoS")
            righe.append({
                "anno": anno_di(anno),
                "anno_tipo": anno_tipo,
                "ateneo_codice": record["AteneoCOD"].strip(),
                "ateneo": record["AteneoNOME"].strip(),
                "sesso": record["SESSO"].strip(),
                "indicatore": indicatore,
                "valore": record[colonna].strip(),
            })

    righe.sort(key=lambda r: (r["ateneo_codice"], r["indicatore"], r["anno"], r["sesso"]))
    write_csv("universita_atenei.csv", righe, COLUMNS_ATENEI)


def _sedi(file: dict[str, Path]) -> None:
    gruppi = {
        r["GruppoCOD"].strip(): r["GruppoNOME"].strip()
        for r in _righe(file["iscritti_gruppo"])
    }
    righe: list[dict[str, str]] = []
    for record in _righe(file["iscritti_sede"]):
        if record["SedeP"].strip().zfill(3) != PROVINCIA_BRESCIA:
            continue
        codice = record["GruppoCODICE"].strip()
        righe.append({
            "anno": anno_di(record["AnnoA"]),
            "ateneo_codice": record["AteneoCOD"].strip(),
            "ateneo": record["AteneoNOME"].strip(),
            "gruppo_codice": codice,
            "gruppo": gruppi.get(codice, ""),
            "regione_residenza": record["ResidenzaR"].strip(),
            "provincia_residenza": record["ResidenzaP"].strip(),
            "iscritti": record["Isc"].strip(),
        })
    if not righe:
        raise RuntimeError(
            f"nessun iscritto con sede didattica in provincia {PROVINCIA_BRESCIA}: "
            "la colonna SedeP ha cambiato forma"
        )

    righe.sort(key=lambda r: (r["anno"], r["ateneo_codice"], r["gruppo_codice"],
                              r["provincia_residenza"]))
    write_csv("universita_sedi_brescia.csv", righe, COLUMNS_SEDI)


def _residenza(file: dict[str, Path], comuni: dict[str, str]) -> None:
    # Prestine e Bienno finiscono sulla stessa chiave negli anni in cui
    # esistevano entrambi: la somma è il punto, non un effetto collaterale.
    totali: dict[tuple[str, str, str], int] = defaultdict(int)
    for record in _righe(file["iscritti_residenza"]):
        codice = record["CODIstatComune"].strip().zfill(6)
        codice = COMUNI_SOPPRESSI.get(codice, codice)
        if codice not in comuni:
            continue
        totali[(codice, anno_di(record["AnnoA"]), record["SESSO"].strip())] += int(
            record["Isc"].strip()
        )
    if not totali:
        raise RuntimeError("nessun comune della provincia negli iscritti per residenza")

    righe = [
        {
            "codice_istat": codice,
            "comune": comuni[codice],
            "anno": anno,
            "sesso": sesso,
            "iscritti": str(valore),
        }
        for (codice, anno, sesso), valore in sorted(totali.items())
    ]
    write_csv("universita_residenza_comuni.csv", righe, COLUMNS_RESIDENZA)
