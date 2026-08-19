# Prossimi passi

Questo documento è **la lista di ciò che resta**, e dice per ogni voce *chi la
può fare*. È scritto per essere ripreso a mesi di distanza da chi non ricorda
più dov'era rimasto: ogni sezione si legge da sola.

## Legenda — chi fa cosa

| | Significato |
|---|---|
| ✅ | **fatto**, resta come traccia |
| 🤖 | **fattibile da una sessione di lavoro qualsiasi**: bastano la rete e questo repository |
| 🙋 | **tocca a te.** Richiede un login personale (SPID/CIE), una macchina con accesso normale alla rete italiana, oppure una decisione che non va presa al posto tuo |

Le voci 🙋 non sono bloccanti per il grosso del progetto: i quattro assi
portanti hanno già tutti i dati che servono. Sono estensioni e finiture.

## Le cose che tocca a te — tutte, in un posto solo

| | Cosa | Perché tocca a te | Tempo | Blocca |
|---|---|---|---|---|
| 🙋 1 | **Scegliere la licenza** (§3.3) | è una tua decisione, non una tecnicalità | 10 min | la pubblicazione, non il lavoro |
| 🙋 2 | **Attivare GitHub Pages** (§7): *Settings → Pages → Source = «GitHub Actions»* | serve il tuo accesso da proprietario del repo | 2 min | il primo deploy |
| 🙋 3 | **Scaricare le quotazioni OMI** e i perimetri delle zone (§2.2) | area riservata Agenzia delle Entrate, SPID/CIE | 1–2 h la prima volta | solo l'asse «casa e prezzi», che è di contorno |
| 🙋 4 | **Scaricare gli open data del Comune di Brescia** (§2.2) | `dati.comune.brescia.it` non risponde dagli ambienti remoti, da una macchina italiana sì | 30 min | estende indietro il turismo cittadino (2005–2013) |
| 🙋 5 | **Scaricare i dati MUR sui due atenei** (§2.2) | `dati-ustat.mur.gov.it` idem | 30 min | l'asse istruzione, che è di contorno |
| 🙋 6 | **Esportare a mano il commercio estero provinciale** (§2.2) | il databrowser ISTAT è una SPA senza API | 1 h | niente: la serie regionale è già scaricata come ripiego dichiarato |
| 🙋 7 | **Rileggere i testi prima di pubblicare** (§8) | è il tuo nome sopra | — | la pubblicazione |

Tutto il resto di questo documento è 🤖 o ✅.

---

Indice:

