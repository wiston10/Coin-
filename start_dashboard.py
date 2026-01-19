#!/usr/bin/env python3
"""
Script de inicio con logging a archivo
"""

import sys
from pathlib import Path
from datetime import datetime

# Configurar logging a archivo
log_file = Path(__file__).parent / "dashboard.log"
sys.stdout = open(log_file, 'w', buffering=1)
sys.stderr = sys.stdout

print(f"=== Dashboard Log - {datetime.now()} ===")
print("Iniciando...")

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("Importando módulos...")
try:
    from src.gui.dashboard import app
    print("✅ App importada")
    
    print("\nIniciando servidor en http://localhost:8080")
    print("Log guardado en: dashboard.log")
    app.run(host='0.0.0.0', port=8080, debug=False)
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
