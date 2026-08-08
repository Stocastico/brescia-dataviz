# Brescia Dataviz — brief di progetto

## La domanda

**Come è cambiata Brescia negli ultimi anni?**

Non c'è una tesi a monte. È la differenza principale rispetto a
`donostia-dataviz`, che partiva da una domanda con un imputato già in scena
(«il turismo sta facendo salire i prezzi?») e ha passato mesi a dimostrare che
non poteva rispondere in modo causale. Qui la domanda è descrittiva e più
larga: **lavoro e struttura produttiva**, chi vive in città e da dove viene,
studi e università, casa e affitti, sicurezza percepita e reale,
riqualificazione dei quartieri, clima e aria. Il prodotto non è una tesi ma un
**ritratto della trasformazione**, quartiere per quartiere dove i dati lo
consentono, con le sue asimmetrie.

Il baricentro è **economico e sociale, non turistico**. Brescia non è una città
turistica e il progetto non ci costruisce sopra: il turismo resta un capitolo
breve, utile soprattutto come contro-prova dello shock 2023 (Capitale italiana
della cultura). Al suo posto, al centro, c'è la domanda sulla città
industriale: una provincia storicamente di meccanica e di piccole aziende — è
ancora così, o si è concentrata?

Questo cambia tre cose nel modo di costruirlo:

1. **Nessun indicatore va costruito per dimostrare qualcosa.** Nel progetto
   basco l'Indice di Trasformazione Urbana serviva a dare corpo a un'ipotesi.
   Qui gli indici composti sono, se mai, un punto di arrivo: prima le
   dimensioni singole, ognuna leggibile da sola.
2. **La copertura temporale disomogenea diventa un tema, non un difetto.**
   L'aria ha trent'anni di serie, il censimento due fotografie, il turismo sei
   anni. Un progetto senza tesi può permettersi di mostrare gli assi con la
   profondità che hanno, invece di tagliarli tutti alla finestra più corta.
3. **La città padana ha un asse che la costa basca non aveva**: l'aria. È
   l'asse con il dato migliore *e* con il significato più immediato per chi ci
   vive. Merita un posto di primo piano, non un capitolo ambientale di
   cortesia.
4. **La mappa cambia soggetto, non sparisce.** Portare l'unità di analisi al
   comune e alla provincia non toglie la coropletica: la sposta sui **205
   comuni della provincia**, un territorio molto più eterogeneo della città —
   Garda, Val Trompia, Franciacorta, Bassa, Valle Camonica. E scioglie i limiti
   che pesavano prima: i reati sono provinciali, le forze di lavoro sono
   provinciali, l'export è provinciale. Erano ripieghi; ora sono la grana
   giusta.

## Unità di analisi

Tre livelli, in quest'ordine:

1. **Comune di Brescia** (`017029`) — l'unità principale. Quasi tutte le fonti
   buone arrivano qui.
2. **Provincia di Brescia** (`ITC47`) — l'aggregato, per ciò che a livello
   comunale non esiste (reati, forze di lavoro, export) e per ciò che è
   provinciale per natura (distretti industriali, turismo del Garda).
3. **I 205 comuni della provincia** — il dettaglio interno. Molte fonti li
   coprono tutti; dove il dato è rado, si tengono i maggiori.

Chiave di join: il **codice ISTAT del comune** a sei cifre, che è già la chiave
nativa di quasi ogni fonte italiana — nessun crosswalk da inventare, a
differenza del `barrio_id` di Donostia.

I 33 quartieri della città restano documentati e disponibili, ma **non sono
l'unità portante**: la grana sub-comunale si usa solo dove è davvero misurata
(censimento, abitazioni, origini) e solo se aggiunge qualcosa.

Dettagli e stato di accesso: [`FONTI.md`](FONTI.md) §1 e §1-bis.

## Assi tematici

Ordinati per **qualità del dato disponibile**, non per interesse presunto. È
l'ordine in cui conviene costruire.

