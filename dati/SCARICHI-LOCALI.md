# I dati troppo grossi per il repository

> **Nota per Stefano.** Una tabella del progetto non è versionata perché pesa
> troppo. Qui c'è come rifarla, quanto costa, e perché va bene così.

## La regola, e la sua unica eccezione

Il patto del progetto è: `dati/raw/` **non** si versiona (sono le risposte grezze
delle fonti, rigenerabili), `dati/processed/` **sì** (sono il prodotto del
lavoro). Oggi c'è **una sola eccezione**, ed è dichiarata in `.gitignore` con la
motivazione accanto:

| File | Peso | Righe | Perché resta fuori |
|---|---|---|---|
| `dati/processed/migrazioni_comuni.csv` | **422 MB** | 1,8 milioni | è la distribuzione congiunta di sei dimensioni censuarie su 205 comuni, con le etichette italiane ripetute per esteso su ogni riga |

Per confronto: le altre ventiquattro tabelle stanno fra le cinquemila e le
quarantamila righe, e la più grossa non arriva a dieci megabyte.

## Come rifarla in locale

```bash
pip install -e ./pipeline
python -m brescia_pipeline.build migrazioni
```

**Venti minuti circa**, e servono ~2 GB liberi per le risposte grezze in
`dati/raw/`. Non serve nessuna chiave, nessun login, nessuna VPN: è tutto
`esploradati.istat.it` in chiaro.

Se lo spazio grezzo dà fastidio, dopo il build si può buttare — la tabella
prodotta resta:

```bash
rm -rf dati/raw/istat_migr_backg_*
```

Il resto delle tabelle si rifà tutto insieme con `python -m
brescia_pipeline.build`, che scarica quello che manca e salta quello che c'è già.

## Perché va bene che non sia versionata

Perché **la riproducibilità la garantisce la pipeline, non il file**. Chiunque
cloni il repository può rifare quella tabella con un comando e venti minuti, e
ottenere esattamente la stessa cosa: il progetto non chiede di fidarsi di un CSV
che qualcuno ha caricato, chiede di poterlo rigenerare.

Il costo reale è un altro, e va tenuto d'occhio: **finché la tabella non è nel
repository, nessuna cifra pubblicata può dipendere da lei.** Questa riga
prometteva che «il giorno in cui l'asse 2 diventerà una storia, quel giorno la
tabella deve entrare, e in una forma versionabile».

✅ **Quel giorno è il 7 settembre 2026**, e la promessa è stata mantenuta senza
versionare 422 MB: l'asse 2 è entrato nella prima storia, e la forma
versionabile sono **due marginali** da 570 KB in tutto, che
`analysis/verifica_cifre.py` ricalcola cifra per cifra. La congiunta resta fuori
da git e nessuna cifra pubblicata dipende da lei. Come, e perché quella forma,
nella sezione qui sotto.

## ✅ La decisione è stata presa: la seconda strada (7 settembre 2026)

Questa sezione diceva «non è una decisione da prendere adesso», e aveva ragione:
la condizione era **guardare la storia che si vuole raccontare**. La prima storia
del sito adesso cita il background migratorio, quindi la condizione è
soddisfatta, e la scelta è stata la **seconda**.

La congiunta resta qui, fuori da git. Accanto, `datasets/migrazioni.py` scrive
due **marginali versionate** dalle stesse righe, senza una richiesta in più:

| tabella | righe | cosa tiene |
|---|---|---|
| `background_migratorio_comuni.csv` | 7.776 | lo stock per comune × anno × indicatore, 2021–2023 |
| `background_migratorio_istruzione.csv` | 270 | il titolo di studio dei tre gruppi per classe d'età, a grana provinciale |

Sono 570 KB in tutto invece di 422 MB, e su di loro poggia ogni cifra che la
pagina pubblica: `verifica_cifre.py` le ricalcola, quindi il vincolo qui sotto
è rispettato senza versionare la congiunta.

**Cosa resta vero.** La congiunta è l'unica che tiene gli incroci fini, e chi
vuole scendere sotto quello che le marginali portano deve rigenerarla. Il giorno
in cui una storia userà un incrocio che le marginali non hanno, si aggiunge una
voce a `SINTESI` o una classe a `ISTRUZIONE`: è una riga, non una decisione.

Il ragionamento originale, per memoria.

Non era una decisione da prendere allora. Quando l'asse 2 verrà affrontato, le
opzioni sono due, e la seconda è quasi certamente quella giusta:

1. **Codici al posto delle etichette**, più una tabella-legenda a parte
   (`migrazioni_modalita.csv`). È anche la forma corretta a prescindere — è la
   lezione di MET-13, le etichette cambiano lingua e i codici no — e taglia il
   file di circa tre quarti. Ma un centinaio di megabyte restano un centinaio di
   megabyte.
2. **Solo le marginali che servono.** Delle sei dimensioni incrociate, una
   storia ne userà due o tre; il resto è prodotto cartesiano che nessuno
   guarderà. Tenere le combinazioni utili in `dati/processed/` e la congiunta
   completa in `dati/raw/` riporta la tabella nell'ordine di grandezza delle
   altre.

La seconda si può scegliere solo **guardando la storia che si vuole
raccontare**, non prima: è il motivo per cui la decisione è rimasta aperta
invece di essere presa a caso.

## Le altre cose pesanti (che non sono un problema)

`dati/raw/` sta sul giga e mezzo abbondante dopo un build completo, ed è
normale: dentro ci sono i file nazionali del registro delle imprese, che
servono anche al confronto fra le 107 province. Sono tutti rigenerabili e tutti
già esclusi da git. Non c'è niente da decidere lì.

---

*Vedi anche: [`PROSSIMI-PASSI.md`](../PROSSIMI-PASSI.md) §2.1 per il contesto, e
[`FONTI.md`](../FONTI.md) §10 punto 6 per il motivo per cui questo scarico è
passato da nove ore a venti minuti.*
