# sito

Il documento narrativo e le sue pagine sorelle. Si costruisce con

```bash
python -m brescia_pipeline.build web    # i JSON, da dati/processed/
python sito/costruisci.py               # -> _site/
```

e il risultato è **un file HTML che sta in piedi da solo**: dati incorporati,
stile e grafici in linea, nessuna `fetch()`, nessuna CDN, nessuna chiave. Si
apre da disco, si manda per email, si archivia.

| File | Cos'è |
|---|---|
| `costruisci.py` | assembla `_site/`: incorpora i dati, sostituisce le cifre e le date, copia i CSV |
| `modelli/racconto.html` | il documento narrativo: otto storie e la sezione dei limiti |
| `modelli/esplora.html` | lo strumento: i diciannove indicatori su tutti i comuni, a scelta di chi legge |
| `modelli/metodologia.html` | le regole del progetto, per un lettore che non ha letto il repository |
| `modelli/dati.html` | fonti, tabelle scaricabili e avvertenze |
| `modelli/stile.css` | la tavolozza e l'impaginazione, in variabili CSS |
| `modelli/grafici.js` | mappe, dispersioni, serie e barre in SVG, senza librerie |

## Le tre regole che tengono in piedi tutto il resto

**Nessun numero è scritto a mano.** Nel testo dei modelli le cifre sono
segnaposto `{{c:nome}}`; `costruisci.py` li calcola dalle tabelle e li
sostituisce. Se un segnaposto non trova il suo valore la costruzione **fallisce**
invece di pubblicare una frase con un buco. Aggiungere una frase con un numero
significa aggiungere una voce alla funzione `cifre()`.

**Nessuna dipendenza a runtime.** I grafici sono SVG disegnati a mano in
JavaScript. Costa più codice e in cambio il documento non invecchia: fra dieci
anni non ci sarà una libreria da aggiornare né una CDN da cui dipendere.

**Ogni grafico ha una tabella-specchio.** Sotto ogni mappa e ogni grafico c'è un
`<details>` con gli stessi numeri, navigabile da tastiera e da lettore di
schermo. Una coropletica da sola è inaccessibile, e la tabella serve anche a chi
vuole controllare.

## Lo scrollytelling, e quando vale la pena

Due storie su otto ce l'hanno, e non è una svista: costa attenzione al lettore,
e la si spende dove una figura va **letta più volte**.

- La **prima** (`#svuota`) tiene ferma una mappa e la rilegge cinque volte:
  tutti i comuni, quelli in calo, le dieci cadute peggiori, i grumi, il verso
  opposto. La figura non cambia mai, cambia cosa è acceso (`mappa.evidenzia`).
- L'**ottava** (`#casa`) fa una cosa diversa perché ha un argomento a catena: il
  prezzo com'è scritto → lo stesso prezzo in euro di oggi → il divario → i
  volumi. I passi accendono le linee una alla volta (`serie().mostra`), e negli
  ultimi due il pannello **scambia figura**.

Tre vincoli che valgono per entrambe, e che il prossimo scrollytelling deve
rispettare:

1. **La scala non si ricalcola** quando una linea si accende. Se si adattasse,
   aggiungere una linea farebbe muovere anche quella già disegnata, e un lettore
   che vede due curve cambiare forma insieme non sa più quale sia la notizia. È
   il motivo per cui il primo passo dell'ottava storia ha molto spazio vuoto
   sopra: è lo spazio in cui la seconda linea atterrerà.
2. **Il pannello non deve sobbalzare.** È `position: sticky`, quindi qualunque
   cosa ne cambi l'altezza (una didascalia che passa da due righe a tre) si vede
   come un sussulto accanto al testo che si legge. Le didascalie sono fisse per
   figura e lo spazio è prenotato in CSS.
3. **Spegnere è un'intenzione, non uno stato.** `mostra()` mette una *classe*,
   non un attributo `display`, e il CSS decide se quella classe conta.
   Sotto i 900 px lo scrollytelling non gira: le figure tornano tutte visibili
   e complete, i passi diventano paragrafi, e la storia si legge come si
   leggerebbe senza. Un grafico intitolato «con due righelli» che sul telefono
   ne disegna uno è il modo esatto in cui questa cosa si rompe in silenzio.

E una regola di misura: **due figure per pannello sono il massimo**. Allo
scambio il lettore deve accorgersi che il grafico è cambiato; con quattro non se
ne accorgerebbe più, e il pannello diventerebbe una diapositiva.

