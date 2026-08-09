# Nota metodologica (MET-1…MET-11)

> **Cos'è.** Le decisioni che governano il progetto: *perché* misuriamo come
> misuriamo. È la base di credibilità — qualunque grafico, testo o titolo deve
> essere coerente con quanto scritto qui. Le regole nascono in parte dal
> progetto gemello su Donostia, in parte dai problemi specifici incontrati sui
> dati bresciani.
>
> ## ⚠️ BOZZA — lavori in corso
>
> **Questo documento è stato scritto in anticipo e non è definitivo.** Va
> riscritto e completato **alla fine**, quando i dati saranno tutti scaricati,
> le analisi fatte e le storie scelte: solo allora si saprà davvero quali
> decisioni metodologiche hanno governato il progetto, perché diverse
> nasceranno da problemi che ancora non abbiamo incontrato.
>
> Cosa vale già oggi: le undici regole qui elencate sono reali, applicate nella
> pipeline e in parte coperte da test. MET-9 in particolare nasce da un errore
> effettivamente commesso (§MET-9) e ha già cambiato un titolo del progetto.
>
> Cosa mancherà finché non si chiude l'analisi: le regole che riguardano
> **come si scelgono e si raccontano le storie** — soglie, criteri di
> inclusione di un indicatore in una narrazione, trattamento dei casi limite
> che emergeranno dai dati. Nel progetto Donostia queste sono arrivate dalle
> revisioni esterne, cioè dopo aver scritto i relati.

---

## MET-1 — Unità locale non è impresa

Il registro ASIA conta **unità locali**: lo stabilimento, l'ufficio, il
cantiere. Una società con sede a Milano e un capannone a Lumezzane produce una
unità locale a Lumezzane; un gruppo con dieci filiali produce dieci unità
locali. Quindi:

- **mai scrivere «imprese» dove il dato dice «unità locali»**, e mai contare le
  unità locali come se fossero aziende distinte;
- la **classe dimensionale è dell'unità locale, non del gruppo**: uno
  stabilimento da 300 addetti di una multinazionale e una fabbrica indipendente
  da 300 addetti sono indistinguibili nel dato;
- gli **addetti sono medie annue**, quindi hanno decimali e non vanno
  presentati come teste;
- una riorganizzazione societaria che sposta la sede legale di un'unità
  cambia i numeri **senza che sia cambiato nulla nel mondo reale**. È la
  causa più probabile di variazioni brusche e isolate.

## MET-2 — Il soggetto è la provincia; i livelli si dichiarano sempre

**Decisione presa (agosto 2026): il soggetto è la provincia**, raccontata
attraverso i suoi 205 comuni; il capoluogo è un caso privilegiato con due
approfondimenti dedicati, non il protagonista.

I tre livelli — 205 comuni, provincia (`ITC47`), comune di Brescia (`017029`)
— non sono intercambiabili e la scelta non è mai neutra: il capoluogo pesa il
21 % dell'occupazione provinciale e il 16 % della popolazione, quindi
«Brescia» e «il bresciano» danno risposte diverse alla stessa domanda.

**Il capoluogo va trattato come outlier dichiarato.** Con 199.853 abitanti
contro una mediana attorno ai 2.000, in una coropletica satura la scala e in
una correlazione la guida: servono classi o scale robuste nelle mappe e il
leave-one-out nelle correlazioni (MET-5).

Regole operative:

- ogni grafico dichiara il livello nel titolo o nella legenda, non nelle note;
- **la coropletica è per ciò che è misurato sui 205 comuni**; ciò che esiste
  solo come aggregato provinciale diventa serie o scomposizione, mai mappa;
- quando città e provincia divergono, **la divergenza è il risultato**, non un
  fastidio da appianare.

## MET-3 — Un dato mancante non è uno zero

Le fonti dichiarano l'assenza in modi diversi: cella vuota, `Dato riservato`
(soppressione per riservatezza statistica), `-9999` (misura non valida ARPA).
Nessuno di questi è zero, e convertirli in zero produce mappe che mostrano
«nessun fenomeno» dove c'è «nessuna misura».

Nella pipeline il parser restituisce `None` su tutti i token di assenza e le
tabelle lasciano la cella vuota. Nell'interfaccia serve un **colore dedicato
al «nessun dato»**, distinto dal minimo della scala.

