"""Datos verificados a mano el 2026-10-19 desde las páginas oficiales de precios.
Regenera data/tools.json. Si un dato no aparece en la fuente oficial -> None / 'sin verificar'."""
import json, pathlib
D = "2026-10-19"
SV = "sin verificar"

def plan(name, price, billing, quote, es, models, src, **kw):
    p = dict(name=name, price_usd_month=price, billing_notes=billing, limits_quote=quote,
             limits_es=es, models=models, last_checked=D, source_url=src)
    p.update(kw); return p

T = []
src = "https://cursor.com/pricing"
T.append(dict(slug="cursor", name="Cursor", vendor="Anysphere (vendido vía X Subscription Corp.)", kind="IDE con agente",
  sources=[src], limit_type="Pool semanal compartido",
  summary="IDE basado en VS Code. Todos los planes comparten un pool de uso con Grok que se renueva cada semana; los modelos de terceros (Claude, GPT, etc.) se cobran aparte a precio de API desde Premium.",
  notes=["Precios sin impuestos (IVA no incluido).", "Las suscripciones solo se venden directamente vía X Subscription Corp.", "Plus incluye solo modelos Grok."],
  plans=[
    plan("Free",0,"Gratis","Limited agent requests · Limited Chat requests","Solicitudes de agente y chat limitadas (sin cifra publicada).","Limitado",src),
    plan("Plus",8,"Mensual, sin impuestos","Shared AI usage pool … *Only Grok models are available on this plan","Pool de uso compartido Cursor+Grok, se renueva semanalmente. Solo modelos Grok.","Solo Grok",src),
    plan("Premium",30,"Mensual, sin impuestos","4x more usage compared to Plus … Third-party models at API list price","4x el uso de Plus. Modelos de terceros disponibles pagando aparte a precio de lista de API.","Últimos Grok + terceros (pago aparte)",src),
    plan("Super",100,"Mensual, sin impuestos","15x more usage compared to Plus … Priority model access at peak times","15x el uso de Plus, prioridad en horas pico.","Grok + terceros (pago aparte)",src),
    plan("Ultra",200,"Mensual, sin impuestos","50x more usage compared to Plus","50x el uso de Plus, acceso anticipado.","Grok + terceros (pago aparte)",src),
    plan("Teams",30,"Desde $30 por usuario/mes ('$30+/user/month')","Usage: 4-50x Plus","Entre 4x y 50x Plus según tipo de asiento.","Grok + terceros (pago aparte)",src, per_seat=True, team=True),
  ]))

src = "https://claude.com/pricing"
T.append(dict(slug="claude-code", name="Claude Code", vendor="Anthropic", kind="Agente de terminal / IDE",
  sources=[src], limit_type="Ventana de 5 h + límite semanal",
  summary="Claude Code viene incluido en los planes pagos de Claude. Comparte un mismo pool con el chat de Claude: ventana móvil de 5 horas y límites semanales en planes pagos.",
  notes=["Precios sin impuestos.", "Claude Code y el chat comparten el mismo pool de uso.", "Al llegar al límite puedes activar 'usage credits' a tarifa de API."],
  plans=[
    plan("Free",0,"Gratis","Claude Code: No","No incluye Claude Code.","Sonnet, Haiku",src, no_coding=True),
    plan("Pro",20,"$20 mensual o $17/mes en plan anual ($200 por adelantado)","Pro gives you at least 5x more usage per 5-hour session than Free … paid plans add weekly limits","Al menos 5x el uso de Free por sesión de 5 h, más límite semanal.","Opus, Sonnet, Haiku (Fable con usage credits)",src),
    plan("Max 5x",100,"Mensual. La página dice 'From $100'","Max gives you 5x or 20x more usage per 5-hour session than Pro","5x el uso de Pro por sesión de 5 h. Incluye $100/mes en créditos de API. Fable: 50% de los límites semanales.","Fable, Opus, Sonnet, Haiku",src),
    plan("Max 20x",None,"Mensual. Precio exacto no visible en la página oficial (sin verificar)","Max gives you 5x or 20x more usage per 5-hour session than Pro","20x el uso de Pro por sesión de 5 h. Incluye $200/mes en créditos de API.","Fable, Opus, Sonnet, Haiku",src),
  ]))

