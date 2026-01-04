"""
Módulo para obtener datos de mercado desde múltiples fuentes
Soporta: yfinance, ccxt (exchanges de cripto), y APIs REST
"""
import pandas as pd
import yfinance as yf
import ccxt
from datetime import datetime, timedelta
import time


class MarketDataSources:
    """Gestor de múltiples fuentes de datos de mercado"""
    
    def __init__(self):
        # Inicializar exchanges de CCXT (6 exchanges populares en 2026)
        self.exchanges = {
            'binance': ccxt.binance({'enableRateLimit': True}),
            'coinbase': ccxt.coinbaseadvanced({'enableRateLimit': True}),
            'kraken': ccxt.kraken({'enableRateLimit': True}),
            'bybit': ccxt.bybit({'enableRateLimit': True}),
            'kucoin': ccxt.kucoin({'enableRateLimit': True}),
            'okx': ccxt.okx({'enableRateLimit': True})
        }
        
        # Prioridad de exchanges (ordenado por liquidez y confiabilidad)
        self.exchange_priority = ['binance', 'bybit', 'coinbase', 'okx', 'kraken', 'kucoin']
        
        # Mapeo de símbolos (expandido con criptos populares 2026)
        self.symbol_map = {
            'BTC-USD': {'ccxt': 'BTC/USDT', 'yfinance': 'BTC-USD'},
            'ETH-USD': {'ccxt': 'ETH/USDT', 'yfinance': 'ETH-USD'},
            'ETH-BTC': {'ccxt': 'ETH/BTC', 'yfinance': 'ETH-BTC'},
            'BNB-USD': {'ccxt': 'BNB/USDT', 'yfinance': 'BNB-USD'},
            'SOL-USD': {'ccxt': 'SOL/USDT', 'yfinance': 'SOL-USD'},
            'XRP-USD': {'ccxt': 'XRP/USDT', 'yfinance': 'XRP-USD'},
            'ADA-USD': {'ccxt': 'ADA/USDT', 'yfinance': 'ADA-USD'},
            'DOGE-USD': {'ccxt': 'DOGE/USDT', 'yfinance': 'DOGE-USD'},
            'DOT-USD': {'ccxt': 'DOT/USDT', 'yfinance': 'DOT-USD'},
            'MATIC-USD': {'ccxt': 'MATIC/USDT', 'yfinance': 'MATIC-USD'},
            'AVAX-USD': {'ccxt': 'AVAX/USDT', 'yfinance': 'AVAX-USD'},
            'LINK-USD': {'ccxt': 'LINK/USDT', 'yfinance': 'LINK-USD'},
            'UNI-USD': {'ccxt': 'UNI/USDT', 'yfinance': 'UNI-USD'},
            'ATOM-USD': {'ccxt': 'ATOM/USDT', 'yfinance': 'ATOM-USD'},
            'LTC-USD': {'ccxt': 'LTC/USDT', 'yfinance': 'LTC-USD'},
            'BCH-USD': {'ccxt': 'BCH/USDT', 'yfinance': 'BCH-USD'},
            'ALGO-USD': {'ccxt': 'ALGO/USDT', 'yfinance': 'ALGO-USD'},
            'VET-USD': {'ccxt': 'VET/USDT', 'yfinance': 'VET-USD'},
            'FTM-USD': {'ccxt': 'FTM/USDT', 'yfinance': 'FTM-USD'},
        }
        
        # Pares válidos más comunes (actualizado 2026)
        self.common_valid_pairs = [
            'BTC-USD', 'ETH-USD', 'ETH-BTC', 'BNB-USD', 'SOL-USD',
            'XRP-USD', 'ADA-USD', 'DOGE-USD', 'MATIC-USD', 'AVAX-USD',
            'LINK-USD', 'UNI-USD', 'ATOM-USD', 'LTC-USD', 'DOT-USD'
        ]
    
    def validate_symbol(self, symbol):
        """
        Valida si un símbolo es válido y sugiere alternativas
        
        Returns:
            tuple: (is_valid, suggestion_message)
        """
        # Convertir a mayúsculas
        symbol = symbol.upper()
        
        # Verificar formato básico
        if '-' not in symbol:
            return False, f"❌ Formato inválido. Use: CRYPTO-USD (ej: BTC-USD, ETH-USD)"
        
        parts = symbol.split('-')
        if len(parts) != 2:
            return False, f"❌ Formato inválido. Use: CRYPTO-USD (ej: BTC-USD)"
        
        base, quote = parts
        
        # Pares inválidos comunes
        invalid_patterns = [
            ('BTC', 'ETH'),  # BTC-ETH no existe, debe ser ETH-BTC
            ('USD', 'EUR'),  # USD-EUR no existe, debe ser EUR-USD o usar forex
            ('USD', 'GBP'),  # Similar
        ]
        
        for invalid_base, invalid_quote in invalid_patterns:
            if base == invalid_base and quote == invalid_quote:
                # Sugerir el orden correcto
                suggestion = f"{invalid_quote}-{invalid_base}"
                if suggestion in self.symbol_map or suggestion in self.common_valid_pairs:
                    return False, f"❌ {symbol} no existe. ¿Quisiste decir {suggestion}?"
                else:
                    return False, f"❌ {symbol} no es un par válido. Prueba: {invalid_quote}-USD o {invalid_base}-USD"
        
        # Sugerencias basadas en la moneda base
        if symbol not in self.symbol_map:
            suggestions = [s for s in self.common_valid_pairs if s.startswith(base + '-')]
            if suggestions:
                return False, f"❌ {symbol} no encontrado. Prueba: {', '.join(suggestions[:3])}"
            else:
                return False, f"❌ {symbol} no encontrado. Usa pares como: BTC-USD, ETH-USD, ETH-BTC"
        
        return True, ""
    
    def get_data(self, symbol, period='7d', interval='1d', source='auto'):
        """
        Obtiene datos de mercado con fallback automático
        
        Args:
            symbol: Símbolo del activo
            period: Período de datos
            interval: Intervalo de tiempo
            source: 'auto', 'ccxt', 'yfinance'
        
        Returns:
            DataFrame con OHLCV o None
        """
        # Validar símbolo primero
        is_valid, error_msg = self.validate_symbol(symbol)
        if not is_valid:
            print(error_msg)
            return None
        
        if source == 'auto':
            # Intentar primero con CCXT para cripto, luego yfinance
            if self._is_crypto(symbol):
                print("🔄 Intentando obtener datos desde CCXT (exchange)...")
                df = self._get_from_ccxt(symbol, period, interval)
                if df is not None and len(df) > 50:
                    print(f"✅ Datos obtenidos desde CCXT: {len(df)} velas")
                    return df
                print("⚠️ CCXT no disponible, usando yfinance...")
            
            # Fallback a yfinance
            return self._get_from_yfinance(symbol, period, interval)
        
        elif source == 'ccxt':
            return self._get_from_ccxt(symbol, period, interval)
        
        elif source == 'yfinance':
            return self._get_from_yfinance(symbol, period, interval)
        
        return None
    
    def _is_crypto(self, symbol):
        """Detecta si es criptomoneda"""
        crypto_keywords = ['BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'ADA', 'DOGE', 
                          'DOT', 'MATIC', 'AVAX', 'USDT', 'USDC']
        return any(keyword in symbol.upper() for keyword in crypto_keywords)
    
    def _get_from_ccxt(self, symbol, period, interval):
        """Obtiene datos desde exchanges usando CCXT con fallback entre exchanges"""
        # Mapear símbolo
        if symbol in self.symbol_map:
            ccxt_symbol = self.symbol_map[symbol]['ccxt']
        else:
            # Intentar conversión directa
            ccxt_symbol = symbol.replace('-USD', '/USDT')
        
        # Convertir intervalo a timeframe de CCXT
        timeframe = self._convert_interval_to_ccxt(interval)
        
        # Calcular timestamp de inicio
        since = self._calculate_since(period)
        
        # Intentar con cada exchange en orden de prioridad
        for exchange_name in self.exchange_priority:
            try:
                exchange = self.exchanges[exchange_name]
                
                # Obtener datos OHLCV
                ohlcv = exchange.fetch_ohlcv(
                    ccxt_symbol, 
                    timeframe=timeframe,
                    since=since,
                    limit=1000
                )
                
                if not ohlcv:
                    continue
                
                # Convertir a DataFrame
                df = pd.DataFrame(
                    ohlcv,
                    columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume']
                )
                
                # Convertir timestamp a datetime
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df.set_index('timestamp', inplace=True)
                df['exchange'] = exchange_name
                
                print(f"✅ Datos obtenidos desde {exchange_name.upper()}: {len(df)} velas")
                return df
                
            except Exception as e:
                print(f"⚠️ Error con {exchange_name}: {str(e)}")
                if exchange_name == self.exchange_priority[-1]:
                    print("❌ Todos los exchanges CCXT fallaron")
                    return None
                continue
        
        return None
    
    def _get_from_yfinance(self, symbol, period, interval):
        """Obtiene datos desde Yahoo Finance"""
        try:
            # Usar el símbolo de yfinance si existe el mapeo
            if symbol in self.symbol_map:
                yf_symbol = self.symbol_map[symbol]['yfinance']
            else:
                yf_symbol = symbol
            
            # Ajustar período si es necesario
            period = self._adjust_period_for_interval(interval, period)
            
            ticker = yf.Ticker(yf_symbol)
            df = ticker.history(period=period, interval=interval)
            
            if df.empty:
                return None
            
            return df
            
        except Exception as e:
            print(f"⚠️ Error con yfinance: {str(e)}")
            return None
    
    def _convert_interval_to_ccxt(self, interval):
        """Convierte intervalo a formato CCXT"""
        mapping = {
            '1m': '1m',
            '5m': '5m',
            '15m': '15m',
            '30m': '30m',
            '1h': '1h',
            '2h': '2h',
            '4h': '4h',
            '1d': '1d',
            '1wk': '1w',
            '1mo': '1M'
        }
        return mapping.get(interval, '1h')
    
    def _calculate_since(self, period):
        """Calcula timestamp de inicio en milisegundos"""
        period_map = {
            '1d': 1,
            '5d': 5,
            '7d': 7,
            '1mo': 30,
            '3mo': 90,
            '6mo': 180,
            '1y': 365,
            '2y': 730
        }
        
        days = period_map.get(period, 7)
        since_date = datetime.now() - timedelta(days=days)
        return int(since_date.timestamp() * 1000)
    
    def _adjust_period_for_interval(self, interval, period):
        """Ajusta período según intervalo para yfinance"""
        minute_intervals = ['1m', '2m', '5m', '15m', '30m']
        
        if interval in minute_intervals:
            if period not in ['1d', '5d', '7d']:
                return '7d'
        
        return period
    
    def get_realtime_price(self, symbol):
        """Obtiene precio actual en tiempo real desde múltiples exchanges"""
        try:
            if self._is_crypto(symbol):
                # Usar CCXT para cripto - intentar múltiples exchanges
                ccxt_symbol = self.symbol_map.get(symbol, {}).get('ccxt', symbol.replace('-USD', '/USDT'))
                
                for exchange_name in self.exchange_priority:
                    try:
                        ticker = self.exchanges[exchange_name].fetch_ticker(ccxt_symbol)
                        return ticker['last']
                    except:
                        continue
                
                return None
            else:
                # Usar yfinance para stocks
                ticker = yf.Ticker(symbol)
                data = ticker.history(period='1d', interval='1m')
                if not data.empty:
                    return data['Close'].iloc[-1]
                return None
                
        except Exception as e:
            print(f"⚠️ Error obteniendo precio en tiempo real: {str(e)}")
            return None
    
    def get_available_sources(self, symbol):
        """Lista las fuentes disponibles para un símbolo"""
        sources = []
        
        # Verificar cada exchange CCXT
        if self._is_crypto(symbol):
            ccxt_symbol = self.symbol_map.get(symbol, {}).get('ccxt', symbol.replace('-USD', '/USDT'))
            
            for exchange_name in self.exchange_priority:
                try:
                    self.exchanges[exchange_name].fetch_ticker(ccxt_symbol)
                    sources.append(f'ccxt_{exchange_name}')
                except:
                    pass
        
        # Verificar yfinance
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period='1d')
            if not data.empty:
                sources.append('yfinance')
        except:
            pass
        
        return sources


# Instancia global
market_data = MarketDataSources()


def get_market_data(symbol, period='7d', interval='1d', source='auto'):
    """
    Función de conveniencia para obtener datos de mercado
    
    Args:
        symbol: Símbolo del activo
        period: Período de datos
        interval: Intervalo de tiempo
        source: 'auto', 'ccxt', 'yfinance'
    
    Returns:
        DataFrame con OHLCV
    """
    return market_data.get_data(symbol, period, interval, source)


def get_realtime_price(symbol):
    """
    Función de conveniencia para obtener precio en tiempo real
    
    Args:
        symbol: Símbolo del activo
    
    Returns:
        float: Precio actual
    """
    return market_data.get_realtime_price(symbol)
