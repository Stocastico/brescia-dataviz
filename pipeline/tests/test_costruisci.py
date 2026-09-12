"""Il costruttore del sito (`sito/costruisci.py`).

Ottocento righe che stavano senza rete. È il programma che decide **ogni numero
che il lettore vede**: `cifre()` ne calcola più di duecento, e ciascuno finisce
in una frase come `{{c:nome}}`. Un errore qui non fa cadere niente — produce una
pagina con dentro un numero sbagliato, che è il modo peggiore in cui questo
progetto può rompersi.

I test sono di tre tipi, e il terzo è quello che vale:

1. **le funzioni pure**, con risposte note a mano (mediana, Pearson, i numeri
   in italiano) e con le proprietà che le regole del progetto impongono;
2. **i costruttori dei dati dei grafici** (`casa`, `clima`, `decomposizione`…),
   verificati sulle proprietà che devono valere sempre — serie della stessa
   lunghezza dei periodi, indici che partono da 100, forbici positive;
3. **la costruzione intera**, in una cartella temporanea, con le due condizioni
   che la CI controlla dopo: nessun segnaposto rimasto e nessuna lineetta lunga
   nel testo. Qui girano insieme al resto invece che come due comandi separati.
"""

from __future__ import annotations

import json
import re

import pytest

from conftest import servono_tabelle

import costruisci as C

pytestmark = servono_tabelle

SEGNAPOSTO = re.compile(r"\{\{(c:[a-z0-9_]+|BUILD_DATE|DATA_DATE|N_[A-Z]+|STILE|GRAFICI|FIGURE|DATI|BLOCCHI_TABELLE)\}\}")


# --- le funzioni pure ----------------------------------------------------


def test_la_mediana_su_dispari_e_su_pari() -> None:
    assert C.mediana([3.0, 1.0, 2.0]) == 2.0
    assert C.mediana([4.0, 1.0, 3.0, 2.0]) == 2.5
    assert C.mediana([7.0]) == 7.0


def test_la_mediana_ordina_da_se() -> None:
    """Chiamata su una lista già ordinata o meno, deve dare lo stesso numero."""
    lista = [9.0, 1.0, 5.0, 3.0, 7.0]
    assert C.mediana(lista) == C.mediana(sorted(lista))


def test_pearson_su_punti_allineati_fa_uno_e_su_una_costante_fa_zero() -> None:
    x = [1.0, 2.0, 3.0, 4.0]
    assert C.pearson(x, [3 * v for v in x]) == pytest.approx(1.0)
    # Qui, a differenza di `_tabelle.pearson`, il ripiego è 0.0 e non `None`:
    # sono due implementazioni indipendenti apposta, e questo test fissa la
    # differenza invece di lasciarla scoprire a qualcuno fra sei mesi.
    assert C.pearson([1.0, 1.0, 1.0], [1.0, 2.0, 3.0]) == 0.0


def test_i_numeri_si_scrivono_in_italiano() -> None:
    """Punto per le migliaia, virgola per i decimali: è la lingua della pagina."""
    assert C.numero_it(1234567) == "1.234.567"
    assert C.numero_it(1234.5, 1) == "1.234,5"
    assert C.numero_it(-30.77, 2) == "-30,77"
    assert C.numero_it(0) == "0"


def test_le_percentuali_non_mettono_il_segno_piu_da_sole() -> None:
    """Il `+` lo aggiunge chi chiama, dove il segno è parte della notizia
    (`+2,3 %` in ventun anni). Questa funzione formatta e basta, e il test lo
    fissa perché la differenza fra le due cose non è ovvia leggendo il nome."""
    assert C.percento_it(2.3) == "2,3\u00a0%"
    assert C.percento_it(-30.8) == "-30,8\u00a0%"
    assert C.percento_it(0.0) == "0,0\u00a0%"


def test_lo_spazio_prima_del_percento_non_manda_a_capo() -> None:
    """Uno spazio normale lascia che il `%` scenda di riga da solo, staccato dal
    numero: succedeva nel titolo della storia dei salari. Lo spazio unificatore
    è anche la convenzione tipografica italiana, quindi la resa giusta e il
    comportamento giusto sono la stessa scelta."""
    assert " " not in C.percento_it(25.4)
    assert C.percento_it(25.4) == "25,4" + C.PERCENTO


# --- la contiguità e Moran -----------------------------------------------


