"""Ricalcola dai CSV ogni cifra citata nei documenti del progetto.

    python analysis/verifica_cifre.py           # elenco delle verifiche
    python analysis/verifica_cifre.py --csv     # scrive analysis/output/verifica_cifre.csv

Il principio è in `BRIEF.md` («ogni numero citato ha uno script o una metrica
dietro») e in `PROSSIMI-PASSI.md` §5.4. Finché i numeri stavano solo nei testi
non erano verificabili, e infatti due erano sbagliati: la mediana della
popolazione comunale (2.000 invece di 3.671) e la crescita degli addetti nella
fascia 10–249 (13 mila invece di 23.840). Sono stati corretti nei documenti ad
agosto 2026 grazie a questo script, che da qui in avanti li tiene onesti.

Solo libreria standard: le tabelle sono piccole e la pipeline non ha pandas.
Ogni verifica dichiara il documento e la cifra attesa; l'uscita è 1 se anche
una sola diverge oltre la tolleranza, così lo script può stare in CI.
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
PROCESSED = RADICE / "dati" / "processed"
OUTPUT = Path(__file__).resolve().parent / "output"

CAPOLUOGO = "017029"
IMPONIBILE = "AGGINCR"  # codice MEF, non etichetta: le etichette cambiano lingua


def leggi(nome: str) -> list[dict[str, str]]:
    with (PROCESSED / nome).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def numero(valore: str | None) -> float | None:
    """Le celle vuote sono dati mancanti, non zeri (MET-3)."""
    if valore is None or valore == "":
        return None
    return float(valore)


# --- le fonti dei numeri ------------------------------------------------

sintesi = leggi("comuni_sintesi.csv")
geometria = leggi("comuni_geometria.csv")
imprese = leggi("imprese_classe_addetti.csv")
turismo = leggi("turismo_comuni_annuale.csv")
aria = leggi("aria_mensile.csv")
stazioni = leggi("stazioni_arpa.csv")
meteo = leggi("meteo_mensile.csv")
popolazione = leggi("popolazione_comuni.csv")
redditi = leggi("redditi_comuni.csv")
settore_classe = leggi("imprese_settore_classe.csv")
sezioni = leggi("imprese_sezioni_comuni.csv")
province = leggi("imprese_province.csv")
capoluoghi = leggi("imprese_capoluoghi.csv")
turismo_province = leggi("turismo_province.csv")
bilancio_province = leggi("bilancio_province.csv")

PROVINCIA = "ITC47"


def addetti(anno: str, classe: str, indicatore: str = "addetti", comune: str | None = None) -> float:
    totale = 0.0
    for riga in imprese:
        if riga["anno"] != anno or riga["classe_addetti"] != classe:
            continue
        if riga["indicatore"] != indicatore:
            continue
        if comune is not None and riga["codice_istat"] != comune:
            continue
        valore = numero(riga["valore"])
        if valore is not None:
            totale += valore
    return totale


def presenze_2024() -> dict[str, float]:
    """Presenze per comune, 2024, con il doppio filtro Totale/Totale.

    Senza quel filtro le stesse notti si contano fino a tre volte
    (`dati/README.md`); le righe `zero_fittizio` restano fuori, perché quello
    zero è calcolato su celle soppresse, non misurato.
    """
    per_comune: dict[str, float] = {}
    for riga in turismo:
        if riga["anno"] != "2024" or riga["stato"] != "osservato":
            continue
        if riga["tipo_struttura"] != "Totale" or riga["cittadinanza"] != "Totale":
            continue
        valore = numero(riga["presenze"])
        if valore is not None:
            per_comune[riga["codice_istat"]] = valore
    return per_comune


def media_pm10_broletto(anno: str) -> float:
    """Media delle medie mensili PM10 alla stazione Brescia v.Broletto.

    ⚠️ È una media di medie mensili non pesata sui giorni: nel 2001 i mesi
    disponibili sono 11 su 12. Serve a riprodurre la cifra citata, non come
    media annua ufficiale.
    """
    sensori = {
        r["id_sensore"]
        for r in stazioni
        if "Broletto" in r["stazione"] and r["parametro"].startswith("PM10")
    }
    medie = [
        numero(r["media"])
        for r in aria
        if r["id_sensore"] in sensori and r["mese"].startswith(anno) and r["media"]
    ]
    valide = [m for m in medie if m is not None]
    return sum(valide) / len(valide)


def serie_popolazione() -> dict[str, dict[str, float]]:
    per_comune: dict[str, dict[str, float]] = defaultdict(dict)
    for riga in popolazione:
        if riga["indicatore"] != "popolazione_residente":
            continue
        valore = numero(riga["valore"])
        if valore is not None:
            per_comune[riga["codice_istat"]][riga["anno"]] = valore
    return per_comune


def tasso(iniziale: float, finale: float, anni: int) -> float:
    return ((finale / iniziale) ** (1 / anni) - 1) * 100


def comuni_in_calo() -> int:
    quanti = 0
    for serie in serie_popolazione().values():
        anni = sorted(serie)
        quanti += serie[anni[-1]] < serie[anni[0]]
    return quanti


def reddito_medio(anno: str) -> dict[str, float]:
    """Somma degli imponibili diviso somma dei contribuenti, per comune."""
    imponibile: dict[str, float] = defaultdict(float)
    contribuenti: dict[str, float] = defaultdict(float)
    for riga in redditi:
        if riga["anno"] != anno:
            continue
        valore = numero(riga["valore"])
        if valore is None:
            continue
        deposito = imponibile if riga["codice_indicatore"] == IMPONIBILE else contribuenti
        deposito[riga["codice_istat"]] += valore
    return {c: imponibile[c] / contribuenti[c] for c in imponibile if contribuenti.get(c)}


def correlazione(x: list[float], y: list[float]) -> float:
    mx, my = sum(x) / len(x), sum(y) / len(y)
    num = sum((a - mx) * (b - my) for a, b in zip(x, y))
    dx = (sum((a - mx) ** 2 for a in x)) ** 0.5
    dy = (sum((b - my) ** 2 for b in y)) ** 0.5
    return num / (dx * dy)


def convergenza_reddito(iniziale: str = "2012", finale: str = "2023") -> float:
    """Pearson fra reddito di partenza e crescita annua, tutti i comuni."""
    primo, ultimo = reddito_medio(iniziale), reddito_medio(finale)
    codici = sorted(set(primo) & set(ultimo))
    anni = int(finale) - int(iniziale)
    return correlazione(
        [primo[c] for c in codici],
        [tasso(primo[c], ultimo[c], anni) for c in codici],
    )


def artefatto_reddito(iniziale: str = "2012", finale: str = "2023") -> float:
    """Lo stesso calcolo con il livello finale: è l'artefatto, e cambia segno."""
    primo, ultimo = reddito_medio(iniziale), reddito_medio(finale)
    codici = sorted(set(primo) & set(ultimo))
    anni = int(finale) - int(iniziale)
    return correlazione(
        [ultimo[c] for c in codici],
        [tasso(primo[c], ultimo[c], anni) for c in codici],
    )


def addetti_settore_classe(territorio: str, ateco: str, classe: str, anno: str) -> float:
    for riga in settore_classe:
        if (riga["territorio"], riga["ateco"], riga["classe_addetti"], riga["anno"]) == (
            territorio, ateco, classe, anno
        ) and riga["indicatore"] == "addetti":
            return numero(riga["valore"]) or 0.0
    return 0.0  # una classe che sparisce non ha righe: sono zero addetti in quella classe


def unita_settore_classe(territorio: str, ateco: str, classe: str, anno: str) -> float:
    for riga in settore_classe:
        if (riga["territorio"], riga["ateco"], riga["classe_addetti"], riga["anno"]) == (
            territorio, ateco, classe, anno
        ) and riga["indicatore"] == "unita_locali":
            return numero(riga["valore"]) or 0.0
    return 0.0


def manifattura_grande_capoluogo(anno: str) -> float:
    divisioni = {f"{n:02d}" for n in range(10, 34)}
    return sum(
        numero(riga["valore"]) or 0.0
        for riga in settore_classe
        if riga["territorio"] == CAPOLUOGO
        and riga["anno"] == anno
        and riga["classe_addetti"] == "250+"
        and riga["indicatore"] == "addetti"
        and riga["ateco"] in divisioni
    )


