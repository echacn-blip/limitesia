#!/usr/bin/env python3
"""LímitesIA – refresco diario.
1) Vuelve a descargar cada página oficial listada en data/tools.json.
2) Extrae el texto visible, calcula un hash y lo compara con data/snapshots/.
3) Si cambió, agrega una entrada a data/changes.json (con montos $ agregados/quitados).
4) Descarga tipos de cambio USD -> MXN, COP, ARS, CLP, PEN, EUR (open.er-api.com, sin API key;
   respaldo: frankfurter.app, que no cubre todas las monedas).
Uso: python3 scripts/refresh.py [--no-fx] [--no-pages]
No modifica precios en tools.json: un humano revisa el cambio y actualiza el dato (nunca inventar)."""
import hashlib, html, json, re, subprocess, sys, shutil, datetime, difflib, pathlib
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data"; SNAP = DATA / "snapshots"; SNAP.mkdir(parents=True, exist_ok=True)
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36 LimitesIA-bot (+contacto: TODO)"
CURRENCIES = ["MXN", "COP", "ARS", "CLP", "PEN", "EUR"]
# Páginas que cargan precios con JavaScript: se renderizan con Chrome headless si está disponible.
JS_RENDER = {"https://lovable.dev/pricing"}
NOW = datetime.datetime.now(datetime.timezone.utc)

def get(url, timeout=40):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", errors="ignore")
    except Exception:
        # algunos sitios rechazan urllib; reintento con curl si existe
        if not shutil.which("curl"): raise
        out = subprocess.run(["curl", "-sSL", "--fail", "-A", UA.split(" LimitesIA")[0], "--max-time", str(timeout), url],
                             capture_output=True, text=True)
        if out.returncode != 0: raise RuntimeError(out.stderr.strip() or "curl failed")
        return out.stdout

def render(url):
    chrome = shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("chromium-browser")
    if not chrome:
        return get(url)
    out = subprocess.run([chrome, "--headless=new", "--no-sandbox", "--disable-gpu",
                          "--virtual-time-budget=15000", "--dump-dom", url],
                         capture_output=True, text=True, timeout=90)
    return out.stdout or get(url)

def visible_text(raw):
    t = re.sub(r"(?is)<(script|style|noscript|svg)[^>]*>.*?</\1>", " ", raw)
    t = re.sub(r"(?s)<[^>]+>", "\n", t)
    t = html.unescape(t)
    lines = [re.sub(r"\s+", " ", l).strip() for l in t.split("\n")]
    # quita líneas vacías y ruido típico (fechas de build, contadores)
    return "\n".join(l for l in lines if l and len(l) > 1)

MONEY = re.compile(r"\$\s?\d[\d,]*(?:\.\d+)?")

def load(name, default):
    p = DATA / name
    return json.loads(p.read_text()) if p.exists() else default

def save(name, obj):
    (DATA / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2))

def refresh_pages(tools):
    changes = load("changes.json", [])
    n_changed = 0
    for tool in tools["tools"]:
        for url in tool["sources"]:
            key = hashlib.sha1(url.encode()).hexdigest()[:12]
            snap_p = SNAP / f"{tool['slug']}-{key}.json"
            try:
                raw = render(url) if url in JS_RENDER else get(url)
            except Exception as e:
                print(f"[error] {url}: {e}"); continue
            text = visible_text(raw)
            h = hashlib.sha256(text.encode()).hexdigest()
            old = json.loads(snap_p.read_text()) if snap_p.exists() else None
            snap = dict(url=url, tool=tool["slug"], hash=h, fetched=NOW.isoformat(timespec="seconds"), text=text)
            if old is None:
                print(f"[base] {tool['slug']} {url}")
            elif old["hash"] != h:
                old_lines, new_lines = old["text"].splitlines(), text.splitlines()
                diff = [l for l in difflib.unified_diff(old_lines, new_lines, lineterm="", n=0)
                        if l[:1] in "+-" and not l.startswith(("+++", "---"))]
                added = sorted(set(MONEY.findall(text)) - set(MONEY.findall(old["text"])))
                removed = sorted(set(MONEY.findall(old["text"])) - set(MONEY.findall(text)))
                kind = "precio" if (added or removed) else "texto"
                changes.append(dict(
                    date=NOW.date().isoformat(), tool=tool["slug"], tool_name=tool["name"], url=url,
                    type="detectado", kind=kind, reviewed=False,
                    title=f"Cambió la página de precios de {tool['name']}" + (" (montos)" if kind == "precio" else ""),
                    detail="Cambio detectado automáticamente; pendiente de revisión humana antes de actualizar la tabla.",
                    money_added=added, money_removed=removed, diff_sample=diff[:40],
                    old_hash=old["hash"], new_hash=h))
                n_changed += 1
                print(f"[CAMBIO] {tool['slug']} {url} +{added} -{removed}")
            else:
                print(f"[igual] {tool['slug']}")
            snap_p.write_text(json.dumps(snap, ensure_ascii=False, indent=1))
    save("changes.json", changes)
    return n_changed

def refresh_fx():
    try:
        d = json.loads(get("https://open.er-api.com/v6/latest/USD"))
        if d.get("result") != "success": raise ValueError(d.get("error-type"))
        rates = {c: d["rates"][c] for c in CURRENCIES if c in d["rates"]}
        fx = dict(base="USD", rates=rates, source="https://open.er-api.com (ExchangeRate-API, datos abiertos)",
                  provider_updated=d.get("time_last_update_utc"), fetched=NOW.isoformat(timespec="seconds"))
    except Exception as e:
        print("[fx] open.er-api falló:", e, "-> probando frankfurter")
        d = json.loads(get("https://api.frankfurter.app/latest?from=USD&to=" + ",".join(CURRENCIES)))
        old = load("fx.json", {}).get("rates", {})
        rates = {**old, **d["rates"]}
        fx = dict(base="USD", rates=rates, source="https://frankfurter.app (BCE) + valores previos para monedas no cubiertas",
                  provider_updated=d.get("date"), fetched=NOW.isoformat(timespec="seconds"))
    save("fx.json", fx)
    print("[fx]", fx["rates"])

if __name__ == "__main__":
    tools = load("tools.json", None)
    if "--no-fx" not in sys.argv: refresh_fx()
    if "--no-pages" not in sys.argv:
        n = refresh_pages(tools)
        print(f"Listo. Cambios detectados: {n}")
