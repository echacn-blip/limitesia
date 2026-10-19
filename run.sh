#!/usr/bin/env bash
# Refresca datos (páginas oficiales + tipo de cambio) y regenera el sitio.
set -euo pipefail
cd "$(dirname "$0")"
python3 scripts/refresh.py "$@"
python3 scripts/build.py
