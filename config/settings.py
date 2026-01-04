"""
Configuración del sistema de trading
"""

# Parámetros de análisis técnico
TECHNICAL_PARAMS = {
    # Medias Móviles
    'SMA_PERIODS': [20, 50, 200],
    'EMA_PERIODS': [12, 26],
    
    # RSI
    'RSI_PERIOD': 14,
    'RSI_OVERBOUGHT': 70,
    'RSI_OVERSOLD': 30,
    
    # MACD
    'MACD_FAST': 12,
    'MACD_SLOW': 26,
    'MACD_SIGNAL': 9,
    
    # Bandas de Bollinger
    'BB_PERIOD': 20,
    'BB_STD_DEV': 2,
    
    # Estocástico
    'STOCH_PERIOD': 14,
    'STOCH_SMOOTH_K': 3,
    'STOCH_SMOOTH_D': 3,
    
    # ATR
    'ATR_PERIOD': 14,
    
    # ADX
    'ADX_PERIOD': 14,
    'ADX_STRONG_THRESHOLD': 25,
    'ADX_WEAK_THRESHOLD': 20,
}

# Parámetros de señales de trading
SIGNAL_PARAMS = {
    # Pesos para el cálculo de señales (total debe ser ~100)
    'PATTERN_WEIGHT': 20,
    'RSI_WEIGHT': 15,
    'MACD_WEIGHT': 15,
    'BB_WEIGHT': 10,
    'TREND_WEIGHT': 30,
    'SR_WEIGHT': 10,
    
    # Umbrales de confianza
    'MIN_CONFIDENCE_TO_ENTER': 60,
    'HIGH_CONFIDENCE': 70,
    
    # Risk Management
    'STOP_LOSS_ATR_MULTIPLIER': 2.0,
    'TAKE_PROFIT_ATR_MULTIPLIER': 3.0,
    'MIN_RISK_REWARD_RATIO': 1.5,
}

# Parámetros de detección de tendencias
TREND_PARAMS = {
    'HIGHS_LOWS_PERIOD': 20,
    'SLOPE_PERIOD': 20,
    'SUPPORT_RESISTANCE_WINDOW': 20,
    'NUM_SR_LEVELS': 3,
    'SR_TOLERANCE': 0.01,  # 1% de tolerancia
    'SLOPE_BULLISH_THRESHOLD': 0.5,
    'SLOPE_BEARISH_THRESHOLD': -0.5,
}

# Configuración de datos de mercado
MARKET_DATA_CONFIG = {
    'DEFAULT_PERIOD': '6mo',
    'DEFAULT_INTERVAL': '1d',
    
    # Períodos disponibles
    'AVAILABLE_PERIODS': ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', 'max'],
    
    # Intervalos disponibles
    'AVAILABLE_INTERVALS': ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo'],
}

# Activos predefinidos
PREDEFINED_ASSETS = {
    'CRYPTO': [
        'BTC-USD', 'ETH-USD', 'BNB-USD', 'XRP-USD', 'ADA-USD',
        'SOL-USD', 'DOGE-USD', 'DOT-USD', 'MATIC-USD', 'AVAX-USD'
    ],
    'STOCKS': [
        'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA',
        'META', 'NVDA', 'JPM', 'V', 'WMT'
    ],
    'INDICES': [
        '^GSPC',  # S&P 500
        '^DJI',   # Dow Jones
        '^IXIC',  # NASDAQ
        '^RUT',   # Russell 2000
        '^VIX',   # VIX Volatility Index
    ],
    'FOREX': [
        'EURUSD=X',  # Euro/USD
        'GBPUSD=X',  # British Pound/USD
        'JPYUSD=X',  # Japanese Yen/USD
        'AUDUSD=X',  # Australian Dollar/USD
    ]
}

# Configuración de visualización
DISPLAY_CONFIG = {
    'SHOW_COLORS': True,
    'SHOW_DETAILED_ANALYSIS': True,
    'DECIMAL_PLACES': 2,
}
