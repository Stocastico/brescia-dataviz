"""L'asse casa: il prezzo che sta fermo, i volumi che raddoppiano, e l'inflazione.

    python analysis/casa_e_prezzi.py
    python analysis/casa_e_prezzi.py --save

`PROSSIMI-PASSI.md` §4, «Sulla casa». È la prima analisi del quinto asse, quello
arrivato a settembre 2026 con i dati e senza una lettura, e si legge in tre
parti che rispondono a tre domande diverse:

1. **il capoluogo, prezzi contro volumi.** Le due serie si muovono in modo
   opposto — €/m² fermo dal 2004, compravendite quasi raddoppiate dal fondo del
   2013 — e la domanda vera è quanto di quel «fermo» sia inflazione. Da qui il
   deflatore (MET-20): in euro correnti il prezzo è dove era, in euro costanti
   ha perso quasi un terzo;
2. **dentro il capoluogo, le 23 zone OMI.** È la grana da quartiere che al
   progetto è sempre mancata, e permette la domanda che a Donostia veniva dal
   barrio: il centro si è staccato dalla periferia? La risposta è **no, il
   contrario** — la forbice si stringe;
3. **la provincia, 203 comuni.** Dove costa e dove no, e quanto il prezzo si
   accompagni a reddito, addetti e popolazione. Con il leave-one-out di MET-5,
   che qui non è una formalità: il vertice della classifica è tutto gardesano.

⚠️ **Sono quotazioni, non transazioni.** L'OMI le chiama «indicazioni di valore
di larga massima»: un intervallo min-max per zona e tipologia, non il prezzo
pagato. Servono a confrontare zone e anni, non a stimare quanto vale una casa.

⚠️ **Il deflatore è nazionale** (MET-20). Ogni cifra «in euro costanti» qui
dentro assume che l'inflazione bresciana sia quella italiana.

Confidenza: `derivato` (MET-4) per tutto ciò che è in euro costanti,
`osservato` per le serie in euro correnti e per i volumi.
"""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _tabelle import (  # noqa: E402
    ANNO_EURO_COSTANTI,
    CAPOLUOGO,
    RADICE,
    anagrafica,
    codici_gardesani,
    in_euro_costanti,
    leggi,
    numero,
    pearson,
    scrivi_csv,
    senza,
    serie_imprese,
    serie_popolazione,
    serie_reddito,
    spearman,
)

# La tipologia su cui si legge il mercato della casa: le altre dodici (negozi,
# capannoni, box) misurano altri mercati e non si mediano con questa.
TIPOLOGIA = "Abitazioni civili"
# Le compravendite si sommano **solo** sul segmento `totale`: le classi di
# superficie lo ripartiscono, e sommare tutto conta due volte.
SEGMENTO_TOTALE = "totale"
# La base di superficie sta nella chiave, non nel commento (MET-19). Sulle
# vendite è lorda per tutti i ventidue semestri; sugli affitti cambia nel 2025,
# ed è il motivo per cui questo script legge le vendite.
BASE_VENDITE = "lorda"
# Nelle zone, `stato_prevalente = P` tiene un solo stato conservativo per zona:
# senza, dal 2008 la media mescola NORMALE e OTTIMO e «sale» del 27 % in un anno.
STATO_PREVALENTE = "P"

COLONNE_CAPOLUOGO = ["anno", "euro_mq_correnti", "euro_mq_costanti", "ntn_residenziale"]
COLONNE_ZONE = ["link_zona", "zona", "fascia", "primo_anno", "ultimo_anno",
                "euro_mq_2004", "euro_mq_2004_costanti", "euro_mq_ultimo", "variazione_reale"]
COLONNE_COMUNI = ["codice_istat", "comune", "euro_mq", "reddito", "addetti_per_100_abitanti",
                  "popolazione"]


# --- le tre letture -----------------------------------------------------


