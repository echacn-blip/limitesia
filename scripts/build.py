#!/usr/bin/env python3
"""LímitesIA – genera el sitio estático en site/ desde data/*.json + config.json. Solo librería estándar.
Configuración (config.json, o variables de entorno con el mismo nombre):
  SITE_URL            URL pública completa, p. ej. https://usuario.github.io/limitesia (canónicas, sitemap, OG)
  BASE_PATH           subruta de GitHub Pages, p. ej. /limitesia/ (solo para 404.html; el resto usa enlaces relativos)
  NEWSLETTER_USERNAME usuario de Buttondown. Vacío = modo demo (los formularios no envían nada)."""
import json, os, shutil, html, pathlib, datetime, re
ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA, OUT, ASSETS = ROOT/"data", ROOT/"site", ROOT/"assets"
CFG = json.loads((ROOT/"config.json").read_text()) if (ROOT/"config.json").exists() else {}
def cfg(k, d=""): return os.environ.get(k, CFG.get(k, d))
SITE_URL = cfg("SITE_URL", "https://USUARIO.github.io/limitesia").rstrip("/")
BASE_PATH = "/" + cfg("BASE_PATH", "/").strip("/") + "/" if cfg("BASE_PATH", "/").strip("/") else "/"
NL_USER = cfg("NEWSLETTER_USERNAME", "").strip()
NAME = "LímitesIA"

tools = json.loads((DATA/"tools.json").read_text())
fx = json.loads((DATA/"fx.json").read_text()) if (DATA/"fx.json").exists() else {"rates": {}}
changes = sorted(json.loads((DATA/"changes.json").read_text()) if (DATA/"changes.json").exists() else [], key=lambda c: c["date"], reverse=True)
e = lambda s: html.escape(str(s if s is not None else ""), quote=True)
CURS = [("USD","USD · Dólar"),("MXN","MXN · Peso mexicano"),("COP","COP · Peso colombiano"),("ARS","ARS · Peso argentino"),
        ("CLP","CLP · Peso chileno"),("PEN","PEN · Sol peruano"),("EUR","EUR · Euro")]
MONO = {"cursor":"Cu","claude-code":"CC","codex":"Cx","github-copilot":"GH","windsurf":"Ws","kiro":"Ki","zed":"Ze",
        "gemini-code-assist":"Gm","lovable":"Lv","bolt":"Bo","replit":"Rp"}
MESES = ["ene","feb","mar","abr","may","jun","jul","ago","sep","oct","nov","dic"]
def fecha(iso): y,m,d = iso[:10].split("-"); return f"{int(d)} {MESES[int(m)-1]} {y}"
def usd(x): return f"US${x:,.2f}".replace(".00","") if x is not None else "sin verificar"

N_TOOLS = len(tools["tools"]); N_PLANS = sum(len(t["plans"]) for t in tools["tools"])
N_SOURCES = len({s for t in tools["tools"] for s in t["sources"]})
UPDATED = fecha(tools["updated"])
pages = []

# ---------- datos destacados (calculados, nunca escritos a mano) ----------
indiv = [(t,p) for t in tools["tools"] for p in t["plans"] if not p.get("team") and not p.get("no_coding")]
paid = [(t,p) for t,p in indiv if p["price_usd_month"]]
min_price = min(p["price_usd_month"] for _,p in paid)
cheapest = [(t,p) for t,p in paid if p["price_usd_month"] == min_price]
ratio = [(p["included_usd"]/p["price_usd_month"], t, p) for t,p in paid if p.get("included_usd")]
best = max(ratio, key=lambda x: (x[0], -x[2]["price_usd_month"]))
last = next(c for c in changes if c["type"] != "base")
unverified = [(t,p) for t in tools["tools"] for p in t["plans"] if p["price_usd_month"] is None]

def nl_form(r, variant="hero", tag="web"):
    """Formulario de suscripción. Con NEWSLETTER_USERNAME: POST nativo a Buttondown (sin JS ni terceros).
    Sin él: modo demo, no envía nada y lleva a la página de 'gracias' para previsualizar el flujo."""
    if NL_USER:
        attrs = f'action="https://buttondown.com/api/emails/embed-subscribe/{e(NL_USER)}" method="post"'
        hidden = f'<input type="hidden" name="embed" value="1"><input type="hidden" name="tag" value="{e(tag)}">'
        demo = ""
    else:
        attrs = f'action="#" method="post" data-placeholder data-thanks="{r}gracias/index.html"'
        hidden = ""
        demo = '<div class="demo-note">Modo demo: el formulario aún no está conectado (falta NEWSLETTER_USERNAME). No se guarda ningún correo.</div>'
    uid = f"em-{variant}"
    return (f'<form class="nl-form" {attrs}>{hidden}<label class="sr" for="{uid}">Tu correo</label>'
            f'<div class="capture"><input id="{uid}" type="email" name="email" required placeholder="tu@correo.com" autocomplete="email">'
            f'<button class="btn pri" type="submit">Únete gratis →</button></div>'
            f'<div class="capture-note"><span>1 correo por semana</span><span>Sin spam</span><span>Te das de baja con un clic</span></div>{demo}</form>')

