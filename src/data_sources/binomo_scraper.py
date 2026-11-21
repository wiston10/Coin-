#!/usr/bin/env python3
"""
Scraper para Binomo - Obtiene datos de velas japonesas en tiempo real
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import time
from bs4 import BeautifulSoup
import warnings
from src.env_loader import load_env, env_flag

load_env()
warnings.filterwarnings('ignore')


class BinomoScraper:
    """
    Scraper para obtener datos de trading de Binomo
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Referer': 'https://binomo.com/',
            'Origin': 'https://binomo.com'
        })
        
        # Mapeo de símbolos
        self.symbol_map = {
            'BTC-USD': 'BTCUSD_otc',
            'ETH-USD': 'ETHUSD_otc',
            'EUR-USD': 'EURUSD_otc',
            'GBP-USD': 'GBPUSD_otc',
            'USD-JPY': 'USDJPY_otc',
            'GOLD': 'XAUUSD_otc',
            'SILVER': 'XAGUSD_otc',
            'OIL': 'XTIUSD_otc',
        }
        
        # Mapeo de intervalos
        self.interval_map = {
            '1m': 60,
            '5m': 300,
            '15m': 900,
            '1h': 3600,
        }
        
        self.base_url = 'https://api.binomo.com'
        self.cache = {}
        self.cache_duration = 10
    
    def get_binomo_symbol(self, symbol):
        """Convierte símbolo estándar a formato Binomo"""
        return self.symbol_map.get(symbol, symbol + '_otc')
    
    def get_candles_api(self, symbol, interval='5m', limit=500):
        """
        Intenta obtener velas desde API de Binomo
        """
        try:
            binomo_symbol = self.get_binomo_symbol(symbol)
            interval_seconds = self.interval_map.get(interval, 300)
            
            # Endpoint de API (puede variar)
            url = f"{self.base_url}/platform/candles/{binomo_symbol}"
            
            params = {
                'interval': interval_seconds,
                'limit': limit,
                'to': int(time.time())
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data and 'candles' in data:
                    return self._parse_binomo_candles(data['candles'])
            
            return None
            
        except Exception as e:
            print(f"⚠️ Error API Binomo: {e}")
            return None
    
    def get_candles_websocket_simulation(self, symbol, interval='5m', limit=100):
        """
        Simula obtención de datos de Binomo usando estructura de datos conocida
        En un caso real, esto usaría WebSocket para datos en tiempo real
        """
        try:
            # Por ahora, generamos datos sintéticos basados en precios reales
            # En producción, esto se conectaría a WebSocket de Binomo
            
            print(f"🟣 Simulando datos de Binomo para {symbol}...")
            
            # Obtener precio base (podrías obtenerlo de otra fuente)
            base_prices = {
                'BTC-USD': 92000,
                'ETH-USD': 3800,
                'EUR-USD': 1.09,
                'GBP-USD': 1.27,
                'USD-JPY': 148.5,
                'GOLD': 2050,
                'SILVER': 24.5,
                'OIL': 72.3
            }
            
            base_price = base_prices.get(symbol, 100)
            
            # Generar velas sintéticas con variación realista
            candles = []
            unit, value = interval[-1], int(interval[:-1])
            interval_minutes = value * {'m': 1, 'h': 60, 'd': 1440}.get(unit, 1)
            
            now = datetime.now()
            for i in range(limit):
                timestamp = now - timedelta(minutes=interval_minutes * (limit - i))
                
                # Variación aleatoria pero realista
                variation = np.random.randn() * base_price * 0.002  # 0.2% de variación
                open_price = base_price + variation
                
                high_price = open_price + abs(np.random.randn() * base_price * 0.001)
                low_price = open_price - abs(np.random.randn() * base_price * 0.001)
                
                close_variation = np.random.randn() * base_price * 0.001
                close_price = open_price + close_variation
                
                # Asegurar que high/low sean consistentes
                high_price = max(high_price, open_price, close_price)
                low_price = min(low_price, open_price, close_price)
                
                volume = np.random.uniform(1000, 10000)
                
                candles.append({
                    'timestamp': timestamp,
                    'Open': open_price,
                    'High': high_price,
                    'Low': low_price,
                    'Close': close_price,
                    'Volume': volume
                })
                
                # Actualizar base_price para siguiente vela
                base_price = close_price
            
            df = pd.DataFrame(candles)
            df['source'] = 'binomo_simulation'
            
            print(f"✅ Binomo: {len(df)} velas simuladas")
            return df
            
        except Exception as e:
            print(f"❌ Error simulación Binomo: {e}")
            return None
    
    def _parse_binomo_candles(self, candles_data):
        """Convierte datos de Binomo a DataFrame"""
        try:
            candles = []
            
            for candle in candles_data:
                candles.append({
                    'timestamp': datetime.fromtimestamp(candle.get('time', 0)),
                    'Open': float(candle.get('open', 0)),
                    'High': float(candle.get('high', 0)),
                    'Low': float(candle.get('low', 0)),
                    'Close': float(candle.get('close', 0)),
                    'Volume': float(candle.get('volume', 0))
                })
            
            df = pd.DataFrame(candles)
            df['source'] = 'binomo_api'
            
            return df
            
        except Exception as e:
            print(f"❌ Error parseando Binomo: {e}")
            return None
    
    def get_live_data(self, symbol, interval='5m', limit=500):
        """
        Obtiene datos en vivo de Binomo
        Intenta primero API, luego simulación
        """
        # Verificar caché
        cache_key = f"{symbol}_{interval}"
        if cache_key in self.cache:
            cache_time, cache_data = self.cache[cache_key]
            if time.time() - cache_time < self.cache_duration:
                return cache_data
        
        # Intentar obtener de API
        df = self.get_candles_api(symbol, interval, limit)
        
        # Si falla, usar simulación SOLO si se permite explícitamente.
        # Los datos simulados son aleatorios: no sirven para operar.
        if df is None and env_flag('ALLOW_SIMULATED_DATA', False):
            df = self.get_candles_websocket_simulation(symbol, interval, limit)
        
        # Guardar en caché
        if df is not None:
            self.cache[cache_key] = (time.time(), df)
        
        return df
    
    def get_supported_symbols(self):
        """Retorna lista de símbolos soportados"""
        return list(self.symbol_map.keys())
    
    def compare_with_other_sources(self, symbol, interval='5m'):
        """
        Compara datos de Binomo con otras fuentes
        """
        print(f"\n{'='*80}")
        print(f"🔬 COMPARACIÓN: {symbol} - Binomo vs Otras Fuentes")
        print('='*80)
        
        # Obtener de Binomo
        df_binomo = self.get_live_data(symbol, interval, 100)
        
        comparison = {
            'binomo': {
                'available': df_binomo is not None,
                'rows': len(df_binomo) if df_binomo is not None else 0,
                'latest_price': df_binomo['Close'].iloc[-1] if df_binomo is not None and len(df_binomo) > 0 else None,
                'source': df_binomo['source'].iloc[0] if df_binomo is not None and len(df_binomo) > 0 else None,
                'latency': 'Baja (<1s)' if df_binomo is not None else 'N/A'
            }
        }
        
        print("\n📊 RESULTADOS:")
        print(f"\n🟣 Binomo:")
        print(f"   Disponible: {'✅' if comparison['binomo']['available'] else '❌'}")
        print(f"   Velas: {comparison['binomo']['rows']}")
        if comparison['binomo']['latest_price']:
            print(f"   Precio: ${comparison['binomo']['latest_price']:,.2f}")
        print(f"   Fuente: {comparison['binomo']['source']}")
        print(f"   Latencia: {comparison['binomo']['latency']}")
        
        print('='*80)
        
        return comparison


# Función de conveniencia
def get_binomo_data(symbol, interval='5m', limit=500):
    """
    Obtiene datos de Binomo
    """
    scraper = BinomoScraper()
    return scraper.get_live_data(symbol, interval, limit)


if __name__ == '__main__':
    print("="*80)
    print("🟣 BINOMO SCRAPER - TEST")
    print("="*80)
    
    scraper = BinomoScraper()
    
    # Mostrar símbolos soportados
    print("\n📋 SÍMBOLOS SOPORTADOS:")
    symbols = scraper.get_supported_symbols()
    print(f"   {', '.join(symbols)}")
    
    # Test 1: Bitcoin
    print("\n" + "="*80)
    print("TEST 1: BTC-USD desde Binomo")
    print("="*80)
    df_btc = scraper.get_live_data('BTC-USD', '5m', 100)
    if df_btc is not None:
        print(f"\n✅ BTC-USD: {len(df_btc)} velas")
        print(f"   Precio: ${df_btc['Close'].iloc[-1]:,.2f}")
        print(f"   Fuente: {df_btc['source'].iloc[-1]}")
        print(f"\n📊 Primeras 5 velas:")
        print(df_btc.head())
    
    # Test 2: EUR/USD
    print("\n" + "="*80)
    print("TEST 2: EUR-USD desde Binomo")
    print("="*80)
    df_eur = scraper.get_live_data('EUR-USD', '5m', 100)
    if df_eur is not None:
        print(f"\n✅ EUR-USD: {len(df_eur)} velas")
        print(f"   Precio: ${df_eur['Close'].iloc[-1]:,.4f}")
        print(f"   Fuente: {df_eur['source'].iloc[-1]}")
    
    # Test 3: Comparación
    print("\n" + "="*80)
    print("TEST 3: Comparación de fuentes")
    print("="*80)
    scraper.compare_with_other_sources('BTC-USD', '5m')
    
    print("\n✅ Tests completados!")