src = "https://developers.openai.com/codex/pricing/"
T.append(dict(slug="codex", name="OpenAI Codex", vendor="OpenAI (planes de ChatGPT)", kind="Agente (app, CLI, IDE, nube)",
  sources=[src], limit_type="Ventana de 5 h (+ semanal posible)",
  summary="Codex va incluido en los planes de ChatGPT y comparte uso con ChatGPT Work. Plus tiene estimaciones de mensajes por cada 5 horas; los planes Pro hoy no tienen límite de 5 horas.",
  notes=["Las cifras de mensajes son estimaciones, no límites fijos.", "GPT-5.5 se retiró de Codex con inicio de sesión de ChatGPT el 14-oct-2026.", "También puedes usar Codex con API key pagando tarifas de API."],
  plans=[
    plan("Free",0,"Gratis","GPT-6 Luna at Standard speed in the desktop app, subject to rollout","Tareas rápidas con GPT-6 Luna en la app de escritorio (según despliegue).","GPT-6 Luna",src),
    plan("Go",8,"Mensual","Use Codex for lightweight coding tasks","Tareas ligeras. Límites numéricos sin verificar.","GPT-6 Luna",src),
    plan("Plus",20,"Mensual","Local messages per 5h (estimates): GPT-6.1 Sol 15-160 · GPT-6 Astra 5-45 · GPT-6 Luna 350-3,000. Weekly limits may also apply.","Estimación por 5 h: 15–160 mensajes con GPT-6.1 Sol, 5–45 con GPT-6 Astra, 350–3.000 con GPT-6 Luna. Puede haber límite semanal.","GPT-6.1 Sol, GPT-6 Luna",src),
    plan("Pro $100",100,"Mensual","Pro plans currently have no five-hour limit","Sin límite de 5 horas (por ahora). Más uso que Plus; cifra exacta sin verificar.","GPT-6.1 Sol, GPT-6 Sol, GPT-6 Luna",src),
    plan("Pro $200",200,"Mensual","Pro plans currently have no five-hour limit","Sin límite de 5 horas (por ahora). Cifra exacta sin verificar.","GPT-6.1 Sol, GPT-6 Sol, GPT-6 Luna",src),
    plan("Pro $500",500,"Mensual","Ultrafast mode access on Pro $500","Sin límite de 5 horas; incluye modo Ultrafast.","GPT-6 Astra, GPT-6.1 Sol, Luna",src),
    plan("Business",25,"$25 por usuario/mes facturado mensual (2+ usuarios); precio anual menor, no visible","Local messages per 5h same estimates as Plus (Standard Business)","Mismas estimaciones por 5 h que Plus.","GPT-6.1 Sol, GPT-6 Luna",src, per_seat=True, team=True),
  ]))

src = "https://github.com/features/copilot/plans"
T.append(dict(slug="github-copilot", name="GitHub Copilot", vendor="GitHub (Microsoft)", kind="Extensión multi-IDE + CLI + agente",
  sources=[src], limit_type="Créditos mensuales (AI Credits)",
  summary="Copilot cobra el chat, modo agente, CLI y code review con GitHub AI Credits (1 crédito = US$0,01). El autocompletado es ilimitado en planes pagos. El saldo se renueva cada mes.",
  notes=["1 AI credit = $0.01 USD.", "Autocompletado y next edit suggestions no consumen créditos en planes pagos.", "Desde el 1-jun-2026 el code review también consume minutos de GitHub Actions."],
  plans=[
    plan("Free",0,"Gratis","Copilot Free users are limited to 2000 completions and 50 chat requests","2.000 autocompletados y 50 solicitudes de chat al mes.","Lista amplia (Claude, GPT, Gemini, Grok, Kimi)",src),
    plan("Pro",10,"Mensual","Total GitHub AI Credits: $15 per month ($10 base + $5 flex)","US$15/mes en créditos (10 base + 5 flex). Autocompletado ilimitado.","Claude, GPT, Gemini, Grok, Kimi, MAI",src, included_usd=15),
    plan("Pro+",39,"Mensual","Total GitHub AI Credits: $70 per month ($39 base + $31 flex)","US$70/mes en créditos (39 base + 31 flex).","Claude, GPT, Gemini, Grok, Kimi, MAI",src, included_usd=70),
    plan("Max",100,"Mensual","Total GitHub AI Credits: $200 per month · Base credits $100","US$200/mes en créditos totales (US$100 base).","Claude, GPT, Gemini, Grok, Kimi, MAI",src, included_usd=200),
  ]))

