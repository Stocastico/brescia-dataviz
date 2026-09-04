# OMI — provenienza degli archivi

**Fonte:** Agenzia delle Entrate, Osservatorio del Mercato Immobiliare, servizio
*Forniture dati OMI* — area riservata, `https://telematici.agenziaentrate.gov.it/Main/index.jsp`
(accesso SPID/CIE/CNS o Entratel/Fisconline).

**Scaricati da Stefano il 4 settembre 2026.** Sono l'unico dato del progetto che
un URL pubblico non restituisce: per questo gli archivi stanno **dentro** il
repository invece di essere rigenerabili dalla pipeline.

> **Citazione obbligatoria.** Qualunque uso di questi dati deve riportare la
> fonte «**Agenzia Entrate - OMI**». Vale per il sito, per i grafici e per
> `LICENSE-DATI`, non solo per questo file.

## Cosa c'è

| Cartella | Archivi | Copertura | Grana | Ambito della richiesta |
|---|---|---|---|---|
| `quotazioni/` | 22 zip, `QI_<anno>S<semestre>.zip` | **2° semestre di ogni anno, 2004→2025** | zona OMI | **solo provincia di Brescia** |
| `volumi/` | 15 zip, `VCN_<anno>.zip` | **2011→2025**, annuale | comune, per settore di mercato | **intero territorio nazionale** |

Dentro ogni archivio, i CSV come li manda l'Agenzia: separatore `;`, decimali
con la virgola, encoding latino, e — nelle quotazioni — una **prima riga di
didascalia** («Quotazioni Immobiliari : Valori di Mercato - Semestre 2004/2 -
elaborazione del 04-SET-26») prima dell'intestazione vera. Non è stato corretto
niente: la pipeline li legge così, con `zipfile` della libreria standard.

- `quotazioni/`: `QI_<id>_1_<semestre>_VALORI.csv` (min/max €/m² per tipologia,
  vendita e locazione) e `..._ZONE.csv` (descrizione e tipologia prevalente
  delle zone).
- `volumi/`: quattro CSV per anno — `LISTA-COM` (anagrafica dei comuni),
  `VALORI-COM` (NTN non residenziale: uffici, negozi, depositi),
  `VALORI-PER` (pertinenze: box, depositi) e `VALORI-RES` (residenziale per
  classe di superficie).

## Due cose contate all'arrivo, che vanno dichiarate

- **110.537 righe** di quotazioni sui 22 semestri, da 600 zone OMI nel 2004/2 a
  436 nel 2025/2. Le zone si accorpano: la serie non è a perimetro costante, e
  un confronto 2004→2025 per zona **non** è lecito senza dirlo. A grana comunale
  invece regge, perché il file porta già `Comune_ISTAT`.
- **205 comuni dal 2004 al 2015, 203 dal 2016.** Non è un errore di scarico e
  non è il nostro filtro: le 110.537 righe grezze finiscono tutte nelle tabelle
  prodotte. Sono due fatti sovrapposti — un comune soppresso, che la pipeline
  ricostruisce (vedi «Un comune che non esiste più»), e **Magasa** e
  **Valvestino**, che dal 2016 la fonte non copre più e che nelle compravendite
  non ci sono mai stati. Quei due sono i comuni passati da Trento a Brescia nel
  1934: la spiegazione probabile è il **sistema tavolare**, che l'OMI dichiara di
  escludere, ma la nota dell'Agenzia parla di province e non di questi due
  comuni — quindi è una spiegazione plausibile, non una verificata.

## Cosa ne è uscito, appena letti

Due cose che valgono più di qualunque commento sul formato.

**I prezzi di vendita del capoluogo sono nominalmente fermi da vent'anni.**
Abitazioni civili, media non pesata delle 23 zone, superficie lorda: **1.788
€/m² nel 2004**, punto più alto intorno al 2008–2013 (≈2.000), **1.829 nel
2025**. Ventuno anni per un +2,3 % nominale, cioè — a inflazione italiana di
quel periodo — un calo reale sostanzioso. Va detto con l'avvertenza che sono
quotazioni OMI, non transazioni: «indicazioni di valore di larga massima», come
scrive l'Agenzia stessa.

