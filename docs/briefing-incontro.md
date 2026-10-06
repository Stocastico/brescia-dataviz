# Briefing: cosa abbiamo, cosa manca, dove andare

Scritto il 6 ottobre 2026 per una conversazione con chi ha letto `racconto.html` e
vuole sapere di più. Non sostituisce `PROSSIMI-PASSI.md` (lo stato tecnico) né
`WORKING-PAPER.md` (la tesi): è la versione da tenere in mano parlando.

Le cifre vengono da `README.md`, `WORKING-PAPER.md` §7 e `PROSSIMI-PASSI.md`; la
fonte di verità resta `python analysis/verifica_cifre.py`.

## 1. Cosa è stato fatto, in dieci righe

Soggetto: la **provincia di Brescia** (`ITC47`) raccontata attraverso i suoi
**205 comuni**, con il capoluogo come caso a parte. Cinque assi: lavoro e
imprese, popolazione e origini, reddito e salari, casa, ambiente e turismo.

- **39 tabelle** pulite e versionate (`dati/processed/`), scaricabili con un comando.
- **16 analisi** (`analysis/`), **27 regole di metodo** (`METODOLOGIA.md`),
  452 test, copertura 85 %.
- **Un sito** autocontenuto (`sito/`): racconto in dieci storie, pagina che esplora
  tutti i comuni, metodologia, dati, tabelle-specchio di ogni grafico. Si pubblica
  da solo a ogni push su `main`.
- **Un working paper** con una tesi sul metodo: *«Il numero giusto, la frase
  falsa»*, undici episodi in cui un dato corretto stava per produrre
  un'affermazione falsa.

Le dieci storie, con il risultato che le regge:

| Storia | Risultato |
|---|---|
| Redditi | Convergono (corr. −0,45 fra livello iniziale e crescita), i luoghi no. Vale uguale a Bergamo (−0,48): non è un fatto bresciano |
| Stipendi | +25 % nominali, circa −6 % in termini reali (fonte INPS, 107 province) |
| Casa | Capoluogo: prezzo al m² +2,3 % in euro correnti dal 2004, **−30,8 % in euro 2025**; volumi di compravendita +134,5 % dal 2013 |
| Crollo che non c'è | Il calo dei grandi addetti nel capoluogo è un cambio di come si registra, non deindustrializzazione (succede in 44 capoluoghi su 64) |
| Due economie | 48 comuni con oltre metà addetti in manifattura, 24 con almeno un quarto in alloggio/ristorazione; sono territori contigui (Moran 0,44) |
| Turismo | 10ª provincia d'Italia per presenze, 6ª per quota di stranieri; Sirmione da sola supera la città |
| Aria e clima | PM10 a Broletto da 45,5 a 27,3 µg/m³ (2001–2024); il clima si scalda; la pioggia non dà segnale |
| Popolazione | 93 comuni su 205 perdono abitanti, ma non emigrano: saldo naturale −10.163, migrazione interna −66 |
| Origini | 53.224 nati qui, e metà non ha la cittadinanza |
| Brescia è diversa? | Il 92,7 % di piccole unità locali descrive l'Italia, non Brescia; il tratto distintivo è il settore (15ª per quota manifatturiera) |

## 2. Cosa abbiamo usato, cosa no

**Usato**: ISTAT (censimento permanente, ASIA, bilancio demografico, indice
prezzi, turismo provinciale), Agenzia delle Entrate OMI (quotazioni 2004–2025,
compravendite 2011–2025), MEF (redditi comunali), INPS (retribuzioni), INAIL
(infortuni, aggregati prima di scrivere), ARPA e meteo (aria, clima), Regione
Lombardia (turismo comunale), MUR (atenei), reati provinciali 2006–2024,
confini ISTAT.

**Scaricato ma non (ancora) raccontato**: infortuni INAIL, percezione di
sicurezza e reati, commercio estero (solo regionale), imprese per classe di
addetti nel dettaglio, famiglie e abitazioni censuarie. Sono tabelle senza
storia: la regola MET-25 dice di non aggiungerne altre senza una domanda.

**Non usato**, per scelta o per ostacolo:

- Open data del Comune di Brescia: portale dismesso, i dataset sono migrati su
  `dati.lombardia.it` (da esplorare). Turismo cittadino 2005–2013: solo chiedendo
  all'ufficio statistica.