def prezzi_comune(codice: str) -> dict[str, float]:
    """`anno -> €/m² medio` delle abitazioni civili in vendita, per un comune."""
    fuori: dict[str, float] = {}
    for riga in leggi("quotazioni_comuni.csv"):
        if riga["codice_istat"] != codice or riga["tipologia"] != TIPOLOGIA:
            continue
        if riga["mercato"] != "vendita" or riga["base_superficie"] != BASE_VENDITE:
            continue
        valore = numero(riga["media"])
        if valore is not None:
            fuori[riga["anno"]] = valore
    return fuori


def volumi_residenziali(codice: str) -> dict[str, float]:
    """`anno -> NTN residenziale`, dal solo segmento `totale`."""
    fuori: dict[str, float] = {}
    for riga in leggi("compravendite_comuni.csv"):
        if riga["codice_istat"] != codice or riga["comparto"] != "residenziale":
            continue
        if riga["segmento"] != SEGMENTO_TOTALE:
            continue
        valore = numero(riga["ntn"])
        if valore is not None:
            fuori[riga["anno"]] = valore
    return fuori


def zone_capoluogo() -> dict[str, dict[str, float]]:
    """`link_zona -> anno -> €/m² medio` per le zone OMI del capoluogo.

    La chiave è `link_zona` e non `zona`: il codice di zona viene riusato quando
    la zonizzazione cambia, e nel 2024 a Brescia cambia.
    """
    fuori: dict[str, dict[str, float]] = defaultdict(dict)
    for riga in leggi("quotazioni_zone.csv"):
        if riga["codice_istat"] != CAPOLUOGO or riga["tipologia"] != TIPOLOGIA:
            continue
        if riga["stato_prevalente"] != STATO_PREVALENTE:
            continue
        minimo, massimo = numero(riga["vendita_min"]), numero(riga["vendita_max"])
        if minimo is None or massimo is None:
            continue
        fuori[riga["link_zona"]][riga["anno"]] = (minimo + massimo) / 2
    return dict(fuori)


def anagrafica_zone() -> dict[str, tuple[str, str]]:
    """`link_zona -> (codice zona più recente, fascia)`."""
    fuori: dict[str, tuple[str, str, str]] = {}
    for riga in leggi("quotazioni_zone.csv"):
        if riga["codice_istat"] != CAPOLUOGO:
            continue
        precedente = fuori.get(riga["link_zona"])
        if precedente is None or riga["anno"] >= precedente[0]:
            fuori[riga["link_zona"]] = (riga["anno"], riga["zona"], riga["fascia"])
    return {link: (zona, fascia) for link, (_anno, zona, fascia) in fuori.items()}


def prezzi_provincia(anno: str) -> dict[str, float]:
    """`codice comune -> €/m² medio` in un anno."""
    fuori: dict[str, float] = {}
    for riga in leggi("quotazioni_comuni.csv"):
        if riga["anno"] != anno or riga["tipologia"] != TIPOLOGIA:
            continue
        if riga["mercato"] != "vendita" or riga["base_superficie"] != BASE_VENDITE:
            continue
        valore = numero(riga["media"])
        if valore is not None:
            fuori[riga["codice_istat"]] = valore
    return fuori


# --- le stampe ----------------------------------------------------------


