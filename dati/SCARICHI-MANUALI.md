# I dati che tocca a te scaricare

> **Nota per Stefano.** Istruzioni operative per lo scarico che questo ambiente
> non raggiunge — ne resta **uno**, l'export Coeweb di §3 — più un comando da
> lanciare in locale, e la traccia di quelli già fatti: dove andare, cosa
> chiedere, dove mettere il file, cosa succede dopo. Il contesto sta in
> [`../PROSSIMI-PASSI.md`](../PROSSIMI-PASSI.md) §2.2, lo stato di accesso fonte
> per fonte in [`../FONTI.md`](../FONTI.md).
>
> **Erano cinque, e in un giorno sono diventati uno.** MUR e compravendite NTN
> sono tornati lavoro della pipeline perché quegli host hanno risposto (§5); gli
> open data del Comune di Brescia sono usciti dall'elenco per la ragione opposta,
> ed è quella che vale la pena leggere (§2); le quotazioni OMI sono **arrivate**
> (§1).

## La regola, prima delle istruzioni

Un file scaricato a mano **non va copiato in `dati/processed/`**. Va messo in
`dati/input/<fonte>/` col **nome originale**, e da lì lo legge la pipeline:
`processed/` contiene solo tabelle prodotte da uno script, `input/` gli input
curati che quello script consuma. La cartella nasce col primo file scaricato, ed
è versionata come `processed/` — un file che nessuno può riscaricare da un URL è
l'unico caso in cui il repository *è* la fonte.

Accanto al file, una riga di provenienza: URL esatto, data dello scarico,
formato ottenuto. Serve perché di questi file nessuno sa dire, guardandoli, se
siano quelli giusti: è la stessa ragione per cui `FONTI.md` porta uno stato di
accesso e non una promessa. Il modello è
[`input/omi/PROVENIENZA.md`](input/omi/PROVENIENZA.md), scritto quando è arrivato
il primo di questi file.

**Il nome originale ha un'eccezione, ed è già capitata:** se contiene un dato
personale, si rinomina. Gli archivi OMI arrivano col codice fiscale del
richiedente nel nome, e questo repository è pubblico — vedi §1.

**E soprattutto: non correggere i file a mano.** Se l'intestazione è sporca, se
lo zero iniziale è sparito, se l'encoding è latino — resta com'è, e lo sistema la
pipeline, dove la correzione è leggibile e ripetibile. Un CSV ripulito a mano è
un dato di cui nessuno conosce più la storia.

---

## 1. ✅ Quotazioni immobiliari OMI — fatto il 4 settembre 2026

> **Arrivate.** In [`input/omi/`](input/omi/PROVENIENZA.md): **22 semestri** di
> quotazioni (il 2° di ogni anno dal 2004 al 2025, già filtrate sulla provincia)
> e **15 anni** di volumi di compravendita comunali (2011–2025, nazionali).
> 5,7 MB di archivi versionati, 110.537 righe di quotazioni. La provenienza, i
> conteggi e le due avvertenze che ne sono uscite — le zone si accorpano nel
> tempo, i comuni erano 206 nel 2004 e 203 nel 2025 — stanno in
> [`input/omi/PROVENIENZA.md`](input/omi/PROVENIENZA.md).
>
> ⚠️ **Lezione per il prossimo scarico:** il servizio nomina gli archivi col
> **codice fiscale** di chi li richiede. Sono stati rinominati col periodo prima
> di entrare in git — il repository è pubblico. Chi riscarica il semestre 2026/1
> deve rifare la stessa cosa.

Le istruzioni restano qui sotto, perché fra sei mesi esce il 1° semestre 2026 e
la strada è la stessa.

**Perché tocca a te:** area riservata dell'Agenzia delle Entrate. Si entra con
SPID / CIE / CNS o con le credenziali Entratel/Fisconline. Il download è
gratuito.

**Dove:** <https://telematici.agenziaentrate.gov.it/Main/index.jsp> → accedi →
nel box dei servizi a sinistra *«Servizi ipotecari e catastali, Osservatorio
Mercato Immobiliare»* → **«Forniture dati OMI»**. Da lì si chiede per comune,
per provincia, per regione o per l'intero territorio nazionale.

**Cosa chiedere,** in ordine di utilità:

| | Cosa | Copertura verificata (4 set 2026) | Formato |
|---|---|---|---|
| **a** | **Quotazioni immobiliari**, provincia di Brescia | semestrale **dal 1° semestre 2004**; ultimo pubblicato **2° semestre 2025** (44 semestri) | CSV, due file per semestre: `…_VALORI_…` e `…_ZONE_…` |
| **b** | ✅ **Volumi di compravendita, dettaglio comunale** per settore di mercato — **scaricati** (15 anni, 2011–2025) | annuale **dal 2011** | CSV |
| **c** | **Perimetri delle zone OMI**, provincia di Brescia, semestre per semestre | **dal 2° semestre 2010** | KML |

