#!/usr/bin/env python3
"""
Sistema Híbrido de Datos en Tiempo Real
Combina Web Scraping (6 exchanges) + yfinance + Múltiples Brokers (7 APIs) para máxima precisión
Exchanges soportados: Binance, Bybit, Coinbase Advanced, OKX, Kraken, KuCoin
Brokers/APIs: Alpha Vantage, Finnhub, Twelve Data, IEX Cloud, Polygon, Marketstack, Fixer
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import yfinance as yf
from src.data_sources.web_scraper import CryptoWebScraper
from src.data_sources.binomo_scraper import BinomoScraper
from src.data_sources.multi_broker_client import multi_broker
from src.data_sources.price_aggregator import price_aggregator, get_aggregated_price
import warnings
warnings.filterwarnings('ignore')

try:
    from config.broker_apis import get_enabled_sources, SOURCE_PRIORITY
except ImportError:
    get_enabled_sources = lambda: ['yfinance']
    SOURCE_PRIORITY = {'stocks': ['yfinance'], 'forex': ['yfinance'], 'indices': ['yfinance'], 'crypto': ['exchanges']}


class HybridDataSource:
    """
    Fuente de datos híbrida que combina:
    - Web Scraping para criptomonedas (6 exchanges: Binance, Bybit, Coinbase Advanced, OKX, Kraken, KuCoin) - Datos en tiempo real
    - Múltiples Brokers/APIs (7 fuentes: Alpha Vantage, Finnhub, Twelve Data, IEX Cloud, Polygon, Marketstack, Fixer) - Precisión mejorada
    - yfinance para acciones, índices y forex - Datos cada 15-60s
    - Binomo para velas japonesas adicionales - Datos de trading binario
    - Sistema de agregación inteligente - Precio consenso de múltiples fuentes
    """
    
    def __init__(self):
        self.scraper = CryptoWebScraper()
        self.binomo = BinomoScraper()
        self.multi_broker = multi_broker
        self.price_aggregator = price_aggregator
        
        # Fuentes habilitadas
        self.enabled_sources = get_enabled_sources()
        print(f"📡 Fuentes habilitadas: {', '.join(self.enabled_sources)}")
        
        # Mapeo de símbolos crypto para diferentes fuentes (actualizado 2026)
        self.crypto_symbols = {
            # Formato interno -> Exchange format
            'BTC-USD': 'BTC/USDT',
            'ETH-USD': 'ETH/USDT',
            'SOL-USD': 'SOL/USDT',
            'MATIC-USD': 'MATIC/USDT',
            'ADA-USD': 'ADA/USDT',
            'DOT-USD': 'DOT/USDT',
            'AVAX-USD': 'AVAX/USDT',
            'LINK-USD': 'LINK/USDT',
            'UNI-USD': 'UNI/USDT',
            'LTC-USD': 'LTC/USDT',
            'ATOM-USD': 'ATOM/USDT',
            'BCH-USD': 'BCH/USDT',
            'ALGO-USD': 'ALGO/USDT',
            'VET-USD': 'VET/USDT',
            'FTM-USD': 'FTM/USDT',
        }
        
        # Mapeo de símbolos para yfinance
        self.yfinance_symbols = {
            # Acciones
            'AAPL': 'AAPL',
            'MSFT': 'MSFT',
            'GOOGL': 'GOOGL',
            'AMZN': 'AMZN',
            'TSLA': 'TSLA',
            'NVDA': 'NVDA',
            'META': 'META',
            
            # Índices
            'SPY': 'SPY',
            'QQQ': 'QQQ',
            'DIA': 'DIA',
            
            # Forex (todos los 20 pares)
            'EUR-USD': 'EURUSD=X',
            'GBP-USD': 'GBPUSD=X',
            'USD-JPY': 'USDJPY=X',
            'USD-CAD': 'USDCAD=X',
            'AUD-USD': 'AUDUSD=X',
            'NZD-USD': 'NZDUSD=X',
            'USD-CHF': 'USDCHF=X',
            'EUR-GBP': 'EURGBP=X',
            'EUR-JPY': 'EURJPY=X',
            'GBP-JPY': 'GBPJPY=X',
            'AUD-JPY': 'AUDJPY=X',
            'EUR-CHF': 'EURCHF=X',
            'GBP-CHF': 'GBPCHF=X',
            'CAD-JPY': 'CADJPY=X',
            'NZD-JPY': 'NZDJPY=X',
            'EUR-AUD': 'EURAUD=X',
            'GBP-AUD': 'GBPAUD=X',
            'EUR-CAD': 'EURCAD=X',
            'AUD-CAD': 'AUDCAD=X',
            'CHF-JPY': 'CHFJPY=X',
            
            # Commodities
            'GOLD': 'GC=F',
            'SILVER': 'SI=F',
            'OIL': 'CL=F',
        }
        
        # Lista explícita de forex para detección correcta
        self.forex_pairs = [
            'EUR-USD', 'GBP-USD', 'USD-JPY', 'USD-CAD', 'AUD-USD',
            'NZD-USD', 'USD-CHF', 'EUR-GBP', 'EUR-JPY', 'GBP-JPY',
            'AUD-JPY', 'EUR-CHF', 'GBP-CHF', 'CAD-JPY', 'NZD-JPY',
            'EUR-AUD', 'GBP-AUD', 'EUR-CAD', 'AUD-CAD', 'CHF-JPY'
        ]
        
        # Cache para optimizar requests y evitar rate limiting
        self.cache = {}
        self.cache_duration = 30  # 30 segundos para reducir requests
        self.last_request_time = {}
        self.min_request_interval = 0.5  # Mínimo 0.5s entre requests
    
    def detect_asset_type(self, symbol):
        """
        Detecta el tipo de activo basándose en el símbolo
        Returns: 'crypto', 'stock', 'forex', 'index', 'commodity'
        """
        symbol_upper = symbol.upper()
        
        # Forex (verificar primero para evitar confusión con crypto)
        if symbol_upper in self.forex_pairs:
            return 'forex'
        
        # Crypto
        if symbol_upper in self.crypto_symbols or (symbol_upper.endswith('-USD') and symbol_upper not in self.forex_pairs):
            return 'crypto'
        
        # Índices
        if symbol_upper in ['SPY', 'QQQ', 'DIA', 'IWM', 'VIX']:
            return 'index'
        
        # Commodities
        if symbol_upper in ['GOLD', 'SILVER', 'OIL']:
            return 'commodity'
        
        # Por defecto, asumimos acciones
        return 'stock'
    
    def get_live_data(self, symbol, interval='5m', limit=500):
        """
        Obtiene datos en tiempo real del símbolo especificado
        Usa web scraping para crypto, yfinance para el resto
        
        Args:
            symbol: Símbolo del activo (ej: 'BTC-USD', 'AAPL', 'EUR-USD')
            interval: Intervalo de tiempo ('1m', '5m', '15m', '1h', '1d')
            limit: Número de velas a obtener
            
        Returns:
            DataFrame con OHLCV data
        """
        asset_type = self.detect_asset_type(symbol)
        
        print(f"🔍 Detectado: {symbol} -> {asset_type.upper()}")
        
        if asset_type == 'crypto':
            return self._get_crypto_data(symbol, interval, limit)
        else:
            return self._get_yfinance_data(symbol, interval, limit, asset_type)
    
    def _get_crypto_data(self, symbol, interval, limit):
        """Obtiene datos de crypto usando web scraping con múltiples exchanges (tiempo real)"""
        try:
            print(f"🔴 Obteniendo {symbol} desde Exchanges (TIEMPO REAL)...")
            
            # Convertir símbolo si es necesario
            exchange_symbol = self.crypto_symbols.get(symbol, symbol)
            
            # Usar web scraper para datos en tiempo real (intentará múltiples exchanges)
            df = self.scraper.get_live_data(exchange_symbol, interval, limit)
            
            if df is not None and len(df) > 0:
                # Obtener el nombre del exchange usado (si está en el DataFrame)
                exchange_used = df['exchange'].iloc[0] if 'exchange' in df.columns else 'exchange'
                print(f"✅ {len(df)} velas obtenidas desde {exchange_used.upper()}")
                df['source'] = f'{exchange_used}_realtime'
                return df
            
            return None
            
        except Exception as e:
            print(f"❌ Error en crypto: {e}")
            return None
    
    def _get_binomo_data(self, symbol, interval, limit):
        """Obtiene datos adicionales desde Binomo"""
        try:
            print(f"🟣 Obteniendo {symbol} desde Binomo (VELAS JAPONESAS)...")
            
            # Obtener datos de Binomo
            df = self.binomo.get_live_data(symbol, interval, limit)
            
            if df is not None and len(df) > 0:
                print(f"✅ {len(df)} velas obtenidas desde Binomo")
                return df
            
            return None
            
        except Exception as e:
            print(f"❌ Error en Binomo: {e}")
            return None
    
    def _get_yfinance_data(self, symbol, interval, limit, asset_type):
        """Obtiene datos usando yfinance (stocks, forex, etc)"""
        try:
            # Rate limiting: esperar entre requests
            import time
            current_time = time.time()
            if symbol in self.last_request_time:
                time_since_last = current_time - self.last_request_time[symbol]
                if time_since_last < self.min_request_interval:
                    time.sleep(self.min_request_interval - time_since_last)
            
            self.last_request_time[symbol] = time.time()
            
            print(f"📊 Obteniendo {symbol} desde Yahoo Finance...")
            
            # Convertir símbolo si es necesario
            yf_symbol = self.yfinance_symbols.get(symbol, symbol)
            
            # Mapear intervalos
            interval_map = {
                '1m': '1m',
                '5m': '5m',
                '15m': '15m',
                '30m': '30m',
                '1h': '1h',
                '1d': '1d'
            }
            yf_interval = interval_map.get(interval, '5m')
            
            # Calcular período basado en el intervalo y límite
            if interval in ['1m', '5m']:
                period = '7d'  # Máximo para intervalos cortos
            elif interval in ['15m', '30m']:
                period = '60d'
            elif interval == '1h':
                period = '730d'
            else:
                period = 'max'
            
            # Obtener datos con retry y backoff
            max_retries = 3
            retry_delay = 1
            df = None
            
            for attempt in range(max_retries):
                try:
                    ticker = yf.Ticker(yf_symbol)
                    df = ticker.history(period=period, interval=yf_interval)
                    
                    if df is not None and len(df) > 0:
                        break
                    
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Backoff exponencial
                        
                except Exception as retry_error:
                    if 'Too Many Requests' in str(retry_error) or 'Rate limited' in str(retry_error):
                        if attempt < max_retries - 1:
                            print(f"⏳ Rate limit detectado, esperando {retry_delay}s...")
                            time.sleep(retry_delay)
                            retry_delay *= 2
                        else:
                            raise
                    else:
                        raise
            
            if df is not None and len(df) > 0:
                # Limpiar y formatear
                df = df.reset_index()
                
                # Renombrar columnas para consistencia
                df = df.rename(columns={
                    'Datetime': 'timestamp',
                    'Date': 'timestamp'
                })
                
                if 'timestamp' not in df.columns and 'index' in df.columns:
                    df = df.rename(columns={'index': 'timestamp'})
                
                # Asegurar que tenemos timestamp
                if 'timestamp' not in df.columns:
                    df['timestamp'] = df.index
                
                # Limitar a las últimas N velas
                df = df.tail(limit)
                
                # Agregar metadata
                df['source'] = f'yfinance_{asset_type}'
                
                print(f"✅ {len(df)} velas obtenidas desde Yahoo Finance")
                return df
            
            return None
            
        except Exception as e:
            print(f"❌ Error en yfinance: {e}")
            return None
    
    def get_aggregated_price(self, symbol: str, asset_type: str = None) -> Dict:
        """
        Obtiene precio agregado de múltiples fuentes para máxima precisión
        
        Args:
            symbol: Símbolo del activo
            asset_type: Tipo de activo (auto-detectado si no se proporciona)
            
        Returns:
            Dict con precio consenso, metadata y calidad
        """
        if asset_type is None:
            asset_type = self.detect_asset_type(symbol)
        
        print(f"💰 Obteniendo precio multi-source para {symbol} ({asset_type})...")
        
        prices = {}
        
        # 1. Obtener de yfinance (siempre disponible)
        try:
            yf_price = self._get_yfinance_quick_price(symbol, asset_type)
            if yf_price:
                prices['yfinance'] = yf_price
                print(f"   ✓ yfinance: ${yf_price:.4f}")
        except Exception as e:
            print(f"   ✗ yfinance: {e}")
        
        # 2. Obtener de exchanges (para crypto)
        if asset_type == 'crypto':
            try:
                ticker = self._get_crypto_ticker(symbol)
                if ticker and 'price' in ticker:
                    exchange_name = ticker.get('exchange', 'exchange')
                    prices[exchange_name] = ticker['price']
                    print(f"   ✓ {exchange_name}: ${ticker['price']:.4f}")
            except Exception as e:
                print(f"   ✗ exchanges: {e}")
        
        # 3. Obtener de brokers adicionales
        priority_list = SOURCE_PRIORITY.get(asset_type, ['yfinance'])
        
        for source in priority_list:
            if source in ['yfinance', 'exchanges']:
                continue  # Ya obtenidos
            
            if source not in self.enabled_sources:
                continue
            
            try:
                price = self.multi_broker.get_price_from_source(symbol, source, asset_type)
                if price and price > 0:
                    prices[source] = price
                    print(f"   ✓ {source}: ${price:.4f}")
            except Exception as e:
                print(f"   ✗ {source}: {e}")
        
        # 4. Agregar precios
        if not prices:
            print(f"   ❌ No se obtuvieron precios para {symbol}")
            return {
                'symbol': symbol,
                'price': None,
                'sources_used': 0,
                'confidence': 0.0,
                'quality': 'Poor',
                'error': 'No prices available'
            }
        
        consensus_price, metadata = get_aggregated_price(prices)
        
        if consensus_price is None:
            return {
                'symbol': symbol,
                'price': None,
                'sources_used': len(prices),
                'confidence': 0.0,
                'quality': 'Poor',
                'error': metadata.get('error', 'Aggregation failed')
            }
        
        # Calcular confianza y calidad
        confidence = self.price_aggregator.calculate_confidence_score(metadata)
        quality = self.price_aggregator.get_price_quality_rating(confidence)
        
        print(f"   💎 Precio consenso: ${consensus_price:.4f} ({quality} - {len(prices)} fuentes)")
        
        return {
            'symbol': symbol,
            'asset_type': asset_type,
            'price': consensus_price,
            'sources_used': len(prices),
            'confidence': confidence,
            'quality': quality,
            'spread_pct': metadata.get('spread_pct', 0),
            'std_dev': metadata.get('std_dev', 0),
            'individual_prices': metadata.get('individual_prices', {}),
            'outliers': metadata.get('outliers', []),
            'timestamp': metadata.get('timestamp'),
        }
    
    def _get_yfinance_quick_price(self, symbol: str, asset_type: str) -> Optional[float]:
        """Obtiene precio rápido de yfinance sin histórico completo"""
        try:
            yf_symbol = self.yfinance_symbols.get(symbol, symbol)
            ticker = yf.Ticker(yf_symbol)
            
            # Intentar fast_info primero (más rápido)
            if hasattr(ticker, 'fast_info'):
                return ticker.fast_info.get('lastPrice') or ticker.fast_info.get('regularMarketPrice')
            
            # Fallback a info
            info = ticker.info
            return info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose')
        except:
            return None
    
    def get_realtime_ticker(self, symbol):
        """
        Obtiene datos de ticker en tiempo real
        
        Returns:
            dict con: price, bid, ask, volume_24h, change_24h, high_24h, low_24h
        """
        asset_type = self.detect_asset_type(symbol)
        
        if asset_type == 'crypto':
            return self._get_crypto_ticker(symbol)
        else:
            return self._get_yfinance_ticker(symbol, asset_type)
    
    def _get_crypto_ticker(self, symbol):
        """Ticker en tiempo real para crypto (usando múltiples exchanges)"""
        try:
            exchange_symbol = self.crypto_symbols.get(symbol, symbol)
            ticker = self.scraper.get_realtime_ticker(exchange_symbol)
            
            # El ticker ahora incluye información del exchange usado
            if ticker and 'exchange' in ticker:
                ticker['source'] = f"{ticker['exchange']}_realtime"
            
            return ticker if ticker else {}
        except Exception as e:
            print(f"❌ Error obteniendo ticker crypto: {e}")
            return {}
    
    def _get_yfinance_ticker(self, symbol, asset_type):
        """Ticker para stocks/forex/etc usando yfinance"""
        try:
            yf_symbol = self.yfinance_symbols.get(symbol, symbol)
            ticker = yf.Ticker(yf_symbol)
            info = ticker.info
            
            # Obtener precio actual
            current_price = info.get('currentPrice') or info.get('regularMarketPrice') or 0
            
            # Obtener datos del día
            hist = ticker.history(period='2d', interval='1d')
            
            if len(hist) >= 2:
                prev_close = hist['Close'].iloc[-2]
                change_24h = ((current_price - prev_close) / prev_close * 100) if prev_close > 0 else 0
            else:
                change_24h = 0
            
            return {
                'symbol': symbol,
                'price': current_price,
                'bid': info.get('bid', current_price),
                'ask': info.get('ask', current_price),
                'volume_24h': info.get('volume', 0),
                'change_24h': change_24h,
                'high_24h': info.get('dayHigh', current_price),
                'low_24h': info.get('dayLow', current_price),
                'source': f'yfinance_{asset_type}',
                'updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error obteniendo ticker yfinance: {e}")
            return {}
    
    def get_multi_asset_data(self, symbols, interval='5m', limit=500):
        """
        Obtiene datos de múltiples activos en paralelo
        
        Args:
            symbols: Lista de símbolos ['BTC-USD', 'AAPL', 'EUR-USD', ...]
            interval: Intervalo de tiempo
            limit: Número de velas
            
        Returns:
            dict con {symbol: dataframe}
        """
        results = {}
        
        for symbol in symbols:
            print(f"\n{'='*60}")
            print(f"📊 Procesando: {symbol}")
            print('='*60)
            
            df = self.get_live_data(symbol, interval, limit)
            
            if df is not None and len(df) > 0:
                results[symbol] = df
                print(f"✅ {symbol}: {len(df)} velas cargadas")
            else:
                print(f"❌ {symbol}: No se pudieron obtener datos")
        
        return results
    
    def get_available_assets(self):
        """
        Retorna lista de activos disponibles agrupados por tipo
        """
        return {
            'crypto': list(self.crypto_symbols.keys()),
            'stocks': [k for k, v in self.yfinance_symbols.items() 
                      if not any(x in k for x in ['-', '='])],
            'forex': [k for k in self.yfinance_symbols.keys() 
                     if '-' in k and 'USD' in k],
            'indices': ['SPY', 'QQQ', 'DIA'],
            'commodities': ['GOLD', 'SILVER', 'OIL']
        }
    
    def get_data_with_binomo_fallback(self, symbol, interval='5m', limit=500):
        """
        Obtiene datos intentando múltiples fuentes incluyendo Binomo
        Prioridad: Principal (Binance/yfinance) -> Binomo -> Fallback
        """
        # Intentar fuente principal
        df_primary = self.get_live_data(symbol, interval, limit)
        
        if df_primary is not None and len(df_primary) >= limit * 0.5:  # Al menos 50% de datos
            print(f"✅ Usando fuente principal: {len(df_primary)} velas")
            return df_primary
        
        # Intentar Binomo como fallback
        print(f"🟣 Intentando Binomo como fuente alternativa...")
        df_binomo = self._get_binomo_data(symbol, interval, limit)
        
        if df_binomo is not None and len(df_binomo) > 0:
            print(f"✅ Usando Binomo: {len(df_binomo)} velas")
            return df_binomo
        
        # Retornar lo que tengamos
        return df_primary if df_primary is not None else df_binomo
    
    def compare_sources(self, symbol, interval='5m'):
        """
        Compara datos de TODAS las fuentes para verificar calidad
        Incluye: web scraping, yfinance y Binomo
        """
        print(f"\n{'='*80}")
        print(f"🔬 COMPARACIÓN DE FUENTES: {symbol}")
        print('='*80)
        
        # Intentar obtener de web scraping
        df_scraper = self._get_crypto_data(symbol, interval, 100)
        
        # Intentar obtener de yfinance
        yf_symbol = symbol if not symbol.endswith('-USD') else symbol
        df_yfinance = self._get_yfinance_data(yf_symbol, interval, 100, 'crypto')
        
        # Intentar obtener de Binomo
        df_binomo = self._get_binomo_data(symbol, interval, 100)
        
        comparison = {
            'web_scraping': {
                'available': df_scraper is not None,
                'rows': len(df_scraper) if df_scraper is not None else 0,
                'latest_price': df_scraper['Close'].iloc[-1] if df_scraper is not None and len(df_scraper) > 0 else None,
                'latency': 'Tiempo real (<1s)'
            },
            'yfinance': {
                'available': df_yfinance is not None,
                'rows': len(df_yfinance) if df_yfinance is not None else 0,
                'latest_price': df_yfinance['Close'].iloc[-1] if df_yfinance is not None and len(df_yfinance) > 0 else None,
                'latency': 'Diferido (15-60s)'
            },
            'binomo': {
                'available': df_binomo is not None,
                'rows': len(df_binomo) if df_binomo is not None else 0,
                'latest_price': df_binomo['Close'].iloc[-1] if df_binomo is not None and len(df_binomo) > 0 else None,
                'latency': 'Baja (<5s)'
            }
        }
        
        # Mostrar resultados
        print("\n📊 RESULTADOS:")
        print(f"\n🔴 Web Scraping (Multi-Exchange):")
        print(f"   Disponible: {'✅' if comparison['web_scraping']['available'] else '❌'}")
        print(f"   Velas: {comparison['web_scraping']['rows']}")
        print(f"   Precio: ${comparison['web_scraping']['latest_price']:.2f}" if comparison['web_scraping']['latest_price'] else "   Precio: N/A")
        print(f"   Latencia: {comparison['web_scraping']['latency']}")
        
        print(f"\n📊 yfinance:")
        print(f"   Disponible: {'✅' if comparison['yfinance']['available'] else '❌'}")
        print(f"   Velas: {comparison['yfinance']['rows']}")
        print(f"   Precio: ${comparison['yfinance']['latest_price']:.2f}" if comparison['yfinance']['latest_price'] else "   Precio: N/A")
        print(f"   Latencia: {comparison['yfinance']['latency']}")
        
        print(f"\n🟣 Binomo:")
        print(f"   Disponible: {'✅' if comparison['binomo']['available'] else '❌'}")
        print(f"   Velas: {comparison['binomo']['rows']}")
        print(f"   Precio: ${comparison['binomo']['latest_price']:.2f}" if comparison['binomo']['latest_price'] else "   Precio: N/A")
        print(f"   Latencia: {comparison['binomo']['latency']}")
        
        # Calcular diferencia de precio
        if comparison['web_scraping']['latest_price'] and comparison['yfinance']['latest_price']:
            price_diff = abs(comparison['web_scraping']['latest_price'] - comparison['yfinance']['latest_price'])
            price_diff_pct = (price_diff / comparison['web_scraping']['latest_price']) * 100
            print(f"\n💰 Diferencia de precio: ${price_diff:.2f} ({price_diff_pct:.2f}%)")
        
        print('='*80)
        
        return comparison


# Función de conveniencia
def get_hybrid_data(symbol, interval='5m', limit=500):
    """
    Obtiene datos usando el sistema híbrido
    Automáticamente elige la mejor fuente según el tipo de activo
    """
    source = HybridDataSource()
    return source.get_live_data(symbol, interval, limit)


if __name__ == '__main__':
    # Pruebas del sistema híbrido
    print("="*80)
    print("🚀 SISTEMA HÍBRIDO DE DATOS EN TIEMPO REAL")
    print("="*80)
    
    hybrid = HybridDataSource()
    
    # Mostrar activos disponibles
    print("\n📋 ACTIVOS DISPONIBLES:")
    assets = hybrid.get_available_assets()
    for asset_type, symbols in assets.items():
        print(f"\n{asset_type.upper()}: {len(symbols)} activos")
        print(f"   {', '.join(symbols[:5])}{'...' if len(symbols) > 5 else ''}")
    
    # Test 1: Crypto (web scraping - tiempo real)
    print("\n" + "="*80)
    print("TEST 1: CRYPTO (Web Scraping)")
    print("="*80)
    df_btc = hybrid.get_live_data('BTC-USD', '5m', 100)
    if df_btc is not None:
        print(f"\n✅ BTC-USD: {len(df_btc)} velas")
        print(f"   Precio: ${df_btc['Close'].iloc[-1]:,.2f}")
        print(f"   Fuente: {df_btc['source'].iloc[-1]}")
    
    # Test 2: Stock (yfinance)
    print("\n" + "="*80)
    print("TEST 2: STOCK (yfinance)")
    print("="*80)
    df_aapl = hybrid.get_live_data('AAPL', '5m', 100)
    if df_aapl is not None:
        print(f"\n✅ AAPL: {len(df_aapl)} velas")
        print(f"   Precio: ${df_aapl['Close'].iloc[-1]:,.2f}")
        print(f"   Fuente: {df_aapl['source'].iloc[-1]}")
    
    # Test 3: Forex (yfinance)
    print("\n" + "="*80)
    print("TEST 3: FOREX (yfinance)")
    print("="*80)
    df_eur = hybrid.get_live_data('EUR-USD', '5m', 100)
    if df_eur is not None:
        print(f"\n✅ EUR-USD: {len(df_eur)} velas")
        print(f"   Precio: ${df_eur['Close'].iloc[-1]:,.4f}")
        print(f"   Fuente: {df_eur['source'].iloc[-1]}")
    
    # Test 4: Comparación de fuentes
    print("\n" + "="*80)
    print("TEST 4: COMPARACIÓN DE FUENTES (BTC)")
    print("="*80)
    hybrid.compare_sources('BTC-USD', '5m')
    
    print("\n✅ Tests completados!")
