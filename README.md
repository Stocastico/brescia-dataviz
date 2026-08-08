# Brescia Dataviz

Ricognizione preliminare per un progetto di data visualization sull'evoluzione
della città di **Brescia** (comune ISTAT 017029), modellato sull'architettura di
`donostia-dataviz` ma con una domanda di ricerca diversa: *come è cambiata la
città*, senza una tesi turistica a monte.

**Stato: solo documentazione.** Nessun codice, nessuna pipeline, nessun dato
scaricato. Questa cartella contiene il lavoro che nel progetto Donostia
corrisponde a `docs/PROJECT-BRIEF-v2.md` + `docs/SOURCES.md` +
`datos/input/FUENTES.md`, cioè la fase che precede la pipeline.

## I documenti

| Documento | Cos'è |
|---|---|
| [`BRIEF.md`](BRIEF.md) | Il brief: la domanda, la geometria di riferimento, i dieci assi tematici ordinati per qualità del dato, le otto storie candidate, i principi. |
| [`FONTI.md`](FONTI.md) | **Il registro delle fonti.** Per ogni fonte: endpoint, grana geografica e temporale, copertura, licenza e stato di accesso verificato. Include la tabella di raggiungibilità dei portali e la sintesi di cosa è più forte e più debole rispetto a Donostia. |

## Come leggere il registro

Ogni riga di `FONTI.md` porta uno **stato di accesso**. Le righe marcate
`verificata ✓` sono state interrogate realmente durante la ricognizione
(agosto 2026) e portano la prova sotto forma di conteggi, ID di dataset e date;
le altre dichiarano perché non lo sono: login richiesto, host non raggiungibile
da questo ambiente, dato solo in PDF, o semplicemente non ancora testata.

Questa distinzione è il punto del documento. Serve a non ritrovarsi, a
pipeline mezza costruita, davanti a una fonte che sulla carta esisteva.

## In sintesi

Il baricentro del progetto è **economico e sociale, non turistico**: lavoro e
struttura produttiva, chi vive in città e da dove viene, studi, casa, aria.

Il ritrovamento principale è il **Censimento permanente ISTAT via SDMX**: una
famiglia di tabelle `DF_DCSS_*` con grana **comunale e annuale** (non decennale)
che copre occupazione per settore e posizione professionale, titolo di studio
per cittadinanza, pendolarismo, background migratorio — inclusa la distinzione
fra stranieri, seconde generazioni e italiani per acquisizione — abitazioni per
titolo di godimento e persino la **percezione della sicurezza a livello di
città**. Accanto, il registro **ASIA** dà unità locali e addetti per classe
dimensionale e settore, 2018–2023: è la fonte che risponde direttamente alla
domanda se Brescia sia ancora una città di microimprese.

Il secondo canale è **`dati.lombardia.it`** (API Socrata aperta, senza chiave):
trent'anni di qualità dell'aria su cinque stazioni bresciane georeferenziate e
il clima dal 1990 su due stazioni. Il terzo sono le **basi territoriali e
variabili censuarie ISTAT**, che portano popolazione, istruzione, origini e
abitazioni a grana di sezione di censimento, aggregabile ai 33 quartieri.

Tre limiti da mettere in conto subito: **nessun dato aperto di criminalità per
quartiere** (percezione al massimo comunale e solo dal 2022, reati provinciali);
**nessuna copertura Inside Airbnb per Brescia**; e **molti assi si fermano al
comune**, quindi buona parte del progetto sarà fatta di serie temporali e
scomposizioni, non di mappe.

Il collo di bottiglia resta **`dati.comune.brescia.it`**, che da questo ambiente
non risponde: ci stanno i pezzi più preziosi, in particolare l'indirizzario che
lega indirizzo → sezione di censimento → quartiere → zona, e che è ciò che rende
esatta l'aggregazione del censimento sui quartieri.

Dettagli, prove e tabella completa di raggiungibilità in [`FONTI.md`](FONTI.md).
Se lavori con l'SDMX di ISTAT, leggi prima la nota tecnica in fondo a quel
documento: un parametro sbagliato fa sembrare vuoti dataset che sono pieni.
