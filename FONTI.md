# Brescia Dataviz — registro delle fonti aperte

Ricognizione delle fonti di dati aperti utilizzabili per un progetto di data
visualization sull'**evoluzione della città di Brescia** (comune 017029),
modellato sul pattern di `donostia-dataviz` ma con la domanda di ricerca
riformulata: *come è cambiata Brescia negli ultimi anni*, senza una tesi
turistica a monte.

> **Cos'è questo documento.** È il *registro delle fonti* (l'equivalente di
> `docs/SOURCES.md` + `datos/input/FUENTES.md` nel progetto Donostia). Non c'è
> ancora nessuna pipeline: qui si stabilisce **cosa esiste, a che grana, con
> quale copertura e come si scarica**. La colonna «stato accesso» è la cosa
> che guida l'ordine di costruzione: prima le fonti `verificata`, poi quelle
> che richiedono registrazione, per ultime quelle da estrarre a mano.

## Legenda «stato accesso»

| Stato | Significato |
|---|---|
| **verificata ✓** | Endpoint interrogato realmente durante questa ricognizione (ago-2026): risponde, e i dati di Brescia ci sono. Sotto ogni riga così marcata c'è la prova (conteggi, ID, date). |
| **da registrare** | Fonte pubblica e gratuita, ma dietro autenticazione (SPID/CIE/Fisconline). Nessun ostacolo tecnico, serve un login una volta. |
| **non raggiungibile da qui** | Fonte che esiste e è pubblica, ma l'host non risponde da questo ambiente di esecuzione (timeout, 403 anti-bot, 503). Scaricabile da una macchina normale con un browser. |
| **da estrarre a mano** | Non esiste un dataset strutturato: il dato vive in PDF, in una sala stampa o in un report. Va curato come CSV versionato (stesso pattern dei `datos/input/*.csv` curati in Donostia). |
| **da verificare** | Trovata, plausibile, non ancora testata contro Brescia. |

---

## 1. Geometria di riferimento

Il principio del progetto Donostia — *una sola geometria, un solo join in
ingestione* — vale identico qui. Brescia ha una struttura ufficiale a due
livelli: **33 quartieri** raggruppati in **5 zone** (Centro, Nord, Est, Sud,
Ovest). Le circoscrizioni sono state abolite, ma alcune pubblicazioni comunali
citano ancora il termine.

| Risorsa | Fonte | Endpoint | Stato | Note |
|---|---|---|---|---|
| Quartieri (33) + zone (5) | OpenStreetMap | Overpass API, `area(3600045144)` → `rel[boundary=administrative][admin_level=10]` (quartieri) e `admin_level=9` (zone) | **verificata ✓** | 33 relazioni `admin_level=10` e 5 `admin_level=9` restituite; 29/33 quartieri portano un `wikidata`. Licenza ODbL. Geometria poligonale completa via `out geom`. |
| Confini quartieri ufficiali | Comune di Brescia — open data / geoportale | `dati.comune.brescia.it`, `geoportale.comune.brescia.it` | **non raggiungibile da qui** | Da usare come **fonte primaria** e OSM come ripiego/controllo: i confini amministrativi vanno validati contro il dato comunale prima di pubblicare qualsiasi mappa. |
| Sezioni di censimento (grana sub-quartiere) | ISTAT — Basi territoriali | `istat.it/storage/cartografia/basi_territoriali/2021/R03_21.zip` (Lombardia 2021, 62 MB) · `.../WGS_84_UTM/2011/R03_11_WGS84.zip` (2011, 46 MB) | **verificata ✓** | HTTP 200, `application/zip`, dimensioni sopra. Anche 1991 e 2001. Proiezione WGS84/UTM32N → riproiettare a EPSG:4326. |
| Crosswalk indirizzo → sezione → quartiere → zona | Comune di Brescia — *Indirizzario completo* (2015) | `dati.comune.brescia.it/.../25-viario-completo-del-comune-di-brescia` | **non raggiungibile da qui** | **Pezzo chiave.** Contiene indirizzi con civici *insieme a* sezione di censimento, quartiere e zona: rende l'aggregazione sezioni→quartieri **esatta** invece che approssimata per sovrapposizione geometrica. È l'analogo del callejero municipale che in Donostia ha sbloccato la grana «via». |

