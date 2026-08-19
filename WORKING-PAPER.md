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
> ## ⚠️ Bozza — versione 1, agosto 2026
>
> **Riscritta dopo il primo giro di analisi e la pubblicazione di quattro
> storie.** La §7 non contiene più solo ciò che era emerso costruendo la
> pipeline: contiene risultati veri, con i loro controlli. La §6.1, che era il
> pezzo più solido del documento, ha ora la sua conclusione invece della sua
> domanda.
>
> Cosa resta provvisorio: il **titolo**, che cambierà quando sarà chiara la
> tesi; la §5, da rivedere se si aggiungeranno indicatori; e soprattutto
> l'assenza di un **confronto esterno**. Tutti i risultati qui sotto descrivono
> Brescia senza dire se Brescia sia diversa da una provincia qualunque: la
> convergenza dei redditi in particolare potrebbe essere un fatto italiano e
> non bresciano, e finché non c'è almeno Bergamo non si può sapere. È il limite
> più serio di questa versione ed è dichiarato in §8.

---

## Sintesi

Il progetto costruisce un ritratto quantitativo di Brescia — il comune, la
provincia e i suoi 205 comuni — a partire da fonti esclusivamente aperte:
ISTAT (censimento permanente, registro ASIA delle unità locali, criminalità,
forze di lavoro, commercio estero), MEF (dichiarazioni dei redditi per classi
di importo), ARPA Lombardia (qualità dell'aria dal 1992 e clima dal 1990),
Regione Lombardia (flussi turistici). Ventuno tabelle tidy, tutte ricostruibili
con `requests` e la libreria standard di Python, senza chiavi API — e da lì un
sito statico autocontenuto, costruito senza alcuna dipendenza a runtime.

Il problema metodologico centrale **non** è l'N piccolo — 205 comuni sono
abbastanza — ma tre altre cose: la **eterogeneità delle grane** (alcuni assi si
fermano alla provincia, altri arrivano al comune, nessuno scende sotto), la
**disomogeneità delle finestre temporali** (da trentaquattro anni a tre), e
soprattutto la **fragilità semantica degli aggregati amministrativi**, che
cambiano per ragioni contabili senza che cambi nulla nel mondo.

I risultati metodologicamente più utili sono **quattro errori corretti**, tutti
trovati sui dati e non previsti a tavolino.

1. **§6.1 — decomporre prima di titolare.** Una variazione aggregata
   spettacolare — il crollo dell'occupazione nelle grandi unità locali del
   capoluogo — si è dissolta appena scomposta per settore, e poi ancora appena
   guardata a due scale territoriali: la manifattura grande non si era mossa, e
   le due divisioni di servizi che facevano tutto il calo non avevano perso
   lavoro ma cambiato forma societaria o comune di registrazione.
2. **§4 — per la convergenza serve il livello iniziale.** Correlare la crescita
   con il livello finale è un artefatto, perché il livello finale contiene la
   crescita. Sul reddito bresciano i due calcoli danno **segni opposti**: la
   convergenza esiste ed è forte, e il calcolo sbagliato la nasconde.
3. **§4 — una decisione sul dato mancante si prende in un posto solo.** Due
   parti del progetto rispondevano numeri diversi alla stessa domanda, non per
   un errore di calcolo ma perché ciascuna aveva deciso per conto suo cosa fare
   di una cella che la fonte non pubblica. L'ha trovato lo script che ricalcola
   ogni cifra citata, che è precisamente il motivo per cui esiste.
4. **§7.1 — un numero senza termine di paragone non è un risultato.** La frase
   che il progetto ripeteva dal primo giorno — «Brescia è un territorio di
   microimprese» — è vera in assoluto e fuorviante come descrizione: la
   provincia italiana mediana è **più** frammentata di Brescia, non meno.
   Misurare un territorio solo contro sé stesso fa scambiare la normalità di un
   paese per la caratteristica di un luogo.

Nessuno dei quattro è un errore di programmazione: sono quattro modi diversi di
far dire a un dato corretto una cosa falsa.

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
  Fatto, ed è il controllo che ha cambiato di più il testo: la §7.1 diceva il
  contrario prima di averlo. Da estendere a redditi, popolazione e turismo, che
  richiedono un download in più ciascuno.
- **Rottura Covid**, testata in modo sistematico. Oggi è dichiarata (MET-8) e
  mostrata su un caso solo — la serie della classe ≥250 del capoluogo, dove la
  discontinuità del 2020 è visibile a occhio.
- **Decomposizione demografica**: quanta parte della variazione di popolazione
  viene da saldo naturale, migrazione interna, migrazione estera. È la prima
  voce della sezione «cosa non possiamo dire» del sito pubblicato, ed è l'unica
  di quella lista che si tolga scaricando una tabella.

## 7. Risultati

Quattro risultati, con i loro controlli. Nessuno è causale: sono descrizioni di
un territorio, e la §8 dice cosa non permettono di affermare.

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
rassicurante. Ma **convergenza non è uguaglianza**: nel 2023 il comune più ricco
dichiara 2,51 volte il più povero, e nel 2012 erano 2,17. La distanza si è
ridotta di poco e resta grande.

Tre avvertenze che il testo pubblicato ripete e che vanno ripetute anche qui:
sono **euro correnti** (nessun deflatore è entrato nel progetto, quindi parte
della crescita è inflazione — il che però non tocca la *correlazione*, perché
l'inflazione è comune a tutti i comuni); sono **contribuenti**, non residenti; e
sono **redditi dichiarati**, che non sono ricchezza.

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
  montagna (Magasa −2,9 % l'anno), e non sono sparse: Moran 0,34.
- **La provincia è turistica, il capoluogo no.** 12.246.854 presenze nel 2024,
  di cui il 68,8 % nei primi dieci comuni, otto sul Garda. Sirmione da sola
  (1.406.590) supera Brescia città (883.531, il 7,2 %).
- **L'aria è migliorata, e non abbastanza.** PM10 a Brescia Broletto: 45,5 µg/m³
  nel 2001, 27,3 nel 2024. Circa −40 %, e comunque sopra la linea guida
  dell'Organizzazione mondiale della sanità.
- **La città importa lavoro**: addetti localizzati su occupati residenti ≈ 1,16;
  26.425 residenti escono ogni giorno dal comune, 23.699 per lavoro (2019).

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
- **Il termine di paragone c'è solo sulle imprese.** Il confronto con le 107
  province (§7.1) e con i capoluoghi (§7.2) è stato fatto sul registro ASIA, ed
  è servito: ha corretto la §7.1 e rafforzato la §7.2. Ma **sulla convergenza
  dei redditi, sullo spopolamento e sul turismo non esiste**, e quelle tre
  sezioni restano misurate contro sé stesse. La convergenza in particolare
  potrebbe essere un fatto italiano prima che bresciano: finché non lo si
  verifica, la §7.3 va letta come «a Brescia succede questo», mai come «a
  Brescia, a differenza di altrove, succede questo». Estenderla costa un
  download dei redditi per almeno una seconda provincia.
- **La variazione di popolazione è netta**: non distingue saldo naturale da
  migrazione, quindi «spopolamento montano» qui è una descrizione e non una
  spiegazione.
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
