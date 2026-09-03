"""Il turismo bresciano, confrontato con le altre 106 province italiane.

    python analysis/confronto_turismo.py
    python analysis/confronto_turismo.py --save

Era l'ultimo dei quattro assi senza un altrove. Imprese, redditi e popolazione
sanno dire se una cifra bresciana sia bresciana o italiana; il turismo no,
perché la sua fonte si ferma al confine lombardo. `turismo_province.csv` porta
la stessa misura su tutte e 107 le province dal 2008, e permette di chiedere
alla provincia di Brescia la domanda che MET-14 impone: *undici milioni di
presenze sono tante?*

Cinque letture:

1. **Dove sta Brescia nella distribuzione** delle 107 province su otto
   indicatori: valore, rango, mediana. Un rango a metà classifica è un
   risultato, non un fallimento.
2. **La serie lunga 2008–2024**, che la fonte regionale non aveva: Brescia
   contro l'Italia e contro la provincia mediana.
3. **La composizione**, cioè cosa distingue davvero questa provincia: non
   quanto turismo ha, ma di che tipo è.
4. **Il 2020 e il recupero**, per collocare la rottura che `rottura_covid.py`
   misura sull'occupazione.
5. **Il controllo fra le due fonti** (MET-17): la somma dei comuni di Regione
   Lombardia contro il totale provinciale ISTAT, anno per anno.

⚠️ Tre vincoli che questo script fa rispettare per costruzione, e che chiunque
riusi la tabella deve rispettare a mano:

- **l'ultimo anno confrontabile è il 2024.** Il 2025 c'è, ma dentro ha una
  definizione cambiata (`stato = definizione_cambiata`) e non si mette in una
  serie storica;
- **la Sardegna esce dai confronti pluriennali** che attraversano il 2017: le
  sue province hanno cambiato territorio (`stato = confine_cambiato`);
- **le due fonti sul turismo non si mescolano in una frase.** Il confronto fra
  province sta tutto nella tabella ISTAT, i comuni tutti in quella regionale, e
  il §5 misura quanto distano invece di far finta che coincidano.

Confidenza: `derivato` (MET-4).
"""

from __future__ import annotations

import argparse
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _tabelle import RADICE, leggi, numero, scrivi_csv, tasso_annualizzato  # noqa: E402

BRESCIA = "017"
BERGAMO = "016"  # la gemella, come in `confronto_province.py`

# L'ultimo anno con la stessa definizione degli anni prima. Il 2025 esiste nella
# tabella ed è marcato: vedi il docstring.
ULTIMO_CONFRONTABILE = "2024"
PRIMO = "2008"
PRIMA_DEL_COVID = "2019"

COLONNE = ["indicatore", "codice_provincia", "provincia", "valore", "rango", "province", "mediana"]


# --- lettura ------------------------------------------------------------


def carica() -> tuple[dict, dict[str, str], dict[str, str]]:
    """`(valori, nomi, regioni)` per le sole province, escluse le righe marcate.

    Le righe con `stato` diverso da `osservato` non entrano: sono i due casi in
    cui il numero è giusto ma non confrontabile, e lasciarli passare qui
    significherebbe ricordarsi di escluderli in ognuno dei cinque paragrafi.
    """
    valori: dict[tuple[str, str, str, str, str], float] = {}
    nomi: dict[str, str] = {}
    regioni: dict[str, str] = {}
    for riga in leggi("turismo_province.csv"):
        if riga["livello"] != "provincia" or riga["stato"] != "osservato":
            continue
        valore = numero(riga["valore"])
        if valore is None:
            continue
        codice = riga["codice_provincia"]
        nomi[codice] = riga["territorio"]
        regioni[codice] = riga["regione"]
        valori[(codice, riga["anno"], riga["tipologia"], riga["residenza"], riga["indicatore"])] = (
            valore
        )
    return valori, nomi, regioni


def popolazione_province() -> dict[tuple[str, str], float]:
    return {
        (riga["codice_provincia"], riga["anno"]): float(riga["valore"])
        for riga in leggi("bilancio_province.csv")
        if riga["indicatore"] == "popolazione_censita"
    }


# --- statistica ---------------------------------------------------------