def test_la_contiguita_non_lascia_nessun_comune_isolato() -> None:
    """Il controllo di sanità della matrice: se un comune non confina con
    nessuno, il GeoJSON o la soglia di arrotondamento sono cambiati."""
    vicini = C.contiguita()
    assert len(vicini) == 205
    isolati = [c for c, v in vicini.items() if not v]
    assert not isolati, f"comuni senza vicini: {isolati}"


def test_la_contiguita_e_simmetrica() -> None:
    """Se A confina con B, B confina con A. Non è garantito da come è costruita:
    lo è solo se i vertici condivisi sono davvero lo stesso punto."""
    vicini = C.contiguita()
    for uno, altri in vicini.items():
        for altro in altri:
            assert uno in vicini[altro], f"{uno}->{altro} ma non il contrario"


def test_il_grado_medio_e_quello_di_una_provincia_vera() -> None:
    vicini = C.contiguita()
    grado = sum(len(v) for v in vicini.values()) / len(vicini)
    assert 4 < grado < 7, f"grado medio {grado:.2f}"


def test_moran_su_un_indicatore_costante_e_zero() -> None:
    """Senza varianza non c'è autocorrelazione da misurare."""
    vicini = C.contiguita()
    assert C.moran({c: 1.0 for c in vicini}) == 0.0


def test_moran_su_pochi_comuni_non_esplode() -> None:
    assert C.moran({}) == 0.0


def test_moran_sulla_crescita_e_positivo_e_sotto_uno() -> None:
    """La prima storia poggia su questo numero: i comuni che si svuotano
    confinano fra loro."""
    metrica = C.leggi_metrica("crescita_popolazione")
    assert metrica is not None
    indice = C.moran(C.valori(metrica))
    assert 0.1 < indice < 1.0, indice


# --- i costruttori dei dati dei grafici ----------------------------------


def test_casa_produce_serie_allineate_ai_loro_anni() -> None:
    casa = C.casa()
    assert casa, "casa() non ha trovato le tabelle OMI"
    assert len(casa["correnti"]) == len(casa["anni"])
    assert len(casa["reali"]) == len(casa["anni"])
    assert len(casa["ntn"]) == len(casa["anni_ntn"])
    assert len(casa["indice_reale"]) == len(casa["anni_ntn"])
    assert len(casa["indice_ntn"]) == len(casa["anni_ntn"])


def test_le_due_serie_del_capoluogo_si_toccano_nellultimo_anno() -> None:
    """In euro dell'ultimo anno non c'è niente da scontare: le due curve
    coincidono lì per costruzione, ed è la chiave di lettura del grafico."""
    casa = C.casa()
    assert casa["correnti"][-1] == pytest.approx(casa["reali"][-1], abs=0.5)
    assert casa["anno_base_reale"] == casa["anni"][-1]


def test_gli_indici_partono_da_cento() -> None:
    casa = C.casa()
    assert casa["indice_reale"][0] == pytest.approx(100.0)
    assert casa["indice_ntn"][0] == pytest.approx(100.0)


def test_il_prezzo_reale_del_passato_e_sopra_quello_corrente() -> None:
    """Con inflazione positiva, deflazionare alza i valori del passato."""
    casa = C.casa()
    assert casa["reali"][0] > casa["correnti"][0]


def test_le_zone_stanno_sul_panel_bilanciato_e_la_forbice_si_stringe() -> None:
    zone = C.casa()["zone"]
    assert zone["quante_panel"] <= zone["quante_ultimo"]
    assert len(zone["forbice_panel"]) == len(zone["anni"])
    assert all(f > 1 for f in zone["forbice_panel"]), "una forbice non può stare sotto 1"
    assert zone["forbice_panel"][-1] < zone["forbice_panel"][0]
    # l'ottava storia dice che le tre linee sono ordinate, sempre
    for alto, mezzo, basso in zip(zone["alta"], zone["mediana"], zone["bassa"]):
        assert alto >= mezzo >= basso


def test_le_zone_agli_estremi_sono_nominate_anno_per_anno() -> None:
    """MET-21: la linea del minimo è un inviluppo, e ogni punto deve dire da
    quale zona viene."""
    zone = C.casa()["zone"]
    assert len(zone["alta_zona"]) == len(zone["anni"])
    assert len(zone["bassa_zona"]) == len(zone["anni"])
    assert zone["quante_zone_in_cima"] == len(set(zone["alta_zona"]))
    assert zone["quante_zone_in_fondo"] == len(set(zone["bassa_zona"]))
    assert all(z for z in zone["alta_zona"] + zone["bassa_zona"])


