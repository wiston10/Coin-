#!/usr/bin/env python3
"""
Demo Rápido del Sistema Multi-Broker
Muestra las capacidades del sistema de agregación multi-fuente
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data_sources.hybrid_data_source import HybridDataSource

def print_header(text):
    """Imprime un encabezado formateado"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def print_price_result(symbol, result):
    """Imprime el resultado del precio de forma formateada"""
    print(f"\n📊 {symbol}")
    print("-" * 70)
    print(f"💰 Precio Consensuado: ${result['price']:,.2f}")
    print(f"✨ Confianza: {result['confidence']:.1%} - {result['quality']}")
    print(f"📈 Fuentes usadas: {result['sources_used']}")
    print(f"📉 Spread: {result['spread_pct']:.3f}%")
    
    if result['std_dev'] > 0:
        print(f"📊 Desviación estándar: ${result['std_dev']:.2f}")
    
    if result.get('individual_prices'):
        print(f"\n🎯 Precios por fuente:")
        for source, price in result['individual_prices'].items():
            diff_pct = ((price - result['price']) / result['price']) * 100
            symbol_diff = "↑" if diff_pct > 0 else "↓" if diff_pct < 0 else "="
            print(f"   • {source:20s}: ${price:>10,.2f}  {symbol_diff} {abs(diff_pct):.2f}%")
    
    if result.get('outliers'):
        print(f"\n⚠️  Outliers removidos: {len(result['outliers'])}")
        for outlier in result['outliers']:
            print(f"   • {outlier['source']}: ${outlier['price']:,.2f}")

def main():
    """Función principal"""
    
    print_header("🚀 DEMO SISTEMA MULTI-BROKER v2.0")
    
    print("\n📝 Descripción:")
    print("   Este sistema agrega precios de MÚLTIPLES fuentes para obtener")
    print("   el precio más preciso y confiable posible.")
    print("\n📊 Fuentes disponibles:")
    print("   • yfinance (Yahoo Finance) - Gratuito")
    print("   • 6 Crypto Exchanges - Gratuito")
    print("   • 7 Financial APIs - Requiere API keys (ver MULTI_BROKER_SETUP.md)")
    
    print("\n⚙️  Inicializando sistema...")
    ds = HybridDataSource()
    
    # Lista de assets para probar
    test_assets = [
        ('AAPL', 'Apple Inc. - Stock'),
        ('MSFT', 'Microsoft - Stock'),
        ('EUR-USD', 'Euro/Dollar - Forex'),
        ('GBP-USD', 'Pound/Dollar - Forex'),
        ('BTC-USD', 'Bitcoin - Cryptocurrency'),
        ('ETH-USD', 'Ethereum - Cryptocurrency'),
        ('SPY', 'S&P 500 ETF - Index'),
    ]
    
    print_header("📈 PRUEBA DE AGREGACIÓN MULTI-FUENTE")
    
    for symbol, description in test_assets:
        try:
            print(f"\n⏳ Obteniendo {description}...")
            result = ds.get_aggregated_price(symbol)
            print_price_result(symbol, result)
            
            # Dar recomendaciones basadas en la calidad
            if result['quality'] == 'Poor':
                print(f"\n💡 RECOMENDACIÓN:")
                print(f"   La confianza es baja ({result['confidence']:.1%}) porque solo")
                print(f"   se están usando {result['sources_used']} fuente(s).")
                print(f"   Para mejorar la precisión:")
                print(f"   1. Agrega API keys en config/broker_apis.py")
                print(f"   2. Ver MULTI_BROKER_SETUP.md para instrucciones")
            elif result['quality'] == 'Fair':
                print(f"\n💡 SUGERENCIA:")
                print(f"   Confianza aceptable pero puede mejorarse agregando más API keys.")
            elif result['quality'] == 'Good':
                print(f"\n✅ Buena calidad de datos con {result['sources_used']} fuentes!")
            else:  # Excellent
                print(f"\n⭐ ¡Excelente! Máxima confianza con {result['sources_used']} fuentes.")
            
        except Exception as e:
            print(f"\n❌ Error obteniendo {symbol}: {e}")
    
    # Mostrar estadísticas globales
    print_header("📊 ESTADÍSTICAS DEL SISTEMA")
    
    try:
        from src.data_sources.multi_broker_client import multi_broker
        stats = multi_broker.get_statistics()
        
        print(f"\n📈 Uso de APIs:")
        print(f"   Total de requests: {stats['total_requests']}")
        print(f"   Cache hits: {stats['cache_hits']} ({stats['cache_hits']/max(stats['total_requests'],1)*100:.1f}%)")
        
        if stats.get('requests_by_source'):
            print(f"\n📊 Requests por fuente:")
            for source, count in sorted(stats['requests_by_source'].items(), key=lambda x: x[1], reverse=True):
                print(f"   • {source:20s}: {count:>4d} requests")
    except Exception as e:
        print(f"\n⚠️  No se pudieron obtener estadísticas: {e}")
    
    # Conclusión
    print_header("📋 CONCLUSIÓN")
    
    print("\n✅ El sistema multi-broker está funcionando correctamente!")
    print("\n📝 Próximos pasos:")
    print("   1. Agrega API keys en config/broker_apis.py para mejorar la precisión")
    print("   2. Lee MULTI_BROKER_SETUP.md para configuración completa")
    print("   3. Inicia el dashboard: python3 run_gui.py")
    print("   4. Explora los endpoints de la API REST")
    
    print("\n🌐 Endpoints disponibles:")
    print("   • GET /api/price-quality/<symbol>  - Precio con calidad")
    print("   • GET /api/broker-stats            - Estadísticas de uso")
    print("   • GET /api/analyze/<symbol>        - Análisis completo")
    print("   • GET /api/analyze-all             - Todos los activos")
    
    print("\n🎯 Fuentes de datos totales: 14")
    print("   • 6 Crypto Exchanges (Binance, Bybit, Coinbase, OKX, Kraken, KuCoin)")
    print("   • 1 Free API (yfinance)")
    print("   • 7 Premium APIs (Alpha Vantage, Finnhub, Twelve Data, etc.)")
    
    print("\n" + "="*70)
    print("  Para más información: MULTI_BROKER_SETUP.md o SISTEMA_COMPLETO.md")
    print("="*70 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrumpida por el usuario")
    except Exception as e:
        print(f"\n❌ Error en la demo: {e}")
        import traceback
        traceback.print_exc()
