"""Infortuni sul lavoro denunciati, per provincia e settore. Fonte: INAIL.

In una provincia manifatturiera è la misura che manca a tutto l'asse «lavoro e
struttura produttiva»: il registro delle imprese dice quanti addetti ci sono,
l'INPS quanto vengono pagati, questa dice **cosa gli succede**.

## Sono microdati, e questo cambia due cose

L'API INAIL non pubblica aggregati: pubblica **una riga per caso denunciato**,
con età, sesso, data di accadimento, data di morte, settore del datore di
lavoro e un identificativo dell'infortunato. È un archivio pseudonimizzato, ma
resta a grana individuale.

Il sito di questo progetto dichiara, fra i limiti, che «tutte le fonti sono
aggregate». Perché quella frase resti vera, questo modulo **aggrega prima di
scrivere** e non versiona nessun record individuale: in `dati/processed/`
finiscono conteggi per provincia, anno e sezione Ateco, e i microdati restano
in `dati/raw/`, che non è versionata. Non è una precauzione formale: pubblicare
in un repository l'incrocio età × sesso × giorno × comune di un infortunio è un
modo di rendere identificabile qualcuno senza volerlo.

## Le trappole della fonte

**1. `MeseAccadimento` vuole lo zero iniziale.** Con `6` la risposta è
`{"error": "Dati non trovati"}`, con `06` arrivano i dati. È un errore
silenzioso che assomiglia a una copertura mancante, ed è costato mezz'ora di
diagnosi sbagliata: sembrava che esistessero solo ottobre, novembre e dicembre,
perché sono gli unici mesi già a due cifre.

**2. La chiave territoriale è già quella giusta.** `LuogoAccadimento` è il
codice provincia a **tre cifre** (`017` per Brescia), cioè la stessa chiave con
cui il progetto scrive le province. Nessun crosswalk da inventare.

**3. La finestra è mobile: cinque anni.** Al 7 settembre 2026 rispondono il
2020, 2021, 2022, 2023 e 2024; il 2019 non più e il 2025 non ancora. Gli anni
si chiedono uno per uno e il modulo **tiene quelli che rispondono**, invece di
fermarsi al primo che manca: una finestra che scorre non è un guasto.

**4. Il perimetro è la Lombardia, non l'Italia.** L'API filtra per regione e
restituisce microdati: le 107 province vorrebbero venti regioni per sessanta
mesi, cioè qualche gigabyte per un confronto che nessuna storia chiede ancora.
Qui il confronto è con le **altre undici province lombarde**, ed è dichiarato.
Allargarlo è aggiungere nomi a `REGIONI`.

⚠️ **Un infortunio denunciato non è un infortunio riconosciuto.** La fonte
pubblica le denunce; `DefinizioneAmministrativa` dice come sono state definite,
e i casi «negativi» restano nel conteggio dei denunciati. Il tasso rispetto agli
addetti, poi, non è calcolato qui: mescolare un conteggio INAIL con un
denominatore ASIA è una scelta da fare in `analysis/`, dichiarandola.
"""

from __future__ import annotations

import json
from collections import defaultdict

import requests

from ..config import RAW_DIR
from ..fetch import DEFAULT_TIMEOUT
from ..tidy import write_csv

API = "https://dati.inail.it/api/OpenData/DatiConCadenzaSemestraleInfortuni"

COLUMNS = ["codice_provincia", "provincia", "anno", "sezione_ateco", "indicatore", "valore"]

# Le regioni da scaricare, col nome che l'API vuole. Vedi il punto 4.
REGIONI = ["Lombardia"]

# Gli anni da provare. Quelli che non rispondono si saltano: la finestra della
# fonte scorre, e un anno che esce non è un errore della pipeline.
ANNI = [str(a) for a in range(2019, 2027)]

MESI = [f"{m:02d}" for m in range(1, 13)]

CHIAVE = "DatiConCadenzaSemestraleInfortuni"

# Il messaggio con cui la fonte dice «questo mese non c'e'», e lo dice con un
# 500. Vedi il docstring di `scarica`.
NON_TROVATI = "Dati non trovati"


def _sezione(settore: str | None) -> str:
    """`'F 43390'` -> `'F'`: la sezione Ateco, che è la grana di `sezioni.py`.

    La divisione a cinque cifre c'è, ma incrociarla con il registro delle
    imprese vorrebbe dire un crosswalk fra due vintage Ateco. La sezione no: è
    una lettera, e le lettere non sono cambiate.
    """
    testo = (settore or "").strip()
    if not testo or testo.upper() in {"ND", "NON DETERMINATO"}:
        return "non determinato"
    lettera = testo[0].upper()
    return lettera if lettera.isalpha() else "non determinato"


