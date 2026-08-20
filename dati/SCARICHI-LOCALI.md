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
repository, nessuna cifra pubblicata può dipendere da lei.** Oggi è vero — le
cinque storie del sito non la usano, e `analysis/verifica_cifre.py` non la
tocca. Il giorno in cui l'asse 2 («chi vive nel bresciano») diventerà una
storia, quel giorno la tabella deve entrare, e in una forma versionabile.

## Quando servirà davvero: le due strade

Non è una decisione da prendere adesso. Quando l'asse 2 verrà affrontato, le
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