**Quanti semestri prendere.** Se il servizio accetta una richiesta multipla,
tutti. Se costringe a un semestre per volta, prendi **il 2° semestre di ogni
anno dal 2004 al 2025**: ventidue file invece di quarantaquattro, e una serie
annuale regolare vale più di una semestrale con i buchi. Il 2025/2 va preso in
ogni caso, perché è il semestre a cui si riferiscono i perimetri che GeoPOI
distribuisce senza richiesta (<https://www1.agenziaentrate.gov.it/servizi/geopoi_omi/index.htm>).

**La (c) serve meno di quanto sembri.** Per una storia sui 205 comuni i
perimetri non servono affatto: i file delle quotazioni portano già il codice del
comune, quindi l'aggregazione comunale è un raggruppamento, non un incrocio fra
geometrie — e l'incrocio fra geometrie è il punto pericoloso di tutto l'asse
casa (§9 di `PROSSIMI-PASSI.md`). Le zone servono solo per **scendere sotto il
capoluogo**, e lì valgono la pena: la città di Brescia ha **26 zone OMI censite
e 23 quotate** nel 2025/2 (25 censite nel 2018/2), che è una grana da quartiere —
la stessa che in Donostia veniva dal barrio. Se il tempo è poco, (c) è la voce da
rinviare.

**Due cose da sapere prima di aprire i file** — verificate su un semestre già
aperto, vedi §5:

- la chiave del comune è `Comune_ISTAT` e per Brescia vale **`3017029`**: cifra
  della regione (3 = Lombardia) più il codice ISTAT a sei cifre. Non è il
  `codice_istat` del progetto (`017029`) e non si incrocia senza normalizzarlo.
  Lo farà la pipeline: è esattamente la lezione di MET-13;
- l'elenco dei comuni cambia da un semestre all'altro, perché segue il catasto:
  nel 2018/2 la provincia aveva 664 zone censite su 203 comuni, e nei 22
  semestri scaricati compare un comune che oggi non esiste più (Prestine, dal
  2016 territorio di Bienno). Non è un errore di scarico, ed è gestito nella
  pipeline invece di essere arrotondato — vedi
  [`input/omi/PROVENIENZA.md`](input/omi/PROVENIENZA.md).

**Obbligo di citazione:** «Agenzia Entrate - OMI». Va nel sito e in
`LICENSE-DATI`, non solo qui.

**Dove metterli:** `dati/input/omi/`, i KML in `dati/input/omi/zone/`.

**Tempo:** un'ora la prima volta, quasi tutta fra autenticazione e interfaccia.
Poi dieci minuti per semestre.

---

## 2. ✗ Open data del Comune di Brescia — il portale non esiste più

**Questa voce era scritta su una diagnosi sbagliata, e la correzione è la parte
utile.** «Non risponde dagli ambienti remoti, da una macchina italiana sì» era
una supposizione: il 4 settembre 2026 non ha risposto nemmeno dalla tua. Allora
l'ho guardata come si guarda un guasto, e non era un guasto:

- il DNS risolve — `dati.comune.brescia.it` → `91.192.127.7` — ma nessuna porta
  accetta connessioni;
- sul sito nuovo, `comune.brescia.it/opendata` risponde **410 Gone**: il codice
  con cui un server dichiara di aver rimosso una risorsa **per sempre**;
- l'ultimo passaggio dell'Internet Archive è di **gennaio 2021**;
- il sito del Comune, intanto, è stato rifatto sulla piattaforma condivisa di
  Regione Lombardia (nuovo IP) — e da qui adesso risponde 200, mentre ad agosto
  2026 dava 403.

Il portale CKAN del Comune è **dismesso**, e i suoi dataset sono **migrati su
`dati.lombardia.it`**: cercando `brescia` su `dati.gov.it` si trovano una
ventina di `comune-brescia-*` — media componenti per famiglia, elenco residenti,
nascite, decessi, matrimoni, incidenti stradali, fabbricati e terreni attivi —
censiti sotto Regione Lombardia, con le distribuzioni servite da
`dati.lombardia.it/api/views/<id>/rows.csv`. Quel portale la pipeline lo
interroga già da mesi: **quei dati non sono più tuoi, sono 🤖.**

**Quello che la migrazione non ha portato con sé,** e che quindi resta perduto:
il **flusso turistico a Brescia per nazionalità 2005–2013**, cioè il pezzo che
avrebbe esteso indietro la settima storia. Non è su `dati.lombardia.it` (le
quattro tabelle turistiche regionali cominciano tutte dal 2019, compresa
*Provenienza dei turisti nei comuni lombardi*, `c9ae-qhbj`, che è la più simile e
comincia esattamente dove quella finiva), e l'Internet Archive ha salvato solo
le pagine indice del portale: **nessuna risorsa CSV**.

**Se quella serie ti interessa davvero, l'unica strada è umana**: chiederla
all'ufficio statistica del Comune, che i dati li ha (i PDF di *Indicatori
Demografici* e *Popolazione residente per quartiere* sono ancora pubblicati su
`comune.brescia.it/it/documenti_pubblici/statistica-demografica`, e li scarico
io). È una mail, non un download — e se la risposta non arriva, la settima
storia resta quella che è: dichiarata dal 2019, che è quanto la fonte copre.

