#!/usr/bin/env python3
"""
Script de inicio rápido para el Dashboard Web
"""

import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.gui.dashboard import app

if __name__ == '__main__':
    print("=" * 80)
    print("🚀 Sistema de Trading - Dashboard Web")
    print("=" * 80)
    print("\n📊 Dashboard Moderno:")
    print("  ✓ Interfaz web profesional")
    print("  ✓ Múltiples activos simultáneos")
    print("  ✓ Actualización en tiempo real")
    print("  ✓ Notificaciones webhook integradas")
    print("  ✓ Gráficos y análisis completo")
    print("\n🌐 Abriendo servidor web...")
    print("   URL: http://localhost:8080")
    print("   Presiona Ctrl+C para detener\n")
    print("=" * 80)
    
    try:
        app.run(host='0.0.0.0', port=8080, debug=False)
    except KeyboardInterrupt:
        print("\n\n👋 Dashboard detenido. ¡Hasta luego!\n")
        sys.exit(0)
