#!/usr/bin/env python3
"""
Script de prueba para el sistema multi-broker y agregación de precios
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data_sources.hybrid_data_source import HybridDataSource


def test_aggregated_prices():
    """Prueba el sistema de agregación de precios multi-source"""
    print("\n" + "="*80)
    print("🧪 PRUEBA: Sistema Multi-Broker y Agregación de Precios")
    print("="*80)
    
    hybrid = HybridDataSource()
    
    # Activos de prueba
    test_assets = [
        ('AAPL', 'stock', 'Apple Inc.'),
        ('MSFT', 'stock', 'Microsoft'),
        ('EUR-USD', 'forex', 'Euro/Dollar'),
        ('GBP-USD', 'forex', 'Pound/Dollar'),
        ('SPY', 'index', 'S&P 500 ETF'),
        ('BTC-USD', 'crypto', 'Bitcoin'),
        ('ETH-USD', 'crypto', 'Ethereum'),
    ]
    
    results = []
    
    for symbol, asset_type, name in test_assets:
        print(f"\n{'='*80}")
        print(f"📊 Testeando: {name} ({symbol})")
        print(f"{'='*80}")
        
        try:
            result = hybrid.get_aggregated_price(symbol, asset_type)
            
            if result.get('price'):
                results.append({
                    'symbol': symbol,
                    'name': name,
                    'asset_type': asset_type,
                    'success': True,
                    **result
                })
                
                print(f"\n✅ ÉXITO:")
                print(f"   💰 Precio: ${result['price']:.4f}")
                print(f"   📊 Fuentes: {result['sources_used']}")
                print(f"   🎯 Confianza: {result['confidence']:.1%}")
                print(f"   ⭐ Calidad: {result['quality']}")
                print(f"   📈 Spread: {result['spread_pct']:.2f}%")
                
                if result.get('individual_prices'):
                    print(f"\n   📋 Precios individuales:")
                    for source, price in result['individual_prices'].items():
                        print(f"      • {source}: ${price:.4f}")
                
                if result.get('outliers'):
                    print(f"\n   ⚠️ Outliers detectados: {len(result['outliers'])}")
                    for outlier in result['outliers']:
                        print(f"      • {outlier['source']}: ${outlier['price']:.4f} (z-score: {outlier['z_score']:.2f})")
            else:
                results.append({
                    'symbol': symbol,
                    'name': name,
                    'asset_type': asset_type,
                    'success': False,
                    'error': result.get('error', 'Unknown error')
                })
                print(f"\n❌ ERROR: {result.get('error', 'No se pudo obtener precio')}")
                
        except Exception as e:
            results.append({
                'symbol': symbol,
                'name': name,
                'asset_type': asset_type,
                'success': False,
                'error': str(e)
            })
            print(f"\n❌ EXCEPCIÓN: {str(e)}")
    
    # Resumen
    print("\n" + "="*80)
    print("📊 RESUMEN DE PRUEBAS")
    print("="*80)
    
    successful = [r for r in results if r.get('success')]
    failed = [r for r in results if not r.get('success')]
    
    print(f"\n✅ Exitosos: {len(successful)}/{len(results)}")
    print(f"❌ Fallidos: {len(failed)}/{len(results)}")
    
    if successful:
        print(f"\n🏆 ACTIVOS CON DATOS EXITOSOS:")
        for r in successful:
            quality_emoji = {
                'Excellent': '💎',
                'Good': '✨',
                'Fair': '⭐',
                'Poor': '⚠️'
            }.get(r.get('quality', 'Poor'), '❓')
            
            print(f"   {quality_emoji} {r['name']:20s} | ${r['price']:10.4f} | {r['sources_used']} fuentes | {r['quality']}")
    
    if failed:
        print(f"\n❌ ACTIVOS FALLIDOS:")
        for r in failed:
            print(f"   • {r['name']:20s} - {r.get('error', 'Unknown')}")
    
    # Estadísticas de brokers
    print(f"\n" + "="*80)
    print("📈 ESTADÍSTICAS DE USO DE APIS")
    print("="*80)
    
    stats = hybrid.multi_broker.get_statistics()
    
    if stats['requests']:
        print(f"\n📞 Requests realizados:")
        for source, count in sorted(stats['requests'].items(), key=lambda x: x[1], reverse=True):
            errors = stats['errors'].get(source, 0)
            success_rate = ((count - errors) / count * 100) if count > 0 else 0
            print(f"   • {source:20s}: {count:3d} requests ({success_rate:.0f}% éxito)")
    
    if stats['errors']:
        print(f"\n⚠️ Errores por fuente:")
        for source, count in sorted(stats['errors'].items(), key=lambda x: x[1], reverse=True):
            print(f"   • {source:20s}: {count} errores")
    
    print(f"\n💾 Cache size: {stats['cache_size']} entradas")
    
    print("\n" + "="*80)
    
    return len(successful) == len(results)


def test_enabled_sources():
    """Muestra qué fuentes están habilitadas"""
    print("\n" + "="*80)
    print("🔌 FUENTES DE DATOS HABILITADAS")
    print("="*80)
    
    try:
        from config.broker_apis import get_enabled_sources, get_api_config
        
        enabled = get_enabled_sources()
        print(f"\n✅ Fuentes habilitadas: {len(enabled)}")
        
        for source in enabled:
            config = get_api_config(source)
            if config:
                rate_limit = config.get('rate_limit', 'N/A')
                print(f"   • {source:20s} - Rate limit: {rate_limit}/min")
            else:
                print(f"   • {source:20s} - Sin límites")
        
        disabled = ['alpha_vantage', 'finnhub', 'twelve_data', 'iex_cloud', 'polygon', 'marketstack', 'fixer']
        disabled = [s for s in disabled if s not in enabled]
        
        if disabled:
            print(f"\n⚠️ Fuentes disponibles pero no habilitadas: {len(disabled)}")
            for source in disabled:
                print(f"   • {source}")
            print(f"\n💡 Para habilitarlas, agrega tus API keys en config/broker_apis.py")
        
    except ImportError:
        print("\n⚠️ No se pudo cargar configuración de broker APIs")
        print("   Solo se usarán yfinance y exchanges")
    
    print("="*80)


def main():
    """Ejecutar todas las pruebas"""
    print("\n" + "="*80)
    print("🚀 INICIANDO PRUEBAS DEL SISTEMA MULTI-BROKER")
    print("="*80)
    print("\n📡 Sistema de agregación multi-source para máxima precisión")
    print("🎯 Combina datos de hasta 14 fuentes diferentes:")
    print("   • 6 Exchanges crypto")
    print("   • 7 Brokers/APIs financieras")
    print("   • Yahoo Finance")
    
    # Mostrar fuentes habilitadas
    test_enabled_sources()
    
    # Ejecutar pruebas de precios
    all_passed = test_aggregated_prices()
    
    if all_passed:
        print("\n🎉 ¡TODAS LAS PRUEBAS PASARON!")
        print("✅ El sistema multi-broker está funcionando correctamente")
        return 0
    else:
        print("\n⚠️ ALGUNAS PRUEBAS FALLARON")
        print("💡 Esto es normal si no has configurado API keys")
        print("   El sistema seguirá funcionando con yfinance y exchanges")
        return 1


if __name__ == '__main__':
    sys.exit(main())
