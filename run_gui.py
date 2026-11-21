#!/usr/bin/env python3
"""
Script de inicio rápido para el Dashboard Web con Multi-Broker
"""

import sys
from pathlib import Path

print("🔧 Iniciando run_gui.py...", flush=True)

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("📦 Importando módulos...", flush=True)
try:
    from src.gui.dashboard import app, SERVER_HOST, SERVER_PORT
    from src.data_sources.hybrid_data_source import HybridDataSource
    print("✅ Módulos importados correctamente", flush=True)
except Exception as e:
    print(f"❌ Error al importar módulos: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)

def show_multibroker_status():
    """Muestra el estado del sistema multi-broker"""
    try:
        print("\n📡 SISTEMA MULTI-BROKER")
        print("-" * 80)
        
        # Inicializar sistema
        ds = HybridDataSource()
        
        # Mostrar fuentes habilitadas
        try:
            from config.broker_apis import get_enabled_sources
            enabled = get_enabled_sources()
            print(f"✅ Fuentes habilitadas: {', '.join(enabled)}")
        except:
            print("✅ Fuentes habilitadas: yfinance, exchanges")
        
        # Probar algunos activos rápidamente
        test_assets = [
            ('AAPL', 'Stock'),
            ('BTC-USD', 'Crypto'),
            ('EUR-USD', 'Forex')
        ]
        
        print(f"\n📊 Probando calidad de datos:")
        print("-" * 80)
        
        for symbol, asset_type in test_assets:
            try:
                result = ds.get_aggregated_price(symbol)
                quality_emoji = {
                    'Excellent': '⭐',
                    'Good': '✅',
                    'Fair': '⚠️',
                    'Poor': '❌'
                }.get(result['quality'], '❓')
                
                print(f"{quality_emoji} {symbol:12} | ${result['price']:>12,.2f} | "
                      f"{result['quality']:10} ({result['confidence']:>5.1%}) | "
                      f"{result['sources_used']} fuentes")
            except Exception as e:
                print(f"❌ {symbol:12} | Error: {str(e)[:40]}")
        
        # Mostrar recomendación si hay baja calidad
        print("\n💡 RECOMENDACIONES:")
        print("-" * 80)
        
        try:
            # Verificar si hay API keys configuradas
            from config.broker_apis import (
                ALPHA_VANTAGE_API_KEY, 
                FINNHUB_API_KEY,
                TWELVE_DATA_API_KEY
            )
            
            has_alpha = ALPHA_VANTAGE_API_KEY and ALPHA_VANTAGE_API_KEY != "demo"
            has_finnhub = FINNHUB_API_KEY and FINNHUB_API_KEY != "demo"
            has_twelve = TWELVE_DATA_API_KEY and TWELVE_DATA_API_KEY != "demo"
            
            if not any([has_alpha, has_finnhub, has_twelve]):
                print("⚠️  ATENCIÓN: Solo usando fuentes gratuitas")
                print("   • Stocks/Forex/Indices tienen baja precisión (Poor)")
                print("   • Para mejorar, agrega API keys en config/broker_apis.py")
                print("\n   APIs gratuitas recomendadas:")
                print("   1. Alpha Vantage: https://www.alphavantage.co/support/#api-key")
                print("   2. Finnhub: https://finnhub.io/register")
                print("\n   Ver: MULTI_BROKER_SETUP.md para instrucciones completas")
            else:
                apis_active = []
                if has_alpha: apis_active.append("Alpha Vantage")
                if has_finnhub: apis_active.append("Finnhub")
                if has_twelve: apis_active.append("Twelve Data")
                print(f"✅ APIs activas: {', '.join(apis_active)}")
                print("   • Mayor precisión disponible para Stocks/Forex/Indices")
        except ImportError:
            print("⚠️  ATENCIÓN: Solo usando fuentes gratuitas (yfinance + exchanges)")
            print("   • Para stocks/forex/indices, considera agregar API keys")
            print("   • Ver: MULTI_BROKER_SETUP.md")
        
        # Estadísticas
        try:
            from src.data_sources.multi_broker_client import multi_broker
            stats = multi_broker.get_statistics()
            if stats['total_requests'] > 0:
                print(f"\n📈 Estadísticas de uso:")
                print(f"   • Total requests: {stats['total_requests']}")
                print(f"   • Cache hits: {stats['cache_hits']} "
                      f"({stats['cache_hits']/stats['total_requests']*100:.1f}%)")
        except:
            pass
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"\n⚠️  No se pudo verificar el sistema multi-broker: {e}")
        print("=" * 80)

if __name__ == '__main__':
    print("=" * 80)
    print("🚀 Sistema de Trading - Dashboard Web con Multi-Broker v2.0")
    print("=" * 80)
    
    # Mostrar estado del sistema multi-broker
    show_multibroker_status()
    
    print("\n📊 Dashboard Web:")
    print("  ✓ Interfaz web profesional")
    print("  ✓ Múltiples activos simultáneos")
    print("  ✓ Actualización en tiempo real")
    print("  ✓ Sistema multi-broker integrado (14 fuentes)")
    print("  ✓ Calidad de datos por activo")
    print("  ✓ Notificaciones webhook integradas")
    print("  ✓ Gráficos y análisis completo")
    
    print("\n🌐 Iniciando servidor web...")
    print(f"   URL: http://localhost:{SERVER_PORT}")
    print("   Presiona Ctrl+C para detener")
    
    print("\n📡 Endpoints multi-broker disponibles:")
    print("   • GET /api/price-quality/<symbol>  - Precio con calidad")
    print("   • GET /api/broker-stats            - Estadísticas de uso")
    print("   • GET /api/analyze/<symbol>        - Análisis completo con calidad")
    print("   • GET /api/analyze-all             - Todos los activos")
    
    print("\n" + "=" * 80 + "\n")
    
    try:
        app.run(host=SERVER_HOST, port=SERVER_PORT, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\n\n👋 Dashboard detenido. ¡Hasta luego!\n")
        sys.exit(0)
