# Dati

Tre cartelle:

- **`processed/`** — le tabelle tidy, **versionate**: sono il prodotto del
  progetto. Circa 8 MB in tutto.
- **`geo/`** — la geometria di riferimento, **versionata**: i confini dei 205
  comuni in GeoJSON (320 KB). È la base di ogni coropletica.
- **`raw/`** — le risposte grezze delle fonti, **non versionate** (centinaia di
  MB) e rigenerabili con `python -m brescia_pipeline.build` da
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
| `redditi_comuni.csv` | 36.952 | Contribuenti e reddito complessivo per **classe di importo** (8 classi, da «≤ 0 €» a «oltre 120.000 €»), per comune, 2012–2023. Dà la distribuzione, non solo la media: è ciò che serve per parlare di disuguaglianza. |

### Chi vive nel bresciano — ⏳ pipeline pronta, tabelle non ancora prodotte

| File | Contenuto |
|---|---|
| `migrazioni_comuni.csv` | Background migratorio per comune: **stranieri immigrati**, **stranieri nati in Italia** e **italiani per acquisizione**, per sesso, età, cittadinanza, luogo di nascita dei genitori e titolo di studio. Dieci tavole censuarie in una tabella, distinte dalla colonna `tavola`. |
| `abitazioni_comuni.csv` | Abitazioni occupate e non occupate, e quelle occupate per **proprietà, affitto, altro titolo**. È la risposta a «quante case in affitto» che non passa per i prezzi. |
| `famiglie_comuni.csv` | Famiglie per numero di componenti, con **almeno uno** o **tutti** i componenti stranieri. Le due situazioni restano separate come le tiene la fonte. |

> Il codice c'è ed è testato sul parsing; manca solo lo scarico, che non è mai
> andato a buon fine perché `esploradati.istat.it` ha smesso di accettare
> connessioni (agosto 2026). Si producono con
> `python -m brescia_pipeline.build migrazioni abitazioni famiglie`.
>
> A differenza di `censimento_lavoro_brescia.csv`, queste tabelle tengono
> **una riga per osservazione con tutte le dimensioni in colonna**: dentro
> ciascuna famiglia le dimensioni sono fisse, e appiattirle distruggerebbe la
> distribuzione congiunta — che è l'informazione per cui valgono la pena.

### Ambiente

| File | Righe | Contenuto |
|---|---|---|
| `stazioni_arpa.csv` | 323 | Anagrafica dei sensori ARPA della provincia (aria e meteo) con coordinate, quota e date di attivazione. |
| `aria_mensile.csv` | 15.463 | Medie mensili per sensore: PM10, PM2.5, NO₂, ozono e altri, dal 2000 al 2026. Aggregate lato server: le serie orarie grezze sono decine di milioni di righe. |
| `meteo_mensile.csv` | 10.415 | Medie mensili di temperatura, precipitazione, umidità e vento, dal 1990. |

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

⚠️ Due avvertenze specifiche, entrambe già costate un errore:

1. **Filtrare su `tipo_struttura = 'Totale'` *e* `cittadinanza = 'Totale'`.** Le
   righe esistono per ogni combinazione, totali inclusi: sommare senza filtrare
   conta fino a tre volte le stesse notti.
2. **Guardare la colonna `stato`.** Vale `osservato`, `riservato` (dato
   soppresso dalla fonte per riservatezza statistica: la cella è vuota) oppure
   `zero_fittizio` — la riga «Totale» dichiara 0 ma tutte le sue componenti
   sono soppresse, quindi lo zero è calcolato su celle vuote, non misurato.
   Riguarda un solo comune (Gottolengo, 2024) e va escluso dai grafici, non
   disegnato come «nessun turismo».

### Commercio estero

| File | Righe | Contenuto |
|---|---|---|
| `commercio_estero_lombardia.csv` | 691 | Import ed export della **Lombardia** per raggruppamento merceologico, 1991–2025. |

> ⚠️ **Grana regionale, ed è un ripiego dichiarato.** Il dato provinciale non è
> accessibile via API (vedi [`../FONTI.md`](../FONTI.md) §1-ter). Brescia è la
> seconda provincia manifatturiera lombarda: la serie regionale è un contesto
> onesto, non un sostituto del dato provinciale, e va etichettata come tale in
> qualsiasi grafico.