- Commercio estero provinciale: Coeweb dismesso, resta la serie regionale.
- Sezioni di censimento (grana di quartiere): chiuse, il soggetto è provinciale.
- Elettorale (Eligendo non risponde), OpenPNRR (licenza ODbL, contaminerebbe la
  licenza del repo), mappatura acustica.
- Migrazioni comunali per origine: 20 minuti di download, fuori da git per
  scelta.

**Buchi che il progetto non dichiara abbastanza**, e che un parlamentare noterà:

- **Nessun PIL / valore aggiunto provinciale.** Per una provincia manifatturiera
  è la prima domanda. ISTAT (conti territoriali) ed Eurostat (NUTS3) lo
  pubblicano; non è in `FONTI.md`. Non l'ho verificato qui.
- **Nessuna finanza pubblica locale**, nessuna sanità, nessuna scuola, nessun
  trasporto. Il progetto copre economia e demografia; i servizi sono assenti.
- **Il confronto con l'Italia c'è per i quattro assi economici, non per
  l'ambiente.** Dichiarato in WORKING-PAPER §8.

## 3. Dati da prendere con più fatica

Ordinati per rapporto valore/sforzo, secondo me. Quelli marcati ⚠ non li ho
verificati in questo repo: l'accessibilità va testata prima di promettere.

| Dato | Perché | Ostacolo |
|---|---|---|
| **Valore aggiunto e PIL per provincia** (ISTAT conti territoriali, Eurostat NUTS3) ⚠ | Mette Brescia nel quadro macro: produttività, quota manifatturiera sul valore e non solo sugli addetti | Probabilmente nessuno: SDMX come le altre fonti |
| **INPS per settore Ateco** | Salari e addetti per settore: la cosa più interessante che l'osservatorio può dire in una provincia manifatturiera | Il dimension-id interno non è documentato, va intercettato (`PROSSIMI-PASSI` §2.3) |
| **Cassa integrazione per provincia** (INPS) ⚠ | Il termometro congiunturale del manifatturiero; già in `FONTI.md` come «da verificare» | Da verificare |
| **Migrazioni interne per comune** | Chiude l'asse 2: chi arriva, da dove | Venti minuti, già descritto |
| **Distribuzione del reddito per classi** (MEF) ⚠ | Permette di parlare di disuguaglianza, non solo di livello medio | Va controllato che la grana comunale sia pubblica |
| **Consumo di suolo** (ISPRA) ⚠ | Cementificazione per comune, serie annuale; si lega a casa e spopolamento | Da verificare |
| **Emissioni per comune** (INEMAR, ARPA Lombardia) ⚠ | Dà una mappa dell'aria che le centraline non permettono | Da verificare su `dati.lombardia.it` |
| **Parco veicoli** (ACI) ⚠ | Mobilità, qualità dell'aria, reddito | Da verificare |
| **Demografia d'impresa** (famiglia ISTAT `DICA_ACDP`) | Imprese guidate da stranieri, età delle imprese | Nessuno, è SDMX come il resto |
| **Dati del Comune su `dati.lombardia.it`** | Dati cittadini a grana fine | Esplorare |
| **Sanità** (ATS Brescia, mortalità) ⚠ | Servirebbe per Caffaro e per qualunque domanda di salute | Dati spesso su richiesta |
| **Pendolarismo comunale** | 26.425 escono ogni giorno dal capoluogo; la matrice origine-destinazione sarebbe una mappa dei flussi | Il permanente dà solo i totali, la matrice è del censimento 2011 ⚠ |

## 4. Storie che non abbiamo raccontato

Le prime cinque sono quelle che giudico più mature: i dati ci sono già o si
scaricano senza ostacoli.