def cur_select(uid="cur"):
    return (f'<span class="cur-wrap"><label for="{uid}">Moneda</label><select id="{uid}" class="cur-select">'
            + "".join(f'<option value="{c}">{e(n)}</option>' for c,n in CURS) + '</select></span>')

def sponsor_slot(r, where):
    return (f'<aside class="sponsor" aria-label="Espacio publicitario"><span><b>Patrocinio</b>Espacio disponible · {e(where)}</span>'
            f'<a class="btn sec sm" href="{r}anunciate.html">Anúnciate aquí</a></aside>')

def badge(t): return f'<span class="mono-badge" aria-hidden="true">{MONO.get(t["slug"], t["name"][:2])}</span>'
def price_attr(p): return "null" if p["price_usd_month"] is None else f'{p["price_usd_month"]}'

def layout(path, title, desc, body, active="", sticky=True):
    depth = path.count("/"); r = "../"*depth
    canon = f"{SITE_URL}/{path}"
    canon = re.sub(r"index\.html$", "", canon)
    nav = [("index.html","Comparar"),("cambios.html","Cambios"),("cual-me-conviene.html","¿Cuál me conviene?"),
           ("calculadora.html","Calculadora"),("reporta.html","Reporta límites")]
    navh = "".join(f'<a href="{r}{h}"{" class=on aria-current=page" if h==active else ""}>{t}</a>' for h,t in nav)
    slim = {"tools":[{k:t[k] for k in ("slug","name","limit_type","plans")} for t in tools["tools"]], "fx": fx}
    sticky_html = (f'<div class="sticky-cta" role="complementary" aria-label="Suscripción"><span class="txt">📬 <b>Los cambios de precios, cada semana.</b> <span class="dim">Gratis.</span></span>'
                   f'<a class="btn pri sm" href="{r}suscribete/index.html">Únete</a><button class="x" type="button" aria-label="Cerrar">×</button></div>') if sticky else ""
    doc = f"""<!doctype html><html lang="es-419"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}">
<link rel="canonical" href="{e(canon)}">
<meta property="og:type" content="website"><meta property="og:site_name" content="{NAME}"><meta property="og:locale" content="es_419">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{e(canon)}"><meta property="og:image" content="{SITE_URL}/assets/og.png">
<meta name="twitter:card" content="summary_large_image"><meta name="theme-color" content="#08090b"><meta name="color-scheme" content="dark">
<link rel="preload" href="{r}assets/fonts/inter-var.woff2" as="font" type="font/woff2" crossorigin>
<link rel="icon" href="{r}assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{r}assets/style.css">
</head><body>
<a class="skip" href="#main">Saltar al contenido</a>
<header class="top"><div class="wrap">
<a class="logo" href="{r}index.html" aria-label="{NAME}, inicio"><span class="mark">L/</span><span>Límites<b>IA</b></span></a>
<nav class="main" aria-label="Principal">{navh}</nav>
<button class="btn sec sm menu-btn" type="button" aria-expanded="false" aria-label="Menú">☰</button>
<a class="btn pri sm" href="{r}suscribete/index.html">Únete a la lista</a>
</div></header>
<main id="main" class="wrap">{body}</main>
<footer><div class="wrap">
<div class="fgrid">
<div><a class="logo" href="{r}index.html"><span class="mark">L/</span><span>Límites<b>IA</b></span></a>
<p>Precios y límites de las herramientas de IA para programar, en tu moneda. Cada dato sale de la página oficial, con fecha y enlace. Independiente: no estamos afiliados a ningún proveedor.</p></div>
<div><h4>Explorar</h4><ul><li><a href="{r}index.html">Tabla comparativa</a></li><li><a href="{r}cambios.html">Historial de cambios</a></li><li><a href="{r}cual-me-conviene.html">¿Cuál me conviene?</a></li><li><a href="{r}calculadora.html">Calculadora</a></li></ul></div>
<div><h4>Comunidad</h4><ul><li><a href="{r}suscribete/index.html">Newsletter</a></li><li><a href="{r}reporta.html">Reporta tus límites</a></li><li><a href="{r}anunciate.html">Anúnciate</a></li><li><a href="{r}tools.json">Datos abiertos (JSON)</a></li></ul></div>
<div><h4>Lo que cambió esta semana</h4>{nl_form(r, "footer", "footer")}</div>
</div>
<div class="fbottom"><span>Datos revisados: {UPDATED} · {N_SOURCES} páginas oficiales</span><span>Sin cookies de rastreo ni analíticas</span></div>
</div></footer>
{sticky_html}
<script>window.LIMITES={json.dumps(slim, ensure_ascii=False)};</script><script src="{r}assets/app.js" defer></script>
</body></html>"""
    p = OUT/path; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(doc); pages.append(path)

if OUT.exists(): shutil.rmtree(OUT)
OUT.mkdir()