def quote_sezioni(anno: str) -> dict[str, dict[str, float]]:
    """Quota di addetti per sezione Ateco, comune per comune.

    Denominatore: il **totale ASIA riportato**, non la somma delle sezioni. Una
    sezione assente **non** diventa zero: resta fuori, e chi la usa deve dirlo.
    È la stessa definizione di `_tabelle.quote_sezioni()` — riscritta qui per
    conto suo, perché un verificatore che importa il codice che verifica non
    verifica niente. Se le due divergono, una delle due è sbagliata, ed è
    esattamente quello che questo script serve a scoprire.
    """
    per_comune: dict[str, dict[str, float]] = defaultdict(dict)
    for riga in sezioni:
        if riga["anno"] != anno or riga["indicatore"] != "addetti":
            continue
        valore = numero(riga["valore"])
        if valore is not None:
            per_comune[riga["codice_istat"]][riga["sezione"]] = valore

    totali = {
        riga["codice_istat"]: numero(riga["valore"])
        for riga in imprese
        if riga["anno"] == anno
        and riga["indicatore"] == "addetti"
        and riga["classe_addetti"] == "totale"
    }
    return {
        codice: {s: v / totali[codice] * 100 for s, v in sezioni_comune.items()}
        for codice, sezioni_comune in per_comune.items()
        if totali.get(codice)
    }


def scarto_stagionale_turismo(anno: str, base: str = "2019") -> float:
    """Presenze dell'anno contro i mesi omologhi del `base`, in percentuale."""
    per_mese: dict[str, float] = defaultdict(float)
    for riga in leggi("turismo_comuni_mensile.csv"):
        valore = numero(riga["presenze"])
        if valore is not None:
            per_mese[riga["mese"]] += valore
    osservato = sum(v for m, v in per_mese.items() if m[:4] == anno)
    mesi = {m[5:7] for m in per_mese if m[:4] == anno}
    atteso = sum(v for m, v in per_mese.items() if m[:4] == base and m[5:7] in mesi)
    return (osservato / atteso - 1) * 100


def per_provincia(anno: str, dimensione: str, modalita: str, indicatore: str) -> dict[str, float]:
    fuori: dict[str, float] = {}
    for riga in province:
        if (riga["anno"], riga["dimensione"], riga["modalita"], riga["indicatore"]) == (
            anno, dimensione, modalita, indicatore
        ):
            valore = numero(riga["valore"])
            if valore is not None:
                fuori[riga["codice_provincia"]] = valore
    return fuori


def quota_provinciale(
    anno: str, dimensione: str, parte: str, indicatore: str,
    dimensione_totale: str = "classe_addetti", tutto: str = "totale",
) -> dict[str, float]:
    """Quota sul totale provinciale. Il denominatore sta sempre fra le classi
    dimensionali, anche quando il numeratore è una sezione Ateco: il «totale»
    della dimensione settoriale non esiste in questa tabella."""
    sopra = per_provincia(anno, dimensione, parte, indicatore)
    sotto = per_provincia(anno, dimensione_totale, tutto, indicatore)
    return {c: sopra[c] / sotto[c] * 100 for c in sopra if sotto.get(c)}


def mediana_lista(valori: list[float]) -> float:
    ordinati = sorted(valori)
    meta = len(ordinati) // 2
    return ordinati[meta] if len(ordinati) % 2 else (ordinati[meta - 1] + ordinati[meta]) / 2


def rango_brescia(valori: dict[str, float]) -> int:
    ordinati = sorted(valori.items(), key=lambda kv: -kv[1])
    return [c for c, _ in ordinati].index("017") + 1


def variazioni_capoluoghi() -> list[float]:
    grandi: dict[str, dict[str, float]] = defaultdict(dict)
    for riga in capoluoghi:
        if riga["indicatore"] == "addetti" and riga["classe_addetti"] == "250+":
            valore = numero(riga["valore"])
            if valore is not None:
                grandi[riga["codice_istat"]][riga["anno"]] = valore
    fuori = []
    for serie in grandi.values():
        anni = sorted(serie)
        if serie[anni[0]] >= 2000:
            fuori.append((serie[anni[-1]] / serie[anni[0]] - 1) * 100)
    return sorted(fuori)


def decili(valori: dict[str, float]) -> float:
    """p90/p10: la dispersione senza farla decidere a due comuni su duecento."""
    ordinati = sorted(valori.values())
    return ordinati[int(len(ordinati) * 0.9)] / ordinati[int(len(ordinati) * 0.1)]


def convergenza_bergamo() -> float:
    """Lo stesso conto della convergenza, sui comuni della provincia di Bergamo."""
    righe = leggi("redditi_comuni_confronto.csv")
    imponibile: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    contribuenti: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for riga in righe:
        valore = numero(riga["valore"])
        if valore is None:
            continue
        deposito = imponibile if riga["codice_indicatore"] == IMPONIBILE else contribuenti
        deposito[riga["codice_istat"]][riga["anno"]] += valore
    medi: dict[str, dict[str, float]] = {}
    for codice, per_anno in imponibile.items():
        for anno, totale in per_anno.items():
            teste = contribuenti[codice].get(anno)
            if teste:
                medi.setdefault(codice, {})[anno] = totale / teste
    codici = [c for c in medi if "2012" in medi[c] and "2023" in medi[c]]
    return correlazione(
        [medi[c]["2012"] for c in codici],
        [tasso(medi[c]["2012"], medi[c]["2023"], 11) for c in codici],
    )


def vicini() -> dict[str, set[str]]:
    """Contiguità per vertice condiviso, riletta dal GeoJSON."""
    geo = json.loads((RADICE / "dati" / "geo" / "comuni_brescia.geojson").read_text(encoding="utf-8"))
    per_vertice: dict[tuple[float, float], set[str]] = defaultdict(set)
    for feature in geo["features"]:
        codice = feature["properties"]["codice_istat"]
        for anello in feature["geometry"]["coordinates"]:
            for x, y in anello:
                per_vertice[(round(x, 5), round(y, 5))].add(codice)
    adiacenze: dict[str, set[str]] = {f["properties"]["codice_istat"]: set() for f in geo["features"]}
    for condivisori in per_vertice.values():
        if len(condivisori) > 1:
            for uno in condivisori:
                adiacenze[uno] |= condivisori - {uno}
    return adiacenze


def moran(valori: dict[str, float]) -> float:
    adiacenze = vicini()
    codici = [c for c in valori if adiacenze.get(c)]
    centro = sum(valori[c] for c in codici) / len(codici)
    z = {c: valori[c] - centro for c in codici}
    numeratore = 0.0
    for codice in codici:
        presenti = [z[v] for v in adiacenze[codice] if v in z]
        if presenti:
            numeratore += z[codice] * (sum(presenti) / len(presenti))
    return numeratore / sum(v**2 for v in z.values())


def moran_crescita_popolazione() -> float:
    serie = serie_popolazione()
    return moran({
        codice: tasso(valori[min(valori)], valori[max(valori)], int(max(valori)) - int(min(valori)))
        for codice, valori in serie.items()
    })


def moran_specializzazione(anno: str = "2023") -> float:
    """Solo i comuni che hanno **entrambe** le sezioni: un'assenza non è uno zero."""
    quote = quote_sezioni(anno)
    return moran({
        codice: sezioni_comune["C"] - sezioni_comune["I"]
        for codice, sezioni_comune in quote.items()
        if "C" in sezioni_comune and "I" in sezioni_comune
    })



# --- il turismo confrontato con le altre province ------------------------

BRESCIA_PROV = "017"


def _turismo(livello: str = "provincia", solo_osservato: bool = True) -> dict:
    """`(territorio, anno, tipologia, residenza, indicatore) -> valore`.

    La chiave del livello provinciale è il codice provincia, quella dell'Italia
    è `IT`: due spazi di nomi diversi, e mescolarli darebbe una collisione.
    """
    fuori: dict[tuple[str, str, str, str, str], float] = {}
    for riga in turismo_province:
        if riga["livello"] != livello:
            continue
        if solo_osservato and riga["stato"] != "osservato":
            continue
        valore = numero(riga["valore"])
        if valore is None:
            continue
        chiave = riga["codice_provincia"] if livello == "provincia" else riga["codice_nuts3"]
        fuori[(chiave, riga["anno"], riga["tipologia"], riga["residenza"], riga["indicatore"])] = valore
    return fuori


