# Brescia Dataviz

Ricognizione preliminare per un progetto di data visualization sull'evoluzione
di **Brescia** — il comune (ISTAT `017029`), la **provincia** (`ITC47`) e i suoi
**205 comuni** — modellato sull'architettura di `donostia-dataviz` ma con una
domanda di ricerca diversa: *come è cambiato questo territorio*, senza una tesi
turistica a monte.

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
dimensionale e settore, per **tutti i comuni**, 2018–2023: è la fonte che
risponde direttamente alla domanda se questo sia ancora un territorio di
microimprese.

Il secondo canale è **`dati.lombardia.it`** (API Socrata aperta, senza chiave):
trent'anni di qualità dell'aria su stazioni georeferenziate in tutta la
provincia, il clima dal 1990, e i flussi turistici per comune. Il terzo sono i
**confini e le variabili censuarie ISTAT**, che danno la base geografica dei
comuni e, sotto, la grana di sezione di censimento per gli assi dove serve.

L'unità di analisi è il **comune**, con la **provincia** come aggregato e i
**205 comuni** come dettaglio interno: quasi tutte queste fonti coprono tutti i
comuni italiani, quindi la coropletica si sposta dai quartieri della città al
territorio provinciale — molto più eterogeneo (Garda, Val Trompia, Franciacorta,
Bassa, Valle Camonica).

Il confronto città/provincia è già la cosa più informativa emersa: fra 2018 e
2023 la provincia guadagna 29 mila addetti mentre la città è ferma, e le unità
locali con almeno 250 addetti crollano in città (35 → 28) ma tengono in
provincia (75 → 82). Sul turismo l'asimmetria è ancora più netta: 12,2 milioni
di presenze provinciali nel 2024, di cui il 68,8 % nei primi dieci comuni, otto
dei quali sul Garda — Sirmione da sola fa più del capoluogo.

Limiti da mettere in conto: i **reati** esistono solo a grana provinciale (la
percezione arriva al comune ma solo dal 2022); **nessuna copertura Inside
Airbnb**; i **prezzi delle case** sono dietro un login gratuito (OMI) o sono
prezzi di offerta; e il **commercio estero provinciale** è l'unico asse
importante ancora da verificare.

Dettagli, prove e tabella completa di raggiungibilità in [`FONTI.md`](FONTI.md).
Se lavori con l'SDMX di ISTAT, leggi prima la nota tecnica in fondo a quel
documento: un parametro sbagliato fa sembrare vuoti dataset che sono pieni.
