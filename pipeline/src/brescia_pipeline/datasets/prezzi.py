"""L'indice dei prezzi al consumo (NIC), medie annue: il deflatore che mancava.

Fino a settembre 2026 il progetto non aveva un deflatore, e la cosa era scritta
in tre posti come un limite dichiarato: i redditi MEF sono in **euro correnti**,
quindi «fra il 2012 e il 2023 una parte della crescita è inflazione» e non si
poteva dire quanta. Con le quotazioni OMI il limite ha smesso di essere una
nota: la serie del capoluogo comincia nel **2004**, e su ventun anni la
differenza fra euro correnti ed euro costanti non è una sfumatura, è il segno.

## La trappola: tre basi che non si sovrappongono

ISTAT pubblica le medie annue del NIC (`167_747_DCSP_NIC2B2025_1`) in tre basi,
e sono **tre serie diverse dello stesso indice**:

| anni | base | ultimo/primo valore |
|---|---|---|
| 1996–2010 | 1995 = 100 | 2010 → 139,8 |
| 2011–2015 | 2010 = 100 | 2011 → 102,8 |
| 2016–2025 | 2015 = 100 | 2016 → 99,9 |

Messe in colonna così come sono, e tirate su un grafico, danno **due crolli del
30 %** che non sono mai successi. E non c'è un anno di sovrapposizione da cui
ricavare il raccordo: la prima base finisce dove la seconda comincia.

Il ponte è la **variazione annua**, che la stessa fonte pubblica per ogni anno
(`MEASURE = 8`) e che nell'anno di giunzione è calcolata da ISTAT sul suo
raccordo interno: il 2011 vale `+2,8 %` sul 2010 anche se i due numeri stanno
in due basi diverse. Quindi: dentro una base valgono i livelli pubblicati, fra
una base e la successiva vale la variazione. È MET-20.

⚠️ **Il raccordo costa una cifra di precisione.** Le variazioni sono pubblicate
con un decimale, quindi ogni giunzione porta un errore fino a ~0,05 %. Su due
giunzioni in ventun anni è un decimo di punto contro un'inflazione cumulata di
oltre il 40 %: non tocca nessuna conclusione, ma va detto invece che scoperto.

## Cosa produce

`indice_prezzi.csv`, una riga per anno: l'indice concatenato in **base 2015 =
100**, la variazione annua della fonte, la base in cui la fonte lo pubblica e lo
stato — `osservato` per gli anni che ISTAT dà già in base 2015, `concatenato`
per quelli riscalati qui.

⚠️ **È l'indice nazionale.** Un indice provinciale dei prezzi al consumo esiste
per i capoluoghi, ma non per tutta la serie e non per tutti: deflazionare
Brescia con l'Italia assume che l'inflazione bresciana sia quella italiana, ed è
un'assunzione, non una misura. Va dichiarata ovunque la serie venga usata.
"""

from __future__ import annotations

from .. import sdmx
from ..fetch import sdmx_csv
from ..tidy import fmt, read_sdmx, split_code, to_number, write_csv

DATAFLOW = "167_747_DCSP_NIC2B2025_1"

# L'indice generale, cioè l'intero paniere: la voce `00` di ECOICOP.
INDICE_GENERALE = "00"
# Le due misure che servono: il livello dell'indice e la sua variazione annua.
MISURA_INDICE = "4"
MISURA_VARIAZIONE = "8"

# `DATA_TYPE` non dice «base 2015»: dice `40`. La corrispondenza sta qui, ed è
# l'unica cosa di questo modulo che invecchia — quando ISTAT passerà alla base
# 2025 comparirà un quarto codice, e la concatenazione lo attaccherà da sola
# **solo** se aggiunto a questa mappa. Un codice sconosciuto fa fallire il build
# invece di far sparire in silenzio gli anni nuovi.
BASI = {"2": "1995", "10": "2010", "40": "2015"}

# La base in cui esce la tabella. È quella dell'ultimo tratto pubblicato, così
# gli anni recenti restano i numeri della fonte e il riscalamento tocca il
# passato: se un giorno cambia, cambia con `BASI`.
BASE_TABELLA = "2015"

STATO_OSSERVATO = "osservato"
STATO_CONCATENATO = "concatenato"

COLUMNS = ["anno", "indice", "indice_fonte", "variazione_annua", "base_fonte", "stato"]


