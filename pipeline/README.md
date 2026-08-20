# brescia-pipeline

Da fonti pubbliche a tabelle tidy sull'evoluzione di Brescia: il **comune**
(`017029`), la **provincia** (`ITC47`) e i suoi **205 comuni**.

Dipendenze: `requests` e la libreria standard. Niente pandas, niente build
step, niente chiavi API — tutte le fonti sono aperte.

## Eseguire

```bash
cd pipeline
python -m pip install -e ".[dev]"        # oppure: export PYTHONPATH=src
python -m brescia_pipeline.build         # tutti i dataset
python -m brescia_pipeline.build imprese turismo
python -m brescia_pipeline.build --list
pytest
```

Le risposte grezze finiscono in `../dati/raw/` (non versionata) e vengono
**riusate**: la seconda esecuzione non riscarica nulla. Per forzare un
aggiornamento, cancellare i file interessati. Il primo build completo richiede
parecchi minuti — alcune serie ISTAT superano i 100 MB perché non si possono
filtrare lato server.

## Come è fatta

```
src/brescia_pipeline/
  config.py     codici territoriali, endpoint, percorsi
  fetch.py      scarico con cache su disco e ritentativi
  sdmx.py       costruzione delle chiavi SDMX dalla struttura del dataflow
  tidy.py       parsing dei numeri, lettura delle risposte, scrittura dei CSV
  geo.py        lettura di shapefile e riproiezione UTM 32N -> WGS84
  datasets/     un modulo per tema, ciascuno con un `build(comuni)`
  build.py      orchestratore
```

Aggiungere un dataset = scrivere un modulo in `datasets/` che espone
`build(comuni: dict[str, str]) -> None` e registrarlo in `build.DATASETS`.
È lo schema del progetto Donostia, ridotto all'osso.

## Le tre trappole che questa pipeline evita per te

Sono costate tutte almeno un errore, e sbagliano **in silenzio**: producono
risultati plausibili invece di fallire.

1. **Il formato SDMX si negozia con l'header.** Chiedere il CSV con
   `?format=csvfilewithlabels` restituisce l'intestazione e **zero righe**.
   Serve `Accept: application/vnd.sdmx.data+csv`. Un dataset pieno sembra
   vuoto. (`fetch.SDMX_CSV_ACCEPT`)
2. **Le chiavi SDMX sono posizionali.** Un punto in più o in meno restituisce
   zero righe senza errore. Qui le dimensioni si leggono dal server e la
   chiave si compone da un dizionario. (`sdmx.key`)
3. **I separatori numerici cambiano fonte per fonte.** ISTAT scrive
   `100939.25`, Socrata scrive `1,406,590`. Una `float()` ingenua legge
   `567,391` come 567,391: sbagliato di mille volte, ma perfettamente
   plausibile. (`tidy.to_number`, con i suoi test)

A queste si aggiungono tre vincoli operativi.

- **Le chiavi con più valori per dimensione non funzionano**, e non è una
  questione di lunghezza: `REF_AREA` con 50 codici (430 caratteri di URL)
  riceve `400` esattamente come con 205. Il server non accetta la sintassi
  `codice+codice` su questa dimensione. Un codice solo invece funziona: le
  strade sono quindi due, scaricare l'Italia intera e filtrare in locale
  (quella scelta qui, ed è il motivo per cui il primo build è lungo e per cui
  la cache di `dati/raw/` conta) oppure 205 richieste piccole — vedi
  [`../FONTI.md`](../FONTI.md) §10 punto 6.
- **I valori mancanti** (`Dato riservato`, `-9999`) non vanno **mai**
  convertiti in zero.
- **I confini ISTAT si chiamano `_WGS84` ma sono in metri UTM 32N.** Passarli a
  una mappa senza riproiettare disegna la provincia al largo dell'Africa, e
  l'errore è silenzioso perché i numeri restano numeri. (`geo.py`)

## Dataset

| Nome | Tabelle prodotte | Grana | Fonte |
|---|---|---|---|
| `confini` | `../dati/geo/comuni_brescia.geojson`, `comuni_geometria.csv` | 205 comuni | ISTAT limiti amministrativi 2025 |
| `popolazione` | `popolazione_comuni.csv` | 205 comuni, 2018–2024 | ISTAT Censimento permanente |
| `imprese` | `imprese_classe_addetti.csv`, `imprese_settore.csv` | comuni + provincia, 2018–2023 | ISTAT ASIA |
| `turismo` | `turismo_comuni_annuale.csv`, `turismo_comuni_mensile.csv` | comuni, 2019–2024 | Regione Lombardia |
| `lavoro` | `censimento_lavoro_brescia.csv`, `tasso_occupazione_provincia.csv` | comune / provincia | ISTAT |
| `migrazioni` ⏳ | `migrazioni_comuni.csv` | 205 comuni | ISTAT Censimento permanente (10 tavole) |
| `abitazioni` | `abitazioni_comuni.csv` | 205 comuni, 2019 · 2021 · 2023 | ISTAT Censimento permanente |
| `famiglie` | `famiglie_comuni.csv` | 205 comuni, 2018–2024 | ISTAT Censimento permanente |
| `sicurezza` | `reati_provincia.csv`, `percezione_sicurezza.csv` | provincia / comune | ISTAT |
| `ambiente` | `stazioni_arpa.csv`, `aria_mensile.csv`, `meteo_mensile.csv` | stazione, dal 1990 | ARPA Lombardia |
| `redditi` | `redditi_comuni.csv` | comuni | MEF via ISTAT |
| `commercio_estero` | `commercio_estero_lombardia.csv` | **regione** (ripiego) | ISTAT |

⏳ = **modulo scritto, tabella non ancora prodotta.** `famiglie` e
`abitazioni` sono state prodotte ad agosto 2026, quando
`esploradati.istat.it` è tornato ad accettare connessioni. `migrazioni` no, e
il motivo è la dimensione: dieci tavole nazionali che pesano fra 0,5 e **1,8 GB
l'una** e impiegano da venti minuti a un'ora. Sette sono arrivate (6,9 GB in
cache, non si riscaricano); l'ottava fallisce perché l'host lascia cadere la
connessione, e **ogni caduta fa ripartire da zero** — la cache è per file
intero, non c'è ripresa parziale. Il modulo scrive la tabella solo quando tutte
e dieci sono a posto.

```bash
python -m brescia_pipeline.build migrazioni   # riparte dall'ottava
```

Conviene lanciarlo su una macchina che non si spegne, non in una sessione
remota. **Attenzione a una via d'uscita che sembra ovvia e non lo è**: la
richiesta per singolo comune, che su altri dataflow funziona benissimo, su
questa famiglia va in timeout dopo 300 secondi senza restituire nulla — il
server prepara la risposta a prescindere dal filtro. Il quadro completo, con le
quattro strade possibili, sta in
[`../PROSSIMI-PASSI.md`](../PROSSIMI-PASSI.md) §2.1-bis.

La forma delle tabelle è comunque coperta dai test (`tests/test_censimento.py`)
su una risposta SDMX di prova, quindi il parsing non è materiale non provato.

Il dettaglio delle fonti, con lo stato di accesso verificato riga per riga, sta
in [`../FONTI.md`](../FONTI.md). La descrizione delle tabelle prodotte sta in
[`../dati/README.md`](../dati/README.md).
