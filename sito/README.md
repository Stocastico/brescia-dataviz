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
| `modelli/racconto.html` | il documento narrativo: quattro storie e la sezione dei limiti |
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

Tre differenze deliberate, tutte dovute al vincolo in più che ha questo
documento — **restare autocontenuto**:

1. **Nessun carattere caricato dalla rete.** Le famiglie sono le stesse, con la
   stessa catena di ripieghi di sistema: chi le ha installate le vede, gli altri
   leggono in `system-ui`.
2. **Nessuna fotografia nell'apertura.** L'originale incorpora la baia di La
   Concha come data URI; qui la testata è tipografica, perché una foto
   incorporata peserebbe più di tutti i dati messi insieme.
3. **Nessuna mappa a piastrelle.** L'originale usa Leaflet da una CDN per il
   dettaglio di strada; qui la geometria comunale basta, e si disegna a mano.

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
