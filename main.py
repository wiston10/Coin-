#!/usr/bin/env python3
"""
Punto de entrada principal del Sistema de Trading
"""

import sys
from pathlib import Path

# Agregar src al path de Python
sys.path.insert(0, str(Path(__file__).parent / "src"))


def main():
    """Punto de entrada principal de la aplicación"""
    print("\n" + "=" * 80)
    print("🎯 SISTEMA DE ANÁLISIS DE TRADING")
    print("=" * 80)
    print("\n¿Qué deseas hacer?\n")
    print("1. 🌐 Dashboard Web (Recomendado)")
    print("   └─ Interfaz web moderna")
    print("   └─ Múltiples activos en tiempo real")
    print("   └─ Actualización automática")
    print()
    print("2. 💻 Interfaz de Terminal")
    print("   └─ Menú interactivo")
    print("   └─ Análisis detallado")
    print()
    print("3. 📚 Ver ejemplos disponibles")
    print()
    print("4. ❌ Salir")
    print()
    
    choice = input("Selecciona una opción (1-4): ").strip()
    
    if choice == "1":
        from src.gui.dashboard import app
        print("\n🌐 Iniciando Dashboard Web...")
        print("   URL: http://localhost:8080")
        print("   Presiona Ctrl+C para detener\n")
        app.run(host='0.0.0.0', port=8080, debug=False)
    elif choice == "2":
        from src.core.trading_app import main as app_main
        print("\n⚡ Iniciando interfaz de terminal...\n")
        app_main()
    elif choice == "3":
        print("\n📚 Ejemplos disponibles en la carpeta 'examples/':")
        print("  • quick_start.py - Guía rápida de inicio")
        print("  • ejemplo_rebotes.py - Estrategia de rebotes")
        print("  • ejemplos_avanzados.py - Ejemplos avanzados")
        print("  • ejemplos_binomo.py - Integración con Binomo")
        print("  • ejemplos_hibridos.py - Datos híbridos")
        print("  • ejemplos_live.py - Trading en vivo")
        print("  • ejemplos_webhooks.py - Notificaciones webhook")
        print("\nEjecútalos con: python3 examples/nombre_ejemplo.py")
    elif choice == "4":
        print("\n👋 ¡Hasta luego!\n")
        sys.exit(0)
    else:
        print("\n❌ Opción inválida. Intenta de nuevo.\n")
        main()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Programa interrumpido por el usuario. ¡Hasta luego!\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        sys.exit(1)
