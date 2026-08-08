# Dati di riferimento

Un solo file, per ora. Non è output di una pipeline — non esiste ancora una
pipeline — ma la **tabella anagrafica** su cui tutto il resto si aggancerà, già
popolata con i primi indicatori verificati durante la ricognizione. Serve a due
cose: rendere immediatamente utilizzabile la geografia della provincia, e
lasciare per iscritto numeri che altrimenti resterebbero solo nel testo di
`FONTI.md`.

## `comuni_provincia_brescia.csv`

I **205 comuni della provincia di Brescia**, uno per riga.

| Colonna | Cosa contiene | Fonte | Note |
|---|---|---|---|
| `codice_istat` | Codice ISTAT a 6 cifre (`017001`…`017206`) | ISTAT — *Elenco comuni italiani* | **La chiave di join** di tutto il progetto |
| `comune` | Denominazione in italiano | idem | |
| `popolazione_2024` | Popolazione residente al 31.12.2024 | ISTAT Censimento permanente, `DF_DCSS_FAM_POP_TV_1`, indicatore `RESPOP_AV` | 205/205 valorizzati |
| `unita_locali_2023` | Unità locali di imprese attive | ISTAT ASIA, `183_1163_DF_DICA_ASIAULP_TERRIFDATA_7` | 205/205 |
| `addetti_2023` | Addetti delle unità locali, media annua | idem, indicatore `LUEMPDAA` | 205/205; è un valore medio, quindi con decimali |
| `presenze_turistiche_2024` | Presenze turistiche (notti) | Regione Lombardia, `dati.lombardia.it/resource/vyxt-7jdx` | **133/205**: vuoto dove la fonte riporta «Dato riservato» o dove il comune non compare |

**Totali di controllo** (somma della colonna): popolazione **1.265.884** ·
unità locali **119.565** · addetti **479.418** · presenze **12.246.854**.

### Avvertenze

- **Le celle vuote non sono zeri.** Sulle presenze turistiche, in particolare,
  il vuoto significa «dato soppresso per riservatezza statistica o comune
  assente dalla rilevazione», non «nessun turista». Chi disegna una mappa deve
  renderlo come *nessun dato*, con un colore neutro dedicato.
- **Anni diversi in colonne diverse** (2023 per ASIA, 2024 per popolazione e
  turismo): è la disponibilità delle fonti, non una scelta. Qualsiasi rapporto
  fra colonne (addetti per abitante, presenze per abitante) mescola due anni e
  va dichiarato come tale.
- **`addetti_2023` conta le unità locali *situate* nel comune**, non i residenti
  occupati. Nei comuni con grandi insediamenti produttivi il valore può superare
  di molto la popolazione attiva: è una misura di dove sta il lavoro, non di chi
  lavora.
- Il file è una **fotografia della ricognizione di agosto 2026**. Quando nascerà
  la pipeline andrà rigenerato da essa, non aggiornato a mano.

### Come è stato costruito

Tutte le fonti sono interrogabili senza credenziali. Le ricette esatte —
endpoint, chiavi SDMX, header necessari e le trappole in cui sono già
inciampato — stanno in [`../FONTI.md`](../FONTI.md), §10 e §11.
