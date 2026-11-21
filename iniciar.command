#!/bin/bash
# Doble clic en Finder para iniciar el dashboard.
# La primera vez crea un entorno virtual (.venv) e instala las dependencias.
cd "$(dirname "$0")" || exit 1

pausa() { echo; read -r -p "Pulsa Enter para cerrar..." _; }

PY=""
for c in python3.13 python3.12 python3.11 python3.10 python3.9 python3; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(0 if sys.version_info >= (3,9) else 1)' 2>/dev/null; then
    PY="$c"; break
  fi
done
if [ -z "$PY" ]; then
  echo "❌ No encontré Python 3.9 o superior."
  echo "   Instálalo desde https://www.python.org/downloads/ y vuelve a intentarlo."
  pausa; exit 1
fi
echo "🐍 Usando $($PY --version)"

if [ ! -x ".venv/bin/python" ]; then
  echo "📦 Creando entorno virtual (.venv)..."
  "$PY" -m venv .venv || { echo "❌ No se pudo crear .venv"; pausa; exit 1; }
fi

if [ ! -f ".venv/.deps_ok" ] || [ requirements.txt -nt ".venv/.deps_ok" ]; then
  echo "📥 Instalando dependencias (solo la primera vez, puede tardar unos minutos)..."
  .venv/bin/python -m pip install --upgrade pip -q
  if .venv/bin/python -m pip install -r requirements.txt; then
    touch .venv/.deps_ok
  else
    echo "❌ Falló la instalación de dependencias. Revisa el mensaje de arriba."
    pausa; exit 1
  fi
fi

if [ ! -f ".env" ] && [ -f ".env.example" ]; then
  cp .env.example .env
  echo "📝 Creado .env (pon ahí tu token de Telegram si quieres alertas)."
fi

.venv/bin/python run_gui.py
echo
echo "El dashboard se ha cerrado."
pausa
