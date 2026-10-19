# LímitesIA (v1, local)

Sitio estático en español: precios y límites de herramientas de IA para programar, en moneda local.

## Comandos
```bash
cd /workspace/limitesia
./run.sh                      # refresca páginas oficiales + tipo de cambio y regenera site/
python3 scripts/refresh.py    # solo refrescar (--no-fx / --no-pages)
python3 scripts/build.py      # solo regenerar HTML (SITE_URL=https://dominio para URLs canónicas/sitemap)
python3 scripts/seed_data.py  # re-escribe data/tools.json con los datos verificados a mano
cd site && python3 -m http.server 8765   # ver en http://localhost:8765
```

## Flujo de datos
- `data/tools.json`: planes verificados a mano (fuente + fecha). `null` / "sin verificar" si la fuente oficial no lo dice.
- `scripts/refresh.py`: descarga cada fuente, guarda el texto en `data/snapshots/`, compara el hash y agrega a `data/changes.json`
  los cambios detectados (con montos $ nuevos/eliminados), marcados `reviewed:false`. **No toca precios**: un humano revisa y edita `seed_data.py`/`tools.json`.
- `data/fx.json`: USD→MXN, COP, ARS, CLP, PEN, EUR desde open.er-api.com (respaldo: frankfurter.app).
- `scripts/build.py`: genera `site/` (solo librería estándar de Python).

## TODOs antes de publicar
- Dominio real (`SITE_URL`), servicio de newsletter, backend de formularios (newsletter, reporta, anúnciate), contacto, enlaces de afiliado.
- Lovable se renderiza con Chrome headless; en CI hace falta Chrome o se baja sin JS (el hash cambiará).

## v2: rediseño + newsletter (19 oct 2026)

**config.json** (o variables de entorno con el mismo nombre):
- `SITE_URL`: URL pública, p. ej. `https://USUARIO.github.io/limitesia` (canónicas, sitemap, OG, enlaces del newsletter).
- `BASE_PATH`: `/limitesia/` para un sitio de proyecto en GitHub Pages. Solo lo usa 404.html; todo lo demás va con enlaces relativos.
- `NEWSLETTER_USERNAME`: usuario de Buttondown. **Vacío = modo demo**: los formularios no envían nada y te llevan a /gracias/?demo=1.

**Activar Buttondown:**
1. Crea la cuenta.
2. Pon tu usuario en `NEWSLETTER_USERNAME`.
3. Corre `python3 scripts/build.py`.
4. En Buttondown, configura `subscription_redirect_url` = SITE_URL/gracias/ y `subscription_confirmation_redirect_url` = SITE_URL/confirmado/.
5. Deja activado el doble opt-in.

Los formularios hacen un POST HTML nativo a `https://buttondown.com/api/emails/embed-subscribe/<usuario>` con `email`, `embed=1` y un `tag` según la página (docs.buttondown.com/tags). No usan JS ni scripts de terceros.

**Páginas nuevas:** /suscribete/, /gracias/, /confirmado/, /newsletter/001.html (vista previa) y 404.html.
**Newsletter:** `python3 scripts/newsletter.py` regenera newsletter/001.md y 001.html a partir de data/fx.json y config.json.
**Monetización:** newsletter/monetizacion.md.
