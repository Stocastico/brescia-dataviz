# Handoff — 9 settembre 2026

> **Chiuso il 10 settembre 2026.** La decima storia è stata finita: i sette
> passi qui sotto sono tutti fatti, e il file `cifre2-da-inserire.py.txt` che
> accompagnava questo handoff è stato innestato e rimosso. Il documento resta
> come registro delle decisioni, non come lista di cose da fare.

Due lavori: uno chiuso e mergiato, uno a metà su un branch.

## Chiuso: le figure numerate e la pagina delle tabelle

[PR #26](https://github.com/Stocastico/brescia-dataviz/pull/26), mergiata in
`main` come `fa0759e`. Branch cancellata, locale e remota.

Le 19 figure del racconto prendono un `Fig. N` e un `id="fig-N"`; le tabelle
di tutti i grafici stanno anche su `tabelle.html`, e la tabella-specchio resta
sotto ogni figura (è il mirror accessibile — spostarla via costringeva chi
legge da tastiera a cambiare pagina).

Tre cose da sapere prima di toccare `racconto.html`:

- **I `Fig. N` non stanno nel modello.** `figure()` in `sito/costruisci.py`
  conta le `<figure class="fig">` nell'ordine del documento e li inietta in
  fase di build. Non scriverli a mano: `test_il_racconto_numerato_non_tocca_il_resto`
  fallisce se modello e generato divergono.
- **Lo script dei grafici è in `sito/modelli/figure.js`**, non più in fondo a
  `racconto.html`. È byte-identico a com'era in linea, e ora lo incorporano
  due pagine.
- Due casi non automatici, dichiarati in `costruisci.py`:
  `CONTENITORI_CONDIVISI` (la coppia della casa ha una tabella sola in due) e
  `GRAFICI_FUORI_FIGURA` (il grafico sul disaccordo fra le fonti turistiche
  sta in un `<details>`, non in una figura). Un test confronta i
  `getElementById` di `figure.js` con gli `id` di `tabelle.html`, così la riga
  «tutti i dati dei grafici» non può diventare falsa in silenzio.

## A metà: la decima storia sugli stranieri

Branch **`decima-storia`**, un commit (`f99df00`), **non spinta**. Working tree
pulito, 179 test passano, la costruzione gira.

### Perché la storia si può fare

L'asse era già nel brief (`BRIEF.md`, asse 2 «Chi vive nel bresciano»): è il
solo pianificato senza storia. `analysis/chi_vive_nel_bresciano.py` esiste, 334
righe, e gira. E in `costruisci.py` c'erano già **19 cifre `bg_*`**: 12 usate,
tutte nella sezione dei limiti come avvertenze.

Perimetro deciso: **solo dati già nel repository.** Le due marginali versionate
(`background_migratorio_comuni.csv`, `background_migratorio_istruzione.csv`),
non la congiunta da 422 MB che sta fuori da git.

### Design approvato

**Titolo:** «Cinquantatremila nati qui». Apre sui 53.224 nati in Italia da
genitori stranieri: metà senza cittadinanza italiana, e di quelli il 94,5 %
minorenne.

**Posizione:** nona, fra «Dove il bresciano si svuota» (8, che misura i flussi)
e «Brescia è diversa?», che diventa la decima. L'ottava è il film, questa è la
fotografia dello stesso fenomeno.

**Colore:** per la regola del progetto l'indaco era scelto *per la storia che
segue l'ottava* — quella storia ora è questa, quindi la nuova prende
`--indaco` e la decima posizione prende `--bruno` (`#6d4e22` / `#513815`, già
deciso il 7 settembre, contrasti già calcolati in `stile.css`, mai scritto come
variabile perché mancava il consumatore). **«Brescia è diversa?» cambia
colore**, ed è una conseguenza accettata.

**Cinque figure, nessuna funzione grafica nuova:** `mappa` del background per
comune · `barre` con segno della variazione di stock · `barre` dei nati qui ·
`barre` della laurea per gruppo × classe d'età · `serie` di arrivi e partenze.

### Fatto in questo commit

- `web.py`: indicatore **`quota_background`** (ventesimo del registro, `live`,
  2021–2023, 205 comuni). Compare da sé anche in `esplora.html`.
- `costruisci.py`: `istruzione_background()`, `flussi_estero()`,
  `background_incorporato()` (2,2 KB in `window.DATI`), e la **prima metà**
  delle cifre nuove (i nati qui, il serbatoio, `bg_quota_minima`).
- `test_web.py`: due test nuovi, di cui uno sull'identità delle componenti.
- Export `web/src/data/` rigenerato.

### Da fare, in ordine

1. **Secondo blocco di cifre.** È già scritto e pronto in
   `<scratchpad>/cifre2.py.txt` (istruzione per classe + flussi lordi), da
   inserire in `cifre()` **fuori** dal blocco `if stock:` — il punto di
   innesto è prima di `per_comune = demografia["comuni"]`. *Se lo scratchpad
   della sessione è stato ripulito va riscritto: sono ~40 righe, le cifre
   servono sono elencate al punto 4 qui sotto.*
2. `stile.css`: `--bruno` e `--bruno-d` come variabili, regole `.s10` per
   badge, `question`, `takeaway`, `kn .big`, `step.active`.
3. `racconto.html`: la sezione nuova come `s9`, rinumerare «Brescia è diversa?»
   a `s10` / badge 10, e riscrivere **due** `nextcap` (quello dell'ottava punta
   alla nuova, quello della nuova punta a «diversa»).
4. `figure.js`: cinque chiamate nuove, che leggono `DATI.background`.
5. **Cinque righe nei limiti**, e non sono decorative: finestra di tre anni ·
   le due tabelle non si sommano (9+ contro tutta la popolazione) · il paese di
   origine non c'è · `emigrati_estero` conta residenti e non italiani, e
   sottostima perché chi parte spesso non si cancella · il paese di origine non
   è un proxy di reddito o disagio (la cautela è già scritta in FONTI.md
   §4-quater).
6. `analysis/verifica_cifre.py`: una voce per ogni cifra nuova. Oggi fa 214
   controlli indipendenti, ed è il red/green di una storia in questo progetto.
7. `BRIEF.md`: marcare l'asse 2 come fatto, con la forma che ha preso — gli
   altri assi hanno tutti quella nota.

### I numeri, già verificati contro l'analisi indipendente

| | |
|---|---|
| popolazione 2021→2023 | +7.798 |
| italiani dalla nascita | **−8.219** |
| italiani per acquisizione | **+15.385** (2,0 volte la crescita totale) |
| stranieri | +632 |
| ingresso implicito, due anni | ≥16.017 |
| nati in Italia da genitori stranieri | **53.224**, metà senza cittadinanza |
| di quelli senza cittadinanza, minorenni | 94,5 % |
| background migratorio, provincia | 18,4 % |
| per comune | da 0,6 % a 29,9 %, mediana 13,0 %, max Castelcovati |
| laurea 25–49, dalla nascita / stranieri | 28,0 % / 14,9 % → **+13,1 punti** |
| laurea 65+, dalla nascita / stranieri | 6,5 % / 12,5 % → **−6,0 punti** |
| partenze per l'estero 2019 → 2024 | 4.644 → 4.638 (ferme) |
| arrivi 2019 → 2024 | 9.211 → 11.077 (raddoppiano) |
| sei anni | 26.642 partenze, 54.459 arrivi |

## Gotcha

- **`gh` ha due account.** Le PR sui repo `Stocastico/*` vogliono
  `gh auth switch --user Stocastico`; il push riesce comunque con quello
  aziendale, quindi l'errore compare solo al momento della PR. Ora è attivo
  `smasneri_Grupmp`, quindi **prima di spingere `decima-storia` va commutato**.
- **`pipeline/uv.lock` si ricrea a ogni `uv run`** e non è in `.gitignore`. La
  CI usa pip, quindi il file non serve: l'ho cancellato due volte in questa
  sessione. Una riga in `.gitignore` chiuderebbe la faccenda.
- **Gli screenshot del browser non funzionavano**: il pane riportava
  `viewport 0x0` (finestra nascosta). Le verifiche visive sono state fatte
  leggendo il DOM e gli stili calcolati. Se domani serve una prova visiva, va
  controllato che la finestra sia in primo piano.
- **La copertura in locale è lenta**: `uv run --with pytest-cov pytest tests`
  su tutta la suite si è piantata due volte oltre i dieci minuti. Misurare su
  un file solo (`--cov=../sito` con `tests/test_costruisci.py`) ci mette ~6
  minuti e basta a vedere le righe nuove.

## Aperto altrove

Un task in background su `pipeline/src/brescia_pipeline/datasets/lavoro.py`,
lanciato da questa sessione in un worktree separato: `_censimento()` esplode
ogni osservazione in una riga per dimensione **senza chiave di osservazione**,
quindi l'incrocio occupazione × cittadinanza è irrecuperabile dal CSV anche se
il dato è stato scaricato. È il motivo per cui «integrazione via lavoro» non è
entrata in questa storia. Non tocca nessun file della decima storia.