1. [Lo stato, in una pagina](#1-lo-stato-in-una-pagina)
2. [Cosa resta da scaricare](#2-cosa-resta-da-scaricare)
3. [Le decisioni](#3-le-decisioni)
4. [Dimensioni non ancora considerate](#4-dimensioni-non-ancora-considerate)
5. [Come analizzare i dati](#5-come-analizzare-i-dati)
6. [Come si costruisce il sito statico](#6-come-si-costruisce-il-sito-statico)
7. [Il deploy su GitHub Pages](#7-il-deploy-su-github-pages)
8. [I due documenti da scrivere alla fine](#8-i-due-documenti-da-scrivere-alla-fine)
9. [Le lezioni del progetto precedente](#9-le-lezioni-del-progetto-precedente)
10. [Quanto tempo serve, e da dove ripartire](#10-quanto-tempo-serve-e-da-dove-ripartire)

---

## 1. Lo stato, in una pagina

| Pezzo | Stato |
|---|---|
| Ricognizione delle fonti | ✅ [`FONTI.md`](FONTI.md), con lo stato di accesso verificato riga per riga |
| Soggetto e assi | ✅ decisi: la provincia attraverso i 205 comuni, quattro assi portanti ([`BRIEF.md`](BRIEF.md)) |
| Repository separato | ✅ esiste, `main`, file in radice |
| Pipeline | ✅ funzionante, `requests` + libreria standard, 58 test verdi |
| Base geografica | ✅ i confini dei 205 comuni in GeoJSON, verificati contro l'area nota della provincia |
| Tabelle tidy | ✅ 19 CSV in [`dati/processed/`](dati/README.md), versionati; il ventesimo (`migrazioni_comuni.csv`) è in scarico |
| Analisi | 🤖 appena cominciata: due script in [`analysis/`](analysis/README.md) |
| Storie scelte | 🤖 no. Dodici candidate in `BRIEF.md`, nessuna confermata sui dati |
| Documento narrativo | 🤖 no |
| Pannello interattivo | 🤖 no |
| Deploy | 🙋🤖 no, e serve un passaggio tuo (§7) |
| Licenza | 🙋 **non scelta** (§3.3) |
| `METODOLOGIA.md`, `WORKING-PAPER.md` | ⚠️ bozze, si riscrivono alla fine (§8) |

**Dove sta il progetto, in una frase.** I dati ci sono e sono puliti; il
ritratto del territorio non è ancora stato disegnato. Il prossimo pezzo di
lavoro è l'analisi, non il download.

---

## 2. Cosa resta da scaricare

Lo stato completo, fonte per fonte, è in [`FONTI.md`](FONTI.md). Qui solo ciò
che manca.

### 2.1 Le fonti automatiche — ✅ chiuse

| Cosa | Stato |
|---|---|
| **Confini comunali** | ✅ `datasets/confini.py` + `geo.py`, con lettore di shapefile e riproiezione in libreria standard: niente `pyshp`, per lo stesso motivo per cui §5 reimplementa k-means. Prodotti `dati/geo/comuni_brescia.geojson` e `comuni_geometria.csv`, verificati contro l'area nota della provincia e contro lo `Shape_Area` di ISTAT |
| **Background migratorio** | ⏳ `migrazioni_comuni.csv` — dieci tavole `DF_DCSS_MIGR_BACKG_PAR_TV_*_COM`, scarico in corso: sono le più pesanti di tutte (centinaia di MB l'una) |
| **Abitazioni** | ✅ `abitazioni_comuni.csv` — `DF_DCSS_ABITAZIONI_TV_1` e `_TV_2` |
| **Famiglie con stranieri** | ✅ `famiglie_comuni.csv` — `DF_DCSS_FAMIGLIE_TV_1`, `_TV_2`, `_TV_3` |

Le ultime tre erano rimaste indietro perché `esploradati.istat.it` aveva
smesso di accettare connessioni a metà lavoro. **Non era un bug del codice: era
quell'host**, ed è tornato su. Rilanciarle costa un comando e parecchi minuti
di attesa:

```bash
python -m brescia_pipeline.build migrazioni abitazioni famiglie
```

> **Scoperta che vale la pena tenere per iscritto.** La chiave SDMX con più
> codici nella stessa dimensione **non** fallisce per lunghezza dell'URL, come
> diceva il commento nel codice: `REF_AREA` con 50 codici (430 caratteri)
> riceve `400` esattamente come con 205. Il server proprio non accetta la
> sintassi `codice+codice` lì. Scaricare l'Italia intera e filtrare in locale
> non è una comodità, è l'unica strada — ed è il motivo per cui queste quindici
> tavole pesano più di un giga in `dati/raw/`.

### 2.2 🙋 Le fonti che richiedono te

Nessuna di queste tocca i quattro assi portanti. Sono le estensioni.

| | Cosa | Ostacolo | Come si supera |
|---|---|---|---|
| 🙋 3 | **Quotazioni immobiliari OMI** e **compravendite NTN** | area riservata Agenzia delle Entrate (SPID/CIE/Fisconline, gratuito) | Registrarsi, scaricare le quotazioni semestrali dal 2004 e i perimetri delle zone OMI in GML/KML; le compravendite sono annuali per comune dal 2011. Poi serve un crosswalk zone OMI ↔ comuni, **da dichiarare come tale**: è l'unico punto del progetto in cui si introduce una seconda geometria, e §9 spiega perché è pericoloso |
| 🙋 4 | **Open data del Comune di Brescia** | `dati.comune.brescia.it` non risponde dagli ambienti di esecuzione remota, e ad agosto 2026 nemmeno `comune.brescia.it` (403) | Scaricare da una macchina normale: turismo cittadino 2005–2013 (estende indietro la serie regionale, che parte dal 2019) e i materiali dell'Osservatorio migrazioni |
| 🙋 5 | **Università** | `dati-ustat.mur.gov.it` irraggiungibile | Iscritti 1998/99–2025/26 e laureati 2001–2024 per ateneo. **Attenzione: Brescia ha due atenei**, la statale e la sede della Cattolica; la statale da sola sottostima la popolazione universitaria |
| 🙋 6 | **Commercio estero provinciale** | il portale Coeweb storico è dismesso (confermato: l'host non risponde), il sostituto è una SPA senza API | Esportare a mano dal databrowser via browser e versionare come input curato. In alternativa restare sulla serie **regionale**, già scaricata, dichiarandola — che è la scelta attuale e regge (MET-10) |

Quando arriva un file scaricato a mano, **non va copiato in
`dati/processed/`**: va messo come input curato e passato dalla pipeline, così
resta tracciabile da dove viene. È la stessa regola della provenienza esplicita
di §9.

### 2.3 🤖 Da verificare — promettenti, non testate

Nessuna è stata interrogata davvero: della tabella in `FONTI.md` §8 sappiamo
solo che l'host risponde.

- **INPS** — lavoratori dipendenti per provincia e settore, retribuzioni per
  classi e **cittadinanza**. È la più interessante delle tre, perché è l'unica
  fonte sulle **retribuzioni** e incrocia la cittadinanza, che è l'asse 2. Ma
  attenzione: `servizi2.inps.it` risponde 200 restituendo **la pagina HTML del
  portale**, non JSON. Gli osservatori sono un'applicazione web, non un'API
  documentata: il primo lavoro è trovare l'endpoint che l'applicazione stessa
  chiama, e potrebbe non essercene uno stabile.
- **INAIL** — infortuni sul lavoro. In un territorio industriale è pertinente,
  e a grana provinciale ci sta bene.
- **Sezioni di censimento ISTAT** — variabili censuarie sotto il comune (2011 e
  2021). Servono solo se si vorrà scendere sotto il comune per il capoluogo:
  con il soggetto provinciale non è più una priorità.
- **Mappatura acustica** dell'agglomerato · **progetti PNRR** da OpenPNRR
  (ODbL, e attenzione: aggiungerli cambia gli obblighi di licenza, §3.3) ·
  **risultati elettorali per sezione** da Eligendo
  (`elezioni.interno.gov.it` risponde; `eligendo.interno.gov.it` no).

### 2.4 🤖 Un difetto noto: le etichette censuarie sono in inglese

Nelle tabelle che vengono dall'SDMX di ISTAT le **modalità** delle dimensioni
sono in inglese: `private households on 31st December`, `15 years and over`,
`4 and over`. Riguarda `famiglie_comuni.csv`, `abitazioni_comuni.csv`,
`migrazioni_comuni.csv` e `censimento_lavoro_brescia.csv`, cioè tutte le
tavole censuarie, e stona con la decisione di §3.4 di tenere tutto in italiano
salvo i nomi delle colonne.

**Non è una scelta, è un header mancante.** ISTAT risponde in italiano se la
richiesta porta `Accept-Language: it` — verificato riga per riga: le stesse
osservazioni tornano come `famiglie con tutti i componenti stranieri al 31
dicembre` e `6 e più`. Il rimedio è **una riga in `fetch.py`**, ma comporta un
**riscarico completo** delle quindici tavole (la cache di `dati/raw/` è in
inglese), quindi qualche ora di attesa: conviene farlo insieme al prossimo
riscarico, non da solo.

Finché non è fatto, va tenuto presente in ogni grafico: quelle stringhe non
sono pubblicabili così come sono.

---

## 3. Le decisioni

### 3.1 Il soggetto — ✅ deciso (agosto 2026)

**La provincia di Brescia è il soggetto principale**, con il **capoluogo come
caso privilegiato**: gli si dedicano una o due analisi tutte sue, ma il fuoco
resta sul territorio.

Conseguenze operative:

- l'unità di default di ogni mappa e di ogni classifica sono i **205 comuni**;
- il capoluogo compare come *uno dei* comuni, non come protagonista implicito —
  e siccome è un ordine di grandezza sopra tutti gli altri (199.853 abitanti
  contro una mediana di 3.671), va gestito come outlier dichiarato nelle scale
  di colore e nelle correlazioni (MET-5);
- gli aggregati provinciali servono da riferimento, non da soggetto;
- le due analisi dedicate al capoluogo sono indicate in `BRIEF.md`.

### 3.2 Gli assi — ✅ scelti (agosto 2026)

Quattro assi portanti, il resto come materiale di contorno. Il criterio è
duplice: qualità del dato **e** coerenza con il soggetto provinciale.
Motivazione e forma di ciascuno in [`BRIEF.md`](BRIEF.md).

| | Asse | Forma prevalente | Dati |
|---|---|---|---|
| **1** | Il lavoro e le imprese | coropletica sui 205 comuni + serie | ✅ completi |
| **2** | Chi vive nel bresciano | coropletica + composizioni | ✅ completi |
| **3** | Le due economie: manifattura e Garda | mappa bivariata + concentrazione | ✅ completi |
| **4** | L'aria e il clima | **non una mappa**: 7 stazioni come sezione territoriale, più 52 stazioni meteo | ✅ completi |

Di contorno, non abbandonati: sicurezza, casa e prezzi, commercio estero,
riqualificazione. Entrano se un asse portante li richiama, non per completezza.

### 3.3 🙋 La licenza — **da scegliere**

È l'unica decisione ancora aperta, ed è tua. Le fonti sono tutte aperte ma con
obblighi di citazione diversi:

| Fonte | Obbligo |
|---|---|
| ISTAT, Regione Lombardia | CC-BY: attribuzione |
| Agenzia delle Entrate (OMI) | citazione obbligatoria «Agenzia Entrate - OMI» |
| OpenStreetMap | ODbL: **share-alike sui dati derivati** |
| OpenPNRR | ODbL, stessa conseguenza |

La combinazione usuale per un progetto così è **codice MIT + dati e testi
CC-BY-4.0**, che soddisfa gli obblighi delle fonti *attualmente* usate: oggi
nel repository non c'è un solo dato OpenStreetMap né PNRR, e la geometria viene
da ISTAT. L'ODbL entrerebbe in gioco solo aggiungendoli — quindi la decisione
va rifatta se un giorno si aggiungono (§2.3).

In pratica: due file, `LICENSE` (MIT) e `LICENSE-DATI` (CC-BY-4.0), più una
riga nel `README`. Dieci minuti, ma la scelta resta tua.

### 3.4 Lingua — ✅ decisa, ma non ancora rispettata dai dati

I documenti sono in italiano. Il progetto Donostia teneva la documentazione
tecnica in inglese e i relati in spagnolo, e la mescolanza ha prodotto attrito.
Deciso una volta: **tutto in italiano** salvo i nomi delle colonne.

⚠️ Le tabelle censuarie oggi violano la decisione: le modalità arrivano in
inglese perché manca un header nella richiesta. Vedi §2.4.

---

## 4. Dimensioni non ancora considerate

Idee emerse durante la ricognizione che nessuno ha ancora valutato. Tutte 🤖:
i dati ci sono o si scaricano da soli.

**Sul lavoro e le imprese**

- **La demografia d'impresa**: la famiglia `183_203_DF_DICA_ACDP_*` porta forma
  giuridica, **età dell'impresa**, sesso e **paese di nascita del titolare**.
  Quante imprese bresciane sono guidate da stranieri, e in quali settori, è una
  storia che nessuno ha raccontato con i dati.
- **Il lavoro da casa** (`DF_DCSS_LCAS_FRISC_1`): quanto è rimasto del remoto
  dopo il 2021, in un territorio manifatturiero dove gran parte del lavoro non
  si può fare da casa.
- **I distretti**: Val Trompia e Lumezzane (metalmeccanica), Franciacorta
  (vino), Bassa (agroalimentare), Garda (turismo). Non esiste una
  classificazione ufficiale pronta, ma si può costruire raggruppando i comuni
  per specializzazione settoriale con i dati ASIA già scaricati. Sarebbe un
  contributo originale, non una ripetizione.

**Sul territorio**

- **Odolo, 89,6 addetti ogni 100 abitanti** — e Limone sul Garda 133. Una mappa
  del rapporto addetti/residenti mostra dove il lavoro si concentra rispetto a
  dove si abita, e i due estremi hanno cause opposte (acciaierie contro
  alberghi). È già calcolabile da `comuni_sintesi.csv`.
- **Lo spopolamento montano**: Valle Camonica e Valle Sabbia contro la pianura.
  Il primo sguardo c'è già ed è netto — `analysis/variazione_popolazione.py`
  dice che **93 comuni su 205 perdono popolazione fra il 2018 e il 2024**, e
  che le dieci cadute più rapide sono tutte di montagna (Magasa −2,9 % l'anno,
  Lozio, Berzo Demo, Paisco Loveno, Saviore dell'Adamello), mentre la provincia
  nel suo complesso cresce dello 0,15 % l'anno. È materiale per una storia,
  non ancora una storia: manca la decomposizione fra saldo naturale e
  migrazione.

**Sull'ambiente**

- **Il sito contaminato Caffaro** a Brescia (PCB): una vicenda che dura da
  decenni, con dati ARPA e studi di ATS. È l'incrocio più diretto fra storia
  industriale e salute pubblica di tutto il progetto.
- **L'isola di calore** via Landsat (l'endpoint STAC di Microsoft Planetary
  Computer è verificato e anonimo). In pianura padana il contrasto
  centro/periferia è più marcato che altrove.
- **Il termovalorizzatore e il teleriscaldamento**, fra i più estesi d'Italia.

**Sul metodo**

- **Confrontare Brescia con Bergamo**: due province gemelle, stessa Capitale
  della cultura 2023, storie industriali parallele. Tutte le fonti usate qui
  coprono l'Italia intera: aggiungere Bergamo costa un filtro — e i file grezzi
  nazionali sono già in `dati/raw/`, quindi nemmeno un download. È anche il
  **controllo naturale** per la questione aperta di MET-9.

---

## 5. Come analizzare i dati

L'approccio del progetto precedente, che ha retto alla revisione esterna.

### 5.1 Regole che hanno salvato il progetto

1. **Correlazione non è causalità, e va scritto nel testo, non solo pensato.**
   Il progetto Donostia partiva da «il turismo fa salire i prezzi?» e ha
   passato mesi a dimostrare che con quei dati non si poteva rispondere. Ha
   scelto di dirlo, e quella è diventata la parte più solida del lavoro.
2. **Mai la parola «gentrificazione»** — o qualunque termine che implichi un
   meccanismo che i dati non mostrano. Il progetto usava «trasformazione».
3. **N piccolo**: con 205 comuni si sta meglio che con 19 barrios, ma le
   correlazioni fra indicatori comunali restano descrittive. Usare **Pearson e
   Spearman insieme** e un **leave-one-out** sugli outlier noti (qui: Brescia
   città, e i comuni del Garda per qualunque cosa tocchi il turismo).
4. **Ogni numero citato deve avere uno script dietro.** Non era vero fino ad
   agosto 2026, e infatti due cifre su ventiquattro erano sbagliate: ora
   `analysis/verifica_cifre.py` le ricalcola tutte dalle tabelle e diverge
   rumorosamente se una non torna. **Aggiungere una cifra a un documento
   significa aggiungere una riga a quello script.**
5. **Una scheda di confidenza per indicatore**: `osservato` (misurato
   direttamente), `derivato` (calcolato da altri), `proxy` (approssimazione),
   più le assunzioni esplicite. Nell'interfaccia diventa un distintivo
   visibile, non una nota a piè di pagina.

### 5.2 Analisi che avevano dato i risultati migliori

Riadattate al caso bresciano. La prima è fatta, le altre no.

- ✅ **Velocità di cambio**: tassi annualizzati per comune fra il primo e
  l'ultimo anno di ogni serie. Distingue «dov'è alto» da «dove sta cambiando in
  fretta», che è quasi sempre la domanda più interessante. Fatta sulla
  popolazione (`analysis/variazione_popolazione.py`); **da rifare su addetti,
  unità locali e reddito**, che è un'ora di lavoro perché lo schema è lo stesso.
- 🤖 **Livelli contro variazioni**: uno scatter con il livello sull'asse x e la
  variazione sull'asse y separa i comuni in quattro quadranti e rende visibile
  la polarizzazione.
- 🤖 **Tipologia di comuni**: k-means con seme fisso su poche variabili
  (specializzazione settoriale, dimensione media d'impresa, reddito, densità).
  Da presentare **come profili descrittivi, mai come verità**.
- 🤖 **Autocorrelazione spaziale**: i comuni contigui si somigliano? Con 205
  comuni e una geometria vera, qui ha molto più senso che con 19 barrios. La
  matrice di contiguità si ricava dal GeoJSON già presente.
- 🤖 **Rottura Covid**: 2020–2021 spezza quasi tutte le serie. Testare
  esplicitamente la discontinuità invece di far finta che non ci sia. Vale
  anche per il tasso annualizzato del punto 1, che ci passa sopra.
- 🤖 **Decomposizione della popolazione**: quanto della variazione viene da
  saldo naturale, migrazione interna, migrazione estera. È il seguito naturale
  dello spopolamento montano di §4.
- 🤖 **La decomposizione settoriale del capoluogo**, che MET-9 ha lasciato a
  metà: se la divisione 81 sia scesa davvero a zero o sia stata riclassificata,
  e se lo stesso movimento si veda a Bergamo.

### 5.3 La convenzione di `analysis/`

Uno script per analisi in [`analysis/`](analysis/README.md), `--save` che
scrive CSV in `analysis/output/` (ignorata da git: si rigenera), e come sole
dipendenze la **libreria standard** — niente pandas, niente scipy, niente
sklearn. Le tabelle sono piccole e k-means e le correlazioni si reimplementano
in poche righe; in cambio il progetto resta installabile ovunque, come la
pipeline.

Gli script leggono **solo** da `dati/processed/`: nessuno tocca la rete. La
regola di confine con la pipeline: **se il risultato serve al sito è pipeline,
se serve a capire è analisi.**

---

## 6. Come si costruisce il sito statico

Questa è la parte che si perderebbe. Il progetto Donostia pubblica **due cose
diverse** sullo stesso sito, ed è una separazione che vale la pena copiare.

### 6.1 I due artefatti

**(a) Il documento narrativo** — un **unico file HTML autocontenuto**, senza
dipendenze a runtime, che è la homepage del sito.

- I dati sono **incorporati** in una sola riga `<script>window.DATI = {…}`.
  Nessuna `fetch()`: il file si apre anche da disco, si manda per email, si
  archivia. Nel progetto Donostia pesava 846 KB con sette storie dentro.
- I grafici sono **SVG disegnati a mano in JavaScript**, senza librerie.
  Suona faticoso ed è invece il motivo per cui il file resta autocontenuto e
  non invecchia.
- La forma è **scrollytelling**: la mappa o il grafico restano fissi
  (`position: sticky`) mentre il testo scorre e li aggiorna. Tutti i controlli
  restano anche manipolabili a mano — chi vuole esplorare non è costretto a
  scorrere.
- Ogni metrica complessa ha un riquadro **«la metrica, in chiaro»** che la
  spiega in due frasi.
- Le pagine sorelle sono `metodologia.html` e `dati.html`, con la stessa
  struttura.

**(b) Il pannello interattivo** — un'app React + Vite servita sotto `/app/`.

Dipendenze essenziali (versioni del progetto precedente, da aggiornare):

```
react + react-dom · maplibre-gl (mappe) · recharts (grafici)
d3-array, d3-scale, d3-scale-chromatic (scale e palette)
vite · typescript · vitest + jsdom + @testing-library/react
```

Tre scelte che hanno funzionato:

- **Nessun tile esterno.** La mappa usa uno stile vuoto (`sources: {}`) e
  disegna solo il GeoJSON: funziona offline, senza chiavi API e senza dipendere
  da un servizio di terzi.

  ```ts
  const BLANK_STYLE = { version: 8, sources: {}, layers: [] };
  ```

- **Chunk separati** per maplibre e recharts in `vite.config.ts`: sono molto
  più pesanti del codice dell'app e così restano in cache fra un deploy e
  l'altro.
- **Una tabella-specchio accessibile** accanto a ogni mappa, navigabile da
  tastiera e da lettore di schermo. Una coropletica da sola è inaccessibile.

> **Se il tempo è poco, il documento narrativo viene prima** — nel progetto
> precedente ha avuto molto più valore del pannello (§9).

### 6.2 Il contratto fra pipeline e frontend

È l'idea più preziosa da portare via. La pipeline scrive **JSON statico** in
`web/src/data/`; il frontend legge solo quello e **non ha alcuna dipendenza a
runtime** da Python o dalle API delle fonti. Una forma stabile per indicatore
mantiene generico il codice della mappa: **aggiungere un dataset = un JSON in
più e una riga nel registro**, senza toccare i componenti.

Adattato a Brescia (la chiave diventa il codice ISTAT, e serve un livello per
il territorio):

```jsonc
// metric_addetti.json
{
  "id": "addetti",
  "label": "Addetti delle unità locali",
  "unit": "addetti",
  "kind": "sequential",        // sequential | diverging | categorical
  "livello": "comune",         // comune | provincia | regione
  "theme": "imprese",
  "source": "ISTAT — ASIA unità locali",
  "confidence": "osservato",   // osservato | derivato | proxy
  "assumptions": ["Unità locali, non imprese: le sedi secondarie contano nel comune dove stanno"],
  "periods": ["2018", "2019", "2020", "2021", "2022", "2023"],
  "values": {
    "017029": { "2018": 101135.9, "2023": 100939.2 },
    "017068": { "2018": 10240.0,  "2023": null }
  }
}
```

Più un registro `metrics.json` con i soli descrittori, così l'interfaccia
costruisce il menù senza caricare tutti i dati:

```jsonc
[{ "id": "addetti", "label": "…", "theme": "imprese", "livello": "comune",
   "timeGrain": "year", "source": "…", "status": "live" }]
```

Con `status: "planned"` l'indicatore compare disattivato con la nota «dati in
arrivo»: l'interfaccia degrada con eleganza invece di rompersi.

Caricamento lato frontend, con Vite che trasforma la glob in import pigri:

```ts
const loaders = import.meta.glob<{ default: MetricData }>("../data/metric_*.json");
export async function loadMetric(id: string) {
  return (await loaders[`../data/metric_${id}.json`]()).default;
}
```

**Invarianti da far valere con i test della pipeline:**

1. ogni codice usato in un `metric_*.json` esiste nella geometria;
2. ogni indicatore `live` nel registro ha il suo file, e viceversa;
3. `periods` è ordinato e senza duplicati;
4. nessun valore negativo per conteggi e densità;
5. le chiavi in `values` esistono tutte in `periods`.

### 6.3 Le scale di colore

- **Sequenziale** (`interpolateYlOrRd`) per i valori assoluti.
- **Divergente** (`interpolateRdBu` invertita: blu = giù, rosso = su) centrata
  sullo zero per le variazioni.
- **Qualitativa** per le metriche categoriche, con le etichette nella legenda e
  nel tooltip al posto dell'indice numerico.
- Un colore dedicato per **«nessun dato»** (`#e6e6e6`), mai lo zero della
  scala. Per Brescia questo è cruciale, e più di quanto sembri: sulle presenze
  turistiche 2024 mancano **73 comuni su 205** — 45 con il dato soppresso, 27
  che la fonte non riporta affatto e uno (Gottolengo) con uno zero fittizio.
  Sono tre assenze diverse e nessuna delle tre è uno zero.

### 6.4 Le tabelle CSV canoniche

Oltre al JSON per il frontend, il progetto esportava gli stessi numeri come
**CSV tidy** pubblicati sul sito, con un link «↓ CSV» sotto ogni grafico. Costa
poco e rende il lavoro verificabile da chiunque. Qui esistono già:
`dati/processed/` è pronta a essere copiata nel sito.

---

## 7. Il deploy su GitHub Pages

Un solo workflow, `.github/workflows/deploy-pages.yml`. Struttura del sito:

```
/                     il documento narrativo (copiato anche come index.html)
/metodologia.html     
/dati.html            fonti, vigenza, avvertenze
/app/                 il pannello React
/dati/processed/*.csv le tabelle scaricabili
```

I passaggi, nell'ordine:

1. `actions/checkout` e `actions/setup-node` (Node 22+, cache su
   `web/package-lock.json`);
2. `npm ci` e `npm run build` dentro `web/`, con
   **`VITE_BASE: "/brescia-dataviz/app/"`** — GitHub Pages serve da una
   sottocartella e senza questa variabile tutti gli asset danno 404;
3. assemblaggio: `mkdir -p _site/app`, copia di `web/dist/*` in `_site/app/`,
   copia del narrativo in `_site/index.html` **e** con il suo nome, copia delle
   pagine sorelle e dei CSV;
4. `actions/configure-pages` con `enablement: true`, poi
   `upload-pages-artifact` e `deploy-pages`.

Dettagli che costano tempo se non li sai:

- 🙋 **Una volta sola, e la puoi fare solo tu**: *Settings → Pages → Source =
  «GitHub Actions»*. Il primo deploy fallisce se non è impostato.
- Permessi richiesti: `contents: read`, `pages: write`, `id-token: write`.
- `concurrency: { group: pages, cancel-in-progress: true }` evita che due
  deploy si accavallino.
- **Le date si stampano in fase di deploy**, non a mano: la data del sito viene
  dal commit, quella dei dati da un `manifest.json` che la pipeline scrive a
  ogni build completo. Nelle pagine ci sono i segnaposto `{{BUILD_DATE}}` e
  `{{DATA_DATE}}`, sostituiti dal workflow. Senza questo meccanismo le date
  invecchiano in silenzio e il sito mente.
- Partire con il deploy **manuale** (`workflow_dispatch`) e passare
  all'automatico su `main` solo quando i testi si sono stabilizzati. Il
  progetto precedente ha fatto così, per rileggere prima di pubblicare.

---

## 8. I due documenti da scrivere alla fine

Non ora: **quando i dati saranno completi, le visualizzazioni costruite e le
storie scelte.** Esistono già come bozze in questo repository, e le bozze
vanno riscritte, non ampliate.

### La nota metodologica — [`METODOLOGIA.md`](METODOLOGIA.md)

Le regole che governano il progetto, ciascuna con il proprio perché: è la base
di credibilità, e qualunque grafico o titolo deve esserle coerente. Nel
progetto Donostia si chiamava `NOTA-METODOLOGICA.md` e numerava le decisioni
(MET-1…MET-8); qui la bozza ne conta undici.

**Perché va scritta alla fine.** Buona parte delle regole nasce da problemi
incontrati *facendo* l'analisi, non prima. Nel progetto precedente le tre più
importanti — fallacia ecologica, distinzione fra stato, cambio e traiettoria, e
il bias del proxy turistico — sono arrivate dalle revisioni esterne, cioè dopo
che i relati erano scritti. Qui è già successo due volte: MET-9 («decomporre
prima di titolare») esiste perché un titolo sbagliato è stato scoperto e
corretto, e la regola «ogni numero ha uno script dietro» è diventata vera solo
quando lo script ha trovato due cifre sbagliate nei documenti.

Cosa mancherà finché non si chiude l'analisi: le regole su **come si scelgono e
si raccontano le storie** — quando un indicatore merita una narrazione, quali
soglie, come si trattano i casi limite che i dati faranno emergere.

### Il working paper — [`WORKING-PAPER.md`](WORKING-PAPER.md)

L'esposizione autocontenuta del metodo per un lettore esterno, pensata perché
qualcuno possa **replicare, criticare o riutilizzare** il lavoro: motivazione,
disegno dei dati, decisioni metodologiche, indicatori derivati, strategia
inferenziale, risultati, limiti, regola di arresto, cosa è riutilizzabile
altrove. Nel progetto Donostia era `docs/WORKING-PAPER.md` e veniva convertito
in HTML a ogni deploy da uno script (`scripts/build_working_paper.py`), così da
non divergere mai dal markdown.

**Perché va scritto alla fine.** Un paper metodologico che non può riportare
risultati è mezzo paper: la sezione più utile è quella in cui il metodo viene
messo alla prova dai dati veri. Nella bozza attuale la sezione dei risultati è
esplicitamente provvisoria, e persino il titolo cambierà quando sarà chiaro
qual è la tesi.

Due cose che nel progetto precedente hanno fatto la differenza e vanno
riprodotte:

- **includere le analisi che hanno smontato i propri risultati.** È la parte
  che quasi nessuno pubblica ed è quella che dà credibilità a tutto il resto.
  Qui c'è già il primo candidato (§6.1 della bozza).
- **una sezione esplicita su cosa i dati non permettono di dire.** Nel progetto
  Donostia è stata la più apprezzata dai revisori esterni.

### Ordine consigliato

1. completare le analisi (§5);
2. scegliere le storie e costruire le visualizzazioni (§6);
3. **poi** riscrivere la nota metodologica, che a quel punto descrive decisioni
   davvero prese;
4. **infine** il working paper, che le sintetizza per un lettore esterno;
5. 🙋 rileggere tutto prima di pubblicare.

---

## 9. Le lezioni del progetto precedente

Cose imparate a caro prezzo, che non sono ovvie.

**Sulla struttura**

- **Una sola geometria di riferimento, un solo join in ingestione.** Il momento
  in cui si ammettono due geometrie «quasi uguali» è il momento in cui i numeri
  smettono di tornare. Qui la geometria è il comune e la chiave è il codice
  ISTAT: non inventare slug. L'unica eccezione all'orizzonte sono le zone OMI
  (§2.2), e va trattata come un'eccezione dichiarata.
- **Nessuna riga scartata in silenzio.** Quando un join non trova
  corrispondenza, va registrato e mostrato (il progetto precedente pubblicava
  un `matchRate`). Uno scarto silenzioso è un errore che si scopre mesi dopo.
- **La provenienza viaggia con il dato**: ogni indicatore porta la sua fonte
  fino all'interfaccia.

**Sulla narrazione**

- Il documento narrativo ha avuto **più valore del pannello interattivo**. Il
  pannello serve a chi vuole esplorare; il documento è ciò che si legge, si
  cita e si condivide. Se il tempo è poco, il documento viene prima.
- Le storie vanno scritte **dopo** aver visto i dati, non prima. Le ipotesi
  iniziali del progetto Donostia sono state in gran parte smentite, e il lavoro
  è migliorato quando si è smesso di difenderle.
- **Dichiarare i limiti rafforza il lavoro**, non lo indebolisce. La sezione
  «cosa questi dati non permettono di dire» è stata la più apprezzata dai
  revisori esterni.

**Sui dati, specifiche di questo progetto**

- Le tre trappole tecniche (header SDMX, chiavi posizionali, separatori
  numerici) sono descritte in [`FONTI.md`](FONTI.md) §10 e §11 e già gestite
  nella pipeline: leggerle prima di scrivere qualunque nuovo modulo.
- **Le finestre temporali sono molto diverse per asse** — aria dal 1992, ASIA
  2018–2023, percezione dal 2022. Non appiattirle sulla più corta: mostrarle
  per quello che sono, dichiarando la differenza.
- **I dati mancanti non sono zeri**, e in questo progetto ci sono già tre modi
  diversi di essere assenti sullo stesso indicatore (§6.3).
- **Un host che non risponde non è un modulo rotto.** Le tre tavole censuarie
  sono rimaste ferme per mesi perché `esploradati.istat.it` era giù nel momento
  sbagliato. Prima di mettere mano al codice, riprovare il giorno dopo.

---

## 10. Quanto tempo serve, e da dove ripartire

Stime a spanne, per una sessione di lavoro tranquilla. Servono a decidere cosa
entra nel tempo che hai, non a fare un piano.

| Blocco | Tempo | Serve a |
|---|---|---|
| 🙋 Licenza (§3.3) | **10 min** | poter pubblicare |
| 🤖 Le altre velocità di cambio (addetti, unità locali, reddito) | **1 h** | lo schema è già scritto, si copia |
| 🤖 Livelli contro variazioni + i quattro quadranti | **2 h** | la prima immagine davvero parlante |
| 🤖 Rapporto addetti/residenti sui 205 comuni (§4) | **1 h** | la prima coropletica, e i dati ci sono tutti |
| 🤖 Decomposizione settoriale del capoluogo (MET-9) | **3 h** | chiudere la questione aperta più importante |
| 🤖 Autocorrelazione spaziale e tipologia di comuni | **mezza giornata** | il contributo più originale possibile |
| 🤖 Documento narrativo, prima storia intera | **1–2 giorni** | il prodotto vero |
| 🤖 Workflow di deploy + pagine sorelle | **mezza giornata** | pubblicare |
| 🙋 Attivare Pages (§7) | **2 min** | idem |
| 🤖 Pannello React | **2–3 giorni** | l'esplorazione, ma viene dopo il documento |
| 🙋 I download manuali (§2.2) | **2–4 h in tutto** | estensioni, nessun asse portante |
| 🤖 Etichette censuarie in italiano (§2.4) | **10 min di codice + qualche ora di riscarico** | poter pubblicare quelle tavole |
| 🤖 Riscrivere METODOLOGIA e WORKING-PAPER (§8) | **1 giorno** | in coda, quando le storie sono chiuse |

### Se hai due ore

Fai la licenza (dieci minuti, e toglie l'unica decisione aperta), poi le
velocità di cambio su addetti e reddito. Escono numeri veri e li puoi guardare.

### Se hai mezza giornata

Le due ore di sopra, più il rapporto addetti/residenti e i quattro quadranti.
A quel punto hai tre immagini e sai già quale storia regge.

### Se hai un weekend

Aggiungi la decomposizione settoriale del capoluogo — è la domanda che il
progetto ha lasciato aperta e che nessun altro ha risposto — e comincia il
documento narrativo con una storia sola, fatta bene. Una storia intera vale
più di sette abbozzate, ed è anche il modo per scoprire cosa manca al
contratto dati di §6.2 prima di averlo replicato dieci volte.

**Da dove ripartire in ogni caso**: `python analysis/verifica_cifre.py`. Se le
ventiquattro verifiche passano, le tabelle sono a posto e i documenti dicono il
vero; se una diverge, quello è il primo problema da guardare.

---

*Documento nato ad agosto 2026 come consegna per la separazione del
repository, e riscritto quando la separazione era avvenuta e la pipeline
funzionava. Lo stato delle fonti è in [`FONTI.md`](FONTI.md), quello dei dati
in [`dati/README.md`](dati/README.md), quello della pipeline in
[`pipeline/README.md`](pipeline/README.md).*
