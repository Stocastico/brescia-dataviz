# Brescia Dataviz

Progetto di data visualization sull'evoluzione del **bresciano**: soggetto la
**provincia di Brescia** (`ITC47`) raccontata attraverso i suoi **205 comuni**,
con il capoluogo (`017029`) come caso privilegiato. Modellato sull'architettura
di `donostia-dataviz` ma con una domanda di ricerca diversa: *come è cambiato
questo territorio*, senza una tesi turistica a monte.

**Stato: il sito esiste.** Dati scaricati e puliti, dieci analisi fatte, cinque
storie scritte in un documento narrativo autocontenuto
([`sito/`](sito/README.md)) che si costruisce da solo e ha già il suo workflow
di pubblicazione. Quello che manca per pubblicare non è più tecnico: **una
licenza da scegliere, una rilettura dei testi e un clic nelle impostazioni del
repository**. Tutto il resto è facoltativo, ed è elencato in
[`PROSSIMI-PASSI.md`](PROSSIMI-PASSI.md), che distingue riga per riga **cosa può
fare una sessione di lavoro e cosa richiede te**.

## I documenti

| Documento | Cos'è |
|---|---|
| [`BRIEF.md`](BRIEF.md) | Il brief: la domanda, il soggetto e i **quattro assi scelti**, le due analisi dedicate al capoluogo, le storie candidate, i principi. |
| [`FONTI.md`](FONTI.md) | **Il registro delle fonti.** Per ogni fonte: endpoint, grana geografica e temporale, copertura, licenza e stato di accesso verificato. In coda: la nota tecnica sull'SDMX di ISTAT (§10), le **ricette copiabili già collaudate** (§11) e la traccia storica della separazione del repository (§12). |
| [`METODOLOGIA.md`](METODOLOGIA.md) | ⚠️ **Bozza avanzata.** Le **quattordici** regole che governano il progetto: perché misuriamo come misuriamo. Quattro nascono da errori veri trovati sui dati — MET-9 (un titolo sbagliato), MET-12 (una correlazione con il segno rovesciato), MET-13 (due script che rispondevano numeri diversi alla stessa domanda) e MET-14 (una frase che questo progetto ripeteva dal primo giorno e che il confronto con le altre province ha smontato). |
| [`WORKING-PAPER.md`](WORKING-PAPER.md) | ⚠️ **Bozza.** Il working paper: metodo per un lettore esterno. La sezione dei risultati è provvisoria — si riscrive quando le storie saranno chiuse. |
| [`PROSSIMI-PASSI.md`](PROSSIMI-PASSI.md) | **Cosa resta da fare, e chi lo può fare.** Lo stato in una pagina, cosa manca da scaricare, le decisioni aperte, come si costruiscono analisi, sito statico e deploy — e in testa l'elenco delle cose che **richiedono te** (una licenza da scegliere, un login SPID, una macchina italiana), con una stima dei tempi. |
| [`pipeline/`](pipeline/README.md) | **La pipeline**: da fonti pubbliche a tabelle tidy. `requests` e libreria standard, niente build step, niente chiavi API. |
| [`dati/`](dati/README.md) | **Le tabelle prodotte**: 23 CSV su territorio, imprese, lavoro, popolazione, famiglie e abitazioni, redditi, ambiente, sicurezza e turismo, più i **confini dei 205 comuni** in GeoJSON. Versionati; le risposte grezze no. |
| [`analysis/`](analysis/README.md) | **Le letture delle tabelle**: uno script per analisi, libreria standard soltanto. Comprende `verifica_cifre.py`, che ricalcola dai dati **ogni cifra citata** in questi documenti e nel sito. |
| [`sito/`](sito/README.md) | **Il documento narrativo**: cinque storie in un unico file HTML autocontenuto, con mappe e grafici in SVG disegnati a mano. Nessuna cifra del testo è scritta a mano: sono segnaposto calcolati in fase di costruzione. |

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
la provincia guadagna 29 mila addetti mentre la città è ferma. Il titolo facile
— «la grande industria se ne va dalla città» — è **falso, e ora si può
dimostrare**: la manifattura grande del capoluogo perde 51 addetti su 4.448,
cioè non si muove, e tutto il calo sta in due divisioni di servizi che non hanno
perso lavoro ma cambiato forma (i servizi per edifici si frammentano in 157
unità locali in più) o comune (la somministrazione esce dalla città ma resta in
provincia). È MET-9, che era la questione aperta più importante del progetto ed
è chiusa.

Le altre storie del sito: **93 comuni su 205 perdono abitanti**, e non sono
sparsi a caso ma contigui, tutta la montagna; i **redditi convergono** — chi
partiva sotto cresce più in fretta, correlazione −0,45 — anche se il comune più
ricco dichiara ancora 2,5 volte il più povero, ed era 2,2 undici anni prima; e
la provincia è **davvero due economie**, con la manifattura nelle valli e nella
Bassa e l'alloggio sul Garda, divise così nettamente che la specializzazione
settoriale (Moran 0,44) è la variabile economica più raggruppata nello spazio
fra quelle misurate — dietro solo alla densità abitativa, che però è geografia,
non economia.

**La quinta storia corregge le altre**, e vale la pena leggerla per prima: fino
a poco fa questo progetto misurava Brescia solo contro sé stessa, e ripeteva che
è «un territorio di microimprese». Confrontata con le altre 106 province, Brescia
è la **101ª per frammentazione**, cioè fra le meno frammentate d'Italia: il
92,7 % di unità locali sotto i dieci addetti descrive il paese, non questa
provincia. Quello che la distingue è il settore — 15ª d'Italia per quota
manifatturiera — non la dimensione. E il confronto ha anche rafforzato MET-9: la
classe con almeno 250 addetti si è svuotata in 44 capoluoghi su 64, con una
mediana del −11,9 %.

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
documento: un parametro sbagliato fa sembrare vuoti dataset che sono pieni — e
il riquadro in `PROSSIMI-PASSI.md` §2.1 spiega come ottenere gli incroci che
sembravano impossibili, che è il modo in cui sono arrivate le due tabelle
migliori del progetto.

## Come si rifà tutto

```bash
pip install -e ./pipeline
python -m brescia_pipeline.build          # da zero: scarica e pulisce (ore)
python -m brescia_pipeline.build --offline web   # solo i JSON per il sito (secondi)
python sito/costruisci.py                 # -> _site/
python analysis/verifica_cifre.py         # se una cifra diverge, è quello il primo problema
```
