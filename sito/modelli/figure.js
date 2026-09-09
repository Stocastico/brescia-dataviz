(function () {
  "use strict";
  var G = window.GRAFICI, DATI = window.DATI;

  // L'altezza della barra appiccicosa alimenta `scroll-margin-top` e la
  // posizione della figura: misurarla evita di doverla scrivere due volte.
  var barra = document.querySelector("nav.toc");
  function misuraBarra() {
    document.documentElement.style.setProperty("--navh", (barra.offsetHeight + 6) + "px");
  }
  misuraBarra();
  window.addEventListener("resize", misuraBarra);

  // --- storia 1: la mappa che scorre ---------------------------------
  var mappa = G.mappa(document.getElementById("mappa-popolazione"), {
    metrica: "crescita_popolazione",
    decimali: 2,
    descrizione: "Mappa dei 205 comuni della provincia di Brescia colorati per crescita annua della popolazione"
  });

  if (mappa) {
    var crescita = G.valoriDi("crescita_popolazione");
    var inCalo = Object.keys(crescita).filter(function (c) { return crescita[c] < 0; });
    var peggiori = Object.keys(crescita).sort(function (a, b) { return crescita[a] - crescita[b]; }).slice(0, 10);
    var inCrescita = Object.keys(crescita).filter(function (c) { return crescita[c] > 0; });
    var didascalia = document.getElementById("didascalia-popolazione");
    var testi = {
      tutti: "Tasso annuo composto per comune. Il blu è calo, il rosso è crescita, il grigio in mezzo è «non si muove».",
      calo: "<b>I " + inCalo.length + " comuni che perdono abitanti</b>, sugli altri sbiaditi.",
      peggiori: "<b>Le dieci cadute più rapide</b>: tutte di montagna.",
      grumi: "<b>I comuni in calo, di nuovo</b>: guardate come si toccano fra loro.",
      pianura: "<b>I " + inCrescita.length + " comuni che crescono</b>: la pianura attorno alla città e il lago."
    };
    var selezioni = { tutti: null, calo: inCalo, peggiori: peggiori, grumi: inCalo, pianura: inCrescita };

    G.scrollytelling(document.getElementById("scrolly-popolazione"), function (indice, passo) {
      var nome = passo.getAttribute("data-passo");
      mappa.evidenzia(selezioni[nome]);
      didascalia.innerHTML = testi[nome];
    });
  }

  // --- storia 1: lo scatter dimensione/crescita -----------------------
  var popolazione = G.metrica("popolazione");
  if (popolazione) {
    var primoAnno = popolazione.periods[0];
    var iniziale = G.valoriDi("popolazione", primoAnno);
    var tasso = G.valoriDi("crescita_popolazione");
    var puntiPopolazione = Object.keys(tasso).filter(function (c) { return iniziale[c]; }).map(function (c) {
      return {
        x: Math.log10(iniziale[c]), y: tasso[c], nome: G.nomeComune(c),
        evidenza: DATI.comuni[c][1] === 1, etichetta: DATI.comuni[c][1] === 1
      };
    });
    var mediane = function (lista) {
      var ordinati = lista.slice().sort(function (a, b) { return a - b; });
      return ordinati[Math.floor(ordinati.length / 2)];
    };
    G.scatter(document.getElementById("scatter-popolazione"), {
      punti: puntiPopolazione,
      etichettaX: "popolazione " + primoAnno + " (scala logaritmica)",
      etichettaY: "crescita %/anno",
      decimaliX: 1, decimaliY: 2,
      formattaX: function (v) { return G.num(Math.round(Math.pow(10, v))); },
      medianaX: mediane(puntiPopolazione.map(function (p) { return p.x; })),
      medianaY: mediane(puntiPopolazione.map(function (p) { return p.y; })),
      descrizione: "Grafico a dispersione: popolazione iniziale contro crescita annua, un punto per comune"
    });
  }

  // --- storia 1bis: da dove viene la variazione ------------------------
  var demografia = DATI.demografia;
  if (demografia && demografia.provincia) {
    var prov = demografia.provincia;
    // L'aggiustamento statistico è in fondo e in grigio: è contabilità, non
    // demografia, e messo fra le altre barre si leggerebbe come una di loro.
    var voci = [
      { nome: "migrazione estera", valore: prov.estera },
      { nome: "migrazione interna", valore: prov.interna },
      { nome: "saldo naturale", valore: prov.naturale },
      { nome: "aggiustamento statistico", valore: prov.aggiustamento, colore: "--muted" }
    ];
    if (prov.territorio) voci.push({ nome: "variazioni territoriali", valore: prov.territorio });
    G.barre(document.getElementById("barre-demografia"), {
      voci: voci, conSegno: true, larghezzaEtichette: 200,
      etichettaVoci: "componente", unita: "persone",
      descrizione: "Barre divergenti: le componenti della variazione di popolazione provinciale"
    });

    var puntiDemografia = Object.keys(demografia.comuni).map(function (c) {
      var v = demografia.comuni[c];
      return {
        x: v.naturale, y: v.interna, nome: G.nomeComune(c),
        evidenza: DATI.comuni[c][1] === 1, etichetta: DATI.comuni[c][1] === 1
      };
    });
    G.scatter(document.getElementById("scatter-demografia"), {
      punti: puntiDemografia,
      etichettaX: "saldo naturale (‰ del " + demografia.primo + ")",
      etichettaY: "migrazione interna (‰)",
      decimaliX: 1, decimaliY: 1,
      medianaX: 0, medianaY: 0,
      descrizione: "Grafico a dispersione: saldo naturale contro migrazione interna, un punto per comune"
    });
  }

  // --- storia 2: convergenza contro artefatto -------------------------
  var reddito = G.metrica("reddito_medio");
  if (reddito) {
    var annoI = reddito.periods[0], annoF = reddito.periods[reddito.periods.length - 1];
    var redditoI = G.valoriDi("reddito_medio", annoI);
    var redditoF = G.valoriDi("reddito_medio", annoF);
    var crescitaR = G.valoriDi("crescita_reddito");
    var contenitoreReddito = document.getElementById("scatter-reddito");

    function disegnaReddito(quale) {
      contenitoreReddito.innerHTML = "";
      var base = quale === "iniziale" ? redditoI : redditoF;
      var punti = Object.keys(crescitaR).filter(function (c) { return base[c]; }).map(function (c) {
        return {
          x: base[c], y: crescitaR[c], nome: G.nomeComune(c),
          evidenza: DATI.comuni[c][1] === 1, etichetta: DATI.comuni[c][1] === 1
        };
      });
      G.scatter(contenitoreReddito, {
        punti: punti,
        etichettaX: "reddito medio " + (quale === "iniziale" ? annoI : annoF) + " (euro)",
        etichettaY: "crescita %/anno",
        decimaliX: 0, decimaliY: 2,
        descrizione: "Grafico a dispersione fra reddito e crescita del reddito, un punto per comune"
      });
    }

    G.comandi(document.getElementById("comandi-reddito"), [
      { etichetta: "reddito di partenza (" + annoI + ")", quale: "iniziale" },
      { etichetta: "reddito finale (" + annoF + "): l'artefatto", quale: "finale" }
    ], function (voce) { disegnaReddito(voce.quale); });
    disegnaReddito("iniziale");
  }

  // --- storia 5: il confronto con le altre province --------------------
  var confronto = DATI.confronto;
  if (confronto && confronto.misure) {
    var contenitoreProvince = document.getElementById("grafico-province");
    var vociProvince = [
      { etichetta: "unità locali sotto i 10", chiave: "ul_micro", unita: "%", decimali: 1 },
      { etichetta: "addetti sotto i 10", chiave: "addetti_micro", unita: "%", decimali: 1 },
      { etichetta: "addetti per unità locale", chiave: "dimensione", unita: "addetti", decimali: 2 },
      { etichetta: "manifattura", chiave: "manifattura", unita: "%", decimali: 1 },
      { etichetta: "crescita", chiave: "crescita", unita: "%/anno", decimali: 2 }
    ];

    function disegnaProvince(voce) {
      contenitoreProvince.innerHTML = "";
      var misura = confronto.misure[voce.chiave];
      if (!misura) return;
      G.sciame(contenitoreProvince, {
        valori: misura.valori,
        nomi: confronto.nomi,
        evidenziati: { "017": "Brescia", "016": "Bergamo" },
        mediana: misura.mediana,
        etichetta: voce.etichetta + (voce.unita ? " (" + voce.unita + ")" : ""),
        decimali: voce.decimali,
        descrizione: "Distribuzione delle province italiane per " + voce.etichetta
      });
    }

    G.comandi(document.getElementById("comandi-province"), vociProvince.map(function (v) {
      return { etichetta: v.etichetta, voce: v };
    }), function (scelta) { disegnaProvince(scelta.voce); });
    disegnaProvince(vociProvince[0]);
  }

  // --- storia 7: il turismo fra le province ----------------------------
  var turismo = DATI.turismo;
  if (turismo && turismo.misure) {
    var contenitoreTurismo = document.getElementById("grafico-turismo");
    var vociTurismo = [
      { etichetta: "presenze", chiave: "presenze", unita: "notti", decimali: 0 },
      { etichetta: "presenze per abitante", chiave: "per_abitante", unita: "notti", decimali: 1 },
      { etichetta: "quota dall'estero", chiave: "estera", unita: "%", decimali: 1 },
      { etichetta: "campeggi e villaggi", chiave: "campeggi", unita: "%", decimali: 1 },
      { etichetta: "permanenza media", chiave: "permanenza", unita: "notti", decimali: 2 },
      { etichetta: "ripresa dal 2019", chiave: "ripresa", unita: "%", decimali: 1 }
    ];

    function disegnaTurismo(voce) {
      contenitoreTurismo.innerHTML = "";
      var misura = turismo.misure[voce.chiave];
      if (!misura) return;
      G.sciame(contenitoreTurismo, {
        valori: misura.valori,
        nomi: turismo.nomi,
        evidenziati: { "017": "Brescia" },
        mediana: misura.mediana,
        etichetta: voce.etichetta + (voce.unita ? " (" + voce.unita + ")" : ""),
        decimali: voce.decimali,
        descrizione: "Distribuzione delle province italiane per " + voce.etichetta
      });
    }

    G.comandi(document.getElementById("comandi-turismo"), vociTurismo.map(function (v) {
      return { etichetta: v.etichetta, voce: v };
    }), function (scelta) { disegnaTurismo(scelta.voce); });
    disegnaTurismo(vociTurismo[0]);

    // Le due componenti stanno sullo stesso asse perché sono la stessa unità:
    // notti. La quota estera è la loro distanza, e si legge senza scriverla.
    if (turismo.serie && turismo.serie.length) {
      var anniTur = turismo.serie.map(function (v) { return v.anno; });
      G.serie(document.getElementById("serie-turismo"), {
        periodi: anniTur,
        unita: "presenze",
        decimali: 0,
        linee: [
          { nome: "dall'estero", valori: turismo.serie.map(function (v) { return v.estero; }) },
          { nome: "dall'Italia", valori: turismo.serie.map(function (v) { return v.italia; }) }
        ],
        descrizione: "Presenze turistiche annuali in provincia di Brescia, distinte fra clienti residenti all'estero e in Italia"
      });
    }

    // Lo scarto fra le due fonti, disegnato invece che raccontato: sta tutto
    // sopra lo zero e sale, ed è il punto.
    if (turismo.fonti && turismo.fonti.length) {
      G.colonne(document.getElementById("fonti-turismo"), {
        voci: turismo.fonti.map(function (f) {
          return {
            etichetta: f.anno,
            valore: f.scarto,
            nota: G.num(f.regione, 0) + " contro " + G.num(f.istat, 0)
          };
        }),
        unita: "%",
        decimali: 1,
        etichettaX: "anno",
        etichettaY: "quanto Regione Lombardia sta sopra ISTAT (%)",
        colonnaNota: "presenze, somma dei comuni contro totale provinciale",
        descrizione: "Scarto percentuale fra la somma dei comuni di Regione Lombardia e il totale provinciale ISTAT, anno per anno"
      });
    }
  }

  // --- storia 4: le due economie --------------------------------------
  var contenitoreEconomie = document.getElementById("mappa-economie");
  if (contenitoreEconomie && G.metrica("specializzazione")) {
    var didascaliaEconomie = document.getElementById("didascalia-economie");
    var testiEconomie = {
      specializzazione: "Quota nella manifattura meno quota in alloggio e ristorazione. Rosso = manifatturiero, blu = turistico.",
      quota_manifattura: "<b>Quota di addetti nella manifattura</b>: più scuro, più manifatturiero.",
      quota_alloggio_ristorazione: "<b>Quota di addetti in alloggio e ristorazione</b>: più scuro, più turistico."
    };

    function disegnaEconomie(id) {
      contenitoreEconomie.innerHTML = "";
      G.mappa(contenitoreEconomie, {
        metrica: id, decimali: 1,
        descrizione: "Mappa dei comuni della provincia di Brescia per specializzazione settoriale"
      });
      didascaliaEconomie.innerHTML = testiEconomie[id];
    }

    G.comandi(document.getElementById("comandi-economie"), [
      { etichetta: "le due insieme", id: "specializzazione" },
      { etichetta: "manifattura", id: "quota_manifattura" },
      { etichetta: "alloggio e ristorazione", id: "quota_alloggio_ristorazione" }
    ], function (voce) { disegnaEconomie(voce.id); });
    disegnaEconomie("specializzazione");
  }

  // --- storia 3: la decomposizione ------------------------------------
  var scomposizione = DATI.decomposizione;
  function accorcia(testo, quanti) {
    return testo.length > quanti ? testo.slice(0, quanti - 1) + "…" : testo;
  }
  if (scomposizione && scomposizione.anni) {
    G.serie(document.getElementById("serie-capoluogo"), {
      periodi: scomposizione.anni,
      unita: "addetti",
      linee: [
        { nome: "tutte", valori: scomposizione.serie_totale },
        /* Nessun `|| 0` qui, e vale la pena dire perché. ASIA sopprime le celle
           piccole, e la classe ≥250 di un comune solo è esattamente il genere
           di cella che sopprime: un anno mancante trasformato in zero
           disegnerebbe una linea che precipita a fondo pagina, cioè
           **il titolo che questa storia esiste per smentire**. Un buco resta un
           buco (MET-3), e `serie()` lo salta. */
        { nome: "≥250 addetti", valori: scomposizione.serie_grandi }
      ],
      descrizione: "Due serie storiche degli addetti nel comune di Brescia"
    });

    G.barre(document.getElementById("barre-divisioni"), {
      voci: scomposizione.divisioni.map(function (d) {
        return { nome: accorcia(d.nome, 40), valore: d.variazione };
      }),
      conSegno: true,
      etichettaVoci: "divisione Ateco",
      unita: "addetti",
      descrizione: "Variazione degli addetti per divisione economica nella classe con almeno 250 addetti"
    });
  }
  // --- storia 6: l'aria e il clima -------------------------------------
  var clima = DATI.clima;
  if (clima && clima.inquinanti && clima.inquinanti.length) {
    // Le tre serie cominciano in anni diversi: il panel del biossido di azoto
    // regge due anni in piu' degli altri, quindi si allineano sull'asse piu'
    // lungo e le altre partono con dei buchi, che e' la verita' del dato.
    var anniAria = clima.inquinanti.reduce(function (piuLungo, i) {
      return i.anni.length > piuLungo.length ? i.anni : piuLungo;
    }, []);

    G.serie(document.getElementById("serie-aria"), {
      periodi: anniAria,
      unita: clima.inquinanti[0].unita,
      decimali: 1,
      linee: clima.inquinanti.map(function (i) {
        var perAnno = {};
        i.anni.forEach(function (anno, indice) { perAnno[anno] = i.serie[indice]; });
        return {
          nome: i.parametro.replace(" (SM2005)", ""),
          valori: anniAria.map(function (anno) {
            return perAnno[anno] === undefined ? null : perAnno[anno];
          })
        };
      }),
      descrizione: "Serie storiche della concentrazione media annua di PM10, biossido di azoto e ozono nelle centraline bresciane"
    });
  }

  if (clima && clima.temperatura && clima.temperatura.anomalie.length) {
    // Gli anni scartati (meno di meta' panel presente) devono comparire come
    // buchi dichiarati, non sparire: una colonna assente accanto a una colonna
    // quasi nulla e' indistinguibile da «non e' successo niente», ed e' la
    // confusione che MET-3 vieta.
    var perAnno = {};
    clima.temperatura.anomalie.forEach(function (a) { perAnno[a.anno] = a; });
    var anniClima = clima.temperatura.anomalie.map(function (a) { return +a.anno; });
    var vociClima = [];
    for (var y = Math.min.apply(null, anniClima); y <= Math.max.apply(null, anniClima); y++) {
      var trovato = perAnno[String(y)];
      vociClima.push({
        etichetta: String(y),
        valore: trovato ? trovato.valore : null,
        nota: trovato
          ? trovato.stazioni + (trovato.stazioni === 1 ? " stazione" : " stazioni")
          : "meno di metà delle stazioni osservate"
      });
    }

    G.colonne(document.getElementById("colonne-clima"), {
      voci: vociClima,
      unita: "°C",
      decimali: 2,
      etichettaX: "anno",
      etichettaY: "scostamento (°C)",
      colonnaNota: "stazioni",
      descrizione: "Scostamento annuo della temperatura media dalla base 2004-2013, una colonna per anno"
    });
  }

  // --- storia 9: i salari -----------------------------------------------
  var salari = DATI.salari;
  if (salari && salari.anni && salari.anni.length) {
    /* Le due linee si toccano nell'ultimo anno per costruzione, come nella storia
       della casa: li' l'inflazione da scontare e' zero. */
    G.serie(document.getElementById("serie-salari"), {
      periodi: salari.anni,
      unita: "€",
      linee: [
        { nome: "euro " + salari.anno_base, valori: salari.reali },
        { nome: "euro correnti", valori: salari.correnti }
      ],
      descrizione: "Retribuzione annua media dei dipendenti privati non agricoli in provincia di Brescia, in euro correnti e costanti"
    });

    G.sciame(document.getElementById("sciame-salari"), {
      valori: salari.variazioni,
      nomi: salari.nomi,
      evidenziati: { "017": "Brescia", "015": "Milano" },
      mediana: salari.mediana_variazione,
      etichetta: "variazione reale " + salari.anni[0] + "–" + salari.anno_base + " (%)",
      decimali: 1,
      descrizione: "Distribuzione delle province italiane per variazione reale della retribuzione media"
    });
  }

  // --- storia 8: la casa ------------------------------------------------
  var casa = DATI.casa;
  if (casa && casa.anni && casa.anni.length) {
    /* Due righelli sulla stessa serie. Le due linee si toccano nell'ultimo
       anno per costruzione, perche' li' l'inflazione da scontare e' zero, e non e'
       un artefatto da nascondere: e' la lettura del grafico. */
    var tabelleCasa = document.getElementById("tabelle-casa");
    var serieePrezzo = G.serie(document.getElementById("serie-casa-prezzo"), {
      periodi: casa.anni,
      unita: "€/m²",
      tabellaIn: tabelleCasa,
      linee: [
        { nome: "euro " + casa.anno_base_reale, valori: casa.reali },
        { nome: "euro correnti", valori: casa.correnti }
      ],
      descrizione: "Prezzo al metro quadro delle abitazioni civili nel comune di Brescia, in euro correnti e in euro costanti"
    });

    var seriaVolumi = G.serie(document.getElementById("serie-casa-forbice"), {
      periodi: casa.anni_ntn,
      unita: casa.anni_ntn[0] + " = 100",
      tabellaIn: tabelleCasa,
      linee: [
        { nome: "compravendite", valori: casa.indice_ntn },
        { nome: "prezzo reale", valori: casa.indice_reale }
      ],
      descrizione: "Prezzo reale al metro quadro e numero di compravendite residenziali nel comune di Brescia, indicizzati"
    });

    /* Lo scrollytelling della storia della casa. Quella sulla popolazione lo usa su **una** mappa
       riletta cinque volte; qui l'argomento e' una catena, e i passi la
       percorrono: prima il prezzo come e' scritto, poi lo stesso prezzo in euro
       di oggi, poi il divario fra i due, e infine i volumi. Le linee si
       accendono una alla volta sulla stessa figura, e la scala non si muove
       (`mostra()` non ricalcola gli assi apposta): quello che cambia fra un
       passo e l'altro e' solo cosa si guarda.

       Il pannello tiene **due** figure e non una, perche' i volumi sono in
       un'altra unita' e su un'altra finestra di anni. Due sono il massimo
       sensato: allo scambio il lettore deve riconoscere che il grafico e'
       cambiato, e con quattro non lo riconoscerebbe piu'.

       Sotto i 900 px il CSS spegne tutto questo: le due figure tornano
       visibili e impilate, i passi diventano cinque paragrafi, e la storia si
       legge come si leggeva prima. */
    var scrollyCasa = document.getElementById("scrolly-casa");
    if (scrollyCasa && serieePrezzo && seriaVolumi) {
      var figurePrezzo = document.getElementById("fig-casa-prezzo");
      var figureVolumi = document.getElementById("fig-casa-forbice");

      /* La didascalia **non** cambia a ogni passo, e in questo lo scrollytelling
         della storia della casa differisce da quello della prima. Li' la figura e'
         sempre la stessa mappa e la didascalia e' l'unica cosa che puo' dire
         cosa sia acceso; qui il testo del passo sta a fianco e lo dice gia', e
         una didascalia che passa da due righe a tre farebbe sobbalzare di venti
         pixel un pannello che sta fermo per mestiere. */
      var passiCasa = {
        correnti: { figura: figurePrezzo, manico: serieePrezzo, linee: [1] },
        reali:    { figura: figurePrezzo, manico: serieePrezzo, linee: [0, 1] },
        divario:  { figura: figurePrezzo, manico: serieePrezzo, linee: [0, 1] },
        volumi:   { figura: figureVolumi, manico: seriaVolumi,  linee: [0] },
        insieme:  { figura: figureVolumi, manico: seriaVolumi,  linee: [0, 1] }
      };

      G.scrollytelling(scrollyCasa, function (indice, passo) {
        var conf = passiCasa[passo.getAttribute("data-passo")];
        if (!conf) return;
        figurePrezzo.classList.toggle("on", conf.figura === figurePrezzo);
        figureVolumi.classList.toggle("on", conf.figura === figureVolumi);
        conf.manico.mostra(conf.linee);
      });
    }

    if (casa.zone && casa.zone.anni) {
      /* Le tre linee sono **inviluppi**, non tre zone seguite nel tempo: il
         massimo e il minimo si ricalcolano ogni anno. In cima non cambia mai
         inquilino, in fondo cambia tre volte, e senza il nome accanto al punto
         il grafico direbbe che una singola zona ha fatto quel percorso. */
      G.serie(document.getElementById("serie-casa-zone"), {
        periodi: casa.zone.anni,
        unita: "€/m² del " + casa.anno_base_reale,
        linee: [
          { nome: "la più cara", valori: casa.zone.alta, note: casa.zone.alta_zona },
          { nome: "la mediana", valori: casa.zone.mediana },
          { nome: "la più economica", valori: casa.zone.bassa, note: casa.zone.bassa_zona }
        ],
        descrizione: "Prezzo reale al metro quadro nelle zone OMI del comune di Brescia: la zona più cara, quella mediana e la più economica di ogni anno"
      });
    }
  }

  if (G.metrica("variazione_prezzo_reale")) {
    G.mappa(document.getElementById("mappa-casa"), {
      metrica: "variazione_prezzo_reale", decimali: 2,
      descrizione: "Mappa dei comuni della provincia di Brescia per variazione reale del prezzo delle case fra il 2004 e il 2025"
    });
  }
})();