def test_la_forbice_a_zone_fisse_e_il_controllo_dellinviluppo() -> None:
    """Se le due letture divergessero, «la forbice si stringe» dipenderebbe da
    quale zona sta in fondo e non dal mercato."""
    zone = C.casa()["zone"]
    assert len(zone["forbice_fissa"]) == len(zone["anni"])
    assert zone["forbice_fissa"][0] == pytest.approx(zone["forbice_panel"][0], abs=0.01)
    assert zone["forbice_fissa"][-1] == pytest.approx(zone["forbice_panel"][-1], abs=0.01)


def test_lindice_dei_prezzi_e_crescente_e_raccordato() -> None:
    """Tre basi che non si sovrappongono, raccordate: la serie concatenata deve
    salire, e senza i due crolli del trenta per cento di MET-20."""
    indice = C.indice_prezzi()
    anni = sorted(indice)
    assert len(anni) > 20
    for prima, dopo in zip(anni, anni[1:]):
        rapporto = indice[dopo] / indice[prima]
        assert 0.98 < rapporto < 1.15, f"{prima}->{dopo}: {rapporto:.3f}"
    assert indice[anni[-1]] > indice[anni[0]]


@pytest.mark.parametrize(
    "costruttore",
    ["confronto_province", "turismo_confronto", "controllo_capoluoghi", "clima",
     "decomposizione", "scomposizione_demografica", "scomposizione_province"],
)
def test_ogni_costruttore_di_dati_torna_qualcosa_di_non_vuoto(costruttore: str) -> None:
    """Un costruttore che torna un dizionario vuoto fa sparire un grafico dalla
    pagina senza che niente fallisca."""
    fuori = getattr(C, costruttore)()
    assert isinstance(fuori, dict)
    assert fuori, f"{costruttore}() ha restituito un dizionario vuoto"


def test_il_clima_tiene_le_serie_allineate_ai_loro_anni() -> None:
    clima = C.clima()
    assert len(clima["inquinanti"]) == 3
    for inquinante in clima["inquinanti"]:
        assert len(inquinante["serie"]) == len(inquinante["anni"])
        # il panel bilanciato di MET-16: le stazioni sono nominate, non contate
        assert inquinante["stazioni"], inquinante["parametro"]
        assert all(nome.strip() for nome in inquinante["stazioni"])
        assert inquinante["unita"]


def test_le_anomalie_di_temperatura_sono_scostamenti_non_temperature() -> None:
    """MET: ogni stazione si confronta con sé stessa. Uno scostamento sta
    attorno allo zero; una temperatura media bresciana starebbe attorno a 12."""
    temperatura = C.clima()["temperatura"]
    anomalie = temperatura["anomalie"]
    assert len(anomalie) > 20
    for voce in anomalie:
        assert voce["anno"].isdigit()
        assert -5 < voce["valore"] < 5, voce
        assert voce["stazioni"] > 0
    # e le stazioni stanno a quote molto diverse, che è il motivo della scelta
    assert temperatura["quota_massima"] - temperatura["quota_minima"] > 1000
    assert 0 < temperatura["in_aumento"] <= len(temperatura["stazioni"])


def test_gli_anni_piu_caldi_stanno_in_fondo_alla_serie() -> None:
    """La frase della sesta storia, verificata invece che ripetuta."""
    anomalie = C.clima()["temperatura"]["anomalie"]
    per_valore = sorted(anomalie, key=lambda v: -v["valore"])[:3]
    anni_caldi = {v["anno"] for v in per_valore}
    ultimi = {v["anno"] for v in anomalie[-8:]}
    assert anni_caldi <= ultimi, sorted(anni_caldi)


def test_la_decomposizione_del_capoluogo_ha_divisioni_con_un_nome() -> None:
    scomposizione = C.decomposizione()
    assert scomposizione["divisioni"]
    for divisione in scomposizione["divisioni"]:
        assert divisione["nome"].strip()
        assert isinstance(divisione["variazione"], (int, float))


# --- le cifre del racconto -----------------------------------------------


@pytest.fixture(scope="module")
def contesto():
    import csv

    with (C.PROCESSED / "comuni.csv").open(encoding="utf-8") as handle:
        comuni = {r["codice_istat"]: r for r in csv.DictReader(handle)}
    metriche = {}
    for id_metrica in C.METRICHE_USATE:
        metrica = C.leggi_metrica(id_metrica)
        if metrica is not None:
            metriche[id_metrica] = metrica
    return metriche, comuni