def scarica(regione: str, anno: str, mese: str) -> list[dict]:
    """I casi di un mese. Una lista vuota se la fonte non copre quel mese.

    ⚠️ `mese` deve arrivare **già a due cifre**: vedi il punto 1 del docstring.

    ⚠️ **E questa funzione non passa da `fetch()`, per una ragione che è costata
    un build buttato.** Un mese che la fonte non copre non risponde `200` con
    una lista vuota: risponde **`500` con `{"error": "Dati non trovati"}`**. Per
    `fetch()` un 500 è un guasto di rete, quindi ritenta cinque volte con attese
    di 15, 30, 60 e 120 secondi: **quattro minuti per ogni mese che non
    esiste**, e alla fine solleva invece di restituire vuoto. Con otto anni
    provati per dodici mesi, la sola parte inesistente della finestra costava
    più di un'ora di attese.

    Qui il 500 con quel messaggio è **una risposta**, non un guasto: si legge e
    si va avanti. La cache su disco resta, perché è il patto del progetto, ma la
    scrive questo modulo.
    """
    if len(mese) != 2:
        raise ValueError(f"il mese va passato a due cifre, non {mese!r}")

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    dest = RAW_DIR / f"inail_infortuni_{regione.lower()}_{anno}_{mese}.json"
    if dest.exists() and dest.stat().st_size > 0:
        return _casi(dest.read_bytes())

    risposta = requests.get(
        API,
        params={"Regione": regione, "AnnoAccadimento": anno, "MeseAccadimento": mese},
        timeout=DEFAULT_TIMEOUT,
    )
    if risposta.status_code >= 500 and NON_TROVATI in risposta.text:
        return []
    risposta.raise_for_status()
    dest.write_bytes(risposta.content)
    return _casi(risposta.content)


def _casi(grezzo: bytes) -> list[dict]:
    dati = json.loads(grezzo)
    if not isinstance(dati, dict) or dati.get("error"):
        return []
    return dati.get(CHIAVE, [])


def aggrega(casi: list[dict], anno: str) -> dict[tuple[str, str, str], int]:
    """Da microdati a conteggi: `(provincia, sezione, indicatore) -> casi`.

    Due indicatori: le denunce e, fra queste, quelle con esito mortale. Il
    secondo è un **sottoinsieme** del primo, non una colonna a parte da
    sommare.
    """
    totali: dict[tuple[str, str, str], int] = defaultdict(int)
    for caso in casi:
        provincia = (caso.get("LuogoAccadimento") or "").strip()
        if len(provincia) != 3 or not provincia.isdigit():
            continue  # casi senza luogo: la fonte li marca, non li inventiamo
        sezione = _sezione(caso.get("SettoreAttivitaEconomica"))
        totali[(provincia, sezione, "denunce")] += 1
        totali[(provincia, "totale", "denunce")] += 1
        morte = (caso.get("DataMorte") or "").strip()
        if morte and morte.lower() != "none":
            totali[(provincia, sezione, "casi_mortali")] += 1
            totali[(provincia, "totale", "casi_mortali")] += 1
    del anno
    return totali


def build(comuni: dict[str, str]) -> None:
    del comuni  # tabella provinciale

    from .province import province_italiane

    nomi = {codice: nome for codice, (nome, _) in province_italiane().items()}
    per_anno: dict[str, dict[tuple[str, str, str], int]] = defaultdict(lambda: defaultdict(int))
    coperti: list[str] = []

    for regione in REGIONI:
        for anno in ANNI:
            trovati = 0
            for mese in MESI:
                casi = scarica(regione, anno, mese)
                trovati += len(casi)
                for chiave, quanti in aggrega(casi, anno).items():
                    per_anno[anno][chiave] += quanti
            if trovati:
                coperti.append(anno)

    if not per_anno:
        raise RuntimeError(
            "nessun infortunio da nessun anno: l'API INAIL ha cambiato forma, "
            "oppure il mese non sta arrivando a due cifre (vedi il docstring)"
        )
    print(f"  anni coperti dalla fonte: {', '.join(sorted(set(coperti)))}")

    righe = [
        {
            "codice_provincia": provincia,
            "provincia": nomi.get(provincia, ""),
            "anno": anno,
            "sezione_ateco": sezione,
            "indicatore": indicatore,
            "valore": str(valore),
        }
        for anno, totali in per_anno.items()
        for (provincia, sezione, indicatore), valore in totali.items()
    ]
    righe.sort(key=lambda r: (r["codice_provincia"], r["anno"], r["sezione_ateco"],
                              r["indicatore"]))
    write_csv("infortuni_province.csv", righe, COLUMNS)
