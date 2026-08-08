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
| **Contribuenti e reddito complessivo per classi di importo** | MEF via ISTAT SDMX | dataflow `30_1008_DF_MEF_REDDITIIRPEF_COM_2` | **comune** | serie storica | **verificata ✓** — 261.331 osservazioni. Dà la **distribuzione** del reddito, non solo la media: è ciò che serve per parlare di disuguaglianza invece che di livello |

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
| **Percezione della sicurezza camminando al buio da soli** nella zona in cui si abita | ISTAT — Censimento permanente | dataflow `DF_DCSS_BEST_PPC_6_GC` | **comune** | **2022–2024**, annuale | **verificata ✓** — 11.640 osservazioni, e fra i territori c'è `017029: Brescia` (oltre alla provincia `ITC47`). Popolazione 14+ per classe di risposta e sesso: le quote si derivano dai conteggi |
| **Percezione del rischio di criminalità** nella zona in cui si abita | ISTAT — Censimento permanente | `DF_DCSS_BEST_PPC_1_GC` | **comune** | 2022–2024 | **verificata ✓** (2.446 osservazioni) |
| Soddisfazione di vita, reti di sostegno (parenti, amici, vicini) | ISTAT — Censimento permanente | `DF_DCSS_BEST_PPC_2_GC` … `_5_GC` | comune | 2022–2024 | **verificata ✓** (stessa famiglia) |
| Tasso di delittuosità, per tipo di reato — **grandi comuni** | ISTAT | `73_67_DF_DCCV_DELITTIPS_8` | 12 città | 2006–2024 | ⚠️ **verificata ✓ l'esclusione di Brescia**: il dataflow ha dati (12.684 osservazioni) ma i «grandi comuni» sono solo Torino, Genova, Milano, Verona, Venezia, Bologna, Firenze, Roma, Napoli, Bari, Palermo, Catania. **Brescia non c'è.** |
| Tasso di delittuosità per tipo di reato — **province** | ISTAT | `73_67_DF_DCCV_DELITTIPS_9` | **provincia (BS)** | **2006–2024**, 56 tipologie di reato | **verificata ✓** — 1.057 righe per Brescia. È la serie lunga utilizzabile |
| Delitti denunciati per tipologia | ISTAT | `73_67_DF_DCCV_DELITTIPS_1`, `_4`, `_7` | provincia | serie storica | **da verificare** (stessa famiglia, dati presenti) |
| Infrazioni penali per tipologia | Ministero dell'Interno — Portale Statistico della Criminalità | Banca Dati Interforze | provincia (BS) | serie annuale | **da verificare** — conferma indipendente della serie ISTAT |
| Inquinamento, criminalità e rumore **percepiti** nella zona in cui si vive | ISTAT — *Aspetti della vita quotidiana* | dataflow `33_291` | regione | serie storica lunga | **da verificare** — utile per estendere indietro la percezione, che nel censimento parte dal 2022 |
| Incidenti stradali per fascia d'età | Comune di Brescia via Regione Lombardia | `dati.lombardia.it/resource/6y9w-g8ff` | città | 2015–2018 | **da verificare** (schema non letto) |

**Correzione rispetto alla prima stesura di questo documento.** Avevo concluso
che i dataflow ISTAT sulla criminalità fossero vuoti. Era un errore mio di
client, non un problema della fonte: v. la nota SDMX in §10. I dati ci sono.

**Cosa resta comunque vero.** Il **reato** per Brescia è disponibile solo a
grana **provinciale** — la città non rientra nei dodici «grandi comuni» — mentre
la **percezione** è disponibile a grana **comunale** ma solo dal 2022. Non
esiste, per Brescia, un dato aperto di criminalità *per quartiere*: una mappa
dei quartieri colorata per «sicurezza» sarebbe inventata. Il confronto
percezione-vs-realtà va costruito come serie temporale città/provincia, come
`analysis/perception_vs_crime.py` nel progetto Donostia, con l'asimmetria di
grana e di finestra dichiarata a schermo.

---

## 4-bis. Lavoro, imprese e tessuto produttivo