def test_tutte_le_cifre_sono_stringhe_non_vuote(contesto) -> None:
    valori = C.cifre(*contesto)
    assert len(valori) > 150
    vuote = [k for k, v in valori.items() if not str(v).strip()]
    assert not vuote, f"cifre vuote: {vuote}"


def test_nessuna_cifra_e_nan_o_none(contesto) -> None:
    """`nan` in una frase è un numero che il lettore legge come un numero."""
    valori = C.cifre(*contesto)
    malate = [k for k, v in valori.items() if re.search(r"\b(nan|inf|None)\b", str(v), re.I)]
    assert not malate, f"cifre malate: {malate}"


def test_nessuna_cifra_contiene_una_lineetta_lunga(contesto) -> None:
    """Le cifre finiscono dentro le frasi: se ne portassero una, il test sui
    modelli non la vedrebbe."""
    valori = C.cifre(*contesto)
    colpevoli = [k for k, v in valori.items() if "—" in str(v)]
    assert not colpevoli, colpevoli


# Le percentuali della decima storia. Ogni altra storia passa da
# `percento_it()`; il blocco del confronto fra province usava `numero_it()`, e
# la pagina leggeva «il 92,7 delle unità locali» e «crescono dell'1,3 l'anno».
# Il segno di percentuale non è decorazione: senza, la cifra cambia
# significato, e il modello non può metterlo perché il racconto non scrive
# unità a mano.
CIFRE_IN_PERCENTO = (
    "ul_micro_brescia", "ul_micro_mediana", "ul_micro_bergamo",
    "ul_micro_max", "ul_micro_min",
    "addetti_micro_brescia", "addetti_micro_mediana", "addetti_micro_bergamo",
    "addetti_micro_max", "addetti_micro_min",
    "manifattura_confronto_brescia", "manifattura_confronto_mediana",
    "manifattura_confronto_bergamo", "manifattura_confronto_max",
    "manifattura_confronto_min",
    "crescita_confronto_brescia", "crescita_confronto_mediana",
    "crescita_confronto_bergamo", "crescita_confronto_max",
    "crescita_confronto_min",
)

# Gli addetti per unità locale sono addetti, non per cento: qui il segno
# sarebbe sbagliato, e il test lo dice invece di lasciarlo all'attenzione.
CIFRE_SENZA_PERCENTO = ("dimensione_brescia", "dimensione_mediana", "dimensione_bergamo")


def test_le_quote_del_confronto_fra_province_portano_il_segno_di_percento(contesto) -> None:
    valori = C.cifre(*contesto)
    nude = [k for k in CIFRE_IN_PERCENTO if k in valori and not valori[k].endswith(C.PERCENTO)]
    assert not nude, f"quote senza il percento: {nude}"


def test_gli_addetti_per_unita_locale_non_prendono_il_percento(contesto) -> None:
    valori = C.cifre(*contesto)
    sbagliate = [k for k in CIFRE_SENZA_PERCENTO if k in valori and "%" in valori[k]]
    assert not sbagliate, f"addetti scritti come percentuale: {sbagliate}"


def test_il_racconto_non_cita_cifre_che_non_esistono(contesto) -> None:
    """L'invariante che la costruzione fa valere, controllato prima di
    costruire: ogni `{{c:nome}}` nei modelli ha un valore calcolato."""
    valori = C.cifre(*contesto)
    for modello in C.PAGINE:
        sorgente = (C.MODELLI / modello).read_text(encoding="utf-8")
        citate = set(re.findall(r"\{\{c:([a-z0-9_]+)\}\}", sorgente))
        mancanti = sorted(citate - set(valori))
        assert not mancanti, f"{modello}: {mancanti}"


def test_una_cifra_mancante_fa_fallire_la_sostituzione() -> None:
    """Il controllo del controllo: senza questo, «nessun segnaposto rimasto»
    potrebbe voler dire solo che nessuno ha guardato."""
    with pytest.raises(SystemExit, match="segnaposto senza valore"):
        C.sostituisci("prima {{c:questa_non_esiste}} dopo", {}, "prova.html")


def test_la_sostituzione_mette_i_valori_al_posto_giusto() -> None:
    assert C.sostituisci("a {{c:x}} b", {"x": "42"}, "p") == "a 42 b"


# --- i dati incorporati nella pagina -------------------------------------


def test_la_geometria_compatta_resta_una_provincia(contesto) -> None:
    geo = C.geometria_compatta()
    assert len(geo["comuni"]) == 205
    for comune in geo["comuni"]:
        assert comune["c"] and comune["g"]
        for anello in comune["g"]:
            assert len(anello) >= 3
            for lon, lat in anello:
                assert 9.0 < lon < 11.5, lon
                assert 45.0 < lat < 46.7, lat


