# Brescia Dataviz

Progetto di data visualization sull'evoluzione
di **Brescia** — il comune (ISTAT `017029`), la **provincia** (`ITC47`) e i suoi
**205 comuni** — modellato sull'architettura di `donostia-dataviz` ma con una
domanda di ricerca diversa: *come è cambiato questo territorio*, senza una tesi
turistica a monte.

**Stato: ricognizione completata, pipeline funzionante, dati scaricati e
puliti.** Manca la parte di analisi e visualizzazione: il piano sta in
[`PROSSIMI-PASSI.md`](PROSSIMI-PASSI.md).

## I documenti

| Documento | Cos'è |
|---|---|
| [`BRIEF.md`](BRIEF.md) | Il brief: la domanda, le unità di analisi, i tredici assi tematici ordinati per qualità del dato, le storie candidate, i principi. |
| [`FONTI.md`](FONTI.md) | **Il registro delle fonti.** Per ogni fonte: endpoint, grana geografica e temporale, copertura, licenza e stato di accesso verificato. In coda: la nota tecnica sull'SDMX di ISTAT (§10), le **ricette copiabili già collaudate** (§11) e cosa portarsi dietro in caso di repo separato (§12). |
| [`PROSSIMI-PASSI.md`](PROSSIMI-PASSI.md) | **La consegna.** Come separare il repository, cosa resta da scaricare, le decisioni aperte, le dimensioni non ancora considerate, e — soprattutto — come si costruiscono l'analisi, il sito statico e il deploy. Scritto per essere autosufficiente in un repo nuovo. |
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
prezzi di offerta; e il **commercio estero** è disponibile solo a grana
regionale, come ripiego dichiarato.

Dettagli, prove e tabella completa di raggiungibilità in [`FONTI.md`](FONTI.md).
Se lavori con l'SDMX di ISTAT, leggi prima la nota tecnica in fondo a quel
documento: un parametro sbagliato fa sembrare vuoti dataset che sono pieni.