L'asse centrale della riformulazione. La domanda di fondo — *Brescia è ancora la
città della meccanica fatta di piccole aziende, o si è concentrata?* — ha una
risposta misurabile, e i dati per darla sono aperti e a grana comunale.

### Il registro delle imprese (ASIA)

**`183_1163_DF_DICA_ASIAULP_TERRIFDATA_7`** — *Unità locali e addetti per
classe di addetti e settore economico (Ateco 2 cifre), **comuni***.
**Verificata ✓** con chiave `A.017029...`: 4.266 osservazioni per Brescia,
**2018–2023**, con due indicatori (numero di unità locali `LU` e addetti in
media annua `LUEMPDAA`) incrociati per classe dimensionale
(`W0_9`, `W10_49`, `W50_249`, `W_GE250`).

È **il** dataset per la domanda sulla microimpresa. I totali estratti durante
la verifica:

| | 2018 | 2023 |
|---|---|---|
| Unità locali totali | 24.311 | 26.287 |
| di cui 0–9 addetti | 22.913 (94,2 %) | 24.726 (94,1 %) |
| di cui 10–49 | 1.180 | 1.335 |
| di cui 50–249 | 183 | 198 |
| di cui **≥250** | **35** | **28** |
| Addetti totali | 101.136 | 100.939 |
| addetti in unità 0–9 | 40.149 (39,7 %) | 41.315 (40,9 %) |
| addetti in unità 10–49 | 22.016 | 25.415 |
| addetti in unità 50–249 | 18.860 | 20.434 |
| addetti in unità **≥250** | **20.111 (19,9 %)** | **13.775 (13,6 %)** |

Letto così, in cinque anni: occupazione complessiva **ferma** (~101 mila), ma
**il vertice si assottiglia** — sette unità locali grandi in meno e 6.335
addetti in meno nella classe ≥250, mentre la fascia 10–249 ne guadagna quasi
5.000. La quota di addetti nelle micro-unità sale. Non è ancora una storia
verificata (2020–21 sono anni Covid, e «unità locale» non è «impresa»: lo
stabilimento di un gruppo con sede altrove conta qui), ma è esattamente la
domanda che hai posto, con i numeri che servono per rispondere.

> ⚠️ Due avvertenze da portarsi dietro. **Unità locale ≠ impresa**: una sede
> secondaria conta come unità locale nel comune dove sta. E la grana è
> **comunale**, non di quartiere: questo asse produce serie e barre, non
> coropletiche.

Altri tagli della stessa famiglia: `..._TERRIFDATA_6` (classe di addetti ×
Ateco 3 cifre, **provincia**), `_3` (Ateco 3 cifre, comuni), `_9` (per sistema
locale del lavoro 2021). Sulle imprese in senso proprio — forma giuridica, età
dell'impresa, sesso e **paese di nascita del titolare** — c'è la famiglia
`183_203_DF_DICA_ACDP_*`, da verificare per la grana.

### Occupazione dal Censimento permanente

| Dataflow | Cosa dà | Grana | Stato |
|---|---|---|---|
| `DF_DCSS_EMPLP_2_COM` | Occupati per sesso e **settore di attività economica** | comune | **verificata ✓** |
| `DF_DCSS_EMPLP_1_COM` | Occupati per sesso e **posizione nella professione** (dipendente/autonomo) | comune | **verificata ✓** (stessa famiglia) |
| `DF_DCSS_ISTR_LAV_PEN_2_TV_3` | Popolazione 15+ per **condizione professionale** ed età | comune | **verificata ✓** |
| `DF_DCSS_ISTR_LAV_PEN_2_TV_4` | Popolazione 15+ per **condizione professionale e cittadinanza** | comune | **verificata ✓** |
| `DF_DCSS_ISTR_LAV_PEN_2_TV_5` | Popolazione che si sposta giornalmente per **studio o lavoro** | comune | **verificata ✓** |
| `DF_DCSS_LCAS_FRISC_1`, `_2` | Occupati per utilizzo del **lavoro da casa**, sesso e età | comune | **verificata ✓** (famiglia `_GC`, che include Brescia) |
| `DF_DCSS_LCAS_FRISC_3` | Frequenza di corsi di formazione professionale | comune | idem |

