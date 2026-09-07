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
| ✗ | **caduta**: la fonte non esiste più, e la voce resta scritta perché sapere che un dato è perduto vale quanto averlo |

Le voci 🙋 non sono bloccanti per il grosso del progetto: i quattro assi
portanti hanno già tutti i dati che servono. Sono estensioni e finiture.

## Le cose che tocca a te — tutte, in un posto solo

La licenza è scelta (§3.3) e la sorgente di Pages è a posto dal 4 settembre
2026, quindi per pubblicare resta **un clic**, e non è tecnico: il cancello che
decide quando il sito diventa visibile. Il resto si costruisce da solo a ogni
push su `main`. Sopra a quel clic c'è una **decisione di disegno** aperta da
settembre 2026, che non blocca niente ma è l'unica cosa in questo elenco che
nessuno può prendere al posto tuo perché riguarda due repository insieme.

| | Cosa | Perché tocca a te | Tempo | Blocca |
|---|---|---|---|---|
| ✅ 2 | ~~**Correggere la sorgente di GitHub Pages**~~ (§7) — **fatta il 4 settembre 2026**: *Source* è su «GitHub Actions», e il workflow ha finalmente dove pubblicare | serviva il tuo accesso da proprietario del repo | 2 min | niente più |
| 🙋 9 | **Pubblicare**, quando l'analisi sarà finita (§7): *Actions → «Pubblica il sito» → Run workflow → conferma = `pubblica`* | è la decisione di pubblicare, e non la prende un workflow | 1 min | che il sito diventi visibile. Prima di allora si costruisce a ogni push e resta un artefatto da scaricare |
| ✅ 3 | ~~**Scaricare le quotazioni OMI**~~ — **fatta il 4 settembre 2026**: 22 semestri (2004–2025) più le compravendite comunali 2011–2025, in [`dati/input/omi/`](dati/input/omi/PROVENIENZA.md). Restano da chiedere solo i perimetri KML, se un giorno si scenderà sotto il capoluogo | serviva il tuo SPID: era l'unico scarico del progetto con un login | 1 h | niente più: l'asse «casa e prezzi» ha i dati, gli manca la pipeline (🤖) |
| ✗ 4 | ~~**Scaricare gli open data del Comune di Brescia**~~ — **la voce cade** (4 settembre 2026): il portale è dismesso, non irraggiungibile ([perché](dati/SCARICHI-MANUALI.md) §2) | non era la nostra rete: `comune.brescia.it/opendata` risponde `410 Gone`. I dataset sono su `dati.lombardia.it`, quindi 🤖; il turismo cittadino 2005–2013 non è migrato e resta perduto | — | niente, tranne l'estensione indietro della settima storia, che va dichiarata come non disponibile |
| 🙋 6 | **Esportare a mano il commercio estero provinciale** (§2.2, [istruzioni](dati/SCARICHI-MANUALI.md) §3) | il databrowser ISTAT è una SPA senza API | 1 h | niente: la serie regionale è già scaricata come ripiego dichiarato |
| 🙋 7 | **Rileggere i testi prima di pubblicare** (§8) | è il tuo nome sopra | — | la pubblicazione |
| 🙋 8 | **Scaricare in locale `migrazioni_comuni.csv`** ([istruzioni](dati/SCARICHI-LOCALI.md)) | 422 MB: sta fuori da git, e serve solo quando l'asse 2 diventerà una storia | 20 min di attesa | niente di quello che è pubblicato |
| 🙋 10 | **Dire se la tavolozza va riallineata con `donostia-dataviz`** ([`sito/README.md`](sito/README.md) §Lo stile) | le storie qui sono sette e i colori ereditati sono cinque, quindi ne sono stati aggiunti due (`--oliva` e `--prugna`), con accanto la **regola** che li sceglie: il buco di tinta più largo che resta, alla luminosità della famiglia. Qui il sito è coerente; la domanda che resta tua riguarda la lingua grafica **condivisa fra i due progetti** — tenerli una collana stretta o lasciarli divergere | 10 min per dire di sì com'è, mezz'ora se porti regola e toni anche nell'altro repository | niente |

🤖 **Tre voci non sono più tue, e per due ragioni diverse.** Il 4 settembre 2026
ho riprovato gli host di questo elenco uno per uno. La 🙋 5 e metà della 🙋 3
sono cadute perché gli host hanno risposto: `dati-ustat.mur.gov.it` è un CKAN
funzionante, e le **compravendite NTN a grana provinciale e di capoluogo** sono
pubblicate in chiaro sul sito dell'Agenzia — dietro il login resta solo il
dettaglio comunale. La 🙋 4 è caduta per il motivo opposto: il portale open data
del Comune **non esiste più** (`410 Gone`), i suoi dataset sono migrati su
`dati.lombardia.it` — che la pipeline interroga da mesi — e la serie turistica
cittadina 2005–2013 non è migrata con loro. Dettagli in §2.1, §2.2 e in
[`dati/SCARICHI-MANUALI.md`](dati/SCARICHI-MANUALI.md) §2 e §5. I numeri liberati
non sono stati riusati, perché questo documento viene citato per numero.

