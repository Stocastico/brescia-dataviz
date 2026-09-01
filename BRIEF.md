# Brescia Dataviz — brief di progetto

## La domanda

**Come è cambiato il bresciano negli ultimi anni?**

Non c'è una tesi a monte. È la differenza principale rispetto a
`donostia-dataviz`, che partiva da una domanda con un imputato già in scena
(«il turismo sta facendo salire i prezzi?») e ha passato mesi a dimostrare che
non poteva rispondere in modo causale. Qui la domanda è descrittiva: **lavoro e
struttura produttiva**, chi ci vive e da dove viene, redditi, aria e clima. Il
prodotto non è una tesi ma un **ritratto del territorio**, comune per comune,
con le sue asimmetrie.

Sotto, una domanda di fondo che il disegno dei dati privilegia esplicitamente:
**è ancora la terra della meccanica fatta di piccole aziende, o si è
concentrata?**

Il soggetto è la **provincia**, non il capoluogo. Brescia città è un caso
privilegiato — ha due approfondimenti dedicati — ma non è il protagonista: la
provincia è molto più eterogenea e molto più interessante, e quasi tutte le
fonti buone la coprono per intero.

Questo cambia quattro cose nel modo di costruirlo:

1. **Nessun indicatore va costruito per dimostrare qualcosa.** Nel progetto
   basco l'Indice di Trasformazione Urbana serviva a dare corpo a un'ipotesi.
   Qui gli indici composti sono, se mai, un punto di arrivo: prima le
   dimensioni singole, ognuna leggibile da sola.
2. **La copertura temporale disomogenea diventa un tema, non un difetto.**
   L'aria ha trent'anni di serie, il censimento due fotografie, il turismo sei
   anni. Un progetto senza tesi può permettersi di mostrare gli assi con la
   profondità che hanno, invece di tagliarli tutti alla finestra più corta.
3. **La pianura padana ha un asse che la costa basca non aveva**: l'aria.
   Trent'anni di serie e un significato immediato per chi ci vive. Merita un
   posto di primo piano, non un capitolo ambientale di cortesia.
4. **La mappa è dei 205 comuni.** Il territorio provinciale — Garda, Val
   Trompia, Franciacorta, Bassa, Valle Camonica — è abbastanza eterogeneo da
   rendere la coropletica informativa invece che decorativa. E i limiti che
   pesavano nella prima impostazione si sciolgono: reati, forze di lavoro ed
   export sono provinciali, che ora è la grana giusta invece che un ripiego.

## Unità di analisi — decisa

**Il soggetto è la provincia di Brescia**, raccontata attraverso i suoi **205
comuni**. Il capoluogo è un **caso privilegiato**: ha una o due analisi tutte
sue, ma non è il protagonista.

| Livello | Ruolo |
|---|---|
| **205 comuni** (`017001`…`017206`) | L'unità di default di ogni mappa e ogni classifica. È qui che il territorio mostra la propria eterogeneità. |
| **Provincia** (`ITC47`) | Il riferimento: totali, medie e tutto ciò che a grana comunale non esiste (reati, forze di lavoro, commercio estero). |
| **Comune di Brescia** (`017029`) | Un comune fra i 205, più due approfondimenti dedicati (vedi sotto). |

> ⚠️ Il capoluogo è **un ordine di grandezza sopra tutti gli altri**: 199.853
> abitanti contro una mediana comunale di 3.671, e da solo il 21 %
> dell'occupazione provinciale. In una coropletica satura la scala; in una
> correlazione la guida. Va trattato come outlier dichiarato — leave-one-out
> nelle correlazioni (MET-5), scale robuste o classi nelle mappe.

### Le due analisi dedicate al capoluogo

1. **Il vertice che si assottiglia, e perché non è quel che sembra** — la
   decomposizione del crollo delle grandi unità locali, che è un fenomeno
   esclusivamente urbano e un caso di scuola metodologico
   ([`WORKING-PAPER.md`](WORKING-PAPER.md) §6.1).
