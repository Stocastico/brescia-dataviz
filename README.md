# Brescia Dataviz

Progetto di data visualization sull'evoluzione del **bresciano**: soggetto la
**provincia di Brescia** (`ITC47`) raccontata attraverso i suoi **205 comuni**,
con il capoluogo (`017029`) come caso privilegiato. Modellato su
[`donostia-dataviz`](https://github.com/Stocastico/donostia-dataviz) — di cui
riprende architettura, metodo e lingua grafica — ma con una domanda di ricerca
diversa: *come è cambiato questo territorio*, senza una tesi turistica a
monte.

**Stato: tutti e quattro gli assi portanti hanno la loro storia.** Dati
scaricati e puliti, tredici analisi fatte, sei storie scritte in un documento
narrativo autocontenuto ([`sito/`](sito/README.md)) che si costruisce da solo e
ha già il suo workflow di pubblicazione. La licenza è scelta (MIT per il codice,
CC BY 4.0 per testi e dati: vedi in fondo).

**Quello che manca non è più tecnico, e sta tutto qui:**

| | Cosa | Tempo |
|---|---|---|
| 🙋 | **Rileggere i testi del sito** — sono sei storie, e nessuno script controlla se una frase dice più di quanto il dato sostenga | 1 h |
| 🙋 | **Mettere la sorgente di Pages su «GitHub Actions»** (*Settings → Pages → Source*): oggi è ancora «Deploy from a branch», ed è il motivo per cui l'indirizzo pubblico mostra questo README invece del racconto | 2 min |
| 🙋 | **Pubblicare**, quando sarai pronto: *Actions → «Pubblica il sito» → Run workflow → conferma = `pubblica`* | 1 min |
| 🙋 | **Decidere sul sesto colore di storia** — le storie sono sei e i colori ereditati da `donostia-dataviz` sono cinque, quindi ne è stato aggiunto uno. Riguarda la lingua grafica condivisa fra i due progetti: [`sito/README.md`](sito/README.md) §Lo stile. Non blocca niente | 10 min |

**Il sito non si pubblica da solo**, ed è voluto finché l'analisi non è finita:
ogni push su `main` lo ricostruisce e lo verifica lasciandolo come artefatto da
scaricare, ma per mandarlo online serve quel lancio a mano con la conferma
scritta. Tutto il resto è facoltativo — i download che richiedono SPID o una
macchina italiana, il pannello interattivo, il turismo confrontato con le altre
province — ed è elencato in [`PROSSIMI-PASSI.md`](PROSSIMI-PASSI.md), che
distingue riga per riga **cosa può fare una sessione di lavoro e cosa richiede
te**.

## I documenti

| Documento | Cos'è |
|---|---|
| [`BRIEF.md`](BRIEF.md) | Il brief: la domanda, il soggetto e i **quattro assi scelti** — tutti e quattro ora hanno una storia —, le due analisi dedicate al capoluogo, le storie candidate, i principi. |
| [`FONTI.md`](FONTI.md) | **Il registro delle fonti.** Per ogni fonte: endpoint, grana geografica e temporale, copertura, licenza e stato di accesso verificato. In coda: la nota tecnica sull'SDMX di ISTAT (§10), le **ricette copiabili già collaudate** (§11) e la traccia storica della separazione del repository (§12). |
| [`METODOLOGIA.md`](METODOLOGIA.md) | ⚠️ **Bozza avanzata.** Le **sedici** regole che governano il progetto: perché misuriamo come misuriamo. Cinque nascono da errori veri trovati sui dati — MET-9 (un titolo sbagliato), MET-12 (una correlazione con il segno rovesciato), MET-13 (due script che rispondevano numeri diversi alla stessa domanda), MET-14 (una frase che questo progetto ripeteva dal primo giorno e che il confronto con le altre province ha smontato) e MET-15 (una parola — «spopolamento» — che conteneva già una risposta, e quella sbagliata). La sedicesima è la prima nata da un errore *evitato*: su una rete di centraline che apre e chiude stazioni, la media misura anche la rete. |
| [`WORKING-PAPER.md`](WORKING-PAPER.md) | ⚠️ **Bozza, versione 2.** Il working paper: metodo per un lettore esterno. La §7 non è più provvisoria — copre tutti e quattro gli assi, con i controlli e i due assi che un termine di paragone esterno non ce l'hanno. Restano provvisori il titolo e la §5. |
| [`PROSSIMI-PASSI.md`](PROSSIMI-PASSI.md) | **Cosa resta da fare, e chi lo può fare.** Lo stato in una pagina, cosa manca da scaricare, le decisioni aperte, come si costruiscono analisi, sito statico e deploy — e in testa l'elenco completo delle cose che **richiedono te** (un login SPID, una macchina italiana, una decisione di disegno), con una stima dei tempi. |
| [`pipeline/`](pipeline/README.md) | **La pipeline**: da fonti pubbliche a tabelle tidy. `requests` e libreria standard, niente build step, niente chiavi API. |
| [`dati/`](dati/README.md) | **Le tabelle prodotte**: 26 CSV su territorio, imprese, lavoro, popolazione e bilancio demografico, famiglie e abitazioni, redditi, ambiente, sicurezza e turismo, più le tabelle di confronto con le altre 106 province e i **confini dei 205 comuni** in GeoJSON. Versionati; le risposte grezze no. |
| [`analysis/`](analysis/README.md) | **Le letture delle tabelle**: tredici script, uno per analisi, libreria standard soltanto. Comprende `verifica_cifre.py`, che ricalcola dai dati **ogni cifra citata** in questi documenti e nel sito. |
| [`sito/`](sito/README.md) | **Il documento narrativo**: sei storie in un unico file HTML autocontenuto, con mappe e grafici in SVG disegnati a mano e la lingua grafica del progetto gemello `donostia-dataviz`. Nessuna cifra del testo è scritta a mano: sono segnaposto calcolati in fase di costruzione. |

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

Il quarto è arrivato per ultimo e vale quanto il primo: **`demo.istat.it`**, che
è un altro sito di ISTAT e un'altra logica — niente SDMX, un CSV zippato per
anno. La tavola **D7B** porta il **bilancio demografico mensile** di tutti i
comuni italiani, cioè nascite, morti, iscrizioni e cancellazioni: l'unica fonte
del progetto che *spiega* la popolazione invece di misurarla. È il caso più
netto di una lezione che vale la pena tenere: per mesi «ISTAT» aveva voluto dire
`esploradati.istat.it`, e la fonte che mancava non mancava.

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
sparsi a caso ma contigui, tutta la montagna — ma **non perché la gente se ne
vada**: scomposta con il bilancio demografico, la migrazione interna di quei 93
comuni sommata vale −66 persone in sei anni, contro −10.163 di saldo naturale.
Non se ne va nessuno, ci si muore. Lo stesso vale un livello sopra: la provincia
guadagna 11.465 abitanti solo perché ne arrivano 27.817 dall'estero, e senza
quella componente ne perderebbe 16.352. È MET-15, ed è il secondo caso in cui un
titolo dato prima di decomporre si è rivelato sbagliato. Fra le 107 province
Brescia è comunque la **6ª per crescita**, in un paese dove il saldo naturale è
positivo in una sola. Poi: i **redditi convergono** — chi
partiva sotto cresce più in fretta, correlazione −0,45, e lo stesso conto su
Bergamo dà −0,48, quindi non è una specialità locale — anche se mentre il grosso
dei comuni si avvicina i due estremi si allontanano; e
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

**La sesta storia dura vent'anni**, che è tre volte il resto del progetto, e
dice due cose opposte. L'aria è **molto** migliorata: tenendo solo le centraline
osservate in tutti gli anni della serie — perché la rete apre e chiude stazioni,
e mediare quelle che ci sono ogni anno misura anche il cambio della rete — il
PM10 fa **−42,0 %** e il biossido di azoto **−38,9 %**. Sono i cali più grandi
misurati in tutto il lavoro. L'**ozono** però non si muove, −1,8 %: non è un
inquinante primario, non esce da un camino, e la sua chimica non risponde alle
stesse leve. Il clima intanto va nell'altra direzione: fra la base 2004–2013 e
il decennio 2016–2025 le stazioni bresciane segnano **+1,10 °C**, e salgono
**tutte e otto**, dai 47 metri della Bassa ai 2.108 del Pantano d'Avio. La
pioggia, dalla stessa fonte e con lo stesso metodo, **non dà segnale** — mediana
+0,5 %, sette stazioni in aumento e cinque in calo — e resta nel racconto proprio
per questo: due serie della stessa rete, una con un segnale netto e una senza,
sono anche la prova che il segnale della prima non lo ha fabbricato il metodo.
Nessuna di queste variazioni è attribuita a una causa: la meteorologia governa la
dispersione degli inquinanti quanto le emissioni.

Limiti da mettere in conto: l'aria e il clima si misurano **dove c'è una
centralina**, e in 194 comuni su 205 non ce n'è mai stata nessuna; i **reati**
esistono solo a grana provinciale (la
percezione arriva al comune ma solo dal 2022); **nessuna copertura Inside
Airbnb**; i **prezzi delle case** sono dietro un login gratuito (OMI) o sono
prezzi di offerta; il **commercio estero** è disponibile solo a grana regionale,
come ripiego dichiarato; e il bilancio demografico dice **quanti** entrano ed
escono da ogni comune, non **da dove a dove** — «chi lascia la Valle Camonica
scende in città» resta una frase che questi dati non sostengono.

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

## Licenza

Due licenze, perché le due metà del progetto vivono di regole diverse:

| Cosa | Licenza |
|---|---|
| **Il codice** — `pipeline/`, `analysis/`, `sito/costruisci.py`, i grafici in `sito/modelli/grafici.js` | [MIT](LICENSE) |
| **I testi e i dati** — i documenti `.md`, il testo del sito, le tabelle in `dati/` e i JSON in `web/src/data/` | [CC BY 4.0](LICENSE-DATI) |

CC BY 4.0 è la più permissiva fra le licenze Creative Commons che chiedono
l'attribuzione: si copia, si modifica e si riusa anche commercialmente,
citando la fonte. Attribuzione consigliata: «Brescia Dataviz» di Stefano
Masneri (CC BY 4.0), <https://github.com/Stocastico/brescia-dataviz>.

Le fonti originali mantengono i propri obblighi di citazione — ISTAT e Regione
Lombardia in CC BY, ARPA Lombardia, MEF — e sono elencate fonte per fonte in
[`FONTI.md`](FONTI.md). Aggiungere un giorno dati OpenStreetMap o OpenPNRR
(ODbL, share-alike sui derivati) obbligherebbe a rifare questa scelta:
[`PROSSIMI-PASSI.md`](PROSSIMI-PASSI.md) §3.3.