| # | Asse | Grana disponibile | Profondità | Solidità |
|---|---|---|---|---|
| 1 | **Lavoro e imprese** — unità locali per classe di addetti e settore, occupati, pendolarismo | **205 comuni** + comune + provincia | 2018–2023 (ASIA), 2021 (censimento) | forte: risposta diretta alla domanda sulla struttura produttiva, e mappabile su tutta la provincia |
| 2 | **Aria** — PM10, PM2.5, NO₂, ozono | stazioni in tutta la provincia | dal 1992 | forte: API aperta, serie continue |
| 3 | **Popolazione e origini** — cittadinanza, seconde generazioni, italiani per acquisizione | **comune** (tutti) | 2018→ annuale; censimenti per sezione | forte, e più ricca di quanto sembrasse |
| 4 | **Istruzione** — titolo di studio per età e cittadinanza, università | comune; ateneo | 2018→; iscritti dal 1998/99 | forte |
| 5 | **Clima** — temperatura, precipitazioni, giorni caldi | stazioni | dal 1990 | forte |
| 6 | **Reddito** — livello e **distribuzione per classi** | **comune** (tutti) | serie annuale fino a imposta 2024 | forte a grana comunale; il dettaglio per CAP resta un extra |
| 7 | **Turismo** — arrivi, presenze per tipo di struttura e cittadinanza | **comuni della provincia** | 2019–2024 | forte *come storia provinciale*: il Garda contro tutto il resto |
| 8 | **Abitazioni** — stock, **affitto vs proprietà**, vuote, epoca | comune + sezione | 2011 → 2021 + censimento permanente | forte come stock, muta sui prezzi |
| 9 | **Sicurezza** — percezione (comune) e reati (provincia) | comune / provincia | percezione 2022–2024; reati 2006–2024, 56 tipologie | ora coerente con l'impostazione: due grane, due finestre |
| 10 | **Prezzi della casa** | zona OMI / comune | semestrale dal 2004 (OMI) | media: geometria propria, dietro login; il resto è offerta (proxy) |
| 11 | **Riqualificazione** — PNRR, opere, PGT | progetto georeferenziato | 2021→ | media: dato buono, finestra corta |
| 12 | **Commercio estero** — import/export per paese e merce | provincia | dal 1991 | **da verificare**, ma per una provincia manifatturiera sarebbe di prima grandezza |
| 13 | **Rumore** | isofone dell'agglomerato | 2022 | da recuperare i layer, non solo il PDF |

## Storie candidate

Ipotesi di narrazione, da confermare o smentire con i dati. Nessuna è una tesi
da difendere.

1. **Il vertice che si assottiglia — ma solo in città.** La domanda diretta:
   Brescia è ancora la terra della meccanica fatta di piccole aziende? I dati
   ASIA dicono di sì, e aggiungono una torsione. **In città** fra 2018 e 2023
   l'occupazione è ferma (~101 mila addetti) ma le unità locali con almeno 250
   addetti scendono da **35 a 28** e i loro addetti da 20.111 a 13.775 (dal
   19,9 % al 13,6 %). **In provincia** succede il contrario: +29.421 addetti
   (+6,5 %), la classe ≥250 tiene (75 → 82 unità) e le micro-unità restano
   stabilmente il 92,7 % del totale, con il 42,9 % degli addetti. Il peso delle
   grandi unità è la metà di quello urbano: 7,0 % contro 13,6 %.
   L'assottigliamento del vertice è quindi un fenomeno **del capoluogo**, non
   del territorio. Questa asimmetria è, per come stanno i numeri oggi, **la
   storia principale del progetto**.