Le tabelle-specchio dell'ottava storia stanno **fuori** dal pannello
(`#tabelle-casa`, via l'opzione `tabellaIn` di `serie()`): la figura spenta è
`display:none`, e con lei sparirebbe dalla tastiera anche la sua tabella.

## Le due pagine che fanno cose diverse

`racconto.html` sceglie. Otto storie, quindici indicatori, e per ognuna una
figura tagliata su quella frase.

`esplora.html` non sceglie: tutti e diciannove gli indicatori del registro, su
tutti i comuni, e l'ordine lo decide chi legge. Le due pagine hanno lo stesso
peso e lo stesso stile, e non hanno lo stesso mestiere: la prima risponde a
domande che qualcuno ha già fatto, la seconda serve a farne di nuove.

**Non è l'app React della specifica** ([`PROSSIMI-PASSI.md`](../PROSSIMI-PASSI.md)
§6.1), ed è una differenza voluta. La specifica era stata copiata dal progetto
precedente, dove il pannello era servito a parte con React, Vite, maplibre e
recharts. Qui `grafici.js` ha già la coropletica, le due scale, la legenda, la
tabella-specchio e la riga di provenienza: seguire la specifica voleva dire
riscriverle in quattro dipendenze e aggiungere alla CI una catena di
costruzione Node che oggi non esiste. Quello che mancava davvero sono due menù
e il ritratto del comune, e sono centosessanta righe in fondo al modello. La
regola «nessuna dipendenza a runtime» vale anche per lo strumento.

Tre cose che la pagina fa e che vale la pena non rompere:

1. **L'elenco degli indicatori viene dal registro, non dal modello.**
   `metriche_esplora()` legge `web/src/data/metrics.json` e prende quelli
   `live`. Un indicatore nuovo compare nel menù senza che nessuno tocchi né il
   modello né il costruttore, ed è quello che rende vera la riga «aggiungere un
   dataset = un JSON in più e una riga nel registro».
2. **I dati incorporati sono due, non uno.** Le pagine del racconto portano i
   quindici indicatori che le storie citano; `esplora.html` e `dati.html` li
   portano tutti. Il resto (geometria, anagrafica, le serie delle figure) è
   calcolato una volta sola e condiviso.
3. **Ogni scelta sta nell'indirizzo**, e ci sta in tutte e due le direzioni:
   `#prezzo_case/2012/017068` è indicatore, anno e comune. La pagina lo scrive
   con `replaceState` (un menù che riempie la cronologia rende inutile il tasto
   «indietro») e lo rilegge anche quando cambia sotto una finestra già aperta.

## Lo stile viene da `donostia-dataviz`