# ---------- HOME ----------
ch_names = " · ".join(f"{t['name']} {p['name']}" for t,p in cheapest)
term = f"""<div class="term" aria-label="Resumen de hoy"><div class="term-bar"><i></i><i></i><i></i><span>limitesia — hoy</span></div>
<pre><span class="c">$</span> <span class="v">limitesia resumen --fecha {tools["updated"]}</span>
<span class="c"># {N_SOURCES} páginas oficiales · {N_TOOLS} herramientas · {N_PLANS} planes</span>

<span class="k">plan_pago_mas_barato</span>  <span class="v">{usd(min_price)}/mes</span>
  <span class="c">↳ {e(ch_names)}</span>
<span class="k">mas_saldo_por_dolar</span>   <span class="v">{best[0]:.1f}x</span>
  <span class="c">↳ {e(best[1]["name"])} {e(best[2]["name"])}: {usd(best[2]["included_usd"])} por {usd(best[2]["price_usd_month"])}</span>
<span class="k">ultimo_cambio</span>         <span class="v">{fecha(last["date"])}</span>
  <span class="c">↳ {e(last["title"][:58])}{"…" if len(last["title"])>58 else ""}</span>
<span class="w">sin_verificar</span>         <span class="v">{len(unverified)} precio(s)</span>
  <span class="c">↳ {e(", ".join(t["name"]+" "+p["name"] for t,p in unverified))}</span></pre></div>"""

types = sorted({t["limit_type"] for t in tools["tools"]})
rows = []
for t in tools["tools"]:
    for p in t["plans"]:
        pr = "" if p["price_usd_month"] is None else p["price_usd_month"]
        bdg = ""
        if p["price_usd_month"] is None: bdg += '<span class="badge warn">precio sin verificar</span>'
        if p.get("team"): bdg += '<span class="badge">equipos</span>'
        if (t,p) in cheapest: bdg += '<span class="badge acc">más barato</span>'
        if p is best[2]: bdg += '<span class="badge acc">más saldo por dólar</span>'
        seat = '<small>por usuario</small>' if p.get("per_seat") else ""
        rows.append(f'<tr data-tool="{e(t["name"])}" data-price="{pr}" data-type="{e(t["limit_type"])}" data-team="{1 if p.get("team") else 0}" data-plan="{e(p["name"])}">'
            f'<td class="c-tool"><div class="tcell">{badge(t)}<div><a class="tname" href="herramientas/{t["slug"]}.html">{e(t["name"])}</a><span class="tkind">{e(t["kind"])}</span></div></div></td>'
            f'<td class="c-plan"><span class="pname">{e(p["name"])}</span><div>{bdg}</div></td>'
            f'<td class="c-price"><div class="price"><span data-usd="{price_attr(p)}"></span>{seat}</div><span class="bill">{e(p["billing_notes"])}</span></td>'
            f'<td class="c-lim"><div class="lim">{e(p["limits_es"])}</div><span class="badge">{e(t["limit_type"])}</span></td>'
            f'<td class="c-models"><div class="models">{e(p["models"])}</div></td>'
            f'<td class="c-src"><div class="src"><a href="{e(p["source_url"])}" rel="nofollow noopener" target="_blank">Fuente oficial ↗</a><div class="dim xs mono">{fecha(p["last_checked"])}</div></div></td></tr>')