src = "https://devin.ai/pricing"
T.append(dict(slug="windsurf", name="Windsurf (Devin Desktop)", vendor="Cognition", kind="IDE con agente",
  sources=[src, "https://docs.devin.ai/desktop/devin-desktop-faq"], limit_type="Cuota diaria + semanal",
  summary="Windsurf pasó a llamarse Devin Desktop el 2-jun-2026. Usa cuotas que se renuevan cada día y cada semana; el uso extra se paga a precio de API.",
  notes=["La página de Windsurf ahora vive en devin.ai/pricing.", "Uso extra a precio de API.", "La promo de SWE-2 gratis terminó el 16-oct-2026."],
  plans=[
    plan("Free",0,"Gratis","Light quota to code with agents · Limited model availability · Unlimited inline edits · Unlimited Tab completions","Cuota ligera para agentes, modelos limitados, Tab ilimitado.","Limitado",src),
    plan("Pro",20,"Mensual","Increased quotas, including access to frontier models from OpenAI, Claude, Gemini, and SpaceXAI","Cuotas mayores (diaria y semanal), todos los modelos. Cifra exacta no publicada.","OpenAI, Claude, Gemini, SpaceXAI, open source, SWE-2",src),
    plan("Max",200,"Mensual","Everything in Pro, plus: Significantly higher quotas","Cuotas 'significativamente mayores' (sin cifra publicada).","Todos",src),
    plan("Teams",80,"US$80/mes por el plan + US$40/mes por asiento completo","Each full user includes their own generous quota","Cada usuario completo tiene su propia cuota.","Todos",src, team=True),
  ]))

src = "https://kiro.dev/pricing/"
T.append(dict(slug="kiro", name="Kiro", vendor="AWS", kind="IDE + CLI con specs",
  sources=[src], limit_type="Créditos mensuales",
  summary="Kiro usa créditos mensuales que no se acumulan. Créditos extra a US$0,04. Paga una vez al mes, el día 1.",
  notes=["Precios sin impuestos.", "Bono de US$20 al primer upgrade (social login o AWS Builder ID).", "Créditos del plan no se acumulan al mes siguiente."],
  plans=[
    plan("Free",0,"Gratis","50 credits · Access to open weight models and Claude Sonnet 4.5","50 créditos; modelos abiertos y Claude Sonnet 4.5 con límites.","Claude Sonnet 4.5, Qwen3 Coder Next, DeepSeek 3.2, MiniMax",src),
    plan("Pro",20,"Por usuario/mes","1,000 credits · Add-on credits ($0.04/credit)","1.000 créditos/mes.","Auto, Claude Sonnet 5, Opus 5, GPT-5.6, abiertos",src),
    plan("Pro+",40,"Por usuario/mes","2,000 credits","2.000 créditos/mes.","Auto, Claude, GPT-5.6, abiertos",src),
    plan("Pro Max",100,"Por usuario/mes","5,000 credits","5.000 créditos/mes.","Auto, Claude, GPT-5.6, abiertos",src),
    plan("Power",200,"Por usuario/mes","10,000 credits","10.000 créditos/mes.","Auto, Claude, GPT-5.6, abiertos",src),
  ]))

src = "https://zed.dev/pricing"
T.append(dict(slug="zed", name="Zed", vendor="Zed Industries", kind="Editor (BYOK o hospedado)",
  sources=[src], limit_type="Tokens incluidos + pago por uso",
  summary="Editor open source muy rápido. Gratis con tus propias API keys o agentes externos; Pro incluye US$5 en tokens y luego cobra precio de API +10%.",
  notes=["Prueba de 14 días de Pro con US$5 de GPT-6 Luna, sin tarjeta.", "Uso extra: precio de lista de API +10%."],
  plans=[
    plan("Personal",0,"Gratis","Unlimited use with your API keys or external agents like Claude Agent, Codex CLI, and more","Ilimitado con tus propias keys o agentes externos.","BYOK",src),
    plan("Pro",10,"Mensual","Unlimited edit predictions · $5 of tokens included · Usage-based billing beyond $5","US$5 en tokens incluidos; después, precio de API +10%.","Modelos hospedados por Zed",src, included_usd=5),
    plan("Business",30,"Por asiento/mes","Business seats don't bundle a fixed LLM credit allotment","Sin créditos incluidos; controles de organización.","Hospedados o BYOK",src, per_seat=True, team=True),
  ]))