2. **Brescia importa lavoro** — rapporto di concentrazione (~1,16 addetti
   localizzati per occupato residente), pendolarismo in uscita (26.425
   residenti al giorno) e composizione settoriale degli occupati residenti
   (2021: solo il 22,8 % nell'industria in senso lato). È l'unico punto in cui
   la grana censuaria comunale dice qualcosa che i 205 comuni non dicono.

Chiave di join: il **codice ISTAT del comune** a sei cifre, che è già la chiave
nativa di quasi ogni fonte italiana — nessun crosswalk da inventare, a
differenza del `barrio_id` di Donostia.

I 33 quartieri del capoluogo restano documentati in [`FONTI.md`](FONTI.md) §1
ma **fuori dal progetto**: con il soggetto provinciale non hanno più un ruolo.

Dettagli e stato di accesso: [`FONTI.md`](FONTI.md) §1 e §1-bis.

## Assi tematici — scelti

**Quattro assi portanti**, scelti su qualità del dato *e* coerenza con il
soggetto provinciale. Gli altri restano materiale di contorno: entrano se un
asse portante li richiama, non per completezza. La regola di arresto vale
soprattutto qui — tre o quattro assi ben fatti valgono più di tredici
abbozzati.

### I quattro portanti

| | Asse | Perché questo | Forma prevalente | Cosa manca |
|---|---|---|---|---|
| **1** | **Il lavoro e le imprese** — unità locali per classe di addetti e settore | È la domanda che ha originato il progetto, ed è l'unico asse con dati completi su tutti i 205 comuni e sei anni. La struttura dimensionale è stabile (micro-unità al 92,7 %) e la crescita sta nella fascia intermedia: il fenomeno da spiegare c'è. | coropletica sui comuni + serie per classe | niente: già scaricato |
| **2** | **Chi vive nel bresciano** — popolazione, origini, istruzione, redditi | Completamente mappabile, serie annuale, e la distinzione fra stranieri, seconde generazioni e italiani per acquisizione è materiale che nessuno racconta bene. Il reddito per classi di importo permette di parlare di disuguaglianza, non solo di livello. | coropletica + composizioni | il background migratorio (un download) |
| **3** | **Le due economie: manifattura e Garda** | È *la* storia della provincia: 12,2 milioni di presenze concentrate al 68,8 % in dieci comuni, otto sul lago, mentre la manifattura sta a ovest e a nord. Due economie che si toccano poco, sullo stesso territorio. Nasce dall'incrocio di dati già scaricati. | mappa bivariata, indici di concentrazione | niente |
| **4** | **L'aria e il clima** | Profondità che nessun altro asse ha: PM10 dal 2000, NO₂ dal 1992, temperature dal 1990. In pianura padana è l'asse con il significato più immediato per chi ci vive. | ⚠️ **non una coropletica** | ✅ niente, ed è diventato la **sesta storia** |

> **Nota sull'asse 4.** In tutta la provincia ci sono **sette comuni con
> sensori di qualità dell'aria attivi** — Brescia, Darfo Boario Terme, Odolo,
> Sarezzo, Rezzato, Lonato del Garda, Gambara — non 205. Non è però un limite
> quanto sembra: quei sette sono una **sezione territoriale quasi perfetta**
> (capoluogo, Valle Camonica, Val Trompia metalmeccanica ×2, cintura
> industriale, Garda, Bassa agricola). L'asse va costruito come **confronto fra
> tipi di territorio**, non come mappa. Il meteo invece ha 52 stazioni attive e
> regge una copertura spaziale vera.
>
> ✅ **Fatto** (settembre 2026), e la forma che ha preso non è nessuna delle due
> previste qui. Il confronto fra tipi di territorio non regge: le stazioni con
> una serie lunga abbastanza da confrontare sono troppo poche perché «la Val
> Trompia» sia una stazione sola, e un tipo di territorio rappresentato da un
> sensore non è un tipo di territorio. L'asse è diventato un confronto **fra
> inquinanti** (due crollano, l'ozono no) e **fra epoche** sulla temperatura, con
> le stazioni tenute insieme dalle anomalie invece che dalle medie. La lettura è
> `analysis/aria_e_clima.py`, la storia è la sesta del sito, e le due decisioni
> di metodo — panel bilanciato e anomalie — sono in MET-16.

### Di contorno

Sicurezza (due grane e due finestre, nessun dato sub-comunale) · casa e prezzi
(richiede il passaggio OMI) · commercio estero (solo regionale) ·
riqualificazione e PNRR (finestra corta) · istruzione e università (comune e
ateneo, fuori dalla grana provinciale) · rumore.

### Il quadro completo delle fonti

Ordinato per **qualità del dato disponibile**, indipendentemente dalla scelta
sopra.

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

1. **Il vertice che si assottiglia — o forse no.** La domanda diretta: Brescia
   è ancora la terra della meccanica fatta di piccole aziende? La struttura
   dimensionale dice di sì e non si muove: in provincia le unità locali sotto i
   dieci addetti restano il **92,7 %** del totale e occupano il **42,9 %** degli
   addetti, quasi identico al 2018. La crescita è tutta nella fascia intermedia
   (+23.840 addetti fra 10 e 249, cioè l'81 % dei +29.421 provinciali).

   Sui grandi, invece, c'è una trappola. I totali dicono che nel capoluogo gli
   addetti in unità locali con almeno 250 addetti crollano da 20.111 a 13.775
   mentre in provincia tengono — e sembra deindustrializzazione urbana. **Non lo
   è**: scomponendo per settore, la perdita è quasi tutta nella somministrazione
   di lavoro (−4.167) e nei servizi per edifici (−3.123), mentre la manifattura
   grande della città resta ferma (4.448 → 4.397). Il racconto vero è ancora da
   costruire, e passa dal capire se quel crollo sia un fenomeno del mercato del
   lavoro o un artefatto di come vengono attribuiti i lavoratori somministrati.
   Vedi [`WORKING-PAPER.md`](WORKING-PAPER.md) §6.1.

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

Ricognizione delle fonti: **fatta** ([`FONTI.md`](FONTI.md)). Pipeline in
piedi, tabelle scaricate e pulite, base geografica dei 205 comuni costruita
([`dati/`](dati/README.md)). I quattro assi portanti hanno tutti i dati che
servono; manca l'analisi, e manca il sito.

I passi successivi, in ordine, con il dettaglio in
[`PROSSIMI-PASSI.md`](PROSSIMI-PASSI.md):

1. **Le analisi dell'asse 1**, settore per settore: dove sono spariti i grandi
   stabilimenti urbani e se la meccanica si comporta diversamente dal resto.
   I dati ci sono già tutti (`imprese_settore.csv`), e la domanda è aperta da
   MET-9.
2. **Le altre analisi di `PROSSIMI-PASSI.md` §5**: velocità di cambio, livelli
   contro variazioni, tipologia di comuni, autocorrelazione spaziale, rottura
   Covid. La prima è scritta (`analysis/variazione_popolazione.py`).
3. **Scegliere le storie** fra le dodici candidate qui sopra — dopo aver visto
   i dati, non prima — e costruire il documento narrativo.
4. Quel che resta da scaricare richiede un passaggio manuale (OMI, atenei,
   open data del Comune, commercio estero provinciale): è tutto elencato in
   [`PROSSIMI-PASSI.md`](PROSSIMI-PASSI.md) §2, marcato come tale.
