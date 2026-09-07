# Il numero giusto, la frase falsa

**Undici modi di sbagliare un ritratto territoriale con dati corretti, trovati
costruendone uno.** Brescia, il comune e i suoi 205 comuni, 1990–2025.

> **Cos'è questo documento.** L'esposizione autocontenuta di **come** si
> costruisce il ritratto — fonti, disegno dei dati, decisioni metodologiche,
> strategia inferenziale e limiti — pensata perché un lettore esterno possa
> **replicare, criticare o riutilizzare** il metodo. Non sostituisce i
> documenti operativi ([`METODOLOGIA.md`](METODOLOGIA.md),
> [`FONTI.md`](FONTI.md), [`BRIEF.md`](BRIEF.md)): li sintetizza e li
> referenzia. Ogni numero citato è riproducibile da
> [`pipeline/`](pipeline/README.md).
>
> ## Versione 1.1 — settembre 2026
>
> **Questo documento non è più una bozza, e ha finalmente un titolo che dice
> una tesi invece del suo oggetto.**
>
> La tesi è quella del titolo. Costruendo un ritratto quantitativo di una
> provincia italiana con sole fonti aperte, il lavoro difficile non è stato
> ottenere i dati né calcolarli: è stato il passo fra **un numero corretto e la
> frase che lo riporta**. Undici volte un dato giusto stava per produrre
> un'affermazione falsa, e le undici si raggruppano in quattro famiglie
> (§Sintesi). Otto sono state scoperte dopo averle commesse, tre prima. La
> parte riutilizzabile di questo lavoro è il **catalogo** e la disciplina che
> lo intercetta, non il ritratto di Brescia.
>
> Cosa è cambiato nella 1.1: l'**undicesimo episodio**, trovato costruendo la
> pagina che esplora gli indicatori. Non è un errore nuovo di tipo: è la
> famiglia D che si allarga, ed è il primo episodio che nasce dal **prodotto**
> invece che dall'analisi. Ne è uscita MET-27.
>
> Cosa era cambiato nella 1.0 rispetto alla versione 2: la §7 copre **cinque**
> assi (è arrivata la casa, §7.9); la sintesi passa da sei episodi a dieci e li
> raggruppa; le regole del racconto — che questo documento e
> [`METODOLOGIA.md`](METODOLOGIA.md) dichiaravano mancanti — sono scritte
> (MET-22…MET-26); §5, §9 e §10 sono aggiornate.
>
> Le storie sono **otto** e sono chiuse. Il documento non aspetta altro: le
> revisioni successive verranno da lettori esterni, che è il modo in cui, nel
> progetto gemello, sono arrivate le tre regole più importanti.

---

## Sintesi

