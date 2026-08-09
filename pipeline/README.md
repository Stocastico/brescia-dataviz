# brescia-pipeline

Da fonti pubbliche a tabelle tidy sull'evoluzione di Brescia: il **comune**
(`017029`), la **provincia** (`ITC47`) e i suoi **205 comuni**.

Dipendenze: `requests` e la libreria standard. Niente pandas, niente build
step, niente chiavi API — tutte le fonti sono aperte.

## Eseguire

```bash
cd brescia/pipeline
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

A queste si aggiungono due vincoli operativi: le chiavi con molti codici
sfondano la lunghezza massima dell'URL e il server risponde `400` — meglio
scaricare tutto e filtrare in locale; e i valori mancanti (`Dato riservato`,
`-9999`) non vanno **mai** convertiti in zero.

## Dataset

| Nome | Tabelle prodotte | Grana | Fonte |
|---|---|---|---|
| `popolazione` | `popolazione_comuni.csv` | 205 comuni, 2018–2024 | ISTAT Censimento permanente |
| `imprese` | `imprese_classe_addetti.csv`, `imprese_settore.csv` | comuni + provincia, 2018–2023 | ISTAT ASIA |
| `turismo` | `turismo_comuni_annuale.csv`, `turismo_comuni_mensile.csv` | comuni, 2019–2024 | Regione Lombardia |
| `lavoro` | `censimento_lavoro_brescia.csv`, `tasso_occupazione_provincia.csv` | comune / provincia | ISTAT |
| `sicurezza` | `reati_provincia.csv`, `percezione_sicurezza.csv` | provincia / comune | ISTAT |
| `ambiente` | `stazioni_arpa.csv`, `aria_mensile.csv`, `meteo_mensile.csv` | stazione, dal 1990 | ARPA Lombardia |
| `redditi` | `redditi_comuni.csv` | comuni | MEF via ISTAT |
| `commercio_estero` | `commercio_estero_lombardia.csv` | **regione** (ripiego) | ISTAT |

Il dettaglio delle fonti, con lo stato di accesso verificato riga per riga, sta
in [`../FONTI.md`](../FONTI.md). La descrizione delle tabelle prodotte sta in
[`../dati/README.md`](../dati/README.md).
