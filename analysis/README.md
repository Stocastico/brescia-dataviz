# analysis

Uno script per analisi, libreria standard soltanto, `--save` che scrive i CSV
in `analysis/output/` (non versionata: si rigenera). È la convenzione fissata
in [`../PROSSIMI-PASSI.md`](../PROSSIMI-PASSI.md) §5.

Gli script leggono **solo** da `../dati/processed/`: nessuno di loro tocca la
rete o le fonti. Se una tabella cambia, il numero cambia da solo — che è tutto
il punto.

| Script | Cosa fa |
|---|---|
| `verifica_cifre.py` | Ricalcola dai CSV **ogni cifra citata nei documenti** e la confronta con quella scritta. Esce con codice 1 se una diverge. |
| `variazione_popolazione.py` | Tasso annualizzato di variazione della popolazione per comune, 2018–2024. La prima delle analisi previste in §5. |
| `velocita_di_cambio.py` | Lo stesso tasso su **addetti, unità locali e reddito**, ciascuno sulla sua finestra. |
| `livelli_e_variazioni.py` | I quattro quadranti livello/crescita, e il test di convergenza fatto sul livello **iniziale** — che sul reddito cambia segno al risultato. |
| `autocorrelazione_spaziale.py` | Indice di Moran sui 205 comuni, con la contiguità ricavata dal GeoJSON e la significatività per permutazione. |
| `_tabelle.py` | Non è un'analisi: è la lettura delle tabelle e la statistica di base che gli script hanno in comune. |

```bash
python analysis/verifica_cifre.py                    # 24 verifiche
python analysis/variazione_popolazione.py --save     # + CSV in analysis/output/
python analysis/velocita_di_cambio.py reddito
python analysis/livelli_e_variazioni.py
python analysis/autocorrelazione_spaziale.py --save
```

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

## Cosa **non** va messo qui

Le trasformazioni che producono le tabelle: quelle stanno nella
[`pipeline/`](../pipeline/README.md) e finiscono in `dati/processed/`. Qui
stanno solo le letture di quelle tabelle. La regola pratica: se il risultato
serve al sito, è pipeline; se serve a capire, è analisi.