**I volumi, invece, si sono ripresi del tutto.** NTN residenziale del capoluogo:
**1.957 nel 2011**, fondo a **1.364 nel 2013**, poi risalita fino a **3.242 nel
2021** e **3.199 nel 2025**. Le case cambiano proprietario a un ritmo quasi
raddoppiato rispetto a quindici anni fa, mentre il prezzo al metro quadro è dove
era: è il paio di numeri più interessante di tutta la fornitura, e nessuna delle
due serie da sola lo dice.

**Negli affitti la base di misura cambia nel 2025, e non va letta come un
movimento di mercato.** Dal 2004 al 2024 le locazioni sono quotate su superficie
**netta**, nel 2025 su superficie **lorda** — l'intera provincia, non qualche
comune. La media di Brescia passa da 7,6 €/m² al mese (2024, netta) a 7,4 (2025,
lorda): siccome la lorda è la superficie più grande, lo stesso affitto dà un
€/m² più basso. È uno scalino di definizione, e nella tabella aggregata
`base_superficie` è una dimensione proprio per non poterlo confondere. Le
compravendite non hanno questo problema: superficie lorda in tutti e 22 i
semestri.

## I nomi sono stati normalizzati, e perché

Gli archivi arrivano chiamati `QI<numero-richiesta>_<CODICE FISCALE>.zip`: il
servizio ci mette dentro il codice fiscale di chi li ha richiesti. Questo
repository è pubblico, quindi i file sono stati rinominati con il periodo che
contengono (`QI_2004S2.zip`, `VCN_2011.zip`) — l'unica modifica fatta, e riguarda
il nome, non il contenuto. Il numero di richiesta resta visibile nei nomi dei
CSV interni, e quello non identifica nessuno.

È la sola eccezione alla regola «i file scaricati a mano si tengono col nome
originale» di [`SCARICHI-MANUALI.md`](../../SCARICHI-MANUALI.md): un dato
personale in chiaro in un repository pubblico batte la tracciabilità del nome.

## Un comune che non esiste più

`017154` **PRESTINE** compare in dodici semestri, dal 2004/2 al 2015/2, e poi
sparisce: dal 2016 il suo territorio è di **Bienno** (`017018`), che nello
stesso semestre passa da due zone OMI a tre. La pipeline lo riconduce a Bienno
invece di scartarlo — altrimenti la serie di Bienno cambierebbe territorio a
metà strada — e conserva il `link_zona` originale, così la ricostruzione resta
verificabile. È l'unico caso nei 22 semestri, e la mappa sta in `omi.py`
(`COMUNI_SOPPRESSI`), non in un file di configurazione da ricordarsi.

## Le compravendite hanno la loro trappola: l'intestazione che cambia

I quindici archivi dei volumi non hanno la stessa intestazione. In quindici anni
cambia una dozzina di volte: la colonna chiave si chiama `2011_CodCom`,
`2014_CodFitt` o `COD_COM` (2017 e 2018, senza anno); `AREA` diventa `Area` e
`prov` diventa `PROVINCIA`; il totale residenziale è `NTN 2011`, `NTN 2015_TOTALE`
o `NTN_2022`; una classe di superficie perde il «mq» nel 2014 e nel 2017. Per
questo `compravendite.py` normalizza le intestazioni invece di elencarle, prende
l'anno dal **nome del file** — l'unico posto dove c'è sempre — e **stampa un
avviso** se incontra una colonna che non sa mappare, invece di ignorarla in
silenzio.

Un cambio, però, non è di nome ma di sostanza: dal **2017** i «depositi
commerciali» diventano «depositi commerciali **e autorimesse**». Restano due
segmenti distinti nella tabella, perché sono due perimetri (MET-19).

E la chiave non è il codice ISTAT: è il **codice catastale** (`B157` per
Brescia). La corrispondenza viene dall'elenco ISTAT dei comuni, che pubblica i
due codici accanto, ed è finita in `comuni.csv` come colonna
`codice_catastale`. Il controllo che dice se la lettura è giusta è aritmetico:
**su 3.045 combinazioni comune × anno, il totale residenziale coincide sempre
con la somma delle cinque classi di superficie.**

## Cosa manca, di proposito

I **perimetri delle zone OMI** (KML, scaricabili dallo stesso servizio dal
2010/2) non sono stati chiesti: servono solo per scendere sotto il capoluogo, e
a grana comunale non aggiungono niente. Se un giorno servirà la mappa delle
ventisei zone della città — ventitré delle quali hanno quotazioni nel 2025/2 —
si chiedono allora, per il semestre delle quotazioni che si sta usando e non per
l'ultimo disponibile.