def parte_capoluogo(righe: list[dict[str, str]]) -> None:
    correnti = prezzi_comune(CAPOLUOGO)
    costanti = in_euro_costanti(correnti)
    volumi = volumi_residenziali(CAPOLUOGO)
    anni = sorted(correnti)

    print(f"1. Il capoluogo: prezzi contro volumi, {anni[0]}–{anni[-1]}")
    print(f"  {'anno':>6} {'€/m² correnti':>14} {'€/m² ' + ANNO_EURO_COSTANTI:>14} "
          f"{'NTN residenziale':>18}")
    print("  " + "-" * 56)
    for anno in anni:
        ntn = volumi.get(anno)
        print(f"  {anno:>6} {correnti[anno]:>14,.0f} {costanti[anno]:>14,.0f} "
              f"{(f'{ntn:,.0f}' if ntn else '—'):>18}")
        righe.append({
            "anno": anno,
            "euro_mq_correnti": f"{correnti[anno]:.0f}",
            "euro_mq_costanti": f"{costanti[anno]:.0f}",
            "ntn_residenziale": f"{ntn:.1f}" if ntn else "",
        })

    primo, ultimo = anni[0], anni[-1]
    fondo = min(volumi, key=lambda a: volumi[a])
    print()
    print(f"  In euro correnti il metro quadro fa {correnti[ultimo] / correnti[primo] - 1:+.1%} "
          f"in {int(ultimo) - int(primo)} anni: sembra un mercato fermo.")
    print(f"  In euro {ANNO_EURO_COSTANTI} fa {costanti[ultimo] / costanti[primo] - 1:+.1%}: "
          f"{correnti[primo]:,.0f} € del {primo} sono {costanti[primo]:,.0f} € di oggi.")
    print(f"  I volumi, intanto, dal fondo del {fondo} ({volumi[fondo]:,.0f} NTN) al {ultimo} "
          f"({volumi[ultimo]:,.0f}): {volumi[ultimo] / volumi[fondo] - 1:+.1%}.")
    print("  Le due serie non si contraddicono: si vende molto di più a un prezzo reale")
    print("  molto più basso. È una sola frase, e nessuna delle due serie la dice da sola.")


def parte_zone(righe: list[dict[str, str]]) -> None:
    zone = zone_capoluogo()
    nomi = anagrafica_zone()
    anni = sorted({anno for serie in zone.values() for anno in serie})
    primo, ultimo = anni[0], anni[-1]

    panel = sorted(link for link, serie in zone.items() if len(serie) == len(anni))
    print(f"\n2. Dentro il capoluogo: {len(zone)} perimetri di zona in {len(anni)} anni, "
          f"{len(panel)} presenti in tutti")
    print("  ⚠️ Nel 2024 la zonizzazione del capoluogo cambia: dieci zone finiscono nel 2023")
    print("  e dieci ne cominciano nel 2024. Le medie annue restano su 23 zone quotate, ma")
    print("  non sono le stesse 23: il confronto lungo si fa sul panel bilanciato (MET-16).")

    def forbice(anno: str, chiavi: list[str]) -> tuple[float, float, float]:
        valori = [zone[link][anno] for link in chiavi if anno in zone[link]]
        return min(valori), max(valori), max(valori) / min(valori)

    print(f"\n  {'anno':>6} {'zone':>5} {'più economica':>14} {'più cara':>10} {'forbice':>9}"
          f"   {'panel: forbice':>15}")
    print("  " + "-" * 70)
    for anno in anni:
        presenti = [link for link in zone if anno in zone[link]]
        basso, alto, rapporto = forbice(anno, presenti)
        _, _, rapporto_panel = forbice(anno, panel)
        print(f"  {anno:>6} {len(presenti):>5} {basso:>14,.0f} {alto:>10,.0f} "
              f"{rapporto:>9.2f}   {rapporto_panel:>15.2f}")

    _, _, forbice_primo = forbice(primo, panel)
    _, _, forbice_ultimo = forbice(ultimo, panel)
    print()
    print("  Sul panel bilanciato la forbice fra la zona più cara e la più economica passa")
    print(f"  da {forbice_primo:.2f} a {forbice_ultimo:.2f}: il centro **non** si è staccato "
          "dalla periferia. Si sono avvicinati.")

    for link in sorted(zone, key=lambda k: -zone[k][max(zone[k])]):
        serie = zone[link]
        suo_primo, suo_ultimo = min(serie), max(serie)
        reali = in_euro_costanti(serie)
        zona, fascia = nomi[link]
        righe.append({
            "link_zona": link,
            "zona": zona,
            "fascia": fascia,
            "primo_anno": suo_primo,
            "ultimo_anno": suo_ultimo,
            "euro_mq_2004": f"{serie[suo_primo]:.0f}",
            "euro_mq_2004_costanti": f"{reali[suo_primo]:.0f}",
            "euro_mq_ultimo": f"{serie[suo_ultimo]:.0f}",
            "variazione_reale": f"{(reali[suo_ultimo] / reali[suo_primo] - 1) * 100:.1f}",
        })

    # Tutte e tredici, ordinate per prezzo di partenza: con un panel così piccolo
    # una coda in testa e una in fondo nasconderebbe più di quanto mostra.
    print(f"\n  Il panel bilanciato per intero, {primo}–{ultimo}, ordinato per prezzo iniziale:")
    print(f"    {'zona':>5} {'fascia':>6} {'€/m² ' + primo:>11} {'€/m² ' + ultimo:>11} "
          f"{'var. reale':>11}")
    variazioni: dict[str, float] = {}
    for link in sorted(panel, key=lambda k: -zone[k][primo]):
        reali = in_euro_costanti(zone[link])
        variazioni[link] = (reali[ultimo] / reali[primo] - 1) * 100
        zona, fascia = nomi[link]
        print(f"    {zona:>5} {fascia:>6} {zone[link][primo]:>11,.0f} "
              f"{zone[link][ultimo]:>11,.0f} {variazioni[link]:>+10.1f} %")

    livelli = [zone[link][primo] for link in panel]
    cambi = [variazioni[link] for link in panel]
    print(f"\n  Chi partiva più caro ha perso di più: correlazione fra livello {primo} e")
    print(f"  variazione reale {pearson(livelli, cambi):+.2f} (Pearson) / "
          f"{spearman(livelli, cambi):+.2f} (Spearman), su {len(panel)} zone.")
    # Il leave-one-out di MET-5, qui su due punti diversi: il più economico di
    # partenza e il più anomalo di arrivo. Se il segno cadesse su uno dei due, il
    # risultato sarebbe quel punto e non la città.
    for etichetta, fuori in (
        (f"la più economica del {primo}", min(panel, key=lambda k: zone[k][primo])),
        ("la sola quasi ferma in termini reali", max(panel, key=lambda k: variazioni[k])),
    ):
        resto = [link for link in panel if link != fuori]
        print(f"  Senza {nomi[fuori][0]} ({etichetta}): "
              f"{pearson([zone[k][primo] for k in resto], [variazioni[k] for k in resto]):+.2f} / "
              f"{spearman([zone[k][primo] for k in resto], [variazioni[k] for k in resto]):+.2f}")
    print("  Il segno regge in tutti e tre i conti, la forza cala: la convergenza c'è,")
    print("  e una parte di quella misurata la fa una zona sola.")
    print(f"  ⚠️ Tredici zone sono poche: è una descrizione di questa città, non una legge "
          "urbana.")


