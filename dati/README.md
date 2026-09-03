# Dati

> ⚠️ **Una tabella non è qui**: `migrazioni_comuni.csv` pesa 422 MB e resta
> fuori da git. Come rifarla in venti minuti, e perché va bene così, sta in
> [`SCARICHI-LOCALI.md`](SCARICHI-LOCALI.md).

Tre cartelle:

- **`processed/`** — le tabelle tidy, **versionate**: sono il prodotto del
  progetto. Circa 12 MB in tutto.
- **`geo/`** — la geometria di riferimento, **versionata**: i confini dei 205
  comuni in GeoJSON (320 KB). È la base di ogni coropletica.
- **`raw/`** — le risposte grezze delle fonti, **non versionate** (qualche GB:
  le tavole censuarie arrivano non filtrate, una nazione intera per volta) e
  rigenerabili con `python -m brescia_pipeline.build` da
  [`../pipeline/`](../pipeline/README.md).

Tutto è ricostruibile: nessun file qui è stato scritto a mano.

## Convenzioni comuni a tutte le tabelle

- **`codice_istat`** è la chiave di join: sei cifre, con lo zero iniziale
  (`017029` = Brescia). Va letto come **testo**: un foglio di calcolo che lo
  interpreta come numero mangia lo zero e rompe ogni incrocio.
- **Le celle vuote non sono zeri.** Significano «dato non disponibile o
  soppresso dalla fonte». Un comune senza valore sulle presenze turistiche non
  è un comune senza turisti.
- **Formato lungo (tidy)**: una riga per combinazione territorio × tempo ×
  dimensione, non una colonna per anno. Più righe, ma nessuna trasformazione
  necessaria per graficare.
- **Anni diversi in tabelle diverse**: ASIA si ferma al 2023, popolazione e
  turismo arrivano al 2024, l'aria al 2026. È la disponibilità delle fonti, non
  una scelta: qualsiasi rapporto fra tabelle mescola annate e va dichiarato.

## Le tabelle

### Territorio

| File | Righe | Contenuto |
|---|---|---|
| `comuni.csv` | 205 | Anagrafica: codice ISTAT, denominazione, sigla, flag capoluogo. |
| `comuni_sintesi.csv` | 205 | Una riga per comune con gli indicatori principali affiancati: popolazione 2024, unità locali e addetti 2023, addetti per 100 abitanti, presenze turistiche 2024. È la vista da aprire per prima. |
| `comuni_geometria.csv` | 205 | Superficie in km² e centroide (longitudine, latitudine) di ogni comune. Serve alle densità senza dover caricare la geometria, e rende verificabile con un CSV ciò che sta nel GeoJSON. |

### La geometria

| File | Contenuto |
|---|---|
| `geo/comuni_brescia.geojson` | I confini dei 205 comuni, **in gradi WGS84** (EPSG:4326), pronti per una mappa. Fonte: ISTAT, limiti amministrativi generalizzati al 01/01/2025. Ogni feature ha `id` = codice ISTAT e porta `comune`, `capoluogo`, `area_kmq`. |

È l'**unica geometria di riferimento** del progetto, e la chiave è il codice
ISTAT a sei cifre: nessuno slug inventato, nessun crosswalk (`BRIEF.md`).
Verifiche fatte alla costruzione, e ripetute dai test: la superficie
provinciale torna 4.785,3 km² contro i 4.785,6 noti, e le aree per comune
coincidono con lo `Shape_Area` di ISTAT entro lo 0,01 %.

> ⚠️ La fonte si chiama `_WGS84` ma è **in metri UTM 32N**, non in gradi. La
> pipeline riproietta (`pipeline/src/brescia_pipeline/geo.py`); chi riscarica
> lo shapefile a mano deve ricordarsene, perché l'errore non solleva nulla —
> disegna solo la provincia in mezzo all'oceano.

### Lavoro e imprese