Numeri estratti in verifica, **Brescia 2021** (occupati 15+ per settore):
**86.788 occupati** totali (48.469 uomini, 38.319 donne), di cui industria in
senso lato (B–F) **19.769 (22,8 %)**, commercio-alberghi-ristorazione 15.886,
servizi finanziari/professionali/immobiliari 18.351, altre attività 25.576,
agricoltura 674.

**Pendolarismo, Brescia 2019** (verificato): 108.034 residenti si spostano ogni
giorno, di cui **75.652 per lavoro** e 32.382 per studio; **26.425 escono dal
comune** (23.699 per lavoro). Solo 2018 e 2019 disponibili.

> **Un indicatore derivabile e interessante.** Gli addetti nelle unità locali
> *situate* a Brescia (100.939 nel 2023, ASIA) contro gli occupati *residenti*
> a Brescia (86.788 nel 2021, censimento) danno un rapporto di concentrazione
> del lavoro ≈ **1,16**: la città importa lavoratori. È lo stesso
> `job_concentration_ratio` costruito per Donostia. Da usare con cautela — anni
> e definizioni diversi — ma il segno è robusto e la matrice origine-destinazione
> vera non esiste come dato aperto.

### Altre fonti sul lavoro

| Tema | Fonte | Grana | Stato |
|---|---|---|---|
| Lavoratori dipendenti per attività economica e provincia di lavoro; retribuzioni per classi di importo **e cittadinanza** | INPS — Osservatori statistici (SDMX) | provincia | **da verificare** — serie dal 2008; il taglio per cittadinanza è raro e prezioso |
| Cassa integrazione, precariato, assunzioni | INPS — Open Data | provincia | **da verificare** |
| Forze di lavoro: tasso di occupazione, disoccupazione, attività | ISTAT — RCFL | provincia | **da verificare** |
| Avviamenti e cessazioni, tipologia contrattuale | Regione Lombardia — Comunicazioni Obbligatorie | provincia | **da verificare** |
| **Esportazioni e importazioni per paese e merce** | ISTAT — Coeweb, dataflow `139_176` | provincia | **da verificare** — per una provincia manifatturiera ed esportatrice come Brescia è un asse narrativo di prima grandezza |
| Infortuni sul lavoro | INAIL — Open Data | provincia/settore | **da verificare** — pertinente in una città industriale |

---

## 4-ter. Istruzione e università

| Tema | Fonte | Endpoint | Grana | Copertura | Stato |
|---|---|---|---|---|---|
| Grado di istruzione della popolazione 9+ per età | ISTAT — Censimento permanente | `DF_DCSS_ISTR_LAV_PEN_2_TV_1` | **comune** | dal 2018 | **verificata ✓** |
| Grado di istruzione **per cittadinanza** | idem | `DF_DCSS_ISTR_LAV_PEN_2_TV_2` | **comune** | dal 2018 | **verificata ✓** |
| Grado di istruzione | ISTAT — variabili censuarie | v. §2 | **sezione di censimento** | 2021, 2011 | **verificata ✓** |
| Iscritti, immatricolati, laureati per ateneo, corso, classe di laurea, sesso | MUR — USTAT Open Data | `dati-ustat.mur.gov.it` (CKAN) · portale `ustat.mur.gov.it/opendata/` | **ateneo** | iscritti **1998/99–2025/26**; laureati **2001–2024** | **non raggiungibile da qui** (`dati-ustat` non risponde, `ustat.mur.gov.it` 503 al momento della prova) — ma i dataset sono pubblici in CSV/XLSX |
| Scheda dell'Università degli Studi di Brescia | MUR — USTAT | `ustat.mur.gov.it/dati/didattica/italia/atenei-statali/brescia` | ateneo | serie storica | **da verificare** |

**Nota sui due atenei.** Brescia ha l'**Università degli Studi di Brescia**
(statale: ~12.200 iscritti nel 2000/01 → ~15.700 nel 2023/24, +29 %) e la sede
bresciana dell'**Università Cattolica del Sacro Cuore**. Entrambe compaiono
nell'anagrafica MUR: una lettura onesta della «Brescia che studia» le tiene
insieme, e la statale da sola sottostima la popolazione universitaria.