Tutto il resto di questo documento è 🤖 o ✅. Questa tabella è ripetuta in forma
breve in testa al [`README`](README.md), diviso fra ciò che blocca la
pubblicazione e ciò che no: se ne aggiungi una voce qui, va aggiunta anche lì —
un elenco che promette di essere completo e non lo è vale meno di nessun elenco.

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
| Pipeline | ✅ funzionante, `requests` + libreria standard |
| Test | ✅ **452 test verdi** e **85 % di copertura** su tutti e tre i pezzi di codice — pipeline, i sedici script di `analysis/`, il costruttore del sito. La soglia dell'80 % sta in [`.coveragerc`](.coveragerc) e fa fallire la CI, non stampa un avviso. Fuori dal conto resta `grafici.js`, che non ha test automatici ([`pipeline/README.md`](pipeline/README.md) §I test) |
| Base geografica | ✅ i confini dei 205 comuni in GeoJSON, verificati contro l'area nota della provincia |
| Tabelle tidy | ✅ **31 CSV** in [`dati/processed/`](dati/README.md), versionati — tre vengono dall'OMI (quotazioni in grana zona e comunale, volumi di compravendita 2011–2025) e la trentunesima è il **deflatore** `indice_prezzi.csv`, che è arrivato per leggerle; manca solo `migrazioni_comuni.csv` |
| Asse «casa e prezzi» | ✅ **completo**: i dati (quotazioni OMI 2004–2025 in due grane, compravendite 2011–2025), l'analisi (`casa_e_prezzi.py`, §4) e la **storia** — l'ottava del sito. Prezzo reale −30,8 % in ventun anni mentre i volumi fanno +134,5 % |
| Analisi | ✅ **quindici** script in [`analysis/`](analysis/README.md): velocità di cambio, quadranti, autocorrelazione, tipologia, le due economie, la scomposizione del capoluogo, la rottura del 2020, il confronto fra le 107 province, la scomposizione demografica, l'aria e il clima, il turismo confrontato con le altre province, e da settembre la **casa** — prezzi contro volumi, le zone del capoluogo, i 203 comuni quotati |
| Storie scelte | ✅ **otto**, scritte e pubblicate nel documento narrativo — la quinta corregge quelle che la precedono, la settima è l'unica che nessuno si aspettava, l'ottava è la più lunga e la sola in cui il risultato dipende da come si misura. Le candidate rimaste stanno in `BRIEF.md` |
| Contratto dati per il sito | ✅ `metric_*.json` + registro, con i cinque invarianti come test |
| Documento narrativo | ✅ [`sito/`](sito/README.md), un file HTML autocontenuto da mezzo mega. Riletto a settembre 2026 riga per riga: le **centoundici lineette lunghe** sono uscite dal testo pubblicato (un test le tiene fuori, `pipeline/tests/test_testi.py`), e i grafici sono stati passati in un browser headless — zero errori JS, zero attributi malformati, niente fuori dal riquadro, con tutti i comandi premuti |
| Pannello interattivo | ✅ **fatto** (settembre 2026), e non come la specifica lo prevedeva: è `sito/modelli/esplora.html`, una quarta pagina dello stesso sito autocontenuto, non un'app React servita sotto `/app/`. Tutti e **diciannove** gli indicatori del registro — non i quindici del racconto — su tutti i comuni, con l'anno a scelta, il ritratto del comune cliccato e ogni scelta nell'indirizzo. Il perché della differenza sta in §6.1 |
| Deploy | 🤖 la **costruzione** è automatica su `main` (test, cifre, sito, artefatto); la **pubblicazione** no: parte solo a mano, con una conferma scritta (§7). ✅ la sorgente di Pages è su «GitHub Actions» dal 4 settembre 2026, quindi il primo lancio ha dove pubblicare |
| Licenza | ✅ MIT per il codice (`LICENSE`), CC BY 4.0 per testi e dati (`LICENSE-DATI`) (§3.3) |
| `METODOLOGIA.md` | ✅ **versione 1.1**, non più bozza: **ventisette** regole. Cinque delle ultime sei (MET-22…MET-26) sono quelle che il documento dichiarava mancanti da sempre — come si **scelgono** e si **raccontano** le storie — e sono state ricavate contando cosa le otto storie hanno fatto davvero, non decise a tavolino. MET-23 è nata insieme alla scoperta che quattro storie su otto la violavano; **MET-27** è arrivata dopo, dal prodotto invece che dall'analisi |
| `WORKING-PAPER.md` | ✅ **versione 1.1**, non più bozza. Ha il titolo che gli mancava, perché ha la tesi: «Il numero giusto, la frase falsa» — **undici** episodi in cui un dato corretto stava per produrre un'affermazione falsa, in quattro famiglie. Otto scoperti dopo averli commessi, tre prima. L'undicesimo è nato costruendo la pagina che esplora. La §7 resta la parte sui risultati: nove, sui cinque assi |

**Dove sta il progetto, in una frase.** I dati ci sono, le analisi sono state
fatte e otto storie sono scritte in un sito che si costruisce da solo, e adesso
ha anche dove pubblicarsi: **manca la tua rilettura, e il clic che pubblica**.
Il lavoro tecnico che resta è tutto facoltativo: i download manuali. Il
pannello interattivo, che era la voce grossa, **è stato fatto** a settembre
2026 (§6.1).

---

## 2. Cosa resta da scaricare

Lo stato completo, fonte per fonte, è in [`FONTI.md`](FONTI.md). Qui solo ciò
che manca.

### 2.1 Le fonti automatiche — ✅ chiuse

| Cosa | Stato |
|---|---|
| **Confini comunali** | ✅ `datasets/confini.py` + `geo.py`, con lettore di shapefile e riproiezione in libreria standard: niente `pyshp`, per lo stesso motivo per cui §5 reimplementa k-means. Prodotti `dati/geo/comuni_brescia.geojson` e `comuni_geometria.csv`, verificati contro l'area nota della provincia e contro lo `Shape_Area` di ISTAT |
| **Background migratorio** | ✅ scaricato — dieci tavole `DF_DCSS_MIGR_BACKG_PAR_TV_*_COM`. Erano «le più pesanti di tutte», e lo erano solo perché si scaricava l'Italia intera: con le chiavi a blocchi sono venti minuti. ⚠️ Ma la tabella prodotta **non è versionata**: vedi il riquadro qui sotto |
| **Sezioni Ateco per comune** | ✅ `imprese_sezioni_comuni.csv` — **nuovo**, ed è quello che ha sbloccato l'asse 3: vedi il riquadro qui sotto |
| **Settore × classe dimensionale** | ✅ `imprese_settore_classe.csv` — **nuovo**, capoluogo e provincia: è la tabella che ha chiuso MET-9 |
| **Abitazioni** | ✅ `abitazioni_comuni.csv` — `DF_DCSS_ABITAZIONI_TV_1` e `_TV_2` |
| **Famiglie con stranieri** | ✅ `famiglie_comuni.csv` — `DF_DCSS_FAMIGLIE_TV_1`, `_TV_2`, `_TV_3` |

Le ultime tre erano rimaste indietro perché `esploradati.istat.it` aveva
smesso di accettare connessioni a metà lavoro. **Non era un bug del codice: era
quell'host**, ed è tornato su. Rilanciarle costa un comando e, da quando le
chiavi vanno a blocchi, pochi minuti invece di ore:

```bash
python -m brescia_pipeline.build migrazioni abitazioni famiglie
```

> ~~**Scoperta che vale la pena tenere per iscritto.** La chiave SDMX con più
> codici nella stessa dimensione non fallisce per lunghezza dell'URL: il server
> proprio non accetta la sintassi `codice+codice` lì. Scaricare l'Italia intera
> e filtrare in locale non è una comodità, è l'unica strada.~~
>
> ⚠️ **Era falso, ed è costato caro.** Quel `400` era una chiave con il numero
> di campi sbagliato: i dataflow censuari hanno nove dimensioni, e con otto
> punti rispondono `422 expecting 9 got 8` — che senza guardare il corpo della
> risposta sembra un rifiuto della sintassi. Con il numero giusto di campi,
> **quindici comuni per richiesta passano**: 1,6 MB e nove secondi. Le dieci
> tavole sulle migrazioni passano da otto gigabyte e nove ore a duecento
> megabyte e venti minuti. Dettaglio in `FONTI.md` §10 punto 6, e la ricetta in
> `datasets/_censimento.py`.
>
> La cosa che avrebbe dovuto far sospettare: `redditi.py` usava i blocchi da
> sempre, sotto gli occhi di tutti.

