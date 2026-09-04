# analysis

Uno script per analisi, libreria standard soltanto, `--save` che scrive i CSV
in `analysis/output/` (non versionata: si rigenera). È la convenzione fissata
in [`../PROSSIMI-PASSI.md`](../PROSSIMI-PASSI.md) §5.

Gli script leggono **solo** da `../dati/processed/`: nessuno di loro tocca la
rete o le fonti. Se una tabella cambia, il numero cambia da solo — che è tutto
il punto.

| Script | Cosa fa |
|---|---|
| `verifica_cifre.py` | Ricalcola dai CSV **ogni cifra citata nei documenti e nel sito** e la confronta con quella scritta. Esce con codice 1 se una diverge. |
| `variazione_popolazione.py` | Tasso annualizzato di variazione della popolazione per comune, 2018–2024. La prima delle analisi previste in §5. |
| `decomposizione_popolazione.py` | **Da dove viene** quella variazione: saldo naturale, migrazione interna, migrazione estera, più le due voci che componenti non sono. Ha ribaltato la parola «spopolamento» (MET-15) e porta il confronto con le altre 107 province, che sulla popolazione mancava. |
| `velocita_di_cambio.py` | Lo stesso tasso su **addetti, unità locali e reddito**, ciascuno sulla sua finestra. |
| `livelli_e_variazioni.py` | I quattro quadranti livello/crescita, e il test di convergenza fatto sul livello **iniziale** — che sul reddito cambia segno al risultato. |
| `autocorrelazione_spaziale.py` | Indice di Moran sui 205 comuni, con la contiguità ricavata dal GeoJSON e la significatività per permutazione. |
| `decomposizione_capoluogo.py` | La scomposizione settore × classe che ha chiuso MET-9: il crollo delle grandi unità locali del capoluogo, spiegato. |
| `due_economie.py` | Quote settoriali comune per comune: manifattura contro alloggio e ristorazione, e il quoziente di localizzazione. |
| `tipologia_comuni.py` | k-means++ con seme fisso su sei variabili strutturali. Dichiara anche i comuni che nessun gruppo descrive bene. |
| `dove_si_lavora.py` | Addetti ogni 100 abitanti, e il settore prevalente che spiega perché i due estremi non sono lo stesso fenomeno. |
| `rottura_covid.py` | La discontinuità del 2020, testata dove si può e dichiarata non testabile dove non si può. |
| `aria_e_clima.py` | L'asse 4: il panel bilanciato sulle centraline (PM10 e biossido di azoto crollano, l'ozono no) e le anomalie di temperatura, che è l'unico modo di mediare stazioni fra i 47 e i 2.108 metri. Comprende la serie che **non** dà segnale, la pioggia. |
| `confronto_province.py` | Gli stessi indicatori su tutte e 107 le province italiane: dove sta Brescia, e il controllo esterno di MET-9. |
| `convergenza_confronto.py` | La convergenza dei redditi rifatta su Bergamo: regge identica, quindi non è bresciana. |
| `confronto_turismo.py` | Il turismo confrontato con le altre 106 province, dal 2008: era l'ultimo asse senza un altrove. Ne escono MET-17 (le due fonti sul turismo bresciano distano il 10,6 %) e MET-18 (il 2025 ha una definizione nuova dentro). |
| `_tabelle.py` | Non è un'analisi: è la lettura delle tabelle e la statistica di base che gli script hanno in comune. |

```bash
python analysis/verifica_cifre.py                    # centotrentanove verifiche, settembre 2026
python analysis/variazione_popolazione.py --save     # + CSV in analysis/output/
python analysis/decomposizione_popolazione.py        # perché quella variazione
python analysis/velocita_di_cambio.py reddito
python analysis/livelli_e_variazioni.py
python analysis/autocorrelazione_spaziale.py --save
python analysis/decomposizione_capoluogo.py
python analysis/due_economie.py
python analysis/tipologia_comuni.py --gruppi 5
python analysis/dove_si_lavora.py
python analysis/rottura_covid.py
python analysis/aria_e_clima.py --save
python analysis/confronto_province.py
python analysis/convergenza_confronto.py
python analysis/confronto_turismo.py
```

Il numero delle verifiche è scritto **solo qui**, e di proposito: una cifra
ripetuta in quattro documenti è una cifra che fra sei mesi ne dice quattro
diverse. Negli altri documenti si parla di «ogni cifra citata», che resta vero
comunque vada.

## Il modulo condiviso, e l'unico script che non lo usa

`_tabelle.py` esiste perché ogni script rifarebbe le stesse tre cose: aprire un
CSV di `dati/processed/`, ricavarne una serie per comune e anno, e calcolare le
due correlazioni che MET-6 impone di riportare in coppia. Il trattino basso dice
che non è un'analisi.

**`verifica_cifre.py` non lo usa, ed è deliberato.** Un verificatore che
condivide il codice con ciò che verifica non verifica niente: se la lettura del
CSV avesse un errore, lo avrebbero entrambi e i numeri tornerebbero lo stesso.
Rilegge i file per conto suo, ed è l'unico script a cui la duplicazione fa bene.

## Perché `verifica_cifre.py` esiste

Il principio «ogni numero citato ha uno script dietro» stava in `BRIEF.md` dal
primo giorno, ma finché i numeri vivevano solo nei testi non era controllabile.
Alla prima verifica sistematica (agosto 2026) **due cifre su ventiquattro erano
sbagliate**:

| Dove | Diceva | È |
|---|---|---|
| `BRIEF.md`, `METODOLOGIA.md` MET-2 e MET-5 | mediana della popolazione comunale «attorno ai 2.000» | **3.671** |
| `BRIEF.md`, `WORKING-PAPER.md` §7 | addetti in unità 10–249, +«circa 13 mila» | **+23.840** |

Nessuna delle due cambia una conclusione — il capoluogo resta un outlier di un
ordine di grandezza, la crescita resta nella fascia intermedia — ma la seconda
sottostimava di quasi la metà il fenomeno che il progetto vuole raccontare.
Entrambe sono corrette nei documenti; da qui in avanti lo script le tiene
oneste.

Aggiungere una cifra a un documento significa aggiungere una riga a
`VERIFICHE`. Se non è ricalcolabile dalle tabelle, è un segnale: o manca il
dato, o la frase dice più di quanto il dato sostenga.

**È successo di nuovo ad agosto 2026**, e la seconda volta è più interessante
della prima. Aggiungendo le cifre delle analisi nuove, l'indice di Moran sulla
specializzazione settoriale divergeva: 0,44 nel sito, 0,46 qui. Nessuno dei due
calcoli era sbagliato — erano due decisioni diverse sullo stesso dato mancante,
prese in due file diversi da chi non sapeva dell'altro. Da lì è nata MET-13, e
la definizione ora sta in un posto solo.

Nel sito il problema si pone in modo diverso, e più radicale: **nessuna cifra è
scritta a mano nel testo**. Sono segnaposto che `sito/costruisci.py` calcola
dalle tabelle, e un segnaposto senza valore fa fallire la costruzione. Lì non
serve un verificatore perché non c'è niente da verificare.

## Cosa **non** va messo qui

Le trasformazioni che producono le tabelle: quelle stanno nella
[`pipeline/`](../pipeline/README.md) e finiscono in `dati/processed/`. Qui
stanno solo le letture di quelle tabelle. La regola pratica: se il risultato
serve al sito, è pipeline; se serve a capire, è analisi.
