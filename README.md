# Brescia Dataviz

Progetto di data visualization sull'evoluzione del **bresciano**: soggetto la
**provincia di Brescia** (`ITC47`) raccontata attraverso i suoi **205 comuni**,
con il capoluogo (`017029`) come caso privilegiato. Modellato sull'architettura
di `donostia-dataviz` ma con una domanda di ricerca diversa: *come è cambiato
questo territorio*, senza una tesi turistica a monte.

**Stato: ricognizione completata, pipeline funzionante, dati scaricati e
puliti.** Manca la parte di analisi e visualizzazione: il piano sta in
[`PROSSIMI-PASSI.md`](PROSSIMI-PASSI.md).

## I documenti

| Documento | Cos'è |
|---|---|
| [`BRIEF.md`](BRIEF.md) | Il brief: la domanda, il soggetto e i **quattro assi scelti**, le due analisi dedicate al capoluogo, le storie candidate, i principi. |
| [`FONTI.md`](FONTI.md) | **Il registro delle fonti.** Per ogni fonte: endpoint, grana geografica e temporale, copertura, licenza e stato di accesso verificato. In coda: la nota tecnica sull'SDMX di ISTAT (§10), le **ricette copiabili già collaudate** (§11) e cosa portarsi dietro in caso di repo separato (§12). |
| [`METODOLOGIA.md`](METODOLOGIA.md) | ⚠️ **Bozza.** Le undici regole che governano il progetto: perché misuriamo come misuriamo. MET-9 nasce da un errore reale. Da completare a fine progetto. |
| [`WORKING-PAPER.md`](WORKING-PAPER.md) | ⚠️ **Bozza.** Il working paper: metodo per un lettore esterno. La sezione dei risultati è provvisoria — si riscrive quando le storie saranno chiuse. |
| [`PROSSIMI-PASSI.md`](PROSSIMI-PASSI.md) | **La consegna.** Come separare il repository, cosa resta da scaricare, le decisioni prese e quelle aperte, le dimensioni non ancora considerate, e — soprattutto — come si costruiscono l'analisi, il sito statico e il deploy. Scritto per essere autosufficiente in un repo nuovo. |
| [`pipeline/`](pipeline/README.md) | **La pipeline**: da fonti pubbliche a tabelle tidy. `requests` e libreria standard, niente build step, niente chiavi API. |
| [`dati/`](dati/README.md) | **Le tabelle prodotte**: 16 CSV su territorio, imprese, lavoro, popolazione, redditi, ambiente, sicurezza e turismo. Versionate; le risposte grezze no. |

## Come leggere il registro

Ogni riga di `FONTI.md` porta uno **stato di accesso**. Le righe marcate
`verificata ✓` sono state interrogate realmente durante la ricognizione
(agosto 2026) e portano la prova sotto forma di conteggi, ID di dataset e date;
le altre dichiarano perché non lo sono: login richiesto, host non raggiungibile
da questo ambiente, dato solo in PDF, o semplicemente non ancora testata.

Questa distinzione è il punto del documento. Serve a non ritrovarsi, a
pipeline mezza costruita, davanti a una fonte che sulla carta esisteva.

## In sintesi

Il baricentro del progetto è **economico e sociale**: lavoro e struttura
produttiva, chi ci vive e da dove viene, redditi, aria e clima.

Il ritrovamento principale è il **Censimento permanente ISTAT via SDMX**: una
famiglia di tabelle `DF_DCSS_*` con grana **comunale e annuale** (non decennale)
che copre occupazione per settore e posizione professionale, titolo di studio
per cittadinanza, pendolarismo, background migratorio — inclusa la distinzione
fra stranieri, seconde generazioni e italiani per acquisizione — abitazioni per
titolo di godimento e persino la **percezione della sicurezza a livello di
città**. Accanto, il registro **ASIA** dà unità locali e addetti per classe
dimensionale e settore, per **tutti i comuni**, 2018–2023: è la fonte che
risponde direttamente alla domanda se questo sia ancora un territorio di
microimprese.

Il secondo canale è **`dati.lombardia.it`** (API Socrata aperta, senza chiave):
trent'anni di qualità dell'aria su stazioni georeferenziate in tutta la
provincia, il clima dal 1990, e i flussi turistici per comune. Il terzo sono i
**confini e le variabili censuarie ISTAT**, che danno la base geografica dei
comuni e, sotto, la grana di sezione di censimento per gli assi dove serve.

**Soggetto e assi sono decisi** (agosto 2026): la provincia attraverso i 205
comuni, il capoluogo come caso privilegiato, e quattro assi portanti — lavoro e
imprese, chi vive nel bresciano, le due economie (manifattura e Garda), aria e
clima. Il resto resta materiale di contorno. Dettaglio in
[`BRIEF.md`](BRIEF.md).

Il confronto città/provincia è la cosa più informativa emersa: fra 2018 e 2023
la provincia guadagna 29 mila addetti mentre la città è ferma. Attenzione però
al titolo facile — il crollo delle grandi unità locali del capoluogo, scomposto
per settore, è quasi tutto somministrazione di lavoro e servizi esternalizzati,
non industria: la manifattura grande non si muove. È il caso che ha dato
origine alla regola MET-9 e sta in [`WORKING-PAPER.md`](WORKING-PAPER.md) §6.1.

Sul turismo l'asimmetria è più netta e più semplice: 12,2 milioni di presenze
provinciali nel 2024, di cui il 68,8 % nei primi dieci comuni, otto dei quali
sul Garda — Sirmione da sola fa più del capoluogo.

Limiti da mettere in conto: i **reati** esistono solo a grana provinciale (la
percezione arriva al comune ma solo dal 2022); **nessuna copertura Inside
Airbnb**; i **prezzi delle case** sono dietro un login gratuito (OMI) o sono
prezzi di offerta; e il **commercio estero** è disponibile solo a grana
regionale, come ripiego dichiarato.

Dettagli, prove e tabella completa di raggiungibilità in [`FONTI.md`](FONTI.md).
Se lavori con l'SDMX di ISTAT, leggi prima la nota tecnica in fondo a quel
documento: un parametro sbagliato fa sembrare vuoti dataset che sono pieni.
