# Working paper — Metodo per un ritratto riproducibile di un territorio industriale: Brescia, comune e provincia

> **Cos'è questo documento.** L'esposizione autocontenuta di **come** si
> costruisce il ritratto — fonti, disegno dei dati, decisioni metodologiche,
> strategia inferenziale e limiti — pensata perché un lettore esterno possa
> **replicare, criticare o riutilizzare** il metodo. Non sostituisce i
> documenti operativi ([`METODOLOGIA.md`](METODOLOGIA.md),
> [`FONTI.md`](FONTI.md), [`BRIEF.md`](BRIEF.md)): li sintetizza e li
> referenzia. Ogni numero citato è riproducibile da
> [`pipeline/`](pipeline/README.md).
>
> ## ⚠️ BOZZA — lavori in corso
>
> **Versione 0, agosto 2026, scritta in anticipo.** Il working paper vero si
> scrive **alla fine**, quando i dati saranno completi, le visualizzazioni
> costruite e le storie scelte: un paper metodologico che non può riportare
> risultati è mezzo paper.
>
> Cosa è già solido: il disegno dei dati (§3), le decisioni metodologiche (§4)
> e il caso documentato in §6.1, che è un errore reale corretto e regge da
> solo.
>
> Cosa è provvisorio: **la §7 (risultati)** contiene solo ciò che è emerso
> costruendo la pipeline, non un'analisi sistematica; **la §6.2** elenca
> controlli non ancora eseguiti; la §2 e la §5 andranno riscritte in base agli
> assi che verranno effettivamente scelti. Il titolo stesso del paper cambierà
> quando sarà chiaro qual è la tesi.

---

## Sintesi

