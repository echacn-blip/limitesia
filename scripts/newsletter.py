#!/usr/bin/env python3
"""Genera newsletter/001.md y newsletter/001.html (HTML apto para correo: tablas y estilos en línea).
Los precios en moneda local salen de data/fx.json; los enlaces usan SITE_URL de config.json."""
import json, pathlib, html, os
ROOT = pathlib.Path(__file__).resolve().parents[1]
CFG = json.loads((ROOT/"config.json").read_text())
SITE = os.environ.get("SITE_URL", CFG["SITE_URL"]).rstrip("/")
FX = json.loads((ROOT/"data/fx.json").read_text())
R = FX["rates"]
def n(x, dec=0):
    s = f"{x:,.{dec}f}"; return s.replace(",", "X").replace(".", ",").replace("X", ".")
def local(u): return f"MXN {n(u*R['MXN'])} · COP {n(u*R['COP'])} · ARS {n(u*R['ARS'])} · CLP {n(u*R['CLP'])}"
FXDATE = "19 oct 2026"

SUBJECT = "Codex retira GPT-5.5, se acaba el SWE-2 gratis y qué plan rinde más por dólar"
PREVIEW = "Lo que cambió esta semana en 43 planes de 11 herramientas de IA para programar, en tu moneda."
CHANGES = [
 ("14 oct", "Codex retiró GPT-5.5 si entras con ChatGPT",
  "Desde el 14 de octubre a las 19:00 UTC (15:00 en Nueva York), GPT-5.5 ya no aparece en Codex cuando inicias sesión con tu cuenta de ChatGPT. Si usas Codex con API key, esto no te afecta.",
  "https://developers.openai.com/codex/pricing/"),
 ("16 oct", "Se acabó el SWE-2 gratis en Devin Desktop (ex Windsurf)",
  "La promo decía “Free use of SWE-2… through October 16, 2026”. Ya terminó: desde ahora SWE-2 gasta tu cuota diaria y semanal igual que los demás modelos.",
  "https://devin.ai/pricing"),
 ("19 oct", "Arrancó el registro diario de LímitesIA",
  "Ya guardamos una copia de 13 páginas oficiales de precios. Si cambia una sola línea, la vas a ver en el historial.",
  f"{SITE}/cambios.html"),
]
VALUE = [  # (plan, US$, qué recibes según la página oficial, fuente)
 ("GitHub Copilot Max", 100, "US$200 en créditos al mes → 2,0x lo que pagas", "https://github.com/features/copilot/plans"),
 ("GitHub Copilot Pro+", 39, "US$70 en créditos → 1,8x", "https://github.com/features/copilot/plans"),
 ("GitHub Copilot Pro", 10, "US$15 en créditos + autocompletado ilimitado → 1,5x", "https://github.com/features/copilot/plans"),
 ("Cursor Plus", 8, "Pool semanal compartido; solo modelos Grok", "https://cursor.com/pricing"),
 ("Claude Pro (con Claude Code)", 20, "“At least 5x” el uso de Free por sesión de 5 h, más un tope semanal", "https://claude.com/pricing"),
 ("ChatGPT Plus (Codex)", 20, "Cada 5 h: 15–160 mensajes con GPT-6.1 Sol o 350–3.000 con GPT-6 Luna (estimación oficial)", "https://developers.openai.com/codex/pricing/"),
 ("Kiro Pro", 20, "1.000 créditos al mes; extras a US$0,04", "https://kiro.dev/pricing/"),
]
CURIOSO = ("Copilot es de los pocos que publica su cuota en dólares: 1 crédito = US$0,01. Con Max pagas US$100 y recibes US$200 en créditos. "
           "Es el mejor ratio publicado en dólares que encontramos (Zed Pro, en cambio, te da US$5 por US$10). "
           "Ojo: más créditos no significa mejor modelo ni más velocidad. Solo significa que te rinde más el dinero.")