Il gancio più interessante non è il conteggio degli iscritti ma
l'**incrocio istruzione × lavoro × cittadinanza a livello comunale**, che il
censimento permanente rende possibile: quanti laureati vivono a Brescia, in che
settori lavorano, e come cambia il quadro fra italiani e stranieri.

---

## 4-quater. Stranieri: chi vive a Brescia e da dove viene

Brescia è una delle città italiane a più alta incidenza di popolazione
straniera, e questo è l'asse dove il Censimento permanente è
**inaspettatamente ricco**: pubblica a grana **comunale** una famiglia di
tabelle sul *background migratorio* che va molto oltre il semplice conteggio
degli stranieri.

| Dataflow (famiglia `DF_DCSS_MIGR_BACKG_PAR_TV_*_COM`) | Cosa dà |
|---|---|
| `_1_COM` | Popolazione italiana dalla nascita / italiana **per acquisizione** / straniera, per luogo di nascita dei genitori |
| `_2_COM`, `_3_COM` | Italiani nati in Italia e italiani nati all'estero, per luogo di nascita dei genitori |
| `_4_COM`, `_5_COM` | Italiani **per acquisizione**, per **cittadinanza precedente** e luogo di nascita dei genitori |
| `_6_COM`, `_7_COM` | **Stranieri nati in Italia** (seconde generazioni) e stranieri nati all'estero, per **cittadinanza** |
| `_8_COM`, `_9_COM`, `_10_COM` | Le stesse popolazioni incrociate con il **grado di istruzione** |

**Verificata ✓**: `_7_COM` restituisce 72.792 osservazioni. La famiglia dà, a
livello di comune, la distinzione fra chi è arrivato, chi è nato qui da
genitori stranieri e chi è diventato italiano — cioè la differenza fra
*immigrazione* e *popolazione di origine straniera*, che è la distinzione che
quasi tutte le narrazioni sbagliano.

| Altre fonti | Endpoint | Grana | Stato |
|---|---|---|---|
| Popolazione straniera per stato civile, posizione in famiglia, nel nucleo | `DF_DCSS_FORPOP_1_GC` … `_3_GC` | comune | **verificata ✓** (famiglia `_GC`) |
| Famiglie con almeno uno straniero / con tutti i componenti stranieri | `DF_DCSS_FAMIGLIE_TV_2`, `_3` | comune | **verificata ✓** |
| Nuclei con almeno uno straniero per **area geografica di cittadinanza** della persona di riferimento | `DF_DCSS_FPHH_FNCL_3_GC` | comune | **verificata ✓** |
| Bilancio demografico della popolazione straniera; **stranieri residenti per cittadinanza** | `demo.istat.it/app/?i=P03` | comune | **verificata ✓** (host 200) — è la serie annuale per singolo paese di cittadinanza |
| Acquisizioni di cittadinanza | ISTAT / `demo.istat.it` | comune | **da verificare** |
| Cittadinanza per sezione di censimento | variabili censuarie (§2) | **sezione** | **verificata ✓** — l'unica via per portare l'origine a grana di quartiere |
| Rapporti, ricerche e dossier sulla popolazione di origine straniera in città | **Comune di Brescia — Osservatorio sulle migrazioni e l'inclusione** | `comune.brescia.it/aree-tematiche/immigrazione/osservatorio-sulle-migrazioni-e-linclusione/dati-aperti-open-data` | quartiere, famiglie, seconde generazioni, acquisizioni | **non raggiungibile da qui** — **da recuperare a mano: è la fonte più vicina alla grana di quartiere su questo tema**, con rilevazioni su quartieri, famiglie, matrimoni, prime e seconde generazioni |

> ⚠️ Vale qui la stessa cautela che il progetto Donostia dichiara come MET-5: il
> **paese di origine non è un proxy** di reddito, di disagio o di
> trasformazione urbana. La rappresentazione è descrittiva, e il testo deve
> dirlo.

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