def _per_provincia_turismo(calcola, anno: str = "2024") -> dict[str, float]:
    dati = _turismo()
    province_turismo = {k[0] for k in dati}
    fuori: dict[str, float] = {}
    for codice in province_turismo:
        valore = calcola(dati, codice, anno)
        if valore is not None:
            fuori[codice] = valore
    return fuori


def _presenze(dati: dict, codice: str, anno: str, tipologia: str = "totale", residenza: str = "totale"):
    return dati.get((codice, anno, tipologia, residenza, "presenze"))


def _popolazione_provinciale(anno: str = "2024") -> dict[str, float]:
    return {
        riga["codice_provincia"]: float(riga["valore"])
        for riga in bilancio_province
        if riga["indicatore"] == "popolazione_censita" and riga["anno"] == anno
    }


def turismo_valore(nome: str, anno: str = "2024") -> float:
    return _per_provincia_turismo(_MISURE[nome], anno)[BRESCIA_PROV]


def turismo_mediana(nome: str, anno: str = "2024") -> float:
    return mediana_lista(list(_per_provincia_turismo(_MISURE[nome], anno).values()))


def turismo_rango(nome: str, anno: str = "2024", alto_e_primo: bool = True) -> int:
    valori = _per_provincia_turismo(_MISURE[nome], anno)
    ordinate = sorted(valori, key=lambda c: valori[c], reverse=alto_e_primo)
    return ordinate.index(BRESCIA_PROV) + 1


def turismo_quante(nome: str, anno: str = "2024") -> int:
    return len(_per_provincia_turismo(_MISURE[nome], anno))


def _quota(tipologia: str):
    def calcola(dati, codice, anno):
        parte = _presenze(dati, codice, anno, tipologia=tipologia)
        totale = _presenze(dati, codice, anno)
        return None if parte is None or not totale else parte / totale * 100
    return calcola


def _quota_estera(dati, codice, anno):
    estero = _presenze(dati, codice, anno, residenza="estero")
    totale = _presenze(dati, codice, anno)
    return None if estero is None or not totale else estero / totale * 100


def _per_abitante(dati, codice, anno):
    abitanti = _popolazione_provinciale(anno).get(codice)
    totale = _presenze(dati, codice, anno)
    return None if not abitanti or totale is None else totale / abitanti


def _crescita_dal_2019(dati, codice, anno):
    prima = _presenze(dati, codice, "2019")
    dopo = _presenze(dati, codice, anno)
    return None if not prima or dopo is None else (dopo / prima - 1) * 100


def _caduta_2020(dati, codice, anno):
    del anno
    prima = _presenze(dati, codice, "2019")
    durante = _presenze(dati, codice, "2020")
    return None if not prima or durante is None else (durante / prima - 1) * 100


_MISURE = {
    "presenze": lambda d, c, a: _presenze(d, c, a),
    "per_abitante": _per_abitante,
    "quota_estera": _quota_estera,
    "quota_alberghiera": _quota("alberghiero"),
    "quota_campeggi": _quota("campeggi e villaggi"),
    "crescita_2019": _crescita_dal_2019,
    "caduta_2020": _caduta_2020,
}


def turismo_di(nome_provincia: str, misura: str, anno: str = "2024") -> float:
    """La stessa misura su un'altra provincia: la §7.8 ne cita quattro."""
    codice = next(
        r["codice_provincia"]
        for r in turismo_province
        if r["territorio"] == nome_provincia and r["livello"] == "provincia"
    )
    return _per_provincia_turismo(_MISURE[misura], anno)[codice]


def turismo_piu_internazionali() -> int:
    """Quante province hanno una quota straniera piu' alta di Brescia."""
    quote = _per_provincia_turismo(_MISURE["quota_estera"])
    return sum(1 for v in quote.values() if v > quote[BRESCIA_PROV])


def turismo_sopra_il_2019() -> int:
    quote = _per_provincia_turismo(_MISURE["crescita_2019"])
    return sum(1 for v in quote.values() if v > 0)


def turismo_quota_estera(anno: str) -> float:
    dati = _turismo()
    estero = dati[(BRESCIA_PROV, anno, "totale", "estero", "presenze")]
    totale = dati[(BRESCIA_PROV, anno, "totale", "totale", "presenze")]
    return estero / totale * 100


def turismo_crescita_lunga(codice: str = BRESCIA_PROV) -> float:
    """Tasso composto 2008–2024 delle presenze, in percentuale l'anno."""
    dati = _turismo()
    prima, dopo = _presenze(dati, codice, "2008"), _presenze(dati, codice, "2024")
    return tasso(prima, dopo, 16)


def _crescite_lunghe() -> dict[str, float]:
    """Solo le province con la serie intera e il territorio invariato."""
    dati = _turismo()
    sarde = {
        riga["codice_provincia"]
        for riga in turismo_province
        if riga["regione"] == "Sardegna" and riga["livello"] == "provincia"
    }
    fuori: dict[str, float] = {}
    for codice in {k[0] for k in dati} - sarde:
        prima, dopo = _presenze(dati, codice, "2008"), _presenze(dati, codice, "2024")
        if prima and dopo:
            fuori[codice] = tasso(prima, dopo, 16)
    return fuori


def scarto_fonti_turismo(anno: str, colonna: str = "presenze") -> float:
    """Quanto la somma dei comuni di Regione Lombardia sta sopra ISTAT, in %."""
    somma = sum(
        numero(r[colonna]) or 0.0
        for r in turismo
        if r["anno"] == anno
        and r["tipo_struttura"] == "Totale"
        and r["cittadinanza"] == "Totale"
        and r["stato"] == "osservato"
    )
    indicatore = "presenze" if colonna == "presenze" else "arrivi"
    provinciale = _turismo()[(BRESCIA_PROV, anno, "totale", "totale", indicatore)]
    return (somma / provinciale - 1) * 100


def scalino_2025(tipologia: str = "alloggi in affitto") -> float:
    """La crescita apparente fra 2024 e 2025 sull'Italia: è una definizione."""
    dati = _turismo(livello="italia", solo_osservato=False)
    prima = dati[("IT", "2024", tipologia, "totale", "presenze")]
    dopo = dati[("IT", "2025", tipologia, "totale", "presenze")]
    return (dopo / prima - 1) * 100


# --- le verifiche -------------------------------------------------------
# (documento, cifra citata, valore atteso, funzione, tolleranza)

# --- il bilancio demografico --------------------------------------------

bilancio = leggi("bilancio_demografico_comuni.csv")
bilancio_province = leggi("bilancio_province.csv")

# Le componenti si ricalcolano qui dai flussi lordi, non si leggono dalle
# colonne dei saldi: la tabella non le porta apposta (vedi `datasets/bilancio`),
# e un verificatore che rileggesse un totale già calcolato non verificherebbe
# niente.
COMPONENTI_BILANCIO = {
    "naturale": ("nati", "morti"),
    "interna": ("immigrati_interni", "emigrati_interni"),
    "estera": ("immigrati_estero", "emigrati_estero"),
}


def _somma_bilancio(righe: list[dict[str, str]], chiave: str) -> dict[str, dict[str, float]]:
    fuori: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for riga in righe:
        valore = numero(riga["valore"])
        if valore is not None:
            fuori[riga[chiave]][riga["indicatore"]] += valore
    return fuori


def componenti(conti: dict[str, float]) -> dict[str, float]:
    fuori = {
        nome: conti.get(piu, 0.0) - conti.get(meno, 0.0)
        for nome, (piu, meno) in COMPONENTI_BILANCIO.items()
    }
    fuori["aggiustamento"] = conti.get("aggiustamento_statistico", 0.0)
    fuori["territorio"] = conti.get("variazioni_territoriali", 0.0)
    fuori["totale"] = sum(fuori.values())
    return fuori


def bilancio_comuni() -> dict[str, dict[str, float]]:
    return {c: componenti(v) for c, v in _somma_bilancio(bilancio, "codice_istat").items()}


def componente_provinciale(nome: str) -> float:
    return sum(v[nome] for v in bilancio_comuni().values())


