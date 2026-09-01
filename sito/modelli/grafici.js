/* Grafici in SVG, disegnati a mano, senza librerie.
 *
 * Il motivo non è il gusto della fatica: è che il documento deve restare un
 * unico file autocontenuto che si apre da disco e funziona fra dieci anni.
 * Ogni dipendenza a runtime toglie una di queste proprietà.
 *
 * Convenzioni rispettate ovunque:
 * - i colori vengono dalle variabili CSS, mai scritti qui: la tavolozza è
 *   quella di `donostia-dataviz` e sta tutta in cima a `stile.css`;
 * - «nessun dato» ha un colore proprio e non è mai lo zero della scala;
 * - ogni mappa e ogni grafico hanno una tabella-specchio navigabile da
 *   tastiera: una coropletica da sola è inaccessibile;
 * - i numeri si formattano in italiano.
 */
(function () {
  "use strict";

  const NS = "http://www.w3.org/2000/svg";
  const DATI = window.DATI;

  // --- utilità ---------------------------------------------------------

  function el(nome, attributi, genitore) {
    const nodo = document.createElementNS(NS, nome);
    for (const chiave in attributi || {}) {
      if (attributi[chiave] !== null && attributi[chiave] !== undefined) {
        nodo.setAttribute(chiave, attributi[chiave]);
      }
    }
    if (genitore) genitore.appendChild(nodo);
    return nodo;
  }

  function css(nome) {
    return getComputedStyle(document.documentElement).getPropertyValue(nome).trim();
  }

  function num(valore, decimali) {
    if (valore === null || valore === undefined || Number.isNaN(valore)) return "n.d.";
    return valore.toLocaleString("it-IT", {
      minimumFractionDigits: decimali || 0,
      maximumFractionDigits: decimali === undefined ? 0 : decimali,
    });
  }

  function nomeComune(codice) {
    const riga = DATI.comuni[codice];
    return riga ? riga[0] : codice;
  }

  function metrica(id) {
    return DATI.metriche[id];
  }

  function valoriDi(id, periodo) {
    const m = metrica(id);
    if (!m) return {};
    const scelto = periodo || m.periods[m.periods.length - 1];
    const fuori = {};
    for (const codice in m.values) {
      const v = m.values[codice][scelto];
      if (v !== undefined && v !== null) fuori[codice] = v;
    }
    return fuori;
  }

  // --- il suggerimento (uno solo, riusato) -----------------------------

  const suggerimento = document.createElement("div");
  suggerimento.id = "tip";
  suggerimento.setAttribute("role", "status");
  document.body.appendChild(suggerimento);

  function mostraSuggerimento(evento, html) {
    suggerimento.innerHTML = html;
    suggerimento.classList.add("on");
    const riquadro = suggerimento.getBoundingClientRect();
    let x = evento.clientX + 14;
    let y = evento.clientY + 14;
    if (x + riquadro.width > window.innerWidth - 8) x = evento.clientX - riquadro.width - 14;
    if (y + riquadro.height > window.innerHeight - 8) y = evento.clientY - riquadro.height - 14;
    suggerimento.style.left = x + "px";
    suggerimento.style.top = y + "px";
  }

  function nascondiSuggerimento() {
    suggerimento.classList.remove("on");
  }

  // --- scale di colore -------------------------------------------------

  const SEQUENZIALE = ["--seq-1", "--seq-2", "--seq-3", "--seq-4", "--seq-5", "--seq-6", "--seq-7", "--seq-8"];
  const CATEGORICHE = ["--serie-1", "--serie-2", "--serie-3", "--serie-4", "--serie-5"];
  const DIVERGENTE = [
    "--div-neg-4", "--div-neg-3", "--div-neg-2", "--div-neg-1",
    "--div-zero",
    "--div-pos-1", "--div-pos-2", "--div-pos-3", "--div-pos-4",
  ];

  /* Rotture per quantile: con 205 comuni e distribuzioni storte (il capoluogo
     è un ordine di grandezza sopra) le classi a intervallo uguale metterebbero
     duecento comuni nella prima. */
  function rottureQuantile(valori, quante) {
    const ordinati = valori.slice().sort(function (a, b) { return a - b; });
    const rotture = [];
    for (let i = 1; i < quante; i++) {
      rotture.push(ordinati[Math.floor((ordinati.length * i) / quante)]);
    }
    return rotture;
  }

  /* Per le variazioni: classi simmetriche attorno allo zero, così il grigio
     centrale significa davvero «non si muove» e i due archi sono confrontabili.

     L'estremo non è il massimo assoluto ma il **95º percentile** dei valori
     assoluti: con il massimo, un solo comune fuori scala (qui Magasa, che perde
     il 2,9 % di abitanti l'anno) allarga la scala fino a schiacciare tutti gli
     altri in due classi pallide. I valori oltre l'estremo finiscono nella
     classe di fondo — sono fuori scala, ed è giusto che si vedano come tali. */
  function rottureSimmetriche(valori, quante) {
    const assoluti = valori.map(Math.abs).sort(function (a, b) { return a - b; });
    const estremo = assoluti[Math.floor(assoluti.length * 0.95)] || assoluti[assoluti.length - 1];
    const passo = estremo / (quante / 2);
    const rotture = [];
    for (let i = -quante / 2 + 1; i <= quante / 2 - 1; i++) rotture.push(i * passo);
    return rotture;
  }

  function classeDi(valore, rotture) {
    let indice = 0;
    while (indice < rotture.length && valore >= rotture[indice]) indice++;
    return indice;
  }

  function scala(valori, tipo) {
    const lista = Object.keys(valori).map(function (k) { return valori[k]; });
    if (!lista.length) return null;
    const chiavi = tipo === "diverging" ? DIVERGENTE : SEQUENZIALE;
    const rotture = tipo === "diverging"
      ? rottureSimmetriche(lista, chiavi.length)
      : rottureQuantile(lista, chiavi.length);
    const estremiVeri = [Math.min.apply(null, lista), Math.max.apply(null, lista)];
    return {
      colori: chiavi.map(css),
      rotture: rotture,
      // vero quando qualcuno sta oltre l'ultima rottura: la legenda lo dice
      tagliata: estremiVeri[0] < rotture[0] || estremiVeri[1] > rotture[rotture.length - 1],
      colore: function (valore) {
        if (valore === null || valore === undefined) return this.assente;
        return this.colori[classeDi(valore, rotture)];
      },
      assente: css("--nessun-dato"),
    };
  }

  function disegnaLegenda(contenitore, scalaColore, decimali, unita, quantiSenzaDato) {
    const legenda = document.createElement("div");
    legenda.className = "legend";

    const blocco = document.createElement("div");
    const barra = document.createElement("div");
    barra.className = "scale";
    scalaColore.colori.forEach(function (colore, indice) {
      const passo = document.createElement("span");
      passo.style.background = colore;
      const da = indice === 0 ? null : scalaColore.rotture[indice - 1];
      const a = indice === scalaColore.colori.length - 1 ? null : scalaColore.rotture[indice];
      passo.title = da === null ? "fino a " + num(a, decimali)
        : a === null ? "da " + num(da, decimali)
        : num(da, decimali) + " – " + num(a, decimali);
      barra.appendChild(passo);
    });
    blocco.appendChild(barra);

    const tacche = document.createElement("div");
    tacche.className = "ticks";
    const primo = document.createElement("span");
    primo.textContent = (scalaColore.tagliata ? "≤ " : "") + num(scalaColore.rotture[0], decimali);
    const ultimo = document.createElement("span");
    ultimo.textContent = (scalaColore.tagliata ? "≥ " : "") +
      num(scalaColore.rotture[scalaColore.rotture.length - 1], decimali);
    tacche.appendChild(primo);
    tacche.appendChild(ultimo);
    blocco.appendChild(tacche);
    legenda.appendChild(blocco);

    if (unita) {
      const misura = document.createElement("span");
      misura.textContent = unita;
      legenda.appendChild(misura);
    }

    // Il colore dell'assenza compare solo se qualcuno è davvero assente: una
    // voce di legenda sempre presente e quasi sempre inutile si smette di
    // leggere, e il giorno che serve non la si vede più.
    if (quantiSenzaDato) {
      const gruppo = document.createElement("span");
      gruppo.className = "swatches";
      const voce = document.createElement("span");
      voce.className = "sw";
      const quadratino = document.createElement("i");
      quadratino.className = "assente";
      voce.appendChild(quadratino);
      voce.appendChild(document.createTextNode(
        "nessun dato (" + quantiSenzaDato + (quantiSenzaDato === 1 ? " comune)" : " comuni)")));
      gruppo.appendChild(voce);
      legenda.appendChild(gruppo);
    }

    contenitore.appendChild(legenda);
  }

  // --- la tabella-specchio ---------------------------------------------

  function tabellaSpecchio(contenitore, intestazioni, righe, riassunto) {
    const dettagli = document.createElement("details");
    dettagli.className = "metric-expl";
    const titolo = document.createElement("summary");
    const etichetta = document.createElement("span");
    etichetta.className = "me-lab";
    etichetta.textContent = "i numeri";
    const testo = document.createElement("span");
    testo.textContent = riassunto || "Gli stessi numeri in tabella";
    const leva = document.createElement("span");
    leva.className = "me-tgl";
    titolo.appendChild(etichetta);
    titolo.appendChild(testo);
    titolo.appendChild(leva);
    dettagli.appendChild(titolo);

    const corpoDettagli = document.createElement("div");
    corpoDettagli.className = "me-body";
    const involucro = document.createElement("div");
    involucro.className = "rankwrap";
    const tabella = document.createElement("table");
    tabella.className = "rank";
    const testa = document.createElement("thead");
    const rigaTesta = document.createElement("tr");
    intestazioni.forEach(function (voce, indice) {
      const cella = document.createElement("th");
      cella.scope = "col";
      if (indice > 0) cella.className = "num";
      cella.textContent = voce;
      rigaTesta.appendChild(cella);
    });
    testa.appendChild(rigaTesta);
    tabella.appendChild(testa);
    const corpo = document.createElement("tbody");
    righe.forEach(function (riga) {
      const tr = document.createElement("tr");
      riga.forEach(function (cella, indice) {
        const td = document.createElement(indice === 0 ? "th" : "td");
        if (indice === 0) td.scope = "row";
        else td.className = "num";
        td.textContent = cella;
        tr.appendChild(td);
      });
      corpo.appendChild(tr);
    });
    tabella.appendChild(corpo);
    involucro.appendChild(tabella);
    corpoDettagli.appendChild(involucro);
    dettagli.appendChild(corpoDettagli);
    contenitore.appendChild(dettagli);
  }

  function provenienza(contenitore, m) {
    const scheda = document.createElement("p");
    scheda.className = "conf";
    const pallino = document.createElement("span");
    pallino.className = "dot " + m.confidence;
    scheda.appendChild(pallino);
    const grado = document.createElement("b");
    grado.textContent = m.confidence;
    scheda.appendChild(grado);
    let testo = " · " + m.source;
    if (m.assumptions && m.assumptions.length) testo += " · " + m.assumptions.join(" · ");
    scheda.appendChild(document.createTextNode(testo));
    contenitore.appendChild(scheda);
  }

  // --- la mappa --------------------------------------------------------

  const LARGHEZZA = 720;
  let contatoreTratteggi = 0;

  /* Il tratteggio dell'assenza. Un grigio da solo non basta: accanto al grigio
     neutro di una scala divergente sono due tinte quasi uguali, e «non lo
     sappiamo» finisce per sembrare «non si muove». Il tratto distingue le due
     cose anche in stampa e senza distinguere i colori. */
  function tratteggioAssenza(svg) {
    const id = "senza-dato-" + ++contatoreTratteggi;
    const defs = el("defs", null, svg);
    const pattern = el("pattern", {
      id: id, width: 6, height: 6, patternUnits: "userSpaceOnUse",
      patternTransform: "rotate(45)",
    }, defs);
    el("rect", { width: 6, height: 6, fill: css("--nessun-dato") }, pattern);
    el("line", {
      x1: 0, y1: 0, x2: 0, y2: 6,
      stroke: css("--nessun-dato-tratto"), "stroke-width": 2,
    }, pattern);
    return "url(#" + id + ")";
  }

  function proiezione() {
    let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
    DATI.geo.comuni.forEach(function (comune) {
      comune.g.forEach(function (anello) {
        anello.forEach(function (punto) {
          if (punto[0] < minX) minX = punto[0];
          if (punto[0] > maxX) maxX = punto[0];
          if (punto[1] < minY) minY = punto[1];
          if (punto[1] > maxY) maxY = punto[1];
        });
      });
    });
    // Equirettangolare con la longitudine compressa per la latitudine media:
    // su una provincia sono chilometri di errore, invisibili, e non serve
    // nessuna libreria di proiezioni.
    const k = Math.cos((((minY + maxY) / 2) * Math.PI) / 180);
    const larghezzaGeo = (maxX - minX) * k;
    const altezzaGeo = maxY - minY;
    const scala = LARGHEZZA / larghezzaGeo;
    const altezza = altezzaGeo * scala;
    return {
      altezza: altezza,
      x: function (lon) { return (lon - minX) * k * scala; },
      y: function (lat) { return altezza - (lat - minY) * scala; },
    };
  }

  const PROIEZIONE = proiezione();

  function tracciato(comune) {
    let d = "";
    comune.g.forEach(function (anello) {
      anello.forEach(function (punto, indice) {
        d += (indice ? "L" : "M") + PROIEZIONE.x(punto[0]).toFixed(1) + " " + PROIEZIONE.y(punto[1]).toFixed(1);
      });
      d += "Z";
    });
    return d;
  }

  function mappa(contenitore, opzioni) {
    const m = metrica(opzioni.metrica);
    if (!m) return null;
    const decimali = opzioni.decimali === undefined ? 1 : opzioni.decimali;

    const svg = el("svg", {
      viewBox: "0 0 " + LARGHEZZA + " " + PROIEZIONE.altezza,
      class: "mappa",
      role: "img",
      "aria-label": opzioni.descrizione || m.label,
    });
    contenitore.appendChild(svg);
    const riempimentoAssente = tratteggioAssenza(svg);

    const forme = {};
    DATI.geo.comuni.forEach(function (comune) {
      const forma = el("path", {
        d: tracciato(comune),
        stroke: css("--card"),
        "stroke-width": 0.5,
        "stroke-linejoin": "round",
      }, svg);
      forme[comune.c] = forma;
      forma.addEventListener("mousemove", function (evento) {
        const valore = forma.__valore;
        mostraSuggerimento(evento,
          "<b>" + nomeComune(comune.c) + "</b>" +
          (valore === undefined ? "nessun dato" : num(valore, decimali) + " " + m.unit));
      });
      forma.addEventListener("mouseleave", nascondiSuggerimento);
    });

    const piede = document.createElement("div");
    contenitore.appendChild(piede);

    let scalaCorrente = null;

    function aggiorna(periodo) {
      const valori = valoriDi(opzioni.metrica, periodo);
      scalaCorrente = scala(valori, m.kind);
      scalaCorrente.assente = riempimentoAssente;
      DATI.geo.comuni.forEach(function (comune) {
        const valore = valori[comune.c];
        forme[comune.c].__valore = valore;
        forme[comune.c].setAttribute("fill", scalaCorrente.colore(valore));
      });
      piede.innerHTML = "";
      const righe = Object.keys(valori)
        .sort(function (a, b) { return valori[b] - valori[a]; })
        .map(function (codice) { return [nomeComune(codice), num(valori[codice], decimali)]; });
      const senzaDato = DATI.geo.comuni.length - righe.length;
      disegnaLegenda(piede, scalaCorrente, decimali, m.unit, senzaDato);
      tabellaSpecchio(piede, ["comune", m.unit], righe,
        "Gli stessi numeri in tabella (" + righe.length + " comuni con dato" +
        (senzaDato ? ", " + senzaDato + " senza" : "") + ")");
      provenienza(piede, m);
    }

    aggiorna(opzioni.periodo);
    return { aggiorna: aggiorna, evidenzia: function (codici) {
      const insieme = codici ? {} : null;
      (codici || []).forEach(function (c) { insieme[c] = true; });
      DATI.geo.comuni.forEach(function (comune) {
        const dentro = !insieme || insieme[comune.c];
        forme[comune.c].setAttribute("opacity", dentro ? 1 : 0.25);
        forme[comune.c].setAttribute("stroke", dentro && insieme ? css("--ink") : css("--card"));
        forme[comune.c].setAttribute("stroke-width", dentro && insieme ? 1.2 : 0.5);
      });
    } };
  }

  // --- assi condivisi da scatter e serie -------------------------------

  function assi(svg, riquadro, scalaX, scalaY, etichetteX, etichetteY, decimaliX, decimaliY, formattaX, formattaY) {
    const gruppo = el("g", null, svg);
    etichetteY.forEach(function (valore) {
      const y = scalaY(valore);
      el("line", {
        x1: riquadro.sinistra, x2: riquadro.sinistra + riquadro.larghezza, y1: y, y2: y,
        stroke: css("--line"), "stroke-width": 1,
      }, gruppo);
      const testo = el("text", {
        x: riquadro.sinistra - 8, y: y + 4, "text-anchor": "end",
        fill: css("--muted"), "font-size": 11,
      }, gruppo);
      testo.textContent = formattaY ? formattaY(valore) : num(valore, decimaliY);
    });
    etichetteX.forEach(function (valore) {
      const x = scalaX(valore);
      const testo = el("text", {
        x: x, y: riquadro.alto + riquadro.altezza + 18, "text-anchor": "middle",
        fill: css("--muted"), "font-size": 11,
      }, gruppo);
      testo.textContent = formattaX ? formattaX(valore) : num(valore, decimaliX);
    });
    el("line", {
      x1: riquadro.sinistra, x2: riquadro.sinistra + riquadro.larghezza,
      y1: riquadro.alto + riquadro.altezza, y2: riquadro.alto + riquadro.altezza,
      stroke: css("--line"), "stroke-width": 1,
    }, gruppo);
    return gruppo;
  }

  function passi(minimo, massimo, quanti) {
    const grezzo = (massimo - minimo) / quanti;
    const potenza = Math.pow(10, Math.floor(Math.log10(grezzo)));
    const passo = [1, 2, 2.5, 5, 10].map(function (m) { return m * potenza; })
      .filter(function (p) { return p >= grezzo; })[0] || potenza * 10;
    const fuori = [];
    for (let v = Math.ceil(minimo / passo) * passo; v <= massimo + 1e-9; v += passo) fuori.push(v);
    return fuori;
  }

  // --- lo scatter dei quadranti ----------------------------------------

  function scatter(contenitore, opzioni) {
    const ALTEZZA = 420;
    const riquadro = { sinistra: 58, alto: 14, larghezza: LARGHEZZA - 78, altezza: ALTEZZA - 58 };
    const punti = opzioni.punti;
    if (!punti.length) return;

    const xs = punti.map(function (p) { return p.x; });
    const ys = punti.map(function (p) { return p.y; });
    const xMin = Math.min.apply(null, xs), xMax = Math.max.apply(null, xs);
    const yMin = Math.min.apply(null, ys), yMax = Math.max.apply(null, ys);
    const margineX = (xMax - xMin) * 0.05, margineY = (yMax - yMin) * 0.08;

    function sx(v) {
      return riquadro.sinistra + ((v - xMin + margineX) / (xMax - xMin + 2 * margineX)) * riquadro.larghezza;
    }
    function sy(v) {
      return riquadro.alto + riquadro.altezza -
        ((v - yMin + margineY) / (yMax - yMin + 2 * margineY)) * riquadro.altezza;
    }

    const svg = el("svg", {
      viewBox: "0 0 " + LARGHEZZA + " " + ALTEZZA,
      role: "img",
      "aria-label": opzioni.descrizione,
    });
    contenitore.appendChild(svg);

    assi(svg, riquadro, sx, sy,
      passi(xMin, xMax, 5), passi(yMin, yMax, 5),
      opzioni.decimaliX || 0, opzioni.decimaliY === undefined ? 1 : opzioni.decimaliY,
      opzioni.formattaX, opzioni.formattaY);

    // Le due mediane: sono i confini dei quadranti, e vanno viste.
    [["x", opzioni.medianaX, sx], ["y", opzioni.medianaY, sy]].forEach(function (coppia) {
      if (coppia[1] === undefined || coppia[1] === null) return;
      const posizione = coppia[2](coppia[1]);
      el("line", coppia[0] === "x"
        ? { x1: posizione, x2: posizione, y1: riquadro.alto, y2: riquadro.alto + riquadro.altezza,
            stroke: css("--line"), "stroke-dasharray": "3 3" }
        : { x1: riquadro.sinistra, x2: riquadro.sinistra + riquadro.larghezza, y1: posizione, y2: posizione,
            stroke: css("--line"), "stroke-dasharray": "3 3" }, svg);
    });

    punti.forEach(function (punto) {
      const cerchio = el("circle", {
        cx: sx(punto.x), cy: sy(punto.y), r: punto.evidenza ? 6 : 4,
        fill: punto.evidenza ? css("--coral") : css("--sea"),
        "fill-opacity": punto.evidenza ? 1 : 0.55,
        stroke: css("--card"), "stroke-width": punto.evidenza ? 2 : 0,
      }, svg);
      cerchio.addEventListener("mousemove", function (evento) {
        mostraSuggerimento(evento, "<b>" + punto.nome + "</b>" +
          opzioni.etichettaX + ": " +
          (opzioni.formattaX ? opzioni.formattaX(punto.x) : num(punto.x, opzioni.decimaliX || 0)) + "<br>" +
          opzioni.etichettaY + ": " + num(punto.y, opzioni.decimaliY === undefined ? 2 : opzioni.decimaliY));
      });
      cerchio.addEventListener("mouseleave", nascondiSuggerimento);
      if (punto.etichetta) {
        // Vicino al bordo destro l'etichetta si ribalta a sinistra, invece di
        // uscire dal riquadro come faceva Brescia.
        const vicinoAlBordo = sx(punto.x) > riquadro.sinistra + riquadro.larghezza - 70;
        const testo = el("text", {
          x: sx(punto.x) + (vicinoAlBordo ? -9 : 9), y: sy(punto.y) + 4,
          "text-anchor": vicinoAlBordo ? "end" : "start",
          fill: css("--ink2"), "font-size": 11,
        }, svg);
        testo.textContent = punto.nome;
      }
    });

    const testoX = el("text", {
      x: riquadro.sinistra + riquadro.larghezza / 2, y: ALTEZZA - 6,
      "text-anchor": "middle", fill: css("--ink2"), "font-size": 11.5,
    }, svg);
    testoX.textContent = opzioni.etichettaX;
    const testoY = el("text", {
      x: 0, y: 0, "text-anchor": "middle", fill: css("--ink2"), "font-size": 11.5,
      transform: "translate(14," + (riquadro.alto + riquadro.altezza / 2) + ") rotate(-90)",
    }, svg);
    testoY.textContent = opzioni.etichettaY;

    const righe = punti.slice()
      .sort(function (a, b) { return b.y - a.y; })
      .map(function (p) {
        return [
          p.nome,
          opzioni.formattaX ? opzioni.formattaX(p.x) : num(p.x, opzioni.decimaliX || 0),
          num(p.y, opzioni.decimaliY === undefined ? 2 : opzioni.decimaliY),
        ];
      });
    tabellaSpecchio(contenitore, ["comune", opzioni.etichettaX, opzioni.etichettaY], righe);
  }

  // --- serie storiche ---------------------------------------------------

  function serie(contenitore, opzioni) {
    const ALTEZZA = 340;
    const riquadro = { sinistra: 58, alto: 16, larghezza: LARGHEZZA - 195, altezza: ALTEZZA - 56 };
    const linee = opzioni.linee;
    const periodi = opzioni.periodi;

    let yMin = Infinity, yMax = -Infinity;
    linee.forEach(function (linea) {
      linea.valori.forEach(function (v) {
        if (v === null) return;
        if (v < yMin) yMin = v;
        if (v > yMax) yMax = v;
      });
    });
    const margine = (yMax - yMin) * 0.1;
    yMin -= margine; yMax += margine;

    function sx(indice) {
      return riquadro.sinistra + (indice / (periodi.length - 1)) * riquadro.larghezza;
    }
    function sy(valore) {
      return riquadro.alto + riquadro.altezza - ((valore - yMin) / (yMax - yMin)) * riquadro.altezza;
    }

    const svg = el("svg", {
      viewBox: "0 0 " + LARGHEZZA + " " + ALTEZZA,
      role: "img", "aria-label": opzioni.descrizione,
    });
    contenitore.appendChild(svg);

    passi(yMin, yMax, 5).forEach(function (valore) {
      const y = sy(valore);
      el("line", { x1: riquadro.sinistra, x2: riquadro.sinistra + riquadro.larghezza, y1: y, y2: y,
        stroke: css("--line") }, svg);
      const testo = el("text", { x: riquadro.sinistra - 8, y: y + 4, "text-anchor": "end",
        fill: css("--muted"), "font-size": 11 }, svg);
      testo.textContent = num(valore, opzioni.decimali === undefined ? 0 : opzioni.decimali);
    });
    /* Un'etichetta ogni `n` periodi. Con le sei annate di ASIA ci stanno tutte;
       con i ventitre anni delle centraline si sovrappongono fino a diventare
       una striscia nera, e una data illeggibile è peggio di nessuna data.
       L'ultimo periodo si scrive sempre: è quello che il lettore cerca. */
    const saltoX = Math.ceil(periodi.length / 12);
    periodi.forEach(function (periodo, indice) {
      if (indice % saltoX && indice !== periodi.length - 1) return;
      const testo = el("text", { x: sx(indice), y: riquadro.alto + riquadro.altezza + 18,
        "text-anchor": "middle", fill: css("--muted"), "font-size": 11 }, svg);
      testo.textContent = periodo;
    });

    const colori = CATEGORICHE.map(css);
    linee.forEach(function (linea, indiceLinea) {
      let d = "";
      linea.valori.forEach(function (valore, indice) {
        if (valore === null) return;
        d += (d ? "L" : "M") + sx(indice).toFixed(1) + " " + sy(valore).toFixed(1);
      });
      el("path", { d: d, fill: "none", stroke: colori[indiceLinea % colori.length],
        "stroke-width": 2, "stroke-linejoin": "round", "stroke-linecap": "round" }, svg);
      linea.valori.forEach(function (valore, indice) {
        if (valore === null) return;
        const punto = el("circle", { cx: sx(indice), cy: sy(valore), r: 4.5,
          fill: colori[indiceLinea % colori.length], stroke: css("--card"), "stroke-width": 2 }, svg);
        punto.addEventListener("mousemove", function (evento) {
          mostraSuggerimento(evento, "<b>" + linea.nome + "</b>" + periodi[indice] + ": " +
            num(valore, opzioni.decimali === undefined ? 0 : opzioni.decimali) + " " + (opzioni.unita || ""));
        });
        punto.addEventListener("mouseleave", nascondiSuggerimento);
      });
      // Etichetta diretta in fondo alla linea: la legenda separata costringe
      // l'occhio a fare avanti e indietro.
      const ultimo = linea.valori.length - 1;
      const testo = el("text", { x: sx(ultimo) + 10, y: sy(linea.valori[ultimo]) + 4,
        fill: colori[indiceLinea % colori.length], "font-size": 12, "font-weight": 600 }, svg);
      testo.textContent = linea.nome;
    });

    const righe = periodi.map(function (periodo, indice) {
      return [periodo].concat(linee.map(function (linea) {
        return num(linea.valori[indice], opzioni.decimali === undefined ? 0 : opzioni.decimali);
      }));
    });
    tabellaSpecchio(contenitore, ["periodo"].concat(linee.map(function (l) { return l.nome; })), righe);
  }

  // --- barre orizzontali (le decomposizioni) ---------------------------

  function barre(contenitore, opzioni) {
    const voci = opzioni.voci;
    const ALTEZZA_RIGA = 26;
    const ALTEZZA = voci.length * ALTEZZA_RIGA + 34;
    const sinistra = opzioni.larghezzaEtichette || 275;
    const larghezza = LARGHEZZA - sinistra - 70;

    const estremo = Math.max.apply(null, voci.map(function (v) { return Math.abs(v.valore); }));
    const zero = opzioni.conSegno ? sinistra + larghezza / 2 : sinistra;
    const scalaLarghezza = opzioni.conSegno ? larghezza / 2 / estremo : larghezza / estremo;

    const svg = el("svg", {
      viewBox: "0 0 " + LARGHEZZA + " " + ALTEZZA,
      role: "img", "aria-label": opzioni.descrizione,
    });
    contenitore.appendChild(svg);

    voci.forEach(function (voce, indice) {
      const y = indice * ALTEZZA_RIGA + 10;
      const lunghezza = Math.abs(voce.valore) * scalaLarghezza;
      const x = voce.valore < 0 ? zero - lunghezza : zero;
      el("rect", {
        x: x, y: y, width: Math.max(lunghezza, 1), height: ALTEZZA_RIGA - 10,
        rx: 4,
        fill: voce.colore ? css(voce.colore)
          : voce.valore < 0 ? css("--div-neg-3") : css("--div-pos-4"),
      }, svg);
      const etichetta = el("text", { x: sinistra - 10, y: y + 12, "text-anchor": "end",
        fill: css("--ink2"), "font-size": 11.5 }, svg);
      etichetta.textContent = voce.nome;
      // Se il numero finirebbe sopra la colonna delle etichette, entra nella
      // barra: fuori si sovrapporrebbe al nome del settore.
      const fuoriASinistra = voce.valore < 0 && x - 8 < sinistra + 40;
      const numero = el("text", {
        x: fuoriASinistra ? x + 8 : voce.valore < 0 ? x - 8 : x + lunghezza + 8,
        y: y + 12,
        "text-anchor": fuoriASinistra ? "start" : voce.valore < 0 ? "end" : "start",
        fill: fuoriASinistra ? css("--card") : css("--ink"),
        "font-size": 11.5, "font-weight": 600,
      }, svg);
      numero.textContent = num(voce.valore, opzioni.decimali === undefined ? 0 : opzioni.decimali);
    });

    if (opzioni.conSegno) {
      el("line", { x1: zero, x2: zero, y1: 4, y2: ALTEZZA - 26, stroke: css("--line") }, svg);
    }

    tabellaSpecchio(contenitore, [opzioni.etichettaVoci || "voce", opzioni.unita || "valore"],
      voci.map(function (v) { return [v.nome, num(v.valore, opzioni.decimali === undefined ? 0 : opzioni.decimali)]; }));
  }

  /* Colonne attorno allo zero: per le anomalie, dove il segno è metà del
     messaggio. Una linea spezzata direbbe «la temperatura sale»; le colonne
     dicono anche *rispetto a cosa*, perché lo zero è una riga disegnata e non
     un bordo del riquadro. La rampa è la divergente della lingua grafica, così
     un anno freddo è freddo anche di colore. */
  function colonne(contenitore, opzioni) {
    const ALTEZZA = 320;
    const riquadro = { sinistra: 52, alto: 18, larghezza: LARGHEZZA - 76, altezza: ALTEZZA - 60 };
    const voci = opzioni.voci;
    const decimali = opzioni.decimali === undefined ? 2 : opzioni.decimali;

    const valori = voci.map(function (v) { return v.valore; });
    const estremo = Math.max.apply(null, valori.map(Math.abs)) * 1.15;
    const yMin = -estremo, yMax = estremo;

    function sy(valore) {
      return riquadro.alto + riquadro.altezza - ((valore - yMin) / (yMax - yMin)) * riquadro.altezza;
    }

    const svg = el("svg", {
      viewBox: "0 0 " + LARGHEZZA + " " + ALTEZZA,
      role: "img", "aria-label": opzioni.descrizione,
    });
    contenitore.appendChild(svg);

    passi(yMin, yMax, 5).forEach(function (valore) {
      const y = sy(valore);
      el("line", { x1: riquadro.sinistra, x2: riquadro.sinistra + riquadro.larghezza, y1: y, y2: y,
        stroke: css("--line") }, svg);
      const testo = el("text", { x: riquadro.sinistra - 8, y: y + 4, "text-anchor": "end",
        fill: css("--muted"), "font-size": 11 }, svg);
      testo.textContent = num(valore, decimali === 0 ? 0 : 1);
    });

    const zero = sy(0);
    el("line", { x1: riquadro.sinistra, x2: riquadro.sinistra + riquadro.larghezza,
      y1: zero, y2: zero, stroke: css("--ink"), "stroke-width": 1.5 }, svg);

    // La rampa divergente scelta sull'estremo osservato: un +1,7 °C prende la
    // classe di fondo calda, un −0,1 °C il neutro.
    const passoClasse = estremo / 4;
    const larghezzaColonna = Math.max(3, riquadro.larghezza / voci.length - 3);

    voci.forEach(function (voce, indice) {
      const x = riquadro.sinistra + (indice + 0.5) * (riquadro.larghezza / voci.length)
        - larghezzaColonna / 2;
      const alto = Math.min(sy(voce.valore), zero);
      const altezza = Math.max(1, Math.abs(sy(voce.valore) - zero));
      let classe = 4 + Math.round(voce.valore / passoClasse);
      classe = Math.max(0, Math.min(DIVERGENTE.length - 1, classe));
      const barra = el("rect", { x: x, y: alto, width: larghezzaColonna, height: altezza,
        fill: css(DIVERGENTE[classe]) }, svg);
      barra.addEventListener("mousemove", function (evento) {
        mostraSuggerimento(evento, "<b>" + voce.etichetta + "</b>" +
          num(voce.valore, decimali) + " " + (opzioni.unita || "") +
          (voce.nota ? "<br>" + voce.nota : ""));
      });
      barra.addEventListener("mouseleave", nascondiSuggerimento);
    });

    // Un'etichetta ogni `n` colonne: con trent'anni scriverli tutti li
    // sovrappone, e una data illeggibile è peggio di nessuna data.
    const salto = Math.ceil(voci.length / 12);
    voci.forEach(function (voce, indice) {
      if (indice % salto) return;
      const x = riquadro.sinistra + (indice + 0.5) * (riquadro.larghezza / voci.length);
      const testo = el("text", { x: x, y: riquadro.alto + riquadro.altezza + 18,
        "text-anchor": "middle", fill: css("--muted"), "font-size": 11 }, svg);
      testo.textContent = voce.etichetta;
    });

    tabellaSpecchio(
      contenitore,
      [opzioni.etichettaX || "periodo", opzioni.etichettaY || "valore"].concat(opzioni.colonnaNota ? [opzioni.colonnaNota] : []),
      voci.map(function (voce) {
        const riga = [voce.etichetta, num(voce.valore, decimali)];
        if (opzioni.colonnaNota) riga.push(voce.nota || "");
        return riga;
      })
    );
  }

  // --- sciame: una distribuzione, non una classifica -------------------

  function sciame(contenitore, opzioni) {
    const ALTEZZA = 200;
    const riquadro = { sinistra: 24, alto: 40, larghezza: LARGHEZZA - 48, altezza: 92 };
    const codici = Object.keys(opzioni.valori);
    if (!codici.length) return;

    const lista = codici.map(function (c) { return opzioni.valori[c]; });
    const minimo = Math.min.apply(null, lista);
    const massimo = Math.max.apply(null, lista);
    const margine = (massimo - minimo) * 0.04 || 1;

    function sx(valore) {
      return riquadro.sinistra +
        ((valore - minimo + margine) / (massimo - minimo + 2 * margine)) * riquadro.larghezza;
    }

    const svg = el("svg", {
      viewBox: "0 0 " + LARGHEZZA + " " + ALTEZZA,
      role: "img", "aria-label": opzioni.descrizione,
    });
    contenitore.appendChild(svg);

    // Impilamento: i punti vicini si scostano in verticale invece di
    // sovrapporsi. La posizione verticale non significa niente — è l'unico
    // modo onesto di mostrare 107 valori su una riga sola.
    const RAGGIO = 5;
    const occupati = [];
    const disposti = codici.map(function (codice) {
      const x = sx(opzioni.valori[codice]);
      let livello = 0;
      while (occupati.some(function (p) {
        return p.livello === livello && Math.abs(p.x - x) < RAGGIO * 1.7;
      })) livello++;
      occupati.push({ x: x, livello: livello });
      return { codice: codice, x: x, livello: livello };
    });
    const massimoLivello = Math.max.apply(null, disposti.map(function (d) { return d.livello; }));
    const passoY = Math.min(RAGGIO * 1.8, riquadro.altezza / (massimoLivello + 1));
    const base = riquadro.alto + riquadro.altezza;

    if (opzioni.mediana !== undefined) {
      const x = sx(opzioni.mediana);
      el("line", { x1: x, x2: x, y1: riquadro.alto - 10, y2: base + 6,
        stroke: css("--line"), "stroke-dasharray": "3 3" }, svg);
      const etichetta = el("text", { x: x, y: riquadro.alto - 15, "text-anchor": "middle",
        fill: css("--muted"), "font-size": 11 }, svg);
      etichetta.textContent = "mediana " + num(opzioni.mediana, opzioni.decimali);
    }

    // Le etichette dei punti evidenziati si scalano in verticale quando i punti
    // sono vicini: due province gemelle finiscono per forza una accanto
    // all'altra, ed è proprio il caso che va letto.
    const evidenziatiOrdinati = disposti
      .filter(function (d) { return opzioni.evidenziati && opzioni.evidenziati[d.codice]; })
      .sort(function (a, b) { return a.x - b.x; });

    disposti.forEach(function (punto) {
      const evidenziato = opzioni.evidenziati && opzioni.evidenziati[punto.codice];
      const cerchio = el("circle", {
        cx: punto.x, cy: base - punto.livello * passoY, r: evidenziato ? 6.5 : RAGGIO,
        fill: evidenziato
          ? (punto.codice === "017" ? css("--coral") : css("--card"))
          : css("--sea"),
        "fill-opacity": evidenziato ? 1 : 0.4,
        stroke: evidenziato ? css("--coral") : "none",
        "stroke-width": evidenziato ? 2 : 0,
      }, svg);
      const nome = opzioni.nomi[punto.codice] || punto.codice;
      cerchio.addEventListener("mousemove", function (evento) {
        mostraSuggerimento(evento, "<b>" + nome + "</b>" +
          num(opzioni.valori[punto.codice], opzioni.decimali) + " " + (opzioni.etichetta || ""));
      });
      cerchio.addEventListener("mouseleave", nascondiSuggerimento);
      if (evidenziato) {
        const indice = evidenziatiOrdinati.indexOf(punto);
        const vicino = evidenziatiOrdinati.some(function (altro, i) {
          return i < indice && Math.abs(altro.x - punto.x) < 60;
        });
        const cy = base - punto.livello * passoY;
        const alzata = vicino ? 38 : 16;
        el("line", {
          x1: punto.x, x2: punto.x, y1: cy - 7, y2: cy - alzata + 4,
          stroke: css("--muted"), "stroke-width": 1,
        }, svg);
        const testo = el("text", {
          x: punto.x, y: cy - alzata, "text-anchor": "middle",
          fill: css("--ink"), "font-size": 11.5, "font-weight": 600,
        }, svg);
        testo.textContent = evidenziato;
      }
    });

    [minimo, massimo].forEach(function (valore, indice) {
      const nomeEstremo = opzioni.nomi[codici.reduce(function (migliore, c) {
        const scelto = indice === 0
          ? (opzioni.valori[c] < opzioni.valori[migliore] ? c : migliore)
          : (opzioni.valori[c] > opzioni.valori[migliore] ? c : migliore);
        return scelto;
      }, codici[0])];
      const testo = el("text", {
        x: sx(valore), y: base + 22, "text-anchor": indice === 0 ? "start" : "end",
        fill: css("--muted"), "font-size": 11,
      }, svg);
      testo.textContent = num(valore, opzioni.decimali) + " · " + nomeEstremo;
    });

    const asse = el("text", {
      x: riquadro.sinistra + riquadro.larghezza / 2, y: ALTEZZA - 6,
      "text-anchor": "middle", fill: css("--ink2"), "font-size": 11.5,
    }, svg);
    asse.textContent = opzioni.etichetta;

    const righe = codici
      .sort(function (a, b) { return opzioni.valori[b] - opzioni.valori[a]; })
      .map(function (c) { return [opzioni.nomi[c] || c, num(opzioni.valori[c], opzioni.decimali)]; });
    tabellaSpecchio(contenitore, ["provincia", opzioni.etichetta], righe,
      "Le " + codici.length + " province in tabella");
  }

  // --- scrollytelling ---------------------------------------------------

  function scrollytelling(radice, alCambio) {
    const passiTesto = Array.prototype.slice.call(radice.querySelectorAll(".step"));
    if (!passiTesto.length) return;

    function attiva(indice) {
      passiTesto.forEach(function (passo, i) {
        passo.classList.toggle("active", i === indice);
      });
      alCambio(indice, passiTesto[indice]);
    }

    if (!("IntersectionObserver" in window)) {
      attiva(passiTesto.length - 1);
      return;
    }
    const osservatore = new IntersectionObserver(function (voci) {
      voci.forEach(function (voce) {
        if (voce.isIntersecting) attiva(passiTesto.indexOf(voce.target));
      });
    }, { rootMargin: "-45% 0px -45% 0px" });
    passiTesto.forEach(function (passo) { osservatore.observe(passo); });
    attiva(0);
  }

  // --- controlli a pulsanti --------------------------------------------

  function comandi(contenitore, voci, alClic) {
    const barra = document.createElement("div");
    barra.className = "controls";
    const gruppo = document.createElement("div");
    gruppo.className = "segmented";
    gruppo.setAttribute("role", "group");
    const bottoni = voci.map(function (voce, indice) {
      const bottone = document.createElement("button");
      bottone.type = "button";
      bottone.textContent = voce.etichetta;
      bottone.setAttribute("aria-pressed", indice === 0 ? "true" : "false");
      bottone.addEventListener("click", function () {
        bottoni.forEach(function (altro) { altro.setAttribute("aria-pressed", "false"); });
        bottone.setAttribute("aria-pressed", "true");
        alClic(voce, indice);
      });
      gruppo.appendChild(bottone);
      return bottone;
    });
    barra.appendChild(gruppo);
    contenitore.appendChild(barra);
    return {
      seleziona: function (indice) {
        if (bottoni[indice]) bottoni[indice].click();
      },
    };
  }

  window.GRAFICI = {
    el: el, css: css, num: num, nomeComune: nomeComune, metrica: metrica, valoriDi: valoriDi,
    mappa: mappa, scatter: scatter, serie: serie, barre: barre, colonne: colonne, sciame: sciame,
    scrollytelling: scrollytelling, comandi: comandi, tabellaSpecchio: tabellaSpecchio,
  };
})();