def collocazione(valori_per_provincia: dict[str, float], codice: str, alto_e_primo: bool = True):
    """`(valore, rango, quante, mediana)`. Rango 1 = il più alto, se `alto_e_primo`."""
    ordinate = sorted(valori_per_provincia, key=lambda c: valori_per_provincia[c], reverse=alto_e_primo)
    return (
        valori_per_provincia[codice],
        ordinate.index(codice) + 1,
        len(ordinate),
        statistics.median(valori_per_provincia.values()),
    )


def rapporto(valori: dict, numeratore: tuple, denominatore: tuple, per_cento: bool = True):
    sopra, sotto = valori.get(numeratore), valori.get(denominatore)
    if sopra is None or not sotto:
        return None
    return sopra / sotto * (100 if per_cento else 1)


# --- le cinque letture ---------------------------------------------------


def indicatori(valori: dict, nomi: dict, pop: dict, anno: str) -> dict[str, dict[str, float]]:
    """Per ogni indicatore, il valore di ciascuna provincia nell'anno dato."""
    def presenze(c: str, tipologia: str = "totale", residenza: str = "totale"):
        return valori.get((c, anno, tipologia, residenza, "presenze"))

    fuori: dict[str, dict[str, float]] = {k: {} for k in (
        "presenze",
        "presenze per abitante",
        "quota di presenze straniere (%)",
        "permanenza media (notti)",
        "quota alberghiera (%)",
        "quota in campeggi e villaggi (%)",
        "crescita delle presenze 2019-2024 (%)",
        "caduta delle presenze nel 2020 (%)",
    )}

    for codice in nomi:
        totale = presenze(codice)
        if totale is None:
            continue
        fuori["presenze"][codice] = totale

        abitanti = pop.get((codice, anno))
        if abitanti:
            fuori["presenze per abitante"][codice] = totale / abitanti

        for etichetta, tipologia in (
            ("quota alberghiera (%)", "alberghiero"),
            ("quota in campeggi e villaggi (%)", "campeggi e villaggi"),
        ):
            quota = rapporto(valori, (codice, anno, tipologia, "totale", "presenze"),
                             (codice, anno, "totale", "totale", "presenze"))
            if quota is not None:
                fuori[etichetta][codice] = quota

        estera = rapporto(valori, (codice, anno, "totale", "estero", "presenze"),
                          (codice, anno, "totale", "totale", "presenze"))
        if estera is not None:
            fuori["quota di presenze straniere (%)"][codice] = estera

        notti = rapporto(valori, (codice, anno, "totale", "totale", "presenze"),
                         (codice, anno, "totale", "totale", "arrivi"), per_cento=False)
        if notti is not None:
            fuori["permanenza media (notti)"][codice] = notti

        base = presenze(codice)
        prima = valori.get((codice, PRIMA_DEL_COVID, "totale", "totale", "presenze"))
        if base and prima:
            fuori["crescita delle presenze 2019-2024 (%)"][codice] = (base / prima - 1) * 100
        durante = valori.get((codice, "2020", "totale", "totale", "presenze"))
        if durante and prima:
            fuori["caduta delle presenze nel 2020 (%)"][codice] = (durante / prima - 1) * 100

    return fuori


def stampa_distribuzione(fuori: dict, nomi: dict, righe_csv: list) -> None:
    print(f"1. Dove sta Brescia fra le 107 province, {ULTIMO_CONFRONTABILE}\n")
    print(f"   {'indicatore':38} {'Brescia':>12} {'mediana':>12} {'rango':>10}   testa della classifica")
    for etichetta, per_provincia in fuori.items():
        if BRESCIA not in per_provincia:
            continue
        # La caduta del 2020 è un numero negativo: «prima» vuol dire «più
        # profonda», e ordinarla come le altre direbbe il contrario.
        alto_e_primo = "caduta" not in etichetta
        valore, rango, quante, med = collocazione(per_provincia, BRESCIA, alto_e_primo)
        decimali = 0 if etichetta == "presenze" else 2
        testa = sorted(per_provincia, key=lambda c: per_provincia[c], reverse=alto_e_primo)[:3]
        print(f"   {etichetta:38} {valore:>12,.{decimali}f} {med:>12,.{decimali}f} "
              f"{f'{rango}ª/{quante}':>10}   " + ", ".join(nomi[c] for c in testa))
        for codice, v in per_provincia.items():
            _, r, q, _ = collocazione(per_provincia, codice, alto_e_primo)
            righe_csv.append({
                "indicatore": etichetta, "codice_provincia": codice, "provincia": nomi[codice],
                "valore": f"{v:.3f}", "rango": r, "province": q, "mediana": f"{med:.3f}",
            })
    print()


