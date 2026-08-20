"""I comuni contigui si somigliano? Indice di Moran sui 205 comuni.

    python analysis/autocorrelazione_spaziale.py
    python analysis/autocorrelazione_spaziale.py --save     # + i due CSV in analysis/output/
    python analysis/autocorrelazione_spaziale.py --permutazioni 9999

`PROSSIMI-PASSI.md` §5.2, quarto punto. Con 19 quartieri non aveva senso; con
205 comuni e una geometria vera sì: **quanto di un indicatore è spiegato dal
semplice stare vicino a chi ce l'ha uguale.** Se l'autocorrelazione è alta, i
confini comunali non sono l'unità del fenomeno — la valle lo è — e questo
cambia il modo in cui una coropletica va letta.

**La matrice di contiguità** si ricava dal GeoJSON già nel repository, senza
librerie: due comuni sono vicini se i loro poligoni **condividono almeno un
vertice**. Funziona perché i confini ISTAT sono topologicamente coerenti — il
vertice sul confine fra due comuni è lo stesso punto in entrambi i poligoni, non
due punti quasi uguali. Il grado medio risultante è 5,4 vicini per comune e
nessun comune resta isolato, che è il controllo di sanità di questa scelta.

⚠️ Il Garda è acqua ma i confini comunali ci passano dentro: comuni sulle due
sponde risultano contigui. È corretto dal punto di vista amministrativo e
discutibile da quello economico, e va ricordato quando l'indicatore è turistico.

**L'indice di Moran** vale circa 0 quando i valori sono sparsi a caso, tende a
+1 quando i simili stanno vicini, a −1 quando i vicini sono sistematicamente
diversi (a scacchiera). Il valore atteso sotto ipotesi nulla non è 0 ma
−1/(n−1) = −0,0049, e per 205 comuni la differenza è trascurabile ma si
riporta comunque.

**La significatività è per permutazione**, non da una formula: si rimescolano i
valori fra i comuni tenendo ferma la geometria, e si guarda quanto è raro
l'indice osservato. Il seme è fisso (MET-1: due esecuzioni devono dare lo stesso
numero). Il *pseudo-p* così ottenuto non è un p-value classico e non va
raccontato come tale.

Confidenza: `derivato` (MET-4).
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _tabelle import (  # noqa: E402
    PROCESSED,
    RADICE,
    anagrafica,
    geometria,
    media,
    numero,
    scrivi_csv,
    serie_imprese,
    serie_popolazione,
    serie_reddito,
    sintesi,
    tasso_annualizzato,
)

GEOJSON = RADICE / "dati" / "geo" / "comuni_brescia.geojson"
SEME = 20260819  # MET-1: fisso, e scritto qui perché si veda

COLONNE_GLOBALI = ["indicatore", "n", "moran_i", "atteso", "media_permutazioni", "pseudo_p"]
COLONNE_LOCALI = ["indicatore", "codice_istat", "comune", "valore", "z", "media_vicini_z", "moran_locale", "tipo"]


# --- la matrice di contiguità -------------------------------------------


def vicini() -> dict[str, set[str]]:
    """Contiguità per vertice condiviso, letta dal GeoJSON del progetto."""
    geo = json.loads(GEOJSON.read_text(encoding="utf-8"))
    per_vertice: dict[tuple[float, float], set[str]] = defaultdict(set)
    for feature in geo["features"]:
        codice = feature["properties"]["codice_istat"]
        for anello in feature["geometry"]["coordinates"]:
            for x, y in anello:
                per_vertice[(round(x, 5), round(y, 5))].add(codice)

    adiacenze: dict[str, set[str]] = {f["properties"]["codice_istat"]: set() for f in geo["features"]}
    for condivisori in per_vertice.values():
        if len(condivisori) < 2:
            continue
        for uno in condivisori:
            adiacenze[uno] |= condivisori - {uno}
    return adiacenze


# --- gli indicatori da testare ------------------------------------------


def indicatori() -> dict[str, dict[str, float]]:
    riassunto = sintesi()
    geo = geometria()
    popolazione = serie_popolazione()
    addetti = serie_imprese("addetti")
    reddito = serie_reddito()

    valori: dict[str, dict[str, float]] = {
        "addetti per 100 abitanti (2023)": {},
        "reddito per contribuente (2023)": {},
        "densità abitativa (ab./km², 2024)": {},
        "crescita della popolazione (%/anno, 2018–2024)": {},
        "crescita degli addetti (%/anno, 2018–2023)": {},
        "presenze turistiche per abitante (2024)": {},
    }

    for codice, riga in riassunto.items():
        abitanti = numero(riga["popolazione_2024"])
        area = numero(geo[codice]["area_kmq"])
        occupati = numero(riga["addetti_2023"])
        presenze = numero(riga["presenze_turistiche_2024"])

        if abitanti and occupati is not None:
            valori["addetti per 100 abitanti (2023)"][codice] = occupati / abitanti * 100
        if abitanti and area:
            valori["densità abitativa (ab./km², 2024)"][codice] = abitanti / area
        if abitanti and presenze is not None:
            # I 73 comuni senza dato restano fuori: un'assenza non è uno zero
            # (MET-3), e su questo indicatore ce ne sono tre tipi diversi.
            valori["presenze turistiche per abitante (2024)"][codice] = presenze / abitanti

    for codice, serie in reddito.items():
        valori["reddito per contribuente (2023)"][codice] = serie[max(serie)]

    for nome_serie, serie in (
        ("crescita della popolazione (%/anno, 2018–2024)", popolazione),
        ("crescita degli addetti (%/anno, 2018–2023)", addetti),
    ):
        for codice, per_anno in serie.items():
            anni = sorted(per_anno)
            tasso = tasso_annualizzato(
                per_anno[anni[0]], per_anno[anni[-1]], int(anni[-1]) - int(anni[0])
            )
            if tasso is not None:
                valori[nome_serie][codice] = tasso

    return valori


# --- l'indice ------------------------------------------------------------


def moran(valori: dict[str, float], adiacenze: dict[str, set[str]]) -> tuple[float, list[float], list[float]]:
    """Moran's I con pesi normalizzati per riga, più gli scarti standardizzati
    e la media dei vicini di ciascun comune (che servono al Moran locale)."""
    codici = [c for c in valori if adiacenze.get(c)]
    media_valori = media([valori[c] for c in codici])
    z = {c: valori[c] - media_valori for c in codici}

    medie_vicine: list[float] = []
    numeratore = 0.0
    for codice in codici:
        presenti = [v for v in adiacenze[codice] if v in z]
        if not presenti:
            medie_vicine.append(0.0)
            continue
        # Pesi normalizzati per riga: ogni comune pesa uno, non pesa quanti
        # vicini ha. Senza questo, i comuni di pianura con dodici confinanti
        # dominerebbero l'indice.
        media_vicini = media([z[v] for v in presenti])
        medie_vicine.append(media_vicini)
        numeratore += z[codice] * media_vicini

    denominatore = sum(valore**2 for valore in z.values())
    if denominatore == 0:
        return 0.0, [], []
    # I = (n/W) · Σ wij zi zj / Σ zi². Con i pesi normalizzati per riga ogni
    # riga somma 1, quindi W = n e il fattore n/W sparisce.
    return numeratore / denominatore, [z[c] for c in codici], medie_vicine


def permuta(
    valori: dict[str, float], adiacenze: dict[str, set[str]], quante: int
) -> tuple[float, float]:
    """Pseudo-p per permutazione, con seme fisso."""
    codici = [c for c in valori if adiacenze.get(c)]
    osservato, _, _ = moran(valori, adiacenze)
    rng = random.Random(SEME)
    estratti = [valori[c] for c in codici]
    estremi = 0
    somma = 0.0
    for _ in range(quante):
        rng.shuffle(estratti)
        rimescolato = dict(zip(codici, estratti))
        indice, _, _ = moran(rimescolato, adiacenze)
        somma += indice
        if abs(indice) >= abs(osservato):
            estremi += 1
    return (estremi + 1) / (quante + 1), somma / quante


def tipo_locale(z: float, media_vicini: float) -> str:
    if z >= 0 and media_vicini >= 0:
        return "alto fra alti"
    if z < 0 and media_vicini < 0:
        return "basso fra bassi"
    if z >= 0:
        return "alto fra bassi"
    return "basso fra alti"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="autocorrelazione_spaziale")
    parser.add_argument("--save", action="store_true", help="scrive i CSV in analysis/output/")
    parser.add_argument("--permutazioni", type=int, default=999, help="quante permutazioni (default 999)")
    parser.add_argument("--locali", type=int, default=5, help="quanti comuni per tipo nel dettaglio locale")
    args = parser.parse_args(argv)

    if not GEOJSON.exists() or not (PROCESSED / "comuni_sintesi.csv").exists():
        print("mancano i dati: lanciare prima `python -m brescia_pipeline.build`", file=sys.stderr)
        return 1

    adiacenze = vicini()
    gradi = [len(v) for v in adiacenze.values()]
    print(f"contiguità: {len(adiacenze)} comuni, {sum(gradi) // 2} confini, "
          f"grado medio {sum(gradi) / len(gradi):.2f} (da {min(gradi)} a {max(gradi)})")

    comuni = anagrafica()
    globali: list[dict[str, str]] = []
    locali: list[dict[str, str]] = []

    intestazione = f"\n{'indicatore':46} {'n':>4} {'Moran I':>9} {'pseudo-p':>9}"
    print(intestazione)
    print("-" * (len(intestazione) - 1))

    for nome_indicatore, valori in indicatori().items():
        indice, _, _ = moran(valori, adiacenze)
        pseudo_p, media_nulla = permuta(valori, adiacenze, args.permutazioni)
        n = len([c for c in valori if adiacenze.get(c)])
        print(f"{nome_indicatore:46} {n:>4} {indice:>9.3f} {pseudo_p:>9.4f}")
        globali.append(
            {
                "indicatore": nome_indicatore,
                "n": str(n),
                "moran_i": f"{indice:.4f}",
                "atteso": f"{-1 / (n - 1):.4f}",
                "media_permutazioni": f"{media_nulla:.4f}",
                "pseudo_p": f"{pseudo_p:.4f}",
            }
        )

        codici = [c for c in valori if adiacenze.get(c)]
        _, z, medie_vicine = moran(valori, adiacenze)
        for codice, scarto, vicinato in zip(codici, z, medie_vicine):
            locali.append(
                {
                    "indicatore": nome_indicatore,
                    "codice_istat": codice,
                    "comune": comuni[codice]["comune"],
                    "valore": f"{valori[codice]:.3f}",
                    "z": f"{scarto:.3f}",
                    "media_vicini_z": f"{vicinato:.3f}",
                    "moran_locale": f"{scarto * vicinato:.3f}",
                    "tipo": tipo_locale(scarto, vicinato),
                }
            )

    print("-" * (len(intestazione) - 1))
    print(f"{args.permutazioni} permutazioni, seme {SEME}. Atteso sotto ipotesi nulla: "
          f"{-1 / (len(adiacenze) - 1):.4f}")

    print("\nI grumi più forti (Moran locale, per indicatore)")
    for nome_indicatore in dict.fromkeys(r["indicatore"] for r in locali):
        sotto = [r for r in locali if r["indicatore"] == nome_indicatore]
        sotto.sort(key=lambda r: float(r["moran_locale"]), reverse=True)
        print(f"\n  {nome_indicatore}")
        for riga in sotto[: args.locali]:
            print(f"    {riga['comune'][:26]:26} {riga['valore']:>12}  {riga['tipo']}")

    if args.save:
        uno = scrivi_csv("autocorrelazione_globale.csv", COLONNE_GLOBALI, globali)
        due = scrivi_csv("autocorrelazione_locale.csv", COLONNE_LOCALI, locali)
        print(f"\nscritti {uno.relative_to(RADICE)} e {due.relative_to(RADICE)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
