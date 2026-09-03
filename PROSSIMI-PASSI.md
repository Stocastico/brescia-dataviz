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

La licenza è scelta (§3.3), quindi per pubblicare restano **due clic**, e
nessuno dei due è tecnico: la sorgente di Pages, e il cancello che decide quando
il sito diventa visibile. Il resto si costruisce da solo a ogni push su `main`.
Sopra ai due clic c'è una **decisione di disegno** aperta da settembre 2026, che
non blocca niente ma è l'unica cosa in questo elenco che nessuno può prendere al
posto tuo perché riguarda due repository insieme.

| | Cosa | Perché tocca a te | Tempo | Blocca |
|---|---|---|---|---|
| 🙋 2 | **Correggere la sorgente di GitHub Pages** (§7): *Settings → Pages → Source* è su «Deploy from a branch», va messo su **«GitHub Actions»** | serve il tuo accesso da proprietario del repo | 2 min | il primo deploy: finché resta com'è, l'indirizzo pubblico serve il README passato per Jekyll, non il racconto |
| 🙋 9 | **Pubblicare**, quando l'analisi sarà finita (§7): *Actions → «Pubblica il sito» → Run workflow → conferma = `pubblica`* | è la decisione di pubblicare, e non la prende un workflow | 1 min | che il sito diventi visibile. Prima di allora si costruisce a ogni push e resta un artefatto da scaricare |
| 🙋 3 | **Scaricare le quotazioni OMI** e i perimetri delle zone (§2.2) | area riservata Agenzia delle Entrate, SPID/CIE | 1–2 h la prima volta | solo l'asse «casa e prezzi», che è di contorno |
| 🙋 4 | **Scaricare gli open data del Comune di Brescia** (§2.2) | `dati.comune.brescia.it` non risponde dagli ambienti remoti, da una macchina italiana sì | 30 min | estende indietro il turismo cittadino (2005–2013) |
| 🙋 5 | **Scaricare i dati MUR sui due atenei** (§2.2) | `dati-ustat.mur.gov.it` idem | 30 min | l'asse istruzione, che è di contorno |
| 🙋 6 | **Esportare a mano il commercio estero provinciale** (§2.2) | il databrowser ISTAT è una SPA senza API | 1 h | niente: la serie regionale è già scaricata come ripiego dichiarato |
| 🙋 7 | **Rileggere i testi prima di pubblicare** (§8) | è il tuo nome sopra | — | la pubblicazione |
| 🙋 8 | **Scaricare in locale `migrazioni_comuni.csv`** ([istruzioni](dati/SCARICHI-LOCALI.md)) | 422 MB: sta fuori da git, e serve solo quando l'asse 2 diventerà una storia | 20 min di attesa | niente di quello che è pubblicato |
| 🙋 10 | **Decidere sul sesto colore di storia** ([`sito/README.md`](sito/README.md) §Lo stile) | le storie sono sei e i colori ereditati da `donostia-dataviz` sono cinque, quindi ne è stato aggiunto uno (`--oliva` in `stile.css`). Riguarda la lingua grafica **condivisa fra i due progetti**, e tenerli una collana o lasciarli divergere è una scelta tua | 10 min, o mezz'ora se lo porti anche nell'altro repository | niente. Il sito è coerente così com'è; la domanda è se lo sono i due progetti insieme |

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
| Pipeline | ✅ funzionante, `requests` + libreria standard, 209 test verdi |
| Base geografica | ✅ i confini dei 205 comuni in GeoJSON, verificati contro l'area nota della provincia |
| Tabelle tidy | ✅ 27 CSV in [`dati/processed/`](dati/README.md), versionati; manca solo `migrazioni_comuni.csv` |
| Analisi | ✅ tredici script in [`analysis/`](analysis/README.md): velocità di cambio, quadranti, autocorrelazione, tipologia, le due economie, la scomposizione del capoluogo, la rottura del 2020, il confronto fra le 107 province, la scomposizione demografica, l'aria e il clima |
| Storie scelte | ✅ **sei**, scritte e pubblicate nel documento narrativo — la quinta corregge quelle che la precedono, la sesta è l'unica che dura vent'anni. Le candidate rimaste stanno in `BRIEF.md` |
| Contratto dati per il sito | ✅ `metric_*.json` + registro, con i cinque invarianti come test |
| Documento narrativo | ✅ [`sito/`](sito/README.md), un file HTML autocontenuto da mezzo mega |
| Pannello interattivo | 🤖 no, e viene dopo (§6.1) |
| Deploy | 🤖 la **costruzione** è automatica su `main` (test, cifre, sito, artefatto); la **pubblicazione** no: parte solo a mano, con una conferma scritta (§7). 🙋 serve il tuo passaggio su Pages |
| Licenza | ✅ MIT per il codice (`LICENSE`), CC BY 4.0 per testi e dati (`LICENSE-DATI`) (§3.3) |
| `METODOLOGIA.md` | ⚠️ bozza avanzata: **sedici** regole, MET-9 chiusa, MET-15 dalla scomposizione demografica, MET-16 dal panel bilanciato delle centraline |
| `WORKING-PAPER.md` | ⚠️ bozza, la sezione dei risultati va riscritta con le sei storie (§8) |

