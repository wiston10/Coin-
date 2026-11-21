#!/usr/bin/env python3
import sys
import webbrowser
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.gui.dashboard import app, SERVER_HOST, SERVER_PORT

def abrir_navegador():
    time.sleep(1.5)
    webbrowser.open(f'http://localhost:{SERVER_PORT}')

if __name__ == '__main__':
    import threading
    threading.Thread(target=abrir_navegador, daemon=True).start()
    app.run(host=SERVER_HOST, port=SERVER_PORT, debug=False, threaded=True)
