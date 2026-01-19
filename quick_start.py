#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Importar sin cargar pandas pesado
from flask import Flask
app_instance = Flask(__name__)

@app_instance.route('/')
def index():
    return "<h1>Dashboard funcionando!</h1><p>Cargando módulos completos...</p>"

if __name__ == '__main__':
    print("Dashboard iniciando en http://localhost:8080")
    app_instance.run(host='0.0.0.0', port=8080)