**Dove metterli, se arrivano:** `dati/input/comune_brescia/`.

---

## 3. Commercio estero provinciale — un export a mano dal databrowser

**Perché tocca a te:** il portale storico `coeweb.istat.it` è dismesso dal 30
settembre 2025. Il sostituto <https://esploradati.istat.it/coeweb/databrowser/>
risponde — verificato il 4 settembre 2026, HTTP 200 — ma è una single-page
application: consultabile dal browser, senza un endpoint SDMX che io riesca a
raggiungere. L'export lo fa l'interfaccia, e l'interfaccia vuole un umano.

**Cosa esportare:** territorio **Brescia**, e tre tagli, dal più utile:

1. **esportazioni e importazioni totali verso il mondo**, la serie annuale più
   lunga disponibile;
2. lo stesso **per raggruppamento merceologico** (CPA Ateco 2007, dieci voci);
3. lo stesso **per i primi paesi partner** — non tutti e 320: i primi venti
   coprono la storia, e l'export completo rischia il tetto di righe
   dell'interfaccia.

Se l'interfaccia taglia l'export, **spezzalo per dimensione** — un file per
taglio — invece di accorciare gli anni: la lunghezza della serie è il punto.

**La cosa da non fare.** Non mescolare questi numeri con la serie **regionale**
già in `dati/processed/commercio_estero_lombardia.csv`. Sono due grane dello
stesso fenomeno: stanno in due frasi diverse, mai nella stessa. È MET-17, ed è
nata da un errore vero sul turismo. Finché il provinciale non c'è, la scelta
attuale — dichiarare la Lombardia come contesto — regge (MET-10).

**Dove metterli:** `dati/input/coeweb/`.

**Tempo:** un'ora, quasi tutta spesa a capire l'interfaccia.

---

## 4. `migrazioni_comuni.csv` — non è uno scarico, è un comando

Nessun login e nessuna rete particolare: è solo un file da 422 MB che sta fuori
da git.

```bash
pip install -e ./pipeline
python -m brescia_pipeline.build migrazioni
```

Venti minuti e ~2 GB liberi per le risposte grezze. Il perché, e le due strade
per versionarlo un giorno, stanno in [`SCARICHI-LOCALI.md`](SCARICHI-LOCALI.md).

---

## 5. Le due voci che non sono più tue

Il 4 settembre 2026 ho riprovato tutti gli host di questo elenco. Due hanno
risposto, e quindi sono tornati lavoro della pipeline:

- **MUR, i due atenei.** `dati-ustat.mur.gov.it` risponde, ed è un CKAN vero:
  `api/3/action/package_search?q=iscritti` restituisce 31 dataset, e quello
  chiamato `iscritti` ne ha 24 risorse. Iscritti e laureati per ateneo si
  scaricano da qui. L'avvertenza resta, e non la risolve nessuna API: **Brescia
  ha due atenei**, la statale e la sede della Cattolica, e la statale da sola
  sottostima la popolazione universitaria.
- **Compravendite NTN, provincia e capoluogo.** Non stanno dietro il login: la
  pagina pubblica *Volumi di compravendita* distribuisce direttamente
  `RESIDENZIALE_DEFINITIVO_2011_2024.zip`,
  `NON_RESIDENZIALE_DEFINITIVO_2011_2024.zip` e i provvisori 2025–2026 — serie
  **trimestrale dal 1° trimestre 2011**, dettaglio provinciale e di capoluogo.
  È esattamente la grana del progetto. Dietro il login resta solo il **dettaglio
  comunale** per settore di mercato, che è la voce (b) di §1.

Una terza mezza notizia, che però non cambia niente: le quotazioni OMI
**2016/1–2018/2** esistono già aperte, rielaborate da onData APS
(`github.com/ondata/quotazioni-immobiliari-agenzia-entrate`, CSV in UTF-8 con le
intestazioni sistemate — sono quelli su cui ho verificato i conti di §1). Il
resto di quel repository sta in archivi `.7z`, che questo progetto non apre
senza aggiungere una dipendenza, e comunque la raccolta si ferma al 2018. Tre
anni non sono una serie: il login di §1 resta la strada.

---

## Quando il file è arrivato

1. Mettilo in `dati/input/<fonte>/` col nome originale, senza ritoccarlo.
2. Scrivi accanto la riga di provenienza: URL, data, formato.
3. **Dimmelo.** Da lì tocca alla pipeline: un modulo in
   `pipeline/src/brescia_pipeline/datasets/`, una tabella in `dati/processed/`,
   la riga in [`README.md`](README.md) e la fonte aggiornata in `FONTI.md` con lo
   stato **verificata ✓** e la prova accanto.

E un vincolo che vale per tutti: **finché un dato non è nel repository, nessuna
cifra pubblicata può dipendere da lui.** Vale per
`migrazioni_comuni.csv` oggi e varrà per l'OMI domani — se una storia del sito
cita un numero, `analysis/verifica_cifre.py` deve poterlo ricalcolare da una
tabella versionata.
