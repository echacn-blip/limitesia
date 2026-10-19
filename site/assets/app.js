(function(){
"use strict";
var D = window.LIMITES || {tools:[],fx:{rates:{}}};
var RATES = Object.assign({USD:1}, (D.fx && D.fx.rates) || {});
var KEY = "limitesia-moneda"; // solo preferencia local, sin rastreo
var qp = (location.search.match(/[?&]moneda=([A-Z]{3})/i)||[])[1];
var cur = (qp && qp.toUpperCase()) || localStorage.getItem(KEY) || "USD";
if(!RATES[cur]) cur = "USD";

function fmt(usd, c){
  c = c || cur;
  if(usd === null || usd === undefined || usd === "") return "sin verificar";
  var v = Number(usd) * RATES[c];
  var big = ["COP","CLP","ARS"].indexOf(c) >= 0;
  try{ return new Intl.NumberFormat("es-419",{style:"currency",currency:c,maximumFractionDigits: big?0:(v%1?2:0)}).format(v); }
  catch(e){ return c+" "+v.toFixed(2); }
}
function paint(){
  document.querySelectorAll("[data-usd]").forEach(function(el){
    var u = el.getAttribute("data-usd");
    if(u !== "null" && Number(u) === 0){ el.innerHTML = '<span class="free">Gratis</span>'; return; }
    var main = fmt(u === "null" ? null : u);
    var show = cur !== "USD" && u !== "null" && Number(u) !== 0, usd = "US$" + Number(u).toLocaleString("es-419");
    var sub = !show ? "" : (el.closest(".price,.p,.big") ? "<small class=\"usd\">≈ " + usd + "</small>" : ' <span class="mut">(' + usd + ')</span>');
    el.innerHTML = main + sub;
  });
  document.querySelectorAll(".cur-select").forEach(function(s){ s.value = cur; });
  document.querySelectorAll(".cur-note").forEach(function(n){ n.hidden = (cur === "USD"); });
}
document.querySelectorAll(".cur-select").forEach(function(s){
  s.addEventListener("change", function(){ cur = s.value; localStorage.setItem(KEY,cur); paint(); });
});

// ---- Tabla comparativa ----
var tbl = document.getElementById("cmp");
if(tbl){
  var tbody = tbl.tBodies[0], rows = Array.prototype.slice.call(tbody.rows);
  var q = document.getElementById("f-q"), lt = document.getElementById("f-type"),
      mx = document.getElementById("f-max"), team = document.getElementById("f-team"), free = document.getElementById("f-free"),
      count = document.getElementById("f-count");
  function filter(){
    var term = (q.value||"").toLowerCase().trim(), t = lt.value, m = parseFloat(mx.value), n = 0;
    rows.forEach(function(r){
      var ok = true, p = r.dataset.price === "" ? null : parseFloat(r.dataset.price);
      if(term && r.textContent.toLowerCase().indexOf(term) < 0) ok = false;
      if(t && r.dataset.type !== t) ok = false;
      if(!isNaN(m) && (p === null || p > m)) ok = false;
      if(!team.checked && r.dataset.team === "1") ok = false;
      if(!free.checked && p === 0) ok = false;
      r.hidden = !ok; if(ok) n++;
    });
    count.textContent = n + " planes";
  }
  [q,lt,mx,team,free].forEach(function(el){ el.addEventListener("input", filter); el.addEventListener("change", filter); });
  tbl.querySelectorAll("th[data-sort]").forEach(function(th, i){
    th.addEventListener("click", function(){
      var k = th.dataset.sort, asc = !th.classList.contains("asc");
      tbl.querySelectorAll("th").forEach(function(x){ x.classList.remove("asc","desc"); });
      th.classList.add(asc ? "asc" : "desc");
      rows.sort(function(a,b){
        var x = a.dataset[k], y = b.dataset[k];
        if(k === "price"){ x = x === "" ? 1e9 : +x; y = y === "" ? 1e9 : +y; return asc ? x-y : y-x; }
        return asc ? x.localeCompare(y,"es") : y.localeCompare(x,"es");
      });
      rows.forEach(function(r){ tbody.appendChild(r); });
    });
  });
  filter();
}

// ---- Quiz ----
var quiz = document.getElementById("quiz");
if(quiz){
  quiz.addEventListener("submit", function(ev){
    ev.preventDefault();
    var f = new FormData(quiz), b = +f.get("budget"), w = f.get("work"), u = f.get("use"), m = f.get("model");
    var all = [];
    D.tools.forEach(function(t){ t.plans.forEach(function(p){ if(!p.team && !p.no_coding && p.price_usd_month !== null) all.push({t:t,p:p}); }); });
    var scored = all.map(function(x){
      var s = 0, t = x.t, p = x.p, price = p.price_usd_month;
      if(price > b) s -= 100;
      if(w === "terminal" && /claude-code|codex|gemini|kiro/.test(t.slug)) s += 6;
      if(w === "ide" && /cursor|windsurf|kiro|zed|github-copilot/.test(t.slug)) s += 6;
      if(w === "editor" && /github-copilot|zed|gemini/.test(t.slug)) s += 6;
      if(w === "nocode" && /lovable|bolt|replit/.test(t.slug)) s += 9;
      if(w !== "nocode" && /lovable|bolt|replit/.test(t.slug)) s -= 4;
      if(m === "claude" && /claude|anthropic|opus|sonnet/i.test(t.slug + " " + p.models)) s += 4;
      if(m === "gpt" && /codex|gpt/i.test(t.slug + " " + p.models)) s += 4;
      if(m === "gemini" && /gemini/i.test(t.slug + " " + p.models)) s += 4;
      if(u === "light") s += price === 0 ? 3 : (price <= 20 ? 2 : -2);
      if(u === "daily") s += (price >= 10 && price <= 40) ? 3 : (price === 0 ? -2 : 0);
      if(u === "heavy") s += price >= 100 ? 4 : (price >= 30 ? 1 : -3);
      s -= price / 200; // a igual puntaje, más barato primero
      return {x:x, s:s};
    }).filter(function(o){ return o.s > -50; }).sort(function(a,b){ return b.s - a.s; }).slice(0,3);
    var out = document.getElementById("quiz-out");
    if(!scored.length){ out.innerHTML = '<p class="note">Con ese presupuesto no encontramos un plan pago que encaje. Mira los planes gratis en la tabla.</p>'; return; }
    out.innerHTML = "<h3>Te sugerimos mirar:</h3>" + scored.map(function(o,i){
      var t = o.x.t, p = o.x.p;
      return '<div class="plan" style="margin:10px 0"><div class="mut small">#'+(i+1)+' · '+t.limit_type+'</div><h3><a href="herramientas/'+t.slug+'.html">'+t.name+' — '+p.name+'</a></h3><div class="p" data-usd="'+p.price_usd_month+'"></div><div class="small">'+p.limits_es+'</div></div>';
    }).join("") + '<p class="mut small">Sugerencia orientativa basada en reglas simples, no en pruebas de rendimiento. Revisa siempre la página oficial.</p>';
    paint();
  });
}

// ---- Calculadora ----
var calc = document.getElementById("calc");
if(calc){
  function run(){
    var model = calc.model.value.split("|"), pin = +model[0], pout = +model[1];
    if(calc.model.value === "custom"){ pin = +calc.cin.value || 0; pout = +calc.cout.value || 0; }
    var tin = +calc.tin.value || 0, tout = +calc.tout.value || 0;
    var api = tin * pin + tout * pout;
    var out = document.getElementById("calc-out");
    var plans = [];
    D.tools.forEach(function(t){ t.plans.forEach(function(p){ if(!p.team && p.price_usd_month > 0) plans.push({t:t,p:p}); }); });
    plans.sort(function(a,b){ return a.p.price_usd_month - b.p.price_usd_month; });
    var cheaper = plans.filter(function(x){ return x.p.price_usd_month < api; });
    out.innerHTML = '<div class="card"><div class="mut small">Costo estimado pagando por uso (API, precio de lista)</div><div class="plan" style="border:0;padding:0;background:none"><div class="p" data-usd="'+api.toFixed(2)+'"></div></div>' +
      '<p class="small">'+(cheaper.length ? 'Hay <b>'+cheaper.length+'</b> planes de suscripción que cuestan menos que eso al mes. Si su cuota cubre tu trabajo, la suscripción te conviene. Ojo: las cuotas de los planes no siempre alcanzan para ese volumen.' : 'A ese volumen, pagar por uso cuesta menos que cualquier plan pago de la tabla.')+'</p>' +
      (cheaper.length ? '<ul class="small">'+cheaper.slice(-6).reverse().map(function(x){ return '<li><a href="herramientas/'+x.t.slug+'.html">'+x.t.name+' '+x.p.name+'</a> — <span data-usd="'+x.p.price_usd_month+'"></span>/mes · '+x.p.limits_es+'</li>'; }).join("")+'</ul>' : '') + '</div>';
    paint();
  }
  calc.addEventListener("input", run); calc.addEventListener("submit", function(e){ e.preventDefault(); run(); });
  calc.model.addEventListener("change", function(){ document.getElementById("custom-prices").hidden = calc.model.value !== "custom"; });
  run();
}

// ---- Formularios placeholder: no envían datos a ningún lado ----
document.querySelectorAll("form[data-placeholder]").forEach(function(f){
  f.addEventListener("submit", function(e){
    e.preventDefault();
    if(f.dataset.thanks){ location.href = f.dataset.thanks + "?demo=1"; return; }
    var m = f.querySelector(".form-msg");
    if(m){ m.textContent = "Gracias. (Versión de prueba: este formulario todavía no está conectado, no se guardó nada.)"; }
  });
});
// ---- Menú móvil ----
var mb = document.querySelector(".menu-btn"), nav = document.querySelector("nav.main");
if(mb && nav){ mb.addEventListener("click", function(){ var o = nav.classList.toggle("open"); mb.setAttribute("aria-expanded", o); }); }

// ---- CTA fijo para suscribirse (se oculta si lo cierras en esta sesión) ----
var sc = document.querySelector(".sticky-cta");
if(sc && !sessionStorage.getItem("limitesia-cta-cerrado")){
  var trigger = document.querySelector("[data-cta-trigger]");
  function chk(){
    var past = trigger ? trigger.getBoundingClientRect().bottom < 0 : window.scrollY > 600;
    sc.classList.toggle("show", past);
  }
  window.addEventListener("scroll", chk, {passive:true}); chk();
  sc.querySelector(".x").addEventListener("click", function(){ sc.classList.remove("show"); sessionStorage.setItem("limitesia-cta-cerrado","1"); window.removeEventListener("scroll", chk); });
}
paint();
})();