Il progetto costruisce un ritratto quantitativo di Brescia — il comune, la
provincia e i suoi 205 comuni — a partire da fonti esclusivamente aperte:
ISTAT (censimento permanente, registro ASIA delle unità locali, criminalità,
forze di lavoro, commercio estero, indice dei prezzi al consumo), MEF
(dichiarazioni dei redditi per classi di importo), ARPA Lombardia (qualità
dell'aria dal 1992 e clima dal 1990), Regione Lombardia (flussi turistici),
Agenzia delle Entrate (quotazioni immobiliari OMI e volumi di compravendita dal
2004), ISTAT `demo.istat.it` (bilancio demografico comunale). **Trentuno**
tabelle tidy, tutte ricostruibili con `requests` e la libreria standard di
Python, senza chiavi API — e da lì un sito statico autocontenuto, costruito
senza alcuna dipendenza a runtime, con **otto storie**.

Il problema metodologico centrale **non** è l'N piccolo — 205 comuni sono
abbastanza — ma tre altre cose: la **eterogeneità delle grane** (alcuni assi si
fermano alla provincia, altri arrivano al comune, uno solo scende sotto: le
zone OMI del capoluogo), la **disomogeneità delle finestre temporali** (da
trentaquattro anni a sei), e soprattutto la **fragilità semantica degli
aggregati amministrativi**, che cambiano per ragioni contabili senza che cambi
nulla nel mondo.

### Il risultato principale: undici volte un numero giusto stava per dire una cosa falsa

Nessuno degli undici è un errore di programmazione, e nessuno sarebbe stato
intercettato da un test sui dati: le tabelle erano corrette in tutti e undici i
casi. Sono undici modi diversi di **sbagliare la frase** che riporta un numero
giusto. **Otto sono stati commessi e corretti; tre intercettati prima di finire
in una frase.**

**Famiglia A — sul numero: scomporre, o confrontare, prima di dargli un nome.**

1. **§6.1 / MET-9 — decomporre prima di titolare.** Una variazione aggregata
   spettacolare — il crollo dell'occupazione nelle grandi unità locali del
   capoluogo — si è dissolta appena scomposta per settore, e poi ancora appena
   guardata a due scale territoriali: la manifattura grande non si era mossa, e
   le due divisioni di servizi che facevano tutto il calo non avevano perso
   lavoro ma cambiato forma societaria o comune di registrazione.
2. **§4 / MET-12 — per la convergenza serve il livello iniziale.** Correlare la
   crescita con il livello finale è un artefatto, perché il livello finale
   contiene la crescita. Sul reddito bresciano i due calcoli danno **segni
   opposti**: la convergenza esiste ed è forte, e il calcolo sbagliato la
   nasconde.
3. **§7.1 / MET-14 — un numero senza termine di paragone non è un risultato.**
   La frase che il progetto ripeteva dal primo giorno — «Brescia è un
   territorio di microimprese» — è vera in assoluto e fuorviante come
   descrizione: la provincia italiana mediana è **più** frammentata di Brescia,
   non meno. Misurare un territorio solo contro sé stesso fa scambiare la
   normalità di un paese per la caratteristica di un luogo.
4. **§7.6 / MET-15 — una variazione netta non è una spiegazione, e il titolo
   che le si dà non deve contenerne una.** La prima storia si intitolava «dove
   il bresciano si svuota» e la parola *spopolamento* portava con sé un
   meccanismo — la gente se ne va — che una differenza fra due stock non
   contiene. Scomposta, la risposta è l'opposto: sui 93 comuni in calo la
   migrazione interna sommata vale **−66 persone in sei anni** contro −10.163
   di saldo naturale.

**Famiglia B — sullo strumento: quando cambia il righello, la misura misura il
righello.**

5. **§7.7 / MET-16 — quando la rete di misura cambia, la media misura la rete.**
   *Intercettato prima.* Le centraline dell'aria aprono e chiudono, e la media
   annua di quelle presenti avrebbe attribuito all'atmosfera un miglioramento
   che sta in parte nel rimaneggiamento della rete. Il conto ingenuo, calcolato
   apposta per il confronto, esagera due cali di tre punti e **rovescia il
   segno** del terzo.
6. **§7.9 / MET-20 — un indice pubblicato in più basi non è una serie.**
   *Intercettato prima.* ISTAT pubblica l'indice dei prezzi al consumo in tre
   basi che non si sovrappongono in nessun anno. Messi in colonna, quei numeri
   disegnano **due crolli del trenta per cento mai avvenuti** — e la serie
   sbagliata supera ogni controllo che verrebbe in mente: gli anni ci sono
   tutti, i valori sono positivi, l'indice cresce a tratti.
7. **MET-19 — l'unità di misura è una dimensione della tabella, non una nota.**
   Sempre nell'OMI, e non è la stessa cosa di sopra: lì cambiava la **base di
   un indice**, qui cambia il **metro con cui si misura la superficie**. Negli
   affitti la base passa da netta a lorda nel 2025, e la media del capoluogo
   «cala» di due decimi senza che il mercato si muova. La colonna che lo dice
   esiste ed è larga un carattere: guardarla è una decisione, non una
   distrazione.

**Famiglia C — sulla forma della serie.**

8. **§7.9 / MET-21 — un estremo ricalcolato ogni anno è un inviluppo, non una
   serie.** Il grafico delle zone OMI del capoluogo ha una linea chiamata «la
   più economica»: il minimo si ricalcola su ogni annata, e la zona che lo
   occupa cambia **tre volte in ventidue anni**. Il conto era giusto, il
   grafico era giusto, e le tre parole sotto le linee dicevano un'altra cosa.

**Famiglia D — sul processo, non sul dato.** Sono i tre che nessuna rilettura
del singolo numero avrebbe trovato, perché il difetto sta fra i pezzi.

9. **§4 / MET-13 — una decisione sul dato mancante si prende in un posto solo.**
   Due parti del progetto rispondevano numeri diversi alla stessa domanda, non
   per un errore di calcolo ma perché ciascuna aveva deciso per conto suo cosa
   fare di una cella che la fonte non pubblica. L'ha trovato lo script che
   ricalcola ogni cifra citata, che è precisamente il motivo per cui esiste.
10. **MET-23 — uno standard che sale in silenzio lascia indietro quello che
    c'era prima.** Contando l'anatomia delle otto storie, **quattro non
    dichiaravano la propria scheda di confidenza**, che MET-4 impone dal primo
    giorno — ed erano le quattro più vecchie. Il difetto era invisibile perché
    la provenienza automatica esiste solo sulle mappe, e chi controllava
    guardava le mappe.
11. **MET-27 — un numero dichiarato e l'elenco che lo mostra vengono dalla
    stessa sorgente.** `dati.html`, cioè proprio la pagina che documenta i
    dati, annunciava «gli N indicatori» con N preso dal manifesto della
    pipeline — **diciannove** — e due paragrafi sotto costruiva l'elenco dai
    dati incorporati in quella pagina, che erano i **quindici** del racconto.
    Diciannove promessi, quindici elencati, per mesi. Nessuno dei due numeri
    era sbagliato: la frase falsa nasceva dall'averli presi da due sorgenti
    diverse e messi a un paragrafo di distanza. È l'unico degli undici trovato
    non analizzando ma **costruendo** — è saltato fuori scrivendo la pagina che
    esplora, che gli indicatori li mostra tutti.

**Cosa hanno in comune.** Quattro sono la stessa disciplina applicata a oggetti
diversi (**scomporre, o confrontare, prima di dare un nome a una variazione**);
tre sono la stessa disciplina applicata allo **strumento** invece che al numero;
uno alla **forma** della serie; tre al **processo** che produce il documento
invece che al documento. Nessuno di essi richiede statistica avanzata per essere
evitato, e nessuno di essi si evita con più dati.

**Il costo, dichiarato.** Otto degli undici sono stati scoperti *dopo* essere
stati commessi, e quattro erano già nel sito costruito quando sono stati
trovati. Il
meccanismo che li ha trovati non è la revisione: è avere una **seconda
implementazione** che ricalcola ogni cifra citata (`analysis/verifica_cifre.py`,
160 verifiche), un **termine di paragone esterno** su ogni asse, e l'abitudine
di **contare** l'anatomia di quello che si è scritto invece di ricordarsela.

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

Sedici regole, esposte per esteso in [`METODOLOGIA.md`](METODOLOGIA.md). Le
prime undici sono principi; le cinque successive sono nate ciascuna da un caso
concreto, e i loro casi sono la §6.1 e la §7. In sintesi:

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
| MET-12 | **Per la convergenza serve il livello iniziale**: correlare la crescita con il livello finale è un artefatto, e sul reddito bresciano cambia il segno (§7.3). |
| MET-13 | **Una decisione sul dato mancante si prende in un posto solo**, altrimenti due script rispondono numeri diversi alla stessa domanda. |
| MET-14 | **Un numero senza termine di paragone non è un risultato** (§7.1). |
| MET-15 | **Una variazione netta non è una spiegazione**, e il titolo che le si dà non deve contenerne una (§7.6). |
| MET-16 | **Quando la rete di misura cambia, la media misura la rete**: panel bilanciato sulle serie lunghe, anomalie quando le unità non sono confrontabili fra loro (§7.7). |

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

Arrivati con gli assi successivi, e tutti con la stessa regola — una sola
operazione fra due grandezze osservate, mai un punteggio:

- **Specializzazione settoriale**: quota di addetti nella manifattura *meno*
  quota in alloggio e ristorazione. Una differenza fra due quote, non un indice:
  il segno è il messaggio (rosso manifatturiero, blu turistico) e il lettore può
  rifarla a mano. La correlazione fra le due quote è **−0,67**, e va detto che è
  in parte aritmetica: sono due fette della stessa torta, e quando una cresce
  all'altra resta meno spazio.
- **Euro costanti** (MET-20): qualunque serie monetaria moltiplicata per il
  rapporto fra l'indice dei prezzi dell'anno base e quello dell'anno. È
  l'indicatore derivato con l'assunzione più pesante di tutto il progetto —
  l'indice è **nazionale** — ed è anche quello che cambia il segno di un
  risultato: il prezzo delle case passa da +2,3 % a −30,8 %.
- **Anomalie di temperatura** (MET-16): scostamento di ogni stazione dalla
  *propria* media 1991–2020, mediato fra stazioni. Non una temperatura media
  provinciale, che con stazioni fra i 47 e i 2.108 metri non descriverebbe
  nessun luogo e cambierebbe alla chiusura di una stazione di montagna.
- **Forbice fra zone**: rapporto fra il massimo e il minimo delle zone OMI del
  capoluogo nell'anno. È un **inviluppo** e non una serie (MET-21), quindi ogni
  punto porta il nome della zona che lo produce, e il risultato è ricalcolato
  anche seguendo le due zone del primo anno.
- **Indice di Moran**: autocorrelazione spaziale su una matrice di contiguità
  per vertice condiviso. È l'unico indicatore del progetto che dipende dalla
  **geometria** e non solo dalla tabella, ed eredita quindi un'assunzione
  amministrativa: i confini sul Garda passano dentro il lago, quindi due comuni
  su sponde opposte risultano contigui.

Nessun «indice di trasformazione» composito è previsto, e dopo cinque assi la
decisione regge: ognuno dei nove risultati della §7 si dice con **una
grandezza osservata o un rapporto fra due**. Se un indice composito arriverà,
dovrà avere definizione selezionabile e componenti a vista.

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

**La risposta, arrivata dopo** (agosto 2026). Le due domande aperte — se la
divisione 81 fosse davvero scesa a zero o riclassificata, e se il crollo della
somministrazione fosse reale — richiedevano una tabella che non esisteva:
l'incrocio fra divisione Ateco e classe dimensionale. Il vincolo che sembrava
impedirlo era sulla dimensione **territoriale**, e fissando quella (un solo
codice comune) le altre due si possono lasciare libere: mezzo mega di risposta,
quattro richieste in tutto.

Il metodo per rispondere è guardare **la stessa divisione a due scale diverse**.

| Divisione 81 · servizi per edifici | Δ 2018→2023 |
|---|---|
| classe ≥250, comune di Brescia | −3.123 (la classe scompare) |
| **tutte le classi**, comune di Brescia | −1.493 |
| **unità locali**, comune di Brescia, tutte le classi | **+157** |
| tutte le classi, **provincia** | −536 su 12.699 (−4 %) |

Le due unità grandi non hanno chiuso: il comune conta 157 unità locali **in
più** e perde meno della metà degli addetti che la classe grande ha perso. È
una frammentazione societaria, non una perdita di lavoro. In provincia la
divisione è ferma.

| Divisione 78 · somministrazione | Δ 2018→2023 |
|---|---|
| classe ≥250, comune di Brescia | −4.167 |
| tutte le classi, comune di Brescia | −4.830 |
| tutte le classi, **provincia** | −882 su 17.782 (−5 %) |

Qui il capoluogo perde davvero, ma la provincia quasi no: **il lavoro non è
uscito dal bresciano, è uscito dal capoluogo**. Per una fonte che attribuisce i
somministrati all'unità locale dell'agenzia, spostare una sede basta a produrre
questo movimento. E la discontinuità è concentrata in un anno solo — 8.686 nel
2019, 4.393 nel 2020 — che è il profilo di un cambio di registrazione, non di
un'erosione di mercato.

**Conclusione.** Il titolo originale era falso due volte. La manifattura grande
non si è mossa (−51 addetti su 4.448) e le due divisioni che fanno tutto il calo
non hanno perso lavoro: una ha cambiato forma, l'altra comune. Resta aperto solo
il confronto con province comparabili — Bergamo è il controllo naturale, e tutte
le fonti usate qui la coprono già.

**La regola che ne discende (MET-9).** *Nessun titolo su una variazione
aggregata prima di averla scomposta per settore e verificata contro almeno una
spiegazione amministrativa alternativa.* Un aggregato che si muove molto e
all'improvviso è, fino a prova contraria, un cambiamento di come si conta.

Il costo di questo controllo è stato una singola query. Il costo di non farlo
sarebbe stato pubblicare una tesi sulla deindustrializzazione del capoluogo
che i dati non sostengono.

### 6.2 I controlli, eseguiti e non

**Eseguiti** (agosto 2026):

- ✅ **Robustezza delle correlazioni.** Ogni correlazione riportata è calcolata
  in coppia (Pearson e Spearman) e ripetuta tre volte: su tutti i comuni, senza
  il capoluogo, e senza capoluogo e comuni a forte vocazione turistica. Questi
  ultimi sono definiti **dai dati** — almeno 25 presenze per abitante nel 2024,
  ne risultano 21 — e non da una lista presa altrove, così la soglia è
  ispezionabile. Sulla convergenza dei redditi togliere gli outlier **rafforza**
  il risultato (da −0,45 a −0,53), il che è il verso rassicurante.
- ✅ **Autocorrelazione spaziale.** Contiguità per vertice condiviso ricavata dal
  GeoJSON (grado medio 5,37, nessun comune isolato), indice di Moran con pesi
  normalizzati per riga e significatività per permutazione con seme fisso. Tutti
  gli indicatori provati risultano spazialmente aggregati, dal più al meno:
  densità 0,64, specializzazione settoriale 0,44, reddito 0,43, crescita della
  popolazione 0,34, presenze per abitante 0,23, addetti per abitante 0,10.
  **Conseguenza da tenere presente in ogni test successivo**: i 205 comuni non
  sono 205 osservazioni indipendenti, e i gradi di libertà effettivi sono meno.
- ✅ **La correzione di MET-12.** La correlazione fra livello e crescita è stata
  rifatta sul livello iniziale dopo aver scoperto che quella sul livello finale
  è un artefatto (§4). Sul reddito i due calcoli danno segni opposti.

**Non ancora eseguiti**, in ordine di importanza:

- ✅ **Confronto fra province, sulle imprese** (`analysis/confronto_province.py`).
  È il controllo che ha cambiato di più il testo: la §7.1 diceva il contrario
  prima di averlo.
- ✅ **Replicazione della convergenza dei redditi su Bergamo**
  (`analysis/convergenza_confronto.py`). Il risultato regge identico fuori da
  Brescia, il che lo rende più solido e meno bresciano.
- **Rottura Covid**, testata in modo sistematico. Oggi è dichiarata (MET-8) e
  mostrata su un caso solo — la serie della classe ≥250 del capoluogo, dove la
  discontinuità del 2020 è visibile a occhio.
- ✅ **Confronto fra province, sul turismo** (`analysis/confronto_turismo.py`).
  Era il più difficile dei quattro, e l'unico che non fosse gratis: le altre
  volte la fonte era nazionale e bastava non filtrarla, qui è regionale e ne è
  servita una seconda. Ha aggiunto un risultato che il progetto non stava
  cercando (§7.8) e due regole (MET-17, MET-18).
- ✅ **Decomposizione demografica** (`analysis/decomposizione_popolazione.py`).
  Era la prima voce della sezione «cosa non possiamo dire» del sito, ed è stata
  l'unica di quella lista che si sia potuta togliere scaricando una tabella. Il
  risultato è in §7.6 e ribalta la parola su cui poggiava la prima storia. Porta
  con sé anche il **quarto uso del confronto fra province**, gratis: il file
  della fonte è nazionale.
- **Rottura Covid sulla popolazione.** La scomposizione di §7.6 somma sei anni,
  quindi passa sopra il 2020 come qualunque media (MET-8). I dati sono mensili e
  la discontinuità si potrebbe isolare: nel 2020 la mortalità bresciana è stata
  fuori scala, e non sapere quanta parte del saldo naturale di sei anni venga da
  quei pochi mesi è un buco reale in §7.6.

## 7. Risultati

Nove risultati sul territorio — da non confondere con gli undici episodi della
sintesi, che riguardano il metodo e non Brescia. Nessuno è causale: sono
descrizioni, e la §8 dice cosa non permettono di affermare. Quattro di essi —
§7.1, §7.3, §7.6 e §7.8 — hanno un termine di paragone esterno; §7.4, §7.7 e
§7.9 no, e la §8 dice quali conclusioni questo indebolisce.

### 7.1 La domanda di partenza era mal posta

La domanda che ha originato il progetto era: *Brescia è ancora il territorio
della meccanica fatta di piccole aziende?* Presa alla lettera, la risposta è sì:
le unità locali sotto i dieci addetti sono il **92,7 %** del totale (erano il
92,8 % nel 2018) e occupano il **42,9 %** degli addetti (44,2 % nel 2018).
Cinque anni non hanno spostato la struttura.

**Ma il confronto con le altre province rovescia il senso della frase.** La
provincia italiana mediana ha il **94,4 %** di unità locali sotto i dieci
addetti: Brescia è la **101ª su 107**, cioè fra le meno frammentate del paese.
Sugli addetti la distanza è più larga ancora — 42,9 % contro una mediana del
51,0 % — e l'unità locale bresciana media ha **4,01** addetti contro 3,44.

| Indicatore, 2023 | Brescia | mediana | rango |
|---|---|---|---|
| unità locali sotto i 10 addetti | 92,7 % | 94,4 % | 101ª |
| addetti in unità sotto i 10 | 42,9 % | 51,0 % | 85ª |
| addetti per unità locale | 4,01 | 3,44 | 21ª |
| addetti nella manifattura | 32,4 % | 20,7 % | **15ª** |
| crescita degli addetti 2018–2023 | 1,27 %/anno | 1,43 %/anno | 65ª |

Il 92,7 % descrive **l'Italia**, non Brescia. Quello che distingue davvero questa
provincia è il **settore**: 15ª d'Italia per quota manifatturiera, in un grumo
di province che sono i distretti industriali del nord — Vicenza, Treviso, Reggio
Emilia, Modena, e Bergamo, che le sta accanto su quasi ogni riga.

Anche la crescita va ridimensionata dallo stesso confronto. Degli **29.421**
addetti guadagnati fra 2018 e 2023, **23.840** sono in unità da 10 a 249: l'81 %,
e il movimento nella fascia intermedia è reale. Ma l'1,27 % l'anno complessivo è
**sotto** la mediana provinciale italiana (1,43 %): Brescia cresce come l'Italia,
non più dell'Italia, e sull'aggregato provinciale da solo sembrava il contrario.

È l'esempio più costoso di MET-14, ed è il motivo per cui quella regola esiste.

### 7.2 Il capoluogo diverge dal territorio, ma non per il motivo che sembrava

Il fatto: la provincia guadagna 29.421 addetti mentre il comune capoluogo è
fermo (101.136 → 100.939, cioè −197). L'interpretazione industriale di questa
divergenza è però falsa, e la §6.1 la smonta per esteso: la manifattura grande
della città non si muove di 51 addetti su 4.448, e tutto il calo del vertice
dimensionale sta in due divisioni di servizi che non hanno perso lavoro ma
cambiato forma societaria o comune di registrazione.

**È il risultato metodologicamente più importante del progetto**, e vale la pena
enunciarlo in forma generale: in un registro di unità locali, una variazione
aggregata grande e improvvisa è **fino a prova contraria un cambiamento di come
si conta**. La prova contraria costa una query.

Il confronto con gli altri capoluoghi lo conferma dall'esterno. Nei **64** comuni
capoluogo che nel 2018 avevano almeno duemila addetti in unità da 250 in su, la
classe si è svuotata in **44 casi**, con una mediana del **−11,9 %**; i cali più
forti sono Matera (−72 %), Biella (−55 %), Pisa (−48 %). Brescia (−31,5 %) è il
13º. Un movimento così diffuso non è una vicenda industriale che accade
contemporaneamente in quaranta città diverse.

### 7.3 I redditi convergono; i luoghi restano diversi

Fra 2012 e 2023 il reddito imponibile medio per contribuente cresce in tutti i
205 comuni (mediana **+2,23 % l'anno**, in euro correnti), e cresce **di più
dove partiva basso**.

| Reddito medio per contribuente, 2012–2023 | Pearson | Spearman |
|---|---|---|
| livello 2012 contro crescita annua | **−0,45** | −0,47 |
| idem, senza capoluogo | −0,45 | −0,46 |
| idem, senza capoluogo e comuni turistici | **−0,53** | −0,51 |
| *(livello 2023 contro crescita — l'artefatto di MET-12)* | *+0,12* | *+0,07* |

Togliere gli outlier rafforza il risultato invece di scioglierlo, che è il verso
rassicurante.

**La dispersione si riduce, gli estremi no.** Sono due fatti diversi e vanno
tenuti separati: la distribuzione si stringe su ogni misura robusta — deviazione
standard dei logaritmi da 0,123 a 0,110, rapporto fra decili da 1,34 a 1,26 —
mentre il rapporto fra il comune più ricco e il più povero **cresce**, da 2,17 a
2,51. Quel rapporto lo decidono due comuni su duecentocinque, e sono sempre gli
stessi due (Padenghe sul Garda e Magasa): descrive quei due, non la provincia.
Una versione precedente di questa sezione scriveva che «la distanza si è ridotta
di poco» citando proprio quel rapporto, ed era sbagliata.

**E la convergenza non è bresciana.** Rifatto identico sui 240 comuni della
provincia di Bergamo, il coefficiente vale **−0,48** contro il −0,45 di Brescia:
la stessa cosa con la stessa forza (`analysis/convergenza_confronto.py`). Due
province non sono l'Italia, ma bastano a escludere che sia un artefatto locale e
a togliere a questo risultato l'aggettivo «bresciano».

Tre avvertenze che il testo pubblicato ripete e che vanno ripetute anche qui.
La prima è cambiata a settembre 2026: i livelli e i tassi sono in **euro
correnti**, ma il progetto adesso ha un deflatore (MET-20) e quindi la frase
«parte della crescita è inflazione» ha un numero. Fra il 2012 e il 2023
l'inflazione italiana è del **21,4 %**, e la mediana comunale della crescita
passa da **+2,23 % l'anno a +0,44 %**: **45 comuni su 205** perdono potere
d'acquisto invece di guadagnarne. La *convergenza* non ne è toccata — è una
relazione fra comuni, e l'inflazione è comune a tutti — ma la frase «i redditi
crescono» non regge da sola, ed è corretta nel testo pubblicato. Le altre due
restano: sono **contribuenti**, non residenti; e sono **redditi dichiarati**,
che non sono ricchezza.

### 7.4 La provincia è due economie, e sono due territori contigui

Con le quote settoriali per comune — la tabella che mancava fino ad agosto 2026
— la divisione è misurabile. In provincia la manifattura vale il **32,4 %** degli
addetti osservati da ASIA e alloggio e ristorazione l'**8,0 %**; ma **48 comuni**
hanno più della metà degli addetti nella manifattura (Mura 83,6 %, Odolo 81,3 %)
e **24** ne hanno almeno un quarto in alloggio e ristorazione (Limone sul Garda
71,0 %, Gardone Riviera 56,1 %).

Le due quote sono fortemente alternative (Pearson −0,67, Spearman −0,78), il che
è **in parte aritmetico** — sono due fette dello stesso totale — ma il valore
dice quanto la sostituzione sia netta: sul Garda la manifattura non è ridotta, è
assente.

Il fatto più solido è però spaziale: l'indice di Moran sulla specializzazione
vale **0,44**, il più alto fra le variabili economiche misurate. Non esistono
comuni manifatturieri isolati fra gli alberghi né viceversa: esistono due
territori contigui, ciascuno fatto di comuni che si somigliano. Il che, di
nuovo, ha una conseguenza metodologica prima che descrittiva — questi 205 comuni
non sono 205 osservazioni indipendenti.

### 7.5 Il resto, in breve

- **93 comuni su 205 perdono abitanti** fra 2018 e 2024, mentre la provincia nel
  complesso cresce dello 0,15 % l'anno. Le cadute più rapide sono tutte di
  montagna (Magasa −2,9 % l'anno), e non sono sparse: Moran 0,34. Il *perché* è
  in §7.6, e non è quello che la parola «spopolamento» lascia intendere.
- **La provincia è turistica, il capoluogo no.** 12.246.854 presenze nel 2024,
  di cui il 68,8 % nei primi dieci comuni, otto sul Garda. Sirmione da sola
  (1.406.590) supera Brescia città (883.531, il 7,2 %). Quanto sia tanto lo dice
  la §7.8, che usa un'altra fonte e per questo un altro totale (MET-17).
- **L'aria è migliorata, e non abbastanza.** PM10 alla stazione di Brescia
  Broletto: 45,5 µg/m³ nel 2001, 27,3 nel 2024 — una stazione confrontata con sé
  stessa, e comunque sopra la linea guida dell'Organizzazione mondiale della
  sanità. La misura provinciale, che non è una stazione sola e non si ricava
  facendo la media di quelle che ci sono, è in §7.7.
- **La città importa lavoro**: addetti localizzati su occupati residenti ≈ 1,16;
  26.425 residenti escono ogni giorno dal comune, 23.699 per lavoro (2019).

### 7.6 Lo spopolamento montano non è una partenza

È il risultato più recente ed è, di nuovo, la correzione di un titolo dato prima
di decomporre (§6.1). La prima storia del progetto misurava la variazione di
popolazione comunale — 93 comuni su 205 in calo, in una fascia contigua di
montagna — e dichiarava di non poter dire *perché*, perché una differenza fra due
stock non distingue chi muore da chi parte.

**La fonte che mancava non mancava.** Per mesi «ISTAT» ha voluto dire
`esploradati.istat.it`, cioè l'SDMX; il bilancio demografico sta su un altro
sito dello stesso istituto, `demo.istat.it`, con un'altra logica — un CSV
zippato per anno con dentro tutti gli 7.896 comuni italiani. Sei anni si
scaricano in mezzo minuto.

Quello che rende la scomposizione utilizzabile senza mescolare due popolazioni
diverse è un'identità verificata e non assunta: la riga «Popolazione censita al
31 dicembre» del bilancio **coincide** con la popolazione del censimento
permanente, comune per comune e anno per anno, allo zero. La decomposizione
quindi chiude — popolazione iniziale più componenti più aggiustamento uguale
popolazione censita — e la pipeline si rifiuta di scrivere le tabelle se un
giorno smette di chiudere. Non è un modello con un residuo da interpretare.

**Il risultato provinciale.** Fra il 2018 e il 2024 la provincia guadagna 11.465
abitanti, con questa composizione:

| Componente | Persone | ‰ della popolazione 2018 |
|---|---:|---:|
| saldo naturale | **−25.764** | −20,5 |
| migrazione interna | +13.970 | +11,1 |
| migrazione estera | **+27.817** | +22,2 |
| aggiustamento statistico | −4.558 | −3,6 |
| **variazione** | **+11.465** | **+9,1** |

Senza la sola componente estera la provincia **perderebbe 16.352 abitanti**. La
crescita non viene dalle nascite: il saldo naturale è negativo in 189 comuni su
205.

**Il risultato comunale, che ribalta la parola.** Sommando i 93 comuni che
perdono abitanti, la migrazione interna vale **−66 persone in sei anni** contro
−10.163 di saldo naturale. Sessantasei persone su un insieme di comuni che ne
contano oltre centomila non è una cifra piccola, è indistinguibile da zero: chi
ci abita **non se ne sta andando**. In 81 di quei 93 comuni la componente che
tira più giù è il saldo naturale, in 12 la migrazione interna, in nessuno quella
estera.

**Il controllo esterno**, che qui non costa nulla perché il file della fonte è
nazionale — lo stesso vantaggio di §7.1 sulle imprese. Su 107 province:

| | Brescia (‰) | rango | mediana (‰) |
|---|---:|---:|---:|
| variazione | +9,1 | **6ª** | −19,7 |
| saldo naturale | −20,5 | 14ª | −34,4 |
| migrazione interna | +11,1 | 33ª | +6,1 |
| migrazione estera | +22,2 | 44ª | +20,8 |

Solo 21 province italiane crescono, e il saldo naturale è positivo in **una
sola**. Il calo demografico non è montano né bresciano: è italiano. Quello che
distingue Brescia non è che qui si facciano più figli — non se ne fanno, e la
provincia è comunque quattordicesima proprio perché il resto d'Italia sta
peggio — ma quanta gente arriva.

**Una voce che resta fuori, e va detto perché.** L'aggiustamento statistico
(−4.558 persone) è la rettifica che riconcilia l'anagrafe con il censimento, non
un fenomeno demografico. Nel progetto resta una colonna a sé in
`bilancio_demografico_comuni.csv`, nel grafico e in questo documento: sommarlo
alle migrazioni farebbe dire al lavoro che se ne sono andate persone che in
anagrafe non c'erano più. Su un comune di poche centinaia di abitanti basta a
cambiare il segno.

**Cosa questa scomposizione ancora non dice.** Il bilancio conta chi entra e chi
esce da ogni comune, **non la coppia origine-destinazione**. «Chi lascia la Valle
Camonica scende in città» resta fuori portata: servirebbero le matrici di
migrazione, che non sono pubblicate a grana comunale.

### 7.7 L'aria migliora, il clima no, e la pioggia non dice niente

È il risultato con la finestra più lunga di tutto il lavoro — vent'anni contro i
sei degli assi economici — e l'unico che non ha per unità il comune. In tutta la
provincia le centraline di qualità dell'aria sono esistite, in vent'anni, in **11
comuni su 205** — sette delle quali nel solo capoluogo, e una per ciascuno degli
altri dieci; oggi ne restano attive meno — e le
stazioni meteorologiche non coincidono con esse: l'unità osservata è il
**sensore**, e nessuna delle due reti sostiene una coropletica.

**Il problema di disegno viene prima del risultato**, e su questi dati è
severo: le reti aprono e chiudono stazioni. Sul PM10 la rete bresciana passa da
due sensori a sette nell'arco della serie, e non sono gli stessi due. La media
annua «di quello che c'è» misura quindi anche il rimaneggiamento della rete — e
lo misura con un segno prevedibile, perché le prime centraline nascono dove il
problema è grosso e quelle successive tendono a stare in posti più puliti. È lo
stesso genere di artefatto della §6.1: il disegno della misura che produce il
risultato. Il rimedio è il **panel bilanciato** — solo i sensori osservati in
tutti gli anni della finestra — e il conto ingenuo riportato accanto, perché la
distanza fra i due quantifica il contributo della rete. È MET-16.

| Inquinante | panel | sensori | primi 3 anni | ultimi 3 anni | variazione | conto ingenuo |
|---|---|---:|---:|---:|---:|---:|
| PM10 | 2005–2025 | 3 | 48,7 µg/m³ | 28,2 | **−42,0 %** | −45,5 % |
| biossido di azoto | 2003–2025 | 4 | 36,3 µg/m³ | 22,2 | **−38,9 %** | −42,3 % |
| ozono | 2005–2025 | 3 | 54,7 µg/m³ | 53,7 | **−1,8 %** | +5,5 % |

Due dei tre inquinanti crollano di circa il quaranta per cento; il terzo non si
muove. La differenza non è statistica ma fisica, e vale la pena esplicitarla
perché è il motivo per cui «l'aria» non è una grandezza sola: il particolato e
il biossido di azoto sono inquinanti **primari**, escono da una sorgente
identificabile; l'ozono è **secondario**, si forma in atmosfera. Questo lavoro
può dire che non scende. Non può dire perché, e la §8 lo mette per iscritto.

Si noti che il conto ingenuo esagera i due cali di tre punti e **rovescia il
segno** del terzo: sull'ozono darebbe +5,5 % contro il −1,8 % del panel. Sulle
due serie in caduta l'artefatto è un'esagerazione; su quella ferma è un
risultato inventato di sana pianta.

**La temperatura pone un problema diverso**, e la soluzione ingenua è peggiore.
Le stazioni bresciane stanno fra i 47 metri di Gambara e i 2.108 del Pantano
d'Avio: la loro media aritmetica non descrive nessun luogo, e — più grave —
cambierebbe di mezzo grado alla sola chiusura della stazione più alta, senza che
sia successo niente. Ciascuna stazione si confronta quindi con sé stessa, con la
propria media 2004–2013, e si mediano gli **scostamenti**.

| | valore |
|---|---:|
| scostamento medio, 2016–2025 contro 2004–2013 | **+1,10 °C** |
| stazioni con entrambe le finestre osservate | 8 |
| stazioni in aumento | **8 su 8** |
| quote coperte | 47 – 2.108 m |

Il grado in più conta meno della sua distribuzione: **non c'è un'eccezione**, né
in pianura, né in valle, né sul ghiacciaio. Un effetto che si ripete con lo
stesso segno in otto siti indipendenti non lo produce un sensore tarato male, ed
è il controllo che rende il risultato credibile senza bisogno di un test.

**Il controllo negativo, che è la parte utile.** Dalla stessa rete, con lo stesso
metodo e sulle stesse due finestre, la **precipitazione** non dà segnale: su 12
stazioni, 7 in aumento e 5 in calo, con una variazione mediana di **+0,5 %**. Il
segno non è concorde e la mediana è mezzo punto: con questa rete e questa
finestra la risposta è che non lo sappiamo. Il risultato resta nel racconto e in
questo documento per la ragione che il progetto applica altrove ai controlli
falliti (§6.2): una serie **senza** segnale ottenuta con lo stesso procedimento è
la prova che il procedimento non fabbrica segnali. Senza di essa il +1,10 °C
sarebbe un numero da prendere sulla fiducia.

**Cosa questo risultato non è.** Non è una misura dell'aria della provincia: è
una misura dell'aria dove stanno le centraline, che non sono collocate a caso.
Non è una serie di cause: la meteorologia governa la dispersione degli inquinanti
quanto le emissioni, e separarle richiederebbe una normalizzazione meteorologica
che medie mensili non sostengono. E non è un confronto esterno — a differenza di
§7.1, §7.3 e §7.6, questo asse non è stato collocato fra le province italiane,
perché la fonte è regionale.

### 7.8 La provincia è la decima d'Italia per turismo, e nessuno lo direbbe

È l'ultimo risultato in ordine di tempo, e nasce da una domanda che il metodo
imponeva e la fonte impediva. La §7.5 dice che la provincia è turistica; MET-14
chiede *rispetto a cosa*, e la risposta non c'era, perché la fonte comunale è
regionale e si ferma al confine lombardo. Serve una **seconda fonte**: ISTAT
pubblica il movimento dei clienti negli esercizi ricettivi per tutte e 107 le
province, dal 2008.

| Indicatore, 2024 | Brescia | mediana provinciale | rango |
|---|---|---|---|
| presenze | 11.068.441 | 2.088.719 | **10ª** |
| presenze per abitante | 8,74 | 4,97 | 29ª |
| quota di presenze straniere | 72,0 % | 37,7 % | **6ª** |
| presenze in campeggi e villaggi | 26,7 % | 9,1 % | 19ª su 98 |
| quota alberghiera | 52,9 % | 62,1 % | 78ª |
| crescita 2019→2024 | +13,8 % | +5,5 % | 26ª |
| caduta nel 2020 | −54,3 % | −49,5 % | 40ª |

**Il primo numero è il risultato.** Brescia è la **decima provincia italiana per
presenze turistiche**, dietro Roma, Venezia, Bolzano, Trento, Verona, Milano e
poche altre, con più di cinque volte le notti della provincia mediana. È un
fatto che questo lavoro non stava cercando: il progetto è nato per chiedersi se
Brescia sia ancora il territorio della meccanica (§7.1), e il turismo era
classificato come asse di contorno.

**Il secondo numero lo ridimensiona, e insieme lo spiega.** Per abitante Brescia
è ventinovesima, cioè sopra la mediana ma lontanissima da Bolzano (68,7 notti
per residente) o Rimini (44,1). Le due letture non si contraddicono: Brescia è
decima perché è **grande**, con 1,27 milioni di abitanti, non perché sia
intensamente turistica. È la stessa disciplina di §7.1 applicata a un altro
asse — un valore assoluto e un valore per unità dicono cose diverse, e citarne
uno solo è scegliere la conclusione.

**Il terzo numero è quello specifico.** Il **72,0 %** delle presenze bresciane
viene dall'estero: solo cinque province italiane fanno di più (Como, Verbano-
Cusio-Ossola, Firenze, Verona, Venezia), e la mediana nazionale è **37,7 %**.
Questa è la caratteristica che non si spiega con la dimensione: la provincia ha
un turismo internazionale come quello delle città d'arte, ma non ha le città
d'arte. La composizione dice dove sta: **26,7 %** delle notti in campeggi e
villaggi contro una mediana del 9,1 %, e una quota alberghiera sotto la mediana
(78ª su 107). È il Garda — e la §7.5, che sulla fonte comunale trova otto dei
primi dieci comuni sul lago, dice lo stesso da dentro.

**La serie lunga, che la fonte comunale non aveva.** Dal 2008 al 2024 le
presenze bresciane crescono del **2,09 % l'anno** composto, contro una mediana
provinciale dello **0,96 %** (24ª su 99 province con la serie intera). La quota
straniera sale in parallelo, dal 61,9 % al 72,0 %: non è che siano arrivati più
italiani in un posto già internazionale, è che l'internazionalizzazione è essa
stessa la crescita. Bergamo, la provincia gemella su quasi ogni altro
indicatore, cresce più in fretta (+2,98 %) — e per una ragione che questo dato
non contiene, perché è la storia di un aeroporto e non di un lago.

**Il 2020 e il ritorno.** La caduta bresciana è più profonda della mediana
(−54,3 % contro −49,5 %), il che è coerente con una domanda estera: i confini
chiusi pesano più della vacanza corta di prossimità. Il recupero però è più
rapido della mediana, e nel 2024 la provincia sta il 13,8 % sopra il 2019
mentre 35 province su 107 non hanno ancora riguadagnato il livello. Fra le
rotture del 2020 misurate in questo lavoro (`rottura_covid.py`) questa è di gran
lunga la più profonda — le presenze perdono più della metà, gli addetti il
2,7 % e la classe ≥250 della provincia il 19,5 % — ed è anche quella che si è
richiusa più in alto.

**Il controllo che questo risultato porta con sé, ed è la parte scomoda.** Le
due fonti sul turismo bresciano **non danno lo stesso numero**, e la distanza
cresce: la somma dei comuni di Regione Lombardia sta sopra il totale
provinciale ISTAT del **6,5 % nel 2019** e del **10,6 % nel 2024**. Sugli arrivi
lo scarto è la metà (2,0 % → 7,0 %), quindi il fenomeno riguarda le **notti** e
non il conteggio delle persone. Nessuna delle due è sbagliata: sono due filiere
di rilevazione con due perimetri. Ma è il motivo per cui la §7.5 e questa
sezione citano due totali diversi per lo stesso 2024 — 12.246.854 e 11.068.441 —
e devono dichiararlo invece di scegliere il più comodo. La regola che ne è nata
è **MET-17**: una tabella, una fonte, e mai un numeratore da una e un
denominatore dall'altra.

**Un secondo controllo, e una cifra che non è stata scritta.** La stessa fonte
dà per il 2025 un +14,9 % di presenze sull'Italia, che sarebbe il titolo
migliore di tutto questo documento. Scomposto per tipologia si dissolve:
alberghiero +1,5 %, campeggi +1,3 %, alloggi in affitto **+87,6 %** — perché da
quell'anno la voce comprende anche la gestione non imprenditoriale. Non è un
mercato che raddoppia, è un perimetro che si allarga, e la §6.1 di questo
documento è la storia di cosa succede a non fare questa scomposizione. Il 2025
resta nei dati, marcato, e fuori da ogni confronto: è **MET-18**.

**Cosa questo risultato non dice.** Nulla sull'economia del turismo: le presenze
sono notti, non spesa, non occupazione e non valore aggiunto. Un territorio può
avere molte notti e poco valore per notte, e i campeggi sono per definizione il
segmento a valore per notte più basso: la quota del 26,7 % che rende Brescia
riconoscibile è anche la ragione per cui il decimo posto per presenze non è un
decimo posto per fatturato turistico. Il collegamento fra questo asse e gli
addetti dell'alloggio e ristorazione (§7.4) resta da fare e non è fatto qui.

### 7.9 Il prezzo della casa è fermo in euro correnti e perde un terzo in euro costanti

È il risultato più recente (settembre 2026) e l'unico in cui la conclusione
dipende interamente da **come si misura**. Nel comune di Brescia il prezzo medio
delle abitazioni civili in vendita è **1.788 €/m² nel 2004 e 1.829 nel 2025**:
`+2,3 %` in ventun anni, cioè un mercato che sembra non essersi mosso. Nello
stesso periodo l'inflazione italiana cumulata è del **47,8 %**, quindi quei
1.788 € sono **2.642 € di oggi**: in euro costanti il metro quadro perde il
**30,8 %**.

Accanto, i **volumi**. Le compravendite residenziali del capoluogo (NTN, l'unità
con cui l'Agenzia normalizza le transazioni sulla quota di proprietà) toccano il
fondo nel 2013 a 1.364 e arrivano a 3.199 nel 2025: **+134,5 %**. Le due serie
non si contraddicono e nessuna delle due, da sola, dice la frase che le tiene
insieme — *si vende molto di più a un prezzo reale molto più basso*.

**La grana che al progetto mancava, e la trappola che ci ha portato.** Le
quotazioni OMI arrivano alla **zona**, che è quanto di più vicino a un quartiere
esista in un dato ufficiale italiano, e permettono la domanda che di solito si
fa alle città: il centro si è staccato dalla periferia? La risposta bresciana è
**no, il contrario**. Sul panel bilanciato delle 13 zone presenti in tutte e 22
le annate, la forbice fra la più cara e la più economica passa da **2,21 a
1,97**, e la correlazione fra livello iniziale e variazione reale è **−0,38
(Pearson) / −0,53 (Spearman)**: chi partiva più caro ha perso di più. Con tredici
zone è una descrizione di questa città e non una legge urbana, e il leave-one-out
su due punti diversi — la zona più economica del 2004 e la sola quasi ferma in
termini reali — lascia il segno e riduce la forza (−0,34 / −0,41 e −0,27 /
−0,41).

Il panel bilanciato non è prudenza: nel **2024 la zonizzazione del capoluogo
viene rifatta**, dieci perimetri finiscono nel 2023 e dieci cominciano nel 2024.
Le zone quotate restano 23 in ogni annata, quindi una media su «quelle che ci
sono» non solleverebbe nessun sospetto e misurerebbe anche il cambio di
perimetro. È MET-16, nata sulle centraline, che si applica identica a una rete
di tutt'altra natura.

**Fuori dal capoluogo.** Su 203 comuni quotati, **181 perdono valore reale**, con
una mediana di **−1,11 % l'anno**; i pochi in crescita sono il lago e l'alta
montagna. Il livello, invece, disegna la stessa geografia della §7.4 vista dal
lato della casa: il metro quadro più caro è a Sirmione (3.535 €) e il più
economico a Provaglio Val Sabbia (700 €), **cinque volte**, e il capoluogo è solo
**18° su 203** con 1.829 €/m². Il prezzo si accompagna al reddito comunale
(+0,52 / +0,50) e il leave-one-out sui quattordici comuni rivieraschi non lo
sposta, quindi non è una relazione fatta dal Garda.

**Il controllo che questo risultato ha prodotto, ed è metodologico.** Per
scriverlo è servito un deflatore, e il deflatore non era una formalità: l'indice
ISTAT dei prezzi al consumo è pubblicato in **tre basi che non si sovrappongono
in nessun anno**, e attaccarne i livelli disegna due crolli del 30 % mai
avvenuti — una serie sbagliata che supera ogni controllo ovvio. Il raccordo si fa
con la variazione annua della fonte stessa: è **MET-20**, e il test che la tiene
in piedi verifica che ogni rapporto fra anni consecutivi riproduca la variazione
dichiarata.

**Cosa questo risultato non dice.** Le quotazioni OMI sono *indicazioni di valore
di larga massima*, non prezzi di transazione: servono a confrontare zone e anni,
non a stimare quanto vale una casa. Il deflatore è **nazionale**, quindi ogni
cifra in euro costanti assume che l'inflazione bresciana sia quella italiana.
Non c'è nessun termine di paragone esterno — non sappiamo se il −30,8 % bresciano
sia più o meno del resto d'Italia, ed è la lacuna più evidente di questo
risultato. E non c'è niente sullo **stock**: quante case siano vuote dove il
prezzo è caduto di più è la domanda successiva, e i dati censuari per rispondere
sono già in `abitazioni_comuni.csv`.

## 8. Limiti — cosa questo metodo non può affermare

- **Niente sotto il comune, e sull'aria nemmeno il comune.** Nessun asse scende
  al quartiere; l'asse ambientale (§7.7) non arriva nemmeno al comune, perché la
  sua unità è il sensore, e in vent'anni i sensori sono esistiti in 11 comuni su
  205: in 194 non ce n'è mai stato uno. Non esiste
  una mappa comunale della qualità dell'aria di questa provincia che non sia
  inventata, e le stazioni non sono collocate a caso: nascono dove il problema
  era grosso, quindi descrivono sé stesse prima del territorio. I dati
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
- **Sull'aria non si separa la tendenza dalla meteorologia.** La dispersione
  degli inquinanti dipende da vento, inversioni termiche e precipitazioni quanto
  dalle emissioni. Le medie mensili di §7.7 non sostengono una normalizzazione
  meteorologica, quindi ogni variazione riportata è quello che le centraline
  hanno misurato, non quanto è stato emesso. È il motivo per cui la §7.7 non
  attribuisce il calo del PM10 a nessuna politica né l'immobilità dell'ozono a
  nessuna causa.
- **Sulla precipitazione non si afferma niente**, e il non-risultato è
  dichiarato invece che omesso (§7.7).
- **Il commercio estero è regionale**, e la Lombardia non è Brescia.
- **Gli aggregati amministrativi sono fragili** (§6.1): il registro delle unità
  locali misura dove le cose sono *registrate*, che non sempre è dove
  accadono.
- **Il termine di paragone copre i quattro assi economici; l'ambiente no.** Il
  confronto con le 107 province è stato fatto sulle imprese (§7.1), sui
  capoluoghi (§7.2), sulla demografia (§7.6), sul turismo (§7.8), e la
  convergenza dei redditi è stata replicata su Bergamo (§7.3). Ha corretto tre
  letture e ne ha rafforzate due. Resta fuori l'**ambiente** (§7.7), e non per
  pigrizia: l'unità osservata è il sensore, la rete è regionale e le reti delle
  altre province non sono confrontabili con questa senza un lavoro che
  cambierebbe il soggetto del progetto. Quella lettura resta misurata contro sé
  stessa e va scritta come «alle centraline bresciane succede questo», mai come
  «a Brescia, a differenza di altrove, succede questo».
- **Il turismo ha due fonti che non coincidono** (MET-17), e la differenza
  cresce nel tempo: fra il 6,5 % del 2019 e il 10,6 % del 2024 sulle stesse
  presenze provinciali. Il confronto fra province (§7.8) e la lettura comunale
  (§7.5) stanno quindi su due scale leggermente diverse, e ogni cifra dichiara
  da quale viene. Quello che questo lavoro **non** ha fatto è stabilire quale
  delle due sia più vicina al vero: servirebbe la documentazione metodologica
  delle due rilevazioni, e non è un'analisi di dati.
- **Le presenze non sono l'economia del turismo.** Sono notti, non spesa né
  valore aggiunto, e il segmento che rende Brescia riconoscibile — campeggi e
  villaggi, il 26,7 % delle notti contro il 9,1 % della mediana — è per
  definizione quello a valore per notte più basso. Il decimo posto per presenze
  non è un decimo posto per fatturato, e questo lavoro non ha i dati per dire
  quale sia.
- **Due province non sono l'Italia.** La replicazione su Bergamo esclude che la
  convergenza dei redditi sia un artefatto locale; non stabilisce che sia
  generale. Bergamo è per giunta la provincia **più simile** a Brescia fra
  quelle disponibili, il che rende il controllo il più debole possibile fra
  quelli sensati: un controllo forte sarebbe una provincia diversa per
  struttura.
- **La migrazione non ha origine né destinazione.** La variazione di popolazione
  è scomposta (§7.6), ma il bilancio conta quante persone entrano ed escono da
  ogni comune, non da dove a dove. Ogni affermazione sulla *direzione* dei
  movimenti interni — la montagna che si svuota verso la città, il capoluogo che
  perde verso la cintura — resta fuori portata.
- **L'aggiustamento statistico non è attribuibile.** Vale −4.558 persone in
  provincia in sei anni (§7.6) ed è una rettifica anagrafica: si sa quanto vale,
  non di quale movimento reale sia il residuo. Su un comune piccolo basta a
  cambiare il segno della variazione.
- **Le quote settoriali hanno un denominatore parziale.** Il registro delle
  imprese non osserva agricoltura, pubblica amministrazione, istruzione pubblica
  e servizi domestici: nella Bassa agricola un comune «non specializzato» può
  essere semplicemente un comune agricolo.

## 9. Regola di arresto

Il progetto precedente si è chiuso con una regola esplicita, ed è una buona
idea averla scritta prima di averne bisogno: **un dato nuovo entra solo se
prova, precisa o smentisce una domanda già posta** — non perché esiste, non
perché sarebbe interessante, non perché il portale lo pubblica.

Il rischio specifico qui è opposto a quello di Donostia: non l'ostinazione su
una tesi, ma la **dispersione**. La ricognizione aveva individuato tredici assi
possibili; ne sono stati scelti quattro (lavoro e imprese, chi vive nel
bresciano, le due economie, aria e clima) e uno è arrivato dopo, la **casa**,
quando è arrivato il dato che nessuno riusciva a scaricare. Cinque su tredici,
e il resto resta materiale di contorno che entra solo se un asse portante lo
richiama.

**La regola ha funzionato, e si vede da quello che non è stato scritto.** Il
[`BRIEF.md`](BRIEF.md) elenca dodici storie candidate: ne sono state scritte
otto. Le quattro rimaste non sono state scartate perché deboli — il background
migratorio, gli atenei, il PNRR, il pendolarismo sono tutti temi buoni — ma
perché per nessuna di esse era chiaro **cosa chiedere alla tabella** (MET-26).
Il caso che tiene in piedi la regola è l'ottavo asse: le quotazioni OMI sono
state acquisite senza una domanda, e per due settimane sono state un dato senza
lettura. La storia è arrivata quando è arrivato il deflatore, cioè quando la
domanda è diventata «fermo rispetto a cosa?».

**Il progetto si ferma qui.** Le storie sono otto, i cinque assi hanno tutti la
loro, e ogni cifra citata è ricalcolata a ogni push. Quello che resta —
scaricare nuove fonti, aggiungere un pannello interattivo, scendere sotto il
comune — è lavoro **dopo la pubblicazione**, non prima: aggiungerlo adesso
allontanerebbe la pubblicazione invece di avvicinarla, che è la definizione
stessa della dispersione da cui questa regola protegge.

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
- **La struttura della pipeline**: un modulo per tema che espone
  `build(comuni)`, registrato in un unico punto, con cache su disco delle
  risposte grezze e tabelle tidy versionate come prodotto.

E soprattutto, la parte che questo documento considera il proprio contributo:

- **Il catalogo degli undici episodi** (§Sintesi) e le **ventisette regole** che ne
  sono uscite ([`METODOLOGIA.md`](METODOLOGIA.md)). MET-9 — decomporre prima di
  titolare — è la più generale, e vale ben oltre questo dominio; MET-14 — un
  numero senza termine di paragone non è un risultato — è quella che più spesso
  cambia una conclusione già scritta.
- **Le tre pratiche che hanno trovato gli errori**, e che si trasferiscono
  intatte:
  1. una **seconda implementazione** che ricalcola ogni cifra citata nei
     documenti e nel sito, deliberatamente senza condividere codice con ciò che
     verifica (`analysis/verifica_cifre.py`, 160 verifiche a ogni push). Ha
     trovato l'episodio 9 da sola;
  2. un **termine di paragone esterno** su ogni asse dove la fonte copre
     l'Italia — che costa un filtro su file già scaricati e ha cambiato tre
     conclusioni su quattro;
  3. **contare l'anatomia** di quello che si è scritto invece di ricordarsela.
     L'episodio 10 è stato trovato così, contando quante storie avessero la
     scheda di confidenza.
- **Il documento narrativo senza dipendenze a runtime**: SVG disegnati a mano,
  dati incorporati, nessuna `fetch()`. Costa più codice e in cambio la pagina
  si apre da disco e non invecchia. Il costo va dichiarato: è l'unico pezzo del
  progetto **senza test automatici**, e si verifica a mano in un browser.

---

## Riferimenti interni

| Documento | Cosa contiene |
|---|---|
| [`FONTI.md`](FONTI.md) | Registro delle fonti con stato di accesso verificato; note tecniche SDMX e ricette collaudate |
| [`METODOLOGIA.md`](METODOLOGIA.md) | Le quindici decisioni metodologiche per esteso |
| [`BRIEF.md`](BRIEF.md) | La domanda, gli assi, le storie candidate |
| [`PROSSIMI-PASSI.md`](PROSSIMI-PASSI.md) | Consegna: cosa resta da scaricare, decisioni aperte, come si costruiscono analisi e sito |
| [`pipeline/`](pipeline/README.md) | Il codice, con le trappole documentate |
| [`dati/`](dati/README.md) | Le trenta tabelle prodotte |
| [`analysis/`](analysis/README.md) | I quattordici script che leggono quelle tabelle, e le verifiche di `verifica_cifre.py` |

*Versione 1 — settembre 2026. La §7 riporta risultati veri con i loro controlli,
e di quelli elencati in §6.2 ne resta fuori uno solo: la rottura Covid trattata
in modo sistematico. Il confronto esterno sul turismo, che era l'altro, è la
§7.8. Resta provvisorio il titolo, che cambierà quando sarà chiara la tesi.*