1. **Le imprese straniere** (demografia d'impresa). Complemento naturale di
   «53.224 nati qui».
2. **Case vuote dove i prezzi sono caduti** (stock abitativo del censimento
   incrociato con l'OMI). È il seguito diretto della storia sulla casa, ed è
   già in `PROSSIMI-PASSI` §4.
3. **Brescia e Bergamo**, province gemelle. Il confronto c'è già sui redditi; si
   estende a tutto il resto con un filtro, i dati nazionali sono già scaricati.
4. **Il Garda contro il resto** (BRIEF n. 11): turismo, prezzi, redditi e
   addetti hanno tutti il Garda come caso a parte. Una storia di una sola mappa.
5. **Dove si lavora e dove si vive**: Odolo 89,6 addetti ogni 100 abitanti,
   Limone 133 (`analysis/dove_si_lavora.py`). Esiste l'analisi, non la storia.
6. **Lavoro da casa dopo il 2021** (`DF_DCSS_LCAS_FRISC_1`).
7. **Affitti**: la base di superficie cambia nel 2025 (MET-19), vanno letti in
   due tratti.
8. **Caffaro** (PCB, Brescia): l'incrocio più diretto fra storia industriale e
   salute pubblica. È anche la più delicata: serve il dato sanitario, e senza
   quello non si scrive.
9. **Isola di calore** via Landsat (endpoint verificato e anonimo).
10. **Distretti veri**: la Val Trompia è la divisione Ateco 25, non «la
    manifattura». Sezione troppo grossolana, divisione giusta.
11. **PNRR e opere pubbliche**: attenzione alla licenza (ODbL), vedi §2.

## 5. Trend, e come confrontare con l'Italia

Il progetto ha già un metodo: **ogni indicatore va confrontato con le 107
province** (MET-14). Ha smontato frasi che il progetto ripeteva dal primo giorno (MET-14, MET-15), ed è il
motivo per cui il «92,7 % di piccole imprese» non compare più come dato
bresciano. Estendibile così:

- **Indici base 100** per Brescia, Lombardia, Nord-Ovest e Italia sulle stesse
  serie, con il deflatore (MET-20) quando si parla di euro.
- **Shift-share**: la crescita di Brescia è dovuta alla *struttura* (tanta
  manifattura) o alla *performance dentro i settori*? Dice se Brescia cresce
  «per com'è fatta» o «per come lavora». I dati ci sono già.
- **Pari grado**: Bergamo, Vicenza, Treviso, Modena, Reggio Emilia, che il
  working paper già individua come cluster. Confrontare con la media nazionale
  è meno informativo che confrontare con chi ti somiglia.
- **Convergenza e dispersione** (σ e β) su altri indicatori oltre al reddito:
  prezzi della casa, presenze, addetti.
- **Rotture strutturali**: il 2020 è già analizzato (`rottura_covid.py`); manca
  un'analisi sistematica del 2008–2013, che con le serie corte che abbiamo
  (reddito dal 2012, imprese dal 2018) è dove i dati ci tradiscono.
- **Dichiarare la finestra**: le serie economiche sono di 6–11 anni, quelle
  ambientali di 20. Un trend su sei anni è una fotografia, non una tendenza.

## 6. Cosa sono i dati e cosa no, da dire a voce

- Tutto è **descrittivo**, nessun nesso causale (WORKING-PAPER §8).
- Tutte le relazioni sono **fra comuni**, non fra persone.
- I 205 comuni **non sono osservazioni indipendenti** (autocorrelazione spaziale
  alta: Moran 0,34–0,44).
- Il progetto è nato per **rifiutare i dati che sembrano raccontare bene**: metà
  del valore è nelle correzioni, non nei titoli.

## 7. Una nota sull'incontro, non sui dati

Hai scelto di non dire che il lavoro è stato fatto in gran parte con un
assistente di IA. Io lo direi, e prima che lo chieda lui. Tre ragioni, in
ordine di peso:

1. Il progetto lo rivela da sé: il repository, i commit e il working paper
   sono pieni di tracce del metodo. Se lo scopre lui, il problema non è
   l'IA, è che non gliel'hai detto.
2. Il tuo vantaggio è proprio il resto: decidere le domande, dichiarare i
   limiti, rileggere ogni testo (lo hai fatto il 23 settembre). Un parlamentare
   che ha a che fare con consulenti ed uffici studi capisce subito la differenza
   fra strumento e responsabilità.
3. Il progetto ha un'etica del metodo che si presta a questa conversazione: dice
   «ho sbagliato undici volte e questo è come me ne sono accorto». Lo stesso
   spirito vale per l'autore.

Nel repository, a oggi, non c'è una riga che dichiari l'uso dell'IA né nel sito
né nel README. Se vuoi, la aggiungo, in una frase, dove la metti tu.

**Occhio anche a**: un onorevole può chiedere i dati «su cosa fare»: il progetto
non fa raccomandazioni di politica pubblica e non dovrebbe. La risposta onesta è
«questi sono i fatti, questi i limiti, e per la politica servono altri dati,
come la finanza locale o la sanità, che non abbiamo».
