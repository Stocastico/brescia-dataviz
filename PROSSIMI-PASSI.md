# Prossimi passi — e tutto ciò che serve portarsi dietro

Questo documento è scritto per essere letto **in un repository nuovo, in una
sessione che non ha mai visto il progetto Donostia**. Tutto ciò che sta qui
dentro è autosufficiente: decisioni da prendere, dati ancora da scaricare, e
soprattutto la parte di architettura — sito statico, analisi, deploy — che
altrimenti si perderebbe nel passaggio.

Indice:

1. [Creare il repository nuovo](#1-creare-il-repository-nuovo)
2. [Cosa resta da scaricare](#2-cosa-resta-da-scaricare)
3. [Le decisioni da prendere](#3-le-decisioni-da-prendere)
4. [Dimensioni non ancora considerate](#4-dimensioni-non-ancora-considerate)
5. [Come analizzare i dati](#5-come-analizzare-i-dati)
6. [Come si costruisce il sito statico](#6-come-si-costruisce-il-sito-statico)
7. [Il deploy su GitHub Pages](#7-il-deploy-su-github-pages)
8. [I due documenti da scrivere alla fine](#8-i-due-documenti-da-scrivere-alla-fine)
9. [Le lezioni del progetto precedente](#9-le-lezioni-del-progetto-precedente)

---

## 1. Creare il repository nuovo — ✅ fatto (agosto 2026)

Il repository esiste, è su GitHub come `brescia-dataviz`, il branch principale
è `main` e i file stanno in radice. Della lista qui sotto resta aperta **solo
la licenza**: le fonti sono aperte ma con obblighi di citazione diversi
(ISTAT e Regione Lombardia CC-BY, OpenStreetMap ODbL, Agenzia delle Entrate
con «Agenzia Entrate - OMI» obbligatorio), quindi la scelta va fatta con gli
occhi aperti e non è stata fatta al posto di nessuno. La combinazione usuale
per un progetto così è **codice MIT + dati e testi CC-BY-4.0**, che soddisfa
gli obblighi di attribuzione delle fonti attuali; ODbL entrerebbe in gioco
solo se si aggiungessero dati OpenStreetMap, che oggi non ci sono.

Il resto di questa sezione resta come traccia storica di com'è stata fatta la
separazione.

Il lavoro viveva nella cartella `brescia/` di un branch del repo
`donostia-dataviz`. È autoconclusiva: non importa nulla da quel progetto se non
l'ispirazione architetturale, che è interamente riassunta in questo documento.

```bash
# 1. Estrarre la cartella conservando lo storico dei commit
git clone https://github.com/<utente>/donostia-dataviz.git estrazione
cd estrazione
git checkout claude/brescia-data-visualization-7gkn4y
git subtree split --prefix=brescia -b solo-brescia

# 2. Nuovo repository, branch principale main
mkdir ../brescia-dataviz && cd ../brescia-dataviz
git init -b main
git pull ../estrazione solo-brescia
```

Se lo storico non interessa, basta copiare la cartella in un repo vuoto: il
contenuto è lo stesso e si perde solo la cronologia della ricognizione.

**Dopo il primo commit:**

- il branch principale si chiama **`main`** (`git branch -M main` se serve, e
  su GitHub *Settings → Branches → Default branch*);
- spostare i file di `brescia/` nella radice del nuovo repo — `FONTI.md`,
  `BRIEF.md`, `METODOLOGIA.md`, `WORKING-PAPER.md`, `PROSSIMI-PASSI.md`,
  `pipeline/`, `dati/` — e riscrivere il `README.md` di radice partendo da
  quello attuale;
- ⚠️ `METODOLOGIA.md` e `WORKING-PAPER.md` sono **bozze scritte in anticipo**:
  portarle dietro con il loro avviso in testa e riscriverle alla fine (§8);
- portarsi dietro il `.gitignore` (esclude `dati/raw/`, che pesa quasi 1 GB ed
  è rigenerabile);
- **verificare che `dati/processed/` sia versionata**: sono le tabelle pulite,
  8 MB, ed è il prodotto del progetto;
- aggiungere una licenza. Le fonti sono tutte aperte ma con obblighi di
  citazione diversi: ISTAT e Regione Lombardia CC-BY, OpenStreetMap ODbL,
  Agenzia delle Entrate con citazione obbligatoria «Agenzia Entrate - OMI».

---

## 2. Cosa resta da scaricare

Lo stato completo, fonte per fonte, è in [`FONTI.md`](FONTI.md). Qui solo ciò
che manca, in ordine di rapporto valore/fatica.

### Immediato — fonti già verificate, pipeline da scrivere

| Cosa | Fonte | Stato |
|---|---|---|
| **Confini comunali** | `istat.it/storage/cartografia/confini_amministrativi/generalizzati/2025/Limiti01012025_g.zip` (10 MB) | ✅ **fatto** (agosto 2026). `datasets/confini.py` + `geo.py`, con lettore di shapefile e riproiezione in libreria standard: niente `pyshp`, per lo stesso motivo per cui §5 reimplementa k-means. Prodotti `dati/geo/comuni_brescia.geojson` e `comuni_geometria.csv`, verificati contro l'area nota della provincia e contro lo `Shape_Area` di ISTAT. **Non è più il pezzo bloccante.** |
| **Background migratorio** | 10 dataflow `DF_DCSS_MIGR_BACKG_PAR_TV_*_COM` | ⏳ modulo scritto (`datasets/migrazioni.py`), scarico da rifare |
| **Abitazioni** | `DF_DCSS_ABITAZIONI_TV_1` e `_TV_2` | ⏳ modulo scritto (`datasets/abitazioni.py`), scarico da rifare |
| **Famiglie con stranieri** | `DF_DCSS_FAMIGLIE_TV_1`, `_TV_2`, `_TV_3` | ⏳ modulo scritto (`datasets/famiglie.py`), scarico da rifare |

I tre ⏳ hanno gli ID dei dataflow verificati contro l'elenco reale di ISTAT
(4.896 dataflow) e le chiavi che si compongono; manca solo lo scarico, perché
`esploradati.istat.it` ha smesso di accettare connessioni TCP a metà lavoro
mentre `www.istat.it` restava su. Basta rilanciare:

```bash
python -m brescia_pipeline.build migrazioni abitazioni famiglie
```

Se il primo tentativo va a vuoto, non è un bug del modulo: è quel host. Vale la
pena lanciarlo e lasciarlo correre, perché scarica l'Italia intera per ognuna
delle 15 tavole (il filtro territoriale lato server non esiste — vedi sotto).

> **Scoperta che vale la pena mettere per iscritto.** La chiave SDMX con più
> codici nella stessa dimensione **non** fallisce per lunghezza dell'URL, come
> diceva il commento nel codice: `REF_AREA` con 50 codici (430 caratteri)
> riceve `400` esattamente come con 205. Il server proprio non accetta la
> sintassi `codice+codice` lì. Scaricare tutto e filtrare in locale non è una
> comodità, è l'unica strada.

### Richiede un passaggio manuale

| Cosa | Ostacolo | Come si supera |
|---|---|---|
| **Quotazioni immobiliari OMI** | Area riservata Agenzia delle Entrate (SPID/CIE/Fisconline, gratuito) | Registrarsi, scaricare quotazioni semestrali dal 2004 e perimetri delle zone OMI in GML/KML. Poi serve un crosswalk zone OMI ↔ comuni, da dichiarare. |
| **Compravendite NTN** | Stessa area riservata | Dato annuale per comune dal 2011. |
| **Commercio estero provinciale** | Il portale Coeweb storico è dismesso; il sostituto è una SPA senza API raggiungibile | Esportare a mano dal databrowser via browser e versionare come input curato. In alternativa restare sulla serie **regionale**, già scaricata, dichiarandola. |
| **Open data del Comune di Brescia** | `dati.comune.brescia.it` non risponde dagli ambienti di esecuzione remota | Scaricare da una macchina normale: turismo cittadino 2005–2013 (estende indietro la serie regionale che parte dal 2019) e i materiali dell'Osservatorio migrazioni. |
| **Università** | `dati-ustat.mur.gov.it` irraggiungibile dall'ambiente di ricognizione | Iscritti 1998/99–2025/26 e laureati 2001–2024 per ateneo. **Attenzione: Brescia ha due atenei**, la statale e la sede della Cattolica; la statale da sola sottostima la popolazione universitaria. |

### Da verificare — promettenti ma non testate

INPS (lavoratori dipendenti per provincia e settore, retribuzioni per classi e
**cittadinanza**) · INAIL (infortuni, pertinente in un territorio industriale) ·
sezioni di censimento ISTAT (variabili censuarie a grana sub-comunale, 2011 e
2021, se si vorrà scendere sotto il comune) · mappatura acustica
dell'agglomerato · progetti PNRR da OpenPNRR (ODbL) · risultati elettorali per
sezione da Eligendo.

---

## 3. Le decisioni

### 3.1 Il soggetto — ✅ deciso (agosto 2026)

**La provincia di Brescia è il soggetto principale**, con il **capoluogo come
caso privilegiato**: gli si dedicano una o due analisi tutte sue, ma il fuoco
resta sul territorio.

Conseguenze operative:

- l'unità di default di ogni mappa e di ogni classifica sono i **205 comuni**;
- il capoluogo compare come *uno dei* comuni, non come protagonista implicito —
  e siccome è un ordine di grandezza sopra tutti gli altri, va gestito come
  outlier dichiarato nelle scale di colore e nelle correlazioni (MET-5);
- gli aggregati provinciali servono da riferimento, non da soggetto;
- le due analisi dedicate al capoluogo sono indicate in `BRIEF.md`.

### 3.2 Gli assi — ✅ scelti (agosto 2026)

Quattro assi portanti, il resto come materiale di contorno. Il criterio è
duplice: qualità del dato **e** coerenza con il soggetto provinciale.
Motivazione e forma di ciascuno in [`BRIEF.md`](BRIEF.md).

| | Asse | Forma prevalente |
|---|---|---|
| **1** | Il lavoro e le imprese | coropletica sui 205 comuni + serie |
| **2** | Chi vive nel bresciano | coropletica + composizioni |
| **3** | Le due economie: manifattura e Garda | mappa bivariata + concentrazione |
| **4** | L'aria e il clima | **non una mappa**: 7 stazioni come sezione territoriale, più 52 stazioni meteo |

Di contorno, non abbandonati: sicurezza, casa e prezzi, commercio estero,
riqualificazione. Entrano se un asse portante li richiama, non per completezza.

### 3.3 Lingua

I documenti sono in italiano. Il progetto Donostia teneva la documentazione
tecnica in inglese e i relati in spagnolo, e la mescolanza ha prodotto attrito.
Meglio decidere una volta: **tutto in italiano** salvo i nomi delle colonne.

---

## 4. Dimensioni non ancora considerate

Idee emerse durante la ricognizione che nessuno ha ancora valutato.

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
  I dati di popolazione 2018–2024 ci sono già.

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
  coprono l'Italia intera: aggiungere Bergamo costa un filtro.

---

## 5. Come analizzare i dati

L'approccio del progetto precedente, che ha retto alla revisione esterna.

### Regole che hanno salvato il progetto

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
4. **Ogni numero citato deve avere uno script dietro.** Nel progetto
   precedente ogni cifra dei testi era riproducibile da `analysis/*.py`.
5. **Una scheda di confidenza per indicatore**: `osservato` (misurato
   direttamente), `derivato` (calcolato da altri), `proxy` (approssimazione),
   più le assunzioni esplicite. Nell'interfaccia diventa un distintivo
   visibile, non una nota a piè di pagina.

### Analisi che avevano dato i risultati migliori

Riadattate al caso bresciano:

- **Velocità di cambio**: tassi annualizzati per comune fra il primo e
  l'ultimo anno di ogni serie. Distingue «dov'è alto» da «dove sta cambiando in
  fretta», che è quasi sempre la domanda più interessante.
- **Livelli contro variazioni**: uno scatter con il livello sull'asse x e la
  variazione sull'asse y separa i comuni in quattro quadranti e rende visibile
  la polarizzazione.
- **Tipologia di comuni**: k-means con seme fisso su poche variabili
  (specializzazione settoriale, dimensione media d'impresa, reddito, densità).
  Da presentare **come profili descrittivi, mai come verità**.
- **Autocorrelazione spaziale**: i comuni contigui si somigliano? Con 205
  comuni e una geometria vera, qui ha molto più senso che con 19 barrios.
- **Rottura Covid**: 2020–2021 spezza quasi tutte le serie. Testare
  esplicitamente la discontinuità invece di far finta che non ci sia.
- **Decomposizione della popolazione**: quanto della variazione viene da saldo
  naturale, migrazione interna, migrazione estera.

Convenzione pratica: uno script per analisi in `analysis/`, con `--save` che
scrive CSV in `analysis/output/`, e le sole dipendenze `pandas` + `numpy`
(niente scipy o sklearn: si reimplementano k-means e le correlazioni in poche
righe e il progetto resta installabile ovunque).

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
  scala. Per Brescia questo è cruciale: 45 comuni hanno le presenze turistiche
  soppresse e uno ha uno zero fittizio.

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
   **`VITE_BASE: "/<nome-repo>/app/"`** — GitHub Pages serve da una
   sottocartella e senza questa variabile tutti gli asset danno 404;
3. assemblaggio: `mkdir -p _site/app`, copia di `web/dist/*` in `_site/app/`,
   copia del narrativo in `_site/index.html` **e** con il suo nome, copia delle
   pagine sorelle e dei CSV;
4. `actions/configure-pages` con `enablement: true`, poi
   `upload-pages-artifact` e `deploy-pages`.

Dettagli che costano tempo se non li sai:

- **Una volta sola**: *Settings → Pages → Source = «GitHub Actions»*. Il primo
  deploy fallisce se non è impostato.
- Permessi richiesti: `contents: read`, `pages: write`, `id-token: write`.
- `concurrency: { group: pages, cancel-in-progress: true }` evita che due
  deploy si accavallino.
- **Le date si stampano in fase di deploy**, non a mano: la data del sito viene
  dal commit, quella dei dati da un `manifest.json` che la pipeline scrive a
  ogni build completo. Nelle pagine ci sono i segnaposto `{{BUILD_DATE}}` e
  `{{DATA_DATE}}`, sostituiti dal workflow. Senza questo meccanismo le date
  invecchiano in silenzio e il sito mente.
- Decidere se il deploy è **automatico a ogni push su `main`** o **solo
  manuale** (`workflow_dispatch`). Il progetto precedente è partito manuale —
  per rileggere i testi prima di pubblicare — ed è passato ad automatico solo
  dopo che i contenuti si erano stabilizzati. Vale la pena rifare così.

**Test del documento narrativo.** Il progetto eseguiva l'HTML completo sotto
jsdom con vitest, verificando che lo scrollytelling, le etichette dei grafici
e la sincronia dei controlli funzionassero. Dopo ogni rigenerazione,
`npm test` diceva se qualcosa si era rotto. Su un file da 800 KB generato da
script è l'unica rete di sicurezza che regge.

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
che i relati erano scritti. Qui è già successo una volta: MET-9 («decomporre
prima di titolare») esiste solo perché un titolo sbagliato è stato scoperto e
corretto.

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

- **includere gli analisi che hanno smontato i propri risultati.** È la parte
  che quasi nessuno pubblica ed è quella che dà credibilità a tutto il resto.
  Qui c'è già il primo candidato (§6.1 della bozza).
- **una sezione esplicita su cosa i dati non permettono di dire.** Nel progetto
  Donostia è stata la più apprezzata dai revisori esterni.

### Ordine consigliato

1. completare i download e le analisi;
2. scegliere le storie e costruire le visualizzazioni;
3. **poi** riscrivere la nota metodologica, che a quel punto descrive decisioni
   davvero prese;
4. **infine** il working paper, che le sintetizza per un lettore esterno.

---

## 9. Le lezioni del progetto precedente

Cose imparate a caro prezzo, che non sono ovvie.

**Sulla struttura**

- **Una sola geometria di riferimento, un solo join in ingestione.** Il momento
  in cui si ammettono due geometrie «quasi uguali» è il momento in cui i numeri
  smettono di tornare. Qui la geometria è il comune e la chiave è il codice
  ISTAT: non inventare slug.
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
- **I dati mancanti non sono zeri**, e in questo progetto c'è già un caso in
  cui la fonte stessa confonde le due cose (lo `zero_fittizio` del turismo).

---

*Documento scritto ad agosto 2026 come consegna, prima della separazione del
repository. Lo stato dei dati e delle fonti è quello descritto in
[`FONTI.md`](FONTI.md); la pipeline funzionante è in
[`pipeline/`](pipeline/README.md).*
