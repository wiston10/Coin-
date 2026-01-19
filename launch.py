#!/usr/bin/env python3
import sys
import webbrowser
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.gui.dashboard import app

def abrir_navegador():
    time.sleep(1.5)
    webbrowser.open('http://localhost:8080')

if __name__ == '__main__':
    import threading
    threading.Thread(target=abrir_navegador, daemon=True).start()
    app.run(host='0.0.0.0', port=8080, debug=False)
