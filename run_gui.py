#!/usr/bin/env python3
"""
Inicia el Dashboard Web de trading.

    python3 run_gui.py              # inicia y abre el navegador
    python3 run_gui.py --no-browser # sin abrir el navegador
    python3 run_gui.py --port 9000  # puerto concreto
"""
import argparse
import importlib.util
import os
import socket
import sys
import threading
import time
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))

# (módulo a importar, paquete de pip)
REQUIRED = [
    ("flask", "flask"),
    ("flask_cors", "flask-cors"),
    ("pandas", "pandas"),
    ("numpy", "numpy"),
    ("requests", "requests"),
    ("yfinance", "yfinance"),
    ("ccxt", "ccxt"),
    ("bs4", "beautifulsoup4"),
    ("colorama", "colorama"),
]


def check_python():
    if sys.version_info < (3, 9):
        print(f"❌ Se necesita Python 3.9 o superior (tienes {sys.version.split()[0]}).")
        print("   Instálalo desde https://www.python.org/downloads/")
        sys.exit(1)


def check_dependencies():
    missing = [pkg for mod, pkg in REQUIRED if importlib.util.find_spec(mod) is None]
    if missing:
        print("❌ Faltan dependencias: " + ", ".join(missing))
        print("\n   Solución más fácil (Mac): doble clic en 'iniciar.command'")
        print("   O manualmente:")
        print("     python3 -m venv .venv && source .venv/bin/activate")
        print("     pip install -r requirements.txt")
        sys.exit(1)


def port_is_free(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind((host, port))
            return True
        except OSError:
            return False


def find_free_port(host, start):
    for port in range(start, start + 20):
        if port_is_free(host, port):
            return port
    print(f"❌ No hay puertos libres entre {start} y {start + 19}.")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Dashboard de trading")
    parser.add_argument("--port", type=int, default=None)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()

    check_python()
    check_dependencies()

    print("📦 Cargando módulos...", flush=True)
    from src.gui.dashboard import app, SERVER_HOST, SERVER_PORT

    wanted = args.port or SERVER_PORT
    port = find_free_port(SERVER_HOST, wanted)
    if port != wanted:
        print(f"⚠️  El puerto {wanted} está ocupado, uso el {port}.")

    url = f"http://localhost:{port}"
    print("=" * 60)
    print("🚀 Dashboard de Trading")
    print(f"   Abre: {url}")
    print("   Para detenerlo: Ctrl+C")
    print("=" * 60, flush=True)

    if not args.no_browser:
        threading.Thread(target=lambda: (time.sleep(1.5), webbrowser.open(url)), daemon=True).start()

    try:
        app.run(host=SERVER_HOST, port=port, debug=False, threaded=True, use_reloader=False)
    except KeyboardInterrupt:
        pass
    print("\n👋 Dashboard detenido.")


if __name__ == "__main__":
    main()