**Il caso limite trovato sul campo.** Nei flussi turistici 2024, per Gottolengo
tutte le righe di dettaglio sono `Dato riservato` ma la riga «Totale» dichiara
**0**: uno zero calcolato su celle soppresse. La pipeline lo marca
`zero_fittizio` in una colonna `stato` e lo esclude dalla tabella di sintesi.
Quarantacinque comuni su 178 hanno le presenze soppresse: su questo asse la
mappa è a buchi, e va detto.

## MET-4 — Schede di confidenza

Ogni indicatore porta il proprio livello di confidenza, visibile
nell'interfaccia e non relegato alle note:

| Livello | Significato | Esempi bresciani |
|---|---|---|
| `osservato` | misurato direttamente dalla fonte | popolazione residente, addetti ASIA, presenze turistiche |
| `derivato` | calcolato da altri indicatori osservati | addetti per 100 abitanti, quote per classe dimensionale |
| `proxy` | approssimazione di ciò che vorremmo misurare | prezzi di offerta immobiliare al posto delle transazioni; export regionale al posto del provinciale |

Accanto, l'elenco esplicito delle **assunzioni**. Un indicatore senza scheda
non entra nel sito.

## MET-5 — Correlazioni robuste, outlier dichiarati

Con 205 comuni si sta meglio che con i 19 barrios di Donostia, ma la
distribuzione è fortemente asimmetrica: **Brescia città è un ordine di
grandezza sopra tutto il resto** (199.853 abitanti contro una mediana attorno
ai 2.000) e i comuni del Garda sono estremi su qualunque cosa tocchi il
turismo.

Quindi ogni correlazione pubblicata porta:

1. **Pearson e Spearman** insieme — se divergono molto, la relazione è guidata
   da pochi punti;
2. un **leave-one-out** su Brescia città e sui comuni gardesani;
3. la dichiarazione esplicita se il coefficiente crolla senza di loro.

## MET-6 — Fallacia ecologica

Tutte le correlazioni di questo progetto sono **fra comuni**, non fra persone.
Che i comuni con più addetti manifatturieri abbiano redditi mediani più alti
non dice nulla su quanto guadagni un singolo operaio. Dove la lettura
individuale è tentante — reddito e cittadinanza, istruzione e occupazione —
l'avvertenza va **nel testo del grafico**, non in fondo alla pagina.

## MET-7 — Stato, cambio e traiettoria sono tre cose diverse

- **Stato**: dov'è alto oggi (Brescia città concentra 100.939 addetti).
- **Cambio**: dove si muove di più (la provincia guadagna 29.421 addetti fra
  2018 e 2023, la città è ferma).
- **Traiettoria**: la forma del percorso (l'aria migliora dal 2000 ma il
  miglioramento rallenta).

Ogni frase deve dichiarare quale delle tre afferma. È l'errore più facile da
commettere e il più difficile da notare dopo.

## MET-8 — Finestre temporali disomogenee, mai appiattite

La profondità cambia radicalmente per asse: aria dal 1992, meteo dal 1990,
redditi dal 2012, ASIA 2018–2023, turismo 2019–2024, percezione di sicurezza
dal 2022. Tagliare tutto alla finestra più corta butterebbe via trent'anni di
serie ambientali; sovrapporre serie di lunghezza diversa senza dirlo suggerisce
confronti che non reggono.

Regola: **mostrare ogni asse con la profondità che ha**, e rendere visibile la
differenza (assi temporali allineati, estensione della serie dichiarata,
tratteggio o ombreggiatura sui tratti non confrontabili).

E **il 2020–2021 spezza quasi tutto**: la discontinuità Covid va testata
esplicitamente, non attraversata con una linea di tendenza.

## MET-9 — Decomporre prima di titolare

> Questa regola nasce da un errore commesso in questo progetto, ed è la
> ragione per cui esiste il documento che state leggendo.

**Cosa era stato detto.** Dai totali ASIA risultava che nel comune di Brescia
gli addetti in unità locali con almeno 250 addetti fossero crollati da 20.111
a 13.775 fra 2018 e 2023 (dal 19,9 % al 13,6 %), mentre in provincia la stessa
classe teneva. Ne era stato tratto il titolo: *«l'assottigliamento del vertice
è un fenomeno urbano»*, con il sottinteso che la città stesse perdendo i suoi
grandi stabilimenti.

**Cosa dice la decomposizione per settore.** Scomponendo la stessa classe
dimensionale per divisione Ateco, la perdita è **quasi interamente in una sola
sezione**, la N — *attività amministrative e di supporto*:

