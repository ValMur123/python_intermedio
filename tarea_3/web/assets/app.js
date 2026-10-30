/* La luz de las minas · dashboard (D3 v7)
   Lee los archivos de web/data/ que generan los scripts de Python. */
(() => {
"use strict";

// ------------------------------------------------------------------ formato es-PE
const loc = d3.formatLocale({ decimal: ",", thousands: " ", grouping: [3], currency: ["S/ ", ""] });
const f0 = loc.format(",.0f"), f1 = loc.format(",.1f"), f2 = loc.format(",.2f");
const fs = v => v >= 100 ? f0(v) : v >= 10 ? f1(v) : f2(v);

const ACENTOS = { ANCASH: "Áncash", APURIMAC: "Apurímac", HUANUCO: "Huánuco", JUNIN: "Junín",
  "SAN MARTIN": "San Martín", "MADRE DE DIOS": "Madre de Dios", "LA LIBERTAD": "La Libertad" };
const MENORES = new Set(["de", "del", "la", "las", "los", "y", "el"]);
const titulo = s => ACENTOS[s] || String(s).toLowerCase().split(" ")
  .map((w, i) => (i && MENORES.has(w)) ? w : w.charAt(0).toUpperCase() + w.slice(1)).join(" ");
const depPbi = d => d === "CALLAO" ? "LIMA" : d;

const C = { luz: "#ffc857", mina: "#e0703a", gris: "#6b7499", vacio: "#1a2245", borde: "#26305a", tenue: "#9aa3c4" };
const CATS = ["Sin minería", "Pequeña (<1 km²)", "Media (1-10 km²)", "Grande (≥10 km²)"];
const IND = {
  luz_total: { nombre: "Luz total", unidad: "radiancia acumulada", color: C.luz },
  luz_media: { nombre: "Luz por km²", unidad: "radiancia media", color: C.luz },
  mina_km2: { nombre: "Área minera", unidad: "km²", color: C.mina },
};

const estado = { dep: "", grupo: "todos", ind: "luz_total", sel: null };
let D = [], DEP = [], R = {}, GEO = null, porId = new Map();
const tip = d3.select("#tooltip");

// ------------------------------------------------------------------ carga
Promise.all([
  d3.csv("data/distritos.csv", d3.autoType),
  d3.csv("data/departamentos.csv", d3.autoType),
  d3.json("data/resumen.json"),
  d3.json("data/distritos.geojson"),
]).then(([dist, dep, res, geo]) => {
  D = dist; DEP = dep; R = res; GEO = geo;
  D.forEach(d => porId.set(d.id, d));
  GEO.features.forEach(f => { f.d = porId.get(f.properties.id); });
  iniciar();
}).catch(err => {
  console.error(err);
  document.querySelector("main").insertAdjacentHTML("afterbegin",
    `<p class="panel" style="margin-top:20px">No se pudieron cargar los datos de <code>web/data/</code>.
     Si abriste el archivo con doble clic, sírvelo con <code>python -m http.server</code> o publícalo en GitHub Pages.</p>`);
});

// ------------------------------------------------------------------ utilidades
const enGrupo = d => estado.grupo === "todos" ? true
  : estado.grupo === "con" ? d.es_minero === 1
  : estado.grupo === "sin" ? d.es_minero === 0
  : d.intensidad_minera === estado.grupo;
const enDep = d => !estado.dep || d.DEPARTAMEN === estado.dep;
const seleccion = () => D.filter(d => enDep(d) && enGrupo(d));
const ticksLog = max => [0, 1, 10, 100, 1e3, 1e4, 1e5, 1e6].filter(v => v <= max * 1.05);
const jitter = id => ((id * 9301 + 49297) % 233280) / 233280 - 0.5;

function svgEn(id, alto, margen) {
  const nodo = document.getElementById(id);
  const ancho = Math.max(280, nodo.clientWidth);
  d3.select(nodo).selectAll("*").remove();
  const svg = d3.select(nodo).append("svg").attr("viewBox", `0 0 ${ancho} ${alto}`).attr("width", "100%");
  return { svg, ancho, alto, m: margen, iw: ancho - margen.l - margen.r, ih: alto - margen.t - margen.b,
           g: svg.append("g").attr("transform", `translate(${margen.l},${margen.t})`) };
}
function mostrarTip(ev, html) {
  tip.html(html).style("opacity", 1);
  const w = tip.node().offsetWidth, x = ev.clientX + 14;
  tip.style("left", (x + w > innerWidth ? ev.clientX - w - 14 : x) + "px").style("top", (ev.clientY + 14) + "px");
}
const ocultarTip = () => tip.style("opacity", 0);
const tipDistrito = d => `<b>${titulo(d.DISTRITO)}</b><span>${titulo(d.PROVINCIA)}, ${titulo(d.DEPARTAMEN)}</span><br>
  Luz total: ${fs(d.luz_total)} · Luz/km²: ${fs(d.luz_media)}<br>Área minera: ${fs(d.mina_km2)} km² · Área: ${f0(d.area_km2)} km²`;

// ------------------------------------------------------------------ inicio
function iniciar() {
  d3.selectAll('[data-k="n_distritos"]').text(f0(R.n_distritos ?? D.length));
  d3.selectAll('[data-k="anio"]').text(R.anio ?? 2021);

  const deps = [...new Set(D.map(d => d.DEPARTAMEN))].sort();
  d3.select("#f-dep").selectAll("option.d").data(deps).join("option").attr("class", "d")
    .attr("value", d => d).text(titulo);

  const etiqueta = d => `${titulo(d.DISTRITO)} — ${titulo(d.PROVINCIA)}, ${titulo(d.DEPARTAMEN)}`;
  const porEtiqueta = new Map(D.map(d => [etiqueta(d), d]));
  d3.select("#lista-distritos").selectAll("option").data(D).join("option").attr("value", etiqueta);

  d3.select("#f-dep").on("change", e => { estado.dep = e.target.value; estado.sel = null; render(); });
  d3.select("#f-grupo").on("change", e => { estado.grupo = e.target.value; render(); });
  d3.select("#f-ind").on("change", e => { estado.ind = e.target.value; render(); });
  d3.select("#f-buscar").on("change", e => {
    const d = porEtiqueta.get(e.target.value);
    if (!d) return;
    estado.dep = d.DEPARTAMEN; estado.sel = d.id;
    if (!enGrupo(d)) estado.grupo = "todos";
    sincronizar(); render();
  });
  d3.select("#b-reset").on("click", () => {
    Object.assign(estado, { dep: "", grupo: "todos", ind: "luz_total", sel: null });
    d3.select("#f-buscar").property("value", ""); sincronizar(); render();
  });
  d3.select("#b-csv").on("click", descargarCSV);

  let t; addEventListener("resize", () => { clearTimeout(t); t = setTimeout(render, 150); });
  hallazgos(); robustez(); render();
}
function sincronizar() {
  d3.select("#f-dep").property("value", estado.dep);
  d3.select("#f-grupo").property("value", estado.grupo);
  d3.select("#f-ind").property("value", estado.ind);
}
function elegir(id) { estado.sel = estado.sel === id ? null : id; render(); }

function render() {
  const sel = seleccion();
  kpis(sel); mapa(); ficha(); top(sel); caja(); dispersion(); pbi(); pct();
}


// ------------------------------------------------------------------ KPIs
function kpis(sel) {
  const nMin = d3.sum(sel, d => d.es_minero);
  d3.select("#k1").text(f0(sel.length));
  d3.select("#k1s").text(sel.length ? `${f0(nMin)} con minería (${f1(100 * nMin / sel.length)} %)` : "Sin distritos");

  const base = D.filter(enDep);
  const mMin = d3.median(base.filter(d => d.es_minero === 1), d => d.luz_total);
  const mNo = d3.median(base.filter(d => d.es_minero === 0), d => d.luz_total);
  if (mMin == null || !mNo) {
    d3.select("#k2").text("—");
    d3.select("#k2s").text("No hay ambos grupos en este departamento");
  } else {
    d3.select("#k2").text(`${f1(mMin / mNo)}×`);
    d3.select("#k2s").text(`Mediana de luz total: ${fs(mMin)} (mineros) vs ${fs(mNo)} (no mineros)`);
  }

  const area = d3.sum(sel, d => d.mina_km2);
  d3.select("#k3").text(`${fs(area)} km²`);
  d3.select("#k3s").text(`En ${f0(nMin)} distrito${nMin === 1 ? "" : "s"} de la selección`);

  const max = d3.greatest(sel, d => d.luz_total);
  d3.select("#k4").text(max ? titulo(max.DISTRITO) : "—");
  d3.select("#k4s").text(max ? `${titulo(max.PROVINCIA)}, ${titulo(max.DEPARTAMEN)} · luz ${fs(max.luz_total)}` : "");
}

// ------------------------------------------------------------------ mapa
let escalas = null;
function escalaColor() {
  if (escalas) return escalas;
  const tope = k => d3.quantile(D.map(d => Math.log1p(d[k])).sort(d3.ascending), 0.995);
  const minas = D.filter(d => d.mina_km2 > 0).map(d => d.mina_km2);
  escalas = {
    luz_total: d3.scaleSequential(d3.interpolateInferno).domain([0, tope("luz_total")]).clamp(true),
    luz_media: d3.scaleSequential(d3.interpolateInferno).domain([0, tope("luz_media")]).clamp(true),
    mina_km2: d3.scaleSequentialLog(d3.interpolateOranges).domain([d3.min(minas) || 0.01, d3.max(minas) || 1]).clamp(true),
  };
  return escalas;
}
function colorDe(d) {
  const k = estado.ind, s = escalaColor()[k];
  if (k === "mina_km2") return d.mina_km2 > 0 ? s(d.mina_km2) : "#202a52";
  return s(Math.log1p(d[k]));
}
function mapa() {
  const nodo = document.getElementById("mapa");
  const ancho = nodo.clientWidth, alto = nodo.clientHeight || ancho * 4 / 3;
  d3.select(nodo).selectAll("*").remove();
  const svg = d3.select(nodo).append("svg").attr("viewBox", `0 0 ${ancho} ${alto}`);
  const foco = estado.dep ? GEO.features.filter(f => f.d && f.d.DEPARTAMEN === estado.dep) : GEO.features;
  const proj = d3.geoMercator().fitExtent([[8, 8], [ancho - 8, alto - 8]], { type: "FeatureCollection", features: foco });
  const path = d3.geoPath(proj);

  svg.append("g").selectAll("path").data(GEO.features).join("path")
    .attr("d", path)
    .attr("fill", f => !f.d ? C.vacio : (enDep(f.d) && enGrupo(f.d)) ? colorDe(f.d) : C.vacio)
    .attr("fill-opacity", f => f.d && enDep(f.d) ? 1 : 0.55)
    .attr("stroke", f => f.d && f.d.id === estado.sel ? "#fff" : "#0b1020")
    .attr("stroke-width", f => f.d && f.d.id === estado.sel ? 2 : 0.25)
    .on("mousemove", (e, f) => f.d && mostrarTip(e, tipDistrito(f.d)))
    .on("mouseleave", ocultarTip)
    .on("click", (e, f) => f.d && elegir(f.d.id))
    .filter(f => f.d && f.d.id === estado.sel).raise();

  const i = IND[estado.ind];
  const lugar = estado.dep ? titulo(estado.dep) : "Perú";
  d3.select("#t-mapa").text(`${i.nombre} por distrito · ${lugar}`);
  leyenda();
}
function leyenda() {
  const k = estado.ind, s = escalaColor()[k];
  const box = d3.select("#leyenda"); box.selectAll("*").remove();
  const w = Math.min(320, document.getElementById("leyenda").clientWidth || 320), h = 38;
  const svg = box.append("svg").attr("width", w).attr("height", h);
  const id = "grad-" + k, grad = svg.append("defs").append("linearGradient").attr("id", id);
  const [a, b] = s.domain();
  d3.range(0, 1.01, 0.1).forEach(t => grad.append("stop").attr("offset", t)
    .attr("stop-color", k === "mina_km2" ? s(a * Math.pow(b / a, t)) : s(a + t * (b - a))));
  svg.append("rect").attr("x", 0).attr("y", 4).attr("width", w).attr("height", 10).attr("rx", 3).attr("fill", `url(#${id})`);
  const izq = k === "mina_km2" ? `${fs(a)} km²` : "0 (oscuro)";
  const der = k === "mina_km2" ? `${f0(b)} km²` : `${f0(Math.expm1(b))}+`;
  svg.append("text").attr("x", 0).attr("y", 30).text(izq);
  svg.append("text").attr("x", w).attr("y", 30).attr("text-anchor", "end").text(der);
  box.append("div").text(k === "mina_km2" ? "Azul oscuro: sin minería detectada." : "Escala logarítmica de radiancia. Gris: fuera de la selección.");
}

// ------------------------------------------------------------------ ficha
function ficha() {
  const el = d3.select("#ficha");
  const d = porId.get(estado.sel);
  if (!d) { el.html(`<h2>Ficha del distrito</h2><p class="vacio">Selecciona un distrito en el mapa o búscalo arriba.</p>`); return; }
  const pares = D.filter(x => x.DEPARTAMEN === d.DEPARTAMEN);
  const rango = 1 + pares.filter(x => x.luz_total > d.luz_total).length;
  el.html(`<h2>Ficha del distrito</h2>
    <p class="nombre">${titulo(d.DISTRITO)}</p>
    <p class="lugar">${titulo(d.PROVINCIA)}, ${titulo(d.DEPARTAMEN)}</p>
    <span class="etq ${d.es_minero ? "min" : "nomin"}">${d.intensidad_minera}</span>
    <dl>
      <dt>Luz total</dt><dd>${fs(d.luz_total)}</dd>
      <dt>Luz por km²</dt><dd>${fs(d.luz_media)}</dd>
      <dt>Área minera</dt><dd>${fs(d.mina_km2)} km²</dd>
      <dt>Área del distrito</dt><dd>${f0(d.area_km2)} km²</dd>
      <dt>Puesto por luz en ${titulo(d.DEPARTAMEN)}</dt><dd>${rango} de ${pares.length}</dd>
    </dl>`);
}


// ------------------------------------------------------------------ top
function top(sel) {
  const k = estado.ind, i = IND[k];
  const datos = sel.filter(d => d[k] > 0).sort((a, b) => b[k] - a[k]).slice(0, 12);
  d3.select("#t-top").text(`Top 12 · ${i.nombre.toLowerCase()}`);
  const fila = 24, { g, iw } = svgEn("g-top", Math.max(60, datos.length * fila + 10), { t: 4, r: 54, b: 4, l: 132 });
  if (!datos.length) { g.append("text").attr("y", 20).text("Sin datos en esta selección"); return; }
  const x = d3.scaleLinear().domain([0, d3.max(datos, d => d[k])]).range([0, iw]);
  const y = d3.scaleBand().domain(datos.map(d => d.id)).range([0, datos.length * fila]).padding(0.25);
  const filas = g.selectAll("g").data(datos).join("g").attr("transform", d => `translate(0,${y(d.id)})`)
    .style("cursor", "pointer").on("click", (e, d) => elegir(d.id))
    .on("mousemove", (e, d) => mostrarTip(e, tipDistrito(d))).on("mouseleave", ocultarTip);
  filas.append("rect").attr("width", d => Math.max(2, x(d[k]))).attr("height", y.bandwidth()).attr("rx", 3)
    .attr("fill", d => d.id === estado.sel ? "#fff" : (k === "mina_km2" || d.es_minero ? C.mina : C.luz))
    .attr("fill-opacity", d => d.id === estado.sel ? 1 : 0.9);
  filas.append("text").attr("x", -8).attr("y", y.bandwidth() / 2).attr("dy", "0.35em").attr("text-anchor", "end")
    .text(d => { const n = titulo(d.DISTRITO); return n.length > 19 ? n.slice(0, 18) + "…" : n; })
    .style("fill", "#e8ebf5");
  filas.append("text").attr("x", d => x(d[k]) + 6).attr("y", y.bandwidth() / 2).attr("dy", "0.35em").text(d => fs(d[k]));
  if (k !== "mina_km2") g.append("text").attr("x", iw + 50).attr("y", datos.length * fila + 4).attr("text-anchor", "end")
    .style("font-size", "10px").text("naranja = distrito minero");
}

// ------------------------------------------------------------------ caja por intensidad
function caja() {
  const base = D.filter(enDep);
  const { g, iw, ih } = svgEn("g-caja", 330, { t: 10, r: 12, b: 42, l: 52 });
  const x = d3.scaleBand().domain(CATS).range([0, iw]).padding(0.3);
  const ymax = d3.max(base, d => d.luz_total) || 1;
  const y = d3.scaleSymlog().constant(1).domain([0, ymax]).range([ih, 0]);
  g.append("g").attr("class", "grilla").call(d3.axisLeft(y).tickValues(ticksLog(y.domain()[1])).tickSize(-iw).tickFormat(""));
  g.append("g").attr("class", "eje").call(d3.axisLeft(y).tickValues(ticksLog(y.domain()[1])).tickFormat(v => f0(v)));
  g.append("g").attr("class", "eje").attr("transform", `translate(0,${ih})`).call(d3.axisBottom(x).tickFormat(c => c.replace(" (", "\n(")))
    .selectAll("text").each(function () {
      const t = d3.select(this), [a, b] = t.text().split("\n"); t.text(a);
      if (b) t.append("tspan").attr("x", 0).attr("dy", "1.2em").text(b);
    });
  g.append("text").attr("transform", "rotate(-90)").attr("x", -ih / 2).attr("y", -42).attr("text-anchor", "middle").text("Luz total");

  CATS.forEach(c => {
    const vals = base.filter(d => d.intensidad_minera === c);
    if (!vals.length) return;
    const activo = estado.grupo === "todos" || (estado.grupo === "con" ? c !== CATS[0] : estado.grupo === "sin" ? c === CATS[0] : estado.grupo === c);
    const col = c === CATS[0] ? C.gris : C.mina, bw = x.bandwidth(), x0 = x(c);
    const v = vals.map(d => d.luz_total).sort(d3.ascending);
    const [q1, q2, q3] = [0.25, 0.5, 0.75].map(p => d3.quantile(v, p));
    const grupo = g.append("g").attr("opacity", activo ? 1 : 0.25);
    grupo.selectAll("circle").data(vals).join("circle")
      .attr("cx", d => x0 + bw / 2 + jitter(d.id) * bw * 0.9).attr("cy", d => y(d.luz_total))
      .attr("r", d => d.id === estado.sel ? 5 : vals.length > 400 ? 1.6 : 2.6)
      .attr("fill", d => d.id === estado.sel ? "#fff" : col).attr("fill-opacity", d => d.id === estado.sel ? 1 : 0.45)
      .on("mousemove", (e, d) => mostrarTip(e, tipDistrito(d))).on("mouseleave", ocultarTip).on("click", (e, d) => elegir(d.id));
    grupo.append("rect").attr("x", x0 + bw * 0.2).attr("width", bw * 0.6).attr("y", y(q3)).attr("height", Math.max(1, y(q1) - y(q3)))
      .attr("fill", "none").attr("stroke", "#e8ebf5").attr("stroke-width", 1.2).attr("rx", 3).style("pointer-events", "none");
    grupo.append("line").attr("x1", x0 + bw * 0.2).attr("x2", x0 + bw * 0.8).attr("y1", y(q2)).attr("y2", y(q2))
      .attr("stroke", C.luz).attr("stroke-width", 2.5);
    grupo.append("text").attr("x", x0 + bw / 2).attr("y", y(q3) - 6).attr("text-anchor", "middle")
      .style("fill", "#e8ebf5").text(`n=${vals.length} · med ${fs(q2)}`);
  });
}

// ------------------------------------------------------------------ dispersión área vs luz
function dispersion() {
  const base = D.filter(d => enDep(d) && d.area_km2 > 0);
  const { g, iw, ih } = svgEn("g-disp", 330, { t: 10, r: 14, b: 40, l: 52 });
  const x = d3.scaleLog().domain(d3.extent(base, d => d.area_km2)).range([0, iw]).nice();
  const y = d3.scaleSymlog().constant(1).domain([0, d3.max(base, d => d.luz_total) || 1]).range([ih, 0]);
  g.append("g").attr("class", "grilla").call(d3.axisLeft(y).tickValues(ticksLog(y.domain()[1])).tickSize(-iw).tickFormat(""));
  g.append("g").attr("class", "eje").call(d3.axisLeft(y).tickValues(ticksLog(y.domain()[1])).tickFormat(v => f0(v)));
  g.append("g").attr("class", "eje").attr("transform", `translate(0,${ih})`).call(d3.axisBottom(x).ticks(5, "~s"));
  g.append("text").attr("x", iw / 2).attr("y", ih + 34).attr("text-anchor", "middle").text("Área del distrito (km², escala log)");
  g.append("text").attr("transform", "rotate(-90)").attr("x", -ih / 2).attr("y", -42).attr("text-anchor", "middle").text("Luz total");
  const orden = [...base].sort((a, b) => a.es_minero - b.es_minero || (a.id === estado.sel) - (b.id === estado.sel));
  g.selectAll("circle").data(orden).join("circle")
    .attr("cx", d => x(d.area_km2)).attr("cy", d => y(d.luz_total))
    .attr("r", d => d.id === estado.sel ? 6 : d.es_minero ? 3.6 : 2.2)
    .attr("fill", d => d.id === estado.sel ? "#fff" : d.es_minero ? C.mina : C.gris)
    .attr("fill-opacity", d => !enGrupo(d) ? 0.08 : d.es_minero ? 0.9 : 0.35)
    .attr("stroke", d => d.es_minero ? "#0b1020" : "none").attr("stroke-width", 0.5)
    .on("mousemove", (e, d) => mostrarTip(e, tipDistrito(d))).on("mouseleave", ocultarTip).on("click", (e, d) => elegir(d.id));
  const ley = g.append("g").attr("transform", "translate(8,4)");
  [["Con minería", C.mina], ["Sin minería", C.gris]].forEach(([t, c], i) => {
    ley.append("circle").attr("cx", 0).attr("cy", i * 16).attr("r", 4).attr("fill", c);
    ley.append("text").attr("x", 9).attr("y", i * 16).attr("dy", "0.35em").text(t);
  });
}

// ------------------------------------------------------------------ PBI vs luz
function pbi() {
  const datos = DEP.filter(d => d.pbi_millones_s2007 > 0 && d.luz_total > 0);
  const { g, iw, ih } = svgEn("g-pbi", 340, { t: 14, r: 18, b: 40, l: 56 });
  if (!datos.length) { g.append("text").text("Falta el PBI departamental"); return; }
  const x = d3.scaleLog().domain(d3.extent(datos, d => d.pbi_millones_s2007)).range([0, iw]).nice();
  const y = d3.scaleLog().domain(d3.extent(datos, d => d.luz_total)).range([ih, 0]).nice();
  g.append("g").attr("class", "grilla").call(d3.axisLeft(y).ticks(5).tickSize(-iw).tickFormat(""));
  g.append("g").attr("class", "eje").call(d3.axisLeft(y).ticks(5, "~s"));
  g.append("g").attr("class", "eje").attr("transform", `translate(0,${ih})`).call(d3.axisBottom(x).ticks(5, "~s"));
  g.append("text").attr("x", iw / 2).attr("y", ih + 34).attr("text-anchor", "middle").text("PBI (millones de S/ de 2007, log)");
  g.append("text").attr("transform", "rotate(-90)").attr("x", -ih / 2).attr("y", -46).attr("text-anchor", "middle").text("Luz total (log)");
  const actual = depPbi(estado.dep);
  const nodos = g.selectAll("g.p").data(datos).join("g").attr("class", "p")
    .attr("transform", d => `translate(${x(d.pbi_millones_s2007)},${y(d.luz_total)})`).style("cursor", "pointer")
    .on("click", (e, d) => { estado.dep = estado.dep === d.departamento ? "" : d.departamento; estado.sel = null; sincronizar(); render(); })
    .on("mousemove", (e, d) => mostrarTip(e, `<b>${titulo(d.departamento)}</b>PBI: S/ ${f0(d.pbi_millones_s2007)} millones<br>Luz total: ${f0(d.luz_total)}<br>Luz de distritos mineros: ${f1(d.pct_luz_minera)} %`))
    .on("mouseleave", ocultarTip);
  nodos.append("circle").attr("r", d => d.departamento === actual ? 8 : 5.5)
    .attr("fill", d => d.departamento === actual ? "#fff" : d3.interpolateRgb(C.luz, C.mina)(Math.min(1, d.pct_luz_minera / 40)))
    .attr("stroke", "#0b1020");
  nodos.append("text").attr("x", 8).attr("dy", "0.35em").style("font-size", "10px")
    .style("fill", d => d.departamento === actual ? "#fff" : C.tenue).text(d => titulo(d.departamento));
  if (R.corr_luz_pbi_dep != null)
    g.append("text").attr("x", 4).attr("y", 4).style("fill", "#e8ebf5").style("font-size", "13px")
      .text(`r = ${f2(R.corr_luz_pbi_dep)} (sin Lima: ${f2(R.corr_luz_pbi_dep_sin_lima)})`);
}

// ------------------------------------------------------------------ % luz minera
function pct() {
  const datos = [...DEP].sort((a, b) => b.pct_luz_minera - a.pct_luz_minera);
  const fila = 15, { g, iw } = svgEn("g-pct", datos.length * fila + 30, { t: 4, r: 46, b: 22, l: 104 });
  const x = d3.scaleLinear().domain([0, Math.max(10, d3.max(datos, d => d.pct_luz_minera))]).range([0, iw]).nice();
  const y = d3.scaleBand().domain(datos.map(d => d.departamento)).range([0, datos.length * fila]).padding(0.2);
  g.append("g").attr("class", "eje").attr("transform", `translate(0,${datos.length * fila})`).call(d3.axisBottom(x).ticks(5).tickFormat(v => v + " %"));
  const actual = depPbi(estado.dep);
  const filas = g.selectAll("g.b").data(datos).join("g").attr("class", "b").attr("transform", d => `translate(0,${y(d.departamento)})`)
    .style("cursor", "pointer")
    .on("click", (e, d) => { estado.dep = estado.dep === d.departamento ? "" : d.departamento; estado.sel = null; sincronizar(); render(); })
    .on("mousemove", (e, d) => mostrarTip(e, `<b>${titulo(d.departamento)}</b>${f0(d.n_mineros)} de ${f0(d.n_distritos)} distritos con minería<br>${f1(d.pct_luz_minera)} % de la luz`))
    .on("mouseleave", ocultarTip);
  filas.append("rect").attr("width", d => x(d.pct_luz_minera)).attr("height", y.bandwidth()).attr("rx", 2)
    .attr("fill", d => d.departamento === actual ? "#fff" : C.mina).attr("fill-opacity", d => !actual || d.departamento === actual ? 0.9 : 0.35);
  filas.append("text").attr("x", -6).attr("y", y.bandwidth() / 2).attr("dy", "0.35em").attr("text-anchor", "end")
    .style("font-size", "10.5px").style("fill", d => d.departamento === actual ? "#fff" : C.tenue).text(d => titulo(d.departamento));
  filas.append("text").attr("x", d => x(d.pct_luz_minera) + 4).attr("y", y.bandwidth() / 2).attr("dy", "0.35em")
    .style("font-size", "10px").text(d => f1(d.pct_luz_minera) + " %");
}

// ------------------------------------------------------------------ hallazgos y robustez
function hallazgos() {
  const m = R.modelos?.completo || {};
  const menos = R.luz_media_km2_minero < R.luz_media_km2_no_minero;
  const top = R.dep_mayor_pct_luz_minera || {};
  const cards = [
    { num: `${f1(m.veces_mas_luz)}×`, h: "Más luz donde hay minería",
      p: `Comparando distritos de igual tamaño, lluvia y departamento, uno con minería emite en promedio ${f1(m.veces_mas_luz)} veces más luz total que uno sin minería (t = ${f1(m.t)}; ${f0(m.n)} distritos). En medianas simples: ${fs(R.mediana_luz_minero)} vs ${fs(R.mediana_luz_no_minero)}.` },
    { num: `${f2(R.luz_media_km2_minero)} vs ${f2(R.luz_media_km2_no_minero)}`, h: menos ? "…pero menos luz por km²" : "…y también más luz por km²",
      p: menos
        ? `Por km², los distritos mineros brillan menos: son mucho más grandes (mediana de ${f0(R.area_mediana_minero)} km² frente a ${f0(R.area_mediana_no_minero)} km²) y casi vacíos, con un foco muy brillante: el campamento, la planta o el tajo.`
        : `Incluso por km² los distritos mineros brillan más, aunque son más grandes (mediana de ${f0(R.area_mediana_minero)} km² frente a ${f0(R.area_mediana_no_minero)} km²).` },
    { num: `r = ${f2(R.corr_luz_pbi_dep)}`, h: "La luz sigue al PBI oficial",
      p: `Por departamento, la luz satelital y el PBI del INEI van de la mano (correlación de ${f2(R.corr_luz_pbi_dep)}; ${f2(R.corr_luz_pbi_dep_sin_lima)} sin Lima), lo que respalda usar la luz como aproximación. En ${titulo(top.departamento || "")}, el ${f1(top.pct)} % de la luz proviene de distritos mineros (incluye la luz de ciudades ubicadas en esos distritos).` },
  ];
  d3.select("#hallazgos").selectAll("article").data(cards).join("article").attr("class", "card")
    .html(c => `<p class="num">${c.num}</p><h3>${c.h}</h3><p>${c.p}</p>`);
}
function robustez() {
  const filas = R.robustez_umbral || [];
  const t = d3.select("#t-rob");
  t.append("thead").html("<tr><th>«Minero» si el área minera es mayor a…</th><th>Distritos mineros</th><th>Coeficiente</th><th>Veces más luz</th><th>t</th></tr>");
  t.append("tbody").selectAll("tr").data(filas).join("tr")
    .html(r => `<td>${f0(r.umbral_km2)} km²</td><td>${f0(r.n_mineros)}</td><td>${f2(r.coef)}</td><td>${f1(r.veces_mas_luz)}×</td><td>${f1(r.t)}</td>`);
}

// ------------------------------------------------------------------ descarga
function descargarCSV() {
  const blob = new Blob(["\ufeff" + d3.csvFormat(seleccion())], { type: "text/csv;charset=utf-8" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = `distritos_${estado.dep || "peru"}_${estado.grupo}.csv`.toLowerCase().replace(/[^a-z0-9_.]+/g, "_");
  a.click(); setTimeout(() => URL.revokeObjectURL(a.href), 1000);
}
})();