src = "https://codeassist.google/"
q = "https://developers.google.com/gemini-code-assist/resources/quotas"
T.append(dict(slug="gemini-code-assist", name="Gemini Code Assist / CLI", vendor="Google", kind="Extensión IDE + CLI",
  sources=[src, q], limit_type="Solicitudes por día",
  summary="Licencias por usuario para empresas. El modo agente y Gemini CLI comparten una cuota diaria de solicitudes. El nivel gratuito para individuos fue reemplazado por Antigravity el 18-jun-2026.",
  notes=["Nivel gratis individual: reemplazado por Antigravity CLI y Antigravity el 18-jun-2026.", "Una sola instrucción en modo agente puede generar varias solicitudes."],
  plans=[
    plan("Standard",22.8,"US$22,80 por usuario/mes (US$19 con compromiso anual)","Maximum requests per user per day (agent mode + Gemini CLI): Standard 1500","1.500 solicitudes por usuario por día (agente + CLI).","Gemini 3",q, per_seat=True),
    plan("Enterprise",54,"US$54 por usuario/mes (US$45 con compromiso anual)","Maximum requests per user per day: Enterprise 2000","2.000 solicitudes por usuario por día (agente + CLI).","Gemini 3",q, per_seat=True, team=True),
  ]))

src = "https://lovable.dev/pricing"
T.append(dict(slug="lovable", name="Lovable", vendor="Lovable", kind="Constructor de apps (vibe coding)",
  sources=[src], limit_type="Créditos mensuales + diarios",
  summary="Construye apps web chateando. Los planes incluyen créditos mensuales compartidos por todo el workspace (usuarios ilimitados) más 5 créditos diarios.",
  notes=["Plan anual: '2 months free'.", "Descuento para estudiantes de hasta 50% en Pro.", "Créditos mensuales se acumulan 1 mes."],
  affiliate_todo=True,
  plans=[
    plan("Free",0,"Gratis","daily grant of 5 build credits (up to 30 a month), plus monthly grants of 20 Cloud credits","5 créditos diarios (máx. 30/mes) + 20 créditos Cloud.","Sin verificar",src),
    plan("Pro",25,"Mensual (2 meses gratis en anual)","100 monthly credits · Credit rollovers","100 créditos/mes + 5 diarios; acumulación 1 mes.","Sin verificar",src),
    plan("Business",50,"Mensual","100 monthly credits · SSO · Team workspace","100 créditos/mes (Business), SSO y controles.","Sin verificar",src, team=True),
  ]))

src = "https://bolt.new/pricing"
T.append(dict(slug="bolt", name="Bolt", vendor="StackBlitz", kind="Constructor de apps (vibe coding)",
  sources=[src], limit_type="Tokens mensuales",
  summary="Constructor de apps en el navegador. Mide el uso en tokens; los proyectos grandes gastan más tokens por mensaje.",
  notes=["Tokens de planes pagos se acumulan 1 mes extra (desde 1-jul-2025)."],
  affiliate_todo=True,
  plans=[
    plan("Free",0,"Gratis","300K tokens daily limit · 1M tokens per month","300 mil tokens por día, 1 millón al mes.","Sin verificar",src),
    plan("Pro",25,"Mensual","No daily token limit · Start at 10M tokens per month · Unused tokens roll over","Desde 10 millones de tokens/mes, sin límite diario.","Sin verificar",src),
    plan("Teams",30,"Por miembro/mes","Each paid team member receives a monthly token allotment","Cada miembro tiene su propia asignación de tokens.","Sin verificar",src, per_seat=True, team=True),
  ]))

src = "https://replit.com/pricing"
T.append(dict(slug="replit", name="Replit", vendor="Replit", kind="Agente + IDE en la nube",
  sources=[src], limit_type="Crédito mensual en USD",
  summary="IDE en la nube con Replit Agent. Los planes incluyen horas de 'Free Mode' y un saldo en dólares para modelos más potentes.",
  notes=["Precios sujetos a impuestos según ubicación.", "Plan gratuito: sin verificar en la página."],
  plans=[
    plan("Core",20,"$20 mensual o $18/mes facturado anual","Up to 30 hours of chat on Free Mode · $20 towards more powerful models","Hasta 30 h de chat en Free Mode + US$20 para modelos potentes.","Sin verificar",src, included_usd=20),
    plan("Pro",100,"$100 mensual o $90/mes facturado anual","Even more Free Mode usage · $100 towards most powerful models · 10 parallel agents","Más Free Mode + US$100 para los modelos más potentes, 10 agentes en paralelo.","Sin verificar",src, included_usd=100),
  ]))

out = dict(updated=D, currency_base="USD",
  disclaimer="Precios oficiales en USD sin impuestos salvo que se indique. Las conversiones a moneda local son referenciales: impuestos locales (IVA, percepciones), comisiones bancarias y precios de App Store/Google Play pueden variar.",
  tools=T)
p = pathlib.Path(__file__).resolve().parents[1] / "data" / "tools.json"
p.write_text(json.dumps(out, ensure_ascii=False, indent=2))
print(len(T), "tools", sum(len(t["plans"]) for t in T), "plans")