La lingua grafica non è nuova: è quella del **progetto gemello**
[`donostia-dataviz`](https://github.com/Stocastico/donostia-dataviz), adottata
qui per intero. I due racconti sono pezzi della stessa collana e devono
sembrarlo.

Cosa arriva da lì, e va cambiato lì se si vuole cambiare:

| | |
|---|---|
| **Tavolozza** | inchiostro blu notte su carta calda (`--ink` su `--bg`), e i colori delle storie: mare, corallo, ambra, verde, viola |
| **Tipografia** | Libre Franklin per i titoli, Inter per il testo, 17px con interlinea 1,65 |
| **Anatomia di una storia** | numero grande, occhiello, titolo, domanda in corsivo con filetto, capolettera alzata, cifre chiave, riquadro delle conclusioni, scheda di confidenza |
| **Pieghevoli** | «la metrica, in chiaro» per le spiegazioni tecniche e «controllo» per i blocchi che mettono alla prova l'argomento |
| **Scrollytelling** | figura appiccicosa a sinistra, passi di testo a destra, che degrada a articolo semplice sotto i 900px |
| **Rampe dei grafici** | `SEQ` sequenziale calda e `DIV` divergente freddo↔caldo, le stesse dell'originale |

Quattro differenze deliberate. Le prime tre nascono dal vincolo in più che ha
questo documento — **restare autocontenuto**:

1. **Nessun carattere caricato dalla rete.** Le famiglie sono le stesse, con la
   stessa catena di ripieghi di sistema: chi le ha installate le vede, gli altri
   leggono in `system-ui`.
2. **Nessuna fotografia nell'apertura.** L'originale incorpora la baia di La
   Concha come data URI; qui la testata è tipografica, perché una foto
   incorporata peserebbe più di tutti i dati messi insieme.
3. **Nessuna mappa a piastrelle.** L'originale usa Leaflet da una CDN per il
   dettaglio di strada; qui la geometria comunale basta, e si disegna a mano.

La quarta nasce invece dal contenuto, ed è la sola che **allarga** la tavolozza
invece di restringerla:

4. **Due colori di storia in più, e la regola con cui si sceglie il prossimo.**
   L'originale ha cinque storie e cinque colori; qui le storie sono sette. La
   sesta e la settima li avrebbero dovuti riusare, con il risultato che sezioni
   lontane si sarebbero somigliate senza motivo, quindi sono state aggiunte
   `--oliva` e `--prugna` in `stile.css`.

   La cosa che conta non sono i due colori: è che adesso esiste una **regola**,
   ed è scritta sopra le due righe. Il colore nuovo va **nel buco di tinta più
   largo che resta**, alla luminosità della famiglia, e si verifica che il
   contrasto sul fondo non sia il peggiore del gruppo. Applicata ai cinque
   originali dà l'oliva (73°, in mezzo ai 123 gradi fra ambra e verde);
   applicata ai sei dà il prugna (308°, in mezzo ai 97 gradi fra viola e
   corallo, e a 47 gradi dal vicino più prossimo — più di quanto distino fra
   loro mare e verde). Non è una regola inventata adesso per giustificare una
   scelta: è quella che descrive come era stato scelto l'oliva, resa esplicita
   perché valesse anche per l'ottava storia.

   **E all'ottava è stata applicata, senza correggerla a gusto** (settembre
   2026). Il buco più largo rimasto era **dentro i verdi**: fra oliva (73°) e
   verde (156°), 83 gradi, mezzo a 114°. Ne è uscito `--alloro` (`#3c8235`), che
   dista 41 gradi dall'oliva e 42 dal verde — la stessa spaziatura che hanno già
   fra loro mare e verde (40°) e ambra e corallo (41°). Contrasto sul fondo
   4,3:1 la tinta base e 7,1:1 quella scura, entrambi sopra la mediana del
   gruppo (3,45 e 5,64).

   ⚠️ **La conseguenza, dichiarata invece che scoperta dopo:** i colori di storia
   sono adesso **tre verdi su otto**. Regge perché le tre storie che li portano —
   la terza, la sesta e l'ottava — non si toccano mai in pagina. Se una nona
   storia cadesse accanto a una di loro, la regola andrebbe **rinegoziata invece
   che riapplicata**: una regola che dà un risultato scomodo va discussa, non
   aggirata la volta in cui dà fastidio.

   🙋 **Quello che resta da decidere è se portarla di là.** Se i due progetti
   devono restare una collana stretta, la mossa è copiare in
   `donostia-dataviz` la regola e i **tre** toni; se possono divergere, va bene
   così. Le righe da spostare sono tre, più il commento che le spiega.

E una conseguenza da mettere in conto: **non c'è tema scuro.** L'originale è un
disegno a luce sola, e un tema scuro non è l'inversione di una tavolozza chiara:
è una seconda tavolozza da scegliere e verificare.

## Le scale di colore

- **Sequenziale** — la rampa calda dell'originale, dal chiaro allo scuro.
- **Divergente** — freddo ← neutro → caldo, per le variazioni e per le
  opposizioni vere (manifattura contro turismo).
- **Nessun dato** — un colore suo **più un tratteggio**, mai lo zero della
  scala: due grigi vicini si confondono, un tratteggio no, e regge anche in
  stampa. Compare in legenda solo quando qualcuno manca davvero.
- Le classi sono per **quantile** sulle grandezze (con 205 comuni e un capoluogo
  fuori scala, le classi a intervallo uguale metterebbero quasi tutti nella
  prima) e **simmetriche attorno allo zero** sulle variazioni — ma centrate sul
  **95º percentile** dei valori assoluti, non sul massimo: con il massimo un
  solo comune fuori scala (Magasa, che perde il 2,9 % di abitanti l'anno)
  schiaccia tutti gli altri in due classi pallide. Chi sta oltre finisce nella
  classe di fondo, e la legenda lo dichiara con un `≤` e un `≥`.

## Il rapporto con `web/src/data/`

`costruisci.py` legge i JSON che la pipeline scrive in `web/src/data/`, non le
tabelle CSV: è lo stesso contratto che userà il pannello interattivo quando
esisterà, ed è già verificato dai test della pipeline. L'unica eccezione
dichiarata è la scomposizione settore × classe del capoluogo, che non è un
indicatore comunale e verrebbe male se la si piegasse a esserlo.