Il progetto costruisce un ritratto quantitativo di Brescia — il comune, la
provincia e i suoi 205 comuni — a partire da fonti esclusivamente aperte:
ISTAT (censimento permanente, registro ASIA delle unità locali, criminalità,
forze di lavoro, commercio estero), MEF (dichiarazioni dei redditi per classi
di importo), ARPA Lombardia (qualità dell'aria dal 1992 e clima dal 1990),
Regione Lombardia (flussi turistici). Diciannove tabelle tidy, tutte
ricostruibili con `requests` e la libreria standard di Python, senza chiavi
API.

Il problema metodologico centrale **non** è l'N piccolo — 205 comuni sono
abbastanza — ma tre altre cose: la **eterogeneità delle grane** (alcuni assi si
fermano alla provincia, altri arrivano al comune, nessuno scende sotto), la
**disomogeneità delle finestre temporali** (da trentaquattro anni a tre), e
soprattutto la **fragilità semantica degli aggregati amministrativi**, che
cambiano per ragioni contabili senza che cambi nulla nel mondo.

Il risultato metodologico più utile finora è **un errore corretto**, ed è
documentato per esteso in §6.1: una variazione aggregata spettacolare — il
crollo dell'occupazione nelle grandi unità locali del capoluogo — si è
dissolta appena scomposta per settore, rivelandosi concentrata quasi
interamente nelle agenzie di somministrazione e nei servizi esternalizzati,
mentre la manifattura grande restava immobile. Da lì nasce la regola operativa
oggi più importante del progetto: *nessun titolo su una variazione aggregata
prima di averla scomposta*.

---

## 1. Motivazione e domanda

Il punto di partenza non è «un cruscotto con tutti i dati di Brescia», ma una
domanda: **come è cambiato questo territorio negli ultimi anni?**

La domanda è deliberatamente descrittiva. Il progetto gemello su Donostia
partiva da una domanda con un imputato già in scena — *il turismo sta facendo
salire i prezzi delle case?* — e ha impiegato mesi per dimostrare che con quei
dati non si poteva rispondere in modo causale. Qui la scelta è opposta:
nessuna tesi a monte, e gli indicatori non vengono costruiti per sostenere
un'ipotesi.

Resta però una domanda di fondo, quella che ha originato il progetto: **Brescia
è ancora il territorio della meccanica fatta di piccole aziende, o si è
concentrato?** È l'unica domanda che il disegno dei dati privilegia
esplicitamente, e la §7 mostra quanto sia più difficile di quel che sembra.

## 2. Perché Brescia

Tre caratteristiche la rendono un caso interessante e un buon banco di prova
per il metodo.

1. **È un territorio manifatturiero denso e frammentato**: 119.565 unità
   locali per 479.418 addetti in provincia, di cui il 92,7 % con meno di dieci
   addetti. La struttura dimensionale è il fenomeno da spiegare, non lo sfondo.
2. **È fortemente eterogenea al proprio interno**: il Garda turistico, la Val
   Trompia metalmeccanica, la Franciacorta vitivinicola, la Bassa agricola, la
   Valle Camonica montana. Un aggregato provinciale medio non descrive nessuno
   di questi luoghi, il che rende la grana comunale indispensabile invece che
   ornamentale.
3. **È in pianura padana**, quindi la qualità dell'aria è un asse con dati
   trentennali e significato immediato per chi ci vive — cosa che sulla costa
   basca non esisteva.

## 3. Disegno dei dati

### 3.1 Una sola chiave, nessuno slug inventato

Ogni fonte italiana usa il **codice ISTAT del comune a sei cifre** come chiave
naturale (`017029` = Brescia). Il progetto lo adotta senza traduzioni: niente
slug, niente tabelle di corrispondenza, niente join per nome — che è il modo
più affidabile di perdere righe in silenzio quando i nomi hanno apostrofi,
accenti o varianti («Toscolano-Maderno», «Puegnago del Garda»).

I 205 comuni della provincia si ricavano dall'elenco ufficiale ISTAT filtrando
sul codice provincia `017`. La geometria di riferimento sono i confini
comunali generalizzati ISTAT.

**Il soggetto è la provincia**, raccontata attraverso i suoi 205 comuni; il
capoluogo è un caso privilegiato con due approfondimenti dedicati. La scelta è
guidata dai dati: quasi tutte le fonti buone sono comunali e coprono l'Italia
intera, quindi filtrare sui 205 comuni costa una riga di codice e produce mappe
su un territorio molto più eterogeneo della città.

Sotto il comune esiste una grana più fine — le sezioni di censimento — che il
progetto ha verificato come accessibile ma **non usa**: i 33 quartieri del
capoluogo erano l'unità di analisi nella prima impostazione e sono stati
abbandonati con lo spostamento del soggetto.

### 3.2 Registro completo, finestra parziale o proxy

Ogni fonte viene classificata prima di essere usata:

| Tipo | Significato | Esempi |
|---|---|---|
| **Registro completo** | copre l'universo del fenomeno | ASIA (tutte le unità locali attive), popolazione residente, dichiarazioni dei redditi |
| **Finestra parziale** | copre una porzione, con criterio noto | flussi turistici (45 comuni su 178 hanno il dato soppresso); percezione di sicurezza (solo dal 2022) |
| **Proxy** | approssima ciò che vorremmo misurare | prezzi di offerta immobiliare al posto delle transazioni; commercio estero regionale al posto del provinciale |

La distinzione conta perché determina cosa si può dire: da un registro
completo si possono trarre totali, da una finestra parziale solo confronti
interni, da un proxy solo direzioni.

### 3.3 Provenienza e schede di confidenza

Ogni indicatore trascina la propria fonte fino all'interfaccia e porta un
livello di confidenza — `osservato`, `derivato`, `proxy` — con le assunzioni
esplicite. Un indicatore senza scheda non entra nel sito. Dettaglio in
[`METODOLOGIA.md`](METODOLOGIA.md) §MET-4.

### 3.4 Riproducibilità

La pipeline dipende da `requests` e dalla libreria standard: niente pandas,
niente passo di compilazione, nessuna chiave API. Le risposte grezze restano in
una cache su disco non versionata (quasi 1 GB), le tabelle pulite sono
versionate (8 MB). Un build completo da cache impiega venti secondi; da zero,
alcune decine di minuti, perché diverse serie ISTAT non si possono filtrare
lato server.

Tre trappole tecniche delle fonti sono gestite dalla pipeline e coperte da
test, perché **sbagliano in silenzio** — producono risultati plausibili invece
di fallire:

1. il formato SDMX va negoziato con l'header `Accept`: chiedendolo con
   `?format=` ISTAT restituisce l'intestazione e **zero righe**, e un dataset
   pieno sembra vuoto;
2. le chiavi SDMX sono posizionali e un punto di troppo restituisce zero righe
   senza errore: la pipeline legge le dimensioni dalla struttura del dataflow
   invece di contarle a mano;
3. i separatori numerici cambiano fonte per fonte — ISTAT scrive `100939.25`,
   Socrata scrive `1,406,590` — e una conversione ingenua legge `567,391` come
   567,391: sbagliato di mille volte, ma perfettamente credibile.

## 4. Le decisioni metodologiche

Undici regole, esposte per esteso in [`METODOLOGIA.md`](METODOLOGIA.md). In
sintesi:

| | Regola |
|---|---|
| MET-1 | **Unità locale non è impresa**: la classe dimensionale è dello stabilimento, non del gruppo; una riorganizzazione societaria muove i numeri senza che cambi nulla. |
| MET-2 | **Tre livelli territoriali, sempre dichiarati**; la coropletica solo per ciò che è misurato sui comuni. |
| MET-3 | **Un mancante non è uno zero** — inclusi gli zeri che la fonte stessa calcola su celle soppresse. |
| MET-4 | **Schede di confidenza** su ogni indicatore. |
| MET-5 | **Correlazioni robuste**: Pearson e Spearman insieme, leave-one-out su Brescia città e sui comuni gardesani. |
| MET-6 | **Fallacia ecologica**: le correlazioni sono fra comuni, mai fra persone. |
| MET-7 | **Stato, cambio e traiettoria** sono tre affermazioni diverse. |
| MET-8 | **Finestre temporali disomogenee**, mostrate per quello che sono. |
| MET-9 | **Decomporre prima di titolare** (§6.1). |
| MET-10 | **I ripieghi si dichiarano nel grafico**, non nelle note. |
| MET-11 | **L'origine non è un proxy** di reddito o di disagio. |

## 5. Indicatori derivati

Pochi, e tutti trasparenti. La lezione del progetto precedente è che gli indici
compositi comprano sintesi al prezzo dell'interpretabilità, e che un indice
costruito per sostenere una tesi finisce per confermarla.

- **Quote per classe dimensionale**: addetti in unità locali di ciascuna
  fascia sul totale. È l'indicatore centrale del progetto e non richiede
  assunzioni.
- **Addetti per 100 abitanti**: dove il lavoro si concentra rispetto a dove si
  abita. Mescola due annate (addetti 2023, popolazione 2024) e va dichiarato.
  I due estremi hanno cause opposte: Limone sul Garda 133,0 (alberghi), Odolo
  89,6 (acciaierie).
- **Rapporto di concentrazione del lavoro**: addetti nelle unità locali
  *situate* a Brescia (100.939) contro occupati *residenti* a Brescia (86.788)
  ≈ **1,16**. La città importa lavoratori. Anni e definizioni sono diversi:
  è un ordine di grandezza, non una misura.
- **Distribuzione del reddito**: le otto classi di importo MEF permettono di
  parlare di disuguaglianza invece che di livello medio. A Brescia città, nel
  2023, su 145.540 contribuenti, 31.327 dichiarano meno di 10.000 € e 3.213
  più di 120.000.

Nessun «indice di trasformazione» composito è previsto. Se arriverà, dovrà
avere definizione selezionabile e componenti a vista.

## 6. Strategia inferenziale

Con 205 unità spaziali il problema non è la potenza statistica ma la
**robustezza semantica**: cosa significa davvero il numero che si muove.

### 6.1 Il caso che ha definito il metodo: decomporre prima di titolare

È l'episodio più istruttivo del progetto finora, ed è un errore mio.

**L'osservazione.** Dai totali ASIA, nel comune di Brescia gli addetti in unità
locali con almeno 250 addetti crollano da **20.111 (2018) a 13.775 (2023)** —
dal 19,9 % al 13,6 % del totale — e le unità di quella classe passano da 35 a
28. In provincia, la stessa classe tiene (75 → 82 unità, addetti stabili
attorno a 33-34 mila). L'occupazione complessiva della città è ferma
(101.136 → 100.939), quella della provincia cresce di 29.421 addetti.

**Il titolo che ne era stato tratto**, e che è finito nei documenti di
progetto: *«l'assottigliamento del vertice è un fenomeno urbano, non
provinciale»*, con il sottinteso che la città stesse perdendo i suoi grandi
stabilimenti industriali.

**La decomposizione.** Incrociando la stessa classe dimensionale con la
divisione Ateco, la perdita risulta concentrata quasi per intero nella sezione
N — attività amministrative e di supporto:

| | 2018 | 2023 | Δ |
|---|---|---|---|
| 78 · somministrazione e ricerca di personale | 6.418 | 2.251 | **−4.167** |
| 81 · servizi per edifici e paesaggio | 3.123 | — | **−3.123** |
| 82 · supporto per le funzioni d'ufficio | 396 | 284 | −112 |
| 80 · vigilanza | — | 522 | +522 |
| **Sezione N** | **9.937** | **3.057** | **−6.880** |
| Manifattura (sezione C) | 4.448 | 4.397 | **−51** |
| Sanità e assistenza (Q) | 1.597 | 2.163 | +567 |
| Trasporti e magazzinaggio (H) | 1.640 | 2.438 | +798 |
| **Totale ≥250 addetti** | **20.111** | **13.775** | −6.336 |

**La manifattura grande in città non si è mossa.** Ciò che è sparito è
l'occupazione registrata delle grandi agenzie di somministrazione e delle
imprese di servizi esternalizzati — esattamente il tipo di unità che MET-1
avverte di non leggere alla lettera, perché i lavoratori somministrati sono
attribuiti all'unità locale dell'agenzia, non al luogo dove lavorano davvero.

**Cosa resta aperto**: se la divisione 81 sia davvero scesa a zero o sia stata
riclassificata; se il crollo della somministrazione sia un fenomeno reale del
mercato del lavoro o un artefatto di attribuzione; se lo stesso movimento si
osservi in province comparabili — Bergamo è il controllo naturale, e tutte le
fonti usate qui la coprono già.

**La regola che ne discende (MET-9).** *Nessun titolo su una variazione
aggregata prima di averla scomposta per settore e verificata contro almeno una
spiegazione amministrativa alternativa.* Un aggregato che si muove molto e
all'improvviso è, fino a prova contraria, un cambiamento di come si conta.

Il costo di questo controllo è stato una singola query. Il costo di non farlo
sarebbe stato pubblicare una tesi sulla deindustrializzazione del capoluogo
che i dati non sostengono.

### 6.2 Controlli previsti, non ancora eseguiti

- **Robustezza delle correlazioni**: Pearson più Spearman più leave-one-out su
  Brescia città e sui comuni gardesani (MET-5).
- **Autocorrelazione spaziale**: con 205 comuni contigui e una geometria vera,
  verificare se i valori si somigliano fra vicini — e in tal caso trattare i
  comuni come non indipendenti.
- **Rottura Covid**: testare esplicitamente la discontinuità 2020–2021 invece
  di attraversarla con una tendenza.
- **Confronto con Bergamo**: provincia gemella per storia industriale e
  dimensione, stessa Capitale della cultura 2023. Costa un filtro.
- **Decomposizione demografica**: quanta parte della variazione di popolazione
  viene da saldo naturale, migrazione interna, migrazione estera.

## 7. Risultati provvisori

⚠️ **Emersi durante la costruzione della pipeline, non da un'analisi
sistematica.** Vanno letti come indizi da verificare, non come conclusioni.

1. **La struttura dimensionale è stabile, non in movimento.** In provincia le
   unità locali sotto i dieci addetti restano il 92,7 % del totale (era 92,8 %
   nel 2018) e occupano il 42,9 % degli addetti (era 44,2 %). Cinque anni non
   hanno spostato la struttura: la risposta preliminare alla domanda
   originale è che sì, resta un territorio di microimprese.
2. **La crescita è nella fascia intermedia.** Gli addetti in unità da 10 a 249
   crescono di 23.840 in provincia — l'81 % dei 29.421 guadagnati in tutto —
   mentre le micro-unità ne aggiungono 6.842 e le grandi ne perdono 1.260. È lì
   che il territorio si muove, non agli estremi.
3. **Il capoluogo e il territorio divergono**, ma il perché non è quello che
   sembrava (§6.1). La divergenza dei totali è reale; la sua interpretazione
   industriale non regge.
4. **La provincia è turistica, il capoluogo no.** 12.246.854 presenze nel 2024,
   di cui il 68,8 % nei primi dieci comuni, otto dei quali sul Garda. Sirmione
   da sola (1.406.590) supera Brescia città (883.531, il 7,2 % del totale).
5. **L'aria è migliorata, e non abbastanza.** PM10 alla stazione di Brescia
   Broletto: media annua 45,5 µg/m³ nel 2001, 27,3 nel 2024. Un miglioramento
   reale di circa il 40 % che lascia comunque la città sopra la linea guida
   dell'Organizzazione mondiale della sanità.
6. **La città importa lavoro**: rapporto addetti localizzati su occupati
   residenti ≈ 1,16; 26.425 residenti escono ogni giorno dal comune, 23.699
   dei quali per lavoro (2019).

## 8. Limiti — cosa questo metodo non può affermare

- **Niente sotto il comune.** Nessun asse scende al quartiere. I dati
  esisterebbero per alcuni temi (sezioni di censimento) ma non per quelli
  centrali: lavoro, imprese, reddito e criminalità si fermano al comune o alla
  provincia. Una mappa dei quartieri di Brescia colorata per «sicurezza»
  sarebbe inventata.
- **Nessuna causalità.** Il disegno è descrittivo e trasversale. Non ci sono
  strumenti, non ci sono esperimenti naturali, e le serie sono troppo corte
  sugli assi economici per pretendere identificazione.
- **Nessuna lettura individuale.** Tutte le relazioni sono fra comuni (MET-6).
- **Il mercato immobiliare è coperto male.** Senza il passaggio all'OMI ci sono
  solo prezzi di offerta; nessuna copertura Inside Airbnb per Brescia; nessun
  censimento comunale degli alloggi turistici.
- **La percezione di sicurezza parte dal 2022**, quindi non esiste un «prima»
  con cui confrontarla.
- **Il commercio estero è regionale**, e la Lombardia non è Brescia.
- **Gli aggregati amministrativi sono fragili** (§6.1): il registro delle unità
  locali misura dove le cose sono *registrate*, che non sempre è dove
  accadono.

## 9. Regola di arresto

Il progetto precedente si è chiuso con una regola esplicita, ed è una buona
idea averla scritta prima di averne bisogno: **un dato nuovo entra solo se
prova, precisa o smentisce una domanda già posta** — non perché esiste, non
perché sarebbe interessante, non perché il portale lo pubblica.

Il rischio specifico qui è opposto a quello di Donostia: non l'ostinazione su
una tesi, ma la **dispersione**. La ricognizione aveva individuato tredici assi
possibili; ne sono stati scelti **quattro** (lavoro e imprese, chi vive nel
bresciano, le due economie, aria e clima), e il resto resta materiale di
contorno che entra solo se un asse portante lo richiama.

## 10. Cosa è riutilizzabile di questo metodo

Per chi volesse rifare l'esercizio su un'altra provincia italiana, la parte
trasferibile è quasi tutta:

- **Le fonti sono nazionali.** ISTAT SDMX, MEF, ARPA regionale e i confini
  ISTAT coprono l'Italia intera: cambiare provincia significa cambiare un
  codice in un file di configurazione.
- **Il codice ISTAT come chiave unica** elimina l'intera classe di problemi
  legati ai join per nome.
- **Le tre trappole tecniche** (header SDMX, chiavi posizionali, separatori
  numerici) si presenteranno identiche, e sono documentate con le ricette che
  le evitano in [`FONTI.md`](FONTI.md) §10-11.
- **La regola MET-9** — decomporre prima di titolare — è la più generale delle
  undici, e vale ben oltre questo dominio.
- **La struttura della pipeline**: un modulo per tema che espone
  `build(comuni)`, registrato in un unico punto, con cache su disco delle
  risposte grezze e tabelle tidy versionate come prodotto.

---

## Riferimenti interni

| Documento | Cosa contiene |
|---|---|
| [`FONTI.md`](FONTI.md) | Registro delle fonti con stato di accesso verificato; note tecniche SDMX e ricette collaudate |
| [`METODOLOGIA.md`](METODOLOGIA.md) | Le undici decisioni metodologiche per esteso |
| [`BRIEF.md`](BRIEF.md) | La domanda, gli assi, le storie candidate |
| [`PROSSIMI-PASSI.md`](PROSSIMI-PASSI.md) | Consegna: cosa resta da scaricare, decisioni aperte, come si costruiscono analisi e sito |
| [`pipeline/`](pipeline/README.md) | Il codice, con le trappole documentate |
| [`dati/`](dati/README.md) | Le diciannove tabelle prodotte |

*Versione 0 — agosto 2026. Da rivedere quando l'analisi sarà stata fatta: la
§7 è provvisoria e la §6.2 elenca controlli non ancora eseguiti.*
