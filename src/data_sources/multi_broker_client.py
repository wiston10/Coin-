"""
Cliente multi-broker para obtener datos de múltiples fuentes financieras
Soporta: Alpha Vantage, Finnhub, Twelve Data, IEX Cloud, Polygon, Marketstack, Fixer
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
from typing import Optional, Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

try:
    from config.broker_apis import *
except ImportError:
    print("⚠️ No se encontró configuración de broker APIs, usando valores por defecto")
    get_enabled_sources = lambda: ['yfinance']
    get_api_config = lambda x: {}
    API_TIMEOUT = 10
    API_RETRIES = 2
    RETRY_DELAY = 1


class MultiBrokerClient:
    """Cliente para obtener datos de múltiples brokers y APIs financieras"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
        # Cache para evitar requests duplicados
        self.cache = {}
        self.cache_timestamps = {}
        self.cache_duration = 60  # 60 segundos
        
        # Rate limiting
        self.last_request = {}
        self.min_interval = 1.0  # Mínimo 1 segundo entre requests
        
        # Estadísticas de uso
        self.request_count = {}
        self.error_count = {}
    
    def _get_cache_key(self, source, symbol, data_type='price'):
        """Genera clave única para cache"""
        return f"{source}:{symbol}:{data_type}"
    
    def _check_cache(self, cache_key):
        """Verifica si hay datos en cache"""
        if cache_key in self.cache:
            timestamp = self.cache_timestamps.get(cache_key, 0)
            if time.time() - timestamp < self.cache_duration:
                return self.cache[cache_key]
        return None
    
    def _update_cache(self, cache_key, data):
        """Actualiza el cache"""
        self.cache[cache_key] = data
        self.cache_timestamps[cache_key] = time.time()
    
    def _wait_for_rate_limit(self, source):
        """Espera para respetar rate limits"""
        if source in self.last_request:
            elapsed = time.time() - self.last_request[source]
            if elapsed < self.min_interval:
                time.sleep(self.min_interval - elapsed)
        self.last_request[source] = time.time()
    
    def _make_request(self, url, params=None, source='unknown'):
        """Hace request con retry y manejo de errores"""
        self._wait_for_rate_limit(source)
        
        for attempt in range(API_RETRIES):
            try:
                response = self.session.get(url, params=params, timeout=API_TIMEOUT)
                response.raise_for_status()
                
                # Actualizar estadísticas
                self.request_count[source] = self.request_count.get(source, 0) + 1
                
                return response.json()
                
            except Exception as e:
                self.error_count[source] = self.error_count.get(source, 0) + 1
                
                if attempt < API_RETRIES - 1:
                    time.sleep(RETRY_DELAY * (attempt + 1))
                else:
                    print(f"❌ Error con {source}: {str(e)}")
                    return None
        
        return None
    
    # ========================================================================
    # ALPHA VANTAGE
    # ========================================================================
    
    def get_alpha_vantage_price(self, symbol: str, asset_type: str = 'stock') -> Optional[float]:
        """Obtiene precio actual desde Alpha Vantage"""
        config = get_api_config('alpha_vantage')
        if not config.get('enabled'):
            return None
        
        cache_key = self._get_cache_key('alpha_vantage', symbol)
        cached = self._check_cache(cache_key)
        if cached:
            return cached
        
        try:
            # Función según tipo de activo
            if asset_type == 'forex':
                function = 'CURRENCY_EXCHANGE_RATE'
                from_currency = symbol.split('-')[0] if '-' in symbol else symbol[:3]
                to_currency = symbol.split('-')[1] if '-' in symbol else 'USD'
                params = {
                    'function': function,
                    'from_currency': from_currency,
                    'to_currency': to_currency,
                    'apikey': config['api_key']
                }
            else:
                function = 'GLOBAL_QUOTE'
                params = {
                    'function': function,
                    'symbol': symbol,
                    'apikey': config['api_key']
                }
            
            data = self._make_request(config['endpoint'], params, 'alpha_vantage')
            
            if data:
                if asset_type == 'forex' and 'Realtime Currency Exchange Rate' in data:
                    price = float(data['Realtime Currency Exchange Rate']['5. Exchange Rate'])
                elif 'Global Quote' in data and data['Global Quote']:
                    price = float(data['Global Quote']['05. price'])
                else:
                    return None
                
                self._update_cache(cache_key, price)
                return price
                
        except Exception as e:
            print(f"❌ Error Alpha Vantage {symbol}: {e}")
        
        return None
    
    # ========================================================================
    # FINNHUB
    # ========================================================================
    
    def get_finnhub_price(self, symbol: str, asset_type: str = 'stock') -> Optional[float]:
        """Obtiene precio actual desde Finnhub"""
        config = get_api_config('finnhub')
        if not config.get('enabled'):
            return None
        
        cache_key = self._get_cache_key('finnhub', symbol)
        cached = self._check_cache(cache_key)
        if cached:
            return cached
        
        try:
            if asset_type == 'forex':
                # Finnhub usa formato OANDA para forex
                from_currency = symbol.split('-')[0] if '-' in symbol else symbol[:3]
                to_currency = symbol.split('-')[1] if '-' in symbol else 'USD'
                symbol_finnhub = f"OANDA:{from_currency}_{to_currency}"
            else:
                symbol_finnhub = symbol
            
            url = f"{config['endpoint']}/quote"
            params = {
                'symbol': symbol_finnhub,
                'token': config['api_key']
            }
            
            data = self._make_request(url, params, 'finnhub')
            
            if data and 'c' in data:  # 'c' es el precio actual
                price = float(data['c'])
                self._update_cache(cache_key, price)
                return price
                
        except Exception as e:
            print(f"❌ Error Finnhub {symbol}: {e}")
        
        return None
    
    # ========================================================================
    # TWELVE DATA
    # ========================================================================
    
    def get_twelve_data_price(self, symbol: str, asset_type: str = 'stock') -> Optional[float]:
        """Obtiene precio actual desde Twelve Data"""
        config = get_api_config('twelve_data')
        if not config.get('enabled'):
            return None
        
        cache_key = self._get_cache_key('twelve_data', symbol)
        cached = self._check_cache(cache_key)
        if cached:
            return cached
        
        try:
            if asset_type == 'forex':
                # Twelve Data usa formato EUR/USD
                symbol_td = symbol.replace('-', '/')
            else:
                symbol_td = symbol
            
            url = f"{config['endpoint']}/price"
            params = {
                'symbol': symbol_td,
                'apikey': config['api_key']
            }
            
            data = self._make_request(url, params, 'twelve_data')
            
            if data and 'price' in data:
                price = float(data['price'])
                self._update_cache(cache_key, price)
                return price
                
        except Exception as e:
            print(f"❌ Error Twelve Data {symbol}: {e}")
        
        return None
    
    # ========================================================================
    # IEX CLOUD
    # ========================================================================
    
    def get_iex_cloud_price(self, symbol: str) -> Optional[float]:
        """Obtiene precio actual desde IEX Cloud (solo stocks)"""
        config = get_api_config('iex_cloud')
        if not config.get('enabled'):
            return None
        
        cache_key = self._get_cache_key('iex_cloud', symbol)
        cached = self._check_cache(cache_key)
        if cached:
            return cached
        
        try:
            url = f"{config['endpoint']}/stock/{symbol}/quote"
            params = {
                'token': config['api_key']
            }
            
            data = self._make_request(url, params, 'iex_cloud')
            
            if data and 'latestPrice' in data:
                price = float(data['latestPrice'])
                self._update_cache(cache_key, price)
                return price
                
        except Exception as e:
            print(f"❌ Error IEX Cloud {symbol}: {e}")
        
        return None
    
    # ========================================================================
    # POLYGON.IO
    # ========================================================================
    
    def get_polygon_price(self, symbol: str, asset_type: str = 'stock') -> Optional[float]:
        """Obtiene precio actual desde Polygon.io"""
        config = get_api_config('polygon')
        if not config.get('enabled'):
            return None
        
        cache_key = self._get_cache_key('polygon', symbol)
        cached = self._check_cache(cache_key)
        if cached:
            return cached
        
        try:
            if asset_type == 'forex':
                # Polygon usa formato C:EURUSD
                symbol_pg = f"C:{symbol.replace('-', '')}"
            else:
                symbol_pg = symbol
            
            url = f"{config['endpoint']}/v2/last/trade/{symbol_pg}"
            params = {
                'apiKey': config['api_key']
            }
            
            data = self._make_request(url, params, 'polygon')
            
            if data and 'results' in data and 'p' in data['results']:
                price = float(data['results']['p'])
                self._update_cache(cache_key, price)
                return price
                
        except Exception as e:
            print(f"❌ Error Polygon {symbol}: {e}")
        
        return None
    
    # ========================================================================
    # MARKETSTACK
    # ========================================================================
    
    def get_marketstack_price(self, symbol: str) -> Optional[float]:
        """Obtiene precio actual desde Marketstack (stocks/indices)"""
        config = get_api_config('marketstack')
        if not config.get('enabled'):
            return None
        
        cache_key = self._get_cache_key('marketstack', symbol)
        cached = self._check_cache(cache_key)
        if cached:
            return cached
        
        try:
            url = f"{config['endpoint']}/eod/latest"
            params = {
                'access_key': config['api_key'],
                'symbols': symbol
            }
            
            data = self._make_request(url, params, 'marketstack')
            
            if data and 'data' in data and len(data['data']) > 0:
                price = float(data['data'][0]['close'])
                self._update_cache(cache_key, price)
                return price
                
        except Exception as e:
            print(f"❌ Error Marketstack {symbol}: {e}")
        
        return None
    
    # ========================================================================
    # FIXER.IO / EXCHANGERATE
    # ========================================================================
    
    def get_fixer_price(self, symbol: str) -> Optional[float]:
        """Obtiene tasa de cambio desde Fixer.io (solo forex)"""
        config = get_api_config('fixer')
        if not config.get('enabled'):
            return None
        
        cache_key = self._get_cache_key('fixer', symbol)
        cached = self._check_cache(cache_key)
        if cached:
            return cached
        
        try:
            from_currency = symbol.split('-')[0] if '-' in symbol else symbol[:3]
            to_currency = symbol.split('-')[1] if '-' in symbol else 'USD'
            
            url = f"{config['endpoint']}/latest"
            params = {
                'access_key': config['api_key'],
                'base': from_currency,
                'symbols': to_currency
            }
            
            data = self._make_request(url, params, 'fixer')
            
            if data and 'rates' in data and to_currency in data['rates']:
                price = float(data['rates'][to_currency])
                self._update_cache(cache_key, price)
                return price
                
        except Exception as e:
            print(f"❌ Error Fixer {symbol}: {e}")
        
        return None
    
    # ========================================================================
    # MÉTODO UNIFICADO
    # ========================================================================
    
    def get_price_from_source(self, symbol: str, source: str, asset_type: str = 'stock') -> Optional[float]:
        """Obtiene precio desde una fuente específica"""
        methods = {
            'alpha_vantage': lambda: self.get_alpha_vantage_price(symbol, asset_type),
            'finnhub': lambda: self.get_finnhub_price(symbol, asset_type),
            'twelve_data': lambda: self.get_twelve_data_price(symbol, asset_type),
            'iex_cloud': lambda: self.get_iex_cloud_price(symbol) if asset_type == 'stock' else None,
            'polygon': lambda: self.get_polygon_price(symbol, asset_type),
            'marketstack': lambda: self.get_marketstack_price(symbol) if asset_type in ['stock', 'index'] else None,
            'fixer': lambda: self.get_fixer_price(symbol) if asset_type == 'forex' else None,
        }
        
        method = methods.get(source)
        if method:
            return method()
        
        return None
    
    def get_statistics(self):
        """Retorna estadísticas de uso de APIs"""
        return {
            'requests': self.request_count,
            'errors': self.error_count,
            'cache_size': len(self.cache)
        }


# Instancia global
multi_broker = MultiBrokerClient()
