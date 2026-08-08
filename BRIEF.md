# Brescia Dataviz — brief di progetto

## La domanda

**Come è cambiata Brescia negli ultimi anni?**

Non c'è una tesi a monte. È la differenza principale rispetto a
`donostia-dataviz`, che partiva da una domanda con un imputato già in scena
(«il turismo sta facendo salire i prezzi?») e ha passato mesi a dimostrare che
non poteva rispondere in modo causale. Qui la domanda è descrittiva e più
larga: prezzi delle case, quantità di case in affitto, sicurezza percepita e
reale, riqualificazione dei quartieri, clima, aria, popolazione. Il prodotto
non è una tesi ma un **ritratto della trasformazione**, quartiere per
quartiere, con le sue asimmetrie.

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

## Geometria di riferimento

**33 quartieri**, raggruppati in **5 zone** (Centro, Nord, Est, Sud, Ovest).
Chiave di join `quartiere_id` (slug stabile, minuscolo, senza accenti). Sotto,
disponibile e da sfruttare, la **sezione di censimento** ISTAT: la grana
sub-quartiere che in Donostia si è dovuta inventare a metà progetto qui c'è
dall'inizio.

Un solo join in ingestione, come nel progetto originale. Il pezzo che lo rende
rigoroso è l'**indirizzario comunale**, che lega indirizzo → sezione →
quartiere → zona: con quello l'aggregazione sezioni→quartieri è esatta, senza
quello è una sovrapposizione geometrica approssimata (da dichiarare come tale).

Dettagli e stato di accesso: [`FONTI.md`](FONTI.md) §1.

## Assi tematici

Ordinati per **qualità del dato disponibile**, non per interesse presunto. È
l'ordine in cui conviene costruire.

| # | Asse | Grana migliore | Profondità | Solidità |
|---|---|---|---|---|
| 1 | **Aria** — PM10, PM2.5, NO₂, ozono | 5 stazioni georeferenziate | dal 1992 | forte: API aperta, serie continue |
| 2 | **Clima** — temperatura, precipitazioni, giorni caldi | 2 stazioni | dal 1990 | forte |
| 3 | **Popolazione** — residenti, cittadinanza, età, istruzione | sezione di censimento → quartiere | 1991·2001·2011·2021 + PDF comunali annuali | forte sulla struttura, a fotografie |
| 4 | **Abitazioni** — stock, **affitto vs proprietà**, vuote, epoca | sezione di censimento → quartiere | 2011 → 2021 | forte come stock, muta sui prezzi |
| 5 | **Reddito** | comune + CAP | serie annuale fino a imposta 2024 | media: i CAP non sono i quartieri |
| 6 | **Prezzi della casa** | zona OMI / zona urbana | semestrale dal 2004 (OMI), mensile recente (offerta) | media: due geometrie estranee ai quartieri, una dietro login, una proxy |
| 7 | **Riqualificazione** — PNRR, opere, PGT | progetto georeferenziato | 2021→ | media: dato buono, finestra corta |
| 8 | **Turismo** — arrivi, presenze, ricettività | comune | 2019–2024 (+ 2005–2013 comunale) | media: buco 2014–2018 |
| 9 | **Sicurezza** — reati e percezione | **comune / provincia** | serie storica | **debole a grana urbana: nessun dato per quartiere** |
| 10 | **Rumore** | isofone dell'agglomerato | 2022 | da recuperare i layer, non solo il PDF |

## Storie candidate

Ipotesi di narrazione, da confermare o smentire con i dati. Nessuna è una tesi
da difendere.

1. **L'aria che si è ripulita (o no).** Trent'anni di PM10 e NO₂ su cinque
   punti della città. È la serie più lunga e più leggibile del progetto, e
   probabilmente la storia con il finale meno scontato: i limiti europei
   restano superati anche dopo un miglioramento reale.
2. **La città che si scalda.** Warming stripes su Brescia dal 1995, giorni
   ≥30 °C, e — se il calcolo Landsat si replica — l'isola di calore per
   quartiere. In pianura padana il contrasto centro/periferia verde è più
   marcato che sulla costa.
3. **Chi abita Brescia.** Cittadinanza, età, istruzione per quartiere, con le
   due fotografie censuarie 2011 → 2021. Il decennio in cui la città è
   cambiata demograficamente, quartiere per quartiere.
4. **Affittare o possedere.** Il titolo di godimento delle abitazioni per
   sezione di censimento: dove si è ampliato l'affitto, dove le case vuote,
   dove lo stock più vecchio. È la risposta più solida disponibile alla
   domanda «quante case in affitto», e non passa per i prezzi.
5. **Quanto costa, e dove.** Prezzi OMI per zona, incrociati con il reddito
   per CAP. Da costruire con il crosswalk dichiarato e senza pretendere una
   coropletica per quartiere che i dati non sostengono.
6. **I quartieri che vengono rifatti.** PNRR, opere pubbliche, tram, San Polo.
   Cartografia dei progetti con importi, sovrapposta agli assi socio-demografici:
   dove si investe rispetto a dove il disagio è misurato.
7. **Paura e reati.** Serie di città e provincia, percezione a grana
   provinciale. È la storia che va raccontata **come serie temporale, non come
   mappa** — e il perché va spiegato al lettore, non nascosto.
8. **2023, l'anno della Capitale della cultura.** Uno shock datato e
   identificabile nelle serie turistiche: si vede? è rimasto?

## Principi (ereditati, e uno in più)

Dal progetto Donostia, senza modifiche:

- **Una sola geometria di riferimento** e un solo join in ingestione.
- **Provenance esplicita**: ogni valore porta la sua fonte.
- **Onestà metodologica**: correlazione ≠ causalità; una scheda di confidenza
  per metrica (`observed` / `derived` / `proxy`) con le assunzioni a vista.
- **Riproducibilità**: ogni numero citato ha uno script o una metrica dietro.

Uno in più, che nasce da questa ricognizione:

- **La grana disponibile detta la forma del grafico.** Se un dato esiste solo a
  livello di città o di provincia, non diventa una mappa. Se una serie copre
  sei anni, non si disegna accanto a una trentennale sullo stesso asse senza
  dirlo. Le mappe coropletiche sono per ciò che è misurato per quartiere — e
  su alcuni assi (sicurezza in testa) non lo è.

## Stato

Ricognizione delle fonti: **fatta** ([`FONTI.md`](FONTI.md)).
Nessun dato scaricato, nessuna pipeline, nessun codice. I passi successivi
naturali, in ordine:

1. Recuperare da una macchina con accesso normale i tre pezzi che stanno dietro
   `dati.comune.brescia.it`: indirizzario con crosswalk, popolazione per
   quartiere, turismo 2005–2013.
2. Validare i confini OSM dei 33 quartieri contro il dato comunale ufficiale.
3. Registrarsi all'area riservata dell'Agenzia delle Entrate per quotazioni,
   perimetri zone OMI e compravendite NTN.
4. Costruire l'aggregazione sezioni di censimento → quartieri, che è il
   fondamento degli assi 3 e 4.