**Asse minore.** Brescia non è una città turistica e il progetto non ci
costruisce sopra una storia. Resta utile per una ragione sola: **Capitale
italiana della cultura 2023** con Bergamo è uno shock datato e identificabile,
e serve come contro-prova in altre serie (commercio, ricettività, occupazione
nei servizi). Va tenuto come capitolo breve, non come pilastro.

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

**Il ritrovamento principale: il Censimento permanente a grana comunale.**
ISTAT pubblica via SDMX una famiglia larghissima di tabelle `DF_DCSS_*` con
grana **comune** (e per alcune `_GC` «province e grandi comuni», dove Brescia
**c'è**). Copre lavoro, istruzione, condizione professionale, pendolarismo,
background migratorio, abitazioni, famiglie, percezione di sicurezza e
soddisfazione di vita — annuale dal 2018/2021 anziché decennale. È la fonte che
regge quasi tutti gli assi di questa riformulazione, e non era ovvia: sta
dietro sigle opache in un elenco di 4.896 dataflow.

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
- **Reddito sub-comunale** per CAP, più la **distribuzione** per classi di
  importo a livello comunale.
- **Elezioni per sezione**: serie lunga a grana fine.
- **Tessuto produttivo**: ASIA dà unità locali e addetti per classe
  dimensionale e settore, a livello comunale, 2018–2023. Donostia doveva
  accontentarsi di un proxy sugli esercizi commerciali.
- **Background migratorio**: dieci tabelle censuarie che distinguono stranieri,
  seconde generazioni e italiani per acquisizione, a livello comunale. In
  Donostia c'era il solo conteggio per nazionalità.
- **Percezione della sicurezza a livello di città** (2022–2024), che a Donostia
  esisteva solo per una zona statistica sovracomunale.

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

---

## 10. Nota tecnica: come si interroga l'SDMX di ISTAT

Va scritta perché mi ha già fatto sbagliare una conclusione, e farebbe perdere
tempo a chiunque riparta da qui.

**Il parametro `format=` nella query string non funziona.** Una richiesta come
`…/data/IT1,<dataflow>,1.0/<chiave>?format=csvfilewithlabels` restituisce
**l'intestazione CSV e zero righe**, anche quando i dati esistono. Sembra un
dataset vuoto e non lo è. Il formato va negoziato con l'header:

```bash
curl -H 'Accept: application/vnd.sdmx.data+csv;version=1.0.0;labels=both' \
  'https://esploradati.istat.it/SDMXWS/rest/data/IT1,DF_DCSS_EMPLP_2_COM,1.0/A.017029.....'
```

Le altre regole imparate sul campo:

1. **La chiave è posizionale**, un campo per dimensione, separati da punti.
   L'ordine e il numero esatto si leggono dal dataflow:
   `…/rest/dataflow/IT1/<dataflow>?references=all`, poi i tag
   `<structure:Dimension id="…">`. Un punto in più o in meno → zero righe,
   senza errore.
2. **Per sapere cosa esiste davvero**, prima dei dati, si usa
   `…/rest/availableconstraint/IT1,<dataflow>,1.0`: elenca i valori realmente
   presenti per ogni dimensione. È così che si scopre in dieci secondi che i
   «grandi comuni» della criminalità sono solo dodici città e Brescia non c'è.
3. **Il codice di Brescia comune è `017029`** nella codelist `CL_ITTER107`;
   la provincia è `ITC47`, il sistema locale del lavoro `SLL_66`.
4. **I pull a caratteri jolly su tutta Italia sono pesanti** (il tasso di
   delittuosità provinciale supera i 120 MB e va in timeout a 220 s): filtrare
   sempre per `REF_AREA` quando la dimensione lo consente.
5. Le etichette leggibili arrivano solo con `labels=both`; senza, si ottengono
   i codici nudi.

---

*Ricognizione effettuata ad agosto 2026, in due passate: la prima sugli assi
casa/sicurezza/clima/turismo, la seconda su lavoro, imprese, istruzione e
cittadinanze. Ogni riga marcata «verificata ✓» è stata interrogata realmente e
porta la sua prova; le altre dichiarano lo stato di accesso che le descrive.
Nessun dato è ancora stato scaricato o elaborato: questo documento precede la
pipeline.*