home = f"""
<section class="hero" data-cta-trigger>
<div>
<div class="eyebrow"><i></i>Revisado {UPDATED} · {N_SOURCES} páginas oficiales</div>
<h1>Lo que <span class="hl">de verdad</span> te dan las IAs para programar, en tu moneda.</h1>
<p class="lead">Precios, cuotas y letra chica de Cursor, Claude Code, Codex, Copilot, Windsurf, Kiro y más. Comparados en una tabla, convertidos a MXN, COP, ARS, CLP, PEN o EUR, y con aviso cada vez que algo cambia.</p>
{nl_form("", "hero", "hero")}
</div>
{term}
</section>
<div class="trust" aria-label="De dónde salen los datos">
<span><b>{N_SOURCES}</b>páginas oficiales</span><span class="sep"></span><span><b>{N_TOOLS}</b>herramientas</span><span class="sep"></span>
<span><b>{N_PLANS}</b>planes</span><span class="sep"></span><span><b>7</b>monedas</span><span class="sep"></span><span>Cada dato con fecha y enlace</span><span class="sep"></span><span>Sin rastreo</span>
</div>

<section aria-labelledby="h-dest">
<div class="sh"><div><h2 id="h-dest">Lo destacado de hoy</h2><p>Calculado a partir de la tabla; abajo explicamos cómo.</p></div></div>
<div class="hcards">
<a class="hcard" href="herramientas/{cheapest[0][0]["slug"]}.html"><span class="lbl">Plan pago más barato</span>
<span class="big"><span data-usd="{min_price}"></span><small>/mes</small></span><span class="who">{e(ch_names)}</span>
<span class="how">El precio mensual más bajo entre los planes individuales pagos. Ojo: Cursor Plus solo incluye modelos Grok.</span></a>
<a class="hcard" href="herramientas/{best[1]["slug"]}.html"><span class="lbl">Más saldo incluido por dólar</span>
<span class="big">{best[0]:.1f}x</span><span class="who">{e(best[1]["name"])} {e(best[2]["name"])} · {usd(best[2]["included_usd"])} en créditos por {usd(best[2]["price_usd_month"])}</span>
<span class="how">Solo planes que publican su saldo en dólares: Copilot, Zed y Replit. No compara calidad ni velocidad.</span></a>
<a class="hcard" href="cambios.html"><span class="lbl">Último cambio</span>
<span class="big mono" style="font-size:22px">{fecha(last["date"])}</span><span class="who">{e(last["title"])}</span>
<span class="how">{e(last["tool_name"])} · fuente oficial en el historial.</span></a>
</div></section>

<section id="comparar" aria-labelledby="h-tabla">
<div class="sh"><div><h2 id="h-tabla">Compara {N_PLANS} planes de {N_TOOLS} herramientas</h2><p>Haz clic en las columnas para ordenar. Los límites están tal como los describe cada página oficial.</p></div></div>
<div class="controls">
<span class="search"><label class="sr" for="f-q">Buscar</label><input id="f-q" type="search" placeholder="Busca herramienta, plan o modelo…"></span>
<label class="sr" for="f-type">Tipo de límite</label><select id="f-type"><option value="">Todos los tipos de límite</option>{"".join(f'<option>{e(x)}</option>' for x in types)}</select>
<label class="sr" for="f-max">Precio máximo</label><select id="f-max"><option value="">Cualquier precio</option><option value="10">Hasta US$10</option><option value="20">Hasta US$20</option><option value="40">Hasta US$40</option><option value="100">Hasta US$100</option></select>
{cur_select("cur-home")}
<label class="chip"><input type="checkbox" id="f-free" checked> Gratis</label>
<label class="chip"><input type="checkbox" id="f-team"> Equipos</label>
<span id="f-count" class="count" aria-live="polite"></span></div>
<p class="note cur-note" hidden>Conversión referencial con el tipo de cambio del día. El cobro real puede sumar IVA, percepciones o impuestos locales y comisiones de tu banco; en App Store y Google Play el precio suele ser otro.</p>
<div class="tablewrap"><table id="cmp"><thead><tr>
<th data-sort="tool" scope="col">Herramienta</th><th data-sort="plan" scope="col">Plan</th><th data-sort="price" scope="col">Precio / mes</th><th scope="col">Límites según la página oficial</th><th scope="col">Modelos</th><th scope="col">Fuente</th></tr></thead>
<tbody>{"".join(rows)}</tbody></table></div>
<p class="fine">{e(tools["disclaimer"])}</p>
{sponsor_slot("", "debajo de la tabla comparativa")}
</section>

<section class="cta-band" aria-labelledby="h-cta">
<div><h2 id="h-cta">Los planes cambian cada semana. Entérate primero.</h2>
<p>Cada semana mandamos un correo corto con lo que cambió, con fecha y fuente.</p>
<ul><li>Subidas, bajadas y límites nuevos</li><li>Precios en tu moneda</li><li>Datos de la comunidad sobre cuánto rinde cada plan</li></ul></div>
<div>{nl_form("", "band", "band")}</div>
</section>

<section aria-labelledby="h-cambios" class="grid g2" style="align-items:start">
<div><div class="sh"><div><h2 id="h-cambios">Últimos cambios</h2><p>Con fecha y enlace a la fuente.</p></div></div>
<ul class="timeline">{"".join(f'<li><time>{fecha(c["date"])}</time><b>{e(c["title"])}</b><div class="dim small">{e(c["tool_name"])}</div></li>' for c in changes[:5])}</ul>
<a class="btn sec sm" href="cambios.html">Ver el historial completo →</a></div>
<div class="grid">
<a class="hcard" href="cual-me-conviene.html"><span class="lbl">Quiz · 30 segundos</span><h3>¿Cuál me conviene?</h3><span class="mut small">4 preguntas y te sugerimos 3 planes para tu presupuesto.</span></a>
<a class="hcard" href="calculadora.html"><span class="lbl">Calculadora</span><h3>¿Suscripción o pago por uso?</h3><span class="mut small">Compara lo que costaría la API con lo que cuesta cada plan.</span></a>
<a class="hcard" href="reporta.html"><span class="lbl">Comunidad</span><h3>¿Te quedaste sin cuota?</h3><span class="mut small">Cuéntanos cuánto te rinde tu plan. Publicaremos los datos agrupados.</span></a>
</div></section>
"""
layout("index.html", f"{NAME}: precios y límites de las IAs para programar, en tu moneda",
       f"Compara {N_PLANS} planes de {N_TOOLS} herramientas de IA para programar (Cursor, Claude Code, Codex, Copilot, Windsurf, Kiro…) en MXN, COP, ARS, CLP, PEN y EUR. Datos oficiales con fecha.", home, "index.html")