md = [f"""---
número: 1
fecha: 2026-10-19
asunto: "{SUBJECT}"
preheader: "{PREVIEW}"
estado: BORRADOR (no enviado)
---

**Asunto:** {SUBJECT}
**Texto de vista previa:** {PREVIEW}

# Lo que cambió esta semana · #1

¡Hola! 👋 Bienvenido al primer número de **LímitesIA**. Cada semana revisamos **43 planes de 11 herramientas** de IA para programar y te contamos qué cambió, con fecha, fuente oficial y precios en tu moneda. Te toma 2 minutos.

## 🔄 Lo que cambió
"""]
for d,t,txt,u in CHANGES: md.append(f"**{d} · {t}.** {txt} → [Fuente]({u})\n")
md.append(f"""## 💸 Lo que más rinde por dólar

Precios mensuales en US$ y en tu moneda (tipo de cambio del {FXDATE}, open.er-api.com):
""")
for p,u,q,s in VALUE: md.append(f"- **{p} · US${u}** ({local(u)}): {q}. [Fuente]({s})")
md.append(f"""
⚠️ La conversión es una referencia: no incluye IVA, percepciones ni comisiones de tu banco, y en App Store o Google Play el precio suele ser otro. La tabla completa, también en PEN y EUR, está en [{SITE.replace('https://','')}]({SITE}/index.html).

## 🤓 Dato curioso

{CURIOSO}

## 🙋 Te toca a ti

¿Cuánto te dura tu plan antes de chocar con el límite? ¿Cuánto te cobraron en pesos, con impuestos? **[Repórtalo en 1 minuto]({SITE}/reporta.html)**. Es anónimo. Con suficientes reportes publicaremos el primer ranking de “rendimiento real” hecho por la comunidad hispana.

---

> **[ESPACIO PATROCINADO · DISPONIBLE]**
> TODO: aquí va 1 mención marcada como “Patrocinado” (logo + 2 líneas + enlace). Pagar no cambia los datos ni el orden de la tabla. ¿Te interesa? [{SITE.replace('https://','')}/anunciate.html]({SITE}/anunciate.html)

---

*Recibes este correo porque te suscribiste a LímitesIA y confirmaste tu correo. Si ya no quieres recibirlo, date de baja con un clic usando el enlace al pie de este correo. LímitesIA es independiente y no está afiliado a ninguna de estas empresas. Si algún día hay enlaces de afiliado, irán marcados.*
""")
(ROOT/"newsletter/001.md").write_text("\n".join(md))