def in_calo_componente(nome: str) -> float:
    """La componente sommata sui soli comuni che perdono abitanti."""
    return sum(v[nome] for v in bilancio_comuni().values() if v["totale"] < 0)


def comuni_con_naturale_negativo() -> int:
    return sum(1 for v in bilancio_comuni().values() if v["naturale"] < 0)


def comuni_per_componente_piu_negativa(nome: str) -> int:
    """Fra i comuni in calo, quanti hanno `nome` come componente più negativa."""
    quanti = 0
    for valori in bilancio_comuni().values():
        if valori["totale"] >= 0:
            continue
        if min(("naturale", "interna", "estera"), key=lambda k: valori[k]) == nome:
            quanti += 1
    return quanti


def _province_per_mille() -> dict[str, dict[str, float]]:
    per_provincia = _somma_bilancio(bilancio_province, "codice_provincia")
    primo = min(r["anno"] for r in bilancio_province)
    base = {
        r["codice_provincia"]: float(r["valore"])
        for r in bilancio_province
        if r["indicatore"] == "popolazione_inizio" and r["anno"] == primo
    }
    return {
        codice: {n: v / base[codice] * 1000 for n, v in componenti(conti).items()}
        for codice, conti in per_provincia.items()
        if base.get(codice)
    }


def rango_provincia(nome: str) -> int:
    valori = _province_per_mille()
    ordinati = sorted(valori.items(), key=lambda kv: -kv[1][nome])
    return [c for c, _ in ordinati].index("017") + 1


def mediana_province(nome: str) -> float:
    return mediana_lista([v[nome] for v in _province_per_mille().values()])


def brescia_per_mille(nome: str) -> float:
    return _province_per_mille()["017"][nome]


def province_con(nome: str, positivo: bool = True) -> int:
    valori = _province_per_mille()
    return sum(1 for v in valori.values() if (v[nome] > 0) == positivo)



def _comuni_con_centralina() -> dict[str, set[str]]:
    """Comune -> stazioni di qualità dell'aria che compaiono davvero nella serie.

    Sull'**intera** serie, non sulle sole stazioni attive oggi: sono due
    domande diverse, e `BRIEF.md` risponde alla seconda (sette comuni). Il
    filtro su `aria_mensile.csv` serve perché `stazioni_arpa.csv` elenca anche
    sensori di grandezze che il progetto non scarica.
    """
    con_dati = {r["id_sensore"] for r in aria}
    fuori: dict[str, set[str]] = defaultdict(set)
    for riga in stazioni:
        if riga["id_sensore"] in con_dati and riga["comune"]:
            fuori[riga["comune"]].add(riga["stazione"])
    return fuori


# --- l'aria e il clima (la sesta storia) ---------------------------------
#
# Rifatte da capo, come tutto il resto di questo file: `analysis/aria_e_clima.py`
# e `sito/costruisci.py` calcolano le stesse cifre ciascuno per conto suo, e se
# le tre implementazioni divergessero sulla definizione di «panel bilanciato» o
# di «anomalia» è qui che si vedrebbe. È il meccanismo che ha fatto emergere
# MET-13 sull'indice di Moran.

BASE_CLIMA = [str(a) for a in range(2004, 2014)]
RECENTE_CLIMA = [str(a) for a in range(2016, 2026)]


def _annue(righe: list[dict[str, str]], parametro: str, colonna: str, minimo: int) -> dict[str, dict[str, float]]:
    grezzo: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for riga in righe:
        if riga["parametro"] != parametro or riga["stato"] != "osservato":
            continue
        valore = numero(riga[colonna])
        if valore is not None:
            grezzo[riga["id_sensore"]][riga["mese"][:4]].append(valore)
    return {
        sensore: {anno: mesi for anno, mesi in per_anno.items() if len(mesi) >= minimo}
        for sensore, per_anno in grezzo.items()
    }


def variazione_inquinante(parametro: str) -> float:
    """Variazione percentuale fra i primi e gli ultimi tre anni del panel bilanciato."""
    serie = {
        s: {a: sum(m) / len(m) for a, m in per_anno.items()}
        for s, per_anno in _annue(aria, parametro, "media", 10).items()
    }
    tutti = [a for per_anno in serie.values() for a in per_anno]
    primo, ultimo = int(min(tutti)), int(max(tutti))
    for inizio in range(primo, ultimo + 1):
        anni = [str(a) for a in range(inizio, ultimo + 1)]
        if len(anni) < 6:
            break
        sensori = [s for s, per_anno in serie.items() if all(a in per_anno for a in anni)]
        if len(sensori) >= 3:
            testa = sum(serie[s][a] for s in sensori for a in anni[:3]) / (len(sensori) * 3)
            coda = sum(serie[s][a] for s in sensori for a in anni[-3:]) / (len(sensori) * 3)
            return (coda / testa - 1) * 100
    raise AssertionError(f"nessun panel bilanciato per {parametro}")


def variazione_ingenua(parametro: str) -> float:
    """Il conto che il panel bilanciato serve a evitare: tutte le stazioni
    disponibili nel primo anno contro tutte quelle disponibili nell'ultimo.

    Sta qui perché la §7.7 del working paper lo **riporta accanto** al panel: la
    distanza fra i due quantifica quanto ha contribuito il rimaneggiamento della
    rete, e su una serie ferma come l'ozono le rovescia il segno. Un numero
    citato per essere criticato resta un numero citato (MET-16).
    """
    serie = {
        s: {a: sum(m) / len(m) for a, m in per_anno.items()}
        for s, per_anno in _annue(aria, parametro, "media", 10).items()
    }
    tutti = [a for per_anno in serie.values() for a in per_anno]
    primo, ultimo = int(min(tutti)), int(max(tutti))
    for inizio in range(primo, ultimo + 1):
        anni = [str(a) for a in range(inizio, ultimo + 1)]
        if len(anni) < 6:
            break
        if len([s for s, per_anno in serie.items() if all(a in per_anno for a in anni)]) >= 3:
            testa = [per_anno[anni[0]] for per_anno in serie.values() if anni[0] in per_anno]
            coda = [per_anno[anni[-1]] for per_anno in serie.values() if anni[-1] in per_anno]
            return ((sum(coda) / len(coda)) / (sum(testa) / len(testa)) - 1) * 100
    raise AssertionError(f"nessun panel bilanciato per {parametro}")


def _due_finestre(parametro: str, somma: bool) -> list[tuple[float, float]]:
    """Le coppie (base, recente) delle stazioni che hanno entrambe le finestre.

    ⚠️ La soglia dei mesi dipende da cosa si aggrega, e sbagliarla cambia la
    risposta: una **media** annua tollera due mesi mancanti (10 su 12), un
    **totale** annuo no — un totale a cui manca un mese non è un totale basso,
    è un totale di undici mesi. Scritta a 12 anche per la temperatura, questa
    verifica trovava 7 stazioni invece di 8, ed è esattamente il genere di
    divergenza per cui questo file rifà i conti per conto proprio (MET-13).
    """
    coppie = []
    for per_anno in _annue(meteo, parametro, "valore", 12 if somma else 10).values():
        annuali = {a: (sum(m) if somma else sum(m) / len(m)) for a, m in per_anno.items()}
        base = [annuali[a] for a in BASE_CLIMA if a in annuali]
        recente = [annuali[a] for a in RECENTE_CLIMA if a in annuali]
        if len(base) >= 8 and len(recente) >= 8:
            coppie.append((sum(base) / len(base), sum(recente) / len(recente)))
    return coppie


def scarto_temperatura() -> float:
    coppie = _due_finestre("Temperatura", somma=False)
    return sum(r - b for b, r in coppie) / len(coppie)


def stazioni_piu_calde() -> int:
    return sum(1 for b, r in _due_finestre("Temperatura", somma=False) if r > b)


def stazioni_di_temperatura() -> int:
    return len(_due_finestre("Temperatura", somma=False))


def variazione_mediana_pioggia() -> float:
    variazioni = sorted((r / b - 1) * 100 for b, r in _due_finestre("Precipitazione", somma=True))
    return mediana_lista(variazioni)