# ---------- herramientas ----------
for t in tools["tools"]:
    plans = "".join(f"""<div class="plan"><div class="dim xs mono">{e(p["name"]).upper()}{' · EQUIPOS' if p.get('team') else ''}</div>
<div class="p" data-usd="{price_attr(p)}"></div><div class="dim small">{e(p["billing_notes"])}</div>
<p style="margin:4px 0">{e(p["limits_es"])}</p><blockquote lang="en">“{e(p["limits_quote"])}”</blockquote>
<div class="small mut"><b>Modelos:</b> {e(p["models"])}</div>
<div class="xs dim mono">Revisado {fecha(p["last_checked"])} · <a href="{e(p["source_url"])}" rel="nofollow noopener" target="_blank">fuente ↗</a></div></div>""" for p in t["plans"])
    tch = [c for c in changes if c.get("tool") == t["slug"]]
    ch = "".join(f'<li><time>{fecha(c["date"])}</time><b>{e(c["title"])}</b><p>{e(c["detail"])}</p></li>' for c in tch) or '<li><b>Sin cambios registrados todavía.</b><p>Revisamos la página oficial todos los días.</p></li>'
    aff = ('<p class="todo">TODO afiliado: enlace pendiente. Cuando exista irá marcado como “enlace de afiliado”.</p>' if t.get("affiliate_todo") else "")
    priced = [p["price_usd_month"] for p in t["plans"] if p["price_usd_month"]]
    body = f"""<div class="page-hero"><div class="crumbs"><a href="../index.html">Comparar</a> / {e(t["name"])}</div>
<div style="display:flex;gap:14px;align-items:center;margin-bottom:12px">{badge(t).replace('mono-badge"','mono-badge" style="width:48px;height:48px;font-size:16px"')}<span class="eyebrow" style="margin:0"><i></i>Revisado {fecha(t["plans"][0]["last_checked"])}</span></div>
<h1>{e(t["name"])}: precios y límites</h1><p class="lead">{e(t["summary"])}</p>
<div class="pills"><span class="badge">{e(t["vendor"])}</span><span class="badge">{e(t["kind"])}</span><span class="badge acc">Límite: {e(t["limit_type"])}</span></div></div>
<div class="controls">{cur_select("cur-t")}</div><p class="note cur-note" hidden>Conversión referencial; impuestos locales, comisiones y precios de tiendas de apps pueden cambiar el total.</p>
<section><div class="grid g3">{plans}</div></section>
<section class="grid g2" style="align-items:start">
<div class="card"><h3>A tener en cuenta</h3><ul class="mut">{"".join(f"<li>{e(n)}</li>" for n in t["notes"])}</ul>{aff}
<p class="xs dim">Fuentes: {" · ".join(f'<a href="{e(s)}" rel="nofollow noopener" target="_blank">{e(s)}</a>' for s in t["sources"])}</p></div>
<div><h3>Historial de {e(t["name"])}</h3><ul class="timeline" style="margin-top:12px">{ch}</ul></div></section>
{sponsor_slot("../", "página de " + t["name"])}
<section class="cta-band"><div><h2>¿{e(t["name"])} cambia sus planes?</h2><p>Te avisamos en el correo semanal, con la fuente oficial.</p></div><div>{nl_form("../", "tool", t["slug"])}</div></section>"""
    layout(f"herramientas/{t['slug']}.html", f"{t['name']}: precios, planes y límites ({UPDATED}) | {NAME}",
           f"Cuánto cuesta {t['name']} y qué límites tiene cada plan, en tu moneda. Desde US${min(priced or [0]):g}/mes. Datos oficiales con fecha y fuente.", body)

# ---------- cambios ----------
def ch_item(c):
    lab = {"documentado":"Documentado","detectado":"Detectado automáticamente","base":"Registro"}.get(c["type"], c["type"])
    rev = '' if c.get("reviewed", True) else '<span class="badge warn">pendiente de revisión</span>'
    money = ""
    if c.get("money_added") or c.get("money_removed"):
        money = f'<p class="mono xs">+ {e(", ".join(c.get("money_added", [])) or "—")} &nbsp; − {e(", ".join(c.get("money_removed", [])) or "—")}</p>'
    src = f' · <a href="{e(c["url"])}" rel="nofollow noopener" target="_blank">fuente ↗</a>' if c.get("url") else ""
    return f'<li><time>{fecha(c["date"])}</time><span class="badge acc">{e(lab)}</span>{rev}<div><b>{e(c["title"])}</b></div><div class="dim small">{e(c["tool_name"])}{src}</div><p>{e(c["detail"])}</p>{money}</li>'