2. **Dove lavora chi vive a Brescia.** Occupati per settore (2021: 86.788, di
   cui solo il 22,8 % nell'industria in senso lato) e per posizione nella
   professione. Una città che si racconta industriale e che nei numeri dei
   *residenti* è già in larga parte terziaria. Da incrociare con il rapporto di
   concentrazione del lavoro (~1,16: la città importa lavoratori) e con il
   pendolarismo (26.425 residenti escono ogni giorno dal comune).
3. **Chi abita Brescia, e da quanto.** La famiglia censuaria sul background
   migratorio permette di distinguere stranieri arrivati, **stranieri nati in
   Italia** e **italiani per acquisizione** — cioè di separare l'immigrazione
   dalla popolazione di origine straniera, che è la distinzione che quasi tutte
   le narrazioni pubbliche sbagliano. Con la cittadinanza per sezione di
   censimento si porta il quadro a grana di quartiere.
4. **Studiare a Brescia.** Titolo di studio per età e cittadinanza a livello
   comunale, più i due atenei (statale +29 % di iscritti dal 2000/01, e la
   sede della Cattolica). Quanti laureati vivono in città, in che settori
   lavorano, e se la città trattiene o esporta i suoi laureati.
5. **L'aria che si è ripulita (o no).** Trent'anni di PM10 e NO₂ su cinque
   punti della città. La serie più lunga del progetto, e probabilmente quella
   con il finale meno scontato: i limiti europei restano superati anche dopo un
   miglioramento reale.
6. **La città che si scalda.** Warming stripes dal 1995, giorni ≥30 °C, e — se
   il calcolo Landsat si replica — l'isola di calore per quartiere. In pianura
   padana il contrasto centro/periferia verde è più marcato che sulla costa.
7. **Affittare o possedere.** Il titolo di godimento delle abitazioni per
   sezione di censimento: dove si è ampliato l'affitto, dove le case vuote,
   dove lo stock più vecchio. La risposta più solida alla domanda «quante case
   in affitto», e non passa per i prezzi.
8. **Quanto costa, e quanto si guadagna.** Prezzi OMI per zona incrociati con
   il reddito per CAP e con la **distribuzione** del reddito per classi di
   importo — che consente di parlare di disuguaglianza, non solo di livello.
9. **I quartieri che vengono rifatti.** PNRR, opere pubbliche, tram, San Polo.
   Cartografia dei progetti con importi, sovrapposta agli assi
   socio-demografici: dove si investe rispetto a dove il disagio è misurato.
10. **Paura e reati.** Percezione a livello di città (2022–2024) contro reati a
    livello provinciale (2006–2024, 56 tipologie). Due grane e due finestre
    diverse: la storia va raccontata **come serie temporale, non come mappa**, e
    l'asimmetria va spiegata al lettore, non nascosta.
11. **Due province in una.** Il Garda contro il resto: nel 2024 la provincia fa
    12,2 milioni di presenze turistiche e i primi dieci comuni ne concentrano
    il 68,8 %, otto dei quali sul lago. Sirmione da sola (1,4 milioni) ne fa più
    di Brescia città (883 mila, il 7,2 % del totale). Un territorio con due
    economie che si toccano poco — manifattura a ovest e a nord, turismo a est —
    e una mappa che lo rende evidente al primo sguardo.
12. **La provincia che esporta.** Se il commercio estero provinciale si rivela
    accessibile (v. `FONTI.md`, asse 12), la serie dal 1991 per paese e merce è
    il modo più diretto di raccontare cosa produce davvero questo territorio, e
    verso chi.

## Principi (ereditati, e uno in più)

Dal progetto Donostia, senza modifiche:

- **Una sola geometria di riferimento** e un solo join in ingestione.
- **Provenance esplicita**: ogni valore porta la sua fonte.
- **Onestà metodologica**: correlazione ≠ causalità; una scheda di confidenza
  per metrica (`observed` / `derived` / `proxy`) con le assunzioni a vista.
- **Riproducibilità**: ogni numero citato ha uno script o una metrica dietro.

Uno in più, che nasce da questa ricognizione:

- **La grana disponibile detta la forma del grafico.** Le coropletiche sono per
  ciò che è misurato sui 205 comuni; ciò che esiste solo come aggregato
  provinciale diventa serie o scomposizione, non mappa. E una serie di sei anni
  non si disegna accanto a una trentennale sullo stesso asse senza dirlo.
- **Città e provincia si leggono insieme.** Il confronto fra le due è già, nei
  primi numeri, la cosa più informativa emersa: quasi ogni indicatore vale la
  pena di essere mostrato su entrambi i livelli, perché è nella differenza che
  sta la storia.

## Stato

Ricognizione delle fonti: **fatta** ([`FONTI.md`](FONTI.md)).
Nessun dato scaricato, nessuna pipeline, nessun codice. I passi successivi
naturali, in ordine:

1. Scaricare la serie ASIA completa (unità locali e addetti per classe
   dimensionale × Ateco 2 cifre, 2018–2023, 205 comuni) e sviluppare l'asse 1
   settore per settore: dove sono spariti i grandi stabilimenti urbani, e se la
   meccanica si comporta diversamente dal resto.
2. Montare la base geografica: confini comunali ISTAT generalizzati + elenco
   comuni, filtrati sui 205 della provincia. È mezz'ora di lavoro e sblocca
   ogni coropletica.
3. Verificare l'accesso al commercio estero provinciale (Coeweb o bulk
   `DF_BULK_COE*`): è l'unico asse importante ancora incerto.
4. Scaricare gli open data MUR sui due atenei (host non raggiungibile
   dall'ambiente di ricognizione).
5. Recuperare da una macchina con accesso normale i pezzi dietro
   `dati.comune.brescia.it`: turismo cittadino 2005–2013 e i materiali
   dell'Osservatorio migrazioni.
6. Registrarsi all'area riservata dell'Agenzia delle Entrate per quotazioni,
   perimetri zone OMI e compravendite NTN.