def stampa_serie_lunga(valori: dict, nomi: dict, regioni: dict) -> None:
    print(f"2. La serie lunga {PRIMO}–{ULTIMO_CONFRONTABILE}, che la fonte regionale non aveva\n")

    def presenze(c: str, anno: str):
        return valori.get((c, anno, "totale", "totale", "presenze"))

    # La Sardegna esce: le sue province hanno cambiato territorio nel 2017, e
    # una crescita calcolata su quelle serie è una crescita di superficie.
    sarde = [c for c in nomi if regioni[c] == "Sardegna"]
    # Le province istituite dopo il 2008 (Monza e della Brianza, Fermo,
    # Barletta-Andria-Trani) entrano nella fonte solo dal 2010: senza il primo
    # anno la crescita non è calcolabile, e inventarne uno sarebbe peggio.
    senza_primo = [c for c in nomi if c not in sarde and not presenze(c, PRIMO)]
    confrontabili = [
        c for c in nomi
        if c not in sarde and c not in senza_primo and presenze(c, ULTIMO_CONFRONTABILE)
    ]
    crescite = {
        c: tasso_annualizzato(presenze(c, PRIMO), presenze(c, ULTIMO_CONFRONTABILE), 16)
        for c in confrontabili
    }
    crescite = {c: v for c, v in crescite.items() if v is not None}
    valore, rango, quante, med = collocazione(crescite, BRESCIA)
    print(f"   {len(confrontabili)} province con la serie intera. Fuori {len(sarde)} sarde "
          f"(confine cambiato nel 2017)")
    print(f"   e {len(senza_primo)} istituite dopo il {PRIMO} ("
          + ", ".join(sorted(nomi[c] for c in senza_primo)) + ").")
    print(f"   Brescia: {presenze(BRESCIA, PRIMO):,.0f} presenze nel {PRIMO}, "
          f"{presenze(BRESCIA, ULTIMO_CONFRONTABILE):,.0f} nel {ULTIMO_CONFRONTABILE} "
          f"({valore:+.2f} %/anno).")
    print(f"   Mediana provinciale: {med:+.2f} %/anno. Brescia è {rango}ª su {quante}.")
    if BERGAMO in crescite:
        print(f"   Bergamo, la gemella: {crescite[BERGAMO]:+.2f} %/anno.")
    print()

    print(f"   {'anno':6} {'Brescia':>12} {'indice 2008=100':>16} {'quota estera':>14}")
    for anno in [str(a) for a in range(int(PRIMO), int(ULTIMO_CONFRONTABILE) + 1)]:
        v = presenze(BRESCIA, anno)
        if v is None:
            continue
        estera = rapporto(valori, (BRESCIA, anno, "totale", "estero", "presenze"),
                          (BRESCIA, anno, "totale", "totale", "presenze"))
        indice = v / presenze(BRESCIA, PRIMO) * 100
        print(f"   {anno:6} {v:>12,.0f} {indice:>16.1f} {estera:>13.1f} %")
    print()


def stampa_composizione(fuori: dict, nomi: dict) -> None:
    print("3. Non quanto turismo, ma di che tipo\n")
    quota_campeggi = fuori["quota in campeggi e villaggi (%)"]
    quota_estera = fuori["quota di presenze straniere (%)"]
    v_c, r_c, q_c, m_c = collocazione(quota_campeggi, BRESCIA)
    v_e, r_e, q_e, m_e = collocazione(quota_estera, BRESCIA)
    print(f"   In campeggi e villaggi: {v_c:.1f} % delle presenze contro una mediana "
          f"del {m_c:.1f} % ({r_c}ª su {q_c}).")
    print(f"   Dall'estero: {v_e:.1f} % contro {m_e:.1f} % ({r_e}ª su {q_e}).")
    sopra = sorted(
        (c for c in quota_estera if quota_estera[c] > quota_estera[BRESCIA]),
        key=lambda c: -quota_estera[c],
    )
    print(f"   Le province più internazionali di Brescia sono {len(sopra)}: "
          + ", ".join(f"{nomi[c]} ({quota_estera[c]:.1f} %)" for c in sopra) + ".")
    print()