# ---- HTML para correo ----
e = html.escape
A = "color:#5a7d00;text-decoration:underline"
def p(t, extra=""): return f'<p style="margin:0 0 14px;font-size:16px;line-height:1.6;color:#1d1f23;{extra}">{t}</p>'
def h2(t): return f'<h2 style="margin:28px 0 12px;font-size:20px;line-height:1.3;color:#0b0c0e">{t}</h2>'
ch = "".join(f'<tr><td style="padding:12px 0;border-bottom:1px solid #e7e9ee;font-size:15px;line-height:1.55;color:#1d1f23"><span style="font-family:Menlo,Consolas,monospace;font-size:12px;background:#eef8cf;color:#3b5200;padding:2px 6px;border-radius:4px">{e(d)}</span> <b>{e(t)}.</b><br>{e(txt)} <a href="{e(u)}" style="{A}">Fuente</a></td></tr>' for d,t,txt,u in CHANGES)
vr = "".join(f'<tr><td style="padding:10px 8px 10px 0;border-bottom:1px solid #e7e9ee;font-size:14px;line-height:1.45;vertical-align:top"><b>{e(pl)}</b><br><span style="color:#5b616e">{e(q)}</span> <a href="{e(s)}" style="{A};font-size:12px">fuente</a></td><td style="padding:10px 0;border-bottom:1px solid #e7e9ee;font-size:14px;text-align:right;vertical-align:top;white-space:nowrap"><b>US${u}</b><br><span style="color:#5b616e;font-size:12px">MXN {n(u*R["MXN"])}<br>COP {n(u*R["COP"])}<br>ARS {n(u*R["ARS"])}<br>CLP {n(u*R["CLP"])}</span></td></tr>' for pl,u,q,s in VALUE)
doc = f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(SUBJECT)}</title></head>
<body style="margin:0;padding:0;background:#f3f4f6">
<div style="display:none;max-height:0;overflow:hidden;opacity:0">{e(PREVIEW)}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f3f4f6"><tr><td align="center" style="padding:24px 12px">
<table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:#ffffff;border-radius:12px;font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif">
<tr><td style="background:#0b0c0e;border-radius:12px 12px 0 0;padding:20px 28px"><span style="display:inline-block;background:#c4f042;color:#0b0f02;font-family:Menlo,Consolas,monospace;font-weight:700;font-size:13px;padding:4px 7px;border-radius:6px">L/</span> <span style="color:#f4f5f7;font-weight:700;font-size:18px">Límites<span style="color:#c4f042">IA</span></span><div style="color:#9aa1ad;font-size:13px;margin-top:6px;font-family:Menlo,Consolas,monospace">#1 · 19 oct 2026 · Lo que cambió esta semana</div></td></tr>
<tr><td style="padding:28px">
{p("¡Hola! 👋 Bienvenido al primer número de <b>LímitesIA</b>. Cada semana revisamos <b>43 planes de 11 herramientas</b> de IA para programar y te contamos qué cambió, con fecha, fuente oficial y precios en tu moneda. Te toma 2 minutos.")}
{h2("🔄 Lo que cambió")}
<table role="presentation" width="100%" cellpadding="0" cellspacing="0">{ch}</table>
{h2("💸 Lo que más rinde por dólar")}
{p(f"Precios mensuales en US$ y en tu moneda (tipo de cambio del {FXDATE}, open.er-api.com).", "font-size:14px;color:#5b616e")}
<table role="presentation" width="100%" cellpadding="0" cellspacing="0">{vr}</table>
{p(f'⚠️ La conversión es una referencia: no incluye IVA, percepciones ni comisiones de tu banco, y en App Store o Google Play el precio suele ser otro. <a href="{SITE}/index.html" style="{A}">Ver la tabla completa (también en PEN y EUR)</a>.', "font-size:13px;color:#5b616e;margin-top:12px")}
{h2("🤓 Dato curioso")}
<table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr><td style="background:#f6fbe6;border-left:4px solid #9cc31a;padding:14px 16px;font-size:15px;line-height:1.6;color:#1d1f23;border-radius:0 8px 8px 0">{e(CURIOSO)}</td></tr></table>
{h2("🙋 Te toca a ti")}
{p("¿Cuánto te dura tu plan antes de chocar con el límite? ¿Cuánto te cobraron en pesos, con impuestos? Es anónimo. Con suficientes reportes publicaremos el primer ranking de “rendimiento real” hecho por la comunidad hispana.")}
<table role="presentation" cellpadding="0" cellspacing="0"><tr><td style="background:#c4f042;border-radius:8px"><a href="{SITE}/reporta.html" style="display:inline-block;padding:12px 20px;color:#0b0f02;font-weight:700;text-decoration:none;font-size:15px">Reportar mis límites →</a></td></tr></table>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin-top:28px"><tr><td style="border:2px dashed #c9ced8;border-radius:10px;padding:16px;font-size:14px;line-height:1.5;color:#5b616e">
<div style="font-family:Menlo,Consolas,monospace;font-size:11px;letter-spacing:.08em;color:#8a6d00;margin-bottom:6px">ESPACIO PATROCINADO · DISPONIBLE</div>
<!-- TODO patrocinador: logo + 2 líneas + enlace, marcado como "Patrocinado" -->
Aquí va una mención marcada como “Patrocinado”. Pagar no cambia los datos ni el orden de la tabla. <a href="{SITE}/anunciate.html" style="{A}">Anúnciate aquí</a>.</td></tr></table>
</td></tr>
<tr><td style="padding:20px 28px;border-top:1px solid #e7e9ee;font-size:12px;line-height:1.55;color:#8a909c">Recibes este correo porque te suscribiste a LímitesIA y confirmaste tu correo. Si ya no quieres recibirlo, date de baja con un clic usando el enlace al pie de este correo. LímitesIA es independiente y no está afiliado a ninguna de estas empresas. Si algún día hay enlaces de afiliado, irán marcados.</td></tr>
</table></td></tr></table></body></html>"""
(ROOT/"newsletter/001.html").write_text(doc)
print("ok", local(10))
