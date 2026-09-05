# Nota metodologica (MET-1…MET-21)

> **Cos'è.** Le decisioni che governano il progetto: *perché* misuriamo come
> misuriamo. È la base di credibilità — qualunque grafico, testo o titolo deve
> essere coerente con quanto scritto qui. Le regole nascono in parte dal
> progetto gemello su Donostia, in parte dai problemi specifici incontrati sui
> dati bresciani.
>
> ## ⚠️ Bozza avanzata — non ancora definitiva
>
> **Aggiornata a settembre 2026, quando il quinto asse ha avuto la sua prima
> analisi.** Le ventuno regole qui elencate sono tutte reali e
> applicate; sei di esse (MET-9, MET-12, MET-13, MET-14, MET-15, MET-21) nascono da
> errori o incoerenze **effettivamente trovati sui dati bresciani**, non da
> principi scelti a tavolino.
>
> Ultima arrivata: **MET-21**, da una rilettura dei grafici: la linea del
> massimo e quella del minimo di un insieme sono **inviluppi**, non serie, e
> chiamarle «la più cara» e «la più economica» fa credere che raccontino il
> percorso di una zona. Nelle zone OMI del capoluogo quella in fondo cambia tre
> volte in ventidue annate. Prima: **MET-20**, dal deflatore: l'indice dei prezzi al consumo è
> pubblicato in tre basi che non si sovrappongono, e attaccarne i livelli
> disegna due crolli del 30 % mai avvenuti. Prima: **MET-19**, dalle quotazioni immobiliari OMI — negli affitti
> la base di misura passa da superficie netta a superficie lorda nel 2025, e la
> media della città «cala» di due decimi senza che il mercato si muova. Prima:
> **MET-17** e **MET-18**, entrambe nate
> dal confronto sul turismo fra le 107 province. La prima dallo scarto fra le
> due fonti che misurano lo stesso turismo bresciano — cresciuto dal 6,5 % al
> 10,6 % in cinque anni; la seconda da un +87,6 % in dodici mesi che sembrava un
> mercato e invece era un'etichetta. Prima: **MET-16**, la prima regola nata da
> un errore *evitato* invece che commesso — su una rete di sensori che apre e
> chiude stazioni, la media di quello che c'è misura anche il cambiamento della
> rete. Prima ancora, in agosto: **MET-9 non è più una questione aperta**
> (l'incrocio fra settore e classe dimensionale ha chiuso la domanda), e
> **MET-15** è nata subito dopo, quando la stessa disciplina applicata alla
> popolazione ha ribaltato la parola su cui poggiava la prima storia del sito.
>
> Cosa manca ancora: le regole su **come si scelgono e si raccontano le
> storie** — soglie, criteri di inclusione, casi limite. Sei storie sono
> state scritte, che è abbastanza per intuirle e troppo poco per fissarle. Nel
> progetto Donostia sono arrivate dalle revisioni esterne, cioè dopo la
> pubblicazione.

---

## MET-1 — Unità locale non è impresa

Il registro ASIA conta **unità locali**: lo stabilimento, l'ufficio, il
cantiere. Una società con sede a Milano e un capannone a Lumezzane produce una
unità locale a Lumezzane; un gruppo con dieci filiali produce dieci unità
locali. Quindi:

- **mai scrivere «imprese» dove il dato dice «unità locali»**, e mai contare le
  unità locali come se fossero aziende distinte;
- la **classe dimensionale è dell'unità locale, non del gruppo**: uno
  stabilimento da 300 addetti di una multinazionale e una fabbrica indipendente
  da 300 addetti sono indistinguibili nel dato;
- gli **addetti sono medie annue**, quindi hanno decimali e non vanno
  presentati come teste;
- una riorganizzazione societaria che sposta la sede legale di un'unità
  cambia i numeri **senza che sia cambiato nulla nel mondo reale**. È la
  causa più probabile di variazioni brusche e isolate.

## MET-2 — Il soggetto è la provincia; i livelli si dichiarano sempre

**Decisione presa (agosto 2026): il soggetto è la provincia**, raccontata
attraverso i suoi 205 comuni; il capoluogo è un caso privilegiato con due
approfondimenti dedicati, non il protagonista.

I tre livelli — 205 comuni, provincia (`ITC47`), comune di Brescia (`017029`)
— non sono intercambiabili e la scelta non è mai neutra: il capoluogo pesa il
21 % dell'occupazione provinciale e il 16 % della popolazione, quindi
«Brescia» e «il bresciano» danno risposte diverse alla stessa domanda.

**Il capoluogo va trattato come outlier dichiarato.** Con 199.853 abitanti
contro una mediana comunale di 3.671, in una coropletica satura la scala e in
una correlazione la guida: servono classi o scale robuste nelle mappe e il
leave-one-out nelle correlazioni (MET-5).

Regole operative:

- ogni grafico dichiara il livello nel titolo o nella legenda, non nelle note;
- **la coropletica è per ciò che è misurato sui 205 comuni**; ciò che esiste
  solo come aggregato provinciale diventa serie o scomposizione, mai mappa;
- quando città e provincia divergono, **la divergenza è il risultato**, non un
  fastidio da appianare.

## MET-3 — Un dato mancante non è uno zero

Le fonti dichiarano l'assenza in modi diversi: cella vuota, `Dato riservato`
(soppressione per riservatezza statistica), `-9999` (misura non valida ARPA).
Nessuno di questi è zero, e convertirli in zero produce mappe che mostrano
«nessun fenomeno» dove c'è «nessuna misura».

Nella pipeline il parser restituisce `None` su tutti i token di assenza e le
tabelle lasciano la cella vuota. Nell'interfaccia serve un **colore dedicato
al «nessun dato»**, distinto dal minimo della scala.

**Il caso limite trovato sul campo.** Nei flussi turistici 2024, per Gottolengo
tutte le righe di dettaglio sono `Dato riservato` ma la riga «Totale» dichiara
**0**: uno zero calcolato su celle soppresse. La pipeline lo marca
`zero_fittizio` in una colonna `stato` e lo esclude dalla tabella di sintesi.
Quarantacinque comuni su 178 hanno le presenze soppresse: su questo asse la
mappa è a buchi, e va detto.

## MET-4 — Schede di confidenza

Ogni indicatore porta il proprio livello di confidenza, visibile
nell'interfaccia e non relegato alle note:

| Livello | Significato | Esempi bresciani |
|---|---|---|
| `osservato` | misurato direttamente dalla fonte | popolazione residente, addetti ASIA, presenze turistiche |
| `derivato` | calcolato da altri indicatori osservati | addetti per 100 abitanti, quote per classe dimensionale |
| `proxy` | approssimazione di ciò che vorremmo misurare | prezzi di offerta immobiliare al posto delle transazioni; export regionale al posto del provinciale |

Accanto, l'elenco esplicito delle **assunzioni**. Un indicatore senza scheda
non entra nel sito.

## MET-5 — Correlazioni robuste, outlier dichiarati

Con 205 comuni si sta meglio che con i 19 barrios di Donostia, ma la
distribuzione è fortemente asimmetrica: **Brescia città è un ordine di
grandezza sopra tutto il resto** (199.853 abitanti contro una mediana comunale
di 3.671) e i comuni del Garda sono estremi su qualunque cosa tocchi il
turismo.

Quindi ogni correlazione pubblicata porta:

1. **Pearson e Spearman** insieme — se divergono molto, la relazione è guidata
   da pochi punti;
2. un **leave-one-out** su Brescia città e sui comuni gardesani;
3. la dichiarazione esplicita se il coefficiente crolla senza di loro.

## MET-6 — Fallacia ecologica

Tutte le correlazioni di questo progetto sono **fra comuni**, non fra persone.
Che i comuni con più addetti manifatturieri abbiano redditi mediani più alti
non dice nulla su quanto guadagni un singolo operaio. Dove la lettura
individuale è tentante — reddito e cittadinanza, istruzione e occupazione —
l'avvertenza va **nel testo del grafico**, non in fondo alla pagina.

## MET-7 — Stato, cambio e traiettoria sono tre cose diverse

- **Stato**: dov'è alto oggi (Brescia città concentra 100.939 addetti).
- **Cambio**: dove si muove di più (la provincia guadagna 29.421 addetti fra
  2018 e 2023, la città è ferma).
- **Traiettoria**: la forma del percorso (l'aria migliora dal 2000 ma il
  miglioramento rallenta).

Ogni frase deve dichiarare quale delle tre afferma. È l'errore più facile da
commettere e il più difficile da notare dopo.

## MET-8 — Finestre temporali disomogenee, mai appiattite

La profondità cambia radicalmente per asse: aria dal 1992, meteo dal 1990,
redditi dal 2012, ASIA 2018–2023, turismo 2019–2024, percezione di sicurezza
dal 2022. Tagliare tutto alla finestra più corta butterebbe via trent'anni di
serie ambientali; sovrapporre serie di lunghezza diversa senza dirlo suggerisce
confronti che non reggono.

Regola: **mostrare ogni asse con la profondità che ha**, e rendere visibile la
differenza (assi temporali allineati, estensione della serie dichiarata,
tratteggio o ombreggiatura sui tratti non confrontabili).

E **il 2020–2021 spezza quasi tutto**: la discontinuità Covid va testata
esplicitamente, non attraversata con una linea di tendenza.

### Testarla, però, richiede una base che non contenga già la risposta

`analysis/rottura_covid.py` la testa dove si può, e la prima cosa che dice è
**dove non si può**: il registro delle imprese comincia nel 2018, quindi prima
della pandemia ci sono due punti, e con due punti non esiste una tendenza da cui
misurare uno scostamento. Non è un preambolo, è il risultato.

Dove si può, il metodo è l'**attesa stagionale**: ogni mese si confronta con i
mesi omologhi precedenti. E qui c'è la trappola, che è la stessa di MET-12 in
un'altra forma — **una base lunga su una serie che ha una tendenza propria non
misura la rottura, misura la tendenza**:

| PM10, scarto del 2020 dall'attesa | |
|---|---|
| base 2000–2019 (venti anni) | −26 % |
| base 2017–2019 (tre anni) | **−9 %** |

Il PM10 scende da trent'anni per conto suo. Il primo numero attribuisce alla
pandemia due terzi di un miglioramento cominciato prima, e sarebbe un titolo
sbagliato in buona fede. Anche il secondo resta tendenza **più** rottura: questo
metodo non le separa, e dirlo è parte del risultato.

Il confronto fra le due serie mensili è per contro istruttivo: le presenze
turistiche perdono metà delle notti nel 2020 e superano il livello del 2019 già
nel 2022 — una rottura vera, netta e riassorbita — mentre sull'aria lo scarto
resta negativo cinque anni dopo, che è il segno di una tendenza in corso e non
di una rottura.

## MET-9 — Decomporre prima di titolare

> Questa regola nasce da un errore commesso in questo progetto, ed è la
> ragione per cui esiste il documento che state leggendo.

**Cosa era stato detto.** Dai totali ASIA risultava che nel comune di Brescia
gli addetti in unità locali con almeno 250 addetti fossero crollati da 20.111
a 13.775 fra 2018 e 2023 (dal 19,9 % al 13,6 %), mentre in provincia la stessa
classe teneva. Ne era stato tratto il titolo: *«l'assottigliamento del vertice
è un fenomeno urbano»*, con il sottinteso che la città stesse perdendo i suoi
grandi stabilimenti.

**Cosa dice la decomposizione per settore.** Scomponendo la stessa classe
dimensionale per divisione Ateco, la perdita è **quasi interamente in una sola
sezione**, la N — *attività amministrative e di supporto*:

| Divisione | 2018 | 2023 | Variazione |
|---|---|---|---|
| 78 · attività di ricerca e selezione del personale (somministrazione) | 6.418 | 2.251 | **−4.167** |
| 81 · servizi per edifici e paesaggio (pulizie, facility) | 3.123 | — | **−3.123** |
| 82 · supporto per le funzioni d'ufficio | 396 | 284 | −112 |
| 80 · vigilanza e investigazione | — | 522 | +522 |
| **Sezione N nel complesso** | **9.937** | **3.057** | **−6.880** |

E nel frattempo, nella stessa classe ≥250 addetti:

| | 2018 | 2023 | Variazione |
|---|---|---|---|
| Manifattura (sezione C) | 4.448 | 4.397 | **−51, sostanzialmente stabile** |
| Sanità e assistenza sociale (Q) | 1.597 | 2.163 | +567 |
| Trasporti e magazzinaggio (H) | 1.640 | 2.438 | +798 |
| **Totale ≥250** | **20.111** | **13.775** | −6.336 |

**La manifattura grande, in città, non si è mossa.** Ciò che è sparito è
l'occupazione registrata delle grandi agenzie di somministrazione e delle
imprese di servizi esternalizzati. E questo è precisamente il tipo di dato che
MET-1 avverte di non prendere alla lettera: i lavoratori somministrati sono
attribuiti all'unità locale dell'agenzia, non a quella dove lavorano davvero,
e una riorganizzazione societaria basta a spostarne migliaia.

### La questione aperta, chiusa (agosto 2026)

La domanda che restava era: *quegli addetti sono spariti o sono stati
riclassificati?* Non era rispondibile finché il dettaglio settoriale e quello
dimensionale vivevano in due tabelle separate. Con l'incrocio — quattro
richieste piccole, perché il territorio è fissato a un codice solo — la risposta
è netta, e si legge guardando **la stessa divisione a due scale diverse**
(`analysis/decomposizione_capoluogo.py`):

| Divisione 81 — servizi per edifici | Variazione 2018→2023 |
|---|---|
| classe ≥250 addetti, capoluogo | **−3.123** (la classe sparisce) |
| **tutte** le classi, capoluogo | −1.493 |
| unità locali del comune, tutte le classi | **+157** |
| tutte le classi, **provincia** | −536 su 12.699, cioè −4 % |

Le due unità locali grandi non hanno chiuso: si sono **sciolte in unità più
piccole**, e il comune ne conta 157 in più di prima. In provincia la divisione è
sostanzialmente ferma.

| Divisione 78 — somministrazione | Variazione 2018→2023 |
|---|---|
| classe ≥250 addetti, capoluogo | −4.167 |
| tutte le classi, capoluogo | −4.830 |
| tutte le classi, **provincia** | −882 su 17.782, cioè −5 % |

Qui il capoluogo perde davvero, ma la provincia quasi no: il lavoro non è
uscito dal bresciano, è uscito **dal capoluogo** — e per una fonte che attribuisce
i somministrati all'unità locale dell'agenzia, spostare una sede basta. La
rottura, per giunta, è tutta nel 2020 (8.686 → 4.393 in un anno), non una
discesa gradua: è il profilo di un cambio di registrazione, non di
un'erosione.

**Conclusione.** Il titolo *«la grande industria se ne va dalla città»* è falso
due volte: la manifattura grande non si è mossa (−51 addetti su 4.448), e le due
divisioni che fanno tutto il calo non hanno perso lavoro ma cambiato forma o
comune. Resta aperto solo il confronto con province comparabili — Bergamo è il
controllo naturale, e costa un filtro.

**La regola.** *Nessun titolo su una variazione aggregata prima di averla
scomposta per settore e verificata contro almeno una spiegazione
amministrativa alternativa.* Un aggregato che si muove molto e all'improvviso
è, fino a prova contraria, un cambiamento di come si conta.

## MET-10 — I ripieghi si dichiarano nel grafico

Dove la grana giusta non è accessibile si usa quella disponibile, **etichettata
come tale sull'oggetto grafico**, non in una nota metodologica che nessuno
apre:

- **commercio estero**: il dato provinciale non è raggiungibile via API, si usa
  la **Lombardia**. Brescia è la seconda provincia manifatturiera della
  regione: è un contesto onesto, non un sostituto;
- **reati**: solo provinciali. Non esiste il dato comunale per Brescia, che non
  rientra fra i dodici «grandi comuni» della serie ISTAT;
- **prezzi immobiliari**: prezzi di **offerta** (annunci), non di transazione,
  finché non si passa dall'OMI.

## MET-11 — L'origine non è un proxy di nulla

Il paese di cittadinanza o di nascita **non è** un indicatore di reddito, di
disagio, di trasformazione urbana o di pressione sui servizi. Le tabelle sulle
origini sono descrittive e il testo deve dirlo.

In più, il censimento permanente permette una distinzione che quasi tutte le
narrazioni pubbliche sbagliano: **stranieri residenti**, **stranieri nati in
Italia** (seconde generazioni) e **italiani per acquisizione** sono tre
popolazioni diverse. Confonderle in un unico «stranieri» è un errore di misura
prima ancora che di racconto.

## MET-12 — Per la convergenza serve il livello **iniziale**

> Anche questa nasce da un numero sbagliato, trovato ad agosto 2026 mentre si
> costruiva `analysis/livelli_e_variazioni.py`.

Per chiedersi se i comuni si stiano avvicinando o allontanando si correla la
**crescita** con il **livello di partenza**. Correlarla con il livello finale è
un artefatto e basta: il livello finale *contiene* la crescita, quindi chi è
cresciuto di più ci finisce sopra per costruzione.

Sul reddito bresciano i due calcoli non danno un numero un po' diverso: danno
**segni opposti**.

| Reddito medio per contribuente, 2012–2023 | Pearson | Spearman |
|---|---|---|
| livello **2012** contro crescita (il test vero) | **−0,45** | −0,47 |
| livello 2012, senza capoluogo e comuni turistici | **−0,53** | −0,51 |
| livello **2023** contro crescita (l'artefatto) | +0,12 | +0,07 |

C'è convergenza, ed è forte; il calcolo sbagliato la nasconde e suggerisce il
contrario. Il quadrante di una mappa può usare il livello finale — descrive il
presente, ed è quello che il lettore vuole vedere — ma **la correlazione no**.
Gli script del progetto stampano entrambi i numeri di proposito: quando
divergono, il primo è quello che risponde alla domanda.

Corollario, meno vistoso ma dello stesso tipo: se l'indicatore è un rapporto,
numeratore e denominatore vanno presi **allo stesso anno**. Gli addetti ogni 100
abitanti del 2023 sul 2018 misurano anche il movimento della popolazione.

## MET-13 — Una decisione sul dato mancante si prende in un posto solo

> Trovata dal verificatore, che è esattamente il motivo per cui esiste.

MET-3 dice che un dato mancante non è uno zero. Non dice *chi* lo decide, e
finché la decisione viene presa dentro ogni script capita quello che è capitato
qui: l'indice di Moran sulla specializzazione settoriale valeva **0,44** nel
sito e **0,46** negli script di analisi. Nessuno dei due calcoli era sbagliato:
il primo escludeva i comuni senza la riga della manifattura, il secondo li
faceva entrare con lo 0 %.

La decisione giusta è l'esclusione — ASIA non pubblica la cella quando è troppo
piccola, e «zero addetti nella manifattura» è un'affermazione diversa da «non lo
sappiamo» — ma il punto della regola non è quale delle due, è che **deve
esistere un posto solo dove è scritta**. Qui è `analysis/_tabelle.quote_sezioni()`,
con il perché accanto.

L'eccezione, deliberata: `analysis/verifica_cifre.py` riscrive la definizione
per conto suo. Un verificatore che importa il codice che verifica non verifica
niente — se la lettura fosse sbagliata, lo sarebbe da entrambe le parti e i
numeri tornerebbero lo stesso.

E quando un comune viene escluso, **va nominato**: nel sito i tre comuni senza
la riga della manifattura sono scritti per nome, con il loro peso, invece di
sparire dalla mappa in silenzio.

## MET-14 — Un numero senza termine di paragone non è un risultato

> L'ultima nata, e quella che ha corretto più affermazioni in una volta sola.

Per quasi tutto il progetto Brescia è stata misurata **contro sé stessa**. È il
modo in cui si scrivono quasi tutti i ritratti di territorio, ed è il modo in cui
si prende per caratteristica di un luogo quello che è la normalità di un paese.

La verifica costava poco — le fonti coprono l'Italia intera, e i file grezzi
nazionali erano già su disco — e il risultato è questo:

| Indicatore, 2023 | Brescia | mediana delle 107 province | rango |
|---|---|---|---|
| unità locali sotto i 10 addetti | 92,7 % | **94,4 %** | 101ª |
| addetti in unità sotto i 10 | 42,9 % | **51,0 %** | 85ª |
| addetti per unità locale | 4,01 | **3,44** | 21ª |
| addetti nella manifattura | 32,4 % | **20,7 %** | **15ª** |
| crescita degli addetti 2018–2023 | 1,27 %/anno | **1,43 %/anno** | 65ª |

**La frase che il progetto ripeteva dal primo giorno — «Brescia è un territorio
di microimprese» — è vera in assoluto e fuorviante come descrizione.** Il 92,7 %
descrive l'Italia; Brescia è fra le **meno** frammentate del paese, in un grumo
di province che sono i distretti industriali del nord (Vicenza, Treviso, Reggio
Emilia, Modena, Bergamo). Quello che la distingue davvero è il **settore**, non
la dimensione: 15ª d'Italia per quota manifatturiera. E la crescita, che
sull'aggregato provinciale sembrava notevole, è sotto la mediana.

Lo stesso controllo ha rafforzato MET-9 invece di indebolirla: nei 64 comuni
capoluogo con una classe grande significativa, quella classe si è svuotata in 44
casi, con una mediana del −11,9 %. Brescia (−31,5 %) è il 13º calo più forte. Un
movimento così diffuso non è una vicenda industriale che accade
contemporaneamente in quaranta città diverse: è, fino a prova contraria, un
cambiamento di come si conta.

Il terzo uso della stessa regola ha invece **confermato** un risultato e gli ha
tolto un aggettivo: la convergenza dei redditi comunali, che è il risultato più
netto delle analisi, rifatta identica sui 240 comuni di Bergamo dà −0,48 contro
il −0,45 di Brescia. Il risultato regge fuori da qui, il che lo rende più solido
e non più bresciano.

**La regola.** *Prima di dire che un valore caratterizza il territorio, guardare
quanto fa altrove.* Un confronto può correggere una frase (le microimprese),
rafforzarne un'altra (le grandi unità locali) o toglierle un aggettivo (la
convergenza): sono tre esiti diversi e tutti e tre utili. Dove il confronto non
c'è — dopo MET-15 resta solo il turismo — va **dichiarato**, e la frase va
scritta come «a Brescia succede questo», mai come «a Brescia, a differenza di
altrove, succede questo».

⏳ **Il quarto uso**, sulla popolazione, è arrivato con il bilancio demografico
(MET-15): fra le 107 province Brescia è la **6ª per crescita**, con una mediana
provinciale di −19,7 abitanti ogni mille. Anche qui il confronto cambia la
frase: la provincia non «tiene» nonostante la montagna che si svuota, sta fra le
poche che crescono in un paese in cui 86 province su 107 perdono abitanti.

---

## MET-15 — «Si svuota» non dice come, e la parola scelta contiene già una risposta

> Nata dalla prima storia del sito, e nello stesso modo di MET-9: un titolo dato
> prima di decomporre.

La prima storia del sito si intitola «Dove il bresciano si svuota» e dice il
vero: 93 comuni su 205 perdono abitanti fra il 2018 e il 2024, in una fascia
contigua di montagna. Ma **spopolamento** è una parola che porta con sé un
meccanismo — la gente se ne va — che quei numeri non contenevano: la variazione
di popolazione è *netta*, e una differenza fra due stock non distingue chi
muore da chi parte.

Scomposta con il bilancio demografico, la risposta è opposta a quella che la
parola suggerisce. Sommando i 93 comuni in calo:

| Componente, 2018–2024 | Persone |
|---|---|
| saldo naturale | **−10.163** |
| migrazione interna | **−66** |
| migrazione estera | +5.020 |
| aggiustamento statistico | −2.010 |

La migrazione interna, sommata su tutti i comuni che perdono abitanti, vale
**meno di settanta persone in sei anni**: non è piccola, è indistinguibile da
zero. Chi ci abita non se ne sta andando. In 81 di quei 93 comuni la componente
che tira più giù è il saldo naturale, in 12 la migrazione interna, in nessuno
quella estera.

Lo stesso vale un livello sopra: la provincia guadagna 11.465 abitanti, ma con
un saldo naturale di **−25.764**. Cresce perché ne arrivano 27.817 dall'estero;
senza quella componente perderebbe 16.352 abitanti. Il saldo naturale è negativo
in 189 comuni su 205 e — per MET-14 — in 106 province italiane su 107.

**La regola, in due parti.**

1. *Una variazione netta non è una spiegazione, e il titolo che le si dà non
   deve contenerne una.* Prima di scrivere «spopolamento», «fuga», «esodo»,
   «attrattività», decomporre — o dichiarare che non si è potuto, come questa
   storia faceva prima e come le altre voci della sezione dei limiti fanno
   ancora.
2. *Dentro la decomposizione, ciò che non è un fenomeno resta fuori.*
   L'**aggiustamento statistico** del bilancio demografico è la rettifica che
   riconcilia l'anagrafe con il censimento: vale −4.558 persone in provincia in
   sei anni, abbastanza da cambiare il segno di un comune piccolo. Sommarlo alle
   migrazioni farebbe dire al progetto che se ne sono andate persone che in
   anagrafe non c'erano più. Resta una colonna a sé in
   `bilancio_demografico_comuni.csv`, nel grafico e in questo documento.

**Cosa la rende verificabile e non un'opinione.** La scomposizione **chiude**:
popolazione iniziale più componenti più aggiustamento uguale popolazione
censita, comune per comune e anno per anno, allo zero. Non è un modello con un
residuo da interpretare, è la contabilità della fonte, e la pipeline si rifiuta
di scrivere le tabelle se un giorno smette di tornare
(`pipeline/datasets/bilancio.py`, `verifica_identita`).

**Cosa resta fuori anche adesso, e va detto.** Il bilancio conta chi entra e chi
esce da ogni comune, **non la coppia origine-destinazione**. «Chi lascia la Valle
Camonica scende in città» resta una frase che questi dati non sostengono, ed è
nella sezione dei limiti del sito.

---

## MET-16 — Quando la rete di misura cambia, la media misura la rete

> Nata dalla sesta storia, ed è la prima regola del progetto che non nasce da un
> errore commesso ma da uno **evitato guardando il disegno prima del risultato**.

Le centraline dell'aria e le stazioni meteorologiche non sono i 205 comuni: sono
un insieme che si muove. Sul PM10 la rete bresciana passa da due stazioni a sette
nell'arco della serie, e non sono le stesse due. Su questo genere di dato la
media annua «di quello che c'è» è una trappola pulita:

> **la media di un insieme che cambia misura anche il cambiamento
> dell'insieme.**

Se le stazioni che aprono stanno in posti più puliti — e tendenzialmente è così,
perché le prime nascono dove il problema era grosso — un miglioramento compare
anche se nessuna aria è migliorata. È lo stesso genere di artefatto di MET-12: il
disegno della misura che produce il risultato, invece dei dati.

**La regola, in due parti.**

1. *Sulle serie lunghe si confronta un **panel bilanciato**: solo le unità
   osservate in tutti gli anni della finestra.* Il prezzo è che ne restano poche
   — tre stazioni per il PM10, quattro per il biossido di azoto — e che la
   finestra si accorcia all'unità più giovane. In cambio la variazione risponde
   alla domanda che le è stata fatta. Il conto ingenuo va calcolato lo stesso e
   riportato accanto: la distanza fra i due dice quanto la rete ha contribuito al
   risultato. Qui esagera i cali di tre o quattro punti.
2. *Quando le unità non sono confrontabili fra loro, si confronta ciascuna con
   sé stessa: **anomalie**, non medie.* Le stazioni di temperatura di questa
   provincia stanno fra i 47 metri di Gambara e i 2.108 del Pantano d'Avio: la
   loro media aritmetica non descrive nessun luogo e **cambia quando una
   stazione di montagna apre o chiude** — la sola chiusura del Pantano
   «scalderebbe» la provincia di mezzo grado senza che sia successo niente. Ogni
   stazione si confronta quindi con la propria media 2004–2013, e si media lo
   scostamento. È la convenzione climatologica, e qui è anche l'unica che regge.

**Il controllo che rende credibile il risultato non è nel risultato.** Il
+1,10 °C fra le due finestre conta meno del fatto che salgano **tutte e otto** le
stazioni, dalla Bassa al ghiacciaio: un effetto che si ripete uguale in otto
posti diversi non lo fa un sensore tarato male. E accanto sta la pioggia, dalla
stessa rete e con lo stesso metodo, che **non dà segnale** — mediana +0,5 %,
sette stazioni in aumento e cinque in calo. Le due insieme valgono più di
ciascuna: una serie senza segnale, ottenuta con lo stesso procedimento, è la
prova che il procedimento non fabbrica segnali.

**Due soglie che sembrano dettagli e non lo sono.** Un anno vale se ha abbastanza
mesi osservati, e «abbastanza» dipende da cosa si aggrega: una **media** annua
tollera due mesi mancanti, un **totale** annuo no — un totale a cui manca un mese
non è un totale basso, è un totale di undici mesi. Scritta alla soglia sbagliata,
la verifica indipendente di `verifica_cifre.py` contava sette stazioni di
temperatura invece di otto: MET-13 in miniatura, trovata dalla terza
implementazione della stessa definizione. E gli anni in cui è presente meno di
metà del panel restano fuori dal grafico, perché le anomalie tolgono la quota ma
non la variabilità: negli anni Novanta di questa rete c'è letteralmente una
stazione sola, e la sua annata calda diventerebbe l'annata calda della provincia.

**Cosa questa regola non autorizza a dire.** Niente sulle cause. La meteorologia
governa la dispersione degli inquinanti quanto le emissioni, e separare le due
richiederebbe una normalizzazione meteorologica che medie mensili non
sostengono. Vale a maggior ragione per l'ozono, che non scende e che è un
inquinante secondario con una chimica sua: questo progetto misura **cosa hanno
respirato le centraline**, non perché.

---

## MET-17 — Due fonti sullo stesso fenomeno non si mescolano in una frase

> Nata dal confronto sul turismo, e da uno scarto che nessuno stava cercando.

Il turismo di questo progetto ha **due fonti**, e non per scelta: quella
comunale è di Regione Lombardia e si ferma al confine regionale, quindi il
confronto con le altre province si può fare solo con ISTAT. Sono due
rilevazioni dello stesso fenomeno sullo stesso territorio, e la cosa naturale
da aspettarsi è che diano lo stesso numero.

Non lo danno. Sulle presenze in provincia di Brescia la somma dei comuni sta
**sopra** il totale provinciale ISTAT, e la distanza **cresce**:

| anno | ISTAT, provincia | somma dei comuni, Regione Lombardia | scarto |
|---|---|---|---|
| 2019 | 9.725.552 | 10.357.751 | **+6,5 %** |
| 2021 | 7.928.464 | 8.491.772 | +7,1 % |
| 2023 | 10.639.360 | 11.658.687 | +9,6 % |
| 2024 | 11.068.441 | 12.246.854 | **+10,6 %** |

E lo scarto vero è più largo di così: la somma dei comuni **esclude** i comuni
con dato soppresso per riservatezza, che sono decine. Sugli arrivi la stessa
distanza è più contenuta (dal 2,0 % al 7,0 %) e cresce nello stesso modo: è
quindi un fenomeno delle **notti**, non del conteggio delle persone.

**Nessuna delle due è sbagliata.** Sono due filiere amministrative con due
perimetri di rilevazione, e la divergenza crescente somiglia molto a un diverso
trattamento dell'offerta ricettiva nata negli ultimi anni. Ma non serve avere
ragione su questo per sapere cosa fare:

> **una tabella, una fonte.** Il confronto fra province si fa tutto dentro
> `turismo_province.csv`, i comuni tutti dentro `turismo_comuni_annuale.csv`, e
> i due numeri non compaiono nella stessa frase senza che la frase lo dichiari.

**La regola non è «scegliere la fonte migliore».** È non fabbricare per
sbaglio il numero che nasce dal mescolarle: «il Garda vale il 60 % delle
presenze della provincia» calcolato con un numeratore regionale e un
denominatore ISTAT è sbagliato del 10 %, e sembra giusto. Lo stesso vale per
qualunque quota, tasso o classifica che prenda i due pezzi da tabelle diverse.

**Il controllo è un test, non una promessa.** Il test
`test_le_due_fonti_sul_turismo_bresciano_non_coincidono` fallisce sia se lo
scarto sparisce — allora questa
regola va riscritta — sia se esplode, che vorrebbe dire che una delle due
letture si è rotta. Una regola che dipende da un numero e non lo sorveglia
dura fino al prossimo aggiornamento della fonte.

---

## MET-18 — Uno scalino nella serie è una definizione finché non si dimostra il contrario

> Nata dallo stesso scarico, e per poco non è costata la storia intera.

Le presenze turistiche italiane crescono del **14,9 %** fra 2024 e 2025. È il
genere di numero che un titolo se lo prende da solo. Scomposto per tipologia di
esercizio, però, il numero si dissolve:

| tipologia, Italia | 2024 | 2025 | variazione |
|---|---|---|---|
| alberghiero | 283,9 mln | 288,2 mln | +1,5 % |
| campeggi e villaggi | 68,6 mln | 69,5 mln | +1,3 % |
| **alloggi in affitto** | 71,8 mln | 134,7 mln | **+87,6 %** |

Un mercato non raddoppia in dodici mesi mentre gli altri due si muovono di un
punto. La spiegazione è nell'etichetta della fonte, scritta per esteso e facile
da non leggere: *«dal 2025 comprende gli alloggi gestiti in forma
imprenditoriale **e non imprenditoriale**»*. Non è cresciuto il fenomeno, è
cresciuto il perimetro.

> **Uno scalino isolato in una serie lunga si tratta come un cambio di
> definizione, non come un evento, finché la fonte non dice il contrario.** La
> prova sta nella scomposizione: un evento vero si vede su più componenti, un
> cambio di perimetro su una sola.

È la stessa famiglia di MET-9 («decomporre prima di titolare») e di MET-16 («la
media di un insieme che cambia misura anche il cambiamento dell'insieme»): tre
volte su tre, il risultato veniva dal disegno della misura e non dai dati.

**La regola operativa: la marcatura sta nella tabella, non nel commento.** Le
righe interessate portano `stato = definizione_cambiata`, e sono esattamente
quelle in cui la voce entra — `alloggi in affitto`, `extra-alberghiero` che la
contiene, `totale`. Alberghiero e campeggi restano confrontabili e restano
marcati `osservato`. Gli script di analisi escludono per costruzione tutto ciò
che non è `osservato`, quindi la trappola non si può calpestare per
distrazione: bisogna decidere di volerla. È MET-3 applicata a un'altra specie
di dato che c'è ma non si può usare come sembra.

**Il 2025 non si butta.** Il dato è giusto, e nel 2026 avrà accanto un 2026 con
la stessa definizione: la serie ricomincia da lì. Quello che non si può fare è
metterlo nella stessa riga degli anni prima — e la stessa avvertenza vale per la
Sardegna prima del 2017, dove a cambiare non è la definizione ma il confine
(`stato = confine_cambiato`).

---


## MET-19 — L'unità di misura è una dimensione della tabella, non una nota

> Nata dal primo scarico che è entrato nel progetto senza passare da un URL: le
> quotazioni immobiliari OMI, settembre 2026.

Le quotazioni OMI danno, per ogni zona e tipologia, un intervallo di €/m² per la
vendita e uno per la locazione. Accanto a ciascuno c'è una colonna di un solo
carattere — `Sup_NL_compr`, `Sup_NL_loc` — che dice se quei €/m² sono su
superficie **lorda** o **netta**. È l'informazione più facile da non leggere di
tutta la fornitura, e in questa provincia cambia:

| affitti, provincia di Brescia | record su superficie netta | su superficie lorda |
|---|---|---|
| 2004–2023 | tutti, tranne una manciata | qualche unità |
| 2024 | 2.410 | 10 |
| **2025** | **0** | **2.415** |

La media della città passa da **7,6 €/m² al mese nel 2024** a **7,4 nel 2025**.
Chi legge solo la media vede un mercato degli affitti che si raffredda. Ma la
superficie lorda è più grande della netta, quindi **lo stesso affitto, diviso per
una superficie più grande, dà un €/m² più basso**: quel −0,2 è la misura che è
cambiata. Le compravendite, nello stesso file e negli stessi ventidue semestri,
sono sempre su superficie lorda: lì la serie regge.

> **Quando la fonte dichiara l'unità o la base di misura, quella dichiarazione
> diventa una colonna della tabella, e nessuna aggregazione media attraverso
> valori diversi di quella colonna.** Un salto che coincide con un cambio di
> base è il cambio di base, finché non si dimostra il contrario.

La seconda metà della regola è MET-18 applicata alle unità invece che ai
perimetri, e le due si sono presentate insieme: nello stesso scarico, i «depositi
commerciali» dei volumi di compravendita diventano «depositi commerciali **e
autorimesse**» nel 2017. Anche lì la tentazione è di trattarli come lo stesso
segmento con due nomi; anche lì sarebbe una serie che cambia contenuto a metà.

**La regola operativa: la base sta nella chiave, non nel commento.**
`quotazioni_comuni.csv` è aggregata per comune × semestre × tipologia × mercato
× `base_superficie`, e le righe lorda e netta non si sommano mai perché non
condividono la chiave; `compravendite_comuni.csv` tiene
`depositi_commerciali` e `depositi_commerciali_autorimesse` come **due
segmenti**. Non c'è una nota da ricordarsi: c'è una tabella in cui l'errore non
si può scrivere per distrazione. È lo stesso meccanismo di MET-18, dove la
marcatura sta nelle righe, e di MET-3, dove un dato che c'è ma non si può usare
come sembra viene qualificato invece di essere buttato.

**Perché non si «normalizza» e via.** Convertire netto in lordo chiede un
coefficiente di ragguaglio che varia per tipologia edilizia e che l'OMI non
pubblica per zona: inventarlo produrrebbe una serie continua e sbagliata al
posto di una serie spezzata e vera. Meglio due tratti dichiarati che uno finto.

---


## MET-20 — Un indice pubblicato in più basi non è una serie

> Nata dal deflatore, settembre 2026: la prima serie del progetto che la fonte
> pubblica **spezzata**, e che sembra intera.

Il progetto ha vissuto due mesi con una nota ripetuta in tre documenti: i redditi
sono in **euro correnti**, quindi parte della crescita è inflazione e non
sappiamo quanta. La nota era onesta e diventava insostenibile con le quotazioni
immobiliari, che partono dal **2004**: su ventun anni la differenza fra euro
correnti e costanti non è una sfumatura, è il segno del risultato.

Scaricato l'indice dei prezzi al consumo (NIC, medie annue), si scopre che
**non è una serie**: sono tre, in tre basi diverse, e nessuna coppia si
sovrappone in un anno.

| anni | base | valore agli estremi |
|---|---|---|
| 1996–2010 | 1995 = 100 | 2010 → 139,8 |
| 2011–2015 | 2010 = 100 | 2011 → 102,8 |
| 2016–2025 | 2015 = 100 | 2016 → 99,9 |

Messi in colonna e graficati, quei numeri mostrano **due crolli del 30 %** —
nel 2011 e nel 2016 — che non sono mai avvenuti. E la cosa pericolosa è che
questa serie supera ogni controllo che verrebbe da scrivere: gli anni ci sono
tutti, i valori sono positivi, l'indice cresce a tratti.

> **Quando una fonte pubblica lo stesso indice in più basi, il raccordo si fa
> con la variazione che la fonte stessa pubblica, non con i livelli.** Dentro
> una base valgono i livelli pubblicati; nell'anno in cui una base comincia
> vale la variazione annua. E la serie concatenata dichiara, riga per riga,
> quali anni sono stati riscalati.

`indice_prezzi.csv` esce così: `indice` in base 2015 = 100, `indice_fonte` con
il numero **come la fonte lo pubblica** — 139,8 nel 2010, 102,8 nel 2011 —
`base_fonte` con la base a cui quel numero appartiene, `stato` a `osservato` o
`concatenato`. Il livello della fonte sta nella tabella per una ragione precisa:
senza, il raccordo è un'affermazione da credere sulla parola; con, chiunque apra
il CSV lo può rifare e contestare. Il test che la tiene in piedi non guarda i livelli — guarda che
**ogni rapporto fra anni consecutivi riproduca la variazione dichiarata**,
giunzioni comprese: è l'unico controllo che la concatenazione ingenua non passa.

**Il prezzo del raccordo, dichiarato.** Le variazioni sono pubblicate con un
decimale, quindi ogni giunzione porta fino a ~0,05 % di arrotondamento. Su due
giunzioni in trent'anni è un decimo di punto contro il **+47,8 % di inflazione
cumulata fra il 2004 e il 2025**: non tocca nessuna conclusione, ed è scritto
qui perché una
precisione persa che nessuno dichiara è una precisione che qualcuno prima o poi
rivendica.

**L'assunzione che resta, e non si può togliere.** È l'indice **nazionale**.
Deflazionare i prezzi delle case bresciane con l'inflazione italiana assume che
le due coincidano; un indice provinciale dei prezzi al consumo esiste per alcuni
capoluoghi, non per tutta la serie e non per tutti i comuni. Quindi ogni cifra
in euro costanti di questo progetto è **`derivato`** e non `osservato` (MET-4),
e la frase che la accompagna dice con cosa è stata deflazionata.

---


## MET-21 — Un estremo ricalcolato ogni anno è un inviluppo, non una serie

> Nata rileggendo l'ottava storia, settembre 2026. Il conto era giusto, il
> grafico era giusto, e le tre parole sotto le linee dicevano un'altra cosa.

Il grafico delle zone OMI del capoluogo ha tre linee: la più cara, la mediana e
la più economica delle tredici zone del panel bilanciato. Massimo, mediana e
minimo sono ricalcolati **su ogni annata**, che è il modo giusto di mostrare la
forbice che si stringe. Ma le etichette erano al singolare, e al singolare una
linea si legge come il percorso di **una** zona.

Non lo è. In cima non cambia mai inquilino (`B3`, ventidue annate su ventidue);
in fondo se ne alternano **tre**: `E1` dal 2004 al 2009, `B4` dal 2010 al 2012,
di nuovo `E1` fino al 2024, `C3` nel 2025. Chi legge la linea di sotto come la
storia di un quartiere legge una cosa che non esiste, e il grafico non gliel'ha
mai detto.

È la stessa distinzione di MET-16, spostata di un passo. Là il panel bilanciato
serviva a fissare **quali** stazioni entrano nella media, perché «la media di
quelle che ci sono» misura anche quali ci sono. Qui il panel c'era già e faceva
il suo lavoro: tiene ferme quali zone si confrontano. Ma *quale* zona occupi un
estremo è una **seconda domanda**, che il panel non tocca, e che nessuno si era
posto.

> **Una linea costruita come massimo o minimo di un insieme va nominata per
> quello che è, e ogni suo punto deve poter dire da chi viene.** Se l'identità
> dell'estremo non cambia mai, il singolare è lecito e va comunque verificato;
> se cambia, va detto, e la conclusione va rifatta anche sull'altra lettura.

In pratica, sul sito: il suggerimento e la tabella-specchio portano accanto a
ogni punto il nome della zona che lo produce, un riquadro di controllo dice
quante zone passano dai due estremi, e la forbice è ricalcolata una seconda
volta **sulle due zone del primo anno seguite fino in fondo**. Le due letture
danno le stesse due cifre, da 2,21 a 1,97, quindi la frase «la forbice si
stringe» regge in entrambe, e le quattro cifre stanno in `verifica_cifre.py`
come tutte le altre.

**Il controllo è il punto, non l'esito.** Qui l'inviluppo e le zone fisse
coincidono, e sarebbe stato comodo scoprirlo e tacere. La regola esiste perché
la prossima volta possono non coincidere, e in quel caso il grafico va rifatto
e non solo rinominato.

---


## Invarianti tecniche

Fatte valere dai test della pipeline (`pipeline/tests/`):

1. ogni `codice_istat` usato in qualunque tabella esiste nell'anagrafica dei
   205 comuni — **nessuna riga persa in silenzio** nei join;
2. le classi dimensionali sommano al totale;
3. i codici comune sono stringhe a sei cifre con lo zero iniziale (`017029`),
   mai numeri;
4. nessuna tabella prodotta è vuota;
5. i valori soppressi restano vuoti e, se qualificati, portano il proprio
   `stato`;
6. ogni codice usato in un `metric_*.json` esiste nella geometria, ogni
   indicatore dichiarato `live` nel registro ha il suo file e viceversa, i
   periodi sono ordinati e senza duplicati, i conteggi non sono mai negativi e
   le chiavi dei valori esistono tutte fra i periodi — sono i cinque invarianti
   del contratto con il sito;
7. ogni indicatore non `osservato` dichiara almeno un'assunzione: un derivato
   che non le dichiara è un derivato che finge di essere una misura;
8. **la scomposizione demografica chiude** (MET-15): popolazione iniziale più
   componenti più aggiustamento uguale popolazione censita, comune per comune e
   anno per anno; e la popolazione censita del bilancio coincide con quella del
   censimento permanente, che è la condizione per poter scomporre una tabella
   con i flussi di un'altra senza inventare un residuo;
9. la somma dei comuni bresciani torna con l'aggregato provinciale che la fonte
   pubblica per conto suo — due aggregazioni della stessa fonte che si
   controllano a vicenda;
10. **due tabelle che raccontano la stessa cosa devono tornare**: la provincia
    di `imprese_province.csv` è la somma dei comuni di
    `imprese_classe_addetti.csv`; il turismo annuale è la somma dei dodici mesi
    dove i dodici mesi ci sono; `comuni_sintesi.csv` non riscrive un numero
    diverso da quello della tabella da cui viene. Sono controlli nati come
    verifiche fatte a mano in una revisione, e messi nei test perché una
    revisione che non lascia un test dietro di sé va rifatta da capo;
11. **la pioggia si somma e la temperatura si media**, e la colonna
    `aggregazione` lo dice: se un giorno la pioggia uscisse come media i totali
    annui crollerebbero di tre ordini di grandezza senza che niente fallisca;
12. **le due fonti sul turismo bresciano continuano a non coincidere**
    (MET-17), e il test fallisce in tutte e due le direzioni: se lo scarto
    sparisce la regola va riscritta, se esplode una delle due letture si è
    rotta. Accanto, il **2025 resta marcato** come definizione cambiata
    (MET-18): il test controlla che lo scalino del +87,6 % sia ancora lì, cioè
    che la fonte non abbia ricostruito la serie all'indietro rendendo inutile
    la marcatura;
13. **l'indice dei prezzi è una serie sola**: ogni rapporto fra anni
    consecutivi riproduce la variazione annua pubblicata dalla fonte,
    giunzioni fra basi comprese (MET-20). È il solo controllo che la
    concatenazione sbagliata non supera.

E due controlli che non sono test ma girano a ogni push
(`.github/workflows/verifica.yml`):

- `analysis/verifica_cifre.py` ricalcola dalle tabelle **ogni cifra citata**
  nei documenti e nel sito, e fallisce se una diverge;
- il sito si costruisce, e la costruzione fallisce se un segnaposto numerico
  resta senza valore. Nel racconto pubblicato **nessuna cifra è scritta a
  mano**: sono tutte segnaposto sostituiti in fase di build.

## Convenzioni di scrittura

- «unità locali», non «imprese» (MET-1);
- «addetti», non «occupati», quando la fonte è ASIA — gli **occupati** sono i
  residenti che lavorano, gli **addetti** sono i posti di lavoro localizzati, e
  a Brescia i secondi superano i primi di circa il 16 %;
- «provincia di Brescia» o «comune di Brescia», mai «Brescia» da solo quando il
  livello non è ovvio dal contesto;
- i numeri con separatore delle migliaia e senza decimali inutili; le medie
  annue degli addetti arrotondate all'unità nei testi, con il decimale
  conservato nei dati.
