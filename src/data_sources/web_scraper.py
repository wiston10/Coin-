"""
Web Scraper para datos de trading en tiempo real
Obtiene datos directamente desde exchanges y sitios de criptomonedas
Ideal para scalping con datos actualizados cada segundo
"""
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
from bs4 import BeautifulSoup
import json
import ccxt


class CryptoWebScraper:
    """
    Scraper de datos de criptomonedas desde múltiples fuentes
    - CoinGecko API (gratis, sin límites)
    - Binance API pública
    - CryptoCompare API
    - Scraping directo de exchanges
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
        # Exchanges CCXT para datos en vivo (6 exchanges populares)
        self.exchanges = {
            'binance': ccxt.binance({'enableRateLimit': True}),
            'coinbase': ccxt.coinbaseadvanced({'enableRateLimit': True}),
            'kraken': ccxt.kraken({'enableRateLimit': True}),
            'bybit': ccxt.bybit({'enableRateLimit': True}),
            'kucoin': ccxt.kucoin({'enableRateLimit': True}),
            'okx': ccxt.okx({'enableRateLimit': True})
        }
        
        # Prioridad de exchanges (ordenado por confiabilidad y liquidez)
        self.exchange_priority = ['binance', 'bybit', 'coinbase', 'okx', 'kraken', 'kucoin']
        
        # APIs públicas
        self.coingecko_base = "https://api.coingecko.com/api/v3"
        self.binance_base = "https://api.binance.com/api/v3"
        self.cryptocompare_base = "https://min-api.cryptocompare.com/data"
        
        # Caché para reducir requests
        self.cache = {}
        self.cache_duration = 5  # segundos
        
    def get_live_data(self, symbol, interval='1m', limit=500, preferred_exchange=None):
        """
        Obtiene datos en vivo desde exchange (método principal para scalping)
        Intenta múltiples exchanges en orden de prioridad si uno falla
        
        Args:
            symbol: Par de trading (ej: 'BTC/USDT', 'ETH/USDT')
            interval: '1m', '5m', '15m', '30m', '1h'
            limit: Número de velas (100-1000)
            preferred_exchange: Exchange preferido o None para auto-selección
        
        Returns:
            DataFrame con OHLCV actualizado
        """
        # Convertir símbolo al formato de CCXT
        if '-' in symbol:
            symbol = symbol.replace('-', '/')
        if 'USD' in symbol and 'USDT' not in symbol:
            symbol = symbol.replace('USD', 'USDT')
        
        # Determinar orden de exchanges a intentar
        if preferred_exchange and preferred_exchange in self.exchanges:
            exchanges_to_try = [preferred_exchange] + [e for e in self.exchange_priority if e != preferred_exchange]
        else:
            exchanges_to_try = self.exchange_priority
        
        # Intentar obtener datos de exchanges en orden de prioridad
        for exchange_name in exchanges_to_try:
            try:
                print(f"🔴 Obteniendo datos EN VIVO desde {exchange_name.upper()}...")
                
                exchange = self.exchanges[exchange_name]
                ohlcv = exchange.fetch_ohlcv(symbol, interval, limit=limit)
                
                # Convertir a DataFrame
                df = pd.DataFrame(ohlcv, columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df.set_index('timestamp', inplace=True)
                df['exchange'] = exchange_name
                
                print(f"✅ Datos en vivo: {len(df)} velas desde {exchange_name.upper()} (actualizado: {datetime.now().strftime('%H:%M:%S')})")
                return df
                
            except Exception as e:
                print(f"⚠️ Error con {exchange_name}: {str(e)}")
                if exchange_name == exchanges_to_try[-1]:  # Último intento
                    print(f"❌ Todos los exchanges fallaron, intentando API pública...")
                    return self._fallback_to_api(symbol, interval, limit)
                else:
                    print(f"🔄 Intentando siguiente exchange...")
                    continue
        
        return self._fallback_to_api(symbol, interval, limit)
    
    def get_realtime_ticker(self, symbol, preferred_exchange=None):
        """
        Obtiene precio actual en tiempo real (actualización cada segundo)
        Intenta múltiples exchanges en orden de prioridad
        
        Returns:
            dict con precio, volumen, cambio 24h, etc., y el exchange usado
        """
        if '-' in symbol:
            symbol = symbol.replace('-', '/')
        if 'USD' in symbol and 'USDT' not in symbol:
            symbol = symbol.replace('USD', 'USDT')
        
        # Determinar orden de exchanges
        if preferred_exchange and preferred_exchange in self.exchanges:
            exchanges_to_try = [preferred_exchange] + [e for e in self.exchange_priority if e != preferred_exchange]
        else:
            exchanges_to_try = self.exchange_priority
        
        # Intentar obtener ticker de exchanges
        for exchange_name in exchanges_to_try:
            try:
                exchange = self.exchanges[exchange_name]
                ticker = exchange.fetch_ticker(symbol)
                
                return {
                    'symbol': symbol,
                    'price': ticker['last'],
                    'high_24h': ticker['high'],
                    'low_24h': ticker['low'],
                    'volume_24h': ticker['baseVolume'],
                    'change_24h': ticker['percentage'],
                    'bid': ticker['bid'],
                    'ask': ticker['ask'],
                    'exchange': exchange_name,
                    'timestamp': datetime.now()
                }
                
            except Exception as e:
                if exchange_name == exchanges_to_try[-1]:
                    print(f"⚠️ Error obteniendo ticker de todos los exchanges: {str(e)}")
                    return None
                continue
        
        return None
    
    def _fallback_to_api(self, symbol, interval, limit):
        """Fallback a API de Binance pública si CCXT falla"""
        try:
            print(f"🔄 Intentando API pública de Binance...")
            
            # Mapeo de intervalos
            interval_map = {
                '1m': '1m', '5m': '5m', '15m': '15m',
                '30m': '30m', '1h': '1h', '4h': '4h', '1d': '1d'
            }
            
            # Convertir símbolo
            binance_symbol = symbol.replace('/', '').replace('-', '')
            if 'USD' in binance_symbol and 'USDT' not in binance_symbol:
                binance_symbol = binance_symbol.replace('USD', 'USDT')
            
            # Request a API pública
            url = f"{self.binance_base}/klines"
            params = {
                'symbol': binance_symbol,
                'interval': interval_map.get(interval, '1m'),
                'limit': min(limit, 1000)
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Convertir a DataFrame
            df = pd.DataFrame(data, columns=[
                'timestamp', 'Open', 'High', 'Low', 'Close', 'Volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])
            
            df = df[['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume']]
            df['timestamp'] = pd.to_datetime(df['timestamp'].astype(float), unit='ms')
            df[['Open', 'High', 'Low', 'Close', 'Volume']] = df[['Open', 'High', 'Low', 'Close', 'Volume']].astype(float)
            df.set_index('timestamp', inplace=True)
            
            print(f"✅ API pública: {len(df)} velas")
            return df
            
        except Exception as e:
            print(f"❌ Error con API pública: {str(e)}")
            return self._scrape_from_coingecko(symbol, interval, limit)
    
    def _scrape_from_coingecko(self, symbol, interval, limit):
        """Scraping de CoinGecko como último recurso"""
        try:
            print(f"🔄 Intentando CoinGecko...")
            
            # Mapear símbolo a coin ID de CoinGecko
            coin_map = {
                'BTC': 'bitcoin', 'ETH': 'ethereum', 'BNB': 'binancecoin',
                'XRP': 'ripple', 'ADA': 'cardano', 'SOL': 'solana',
                'DOGE': 'dogecoin', 'DOT': 'polkadot', 'MATIC': 'matic-network',
                'AVAX': 'avalanche-2', 'LTC': 'litecoin', 'LINK': 'chainlink'
            }
            
            base = symbol.split('/')[0].split('-')[0]
            coin_id = coin_map.get(base, base.lower())
            
            # Calcular días basado en límite e intervalo
            minutes_per_candle = {'1m': 1, '5m': 5, '15m': 15, '30m': 30, '1h': 60}
            minutes_needed = limit * minutes_per_candle.get(interval, 1)
            days = max(1, minutes_needed // 1440)  # 1440 minutos = 1 día
            
            # Request a CoinGecko
            url = f"{self.coingecko_base}/coins/{coin_id}/market_chart"
            params = {
                'vs_currency': 'usd',
                'days': min(days, 90),  # Máximo 90 días
                'interval': 'minute' if 'm' in interval else 'hourly'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Convertir precios a OHLCV simulado
            prices = data.get('prices', [])
            volumes = data.get('total_volumes', [])
            
            if not prices:
                return None
            
            # Crear DataFrame
            df = pd.DataFrame(prices, columns=['timestamp', 'Close'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df['Volume'] = [v[1] for v in volumes] if volumes else 0
            
            # Simular OHLC desde Close (aproximación)
            df['Open'] = df['Close'].shift(1).fillna(df['Close'])
            df['High'] = df[['Open', 'Close']].max(axis=1) * 1.001
            df['Low'] = df[['Open', 'Close']].min(axis=1) * 0.999
            
            df = df[['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume']]
            df.set_index('timestamp', inplace=True)
            
            # Resample según intervalo si es necesario
            if interval != '1m':
                df = self._resample_data(df, interval)
            
            print(f"✅ CoinGecko: {len(df)} velas")
            return df.tail(limit)
            
        except Exception as e:
            print(f"❌ Error con CoinGecko: {str(e)}")
            return None
    
    def _resample_data(self, df, interval):
        """Resample data a un intervalo diferente"""
        interval_map = {
            '5m': '5min', '15m': '15min', '30m': '30min',
            '1h': '1H', '4h': '4H', '1d': '1D'
        }
        
        freq = interval_map.get(interval, '1min')
        
        resampled = df.resample(freq).agg({
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum'
        })
        
        return resampled.dropna()
    
    def stream_live_data(self, symbol, callback, interval='1m'):
        """
        Stream de datos en vivo con callback
        Perfecto para scalping con actualización continua
        
        Args:
            symbol: Par de trading
            callback: Función que se llama con cada actualización
            interval: Intervalo de actualización
        """
        print(f"🔴 Iniciando stream en vivo de {symbol}...")
        print(f"⏱️  Actualización cada {interval}")
        print(f"⏹️  Presiona Ctrl+C para detener\n")
        
        last_update = {}
        update_seconds = {'1m': 5, '5m': 15, '15m': 30, '30m': 60, '1h': 120}
        wait_time = update_seconds.get(interval, 5)
        
        try:
            while True:
                # Obtener datos actualizados
                df = self.get_live_data(symbol, interval, limit=200)
                ticker = self.get_realtime_ticker(symbol)
                
                if df is not None and not df.empty:
                    # Llamar callback con datos nuevos
                    callback(df, ticker)
                
                # Esperar antes de la siguiente actualización
                time.sleep(wait_time)
                
        except KeyboardInterrupt:
            print(f"\n⏹️  Stream detenido por usuario")
        except Exception as e:
            print(f"\n❌ Error en stream: {str(e)}")
    
    def get_order_book(self, symbol, depth=20):
        """
        Obtiene el libro de órdenes (order book) en tiempo real
        Útil para ver presión de compra/venta
        """
        try:
            if '-' in symbol:
                symbol = symbol.replace('-', '/')
            if 'USD' in symbol and 'USDT' not in symbol:
                symbol = symbol.replace('USD', 'USDT')
            
            exchange = self.exchanges['binance']
            order_book = exchange.fetch_order_book(symbol, limit=depth)
            
            return {
                'bids': order_book['bids'][:depth],  # Órdenes de compra
                'asks': order_book['asks'][:depth],  # Órdenes de venta
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            print(f"⚠️ Error obteniendo order book: {str(e)}")
            return None
    
    def get_recent_trades(self, symbol, limit=100):
        """
        Obtiene las últimas operaciones ejecutadas
        Útil para analizar flujo de órdenes
        """
        try:
            if '-' in symbol:
                symbol = symbol.replace('-', '/')
            if 'USD' in symbol and 'USDT' not in symbol:
                symbol = symbol.replace('USD', 'USDT')
            
            exchange = self.exchanges['binance']
            trades = exchange.fetch_trades(symbol, limit=limit)
            
            df = pd.DataFrame(trades)
            df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            return df[['datetime', 'price', 'amount', 'side', 'cost']]
            
        except Exception as e:
            print(f"⚠️ Error obteniendo trades: {str(e)}")
            return None


# Instancia global
scraper = CryptoWebScraper()


def get_live_data(symbol, interval='1m', limit=500):
    """
    Función de conveniencia para obtener datos en vivo
    
    Args:
        symbol: 'BTC-USD', 'ETH-USD', etc.
        interval: '1m', '5m', '15m', '30m', '1h'
        limit: Número de velas (100-1000)
    
    Returns:
        DataFrame con OHLCV actualizado en tiempo real
    """
    return scraper.get_live_data(symbol, interval, limit)


def get_realtime_price(symbol):
    """
    Obtiene precio actual en tiempo real
    
    Returns:
        dict con precio y estadísticas
    """
    return scraper.get_realtime_ticker(symbol)


def start_live_stream(symbol, callback, interval='1m'):
    """
    Inicia stream de datos en vivo con callback
    
    Args:
        symbol: Par de trading
        callback: función(df, ticker) que se llama con cada actualización
        interval: Intervalo de actualización
    """
    scraper.stream_live_data(symbol, callback, interval)