def test_i_dati_incorporati_hanno_tutto_quello_che_il_javascript_cerca(contesto) -> None:
    dati = C.dati_incorporati(*contesto)
    for chiave in ("comuni", "metriche", "geo", "casa", "clima", "decomposizione"):
        assert chiave in dati, chiave
    assert set(dati["geo"]["comuni"][0]) == {"c", "g"}
    # ogni codice della geometria esiste nell'anagrafica: è il join che, sbagliato,
    # fa sparire un comune dalla mappa in silenzio
    codici = {c["c"] for c in dati["geo"]["comuni"]}
    assert codici <= set(dati["comuni"])


def test_i_dati_incorporati_sono_serializzabili_in_json(contesto) -> None:
    """Finiscono in un `<script>`: un tipo non serializzabile romperebbe la
    pagina intera, e il primo a saperlo sarebbe il lettore."""
    testo = json.dumps(C.dati_incorporati(*contesto), ensure_ascii=False)
    assert len(testo) > 100_000


def test_la_data_dei_dati_e_una_data_iso() -> None:
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", C.data_dei_dati())


# --- la costruzione intera -----------------------------------------------


# --- il registro delle figure --------------------------------------------


@pytest.fixture(scope="module")
def racconto() -> str:
    return (C.MODELLI / "racconto.html").read_text(encoding="utf-8")


def test_le_figure_del_racconto_sono_numerate_di_seguito(racconto) -> None:
    trovate = C.figure(racconto)
    assert len(trovate) >= 15
    assert [f.numero for f in trovate] == list(range(1, len(trovate) + 1))


def test_ogni_figura_ha_un_titolo_e_almeno_un_contenitore(racconto) -> None:
    for fig in C.figure(racconto):
        assert fig.titolo.strip(), fig
        assert fig.contenitori, fig


def test_le_ancore_delle_figure_sono_tutte_diverse(racconto) -> None:
    """I rimandi «Fig. N» puntano a `#ancora`: due uguali ne romperebbero uno."""
    ancore = [f.ancora for f in C.figure(racconto)]
    assert len(set(ancore)) == len(ancore)


def test_una_figura_con_un_id_proprio_lo_tiene(racconto) -> None:
    """Due figure ce l'hanno perché il javascript le cerca per nome: se la
    numerazione lo sovrascrivesse, lo scrollytelling della casa si spegnerebbe."""
    per_ancora = {f.ancora: f for f in C.figure(racconto)}
    assert "fig-casa-prezzo" in per_ancora
    assert "fig-casa-forbice" in per_ancora


def test_una_figura_senza_titolo_ferma_la_costruzione() -> None:
    with pytest.raises(SystemExit, match="non ha un <h3>"):
        C.figure('<figure class="fig"><div id="grafico"></div></figure>')


def test_il_racconto_numerato_mette_un_fig_n_per_figura(racconto) -> None:
    trovate = C.figure(racconto)
    numerato = C.racconto_numerato(racconto, trovate)
    assert numerato.count('class="fignum"') == len(trovate)
    for fig in trovate:
        assert f'>Fig. {fig.numero}</span> ' in numerato, fig
        assert f'id="{fig.ancora}"' in numerato, fig


def test_il_racconto_numerato_non_tocca_il_resto(racconto) -> None:
    """La numerazione è chirurgica: aggiunge, e non riscrive il racconto."""
    numerato = C.racconto_numerato(racconto, C.figure(racconto))
    assert len(numerato) > len(racconto)
    senza = numerato.replace('<span class="fignum">', "")
    senza = re.sub(r"Fig\. \d+</span> ", "", senza)
    senza = re.sub(r'<figure class="fig" id="fig-\d+"', '<figure class="fig"', senza)
    assert senza == racconto