| File | Righe | Contenuto |
|---|---|---|
| `imprese_classe_addetti.csv` | 9.488 | Unità locali e addetti per **comune × anno × classe dimensionale** (0-9, 10-49, 50-249, 250+, totale), 2018–2023. La tabella che regge l'asse principale del progetto. |
| `imprese_settore.csv` | 1.800 | Gli stessi indicatori per **divisione Ateco**, per la provincia e per il comune di Brescia. Il dettaglio settoriale su tutti i comuni sarebbe un prodotto cartesiano da milioni di righe. |
| `censimento_lavoro_brescia.csv` | 18.453 | Comune di Brescia: occupati per settore e posizione professionale, condizione professionale per età e cittadinanza, titolo di studio, pendolarismo. Formato lungo con `dimensione`/`modalita`, perché le tavole censuarie non hanno tutte le stesse dimensioni. |
| `tasso_occupazione_provincia.csv` | 384 | Tasso di occupazione della **provincia**, 2018–2025, per sesso, età, titolo di studio e cittadinanza. |

### Popolazione e redditi

| File | Righe | Contenuto |
|---|---|---|
| `popolazione_comuni.csv` | 5.302 | Popolazione residente, in famiglia, in convivenza e numero di famiglie, per comune, 2018–2024. |
| `bilancio_demografico_comuni.csv` | 13.530 | **Da dove viene** quella popolazione: nati, morti, iscritti e cancellati da altri comuni, iscritti e cancellati dall'estero, variazioni territoriali e aggiustamento statistico, per comune, 2019–2024. Più i tre stock (`popolazione_inizio`, `popolazione_fine`, `popolazione_censita`). |
| `redditi_comuni.csv` | 36.952 | Contribuenti e reddito complessivo per **classe di importo** (8 classi, da «≤ 0 €» a «oltre 120.000 €»), per comune, 2012–2023. Dà la distribuzione, non solo la media: è ciò che serve per parlare di disuguaglianza. |

> ⚠️ **Tre cose da sapere prima di usare il bilancio.**
>
> 1. **La tabella porta i flussi lordi, non i saldi.** Il saldo naturale è
>    `nati − morti`, il migratorio interno `immigrati_interni −
>    emigrati_interni`, e così via. La fonte pubblica anche i saldi già fatti e
>    qui non si riportano: una tabella con gli addendi *e* la somma ha due
>    verità appena una delle due si legge male. La definizione sta scritta una
>    volta sola in `analysis/_tabelle.py` (`COMPONENTI`).
> 2. **`aggiustamento_statistico` non è un fenomeno demografico.** È la
>    rettifica che riconcilia l'anagrafe con il censimento: −4.558 persone in
>    provincia fra il 2018 e il 2024, abbastanza da cambiare il segno di un
>    comune piccolo. Va tenuto separato dalle migrazioni, sempre (MET-15).
> 3. **`popolazione_censita` è la stessa cosa di `popolazione_residente` in
>    `popolazione_comuni.csv`**, comune per comune e anno per anno, allo zero: è
>    la condizione che permette di scomporre quella serie con questi flussi
>    senza inventare un residuo, ed è un test della pipeline.
>
> L'identità chiude: `popolazione_inizio` + i flussi + l'aggiustamento =
> `popolazione_censita`. Se un giorno smette di chiudere, la pipeline si rifiuta
> di scrivere la tabella.


### Chi vive nel bresciano

| File | Righe | Contenuto |
|---|---|---|
| `famiglie_comuni.csv` | 30.126 | Famiglie per numero di componenti, con **almeno uno** o **tutti** i componenti stranieri, per comune, 2018–2024. Le due situazioni restano separate come le tiene la fonte: la colonna `tavola` vale `tutte`, `almeno_uno_straniero` o `tutti_stranieri`, e la prima fa da denominatore quando serve una quota. |
| `abitazioni_comuni.csv` | 3.074 | Abitazioni occupate e non occupate, e quelle occupate per **proprietà, affitto, altro titolo** (`ownership_type`), per comune, 2019 · 2021 · 2023. È la risposta a «quante case in affitto» che non passa per i prezzi. |
| `migrazioni_comuni.csv` | ⏳ | Background migratorio per comune: **stranieri immigrati**, **stranieri nati in Italia** e **italiani per acquisizione**, per sesso, età, cittadinanza, luogo di nascita dei genitori e titolo di studio. Dieci tavole censuarie in una tabella, distinte dalla colonna `tavola`. Scarico in corso: sono le tavole più pesanti del progetto. |