**Elenco dei 33 quartieri** (nomi come restituiti da OSM, da normalizzare in
`quartiere_id` slug stabile):

Borgo Trento · Brescia Antica · Buffalora-Bettole · Caionvico · Casazza ·
Centro Storico Nord · Centro Storico Sud · Chiesanuova · Chiusure · Crocifissa
di Rosa · Don Bosco · Fiumicello · Folzano · Fornaci · Lamarmora · Mompiano ·
Porta Cremona-Volta · Porta Milano · Porta Venezia · Primo Maggio · San
Bartolomeo · San Polo Case · San Polo Cimabue · San Polo Parco · San
Rocchino-Costalunga · Sanpolino · Sant'Eufemia · Sant'Eustacchio · Urago Mella
· Villaggio Badia · Villaggio Prealpino · Villaggio Sereno · Villaggio Violino

> ⚠️ Le tre partizioni di San Polo (Case / Cimabue / Parco) più Sanpolino sono
> quartieri distinti ma contigui e demograficamente affini: nelle mappe
> conviene tenerli separati (sono l'esempio più chiaro di edilizia pubblica
> pianificata in città) ma citarli come blocco nei testi.

---

## 2. Casa: prezzi, affitti, patrimonio

È l'asse su cui il progetto Donostia era più forte e dove Brescia è, in
partenza, **più povera di dati aperti a grana di quartiere**. La differenza
strutturale: in Spagna il dato di affitto €/m² per barrio è pubblicato
dall'amministrazione (EMA/EMAL); in Italia il dato ufficiale equivalente è
l'OMI, che ha una grana propria (le **zone OMI**) e sta dietro un login.

| Tema | Fonte | Endpoint / percorso | Grana | Copertura | Stato | Licenza |
|---|---|---|---|---|---|---|
| Quotazioni immobiliari (vendita e locazione, min-max €/m² per tipologia) | Agenzia delle Entrate — OMI | *Forniture dati OMI*, area riservata (SPID/CIE/CNS/Fisconline) | **zona OMI** | semestrale dal **2004/1** | **da registrare** | citazione obbligatoria «Agenzia Entrate - OMI» |
| Le stesse quotazioni, già ripulite | onData APS | `github.com/ondata/quotazioni-immobiliari-agenzia-entrate` — `data/valori.7z`, `data/zone.7z` | zona OMI | dal **2016/1** | **verificata ✓** (repo raggiungibile) | rielaborazione di dato pubblico |
| Perimetri delle zone OMI (geometria) | Agenzia delle Entrate — GeoPOI | *Download Perimetri → Zone OMI*, livello provinciale, GML/KML | zona OMI | attuale | **da registrare** | serve codice fiscale + CAPTCHA; **non** scaricabile in bulk |
| Compravendite (NTN normalizzate) | Agenzia delle Entrate — OMI | *Forniture dati OMI → Volumi di compravendita* | **comune** | annuale dal **2011** | **da registrare** | — |
| Prezzi richiesti di vendita e affitto €/m² per zona urbana | Immobiliare.it — *Mercato immobiliare* | `immobiliare.it/mercato-immobiliare/lombardia/brescia/` e `.../brescia/zona-<nome>/` | **zona urbana** (≈ gruppi di quartieri) | serie mensile pluriennale | **non raggiungibile da qui** (403 anti-bot) | prezzi **di offerta**, non di transazione → *proxy* |
| Idem, serie storica di città e provincia | idealista — sala stampa | `idealista.it/sala-stampa/report-prezzo-immobile/vendita/lombardia/brescia-provincia/brescia/` | città / provincia | serie storica | **non raggiungibile da qui** (403 anti-bot) | *proxy* di offerta |
| Abitazioni: occupate / non occupate, **titolo di godimento (affitto vs proprietà)**, epoca di costruzione, superficie | ISTAT — Censimento permanente, variabili censuarie | `esploradati.istat.it/databrowser/DWL/PERMPOP/SUBCOM/Dati_regionali_2021.zip` (254 MB) · 2011: `istat.it/storage/cartografia/variabili-censuarie/dati-cpa_2011.zip` (52 MB) | **sezione di censimento** → aggregabile a quartiere | 2021 e 2011 (più 2001, 1991) | **verificata ✓** | HTTP 200, dimensioni sopra |
| Patrimonio immobiliare comunale per quartiere | Comune di Brescia — open data | `dati.comune.brescia.it/.../32-patrimonio-immobiliare-del-comune` | quartiere | 2014, 2016 | **non raggiungibile da qui** | serie vecchia; utile solo come contesto |
| Catasto: fabbricati e terreni attivi (rendita, consistenza, categoria, classe) | Comune di Brescia via Open Data Regione Lombardia | `dati.lombardia.it/resource/j5xd-rtju` (fabbricati), `8jcn-p4vj` (terreni) | foglio/particella/subalterno | snapshot 2021 | **verificata ✓** (schema letto) | ⚠️ **senza coordinate né quartiere**: solo riferimenti catastali. Geolocalizzabile solo con la geometria catastale INSPIRE, che non è confermata come aperta. Stesso vicolo cieco del catastro forale in Donostia. |