def stampa_covid(fuori: dict, valori: dict, nomi: dict) -> None:  # noqa: D103
    print("4. Il 2020, e quanto ci è voluto\n")
    caduta = fuori["caduta delle presenze nel 2020 (%)"]
    ripresa = fuori["crescita delle presenze 2019-2024 (%)"]
    v_c, r_c, q_c, m_c = collocazione(caduta, BRESCIA, alto_e_primo=False)
    v_r, r_r, q_r, m_r = collocazione(ripresa, BRESCIA)
    print(f"   Caduta 2020: {v_c:+.1f} % contro una mediana del {m_c:+.1f} % "
          f"({r_c}ª caduta più profonda su {q_c}).")
    print(f"   Recupero 2019→2024: {v_r:+.1f} % contro {m_r:+.1f} % ({r_r}ª su {q_r}).")

    def presenze(c: str, anno: str):
        return valori.get((c, anno, "totale", "totale", "presenze"))

    sopra_il_2019 = [c for c in nomi if presenze(c, PRIMA_DEL_COVID) and presenze(c, ULTIMO_CONFRONTABILE)
                     and presenze(c, ULTIMO_CONFRONTABILE) > presenze(c, PRIMA_DEL_COVID)]
    print(f"   Province tornate sopra il 2019: {len(sopra_il_2019)} su {len(nomi)}. "
          f"Brescia {'sì' if BRESCIA in sopra_il_2019 else 'no'}.\n")


def stampa_due_fonti(valori: dict) -> None:
    print("5. Le due fonti non danno lo stesso numero (MET-17)\n")
    regionale: dict[str, float] = {}
    for riga in leggi("turismo_comuni_annuale.csv"):
        if riga["tipo_struttura"] != "Totale" or riga["cittadinanza"] != "Totale":
            continue
        if riga["stato"] != "osservato":
            continue
        v = numero(riga["presenze"])
        if v is not None:
            regionale[riga["anno"]] = regionale.get(riga["anno"], 0.0) + v

    print(f"   {'anno':6} {'ISTAT provincia':>16} {'somma dei comuni':>18} {'scarto':>9}")
    for anno in sorted(regionale):
        istat = valori.get((BRESCIA, anno, "totale", "totale", "presenze"))
        if not istat:
            continue
        print(f"   {anno:6} {istat:>16,.0f} {regionale[anno]:>18,.0f} "
              f"{(regionale[anno] / istat - 1) * 100:>8.1f} %")
    print("\n   Lo scarto **cresce**: 6,5 % nel 2019, 10,6 % nel 2024. La somma dei comuni")
    print("   esclude per giunta i comuni con dato riservato, quindi la distanza vera è")
    print("   più ampia. Sono due rilevazioni dello stesso fenomeno, non una sbagliata:")
    print("   la conseguenza è MET-17, una tabella una fonte.\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--save", action="store_true", help="scrive analysis/output/")
    args = parser.parse_args(argv)

    valori, nomi, regioni = carica()
    pop = popolazione_province()
    fuori = indicatori(valori, nomi, pop, ULTIMO_CONFRONTABILE)

    righe_csv: list[dict[str, str]] = []
    print(f"Il turismo bresciano fra le province italiane — {len(nomi)} province, "
          f"{PRIMO}–{ULTIMO_CONFRONTABILE}\n")
    stampa_distribuzione(fuori, nomi, righe_csv)
    stampa_serie_lunga(valori, nomi, regioni)
    stampa_composizione(fuori, nomi)
    stampa_covid(fuori, valori, nomi)
    stampa_due_fonti(valori)

    if args.save:
        destinazione = scrivi_csv("confronto_turismo.csv", COLONNE, righe_csv)
        print(f"scritto {destinazione.relative_to(RADICE)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