| Divisione | 2018 | 2023 | Variazione |
|---|---|---|---|
| 78 · attività di ricerca e selezione del personale (somministrazione) | 6.418 | 2.251 | **−4.167** |
| 81 · servizi per edifici e paesaggio (pulizie, facility) | 3.123 | — | **−3.123** |
| 82 · supporto per le funzioni d'ufficio | 396 | 284 | −112 |
| 80 · vigilanza e investigazione | — | 522 | +522 |
| **Sezione N nel complesso** | **9.937** | **3.057** | **−6.880** |

E nel frattempo, nella stessa classe ≥250 addetti:

| | 2018 | 2023 | Variazione |
|---|---|---|---|
| Manifattura (sezione C) | 4.448 | 4.397 | **−51, sostanzialmente stabile** |
| Sanità e assistenza sociale (Q) | 1.597 | 2.163 | +567 |
| Trasporti e magazzinaggio (H) | 1.640 | 2.438 | +798 |
| **Totale ≥250** | **20.111** | **13.775** | −6.336 |

**La manifattura grande, in città, non si è mossa.** Ciò che è sparito è
l'occupazione registrata delle grandi agenzie di somministrazione e delle
imprese di servizi esternalizzati. E questo è precisamente il tipo di dato che
MET-1 avverte di non prendere alla lettera: i lavoratori somministrati sono
attribuiti all'unità locale dell'agenzia, non a quella dove lavorano davvero,
e una riorganizzazione societaria basta a spostarne migliaia.

**Cosa resta da chiarire** prima di poter dire qualsiasi cosa su questo asse:
se la divisione 81 sia davvero scesa a zero o sia stata riclassificata; se il
crollo della somministrazione sia un fenomeno reale del mercato del lavoro
bresciano o un artefatto di attribuzione; e se lo stesso movimento si veda in
province comparabili (Bergamo è il controllo naturale).

**La regola.** *Nessun titolo su una variazione aggregata prima di averla
scomposta per settore e verificata contro almeno una spiegazione
amministrativa alternativa.* Un aggregato che si muove molto e all'improvviso
è, fino a prova contraria, un cambiamento di come si conta.

## MET-10 — I ripieghi si dichiarano nel grafico

Dove la grana giusta non è accessibile si usa quella disponibile, **etichettata
come tale sull'oggetto grafico**, non in una nota metodologica che nessuno
apre:

- **commercio estero**: il dato provinciale non è raggiungibile via API, si usa
  la **Lombardia**. Brescia è la seconda provincia manifatturiera della
  regione: è un contesto onesto, non un sostituto;
- **reati**: solo provinciali. Non esiste il dato comunale per Brescia, che non
  rientra fra i dodici «grandi comuni» della serie ISTAT;
- **prezzi immobiliari**: prezzi di **offerta** (annunci), non di transazione,
  finché non si passa dall'OMI.

## MET-11 — L'origine non è un proxy di nulla

Il paese di cittadinanza o di nascita **non è** un indicatore di reddito, di
disagio, di trasformazione urbana o di pressione sui servizi. Le tabelle sulle
origini sono descrittive e il testo deve dirlo.

In più, il censimento permanente permette una distinzione che quasi tutte le
narrazioni pubbliche sbagliano: **stranieri residenti**, **stranieri nati in
Italia** (seconde generazioni) e **italiani per acquisizione** sono tre
popolazioni diverse. Confonderle in un unico «stranieri» è un errore di misura
prima ancora che di racconto.

---

## Invarianti tecniche

Fatte valere dai test della pipeline (`pipeline/tests/`):

1. ogni `codice_istat` usato in qualunque tabella esiste nell'anagrafica dei
   205 comuni — **nessuna riga persa in silenzio** nei join;
2. le classi dimensionali sommano al totale;
3. i codici comune sono stringhe a sei cifre con lo zero iniziale (`017029`),
   mai numeri;
4. nessuna tabella prodotta è vuota;
5. i valori soppressi restano vuoti e, se qualificati, portano il proprio
   `stato`.

## Convenzioni di scrittura

- «unità locali», non «imprese» (MET-1);
- «addetti», non «occupati», quando la fonte è ASIA — gli **occupati** sono i
  residenti che lavorano, gli **addetti** sono i posti di lavoro localizzati, e
  a Brescia i secondi superano i primi di circa il 16 %;
- «provincia di Brescia» o «comune di Brescia», mai «Brescia» da solo quando il
  livello non è ovvio dal contesto;
- i numeri con separatore delle migliaia e senza decimali inutili; le medie
  annue degli addetti arrotondate all'unità nei testi, con il decimale
  conservato nei dati.