**Nota sull'asse casa.** La combinazione realistica è: **ISTAT censuario** per
lo *stock* (quante abitazioni, quante in affitto, quante vuote, quanto vecchie)
a grana fine e con due fotografie confrontabili (2011 → 2021); **OMI** per i
*prezzi* con serie semestrale lunga ma su una geometria diversa (serve un
crosswalk zone OMI ↔ quartieri, dichiarato); **Immobiliare.it** come *proxy*
mensile di offerta, curato a mano, per il tratto recente. Nessuna delle tre
sostituisce le altre e la scheda di confidenza va dichiarata metrica per
metrica, come in Donostia (`observed` / `derived` / `proxy`).

---

## 3. Demografia e reddito

| Tema | Fonte | Endpoint | Grana | Copertura | Stato |
|---|---|---|---|---|---|
| Popolazione per quartiere e sesso | Comune di Brescia — Statistica demografica | `comune.brescia.it/it/documenti_pubblici/statistica-demografica` → *Popolazione residente … distinta per circoscrizione, quartiere, sesso* (PDF) | **quartiere** | al 31.12.2024 | **da estrarre a mano** (pagina **verificata ✓**, HTTP 200) |
| Aspetti demografici per quartiere: cittadinanza, età media, indici demografici, densità | idem → *Aspetti demografici della popolazione residente per quartiere* (PDF) | **quartiere** | 2025 (al 1.1.2025) | **da estrarre a mano** (pagina verificata ✓) |
| Indicatori demografici di città (natalità, mortalità) | idem → *Indicatori Demografici* (PDF) | città | **1971–2024** | **da estrarre a mano** (pagina verificata ✓) |
| Popolazione 65+ per quartiere; famiglie per quartiere e per numero di componenti | Comune di Brescia — open data | `dati.comune.brescia.it/dataset?groups=demografia` | quartiere | serie storiche parziali (alcune ferme al 2014) | **non raggiungibile da qui** |
| Popolazione, cittadinanza, titolo di studio, condizione professionale | ISTAT — variabili censuarie (v. §2) | **sezione di censimento** | 2021, 2011, 2001, 1991 | **verificata ✓** |
| Bilancio demografico; stranieri residenti per cittadinanza | ISTAT — `demo.istat.it` | `demo.istat.it/app/?i=P02` (bilancio), `?i=P03` (bilancio stranieri) | comune | annuale, serie lunga | **verificata ✓** (host 200) |
| Popolazione residente al 1° gennaio | ISTAT SDMX | `esploradati.istat.it/SDMXWS/rest/data/IT1,22_289_DF_DCIS_POPRES1_1,1.0/…` | comune | serie lunga | **da verificare** — l'endpoint risponde ma la chiave dimensionale va ricostruita dal DSD (il mio primo tentativo ha dato `NoRecordsFound`) |
| Reddito IRPEF: imponibile, imposta netta, addizionali | MEF — Dipartimento delle Finanze, *Open data comunale* | `finanze.gov.it/it/statistiche-fiscali/open-data-comunale-principali-variabili-irpef/` | **comune + sub-comunale per CAP** | serie storica fino a imposta **2024** | **verificata ✓** (host 200) |

