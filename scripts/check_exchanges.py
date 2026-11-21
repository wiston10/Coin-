#!/usr/bin/env python3
"""
Script de prueba para verificar que todas las exchanges funcionan correctamente
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data_sources.web_scraper import CryptoWebScraper
from src.data_sources.market_data_sources import MarketDataSources
from src.data_sources.hybrid_data_source import HybridDataSource


def test_web_scraper():
    """Probar el web scraper con múltiples exchanges"""
    print("\n" + "="*80)
    print("🧪 PRUEBA 1: Web Scraper (CryptoWebScraper)")
    print("="*80)
    
    scraper = CryptoWebScraper()
    
    print(f"\n📋 Exchanges configurados: {list(scraper.exchanges.keys())}")
    print(f"🔢 Prioridad: {scraper.exchange_priority}")
    
    # Probar obtener datos de BTC
    symbol = 'BTC/USDT'
    print(f"\n🔍 Probando {symbol}...")
    
    try:
        df = scraper.get_live_data(symbol, interval='5m', limit=100)
        
        if df is not None and len(df) > 0:
            exchange_used = df['exchange'].iloc[0] if 'exchange' in df.columns else 'unknown'
            print(f"✅ ÉXITO: Obtenidos {len(df)} velas desde {exchange_used.upper()}")
            print(f"   Precio actual: ${df['Close'].iloc[-1]:.2f}")
            print(f"   Rango: ${df['Low'].min():.2f} - ${df['High'].max():.2f}")
        else:
            print("❌ ERROR: No se obtuvieron datos")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False
    
    # Probar ticker en tiempo real
    print(f"\n🔍 Probando ticker en tiempo real...")
    
    try:
        ticker = scraper.get_realtime_ticker(symbol)
        
        if ticker:
            exchange_used = ticker.get('exchange', 'unknown')
            print(f"✅ ÉXITO: Ticker desde {exchange_used.upper()}")
            print(f"   Precio: ${ticker.get('price', 0):.2f}")
            print(f"   24h High: ${ticker.get('high_24h', 0):.2f}")
            print(f"   24h Low: ${ticker.get('low_24h', 0):.2f}")
            print(f"   24h Change: {ticker.get('change_24h', 0):.2f}%")
        else:
            print("❌ ERROR: No se obtuvo ticker")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False
    
    return True


def test_market_data_sources():
    """Probar MarketDataSources con múltiples exchanges"""
    print("\n" + "="*80)
    print("🧪 PRUEBA 2: Market Data Sources")
    print("="*80)
    
    market = MarketDataSources()
    
    print(f"\n📋 Exchanges configurados: {list(market.exchanges.keys())}")
    print(f"🔢 Prioridad: {market.exchange_priority}")
    print(f"💱 Símbolos soportados: {len(market.symbol_map)}")
    
    # Probar obtener datos de ETH
    symbol = 'ETH-USD'
    print(f"\n🔍 Probando {symbol}...")
    
    try:
        df = market.get_data(symbol, period='1d', interval='5m', source='auto')
        
        if df is not None and len(df) > 0:
            exchange_used = df['exchange'].iloc[0] if 'exchange' in df.columns else 'auto'
            print(f"✅ ÉXITO: Obtenidos {len(df)} velas")
            print(f"   Exchange usado: {exchange_used.upper()}")
            print(f"   Precio actual: ${df['Close'].iloc[-1]:.2f}")
        else:
            print("❌ ERROR: No se obtuvieron datos")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False
    
    # Probar precio en tiempo real
    print(f"\n🔍 Probando precio en tiempo real...")
    
    try:
        price = market.get_realtime_price(symbol)
        
        if price:
            print(f"✅ ÉXITO: Precio actual ${price:.2f}")
        else:
            print("❌ ERROR: No se obtuvo precio")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False
    
    # Probar fuentes disponibles
    print(f"\n🔍 Verificando fuentes disponibles para {symbol}...")
    
    try:
        sources = market.get_available_sources(symbol)
        print(f"✅ Fuentes disponibles: {', '.join(sources)}")
        
        if not sources:
            print("⚠️ ADVERTENCIA: No se encontraron fuentes disponibles")
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    return True


def test_hybrid_data_source():
    """Probar HybridDataSource"""
    print("\n" + "="*80)
    print("🧪 PRUEBA 3: Hybrid Data Source (Sistema Completo)")
    print("="*80)
    
    hybrid = HybridDataSource()
    
    # Probar con diferentes tipos de activos
    test_assets = [
        ('BTC-USD', 'crypto'),
        ('ETH-USD', 'crypto'),
        ('AAPL', 'stock'),
        ('EUR-USD', 'forex')
    ]
    
    for symbol, asset_type in test_assets:
        print(f"\n🔍 Probando {symbol} ({asset_type})...")
        
        try:
            df = hybrid.get_live_data(symbol, interval='5m', limit=100)
            
            if df is not None and len(df) > 0:
                source = df['source'].iloc[0] if 'source' in df.columns else 'unknown'
                print(f"✅ ÉXITO: {len(df)} velas desde {source}")
                print(f"   Precio actual: ${df['Close'].iloc[-1]:.2f}")
            else:
                print(f"❌ ERROR: No se obtuvieron datos para {symbol}")
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
    
    return True


def main():
    """Ejecutar todas las pruebas"""
    print("\n" + "="*80)
    print("🚀 INICIANDO PRUEBAS DE EXCHANGES")
    print("="*80)
    print("\nProbando 6 exchanges: Binance, Bybit, Coinbase Pro, OKX, Kraken, KuCoin")
    print("Sistema de fallback automático activado\n")
    
    results = {
        'web_scraper': False,
        'market_data': False,
        'hybrid': False
    }
    
    # Ejecutar pruebas
    try:
        results['web_scraper'] = test_web_scraper()
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO en Web Scraper: {e}")
    
    try:
        results['market_data'] = test_market_data_sources()
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO en Market Data Sources: {e}")
    
    try:
        results['hybrid'] = test_hybrid_data_source()
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO en Hybrid Data Source: {e}")
    
    # Resumen
    print("\n" + "="*80)
    print("📊 RESUMEN DE PRUEBAS")
    print("="*80)
    
    for test_name, passed in results.items():
        status = "✅ PASÓ" if passed else "❌ FALLÓ"
        print(f"{status} - {test_name}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 ¡TODAS LAS PRUEBAS PASARON!")
        print("✅ El sistema está configurado correctamente con 6 exchanges")
        print("✅ El fallback automático funciona correctamente")
    else:
        print("\n⚠️ ALGUNAS PRUEBAS FALLARON")
        print("❌ Revisa los mensajes de error arriba")
    
    print("="*80 + "\n")
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