> A differenza di `censimento_lavoro_brescia.csv`, queste tabelle tengono
> **una riga per osservazione con tutte le dimensioni in colonna**: dentro
> ciascuna famiglia le dimensioni sono fisse, e appiattirle distruggerebbe la
> distribuzione congiunta — che è l'informazione per cui valgono la pena.

⚠️ Tre avvertenze su queste tre tabelle.

1. **Le modalità sono in inglese** (`private households on 31st December`,
   `4 and over`). Non è una scelta: manca `Accept-Language: it` nella richiesta
   a ISTAT. Vale anche per `censimento_lavoro_brescia.csv`. Si corregge con una
   riga di codice e un riscarico completo — vedi
   [`../PROSSIMI-PASSI.md`](../PROSSIMI-PASSI.md) §2.4.
2. **In `abitazioni_comuni.csv` cinque colonne su sette sono costanti**:
   `numb_room`, `use_floor_spacegroup`, `heating_system_type`,
   `access_building` e `type_of_building` valgono sempre il proprio totale. La
   fonte dichiara quelle dimensioni ma **a grana comunale pubblica solo gli
   aggregati**: il dettaglio per stanze, superficie o riscaldamento non esiste
   sotto il livello provinciale. Le colonne restano per fedeltà alla fonte, non
   perché contengano qualcosa.
3. **Gli anni non sono una serie annuale piena**: le abitazioni ci sono solo
   per 2019, 2021 e 2023.

### Ambiente

| File | Righe | Contenuto |
|---|---|---|
| `stazioni_arpa.csv` | 323 | Anagrafica dei sensori ARPA della provincia (aria e meteo) con coordinate, quota e date di attivazione. |
| `aria_mensile.csv` | 15.463 | Medie mensili per sensore: PM10, PM2.5, NO₂, ozono e altri, dal 2000 al 2026. Aggregate lato server: le serie orarie grezze sono decine di milioni di righe. |
| `meteo_mensile.csv` | 20.150 | **Temperatura** (media mensile, dal 1987) e **precipitazione** (totale mensile, dal 1986) per sensore. La colonna `aggregazione` dice quale delle due è: sono due cose diverse e vanno lette come tali. |

> ⚠️ **La pioggia si somma, la temperatura si media.** Sembra ovvio e non lo è
> stato: i pluviometri registrano i millimetri caduti in ogni intervallo di dieci
> minuti, quindi il valore mensile è il **totale** — la loro media è un numero
> plausibile («in gennaio è caduta una media di 0,04 mm») che non significa
> niente. Per questo la colonna si chiama `valore` e non `media`, e accanto c'è
> `aggregazione`.

> ⚠️ **Il clima non è tutto qui.** L'anagrafica ARPA porta otto parametri —
> temperatura, precipitazione, umidità, vento (velocità e direzione), radiazione,
> livello idrometrico, neve — ma le serie storiche stanno in **un dataset per
> parametro** su `dati.lombardia.it`, non in uno solo. Qui ce ne sono due. Gli
> altri sei hanno i sensori in `stazioni_arpa.csv` e non hanno le misure: il
> build lo stampa a ogni esecuzione invece di lasciarlo dedurre dal file.