body = f"""<div class="page-hero"><span class="eyebrow"><i></i>Se actualiza a diario</span><h1>Historial de cambios</h1>
<p class="lead">Todos los días comparamos las páginas oficiales de precios con la versión anterior. Los cambios que detecta el robot se revisan a mano antes de tocar la tabla.</p></div>
<section class="grid g2" style="grid-template-columns:1.5fr 1fr;align-items:start"><ul class="timeline">{"".join(ch_item(c) for c in changes)}</ul>
<div class="card" style="position:sticky;top:84px"><h3>Recibe cada cambio en tu correo</h3><p class="small">Un resumen por semana. Gratis.</p>{nl_form("", "cambios", "cambios")}</div></section>
{sponsor_slot("", "historial de cambios")}"""
layout("cambios.html", f"Cambios de precios y límites en IAs para programar | {NAME}",
       "Historial fechado de cambios en planes, precios y límites de Cursor, Claude Code, Codex, Copilot, Windsurf y más.", body, "cambios.html")

# ---------- quiz ----------
def opts(name, items, checked):
    return '<div class="opts">' + "".join(f'<label><input type="radio" name="{name}" value="{v}"{" checked" if v==checked else ""}><span>{e(l)}</span></label>' for v,l in items) + '</div>'
body = f"""<div class="page-hero"><span class="eyebrow"><i></i>30 segundos</span><h1>¿Cuál me conviene?</h1><p class="lead">4 preguntas. Te sugerimos 3 planes según tu presupuesto y tu forma de trabajar.</p></div>
<form id="quiz" class="quiz card">
<fieldset><legend>1. ¿Cuánto quieres gastar al mes (USD)?</legend>{opts("budget",[("0","Nada"),("10","Hasta 10"),("20","Hasta 20"),("40","Hasta 40"),("100","Hasta 100"),("500","Más de 100")],"20")}</fieldset>
<fieldset><legend>2. ¿Cómo trabajas?</legend>{opts("work",[("ide","IDE con IA (tipo VS Code)"),("terminal","Agente en la terminal"),("editor","Con mi editor de siempre"),("nocode","No programo: armo apps chateando")],"ide")}</fieldset>
<fieldset><legend>3. ¿Cuánto lo usas?</legend>{opts("use",[("light","Poco, proyectos personales"),("daily","Todos los días en el trabajo"),("heavy","Agentes horas seguidas")],"daily")}</fieldset>
<fieldset><legend>4. ¿Modelo favorito?</legend>{opts("model",[("any","Me da igual"),("claude","Claude"),("gpt","GPT"),("gemini","Gemini")],"any")}</fieldset>
<div style="display:flex;gap:12px;align-items:center;flex-wrap:wrap">{cur_select("cur-q")}<button class="btn pri" type="submit">Ver sugerencias →</button></div>
<div id="quiz-out" class="result" aria-live="polite"></div></form>"""
layout("cual-me-conviene.html", f"¿Qué IA para programar me conviene? Quiz | {NAME}",
       "Responde 4 preguntas y descubre qué plan de Cursor, Claude Code, Codex, Copilot u otras herramientas encaja con tu presupuesto.", body, "cual-me-conviene.html")

# ---------- calculadora ----------
models = [("Claude Haiku 5.5 (≤100K tokens por prompt)",0.5,2.5),("Claude Sonnet 5.5",2,10),("Claude Opus 5.5",4,20),("Claude Fable 5.1",10,50)]
mopts = "".join(f'<option value="{a}|{b}">{e(n)} · US${a:g} entrada / US${b:g} salida</option>' for n,a,b in models)
body = f"""<div class="page-hero"><span class="eyebrow"><i></i>Herramienta</span><h1>¿Suscripción o pago por uso?</h1><p class="lead">Estima cuánto pagarías usando la API directamente y compáralo con los planes mensuales.</p></div>
<form id="calc" class="card form" style="max-width:none">
<label>Modelo (precio de lista de API por millón de tokens)<select name="model">{mopts}<option value="custom">Otro (ingresar precio)</option></select></label>
<div id="custom-prices" hidden class="grid g2"><label>US$ por millón de entrada<input name="cin" type="number" step="0.01" min="0" value="1"></label><label>US$ por millón de salida<input name="cout" type="number" step="0.01" min="0" value="5"></label></div>
<div class="grid g3"><label>Millones de tokens de entrada al mes<input name="tin" type="number" min="0" step="1" value="20"></label>
<label>Millones de tokens de salida al mes<input name="tout" type="number" min="0" step="0.5" value="2"></label><label>Moneda<select class="cur-select" aria-label="Moneda">{"".join(f'<option value="{c}">{e(n)}</option>' for c,n in CURS)}</select></label></div>
<p class="dim small">Los agentes leen mucho más de lo que escriben: es normal tener 10 veces más tokens de entrada que de salida. No incluye descuentos por caché ni batch. Precios tomados de <a href="https://claude.com/pricing" rel="nofollow noopener" target="_blank">claude.com/pricing</a> el {UPDATED}.</p></form>
<div id="calc-out" class="result" style="margin-top:14px"></div>"""
layout("calculadora.html", f"Calculadora: ¿suscripción o pago por uso de API? | {NAME}",
       "Calcula cuánto te costaría usar la API de Claude por uso y compáralo con los planes de Cursor, Claude Code, Codex, Copilot y más.", body, "calculadora.html")