> 🤖 **Una decisione da prendere: che forma dare a `migrazioni_comuni.csv`.**
> Scaricato, è **1,8 milioni di righe e 422 MB** — la distribuzione congiunta di
> sei dimensioni censuarie su 205 comuni, con le etichette italiane ripetute per
> esteso su ogni riga. Le altre tabelle del progetto stanno fra le cinquemila e
> le quarantamila righe.
>
> Per ora è **esclusa da git** (`.gitignore`, con la motivazione accanto) e si
> rigenera in venti minuti. Nessuna delle otto storie pubblicate la usa, quindi
> non blocca niente. Le due strade, quando l'asse 2 verrà affrontato:
>
> - **codici al posto delle etichette**, più una legenda in una tabella a parte.
>   È anche la forma giusta a prescindere (MET-13: le etichette cambiano lingua),
>   e taglia il file di circa tre quarti — ma resta grosso;
> - **solo le marginali che servono**, cioè le poche combinazioni che l'asse 2
>   userà davvero, tenendo il resto in `dati/raw/`.
>
> La seconda è quasi certamente quella giusta, ma va scelta guardando la storia
> che si vuole raccontare, non prima. **Istruzioni per rifarla in locale, e il
> ragionamento per esteso, in [`dati/SCARICHI-LOCALI.md`](dati/SCARICHI-LOCALI.md).**