> ⚠️ **La colonna `stato`**, su entrambe le tabelle ambientali. Vale:
>
> - `osservato`;
> - `copertura_scarsa` — il mese ha molte meno letture del solito **per quel
>   sensore**. Una «media mensile» calcolata su otto letture non è una media
>   mensile, e nel file non si distingue da una calcolata su quattromila. La
>   soglia si calibra sul sensore e non è fissa: il PM10 si misura una volta al
>   giorno, la temperatura ogni dieci minuti, e una soglia assoluta marcherebbe
>   come scarso tutto il particolato;
> - `lettura_implausibile` — il mese contiene una lettura oltre il limite fisico
>   dichiarato per quel parametro. Riguarda **cinque mesi su ventimila**, tutti
>   di pioggia, e ognuno rovina il proprio totale: il pluviometro di Caino segna
>   109.499 mm in un intervallo del maggio 2020 e il mese esce a 109.589 mm. La
>   fonte non marca quelle righe e il filtro sui −999 non le vede.
>
> Le righe marcate **restano nel file**, come le presenze turistiche riservate:
> cancellarle produrrebbe un buco indistinguibile da un dato mai raccolto.
>
> ⏳ **Un residuo noto**: il limite è su una **lettura singola**, quindi non
> cattura un sensore mal calibrato per un mese intero. Ne resta almeno uno —
> Gambara v.Parma, agosto 2004, media mensile di 41,0 °C — che nessuna
> temperatura italiana giustifica ma nessuna lettura singola tradisce.

### Sicurezza

| File | Righe | Contenuto |
|---|---|---|
| `reati_provincia.csv` | 1.057 | Tasso di delittuosità della **provincia** per 100.000 abitanti, 2006–2024, 56 tipologie di reato. |
| `percezione_sicurezza.csv` | 1.224 | Percezione della sicurezza camminando al buio, percezione del rischio di criminalità e soddisfazione di vita, per il **comune** di Brescia e per la provincia, 2022–2024. |

> Le due tabelle restano separate apposta: i reati sono provinciali e partono
> dal 2006, la percezione è comunale e parte dal 2022. Non sono confrontabili
> riga per riga, e non esiste alcun dato per quartiere.

### Turismo

| File | Righe | Contenuto |
|---|---|---|
| `turismo_comuni_annuale.csv` | 8.929 | Arrivi, presenze e permanenza media per comune, tipo di struttura e cittadinanza dei turisti, 2019–2024. |
| `turismo_comuni_mensile.csv` | 8.020 | Gli stessi flussi con dettaglio mensile. |

⚠️ Tre avvertenze specifiche, le prime due già costate un errore:

1. **Filtrare su `tipo_struttura = 'Totale'` *e* `cittadinanza = 'Totale'`.** Le
   righe esistono per ogni combinazione, totali inclusi: sommare senza filtrare
   conta fino a tre volte le stesse notti.
2. **Guardare la colonna `stato`.** Vale `osservato`, `riservato` (dato
   soppresso dalla fonte per riservatezza statistica: la cella è vuota) oppure
   `zero_fittizio` — la riga «Totale» dichiara 0 ma tutte le sue componenti
   sono soppresse, quindi lo zero è calcolato su celle vuote, non misurato.
   Riguarda un solo comune (Gottolengo, 2024) e va escluso dai grafici, non
   disegnato come «nessun turismo».
3. **Nel 2024 mancano 73 comuni su 205, in tre modi diversi**: 45 hanno il dato
   soppresso, 1 è lo zero fittizio di cui sopra, e **27 non compaiono affatto**
   nella fonte — non hanno nemmeno una riga. Sono tre assenze diverse e nessuna
   delle tre è uno zero: su una mappa vanno tutte e tre nel colore «nessun
   dato», ma in una tabella conviene distinguerle.

### Il confronto: fuori dalla provincia

Sei tabelle che **non** sono un secondo soggetto. Servono a una domanda sola:
quello che si è misurato su Brescia è di Brescia o è dell'Italia? (MET-14). Non
entrano in nessuna mappa e non producono classifiche di comuni fuori provincia.

