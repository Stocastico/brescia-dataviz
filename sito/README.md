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

## I colori

Sono ruoli, non valori: stanno tutti in cima a `stile.css` e i grafici li
leggono da lì, così il tema scuro è una sostituzione di variabili e non una
seconda tavolozza.

- **Sequenziale** — una sola tinta, dal chiaro allo scuro, per le grandezze.
- **Divergente** — due tinte opposte con il grigio nel mezzo, per le variazioni
  e per le opposizioni vere (manifattura contro turismo). I due archi hanno la
  stessa chiarezza passo per passo, così nessuno dei due pesa più dell'altro.
- **Nessun dato** — un grigio suo, mai lo zero della scala, e compare in legenda
  solo quando qualcuno manca davvero.
- Le classi sono per **quantile** sulle grandezze (con 205 comuni e un capoluogo
  fuori scala, le classi a intervallo uguale metterebbero quasi tutti nella
  prima) e **simmetriche attorno allo zero** sulle variazioni.

## Il rapporto con `web/src/data/`

`costruisci.py` legge i JSON che la pipeline scrive in `web/src/data/`, non le
tabelle CSV: è lo stesso contratto che userà il pannello interattivo quando
esisterà, ed è già verificato dai test della pipeline. L'unica eccezione
dichiarata è la scomposizione settore × classe del capoluogo, che non è un
indicatore comunale e verrebbe male se la si piegasse a esserlo.