def concatena(
    indici: dict[str, dict[str, float]],
    variazioni: dict[str, float],
    *,
    base: str,
) -> dict[str, float]:
    """Le basi attaccate in una serie sola, con 100 nell'anno `base`.

    `indici` è `codice base -> anno -> livello pubblicato`; `variazioni` è
    `anno -> variazione percentuale sull'anno prima`. Dentro una base valgono i
    livelli; nell'anno in cui una base comincia vale la variazione (vedi il
    docstring del modulo).

    Si ferma — invece di attaccare due tratti a caso — se manca la variazione
    dell'anno di giunzione o se fra due basi c'è un buco d'anni: sono i due modi
    in cui una serie concatenata sbaglia **senza sembrare sbagliata**.
    """
    tratti = sorted(
        ((min(livelli), codice, livelli) for codice, livelli in indici.items() if livelli),
    )
    if not tratti:
        raise ValueError("nessun livello da concatenare")

    serie: dict[str, float] = {}
    for primo_anno, _codice, livelli in tratti:
        if not serie:
            fattore = 1.0
        else:
            precedente = str(int(primo_anno) - 1)
            if precedente not in serie:
                raise ValueError(
                    f"buco fra le basi: il {primo_anno} comincia un tratto ma il "
                    f"{precedente} non è in nessuno di quelli prima"
                )
            variazione = variazioni.get(primo_anno)
            if variazione is None:
                raise ValueError(
                    f"manca la variazione del {primo_anno}: senza, le due basi non "
                    "hanno nessun ponte e attaccarle è inventare un salto"
                )
            atteso = serie[precedente] * (1 + variazione / 100)
            fattore = atteso / livelli[primo_anno]
        for anno, livello in livelli.items():
            serie[anno] = livello * fattore

    if base not in serie:
        raise ValueError(f"l'anno base {base} non è nella serie")
    riferimento = serie[base]
    return {anno: livello / riferimento * 100 for anno, livello in serie.items()}


def righe(
    indici: dict[str, dict[str, float]],
    variazioni: dict[str, float],
    *,
    basi: dict[str, str],
    base: str,
) -> list[dict[str, str]]:
    """Le righe della tabella: la serie concatenata, il livello della fonte, la provenienza."""
    serie = concatena(indici, variazioni, base=base)
    base_per_anno = {
        anno: basi[codice] for codice, livelli in indici.items() for anno in livelli
    }
    livello_fonte = {anno: livello for livelli in indici.values() for anno, livello in livelli.items()}
    return [
        {
            "anno": anno,
            # tre decimali: l'indice è un rapporto, e con uno solo una variazione
            # dello 0,1 % ricalcolata dalla tabella non si ritrova più.
            "indice": fmt(serie[anno], 3),
            # il numero **come la fonte lo pubblica**, nella sua base e con il
            # suo unico decimale: senza, la concatenazione è un'affermazione da
            # credere sulla parola, e con si rifà aprendo il CSV.
            "indice_fonte": fmt(livello_fonte[anno], 1),
            "variazione_annua": fmt(variazioni[anno], 1) if anno in variazioni else "",
            "base_fonte": base_per_anno[anno],
            "stato": STATO_OSSERVATO if base_per_anno[anno] == base else STATO_CONCATENATO,
        }
        for anno in sorted(serie)
    ]


def leggi(record) -> tuple[dict[str, dict[str, float]], dict[str, float]]:
    """Livelli e variazioni dai record SDMX, separati per base.

    I valori arrivano nella forma `codice: etichetta` (`labels=both`): leggerli
    alla lettera non solleva niente, fa uscire una tabella vuota da un build che
    dice «ok».
    """
    indici: dict[str, dict[str, float]] = {}
    variazioni: dict[str, float] = {}
    for riga in record:
        valore = to_number(riga.get("OBS_VALUE"))
        anno = (riga.get("TIME_PERIOD") or "").strip()
        if valore is None or not anno:
            continue
        tipo, _ = split_code(riga.get("DATA_TYPE", ""))
        misura, _ = split_code(riga.get("MEASURE", ""))
        if misura == MISURA_INDICE:
            if tipo not in BASI:
                raise ValueError(
                    f"base sconosciuta nella fonte: DATA_TYPE={tipo!r}. "
                    "Aggiungerla a BASI, o gli anni nuovi spariscono in silenzio."
                )
            indici.setdefault(tipo, {})[anno] = valore
        elif misura == MISURA_VARIAZIONE:
            variazioni[anno] = valore
    return indici, variazioni


def build(comuni: dict[str, str]) -> None:
    del comuni  # è l'indice nazionale: i comuni non c'entrano

    chiave = sdmx.key(
        DATAFLOW,
        {"FREQ": "A", "REF_AREA": "IT", "ECOICOP_2": INDICE_GENERALE},
    )
    path = sdmx_csv(DATAFLOW, chiave, dest_name="istat_prezzi_nic.csv")
    indici, variazioni = leggi(read_sdmx(path))
    write_csv("indice_prezzi.csv", righe(indici, variazioni, basi=BASI, base=BASE_TABELLA), COLUMNS)