**Il reddito per CAP è il ritrovamento più interessante di questa sezione.**
Brescia ha i CAP 25121–25136: non coincidono con i quartieri, ma danno un
gradiente di reddito *interno alla città* — cosa che in Donostia veniva da
Eustat a grana barrio. Va dichiarato come proxy con un crosswalk CAP→quartieri
esplicito, mai come dato di quartiere.

---

## 4. Sicurezza reale e percepita

L'utente ha chiesto esplicitamente entrambe le facce. In Donostia questo asse
era il più fragile (dato comunale parziale, ripiego provinciale dichiarato).
Per Brescia la situazione è simile ma non identica.

| Tema | Fonte | Endpoint | Grana | Copertura | Stato |
|---|---|---|---|---|---|
| Delitti denunciati dalle forze di polizia, per tipo di reato — **grandi comuni** | ISTAT | dataflow `73_67_DF_DCCV_DELITTIPS_2` e tasso di delittuosità `_8` | **comune capoluogo** | serie storica | ⚠️ **dataflow presente ma vuoto** via SDMX: la richiesta restituisce l'intestazione e zero osservazioni. Ripiego: le **tavole XLSX** su `istat.it/tavole-di-dati/…delitti-denunciati…` |
| Delitti denunciati per tipologia | ISTAT | `73_67_DF_DCCV_DELITTIPS_1`, tasso provinciale `_9` | provincia | serie storica | idem (SDMX vuoto → tavole) |
| Infrazioni penali per tipologia | Ministero dell'Interno — Portale Statistico della Criminalità | `estadisticasdecriminalidad`-equivalente italiano: *Portale Statistico della Criminalità* / Banca Dati | provincia (BS) | serie annuale | **da verificare** — è la fonte che in Donostia ha chiuso il buco della serie totale; qui l'equivalente è provinciale, quindi Brescia città ≈ una frazione della provincia: da dichiarare |
| Percezione di sicurezza (camminare da soli al buio), 67 indicatori di benessere | ISTAT — **BesT, Benessere equo e sostenibile dei territori** | report regionali + serie storiche provinciali | **provincia (NUTS3)** | serie storica, ed. 2025 | **verificata ✓** (pagine 200) — include la percezione di sicurezza rilevata dal Censimento |
| Inquinamento, **criminalità e rumore percepiti nella zona in cui si vive** | ISTAT — *Aspetti della vita quotidiana* | dataflow `33_291` | regione | serie storica | **da verificare** (dataflow esiste nell'elenco) |
| Incidenti stradali per fascia d'età | Comune di Brescia via Regione Lombardia | `dati.lombardia.it/resource/6y9w-g8ff` | città | 2015–2018 | **da verificare** (schema non letto) |

**Onestà metodologica obbligata su questo asse.** La percezione è disponibile a
grana **provinciale o regionale**, il reato a grana **comunale nel migliore dei
casi**. Non esiste, per Brescia, un dato aperto di criminalità *per quartiere*.
Qualunque mappa che colori i quartieri per «sicurezza» sarebbe inventata: il
confronto percezione-vs-realtà va tenuto a livello di città/provincia, come
serie temporale, esattamente come `analysis/perception_vs_crime.py` nel
progetto Donostia. Se serve un segnale intra-urbano, l'unica via legittima è
un'indagine comunale di percezione (v. §7, l'analogo dell'indagine sul rumore
usata in Donostia).