# ---------- anúnciate ----------
body = f"""<div class="page-hero"><span class="eyebrow"><i></i>Patrocinios</span><h1>Anúnciate en {NAME}</h1><p class="lead">Llega a desarrolladores hispanohablantes justo cuando están comparando herramientas de IA para programar.</p></div>
<section class="grid g3">
<div class="card"><span class="badge acc">Tabla</span><h3 style="margin-top:10px">Fila destacada</h3><p class="small">Un espacio marcado como “Patrocinado” debajo de la tabla comparativa.</p></div>
<div class="card"><span class="badge acc">Newsletter</span><h3 style="margin-top:10px">Mención semanal</h3><p class="small">Un bloque patrocinado en “Lo que cambió esta semana”.</p></div>
<div class="card"><span class="badge acc">Páginas</span><h3 style="margin-top:10px">Páginas de herramientas</h3><p class="small">Un espacio en las páginas de cada herramienta y en el historial.</p></div></section>
<p class="note">Reglas: todo anuncio va marcado como patrocinado. Pagar no cambia los datos, el orden ni los precios de la tabla. Publicaremos las tarifas cuando tengamos datos reales de audiencia.</p>
<section class="card"><h2>Escríbenos</h2><form class="form" data-placeholder action="#" method="post" style="margin-top:14px">
<label>Empresa<input type="text" name="empresa" required></label><label>Correo<input type="email" name="email" required></label><label>¿Qué te interesa?<textarea name="msg" rows="4"></textarea></label>
<button class="btn pri" type="submit">Enviar</button><span class="todo">TODO: conectar este formulario (aún no envía nada). Correo de contacto: TODO.</span><span class="form-msg"></span></form></section>"""
layout("anunciate.html", f"Anúnciate en {NAME}: llega a desarrolladores hispanohablantes",
       "Espacios de patrocinio, siempre marcados, en la tabla comparativa, las páginas de herramientas y el newsletter semanal de LímitesIA.", body)

# ---------- reporta ----------
topts = "".join(f'<option>{e(t["name"])} — {e(p["name"])}</option>' for t in tools["tools"] for p in t["plans"])
body = f"""<div class="page-hero"><span class="eyebrow"><i></i>Datos de la comunidad</span><h1>Reporta tus límites</h1><p class="lead">Las páginas oficiales dicen “uso limitado” o “5x más”. Ayúdanos a saber cuánto rinde cada plan de verdad. Publicaremos los resultados agrupados, sin datos personales.</p></div>
<form class="card form" data-placeholder action="#" method="post" style="max-width:720px">
<label>Plan<select name="plan" required>{topts}</select></label>
<label>¿Qué modelo usaste más?<input type="text" name="modelo" placeholder="Ej.: Sonnet 5.5, GPT-6.1 Sol, Auto…"></label>
<label>¿Cuánto tardaste en llegar al límite?<select name="tiempo"><option>Nunca llegué</option><option>Menos de 1 hora</option><option>1 a 3 horas</option><option>Más de 3 horas</option><option>Se me acabó la cuota semanal</option><option>Se me acabó la cuota mensual</option></select></label>
<label>País (opcional)<input type="text" name="pais" placeholder="México, Colombia, Argentina…"></label>
<label>¿Cuánto te cobraron en tu moneda, con impuestos? (opcional)<input type="text" name="cobro" placeholder="Ej.: MXN 399 en App Store"></label>
<label>Comentarios<textarea name="comentarios" rows="4"></textarea></label>
<button class="btn pri" type="submit">Enviar reporte</button><span class="todo">TODO: conectar a un formulario o almacenamiento (aún no guarda nada).</span><span class="form-msg"></span></form>"""
layout("reporta.html", f"Reporta cuánto te rinde tu plan de IA para programar | {NAME}",
       "Comparte cuánto te dura la cuota de Cursor, Claude Code, Codex, Copilot y otros para crear datos reales de la comunidad.", body, "reporta.html")

# ---------- suscribete / gracias / confirmado ----------
body = f"""<section class="hero" style="grid-template-columns:1.1fr .9fr">
<div><span class="eyebrow"><i></i>Newsletter semanal · gratis</span>
<h1>Lo que cambió esta semana en las <span class="hl">IAs para programar</span>.</h1>
<p class="lead">Una vez por semana: qué subió, qué bajó y qué límites cambiaron en Cursor, Claude Code, Codex, Copilot, Windsurf y {N_TOOLS-5} herramientas más. Con fuente oficial y en tu moneda.</p>
{nl_form("../", "suscribete", "suscribete")}
<p class="dim xs" style="margin-top:14px">Te enviaremos un correo para confirmar la suscripción (doble opt-in). Solo usamos tu correo para mandarte el newsletter.</p></div>
<div class="card"><h3>Qué recibes cada semana</h3>
<ol class="steps"><li><div><b>Cambios con fecha y fuente</b><div class="dim small">Precios, cuotas y modelos de {N_PLANS} planes de {N_TOOLS} herramientas.</div></div></li>
<li><div><b>Precios en tu moneda</b><div class="dim small">MXN, COP, ARS, CLP, PEN y EUR, con el tipo de cambio del día.</div></div></li>
<li><div><b>Datos de la comunidad</b><div class="dim small">Cuánto rinde cada plan de verdad, según los reportes de lectores.</div></div></li></ol>
<a class="btn sec sm" href="../newsletter/001.html">Ver el número 1 (vista previa) →</a></div>
</section>"""
layout("suscribete/index.html", f"Suscríbete al newsletter de {NAME}: cambios de precios de las IAs para programar",
       "Un correo por semana con los cambios de precios y límites de Cursor, Claude Code, Codex, Copilot y más, en tu moneda. Gratis.", body, sticky=False)