> **E il seguito, che vale ancora di più** (agosto 2026). Il vincolo è **solo**
> sulla dimensione territoriale, e si aggira da due lati opposti:
>
> - **territorio libero, settore fisso** — una richiesta per sezione Ateco su
>   tutta Italia (una dozzina di MB, una ventina di secondi l'una), filtro sui
>   205 comuni in locale. Diciassette sezioni per due indicatori sono
>   trentaquattro richieste e un quarto d'ora, e da lì viene
>   `imprese_sezioni_comuni.csv`: **la specializzazione settoriale di tutti i
>   comuni**, che era data per impossibile e senza la quale l'asse 3 del brief
>   non si poteva disegnare;
> - **territorio fisso, tutto il resto libero** — mezzo mega di risposta per il
>   capoluogo con settore *e* classe dimensionale insieme. È
>   `imprese_settore_classe.csv`, quattro richieste in tutto, ed è la tabella
>   che ha chiuso MET-9 dopo mesi.
>
> Morale: prima di dichiarare impossibile un incrocio, provare a fissare
> **l'altra** dimensione. Le due ricette sono in `datasets/sezioni.py` e in
> `datasets/imprese.py`.

### 2.2 🙋 Le fonti che richiedono te

Nessuna di queste tocca i quattro assi portanti. Sono le estensioni. Le
**istruzioni operative** — dove andare, cosa chiedere, dove mettere il file —
stanno in [`dati/SCARICHI-MANUALI.md`](dati/SCARICHI-MANUALI.md); qui resta il
perché.

| | Cosa | Ostacolo | Come si supera |
|---|---|---|---|
| ✅ 3 | **Quotazioni immobiliari OMI** — **acquisite** il 4 settembre 2026 | area riservata Agenzia delle Entrate (SPID/CIE/Fisconline, gratuito) | Fatto: 22 semestri, il 2° di ogni anno **dal 2004 al 2025**, filtrati sulla provincia, più i volumi di compravendita comunali 2011–2025. Stanno in `dati/input/omi/` come archivi zip, letti dalla pipeline con `zipfile`. Le quotazioni sono libere **dal 1° semestre 2004** e l'ultimo pubblicato è il **2° semestre 2025**. I perimetri delle zone (KML, dal 2010/2) servono **solo** per scendere sotto il capoluogo — a grana comunale il file delle quotazioni porta già il codice del comune, quindi la seconda geometria, che è il punto pericoloso di §9, non entra affatto. Le **compravendite NTN** non sono più qui: vedi §2.1 |
| ✗ 4 | **Open data del Comune di Brescia** — **voce chiusa**, non rinviata | il portale CKAN è **dismesso**: DNS che risolve ma nessuna connessione, `comune.brescia.it/opendata` a `410 Gone`, ultimo passaggio dell'Internet Archive a gennaio 2021. Ad agosto 2026 lo avevamo letto come un problema di rete, e non lo era | I dataset comunali sono **migrati su `dati.lombardia.it`** (una ventina di `comune-brescia-*`, censiti su `dati.gov.it` sotto Regione Lombardia): sono 🤖. Il **turismo cittadino 2005–2013** non è nella migrazione né nell'Internet Archive — la sola strada che resta è chiederlo all'ufficio statistica del Comune, il cui sito intanto **ha riaperto** (200, era 403) |
| 🙋 6 | **Commercio estero provinciale** | il portale Coeweb storico è dismesso (confermato: l'host non risponde), il sostituto è una SPA senza API | Esportare a mano dal databrowser via browser e versionare come input curato. In alternativa restare sulla serie **regionale**, già scaricata, dichiarandola — che è la scelta attuale e regge (MET-10) |

Quando arriva un file scaricato a mano, **non va copiato in
`dati/processed/`**: va messo in `dati/input/<fonte>/` col nome originale e
passato dalla pipeline, così resta tracciabile da dove viene. È la stessa regola
della provenienza esplicita di §9, e sta scritta per intero in
[`dati/SCARICHI-MANUALI.md`](dati/SCARICHI-MANUALI.md).

> **Due host hanno riaperto** (4 settembre 2026). Erano nell'elenco delle cose
> che richiedevano Stefano, e non ci sono più:
>
> - **MUR — atenei.** `dati-ustat.mur.gov.it` risponde, ed è un CKAN vero:
>   `api/3/action/package_search?q=iscritti` dà 31 dataset e quello chiamato
>   `iscritti` ne ha 24 risorse. Iscritti e laureati per ateneo si scaricano da
>   qui, con l'avvertenza che nessuna API risolve: **Brescia ha due atenei**, la
>   statale e la sede della Cattolica, e la statale da sola sottostima la
>   popolazione universitaria.
> - **Compravendite NTN, provincia e capoluogo.** Non stanno dietro il login: la
>   pagina pubblica *Volumi di compravendita* dell'Agenzia distribuisce
>   direttamente `RESIDENZIALE_DEFINITIVO_2011_2024.zip`, il gemello non
>   residenziale e i provvisori 2025–2026 — serie **trimestrale dal 1° trimestre
>   2011**, dettaglio provinciale e di capoluogo, che è esattamente la grana del
>   progetto. Dietro il login resta solo il dettaglio **comunale** per settore di
>   mercato.
>
> Nessuna delle due è ancora scritta come modulo: sono da fare, ma sono 🤖.

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

### 2.4 ✅ Le etichette censuarie sono in italiano

Nelle tabelle che venivano dall'SDMX di ISTAT le **modalità** delle dimensioni
erano in inglese: `private households on 31st December`, `15 years and over`,
`4 and over`. Riguardava `famiglie_comuni.csv`, `abitazioni_comuni.csv` e
`censimento_lavoro_brescia.csv`, cioè le tavole censuarie scaricate per prime, e
stonava con la decisione di §3.4 di tenere tutto in italiano salvo i nomi delle
colonne.

**Non era una scelta, era un header mancante.** ISTAT risponde in italiano se la
richiesta porta `Accept-Language: it`, e l'header è in `fetch.py` con i test che
lo verificano.

✅ **Chiuso a settembre 2026.** Le tre tavole rimaste indietro sono state
riscaricate e sono in italiano: «famiglie con almeno uno straniero residente al
31 dicembre», «15 anni e più», «tutte le voci». Con la cache di `dati/raw/`
vuota — che è la condizione normale di un ambiente di lavoro fresco, visto che
`raw/` non è versionata — non è servito nessun `force`: sono bastati venti
minuti di `build lavoro abitazioni famiglie`, non le ore che questa riga
prometteva. **Su una macchina dove la cache esiste, invece, il `force` serve
ancora**, perché un file grezzo già scaricato non porta traccia della lingua con
cui è arrivato.

Una cosa da sapere prima di guardare il diff: in `abitazioni_comuni.csv`
cambiano anche **1.640 valori**, e non è la fonte che si è mossa. È
l'**ordinamento**: «abitazioni non occupate» viene prima di «abitazioni
occupate» in italiano, mentre `occupied` veniva prima di `unoccupied` in
inglese. I totali per anno e per tavola coincidono all'unità. È la stessa
ragione per cui `redditi.py` filtra sui codici e non sulle etichette (MET-13),
vista da un'altra angolazione: **l'etichetta non è una chiave**, nemmeno per
ordinare.

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
| **4** | L'aria e il clima | **non una mappa**: il confronto è fra inquinanti e fra epoche, sulle sole stazioni osservate in tutti gli anni (MET-16) | ✅ completi, ✅ **e adesso ha la sua storia** — la sesta |

Di contorno, non abbandonati: sicurezza, casa e prezzi, commercio estero,
riqualificazione. Entrano se un asse portante li richiama, non per completezza.

### 3.3 La licenza — ✅ **decisa**

**Codice MIT** ([`LICENSE`](LICENSE)), **testi e dati CC BY 4.0**
([`LICENSE-DATI`](LICENSE-DATI)), più una sezione nel `README`. CC BY 4.0 è la
più permissiva fra le licenze Creative Commons che chiedono l'attribuzione:
riuso libero, anche commerciale, purché si citi la fonte e si dichiarino le
modifiche.

La scelta soddisfa gli obblighi delle fonti **attualmente** usate, che sono
aperte ma con obblighi di citazione diversi:

| Fonte | Obbligo |
|---|---|
| ISTAT, Regione Lombardia | CC-BY: attribuzione |
| Agenzia delle Entrate (OMI) | citazione obbligatoria «Agenzia Entrate - OMI» |
| OpenStreetMap | ODbL: **share-alike sui dati derivati** |
| OpenPNRR | ODbL, stessa conseguenza |

Oggi nel repository non c'è un solo dato OpenStreetMap né PNRR, e la geometria
viene da ISTAT: l'ODbL non è in gioco. ⚠️ **La decisione va rifatta se un
giorno si aggiungono** (§2.3) — lo share-alike sui derivati contagerebbe le
tabelle, e CC BY 4.0 sulle tabelle non basterebbe più.

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
- ✅ **I distretti**: fatto, ed è stata la sorpresa della tornata. La
  specializzazione settoriale per comune **si può scaricare** (§2.1), e da lì
  vengono `analysis/due_economie.py` e `analysis/tipologia_comuni.py`. Resta da
  fare la parte fine: i distretti veri sono di divisione, non di sezione — la
  Val Trompia è la divisione 25, non «la manifattura» — e la ricetta per
  scaricare una divisione è la stessa.

**Sul territorio**

- ✅ **Odolo, 89,6 addetti ogni 100 abitanti** — e Limone sul Garda 133:
  `analysis/dove_si_lavora.py`. Le cause opposte adesso si **mostrano** invece
  di raccontarle: Limone ha il 71 % degli addetti in alloggio e ristorazione,
  Odolo l'81 % nella manifattura.
- **Lo spopolamento montano**: Valle Camonica e Valle Sabbia contro la pianura.
  Il primo sguardo c'è già ed è netto — `analysis/variazione_popolazione.py`
  dice che **93 comuni su 205 perdono popolazione fra il 2018 e il 2024**, e
  che le dieci cadute più rapide sono tutte di montagna (Magasa −2,9 % l'anno,
  Lozio, Berzo Demo, Paisco Loveno, Saviore dell'Adamello), mentre la provincia
  nel suo complesso cresce dello 0,15 % l'anno. È materiale per una storia,
  non ancora una storia: mancava la decomposizione fra saldo naturale e
  migrazione. ✅ È diventata **la prima storia del sito**, con la mappa e
  l'indice di Moran (0,34: i comuni che si svuotano confinano fra loro), e la
  decomposizione **c'è**: `analysis/decomposizione_popolazione.py`. Il risultato
  ribalta la parola — sui 93 comuni in calo la migrazione interna sommata vale
  −66 persone contro −10.163 di saldo naturale, cioè non se ne va nessuno, ci si
  muore — ed è diventata MET-15.

**Sull'ambiente**

- **Il sito contaminato Caffaro** a Brescia (PCB): una vicenda che dura da
  decenni, con dati ARPA e studi di ATS. È l'incrocio più diretto fra storia
  industriale e salute pubblica di tutto il progetto.
- **L'isola di calore** via Landsat (l'endpoint STAC di Microsoft Planetary
  Computer è verificato e anonimo). In pianura padana il contrasto
  centro/periferia è più marcato che altrove.
- **Il termovalorizzatore e il teleriscaldamento**, fra i più estesi d'Italia.

**Sulla casa** — ✅ **fatta**: `analysis/casa_e_prezzi.py`, settembre 2026. Le
tre domande erano queste, e hanno tutte una risposta.

- ✅ **Prezzi contro volumi**, e il controllo che mancava. In euro correnti il
  metro quadro del capoluogo fa **+2,3 % in ventun anni** — 1.788 € nel 2004,
  1.829 € nel 2025 — e sembra un mercato fermo. In **euro 2025** fa **−30,8 %**:
  quei 1.788 € del 2004 sono 2.642 € di oggi. Nello stesso periodo i volumi
  crescono: dal fondo del 2013 al 2025 l'NTN residenziale fa **+134,5 %**. Le
  due serie non si contraddicono — *si vende molto di più a un prezzo reale
  molto più basso* — ed è una frase che nessuna delle due dice da sola. Il
  controllo sull'inflazione ha prodotto il deflatore che al progetto mancava
  (`indice_prezzi.csv`) e **MET-20**.
- ✅ **Il capoluogo per zona**, con una sorpresa sul metodo. La domanda del
  barrio — il centro si è staccato dalla periferia? — ha risposta **no, il
  contrario**: sul panel bilanciato la forbice fra la zona più cara e la più
  economica passa da **2,21 nel 2004 a 1,97 nel 2025**, e chi partiva più caro
  ha perso di più (−0,38 Pearson / −0,53 Spearman fra livello iniziale e
  variazione reale, su tredici zone). ⚠️ Il perimetro **non è costante e cambia
  proprio qui**: nel 2024 la zonizzazione del capoluogo viene rifatta, dieci
  zone finiscono nel 2023 e dieci cominciano nel 2024. Le medie annue restano su
  23 zone quotate ma non sono le stesse 23, quindi il confronto lungo si fa sul
  panel delle **tredici presenti in tutti e ventidue i semestri**. È MET-16
  applicata alle zone invece che alle centraline.
- ✅ **La provincia**, e il vertice non è la città. Il capoluogo è **18° su 203**
  comuni quotati: sopra ci sono il Garda e l'alta montagna, cioè il turismo — lo
  stesso risultato di `dove_si_lavora.py` visto dal lato della casa. Il prezzo
  si accompagna al reddito (+0,52 / +0,50), meno agli addetti (+0,33 / +0,35), e
  sulla popolazione **Pearson e Spearman divergono** (+0,18 contro +0,58): la
  relazione fra rango c'è, quella lineare la schiaccia il capoluogo. Il
  leave-one-out di MET-5 sui quattordici comuni gardesani non sposta niente,
  quindi nessuna delle tre relazioni è fatta dal Garda.

Cosa resta su questo asse, tutto 🤖 — la storia ✅ **è stata scritta** e sta nel
sito (l'ottava, `#casa`). Restano gli **affitti** — che questo script non
tocca perché la base di superficie cambia nel 2025 (MET-19) e vanno letti in due
tratti — e l'incrocio con lo **stock abitativo** censuario, cioè quante case
vuote ci sono dove i prezzi sono caduti di più.

**Sul metodo**

- **Confrontare Brescia con Bergamo**: due province gemelle, stessa Capitale
  della cultura 2023, storie industriali parallele. Tutte le fonti usate qui
  coprono l'Italia intera: aggiungere Bergamo costa un filtro — e i file grezzi
  nazionali sono già in `dati/raw/`, quindi nemmeno un download. Resta il
  **controllo naturale** per MET-9, che nel frattempo si è chiusa da sola sui
  soli dati bresciani (la stessa divisione a due scale diverse basta), e serve
  ora a un'altra domanda: la convergenza dei redditi è bresciana o è di tutti?

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
  l'ultimo anno di ogni serie. Fatta su popolazione
  (`analysis/variazione_popolazione.py`) e su addetti, unità locali e reddito
  (`analysis/velocita_di_cambio.py`).
- ✅ **Livelli contro variazioni** (`analysis/livelli_e_variazioni.py`). Ha
  prodotto il risultato metodologico della tornata: correlare la crescita con il
  livello **finale** è un artefatto, e sul reddito cambia il segno. È MET-12.
- ✅ **Tipologia di comuni** (`analysis/tipologia_comuni.py`): k-means++ con
  seme fisso, trenta righe, cinque gruppi. Stampa anche i comuni che **nessun
  gruppo descrive bene**, che è la parte onesta.
- ✅ **Autocorrelazione spaziale** (`analysis/autocorrelazione_spaziale.py`):
  contiguità per vertice condiviso dal GeoJSON (grado medio 5,37, nessun comune
  isolato), Moran con significatività per permutazione. Tutti gli indicatori
  provati sono spazialmente aggregati; il più aggregato di tutti è la
  specializzazione settoriale.
- ✅ **La decomposizione settoriale del capoluogo**
  (`analysis/decomposizione_capoluogo.py`): MET-9 è chiusa, la risposta è nella
  nota metodologica. Resta aperto solo il confronto con Bergamo.
- ✅ **Le due economie** (`analysis/due_economie.py`), che prima non era
  possibile: quote settoriali comune per comune.
- ✅ **Rottura Covid** (`analysis/rottura_covid.py`). Il risultato è doppio:
  sulle serie annuali **non si può testare** (due punti prima del 2020 non fanno
  una tendenza), e sulle mensili si può ma bisogna scegliere bene la base — con
  vent'anni di base il PM10 del 2020 sembra −26 %, con tre anni è −9 %, e la
  differenza è tutta tendenza di lungo periodo scambiata per pandemia.
- ✅ **Decomposizione della popolazione**
  (`analysis/decomposizione_popolazione.py`). Le tavole del bilancio demografico
  c'erano, ma su un host a cui nessuno aveva pensato: `demo.istat.it`, tavola
  D7B, un CSV zippato per anno con dentro tutti i comuni italiani — niente SDMX,
  niente chiavi posizionali, mezzo minuto per sei anni. La scomposizione
  **chiude allo zero** perché la «popolazione censita» di quella tavola è la
  stessa del censimento permanente, e ha prodotto MET-15. È anche il caso più
  netto della lezione di §9: la fonte non mancava, mancava l'idea di cercarla
  fuori da `esploradati`.
- ✅ **Il confronto fra province** (`analysis/confronto_province.py`), che è
  andato oltre Bergamo: gli stessi indicatori su tutte e 107 le province, perché
  i file grezzi nazionali erano già su disco e il costo era il tempo di
  rileggerli. Ha corretto la frase più ripetuta del progetto (MET-14) e
  rafforzato MET-9. ✅ Esteso ai **redditi** con `convergenza_confronto.py`: la
  convergenza regge identica a Bergamo (−0,48 contro −0,45), quindi è solida e
  non è bresciana. ✅ Esteso alla **popolazione** con
  `decomposizione_popolazione.py`, e per lo stesso motivo — il file della fonte
  è nazionale, le 107 province costano zero download in più: Brescia è la 6ª
  provincia italiana per crescita, contro una mediana di −19,7 abitanti ogni
  mille. ✅ Esteso al **turismo** con `confronto_turismo.py`, ed era l'unico dei
  quattro a costare un download: la fonte comunale è regionale, quindi ne è
  servita una seconda (ISTAT `122_54_DF_DCSC_TUR_7`, tutte e 107 le province dal
  2008). Ne è uscito il risultato meno atteso del progetto — la provincia è la
  **decima d'Italia per presenze** e la sesta per quota di clienti stranieri —
  e due regole, MET-17 e MET-18. **Il confronto esterno adesso copre tutti e
  quattro gli assi economici**; resta fuori il solo ambiente, dove l'unità
  osservata è il sensore e non il comune.

### 5.3 La convenzione di `analysis/`

Uno script per analisi in [`analysis/`](analysis/README.md), `--save` che
scrive CSV in `analysis/output/` (ignorata da git: si rigenera), e come sole
dipendenze la **libreria standard** — niente pandas, niente scipy, niente
sklearn. Dalla tornata di agosto 2026 c'è anche `analysis/_tabelle.py`, che
**non è un'analisi**: è la lettura delle tabelle e la statistica di base che
gli script hanno in comune, più il posto dove stanno scritte una volta sola le
decisioni che altrimenti si prendono in modo diverso in due script diversi
(MET-13). `verifica_cifre.py` non lo usa, ed è deliberato. Le tabelle sono piccole e k-means e le correlazioni si reimplementano
in poche righe; in cambio il progetto resta installabile ovunque, come la
pipeline.

Gli script leggono **solo** da `dati/processed/`: nessuno tocca la rete. La
regola di confine con la pipeline: **se il risultato serve al sito è pipeline,
se serve a capire è analisi.**

---

## 6. Come si costruisce il sito statico

Questa è la parte che si perderebbe. Il progetto Donostia pubblica **due cose
diverse** sullo stesso sito, ed è una separazione che vale la pena copiare.

> **✅ Il primo dei due artefatti esiste** (agosto 2026), in
> [`sito/`](sito/README.md): documento narrativo con otto storie, più
> `metodologia.html` e `dati.html`. Mezzo mega, autocontenuto, mappe e grafici
> in SVG disegnati a mano. Si costruisce con `python sito/costruisci.py`.
>
> Quello che segue resta la specifica — è ancora la descrizione fedele di com'è
> fatto — con l'aggiunta di **una regola scoperta costruendolo**: nessuna cifra
> del racconto è scritta a mano. Nel testo ci sono segnaposto `{{c:nome}}` che
> il costruttore calcola dalle tabelle, e un segnaposto senza valore fa
> **fallire** la costruzione invece di pubblicare una frase con un buco. È la
> regola «ogni numero ha uno script dietro» applicata in avanti, al prodotto,
> invece che a posteriori sui documenti.
>
> ✅ **Anche il secondo artefatto esiste** (settembre 2026), e non è quello
> che questa sezione descriveva: è `esplora.html`, una quarta pagina dello
> stesso sito, non un'app React sotto `/app/`. Il §6.1 (b) qui sotto è stato
> riscritto e dice perché.

### 6.1 I due artefatti

**(a) Il documento narrativo** — un **unico file HTML autocontenuto**, senza
dipendenze a runtime, che è la homepage del sito.

- I dati sono **incorporati** in una sola riga `<script>window.DATI = {…}`.
  Nessuna `fetch()`: il file si apre anche da disco, si manda per email, si
  archivia. Nel progetto Donostia pesava 846 KB con sette storie dentro.
- I grafici sono **SVG disegnati a mano in JavaScript**, senza librerie.
  Suona faticoso ed è invece il motivo per cui il file resta autocontenuto e
  non invecchia.
- La forma è **scrollytelling** dove serve: la mappa o il grafico restano fissi
  (`position: sticky`) mentre il testo scorre e li aggiorna. Tutti i controlli
  restano anche manipolabili a mano — chi vuole esplorare non è costretto a
  scorrere. Ce l'hanno **due storie su otto**, la prima e l'ottava, e il perché
  di quel due (più i tre vincoli che il prossimo deve rispettare) sta in
  [`sito/README.md`](sito/README.md) §Lo scrollytelling.
- Ogni metrica complessa ha un riquadro **«la metrica, in chiaro»** che la
  spiega in due frasi.
- Le pagine sorelle sono `metodologia.html` e `dati.html`, con la stessa
  struttura.

**(b) Il pannello interattivo** — ✅ fatto, ed è `sito/modelli/esplora.html`.

**La specifica diceva un'app React + Vite sotto `/app/`, e non è stata
seguita.** Vale la pena scrivere perché, perché il ragionamento si ripeterà.

Questa sezione era stata copiata dal progetto precedente, dove il pannello era
un'app servita a parte con `react`, `maplibre-gl`, `recharts`, `d3-scale` e
`vite`. Fra quella copia e oggi però il documento narrativo è stato scritto, e
scrivendolo è nato `grafici.js`: mille e cento righe che contengono già la
coropletica dei 205 comuni, le rotture per quantile e quelle simmetriche, la
legenda, il tratteggio del «nessun dato», la tabella-specchio e la riga di
provenienza. Le cinque dipendenze servivano a ottenere cose che il progetto
aveva già scritto a mano, e in cambio avrebbero portato una catena di
costruzione Node dentro una CI che oggi è **solo Python** (§7).

Quello che mancava davvero erano due menù e il ritratto del comune:
centosessanta righe di JavaScript in fondo al modello. La regola «nessuna
dipendenza a runtime» non era una regola del racconto: era una regola del
progetto, e vale anche per lo strumento.

Cosa fa la pagina:

- **tutti e diciannove gli indicatori** del registro, raggruppati per tema, e
  non i quindici che le otto storie citano. La lista non è scritta nel modello:
  `metriche_esplora()` legge `metrics.json` e prende quelli `live`, così un
  indicatore nuovo compare da solo. È la §6.2 presa sul serio;
- **l'anno**, per gli indicatori che ne hanno più di uno, fino ai ventidue
  semestri annualizzati delle quotazioni OMI;
- **il ritratto del comune**: i diciannove indicatori insieme per un comune
  solo, con la posizione fra i comuni che quel dato ce l'hanno — e il
  denominatore cambia da riga a riga, perché cambia la copertura;
- il comune si sceglie dall'elenco **o cliccandolo sulla mappa**;
- **ogni scelta sta nell'indirizzo**: `#prezzo_case/2012/017068`. La pagina lo
  scrive e lo rilegge, anche quando cambia sotto una finestra già aperta;
- **«↓ CSV di questa mappa»**, costruito nel browser dai dati già incorporati:
  è la §6.4 senza dover generare un file per indicatore per anno.

Le due cose della vecchia specifica che sono rimaste, perché erano scelte e non
dipendenze: **nessun tile esterno** (qui non c'è nemmeno una mappa a
piastrelle: si disegna il GeoJSON e basta) e **una tabella-specchio accanto a
ogni mappa**, navigabile da tastiera. Una coropletica da sola è inaccessibile.

> **Se il tempo è poco, il documento narrativo viene prima** — nel progetto
> precedente ha avuto molto più valore del pannello (§9). È rimasto vero: il
> racconto è costato settimane, questa pagina un pomeriggio, e il motivo per
> cui è costata un pomeriggio è che il racconto era già stato scritto.

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

> ✅ **Deciso, e non qui**: le scale sono quelle di `donostia-dataviz`, insieme a
> tutto il resto della lingua grafica. I due progetti sono una collana e devono
> sembrarlo; il dettaglio di cosa è stato ripreso e cosa no sta in
> [`sito/README.md`](sito/README.md).

Le classi sono per **quantile** sulle grandezze — con 205 comuni e un capoluogo
fuori scala, le classi a intervallo uguale ne metterebbero quasi duecento nella
prima — e **simmetriche attorno allo zero** sulle variazioni, centrate però sul
95º percentile dei valori assoluti e non sul massimo: con il massimo, un solo
comune fuori scala schiaccia tutti gli altri in due classi pallide.

- **Sequenziale** (la rampa calda dell'originale, chiaro → scuro) per i valori assoluti.
- **Divergente** (freddo = giù, caldo = su, neutro nel mezzo) centrata
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

> **✅ Il workflow è scritto** (`.github/workflows/deploy-pages.yml`), insieme a
> uno di verifica che a ogni push fa girare i test, il ricalcolo delle cifre
> citate e tutti gli script di analisi. Nessuno dei due tocca la rete: c'è
> `build --offline`, che rilegge le tabelle versionate invece di interrogare
> ISTAT, perché la pubblicazione non deve poter fallire per un host che quel
> giorno non risponde.
>
> **Costruire non è pubblicare**, e i due verbi stanno in due job separati.
> `costruisci` parte a ogni push su `main`: dati, test, ricalcolo delle cifre,
> sito, e l'artefatto scaricabile dalla pagina dell'esecuzione — così il sito si
> rilegge mentre l'analisi va avanti, senza che esista un indirizzo pubblico.
> `pubblica` **non parte da nessun evento automatico**: ci si arriva solo da
> *Actions → «Pubblica il sito» → Run workflow*, scrivendo `pubblica` nella
> casella di conferma.
>
> Non c'è nessuna variabile da impostare prima e nessuno stato da ricordarsi di
> richiudere dopo: la decisione si prende nel momento in cui si pubblica e vale
> per quella esecuzione sola. ⏳ **Era una variabile di repository `PUBBLICA`**,
> che una volta aperta faceva pubblicare ogni push; è stata sostituita ad agosto
> 2026 perché il progetto voleva l'opposto — nessuna pubblicazione finché
> l'analisi non è finita.
>
> ✅ **Il clic su Pages è stato fatto** (4 settembre 2026): *Source =
> «GitHub Actions»*. Fino a quel momento Pages era attivo ma con *Deploy from a
> branch*, e con quella impostazione GitHub ignorava il workflow passando il
> repository per Jekyll: l'indirizzo pubblico
> (<https://stefanomasneri.com/brescia-dataviz/>, dove reindirizza
> `stocastico.github.io/brescia-dataviz` perché il dominio personalizzato è
> impostato sul sito utente) serviva il **README** invece del racconto. Adesso
> `deploy-pages` ha dove pubblicare, e l'unica cosa che manca al sito online è
> la decisione di pubblicarlo.

Un solo workflow, `.github/workflows/deploy-pages.yml`. Struttura del sito
**pubblicata oggi**. Non c'è nessun `app/` e non ci sarà: il pannello
interattivo è una pagina di questo stesso sito (§6.1), quindi il workflow non
ha avuto bisogno di cambiare per accoglierlo.

```
/index.html           il documento narrativo
/esplora.html         i diciannove indicatori, a scelta di chi legge
/metodologia.html     le regole del progetto
/dati.html            fonti, vigenza, avvertenze, licenza
/dati/processed/*.csv le tabelle scaricabili
```

I passaggi, nell'ordine — **solo Python, nessun passo Node**: il sito non ha
build step, i grafici sono SVG scritti a mano e `costruisci.py` incorpora tutto
in tre file:

1. `actions/checkout` con `fetch-depth: 0` (serve la storia per datare i dati) e
   `actions/setup-python` su 3.12;
2. `pip install -e ./pipeline`, poi `build --offline web`: i JSON del sito
   escono dalle tabelle versionate, senza interrogare le fonti;
3. i controlli, che sono la parte che vale: i test del contratto e il ricalcolo
   di **ogni cifra citata**. Se una diverge, non si pubblica;
4. `costruisci.py --uscita _site`, con la data presa dal commit;
5. il controllo che nessun segnaposto sia sopravvissuto, poi
   `upload-pages-artifact`. **Qui finisce il job che gira sempre.**
6. Il job `pubblica`, dietro
   `if: github.event_name == 'workflow_dispatch' && inputs.conferma == 'pubblica'`:
   `configure-pages` con `enablement: true` e `deploy-pages`. È l'unico posto
   che tocca le impostazioni di Pages, e da un push non è raggiungibile.

Dettagli che costano tempo se non li sai:

- **Il cancello è l'evento, non una variabile.** Nessun push, nessuno
  `schedule` aggiunto un domani e nessun `repository_dispatch` può soddisfare
  quella condizione. È una proprietà che vale la pena non perdere per sbaglio,
  quindi ha un test: `pipeline/tests/test_workflow_deploy.py` legge il workflow
  e fallisce se il job `pubblica` smette di essere ristretto al lancio manuale.
  Se un giorno vorrai il deploy automatico, la modifica è una riga e quel test
  ti dirà che l'hai fatta — che è il suo mestiere.
- **La conferma è scritta, non un clic.** Un input obbligatorio in cui digitare
  `pubblica`: «Run workflow» da solo costruisce e basta. Serviva perché il
  bottone è a un clic di distanza da chiunque abbia accesso in scrittura.
- **Se vuoi anche un'approvazione umana** sopra a tutto questo, l'ambiente
  `github-pages` accetta dei «required reviewers»: *Settings → Environments →
  github-pages*. Le due cose convivono.
- **Un push non può annullare una pubblicazione a metà.** I due generi di
  esecuzione stanno in gruppi di concorrenza diversi
  (`pages-${{ github.event_name }}`): due build si annullano a vicenda senza
  danno, un deploy interrotto lascerebbe il sito monco.
- **Le versioni delle action** sono allineate a `donostia-dataviz`, che il
  deploy ce l'ha funzionante: checkout v7, setup-python v7, configure-pages v6,
  upload-pages-artifact v5, deploy-pages v5. Restare indietro di un major è il
  modo tipico di ritrovarsi con l'avviso «Node 20 actions are deprecated» nei
  log: non viene dal workflow — che di Node non ne usa — ma dal runtime con cui
  girano le action stesse.
- ✅ **Una volta sola, e la poteva fare solo lui**: *Settings → Pages → Source =
  «GitHub Actions»*, fatto il 4 settembre 2026. Resta scritto qui perché è il
  genere di impostazione che si perde in una migrazione di repository: il primo
  deploy fallisce se non è così, e non basta che Pages sia «attivo» — con la
  sorgente su un ramo, `deploy-pages` non ha dove pubblicare. `configure-pages`
  con `enablement: true` accende Pages quando è spento, ma non cambia la
  sorgente di un Pages già acceso.
- Il dominio personalizzato **non va toccato qui**: `stefanomasneri.com` è
  impostato sul sito utente (`stocastico.github.io`), e i siti di progetto lo
  ereditano via redirect. Nessun file `CNAME` da mettere nell'artefatto.
- Permessi richiesti: `contents: read`, `pages: write`, `id-token: write`.
- `concurrency: { group: pages, cancel-in-progress: true }` evita che due
  deploy si accavallino.
- **Le date si stampano in fase di deploy**, non a mano. La data del sito viene
  dal commit; quella dei dati **non** dal manifest, come si era previsto qui —
  una data scritta in un file versionato cambia a ogni esecuzione e sporca il
  diff senza che sia cambiato un numero — ma dall'**ultimo commit che ha toccato
  `dati/processed/`**, che è anche più vero. Senza questo meccanismo le date
  invecchiano in silenzio e il sito mente.
- Il workflow **controlla che nessun segnaposto sia sopravvissuto** alla
  sostituzione: meglio un deploy fallito di una pagina con un buco.
- Il deploy era **manuale** e ora è automatico su `main`, ma la prudenza che lo
  teneva manuale non è stata buttata: si è spostata nel cancello. Costruire a
  ogni push serve — se una cifra smette di tornare lo sai subito — e pubblicare
  è un'altra decisione.

---

## 8. I due documenti da scrivere alla fine — ✅ scritti

~~Non ora: **quando i dati saranno completi, le visualizzazioni costruite e le
storie scelte.**~~ **È stato adesso** (settembre 2026): i dati ci sono, le otto
storie sono scritte, e i due documenti sono passati a **versione 1.0**. Le
bozze sono state riscritte, non ampliate, e le condizioni che questa sezione
poneva sono state verificate una per una prima di toccarle.

Cosa è cambiato, in due righe. `METODOLOGIA.md` ha chiuso il buco che
dichiarava da sempre — le regole su **come si scelgono e si raccontano le
storie**, MET-22…MET-26 — ricavandole dal conteggio di cosa le otto storie
avevano fatto davvero, e non da un principio scelto prima. `WORKING-PAPER.md`
ha il titolo che gli mancava perché ha la tesi: **«Il numero giusto, la frase
falsa»**, dieci episodi in cui un dato corretto stava per produrre
un'affermazione falsa, in quattro famiglie.

⏳ **E poi sono diventati undici e ventisette** (settembre 2026, versioni 1.1).
L'undicesimo episodio non viene dall'analisi ma dal **prodotto**: costruendo la
pagina che esplora si è visto che `dati.html` annunciava diciannove indicatori
e ne elencava quindici, presi da due sorgenti diverse. Ne è uscita **MET-27**.
La riga sopra resta com'era scritta, per MET-25.

Il testo che segue è quello originale, con il ragionamento su **perché** questi
due documenti andavano scritti alla fine. Resta perché la previsione si è
avverata, e sapere che si è avverata vale quanto il risultato: entrambe le
famiglie di regole nate in questa passata — MET-23 e le altre quattro — non
sarebbero esistite scrivendole prima.

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
| ✅ ~~Mettere la sorgente di Pages su «GitHub Actions»~~ (§7) | fatta | il 4 settembre 2026: il deploy ha dove pubblicare |
| 🙋 Pubblicare: *Run workflow → conferma = `pubblica`* (§7) | **1 min** | mandare il sito online, quando l'analisi sarà finita |
| 🙋 Rileggere i testi del sito | **1 h** | è il tuo nome sopra |
| 🤖 Scarico delle migrazioni (§2.1) | **venti minuti**, non una notte | l'unico dataset previsto che manchi. ✅ Il riscarico in italiano delle tre tavole censuarie (§2.4) è **fatto** |
| ✅ ~~Decomposizione della popolazione~~ | fatta | ed è diventata MET-15: la prima storia adesso risponde alla domanda che dichiarava di non poter rispondere |
| ✅ ~~Una storia su aria e clima (asse 4)~~ | fatta | `analysis/aria_e_clima.py` e la sesta storia del sito. Ne è uscita anche MET-16, e la pioggia è entrata nel racconto **proprio perché** non dà segnale |
| ✅ ~~Estendere il confronto fra province al **turismo**~~ | fatta | `analysis/confronto_turismo.py` e la §7.8 del working paper. Ne sono uscite MET-17 e MET-18, e la scoperta che la provincia è la decima d'Italia per presenze |
| ✅ ~~Riscrivere la §7 del working paper con le storie~~ | fatta | nove risultati, ciascuno con i suoi controlli |
| ✅ ~~Portare il turismo nel sito come **settima storia**~~ | fatta | «La decima provincia turistica d'Italia», con lo sciame delle 107 province, i diciassette anni di presenze divise fra clienti italiani e stranieri, e lo scarto fra le due fonti disegnato invece che raccontato. Il settimo colore è `--prugna`, scelto con la regola ora scritta in `sito/README.md` |
| 🤖 Analisi e storia sulla casa (§4) | **mezza giornata** per la prima analisi, un giorno per l'ottava storia | l'unico tema che ha i dati e non ha ancora niente: prezzi fermi contro volumi raddoppiati |
| ✅ ~~Pannello interattivo~~ | fatto, e in un pomeriggio invece dei 2–3 giorni stimati | `esplora.html`: non l'app React della stima, ma una pagina che riusa `grafici.js`. La stima era giusta per l'app e sbagliata per il problema (§6.1) |
| 🙋 Quel che resta dei download manuali: l'export Coeweb (§2.2, [istruzioni](dati/SCARICHI-MANUALI.md) §3) | **1 h**, ed erano 2–4 prima che tre voci uscissero dall'elenco e l'OMI arrivasse | estensioni, nessun asse portante |

### Se hai venti minuti

Sono i venti minuti che valgono di più di tutto il resto di questa tabella:
lancia il workflow a mano — lasciando la conferma su `no`, così costruisce e
basta — scarica l'artefatto e rileggi la prima storia. La sorgente di Pages è
già a posto, quindi il sito è pronto ad andare online: lo pubblichi quando lo
sei anche tu.

### Se hai due ore

Rileggi i testi del sito con il tuo occhio — è il tuo nome sopra, e nessuno
script controlla se una frase dice più di quanto il dato sostenga. Sono sette
storie adesso, e le ultime due non le hai mai lette.

### Se hai mezza giornata

**Guarda la tavolozza, e decidi se riallinearla con l'altro progetto.** Le storie sono
sette e i colori presi da `donostia-dataviz` sono cinque, quindi ne sono stati
aggiunti due (`--oliva` e `--prugna` in `stile.css`), con accanto la regola che
li sceglie — il buco di tinta più largo che resta. È l'unica cosa decisa qui che
tocca la lingua grafica condivisa fra i due progetti, ed è quindi l'unica che
vale la pena riesaminare: `sito/README.md` §Lo stile dice cosa comporterebbe
riallineare i due, e sono due righe più un commento.

### Se hai un weekend

**Il pannello era il lavoro da weekend, ed è fatto** (§6.1). Quello che resta
in quella misura è l'analisi: una nona storia dalle candidate di `BRIEF.md`,
oppure portare l'asse 2 fino in fondo scaricando `migrazioni_comuni.csv`.

Il confronto fra province è servito più di qualunque altra analisi — ha smontato
una frase che il progetto ripeteva dal primo giorno (MET-14), ha ribaltato la
parola su cui poggiava la prima storia (MET-15) e sul turismo ha trovato un
risultato che nessuno stava cercando — e adesso copre tutti e quattro gli assi
economici. Lo schema di come si fa sta in `datasets/province.py` (filtro locale
su file nazionale), in `datasets/bilancio.py` (stesso, su un host diverso), in
`datasets/redditi_confronto.py` (quando la fonte non si può filtrare e ogni
provincia costa i suoi download) e ora in `datasets/turismo_confronto.py`
(quando la fonte comunale non copre l'Italia e ne serve **una seconda**, con le
conseguenze scritte in MET-17).

**Da dove ripartire in ogni caso**: `python analysis/verifica_cifre.py`. Se le
verifiche passano, le tabelle sono a posto e i documenti dicono il
vero; se una diverge, quello è il primo problema da guardare — ed è già successo
due volte che ne trovasse una. Quante siano sta scritto in un posto solo,
`analysis/README.md`, e non qui: una cifra ripetuta in quattro documenti è una
cifra che fra sei mesi ne dice quattro diverse — ed era già ripetuta in quattro.
Diciotto vengono dalla scomposizione demografica, tredici dall'aria e dal clima.

---

*Documento nato ad agosto 2026 come consegna per la separazione del
repository, riscritto quando la separazione era avvenuta e la pipeline
funzionava, e aggiornato di nuovo quando le analisi erano fatte e il sito
esisteva. Lo stato delle fonti è in [`FONTI.md`](FONTI.md), quello dei dati
in [`dati/README.md`](dati/README.md), quello della pipeline in
[`pipeline/README.md`](pipeline/README.md), quello del sito in
[`sito/README.md`](sito/README.md).*