def test_ogni_grafico_del_racconto_ha_un_blocco_nella_pagina_delle_tabelle(racconto) -> None:
    """La riga «tutti i dati dei grafici si possono vedere anche come tabelle»
    è vera solo se ogni contenitore che il javascript riempie esiste anche
    sulla pagina delle tabelle. Questo test è quello che la tiene vera."""
    disegno = (C.MODELLI / "figure.js").read_text(encoding="utf-8")
    cercati = set(re.findall(r'getElementById\("([a-z0-9-]+)"\)', disegno))
    pagina = (C.MODELLI / "tabelle.html").read_text(encoding="utf-8")
    pagina = pagina.replace("{{BLOCCHI_TABELLE}}", C.blocchi_tabelle(C.figure(racconto)))
    presenti = set(re.findall(r'id="([a-z0-9-]+)"', pagina))
    # Gli unici che possono mancare sono le radici dello scrollytelling: non
    # sono grafici, sono i passi del racconto, e `scrollytelling()` senza
    # radice non fa niente invece di rompersi.
    assert cercati - presenti <= {"scrolly-popolazione", "scrolly-casa"}


def test_la_pagina_delle_tabelle_rimanda_a_ogni_figura(racconto) -> None:
    trovate = C.figure(racconto)
    blocchi = C.blocchi_tabelle(trovate)
    for fig in trovate:
        assert f'href="index.html#{fig.ancora}"' in blocchi, fig


def test_la_figura_che_condivide_la_tabella_dice_dove_sta(racconto) -> None:
    """Le due serie della casa hanno una tabella sola: la seconda sezione
    sarebbe vuota, e invece rimanda alla prima."""
    blocchi = C.blocchi_tabelle(C.figure(racconto))
    assert 'class="altrove"' in blocchi
    assert 'href="#fig-casa-prezzo"' in blocchi


@pytest.fixture(scope="module")
def sito_costruito(tmp_path_factory):
    uscita = tmp_path_factory.mktemp("sito")
    assert C.main(["--uscita", str(uscita), "--data-build", "2026-09-05"]) == 0
    return uscita


def test_la_costruzione_scrive_tutte_le_pagine(sito_costruito) -> None:
    for destinazione in C.PAGINE.values():
        pagina = sito_costruito / destinazione
        assert pagina.exists(), destinazione
        assert pagina.stat().st_size > 20_000, destinazione


def test_nessun_segnaposto_sopravvive_alla_costruzione(sito_costruito) -> None:
    """La stessa cosa che la CI controlla con un `grep` dopo la costruzione."""
    for destinazione in C.PAGINE.values():
        testo = (sito_costruito / destinazione).read_text(encoding="utf-8")
        rimasti = SEGNAPOSTO.findall(testo)
        assert not rimasti, f"{destinazione}: {sorted(set(rimasti))}"


def test_la_pagina_porta_dentro_stile_grafici_e_dati(sito_costruito) -> None:
    testo = (sito_costruito / "index.html").read_text(encoding="utf-8")
    assert "window.DATI=" in testo
    assert "window.GRAFICI" in testo
    assert "--seq-1" in testo, "lo stile non è stato incorporato"
    assert "http://" not in testo.replace("http://www.w3.org", ""), "una dipendenza esterna"


def test_la_data_di_costruzione_e_quella_che_le_si_passa(sito_costruito) -> None:
    testo = (sito_costruito / "index.html").read_text(encoding="utf-8")
    assert "2026-09-05" in testo


def test_le_tabelle_e_la_geometria_sono_copiate_accanto_al_sito(sito_costruito) -> None:
    tabelle = sorted((sito_costruito / "dati" / "processed").glob("*.csv"))
    assert len(tabelle) >= 30
    assert (sito_costruito / "dati" / "geo" / "comuni_brescia.geojson").exists()


def test_senza_i_json_del_sito_la_costruzione_si_ferma_invece_di_pubblicare(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.setattr(C, "DATI_WEB", tmp_path / "vuota")
    assert C.costruisci(tmp_path / "uscita", None) == 1
    assert "manca web/src/data" in capsys.readouterr().err


def test_le_conclusioni_hanno_una_riga_per_storia(racconto) -> None:
    """La testata dice «N storie» e il riquadro dice «le conclusioni in N
    righe», e N è contato dal modello — ma nessuno controllava che le righe
    fossero davvero N.

    È lo stesso errore che il commento in `cifre()` racconta di aver già preso
    una volta («la testata diceva otto storie quando erano nove»), spostato di
    un riquadro: aggiungere una storia senza aggiungere la sua riga fa dire
    alla pagina un numero che il suo stesso elenco smentisce."""
    storie = len(re.findall(r'class="story s\d', racconto))
    riquadro = re.search(
        r'<span class="t-lab">Le conclusioni.*?</ul>', racconto, re.S
    )
    assert riquadro, "il riquadro delle conclusioni non c'è più"
    righe = len(re.findall(r"<li>", riquadro.group(0)))
    assert righe == storie, f"{storie} storie ma {righe} righe di conclusione"