body = f"""<div class="page-hero center" style="max-width:640px"><div class="big-emoji" aria-hidden="true">📬</div>
<h1>Revisa tu correo para confirmar</h1><p class="lead center">Te acabamos de enviar un correo. Tu suscripción se activa cuando haces clic en el enlace de confirmación.</p>
<p class="demo-note" id="demo-flag" hidden>Modo demo: el formulario no está conectado, así que no se envió ningún correo.</p>
<ol class="steps" style="text-align:left"><li><div><b>Abre el correo de confirmación</b><div class="dim small">Llega en 1–2 minutos.</div></div></li>
<li><div><b>Haz clic en “Confirmar”</b><div class="dim small">Sin ese clic no te llegará nada (doble opt-in).</div></div></li>
<li><div><b>¿No llegó?</b><div class="dim small">Revisa spam y la pestaña Promociones, y agrega al remitente a tus contactos.</div></div></li></ol>
<a class="btn sec" href="../index.html">Volver a la tabla</a></div>
<script>if(/[?&]demo=1/.test(location.search))document.getElementById("demo-flag").hidden=false;</script>"""
layout("gracias/index.html", f"Revisa tu correo para confirmar | {NAME}", "Confirma tu suscripción al newsletter de LímitesIA desde el correo que te enviamos.", body, sticky=False)

body = f"""<div class="page-hero center" style="max-width:680px"><div class="big-emoji" aria-hidden="true">✅</div>
<h1>¡Listo, ya estás dentro!</h1><p class="lead center">Confirmaste tu suscripción. El próximo número de “Lo que cambió esta semana” te llega a tu correo.</p>
<div class="grid g3" style="text-align:left;margin-top:24px">
<a class="hcard" href="../index.html"><span class="lbl">Ahora</span><h3>Compara planes</h3><span class="dim small">{N_PLANS} planes en tu moneda.</span></a>
<a class="hcard" href="../cual-me-conviene.html"><span class="lbl">30 s</span><h3>Haz el quiz</h3><span class="dim small">Te sugerimos 3 planes.</span></a>
<a class="hcard" href="../reporta.html"><span class="lbl">Ayúdanos</span><h3>Reporta tus límites</h3><span class="dim small">Datos reales de la comunidad.</span></a></div></div>"""
layout("confirmado/index.html", f"Suscripción confirmada | {NAME}", "Tu suscripción al newsletter de LímitesIA está confirmada.", body, sticky=False)

# ---------- 404 (GitHub Pages lo sirve en cualquier ruta: usa BASE_PATH) ----------
p404 = (OUT/"index.html").read_text()
nf = f"""<div class="page-hero center"><div class="big-emoji">🔍</div><h1>Esta página no existe</h1><p class="lead center">Puede que el enlace esté mal o que la página se haya movido.</p><a class="btn pri" href="index.html">Ir a la tabla comparativa</a></div>"""
p404 = re.sub(r'<main id="main" class="wrap">.*</main>', lambda m: f'<main id="main" class="wrap">{nf}</main>', p404, flags=re.S)
p404 = p404.replace("<head><meta charset=\"utf-8\">", f'<head><meta charset="utf-8"><base href="{BASE_PATH}"><meta name="robots" content="noindex">', 1)
(OUT/"404.html").write_text(p404)

# ---------- assets, newsletter, sitemap ----------
shutil.copytree(ASSETS, OUT/"assets")
shutil.copy(DATA/"tools.json", OUT/"tools.json")
nl = ROOT/"newsletter"/"001.html"
if nl.exists():
    (OUT/"newsletter").mkdir(exist_ok=True); shutil.copy(nl, OUT/"newsletter"/"001.html")
(OUT/".nojekyll").write_text("")
today = datetime.date.today().isoformat()
sm = "".join(f"<url><loc>{SITE_URL}/{re.sub(r'index[.]html$','',p)}</loc><lastmod>{today}</lastmod></url>" for p in pages)
(OUT/"sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>')
(OUT/"robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")
print(f"Sitio generado en {OUT} — {len(pages)} páginas · newsletter: {'Buttondown/'+NL_USER if NL_USER else 'MODO DEMO'}")