| File | Righe | Contenuto |
|---|---|---|
| `imprese_province.csv` | 28.180 | Unità locali e addetti per **tutte le 107 province**, per classe dimensionale e per sezione Ateco, 2018–2023. Non è costato un download: i file grezzi ASIA sono nazionali e il modulo li riaggrega. |
| `imprese_capoluoghi.csv` | 6.398 | Gli stessi indicatori per i **comuni capoluogo**, per rispondere a una domanda sola: lo svuotamento della classe ≥250 addetti nel capoluogo (MET-9) succede anche altrove? Sì, in 44 capoluoghi su 64. |
| `redditi_comuni_confronto.csv` | 43.080 | I redditi comunali di una provincia di confronto — oggi **Bergamo** (016) — nella stessa forma di `redditi_comuni.csv` più il territorio. Qui non basta un filtro: le tavole MEF si scaricano per blocchi di comuni, quindi ogni provincia costa i suoi download e la lista è corta apposta. |
| `bilancio_province.csv` | 7.062 | Le componenti demografiche per **tutte le 107 province**, 2019–2024. Stesso vantaggio delle imprese: il file della fonte è nazionale. È il termine di paragone che allo spopolamento mancava. |
| `turismo_province.csv` | 68.210 | Arrivi e presenze per **tutte le 107 province** (più Italia e regioni, colonna `livello`), 2008–2025, per tipologia di esercizio e residenza dei clienti. Fonte ISTAT, **diversa** da quella comunale: vedi il riquadro qui sotto. Chiude l'ultimo asse che non aveva un altrove. |

### Il dettaglio settoriale

| File | Righe | Contenuto |
|---|---|---|
| `imprese_sezioni_comuni.csv` | 34.886 | Unità locali e addetti per **comune × sezione Ateco**, 2018–2023. È la tabella che ha sbloccato l'asse «le due economie»: la specializzazione settoriale di *tutti* i comuni, che era data per impossibile. Si ottiene fissando il settore e lasciando libero il territorio — una richiesta per sezione su tutta Italia, filtrata in locale. |
| `imprese_settore_classe.csv` | 7.164 | Settore **e** classe dimensionale insieme, per il capoluogo e per la provincia, 2018–2023. Quattro richieste in tutto, fissando il territorio invece del settore, ed è la tabella che ha chiuso MET-9. |

> ⚠️ **Su `turismo_province.csv` ci sono tre trappole, tutte marcate nella
> colonna `stato`.**
>
> 1. **Il 2025 non si confronta con gli anni prima** (`definizione_cambiata`).
>    Da quell'anno la voce «alloggi in affitto» comprende anche la gestione non
>    imprenditoriale: sull'Italia +87,6 % in dodici mesi, e il totale ne guadagna
>    il 14,9 %. Non è un boom, è una definizione. Riguarda tre tipologie —
>    `alloggi in affitto`, `extra-alberghiero` che la contiene e `totale`;
>    alberghiero e campeggi restano confrontabili.
> 2. **La Sardegna cambia geografia nel 2017** (`confine_cambiato`). Quattro
>    province soppresse: sulle superstiti una crescita 2008–2024 è una crescita
>    di superficie.
> 3. **Le due fonti sul turismo non danno lo stesso numero, e la differenza
>    cresce** (MET-17). La somma dei comuni di `turismo_comuni_annuale.csv` sta
>    sopra il totale provinciale ISTAT del 6,5 % nel 2019 e del 10,6 % nel 2024.
>    Sono due rilevazioni dello stesso fenomeno: si usa una tabella per volta, e
>    non si mescolano nella stessa frase senza dichiararlo.

> ⚠️ Su `imprese_sezioni_comuni.csv`: **una sezione assente resta assente.** ASIA
> non pubblica la sezione di un comune quando la cella è troppo piccola, e
> «nessun addetto nella manifattura» è un'affermazione diversa da «non lo
> sappiamo». Il denominatore delle quote è il totale ASIA riportato, non la somma
> delle sezioni: la decisione sta in `analysis/_tabelle.py` (`quote_sezioni`), una
> volta sola (MET-13).


### Commercio estero

| File | Righe | Contenuto |
|---|---|---|
| `commercio_estero_lombardia.csv` | 691 | Import ed export della **Lombardia** per raggruppamento merceologico, 1991–2025. |

> ⚠️ **Grana regionale, ed è un ripiego dichiarato.** Il dato provinciale non è
> accessibile via API (vedi [`../FONTI.md`](../FONTI.md) §1-ter). Brescia è la
> seconda provincia manifatturiera lombarda: la serie regionale è un contesto
> onesto, non un sostituto del dato provinciale, e va etichettata come tale in
> qualsiasi grafico.