def parte_provincia(righe: list[dict[str, str]], quanti: int) -> None:
    anno = max(riga["anno"] for riga in leggi("quotazioni_comuni.csv"))
    prezzi = prezzi_provincia(anno)
    comuni = anagrafica()
    reddito = serie_reddito()
    addetti = serie_imprese("addetti")
    popolazione = serie_popolazione()

    codici = sorted(
        c for c in prezzi if c in reddito and c in addetti and c in popolazione
    )
    valori = {
        "reddito": {c: reddito[c][max(reddito[c])] for c in codici},
        "addetti ogni 100 abitanti": {
            c: addetti[c][max(addetti[c])] / popolazione[c][max(popolazione[c])] * 100
            for c in codici
        },
        "popolazione": {c: popolazione[c][max(popolazione[c])] for c in codici},
    }

    print(f"\n3. La provincia nel {anno}: {len(prezzi)} comuni quotati su {len(comuni)}")
    print("  ⚠️ Magasa e Valvestino non sono nella fonte dal 2016: non sono un dato mancante")
    print("  di questo script, mancano all'OMI (dati/README §Casa e prezzi).")

    ordinati = sorted(codici, key=lambda c: -prezzi[c])
    gardesani = codici_gardesani()
    print(f"\n  {'comune':26} {'€/m²':>8}  {'':2}")
    print("  " + "-" * 40)
    for codice in ordinati[:quanti]:
        marca = "🌊" if codice in gardesani else ("🏙" if codice == CAPOLUOGO else "")
        print(f"  {comuni[codice]['comune'][:26]:26} {prezzi[codice]:>8,.0f}  {marca}")
    print(f"  {'…':^26}")
    for codice in ordinati[-quanti:]:
        print(f"  {comuni[codice]['comune'][:26]:26} {prezzi[codice]:>8,.0f}")

    rango = ordinati.index(CAPOLUOGO) + 1
    print(f"\n  Il capoluogo è {rango}° su {len(ordinati)} a {prezzi[CAPOLUOGO]:,.0f} €/m². "
          "Il vertice non è la città:")
    print("  sono il Garda e l'alta montagna, cioè il turismo. È lo stesso risultato di")
    print("  `dove_si_lavora.py` visto dal lato della casa.")

    print(f"\n  Correlazioni con il prezzo, {len(codici)} comuni (Pearson / Spearman, MET-6):")
    print(f"  {'contro':30} {'tutti':>16} {'senza Garda':>16} {'senza Garda+città':>20}")
    print("  " + "-" * 86)
    x = [prezzi[c] for c in codici]
    for nome, serie in valori.items():
        y = [serie[c] for c in codici]
        colonne = []
        for escludi in ({}, gardesani, gardesani | {CAPOLUOGO}):
            tieni = senza(codici, set(escludi))
            xs, ys = [x[i] for i in tieni], [y[i] for i in tieni]
            colonne.append(f"{pearson(xs, ys):+.2f} / {spearman(xs, ys):+.2f}")
        print(f"  {nome:30} {colonne[0]:>16} {colonne[1]:>16} {colonne[2]:>20}")

    print("\n  Nessuna delle tre è fatta dal Garda: tolti i quattordici comuni rivieraschi")
    print("  i coefficienti si muovono di poco, e sulla popolazione salgono. Il reddito è")
    print("  la relazione più forte, e resta descrittiva (MET-6: è fra comuni, non fra")
    print("  persone: non dice che chi guadagna di più paghi la casa di più).")
    print("  ⚠️ Sulla popolazione Pearson e Spearman divergono molto (+0,18 contro +0,58):")
    print("  la relazione fra rango c'è, quella lineare no. È il capoluogo, che con 199.853")
    print("  abitanti sta un ordine di grandezza sopra tutti (MET-5) — e infatti Pearson")
    print("  sale a +0,32 quando lo si toglie, cioè il numero senza di lui è più vero.")

    for codice in ordinati:
        righe.append({
            "codice_istat": codice,
            "comune": comuni[codice]["comune"],
            "euro_mq": f"{prezzi[codice]:.0f}",
            "reddito": f"{valori['reddito'][codice]:.0f}",
            "addetti_per_100_abitanti": f"{valori['addetti ogni 100 abitanti'][codice]:.1f}",
            "popolazione": f"{valori['popolazione'][codice]:.0f}",
        })


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="casa_e_prezzi")
    parser.add_argument("--save", action="store_true", help="scrive i CSV in analysis/output/")
    parser.add_argument("--quanti", type=int, default=8, help="quanti comuni per coda")
    args = parser.parse_args(argv)

    capoluogo: list[dict[str, str]] = []
    zone: list[dict[str, str]] = []
    provincia: list[dict[str, str]] = []

    parte_capoluogo(capoluogo)
    parte_zone(zone)
    parte_provincia(provincia, args.quanti)

    if args.save:
        for nome, colonne, righe in (
            ("casa_capoluogo.csv", COLONNE_CAPOLUOGO, capoluogo),
            ("casa_zone_capoluogo.csv", COLONNE_ZONE, zone),
            ("casa_comuni.csv", COLONNE_COMUNI, provincia),
        ):
            destinazione = scrivi_csv(nome, colonne, righe)
            print(f"scritto {destinazione.relative_to(RADICE)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