**Dove sta il progetto, in una frase.** I dati ci sono, le analisi sono state
fatte e sei storie sono scritte in un sito che si costruisce da solo: **manca
la tua rilettura e un clic nelle impostazioni**. Il lavoro tecnico
che resta è tutto facoltativo — il pannello interattivo, i download manuali, i
confronti con altre province.

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
> rigenera in venti minuti. Nessuna delle sei storie pubblicate la usa, quindi
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
  mille. ⏳ Resta fuori il **turismo**.

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
> [`sito/`](sito/README.md): documento narrativo con sei storie, più
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
> Il pannello React (b) resta da fare, e resta il secondo in ordine di
> importanza.

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
> Resta il tuo clic su Pages, e ad agosto 2026 **non è ancora quello giusto**: Pages è attivo, ma con
> *Source = «Deploy from a branch»*. Con quella impostazione GitHub ignora il
> workflow e passa il repository per Jekyll, così l'indirizzo pubblico
> (<https://stefanomasneri.com/brescia-dataviz/>, dove reindirizza
> `stocastico.github.io/brescia-dataviz` perché il dominio personalizzato è
> impostato sul sito utente) serve il **README** invece del racconto. Va messo
> su **«GitHub Actions»**: *Settings → Pages → Source*.

Un solo workflow, `.github/workflows/deploy-pages.yml`. Struttura del sito
**pubblicata oggi** — niente `app/`: il pannello interattivo non esiste ancora
(§6.1), e quando esisterà questa sezione va riscritta insieme al workflow.

```
/index.html           il documento narrativo
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
- 🙋 **Una volta sola, e la puoi fare solo tu**: *Settings → Pages → Source =
  «GitHub Actions»*. Il primo deploy fallisce se non è impostato — e non basta
  che Pages sia «attivo»: con la sorgente su un ramo, `deploy-pages` non ha
  dove pubblicare. `configure-pages` con `enablement: true` accende Pages
  quando è spento, ma non cambia la sorgente di un Pages già acceso.
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
| 🙋 Mettere la sorgente di Pages su «GitHub Actions» (§7) | **2 min** | poter pubblicare |
| 🙋 Pubblicare: *Run workflow → conferma = `pubblica`* (§7) | **1 min** | mandare il sito online, quando l'analisi sarà finita |
| 🙋 Rileggere i testi del sito | **1 h** | è il tuo nome sopra |
| 🤖 Scarico delle migrazioni (§2.1) | **venti minuti**, non una notte | l'unico dataset previsto che manchi. ✅ Il riscarico in italiano delle tre tavole censuarie (§2.4) è **fatto** |
| ✅ ~~Decomposizione della popolazione~~ | fatta | ed è diventata MET-15: la prima storia adesso risponde alla domanda che dichiarava di non poter rispondere |
| ✅ ~~Una storia su aria e clima (asse 4)~~ | fatta | `analysis/aria_e_clima.py` e la sesta storia del sito. Ne è uscita anche MET-16, e la pioggia è entrata nel racconto **proprio perché** non dà segnale |
| 🤖 Estendere il confronto fra province al **turismo** | **mezza giornata** | imprese, redditi e popolazione il termine di paragone ce l'hanno; il turismo no. Ed è il caso più difficile dei quattro: la fonte è regionale, quindi un confronto nazionale va costruito da un'altra fonte |
| 🤖 Riscrivere la §7 del working paper con le sei storie | **mezza giornata** | il documento per un lettore esterno |
| 🤖 Pannello React | **2–3 giorni** | l'esplorazione; il contratto dati che gli serve è già scritto e testato |
| 🙋 I download manuali (§2.2) | **2–4 h in tutto** | estensioni, nessun asse portante |

### Se hai venti minuti

Sono i venti minuti che valgono di più di tutto il resto di questa tabella:
metti la sorgente di Pages su «GitHub Actions», lancia il workflow a mano —
lasciando la conferma su `no`, così costruisce e basta — scarica l'artefatto e
rileggi la prima storia. Il sito è pronto; lo pubblichi quando lo sei anche tu.

### Se hai due ore

Rileggi i testi del sito con il tuo occhio — è il tuo nome sopra, e nessuno
script controlla se una frase dice più di quanto il dato sostenga. Sono sei
storie adesso, e la sesta non l'hai mai letta.

### Se hai mezza giornata

Il **turismo confrontato con il resto d'Italia** (§5.2), che è l'ultimo asse
senza termine di paragone e l'unico caso in cui il confronto non è gratis: le
altre tre volte la fonte era nazionale e bastava non filtrarla.

⚠️ Oppure, e viene prima: **guarda il sesto colore di storia**. Le storie sono
sei e i colori presi da `donostia-dataviz` sono cinque, quindi ne è stato
aggiunto uno (`--oliva` in `stile.css`). È l'unica decisione presa in questa
tornata che tocca la lingua grafica condivisa fra i due progetti, ed è quindi
l'unica che vale la pena riesaminare: `sito/README.md` §Lo stile dice cosa
comporterebbe riallineare i due.

### Se hai un weekend

**Il pannello React** (§6.1), o il **turismo confrontato con il resto d'Italia**.

Il confronto fra province è servito più di qualunque altra analisi — ha smontato
una frase che il progetto ripeteva dal primo giorno (MET-14) e ha ribaltato la
parola su cui poggiava la prima storia (MET-15) — e adesso copre imprese, redditi
e popolazione. Sul turismo no, ed è il caso più difficile: le altre tre volte la
fonte era nazionale e bastava non filtrarla, mentre i flussi turistici arrivano
da `dati.lombardia.it` e coprono la Lombardia. Servirebbe la tavola ISTAT sulla
capacità e sul movimento degli esercizi ricettivi, che è un'altra fonte con le
sue trappole. Lo schema di come si fa sta in `datasets/province.py` (filtro
locale su file nazionale), in `datasets/bilancio.py` (stesso, su un host
diverso) e in `datasets/redditi_confronto.py` (quando la fonte non si può
filtrare e ogni provincia costa i suoi download).

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