VERIFICHE: list[tuple[str, str, float, object, float]] = [
    (
        "BRIEF §Unità di analisi",
        "205 comuni nella provincia",
        205,
        lambda: len(sintesi),
        0,
    ),
    (
        "dati/README §La geometria",
        "superficie provinciale 4.785,3 km²",
        4785.3,
        lambda: sum(float(r["area_kmq"]) for r in geometria),
        0.1,
    ),
    (
        "BRIEF §Unità di analisi / METODOLOGIA MET-2",
        "popolazione del capoluogo 2024: 199.853",
        199853,
        lambda: next(int(r["popolazione_2024"]) for r in sintesi if r["codice_istat"] == CAPOLUOGO),
        0,
    ),
    (
        "METODOLOGIA MET-2, MET-5",
        "mediana della popolazione comunale: 3.671",
        3671,
        lambda: statistics.median(int(r["popolazione_2024"]) for r in sintesi),
        0,
    ),
    (
        "METODOLOGIA MET-2",
        "il capoluogo è il 16 % della popolazione provinciale",
        15.8,
        lambda: next(int(r["popolazione_2024"]) for r in sintesi if r["codice_istat"] == CAPOLUOGO)
        / sum(int(r["popolazione_2024"]) for r in sintesi)
        * 100,
        0.1,
    ),
    (
        "FONTI §1-bis",
        "unità locali in provincia, 2023: 119.565",
        119565,
        lambda: addetti("2023", "totale", "unita_locali"),
        1,
    ),
    (
        "FONTI §1-bis / WORKING-PAPER §7",
        "addetti in provincia, 2023: 479.418",
        479418,
        lambda: addetti("2023", "totale"),
        1,
    ),
    (
        "BRIEF §Storie / WORKING-PAPER §7",
        "unità locali sotto i 10 addetti, 2023: 92,7 %",
        92.7,
        lambda: addetti("2023", "0-9", "unita_locali") / addetti("2023", "totale", "unita_locali") * 100,
        0.05,
    ),
    (
        "BRIEF §Storie / WORKING-PAPER §7",
        "addetti in unità sotto i 10, 2023: 42,9 %",
        42.9,
        lambda: addetti("2023", "0-9") / addetti("2023", "totale") * 100,
        0.05,
    ),
    (
        "FONTI §1-bis / METODOLOGIA MET-8",
        "la provincia guadagna 29.421 addetti fra 2018 e 2023",
        29421,
        lambda: addetti("2023", "totale") - addetti("2018", "totale"),
        2,
    ),
    (
        "BRIEF §Storie / WORKING-PAPER §7",
        "addetti in unità 10–249: +23.840 fra 2018 e 2023",
        23840,
        lambda: (addetti("2023", "10-49") + addetti("2023", "50-249"))
        - (addetti("2018", "10-49") + addetti("2018", "50-249")),
        2,
    ),
    (
        "FONTI §1-bis / WORKING-PAPER §6.1",
        "il capoluogo è fermo: −197 addetti fra 2018 e 2023",
        -197,
        lambda: addetti("2023", "totale", comune=CAPOLUOGO)
        - addetti("2018", "totale", comune=CAPOLUOGO),
        1,
    ),
    (
        "FONTI §1-bis / WORKING-PAPER §6.1",
        "addetti in unità ≥250 nel capoluogo: −6.335",
        -6335,
        lambda: addetti("2023", "250+", comune=CAPOLUOGO) - addetti("2018", "250+", comune=CAPOLUOGO),
        1,
    ),
    (
        "FONTI §1-bis",
        "unità locali ≥250 nel capoluogo: 35 → 28",
        28,
        lambda: addetti("2023", "250+", "unita_locali", comune=CAPOLUOGO),
        0,
    ),
    (
        "FONTI §1-bis",
        "il capoluogo vale il 21 % degli addetti provinciali",
        21.1,
        lambda: addetti("2023", "totale", comune=CAPOLUOGO) / addetti("2023", "totale") * 100,
        0.1,
    ),
    (
        "FONTI §1-bis",
        "quota degli addetti in unità ≥250, città: 13,6 %",
        13.6,
        lambda: addetti("2023", "250+", comune=CAPOLUOGO)
        / addetti("2023", "totale", comune=CAPOLUOGO)
        * 100,
        0.05,
    ),
    (
        "README / BRIEF §Storie / WORKING-PAPER §7",
        "presenze turistiche provinciali 2024: 12.246.854",
        12246854,
        lambda: sum(presenze_2024().values()),
        1,
    ),
    (
        "README / BRIEF §Storie",
        "i primi dieci comuni fanno il 68,8 % delle presenze",
        68.8,
        lambda: sum(sorted(presenze_2024().values(), reverse=True)[:10])
        / sum(presenze_2024().values())
        * 100,
        0.05,
    ),
    (
        "WORKING-PAPER §7",
        "Brescia città: 883.531 presenze, il 7,2 % del totale",
        7.2,
        lambda: presenze_2024()[CAPOLUOGO] / sum(presenze_2024().values()) * 100,
        0.05,
    ),
    (
        "METODOLOGIA MET-3",
        "45 comuni su 178 hanno le presenze 2024 soppresse",
        45,
        lambda: sum(
            1
            for r in turismo
            if r["anno"] == "2024"
            and r["tipo_struttura"] == "Totale"
            and r["cittadinanza"] == "Totale"
            and r["stato"] == "riservato"
        ),
        0,
    ),
    (
        "dati/README §Territorio",
        "Odolo: 89,6 addetti ogni 100 abitanti",
        89.6,
        lambda: next(float(r["addetti_per_100_abitanti"]) for r in sintesi if r["comune"] == "Odolo"),
        0.05,
    ),
    (
        "PROSSIMI-PASSI §4",
        "Limone sul Garda: 133 addetti ogni 100 abitanti",
        133.0,
        lambda: next(
            float(r["addetti_per_100_abitanti"]) for r in sintesi if r["comune"] == "Limone sul Garda"
        ),
        0.05,
    ),
    # --- le cifre delle analisi e del sito (agosto 2026) ----------------
    (
        "PROSSIMI-PASSI §4 / sito §Dove si svuota",
        "93 comuni su 205 perdono popolazione fra 2018 e 2024",
        93,
        comuni_in_calo,
        0,
    ),
    (
        "METODOLOGIA MET-12 / sito §I redditi",
        "convergenza dei redditi: Pearson −0,45 sul livello iniziale",
        -0.45,
        convergenza_reddito,
        0.01,
    ),
    (
        "METODOLOGIA MET-12 / sito §I redditi",
        "lo stesso calcolo sul livello finale: +0,12, e cambia segno",
        0.12,
        artefatto_reddito,
        0.01,
    ),
    (
        "sito §Dove si svuota",
        "Moran sulla crescita della popolazione: 0,34",
        0.34,
        moran_crescita_popolazione,
        0.01,
    ),
    (
        "sito §Le due economie",
        "Moran sulla specializzazione settoriale: 0,44",
        0.44,
        moran_specializzazione,
        0.01,
    ),
    (
        "WORKING-PAPER §6.1 / sito §Il crollo",
        "unità ≥250 del capoluogo: −6.336 addetti fra 2018 e 2023",
        -6335.6,
        lambda: addetti_settore_classe(CAPOLUOGO, "0010", "250+", "2023")
        - addetti_settore_classe(CAPOLUOGO, "0010", "250+", "2018"),
        1,
    ),
    (
        "WORKING-PAPER §6.1 / sito §Il crollo",
        "di cui somministrazione di personale (div. 78): −4.167",
        -4167.1,
        lambda: addetti_settore_classe(CAPOLUOGO, "78", "250+", "2023")
        - addetti_settore_classe(CAPOLUOGO, "78", "250+", "2018"),
        1,
    ),
    (
        "WORKING-PAPER §6.1 / sito §Il crollo",
        "e servizi per edifici (div. 81): −3.123, la classe sparisce",
        -3122.9,
        lambda: addetti_settore_classe(CAPOLUOGO, "81", "250+", "2023")
        - addetti_settore_classe(CAPOLUOGO, "81", "250+", "2018"),
        1,
    ),
    (
        "WORKING-PAPER §6.1 / sito §Il crollo",
        "la manifattura grande del capoluogo è ferma: −51 addetti",
        -51.0,
        lambda: manifattura_grande_capoluogo("2023") - manifattura_grande_capoluogo("2018"),
        1,
    ),
    (
        "WORKING-PAPER §6.1",
        "div. 81 in provincia, tutte le classi: −536 addetti su 12.699",
        -536.1,
        lambda: addetti_settore_classe(PROVINCIA, "81", "totale", "2023")
        - addetti_settore_classe(PROVINCIA, "81", "totale", "2018"),
        1,
    ),
    (
        "sito §Le due economie",
        "48 comuni hanno più della metà degli addetti nella manifattura",
        48,
        lambda: sum(1 for q in quote_sezioni("2023").values() if q.get("C", 0.0) >= 50),
        0,
    ),
    (
        "sito §Le due economie",
        "in provincia la manifattura vale il 32,4 % degli addetti ASIA",
        32.4,
        lambda: sum(
            numero(r["valore"]) or 0.0
            for r in sezioni
            if r["anno"] == "2023" and r["indicatore"] == "addetti" and r["sezione"] == "C"
        )
        / addetti("2023", "totale")
        * 100,
        0.05,
    ),
    (
        "README §In sintesi / sito §I redditi",
        "il comune più ricco dichiara 2,5 volte il più povero (2023)",
        2.51,
        lambda: max(reddito_medio("2023").values()) / min(reddito_medio("2023").values()),
        0.01,
    ),
    (
        "README §In sintesi / sito §I redditi",
        "nel 2012 il rapporto era 2,2",
        2.17,
        lambda: max(reddito_medio("2012").values()) / min(reddito_medio("2012").values()),
        0.01,
    ),
    (
        "METODOLOGIA MET-9",
        "div. 81, unità locali del capoluogo: +157 fra 2018 e 2023",
        157,
        lambda: unita_settore_classe(CAPOLUOGO, "81", "totale", "2023")
        - unita_settore_classe(CAPOLUOGO, "81", "totale", "2018"),
        0,
    ),
    (
        "WORKING-PAPER §7.3",
        "crescita del reddito, mediana dei comuni: +2,23 %/anno",
        2.23,
        lambda: statistics.median(
            tasso(reddito_medio("2012")[c], reddito_medio("2023")[c], 11)
            for c in reddito_medio("2012")
            if c in reddito_medio("2023")
        ),
        0.01,
    ),
    (
        "WORKING-PAPER §7.1",
        "unità locali sotto i 10 addetti, 2018: 92,8 %",
        92.8,
        lambda: addetti("2018", "0-9", "unita_locali") / addetti("2018", "totale", "unita_locali") * 100,
        0.05,
    ),
    (
        "WORKING-PAPER §7.1",
        "addetti in micro-unità: +6.842 fra 2018 e 2023",
        6842,
        lambda: addetti("2023", "0-9") - addetti("2018", "0-9"),
        2,
    ),
    (
        "WORKING-PAPER §7.1",
        "addetti in unità ≥250 in provincia: −1.260",
        -1260,
        lambda: addetti("2023", "250+") - addetti("2018", "250+"),
        2,
    ),
    (
        "WORKING-PAPER §7.4",
        "alloggio e ristorazione: 8,0 % degli addetti provinciali",
        8.0,
        lambda: sum(
            numero(r["valore"]) or 0.0
            for r in sezioni
            if r["anno"] == "2023" and r["indicatore"] == "addetti" and r["sezione"] == "I"
        )
        / addetti("2023", "totale")
        * 100,
        0.05,
    ),
    (
        "WORKING-PAPER §7.4 / sito §Le due economie",
        "manifattura e alloggio sono alternative: Pearson −0,67",
        -0.67,
        lambda: correlazione(
            *zip(*[
                (q["C"], q["I"])
                for q in quote_sezioni("2023").values()
                if "C" in q and "I" in q
            ])
        ),
        0.01,
    ),
    (
        "WORKING-PAPER §7.4",
        "24 comuni hanno almeno un quarto degli addetti in alloggio",
        24,
        lambda: sum(1 for q in quote_sezioni("2023").values() if q.get("I", 0.0) >= 25),
        0,
    ),
    (
        "WORKING-PAPER §6.2",
        "Moran sul reddito per contribuente: 0,43",
        0.43,
        lambda: moran(reddito_medio("2023")),
        0.01,
    ),
    # --- il confronto fra province (MET-14) ------------------------------
    (
        "WORKING-PAPER §7.3 / sito §I redditi",
        "la convergenza dei redditi a Bergamo: Pearson −0,48",
        -0.48,
        convergenza_bergamo,
        0.01,
    ),
    (
        "WORKING-PAPER §7.3 / sito §I redditi",
        "rapporto fra decili del reddito, 2012: 1,34",
        1.345,
        lambda: decili(reddito_medio("2012")),
        0.005,
    ),
    (
        "WORKING-PAPER §7.3 / sito §I redditi",
        "rapporto fra decili del reddito, 2023: 1,26 (si stringe)",
        1.265,
        lambda: decili(reddito_medio("2023")),
        0.005,
    ),
    (
        "METODOLOGIA MET-14 / WORKING-PAPER §7.1",
        "unità locali sotto i 10: mediana provinciale italiana 94,4 %",
        94.4,
        lambda: mediana_lista(list(quota_provinciale(
            "2023", "classe_addetti", "0-9", "unita_locali").values())),
        0.05,
    ),
    (
        "METODOLOGIA MET-14 / WORKING-PAPER §7.1",
        "Brescia è la 101ª provincia su 107 per frammentazione",
        101,
        lambda: rango_brescia(quota_provinciale(
            "2023", "classe_addetti", "0-9", "unita_locali")),
        0,
    ),
    (
        "METODOLOGIA MET-14 / WORKING-PAPER §7.1",
        "addetti in unità sotto i 10: mediana provinciale 51,0 %",
        51.0,
        lambda: mediana_lista(list(quota_provinciale(
            "2023", "classe_addetti", "0-9", "addetti").values())),
        0.05,
    ),
    (
        "METODOLOGIA MET-14 / WORKING-PAPER §7.1",
        "manifattura: Brescia 15ª provincia d'Italia",
        15,
        lambda: rango_brescia(quota_provinciale("2023", "sezione", "C", "addetti")),
        0,
    ),
    (
        "METODOLOGIA MET-14 / WORKING-PAPER §7.1",
        "manifattura: mediana provinciale 20,7 %",
        20.7,
        lambda: mediana_lista(list(quota_provinciale("2023", "sezione", "C", "addetti").values())),
        0.05,
    ),
    (
        "METODOLOGIA MET-14 / WORKING-PAPER §7.2",
        "la classe ≥250 cala in 44 capoluoghi su 64",
        44,
        lambda: sum(1 for v in variazioni_capoluoghi() if v < 0),
        0,
    ),
    (
        "METODOLOGIA MET-14 / WORKING-PAPER §7.2",
        "mediana dei capoluoghi sulla classe ≥250: −11,9 %",
        -11.9,
        lambda: mediana_lista(variazioni_capoluoghi()),
        0.05,
    ),
    (
        "METODOLOGIA MET-8",
        "presenze turistiche 2020: −53,9 % rispetto all'attesa stagionale",
        -53.9,
        lambda: scarto_stagionale_turismo("2020"),
        0.1,
    ),
    (
        "METODOLOGIA MET-8",
        "presenze turistiche 2022: già +18,1 % sopra l'attesa",
        18.1,
        lambda: scarto_stagionale_turismo("2022"),
        0.1,
    ),
    (
        "analysis/autocorrelazione_spaziale",
        "contiguità: grado medio 5,37 vicini per comune",
        5.37,
        lambda: sum(len(v) for v in vicini().values()) / len(vicini()),
        0.01,
    ),
    (
        "WORKING-PAPER §7",
        "PM10 a Brescia v.Broletto, 2001: 45,5 µg/m³",
        45.5,
        lambda: media_pm10_broletto("2001"),
        0.05,
    ),
    (
        "WORKING-PAPER §7",
        "PM10 a Brescia v.Broletto, 2024: 27,3 µg/m³",
        27.3,
        lambda: media_pm10_broletto("2024"),
        0.05,
    ),
    # --- la scomposizione demografica (agosto 2026) ---------------------
    (
        "sito §Dove si svuota / METODOLOGIA MET-15",
        "la scomposizione chiude: componenti = variazione degli stock",
        0,
        lambda: max(
            abs(
                valori["totale"]
                - (
                    serie_popolazione()[codice]["2024"]
                    - serie_popolazione()[codice]["2018"]
                )
            )
            for codice, valori in bilancio_comuni().items()
        ),
        0.5,
    ),
    (
        "sito §Dove si svuota",
        "saldo naturale provinciale 2018-2024: −25.764",
        -25764,
        lambda: componente_provinciale("naturale"),
        0,
    ),
    (
        "sito §Dove si svuota",
        "migrazione estera provinciale: +27.817",
        27817,
        lambda: componente_provinciale("estera"),
        0,
    ),
    (
        "sito §Dove si svuota",
        "migrazione interna provinciale: +13.970",
        13970,
        lambda: componente_provinciale("interna"),
        0,
    ),
    (
        "sito §Dove si svuota",
        "aggiustamento statistico provinciale: −4.558",
        -4558,
        lambda: componente_provinciale("aggiustamento"),
        0,
    ),
    (
        "sito §Dove si svuota",
        "senza la migrazione estera la provincia perderebbe 16.352 abitanti",
        16352,
        lambda: componente_provinciale("estera") - componente_provinciale("totale"),
        0,
    ),
    (
        "sito §Dove si svuota / METODOLOGIA MET-15",
        "i 93 comuni in calo: −10.163 per saldo naturale",
        -10163,
        lambda: in_calo_componente("naturale"),
        0,
    ),
    (
        "sito §Dove si svuota / METODOLOGIA MET-15",
        "gli stessi 93 comuni: −66 per migrazione interna, cioè quasi zero",
        -66,
        lambda: in_calo_componente("interna"),
        0,
    ),
    (
        "sito §Dove si svuota",
        "in 81 dei 93 comuni in calo la componente più negativa è il saldo naturale",
        81,
        lambda: comuni_per_componente_piu_negativa("naturale"),
        0,
    ),
    (
        "sito §Dove si svuota",
        "in 12 dei 93 comuni in calo tira più giù la migrazione interna",
        12,
        lambda: comuni_per_componente_piu_negativa("interna"),
        0,
    ),
    (
        "sito §Dove si svuota",
        "saldo naturale negativo in 189 comuni su 205",
        189,
        comuni_con_naturale_negativo,
        0,
    ),
    (
        "sito §Dove si svuota / PROSSIMI-PASSI §5.2",
        "Brescia è la 6ª provincia italiana per crescita di popolazione",
        6,
        lambda: rango_provincia("totale"),
        0,
    ),
    (
        "sito §Dove si svuota",
        "crescita di Brescia: +9,1 abitanti ogni mille",
        9.1,
        lambda: brescia_per_mille("totale"),
        0.05,
    ),
    (
        "sito §Dove si svuota",
        "mediana delle province: −19,7 ogni mille",
        -19.7,
        lambda: mediana_province("totale"),
        0.05,
    ),
    (
        "sito §Dove si svuota",
        "solo 21 province su 107 crescono",
        21,
        lambda: province_con("totale"),
        0,
    ),
    (
        "sito §Dove si svuota",
        "il saldo naturale è positivo in 1 provincia su 107",
        1,
        lambda: province_con("naturale"),
        0,
    ),
    (
        "sito §Dove si svuota",
        "saldo naturale di Brescia: 14º migliore d'Italia, −20,5 ogni mille",
        14,
        lambda: rango_provincia("naturale"),
        0,
    ),
    (
        "sito §Dove si svuota",
        "mediana del saldo naturale provinciale: −34,4 ogni mille",
        -34.4,
        lambda: mediana_province("naturale"),
        0.05,
    ),
    (
        "README §In sintesi / WORKING-PAPER §7.7 / sito, sesta storia",
        "PM10 sul panel bilanciato: -42,0 %",
        -42.0,
        lambda: variazione_inquinante("PM10 (SM2005)"),
        0.05,
    ),
    (
        "README §In sintesi / WORKING-PAPER §7.7 / sito, sesta storia",
        "biossido di azoto sul panel bilanciato: -38,9 %",
        -38.9,
        lambda: variazione_inquinante("Biossido di Azoto"),
        0.05,
    ),
    (
        "README §In sintesi / WORKING-PAPER §7.7 / sito, sesta storia",
        "ozono sul panel bilanciato: -1,8 %, cioè fermo",
        -1.8,
        lambda: variazione_inquinante("Ozono"),
        0.05,
    ),
    (
        "README §In sintesi / WORKING-PAPER §7.7 / sito, sesta storia",
        "temperatura: +1,10 °C fra le due finestre",
        1.10,
        scarto_temperatura,
        0.005,
    ),
    (
        "README §In sintesi / WORKING-PAPER §7.7 / sito, sesta storia",
        "in aumento 8 stazioni di temperatura su 8",
        8,
        stazioni_piu_calde,
        0,
    ),
    (
        "WORKING-PAPER §7.7 / sito, sesta storia",
        "le stazioni di temperatura con entrambe le finestre sono 8",
        8,
        stazioni_di_temperatura,
        0,
    ),
    (
        "WORKING-PAPER §7.7 / sito, sesta storia e §Limiti",
        "pioggia: variazione mediana +0,5 %, cioè nessun segnale",
        0.5,
        variazione_mediana_pioggia,
        0.05,
    ),
    (
        "WORKING-PAPER §7.7, tabella",
        "conto ingenuo PM10: -45,5 %, contro -42,0 % del panel",
        -45.5,
        lambda: variazione_ingenua("PM10 (SM2005)"),
        0.05,
    ),
    (
        "WORKING-PAPER §7.7, tabella",
        "conto ingenuo biossido di azoto: -42,3 %",
        -42.3,
        lambda: variazione_ingenua("Biossido di Azoto"),
        0.05,
    ),
    (
        "WORKING-PAPER §7.7: il segno rovesciato",
        "conto ingenuo ozono: +5,5 %, cioè il segno opposto al panel",
        5.5,
        lambda: variazione_ingenua("Ozono"),
        0.05,
    ),
    (
        "README §In sintesi / WORKING-PAPER §7.7 e §8 / sito, sesta storia",
        "le centraline sono esistite in 11 comuni su 205",
        11,
        lambda: len(_comuni_con_centralina()),
        0,
    ),
    (
        "WORKING-PAPER §7.7 / sito, sesta storia",
        "7 delle centraline stanno nel capoluogo",
        7,
        lambda: len(_comuni_con_centralina()["Brescia"]),
        0,
    ),
    (
        "WORKING-PAPER §7.7 / sito, sesta storia",
        "gli altri comuni con centralina ne hanno una ciascuno",
        10,
        lambda: sum(1 for c, s in _comuni_con_centralina().items() if c != "Brescia" and len(s) == 1),
        0,
    ),
    (
        "WORKING-PAPER §7.8 / analysis/confronto_turismo.py",
        "presenze in provincia di Brescia 2024: 11.068.441 (ISTAT)",
        11068441,
        lambda: turismo_valore("presenze"),
        0,
    ),
    (
        "WORKING-PAPER §7.8",
        "Brescia è la 10ª provincia italiana per presenze",
        10,
        lambda: turismo_rango("presenze"),
        0,
    ),
    (
        "WORKING-PAPER §7.8",
        "la provincia mediana ha 2.088.719 presenze",
        2088719,
        lambda: turismo_mediana("presenze"),
        0,
    ),
    (
        "WORKING-PAPER §7.8",
        "presenze per abitante: 8,74 contro una mediana di 4,97",
        8.74,
        lambda: turismo_valore("per_abitante"),
        0.005,
    ),
    (
        "WORKING-PAPER §7.8",
        "presenze per abitante, mediana provinciale: 4,97",
        4.97,
        lambda: turismo_mediana("per_abitante"),
        0.005,
    ),
    (
        "WORKING-PAPER §7.8",
        "presenze per abitante: Brescia 29ª su 107",
        29,
        lambda: turismo_rango("per_abitante"),
        0,
    ),
    (
        "WORKING-PAPER §7.8",
        "quota di presenze straniere: 72,0 % contro una mediana del 37,7 %",
        72.01,
        lambda: turismo_valore("quota_estera"),
        0.05,
    ),
    (
        "WORKING-PAPER §7.8",
        "quota di presenze straniere, mediana provinciale: 37,7 %",
        37.68,
        lambda: turismo_mediana("quota_estera"),
        0.05,
    ),
    (
        "WORKING-PAPER §7.8",
        "quota straniera: Brescia 6ª su 107",
        6,
        lambda: turismo_rango("quota_estera"),
        0,
    ),
    (
        "WORKING-PAPER §7.8",
        "quota alberghiera: 52,9 % contro una mediana del 62,1 %",
        52.92,
        lambda: turismo_valore("quota_alberghiera"),
        0.05,
    ),
    (
        "WORKING-PAPER §7.8",
        "quota alberghiera, mediana provinciale: 62,1 %",
        62.06,
        lambda: turismo_mediana("quota_alberghiera"),
        0.05,
    ),
    (
        "WORKING-PAPER §7.8",
        "presenze in campeggi e villaggi: 26,7 % contro una mediana del 9,1 %",
        26.72,
        lambda: turismo_valore("quota_campeggi"),
        0.05,
    ),
    (
        "WORKING-PAPER §7.8",
        "campeggi e villaggi, mediana provinciale: 9,1 %",
        9.14,
        lambda: turismo_mediana("quota_campeggi"),
        0.05,
    ),
    (
        "WORKING-PAPER §7.8",
        "crescita composta delle presenze 2008-2024: +2,09 %/anno",
        2.09,
        turismo_crescita_lunga,
        0.005,
    ),
    (
        "WORKING-PAPER §7.8",
        "crescita 2008-2024, mediana provinciale: +0,96 %/anno",
        0.96,
        lambda: mediana_lista(list(_crescite_lunghe().values())),
        0.005,
    ),
    (
        "WORKING-PAPER §7.8",
        "le province con la serie 2008-2024 intera sono 99",
        99,
        lambda: len(_crescite_lunghe()),
        0,
    ),
    (
        "WORKING-PAPER §7.8",
        "recupero 2019-2024: +13,8 % contro una mediana del +5,5 %",
        13.81,
        lambda: turismo_valore("crescita_2019"),
        0.05,
    ),
    (
        "WORKING-PAPER §7.8",
        "recupero 2019-2024, mediana provinciale: +5,5 %",
        5.45,
        lambda: turismo_mediana("crescita_2019"),
        0.05,
    ),
    (
        "WORKING-PAPER §7.8",
        "caduta 2020: -54,3 % contro una mediana del -49,5 %",
        -54.28,
        lambda: turismo_valore("caduta_2020"),
        0.05,
    ),
    (
        "WORKING-PAPER §7.8",
        "caduta 2020, mediana provinciale: -49,5 %",
        -49.51,
        lambda: turismo_mediana("caduta_2020"),
        0.05,
    ),
    (
        "METODOLOGIA MET-17 / WORKING-PAPER §7.8",
        "le due fonti sul turismo bresciano distano il 6,5 % nel 2019",
        6.5,
        lambda: scarto_fonti_turismo("2019"),
        0.05,
    ),
    (
        "METODOLOGIA MET-17 / WORKING-PAPER §7.8",
        "e il 10,6 % nel 2024: lo scarto cresce",
        10.6,
        lambda: scarto_fonti_turismo("2024"),
        0.05,
    ),
    (
        "WORKING-PAPER §7.8",
        "la quota straniera bresciana era il 61,9 % nel 2008",
        61.9,
        lambda: turismo_quota_estera("2008"),
        0.05,
    ),
    (
        "WORKING-PAPER §7.8",
        "le province piu' internazionali di Brescia sono cinque",
        5,
        turismo_piu_internazionali,
        0,
    ),
    (
        "WORKING-PAPER §7.8",
        "Bolzano fa 68,7 notti per residente, Brescia 8,74",
        68.65,
        lambda: turismo_di("Bolzano/Bozen", "per_abitante"),
        0.05,
    ),
    (
        "WORKING-PAPER §7.8",
        "Rimini 44,1 notti per residente",
        44.14,
        lambda: turismo_di("Rimini", "per_abitante"),
        0.05,
    ),
    (
        "WORKING-PAPER §7.8",
        "Bergamo, la gemella, cresce del 2,98 %/anno dal 2008",
        2.98,
        lambda: _crescite_lunghe()["016"],
        0.005,
    ),
    (
        "WORKING-PAPER §7.8",
        "la caduta 2020 degli addetti ASIA in provincia: -2,7 %",
        -2.69,
        lambda: (addetti("2020", "totale") / addetti("2019", "totale") - 1) * 100,
        0.005,
    ),
    (
        "WORKING-PAPER §7.8",
        "e quella della classe >=250 della provincia: -19,5 %",
        -19.52,
        lambda: (addetti("2020", "250+") / addetti("2019", "250+") - 1) * 100,
        0.005,
    ),
    (
        "WORKING-PAPER §7.8",
        "35 province su 107 non hanno riguadagnato il livello del 2019",
        35,
        lambda: 107 - turismo_sopra_il_2019(),
        0,
    ),
    (
        "METODOLOGIA MET-17",
        "lo scarto fra le fonti nel 2021: 7,1 %",
        7.1,
        lambda: scarto_fonti_turismo("2021"),
        0.05,
    ),
    (
        "METODOLOGIA MET-17",
        "lo scarto fra le fonti nel 2023: 9,6 %",
        9.6,
        lambda: scarto_fonti_turismo("2023"),
        0.05,
    ),
    (
        "METODOLOGIA MET-17",
        "sugli arrivi lo scarto e' piu' contenuto: 2,0 % nel 2019",
        2.0,
        lambda: scarto_fonti_turismo("2019", "arrivi"),
        0.05,
    ),
    (
        "METODOLOGIA MET-17",
        "e 7,0 % nel 2024: e' un fenomeno delle notti, non delle persone",
        7.0,
        lambda: scarto_fonti_turismo("2024", "arrivi"),
        0.05,
    ),
    (
        "METODOLOGIA MET-18 / WORKING-PAPER §7.8",
        "alloggi in affitto, Italia 2024->2025: +87,6 %, cioè una definizione",
        87.6,
        scalino_2025,
        0.05,
    ),
    (
        "METODOLOGIA MET-18",
        "e il totale Italia ne guadagna il 14,9 % in un anno",
        14.9,
        lambda: scalino_2025("totale"),
        0.05,
    ),
    (
        "METODOLOGIA MET-18",
        "mentre l'alberghiero, che la voce non la contiene, fa +1,5 %",
        1.5,
        lambda: scalino_2025("alberghiero"),
        0.05,
    ),
    (
        "METODOLOGIA MET-18",
        "e campeggi e villaggi +1,3 %: un evento vero si vedrebbe su tutti",
        1.3,
        lambda: scalino_2025("campeggi e villaggi"),
        0.05,
    ),
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="verifica_cifre")
    parser.add_argument("--csv", action="store_true", help="scrive anche analysis/output/verifica_cifre.csv")
    args = parser.parse_args(argv)

    righe: list[dict[str, str]] = []
    divergenti = 0

    print(f"{'esito':6} {'cifra citata':62} {'atteso':>14} {'calcolato':>14}")
    print("-" * 100)
    for documento, cifra, atteso, calcola, tolleranza in VERIFICHE:
        ottenuto = float(calcola())
        ok = abs(ottenuto - atteso) <= tolleranza
        divergenti += not ok
        print(f"{'ok' if ok else 'DIVERGE':6} {cifra[:62]:62} {atteso:>14,.2f} {ottenuto:>14,.2f}")
        righe.append(
            {
                "documento": documento,
                "cifra": cifra,
                "atteso": f"{atteso:.4f}",
                "calcolato": f"{ottenuto:.4f}",
                "tolleranza": f"{tolleranza:.4f}",
                "esito": "ok" if ok else "diverge",
            }
        )

    print("-" * 100)
    print(f"{len(VERIFICHE)} verifiche, {divergenti} divergenti")

    if args.csv:
        OUTPUT.mkdir(parents=True, exist_ok=True)
        destinazione = OUTPUT / "verifica_cifre.csv"
        with destinazione.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=["documento", "cifra", "atteso", "calcolato", "tolleranza", "esito"],
                lineterminator="\n",
            )
            writer.writeheader()
            writer.writerows(righe)
        print(f"scritto {destinazione.relative_to(RADICE)}")

    return 1 if divergenti else 0


if __name__ == "__main__":
    sys.exit(main())