---

## 5. Clima, aria, ambiente

Qui Brescia è **più ricca di Donostia**, e per una ragione strutturale: ARPA
Lombardia pubblica tutta la rete di monitoraggio come open data su Socrata, con
serie orarie e storiche complete, senza chiave API. In Donostia il clima veniva
da una sola stazione AEMET con chiave; qui ci sono più stazioni con serie
trentennali e, in più, **la qualità dell'aria** — che per una città della
pianura padana è un asse narrativo di primo piano, non un accessorio.

### 5.1 Clima

| Risorsa | Endpoint (`dati.lombardia.it`) | Copertura |
|---|---|---|
| Anagrafica stazioni idro-nivo-meteo | `resource/nf78-nj6b` | attuale, con `lat`/`lng`, `quota`, `datastart`, `datastop` |
| Temperatura fino al 2010 | `resource/6eu4-4tja` | storico |
| Temperatura 2011–2020 | `resource/d4kj-kbpj` | storico |
| Temperatura dal 2021 | `resource/w9wd-u6jh` | corrente |
| Dati sensori meteo (multi-parametro, corrente) | `resource/647i-nhxk` | corrente |
| Velocità del vento dal 2021 | `resource/hu5q-68e3` | corrente |

**Stazioni utili nel comune di Brescia — verificata ✓** (interrogazione
sull'anagrafica, `provincia='BS'`):

| Sensore | Parametro | Stazione | Dal | Stato |
|---|---|---|---|---|
| 2417 | Precipitazione | Brescia ITAS Pastori | 1990-10-11 | attiva |
| 2414 | Temperatura | Brescia ITAS Pastori | 1995-01-01 | attiva |
| 2415 | Umidità relativa | Brescia ITAS Pastori | 1995-01-01 | attiva |
| 6795 | Temperatura | Brescia v.Ziziola | 1997-10-17 | attiva |
| 6792 | Precipitazione | Brescia v.Ziziola | 1997-10-15 | attiva |
| 6797 | Velocità vento | Brescia v.Ziziola | 1997-10-15 | attiva |
| 6788 | Direzione vento | Brescia v.Ziziola | 1997-10-15 | attiva |
| 6796 | Umidità relativa | Brescia v.Ziziola | 2003-11-18 | attiva |

Due stazioni attive con temperatura dal 1995/1997 e precipitazione dal 1990:
sufficienti per *warming stripes*, giorni ≥30 °C, medie mensili e trend — le
stesse metriche costruite in Donostia da AEMET, ma con due punti invece di uno.

### 5.2 Qualità dell'aria

| Risorsa | Endpoint | Copertura |
|---|---|---|
| Anagrafica stazioni/sensori | `resource/ib47-atvt` | attuale, con `lat`/`lng` |
| Dati sensori aria fino al 1999 | `resource/evzn-32bs` | storico |
| Dati sensori aria 2000–2009 | `resource/cthp-zqrr` | storico |
| Dati sensori aria 2010–2017 | `resource/nr8w-tj77` | storico |
| Dati sensori aria dal 2018 | `resource/g2hp-ar79` | corrente |
| Dati sensori aria NRT | `resource/ykhg-b8rs` | tempo quasi reale |

**Verificata ✓**: 42 serie-sensore nel comune di Brescia, distribuite su 5
stazioni attive (v.Broletto, v.Turati, v.Tartaglia, Villaggio Sereno, S.Polo) e
2 dismesse (v.Ziziola, v.Triumplina). Esempi di profondità storica: ossidi di
azoto a v.Broletto dal **1992-08-05**; PM10 v.Broletto dal **2000-09-23**; PM10
Villaggio Sereno dal **2006-01-01**; PM2.5 Villaggio Sereno dal **2006-06-06**;
PM2.5 S.Polo e NO₂ dal **2020-12-07**. Ogni sensore porta `lat`/`lng`, quindi
il join punto→quartiere è immediato: 5 stazioni non fanno una coropletica, ma
danno un **contrasto intra-urbano reale** (centro storico vs periferia sud vs
San Polo).

### 5.3 Altro ambiente

| Tema | Fonte | Endpoint | Stato |
|---|---|---|---|
| Isola di calore superficiale (LST per quartiere) | Landsat 8/9 Collection 2 L2, banda termica | STAC di Microsoft Planetary Computer, `planetarycomputer.microsoft.com/api/stac/v1/collections/landsat-c2-l2` | **verificata ✓** (200, accesso anonimo) — replicabile *tale e quale* da `analysis/heat_island.py` di Donostia, e in pianura padana è più rilevante che sulla costa basca |
| Mappatura acustica strategica dell'agglomerato di Brescia (END 2002/49/CE) | Comune di Brescia — agglomerato `IT_a_ag00016` | `comune.brescia.it/aree-tematiche/ambiente/…/inquinamento-acustico-mappatura-acustica` + relazione PDF; Piano d'azione 2024 | **non raggiungibile da qui** (410 sui vecchi percorsi) | equivalente diretto delle isofone di Donostia (`noise_night_pct55`); da recuperare i layer GIS, non solo il PDF |
| Verde urbano, aria, mobilità, rifiuti nei comuni capoluogo | ISTAT — *Ambiente urbano* / *Dati ambientali nelle città* | `istat.it/statistiche-per-temi/focus/ambiente-urbano/` | **verificata ✓** (200) | grana comune capoluogo, annuale: set di indicatori di città pronto all'uso |

---

## 6. Turismo e ricettività

L'asse è secondario nella riformulazione bresciana, ma serve: Brescia è stata
**Capitale italiana della cultura 2023** con Bergamo, e quello è uno shock
datato che si deve vedere nelle serie.

| Tema | Fonte | Endpoint | Grana | Copertura | Stato |
|---|---|---|---|---|---|
| Flussi turistici mensili (arrivi, presenze, permanenza media) | Regione Lombardia | `dati.lombardia.it/resource/mzxz-sz25` | **comune** | **2019–2024**, mensile | **verificata ✓** — Brescia presente (`codice_istat` 17029); es. ago-2019: 24.450 arrivi / 53.867 presenze / 2,2 gg |
| Flussi turistici annuali | Regione Lombardia | `resource/vyxt-7jdx` | comune | 2019–2024 | **verificata ✓** (62.891 righe, stesso range) |
| Flussi turistici mensili per provincia | Regione Lombardia | `resource/xzck-giqt` | provincia | mensile | **verificata ✓** (presente in catalogo) |
| Flusso turistico a Brescia per nazionalità | Comune di Brescia — open data | `dati.comune.brescia.it/.../42-flusso-turistico-a-brescia…` | città | **2005–2013** | **non raggiungibile da qui** — è il pezzo che estende indietro la serie regionale (che parte dal 2019) |
| Movimento dei clienti negli esercizi ricettivi | ISTAT | dataflow *Capacità/Movimento esercizi ricettivi* | comune capoluogo | serie lunga | **da verificare** — la via per coprire il buco 2014–2018 |
| Strutture alberghiere e RTA · B&B · affittacamere · alloggi agrituristici · alberghi diffusi | Regione Lombardia | `dati.lombardia.it` id `fiiw-i5su`, `jzsu-f86x`, `6var-2hht`, `yg8e-47jy`, `69j3-9hcp` | struttura (con indirizzo) | agg. 2024 | **da verificare** — presenti in catalogo ma non serviti dall'API tabellare (sono risorse-file): vanno scaricate dal portale |
| Annunci Airbnb geolocalizzati | Inside Airbnb | — | — | — | **non disponibile**: **verificata ✓ l'assenza**. L'Italia è coperta solo per Napoli, Bologna, Roma, Milano, Bergamo, Veneto/Venezia, Toscana/Firenze, Puglia, Sicilia. **Brescia non c'è.** Esiste un archivio nazionale su richiesta. |
| Codice Identificativo Nazionale (CIN) delle locazioni turistiche | Ministero del Turismo — Banca Dati Strutture Ricettive | — | struttura | dal 2024 | **da verificare** — è oggi l'unico censimento pubblico degli affitti brevi; sostituto naturale di Airbnb, ma serie cortissima |

**Conseguenza di progetto.** Il pilastro «VUT / densità Airbnb per barrio» del
progetto Donostia **non è replicabile** a Brescia con dati aperti. Il
sostituto è la ricettività ufficiale (strutture con indirizzo → geocodifica →
quartiere) più il CIN. È un'assenza da dichiarare, non da mascherare con un
proxy debole.

---

## 7. Riqualificazione dei quartieri

| Tema | Fonte | Endpoint | Stato |
|---|---|---|---|
| Progetti PNRR del comune di Brescia (importi, temi, soggetto attuatore) | OpenPNRR (Fondazione Openpolis) | `openpnrr.it/territorio/017029`; open data CSV su `openpnrr.it/opendata/` | **verificata ✓** (host 200). Licenza **ODbL 1.0** |
| Attuazione misure PNRR — pagina istituzionale | Comune di Brescia | `comune.brescia.it/it/attuazione-misure-pnrr` | **da verificare** |
| Progetti a finanziamento europeo georeferenziati | OpenCoesione | `opencoesione.gov.it/it/opendata/` | **non raggiungibile da qui** (403) |
| Progetti PNRR — dati ufficiali | Italia Domani | `italiadomani.gov.it/it/opendata.html` | **non raggiungibile da qui** (403) |
| Codici unici di progetto (CUP) | OpenCUP | `opencup.gov.it` | **da verificare** (404 sul percorso tentato) |
| Piano di Governo del Territorio, tavole | Provincia di Brescia via Regione Lombardia | `dati.lombardia.it/resource/rkd9-8pqd` | **da verificare** |
| Indagini di percezione comunali (rumore, sicurezza, qualità del quartiere) | Comune di Brescia — Indagini statistiche | `comune.brescia.it/aree-tematiche/indagini-statistiche/…` | **non raggiungibile da qui** (410) — vale la pena cercarle: in Donostia un'indagine comunale sul rumore percepito ha fornito l'unico dato di percezione a grana quartiere |
| Risultati elettorali per sezione | Ministero dell'Interno — Eligendo | `elezioni.interno.gov.it/opendata/` | **verificata ✓** (200) — le sezioni elettorali sono mappabili sui quartieri: un indicatore di cambiamento sociale disponibile a grana fine e con serie lunga |

---

## 8. Portali: stato di raggiungibilità da questo ambiente

Tabella di servizio, per non ripetere tentativi inutili. «Non raggiungibile da
qui» **non** significa che la fonte non esista: significa che va scaricata da
una macchina normale. È lo stesso limite che il progetto Donostia documenta per
`opendata.gipuzkoa.eus` e per idealista.

| Host | Esito | Nota |
|---|---|---|
| `dati.lombardia.it` | ✓ 200 | API Socrata piena (SoQL, `$where`, `$select`, `$group`). **Il canale di accesso principale.** |
| `dati.gov.it` | ✓ 200 | CKAN nazionale, `api/3/action/package_search` funziona; fa harvesting anche del catalogo bresciano (115 risultati per «brescia») |
| `esploradati.istat.it` | ✓ 200 | SDMX: 4.896 dataflow. Le strutture rispondono; alcune serie tornano vuote (v. §4) |
| `istat.it` (storage cartografia) | ✓ 200 | Basi territoriali e variabili censuarie scaricabili direttamente |
| `demo.istat.it` | ✓ 200 | — |
| `finanze.gov.it` | ✓ 200 | — |
| `overpass-api.de` | ✓ 200 | Geometrie OSM |
| `planetarycomputer.microsoft.com` | ✓ 200 | Landsat |
| `openpnrr.it` | ✓ 200 | — |
| `elezioni.interno.gov.it` | ✓ 200 | — |
| `insideairbnb.com` | ✓ 200 | (ma senza Brescia) |
| `agenziaentrate.gov.it` | ✓ 200 | portale sì, dati OMI dietro login |
| `dati.comune.brescia.it` | ✗ timeout / 503 | **il portale del Comune**: esiste, è indicizzato, ma l'host non risponde da qui né in HTTP né in HTTPS |
| `comune.brescia.it` | ~ misto | `/it/documenti_pubblici/statistica-demografica` risponde 200; molti vecchi percorsi danno 410 (sito ristrutturato) |
| `geoportale.comune.brescia.it` | ✗ nessuna risposta | — |
| `immobiliare.it`, `idealista.it` | ✗ 403 | anti-bot |
| `opencoesione.gov.it`, `italiadomani.gov.it` | ✗ 403 | — |
| `bresciamobilita.it` | ✗ 403 | — |

---

## 9. Sintesi: cosa è più forte e cosa è più debole rispetto a Donostia

**Più forte a Brescia**

- **Qualità dell'aria**: serie dal 1992, 5 stazioni attive georeferenziate,
  API aperta. In Donostia questo asse non esisteva. Per una città padana è
  materia narrativa centrale, non un contorno.
- **Grana censuaria**: le sezioni di censimento ISTAT con le variabili
  censuarie danno popolazione, istruzione, condizione professionale, abitazioni
  e **affitto vs proprietà** a grana sub-quartiere, con due fotografie
  confrontabili (2011 → 2021). Donostia lavorava a grana barrio e ha dovuto
  costruire a mano la grana «via».
- **Clima**: due stazioni con serie trentennali invece di una.
- **Reddito sub-comunale** per CAP.
- **Elezioni per sezione**: serie lunga a grana fine.

**Più debole a Brescia**

- **Prezzi della casa per quartiere**: nessun equivalente aperto dell'EMA/EMAL
  basco. L'OMI ha la serie ma su una geometria propria e dietro login; il resto
  è offerta scrapata (proxy).
- **Affitti brevi**: nessuna copertura Inside Airbnb, nessun censimento
  comunale di viviendas turísticas. Solo ricettività ufficiale e CIN
  (dal 2024).
- **Criminalità**: nessun dato per quartiere. Comune nel migliore dei casi,
  spesso provincia.
- **Il portale comunale è il collo di bottiglia**: i pezzi più preziosi
  (indirizzario con crosswalk sezione→quartiere, popolazione per quartiere,
  turismo 2005–2013) stanno lì, in PDF o in un CKAN che da qui non risponde.
  Vanno scaricati a mano e versionati come input curati.

**Serie temporali più corte da tenere presente**: flussi turistici regionali
solo 2019–2024 (buco 2014–2018 da colmare con ISTAT), variabili censuarie a
fotografie decennali, CIN dal 2024. Il «negli ultimi anni» del brief è quindi
un orizzonte **disomogeneo per asse**: aria e clima 30 anni, censimento due
punti, turismo 6 anni. Va reso esplicito nella grafica, non appiattito.

---

*Ricognizione effettuata ad agosto 2026. Ogni riga marcata «verificata ✓» è
stata interrogata realmente; le altre portano lo stato di accesso che le
descrive. Nessun dato è ancora stato scaricato o elaborato: questo documento
precede la pipeline.*
