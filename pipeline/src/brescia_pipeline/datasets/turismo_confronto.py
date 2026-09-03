"""Lo stesso turismo, ma per **tutte le province italiane**: il termine di paragone.

Il turismo era l'ultimo dei quattro assi senza confronto esterno. Imprese
(`province.py`), redditi (`redditi_confronto.py`) e popolazione (`bilancio.py`)
sanno dire se una cifra bresciana sia bresciana o italiana; il turismo no,
perché la sua fonte — Regione Lombardia, `turismo.py` — si ferma al confine
regionale. «Undici milioni di presenze» senza un altrove è un numero grande che
non dice se sia grande.

## Perché una seconda fonte per lo stesso fenomeno

Non è una scelta: fuori dalla Lombardia il dato regionale non esiste. ISTAT
pubblica il movimento dei clienti negli esercizi ricettivi per provincia
(`122_54_DF_DCSC_TUR_7`), dal 2008 e per tutte e 107, ed è l'unica strada.

Ne viene un guadagno inatteso: la serie ISTAT comincia nel **2008**, quella
regionale nel 2019. Il confronto fra province si porta dietro undici anni di
storia che il progetto non aveva.

⚠️ **Le due fonti non danno lo stesso numero, e la differenza cresce.** Sulle
presenze bresciane la somma dei comuni di Regione Lombardia sta sopra il totale
provinciale ISTAT del 6,5 % nel 2019 e del 10,6 % nel 2024. Non è un errore di
lettura: sono due rilevazioni diverse dello stesso fenomeno, e la divergenza
crescente è essa stessa un dato. La regola che ne è nata (MET-17) è: **una
tabella, una fonte**. Il confronto fra province si fa tutto dentro questa
tabella, i comuni tutti dentro `turismo_comuni_annuale.csv`, e i due numeri non
si mescolano mai nella stessa frase senza dichiararlo.

## Tre trappole, tutte silenziose

1. **Il 2025 non è confrontabile con gli anni prima.** Dal 2025 la voce
   «alloggi in affitto» comprende anche quelli gestiti in forma **non**
   imprenditoriale: le presenze nazionali in quella tipologia passano da 71,8 a
   134,7 milioni (+87,6 %) in un anno, e il totale Italia cresce del 14,9 %.
   Nessun boom: una definizione cambiata. Le righe interessate portano
   `stato = definizione_cambiata`, e sono esattamente le tre in cui la voce
   entra — `alloggi in affitto`, `extra-alberghiero` che la contiene, e
   `totale`. Alberghiero e campeggi restano confrontabili.
2. **La Sardegna ha una geografia che cambia nel 2017.** Olbia-Tempio,
   Ogliastra, Medio Campidano e Carbonia-Iglesias sono state soppresse: la
   fonte le riporta fino al 2016 e da lì passa a Sud Sardegna. Qui restano solo
   le 107 province attuali, quindi per le quattro province sarde superstiti il
   valore prima del 2017 si riferisce a un territorio **più piccolo** di quello
   di oggi. Le righe lo dichiarano con `stato = confine_cambiato`: una crescita
   2008–2024 calcolata su quelle serie è una crescita di superficie.
3. **I codici territoriali sono NUTS 2010, non 2021.** Veneto, Emilia, Toscana
   e Lazio hanno codici `ITD…` e `ITE…` che nell'elenco ISTAT corrente non
   esistono più (sono diventati `ITH…` e `ITI…`). Agganciare per codice NUTS
   perde metà delle province **senza errore**: qui l'aggancio è sul nome
   normalizzato, e un test verifica che le province ritrovate siano 107.

## Cosa produce

`turismo_province.csv`, una riga per territorio × anno × tipologia × residenza ×
indicatore. Comprende anche l'Italia e le regioni — arrivano nello stesso
scarico e costano zero — distinti dalla colonna `livello`.

⚠️ Come per `province.py`: **non è un secondo soggetto.** Serve a collocare
Brescia in una distribuzione, non a disegnare mappe fuori provincia.
"""

from __future__ import annotations

import csv
import io

from .. import sdmx
from ..config import ELENCO_COMUNI_URL
from ..fetch import fetch, sdmx_csv
from ..tidy import fmt, read_sdmx, split_code, to_number, write_csv

DATAFLOW = "122_54_DF_DCSC_TUR_7"

# Le tipologie che servono, non tutte e undici: i due aggregati che partizionano
# il totale (`ALL = HOTELLIKE + OTHER`, verificato da un test) più le due voci
# extra-alberghiere che distinguono il Garda dal resto d'Italia.
TIPOLOGIE = {
    "ALL": "totale",
    "HOTELLIKE": "alberghiero",
    "OTHER": "extra-alberghiero",
    "CAMP_VILL": "campeggi e villaggi",
    "DWELLINGS": "alloggi in affitto",
}

RESIDENZE = {"WORLD": "totale", "IT": "Italia", "WRL_X_ITA": "estero"}
INDICATORI = {"AR": "arrivi", "NI": "presenze"}

# Primo anno in cui la voce «alloggi in affitto» comprende anche la gestione non
# imprenditoriale. Vedi la trappola 1 nel docstring.
ANNO_DEFINIZIONE_ALLOGGI = 2025
TIPOLOGIE_TOCCATE = {"DWELLINGS", "OTHER", "ALL"}

# Anno in cui le quattro province sarde soppresse escono dalla fonte e il
# territorio delle superstiti si allarga.
ANNO_RIORDINO_SARDEGNA = 2017
REGIONE_SARDEGNA = "Sardegna"

STATO_OSSERVATO = "osservato"
STATO_DEFINIZIONE = "definizione_cambiata"
STATO_CONFINE = "confine_cambiato"

COLUMNS = [
    "codice_nuts3",
    "codice_provincia",
    "territorio",
    "regione",
    "livello",
    "anno",
    "tipologia",
    "residenza",
    "indicatore",
    "valore",
    "stato",
]


# Le uniche due province che i due elenchi scrivono diversamente. Non si
# risolvono con una normalizzazione generica — «Reggio di Calabria» contro
# «Reggio Calabria» è una parola in più, e una regola che togliesse le
# preposizioni romperebbe «Reggio nell'Emilia», che invece combacia. Meglio due
# righe esplicite di una regola che sbaglia altrove.
ALIAS = {
    "Reggio di Calabria": "Reggio Calabria",
}


def _normalizza(nome: str) -> str:
    """Il nome della fonte nella forma dell'elenco ISTAT.

    Le differenze sono due sole: gli spazi attorno alla barra dei nomi bilingui
    (`"Bolzano / Bozen"`) e i due casi in `ALIAS`. Le altre 104 province
    combaciano carattere per carattere.
    """
    pulito = " ".join(nome.split()).replace(" / ", "/")
    return ALIAS.get(pulito, pulito)


def province_per_nome() -> dict[str, tuple[str, str]]:
    """`nome normalizzato -> (codice provincia, regione)` per le 107 attuali.

    L'aggancio è sul nome e non sul codice NUTS: la fonte usa la vintage 2010 e
    l'elenco ISTAT la 2021, e mezza Italia ha cambiato codice in mezzo.
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
        fuori.setdefault(_normalizza(row[11].strip()), (codice[:3], row[10].strip()))
    return fuori


def _stato(codice_tipologia: str, regione: str, anno: str) -> str:
    try:
        numero_anno = int(anno)
    except ValueError:
        return STATO_OSSERVATO
    if numero_anno >= ANNO_DEFINIZIONE_ALLOGGI and codice_tipologia in TIPOLOGIE_TOCCATE:
        return STATO_DEFINIZIONE
    if regione == REGIONE_SARDEGNA and numero_anno < ANNO_RIORDINO_SARDEGNA:
        return STATO_CONFINE
    return STATO_OSSERVATO


def build(comuni: dict[str, str]) -> None:
    del comuni  # qui servono tutte le province, non i comuni di Brescia

    province = province_per_nome()
    rows: list[dict[str, str]] = []
    trovate: set[str] = set()

    for codice_tipologia, tipologia in TIPOLOGIE.items():
        chiave = sdmx.key(
            DATAFLOW,
            {
                "FREQ": "A",
                "ADJUSTMENT": "N",
                "TYPE_ACCOMMODATION": codice_tipologia,
                "ECON_ACTIVITY_NACE_2007": "551_553",
                "LOCALITY_TYPE": "ALL",
                "URBANIZ_DEGREE": "ALL",
                "COASTAL_AREA": "ALL",
                "SIZE_BY_NUMBER_ROOMS": "TOT",
            },
        )
        path = sdmx_csv(
            DATAFLOW, chiave, dest_name=f"istat_turismo_province_{codice_tipologia.lower()}.csv"
        )

        for record in read_sdmx(path):
            valore = to_number(record.get("OBS_VALUE"))
            if valore is None:
                continue
            indicatore = INDICATORI.get(split_code(record.get("DATA_TYPE", ""))[0])
            residenza = RESIDENZE.get(split_code(record.get("COUNTRY_RES_GUESTS", ""))[0])
            if indicatore is None or residenza is None:
                continue

            nuts, etichetta = split_code(record.get("REF_AREA", ""))
            nome = _normalizza(etichetta)
            anno = record.get("TIME_PERIOD", "")

            if nuts == "IT":
                codice_provincia, regione, livello = "", "", "italia"
            elif len(nuts) == 5:
                # Un codice NUTS3 di cinque caratteri è una provincia; le quattro
                # sarde soppresse non sono nell'elenco corrente e cadono qui.
                if nome not in province:
                    continue
                codice_provincia, regione = province[nome]
                livello = "provincia"
                trovate.add(codice_provincia)
            else:
                codice_provincia, regione, livello = "", nome, "regione"

            rows.append(
                {
                    "codice_nuts3": nuts,
                    "codice_provincia": codice_provincia,
                    "territorio": nome,
                    "regione": regione,
                    "livello": livello,
                    "anno": anno,
                    "tipologia": tipologia,
                    "residenza": residenza,
                    "indicatore": indicatore,
                    "valore": fmt(valore),
                    "stato": _stato(codice_tipologia, regione, anno),
                }
            )

    if len(trovate) != 107:
        raise RuntimeError(
            f"agganciate {len(trovate)} province invece di 107: "
            "i nomi della fonte non combaciano più con l'elenco ISTAT"
        )

    rows.sort(
        key=lambda r: (
            r["livello"],
            r["codice_nuts3"],
            r["indicatore"],
            r["tipologia"],
            r["residenza"],
            r["anno"],
        )
    )
    write_csv("turismo_province.csv", rows, COLUMNS)
