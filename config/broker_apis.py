"""
Configuración de APIs para múltiples brokers y mercados financieros
Agrega tus API keys aquí para mejorar la precisión de datos
"""

# ============================================================================
# ALPHA VANTAGE (Stocks, Forex, Crypto)
# ============================================================================
# Registro gratuito: https://www.alphavantage.co/support/#api-key
# Plan gratuito: 25 requests/día, 5 requests/minuto
ALPHA_VANTAGE_API_KEY = "demo"  # Reemplaza con tu API key
ALPHA_VANTAGE_ENABLED = False  # Cambiar a True cuando tengas tu API key

# ============================================================================
# FINNHUB (Stocks, Forex, Crypto)
# ============================================================================
# Registro gratuito: https://finnhub.io/register
# Plan gratuito: 60 requests/minuto
FINNHUB_API_KEY = "demo"  # Reemplaza con tu API key
FINNHUB_ENABLED = False  # Cambiar a True cuando tengas tu API key

# ============================================================================
# TWELVE DATA (Stocks, Forex, Crypto, Indices)
# ============================================================================
# Registro gratuito: https://twelvedata.com/pricing
# Plan gratuito: 800 requests/día
TWELVE_DATA_API_KEY = "demo"  # Reemplaza con tu API key
TWELVE_DATA_ENABLED = False  # Cambiar a True cuando tengas tu API key

# ============================================================================
# IEX CLOUD (Stocks principalmente)
# ============================================================================
# Registro: https://iexcloud.io/cloud-login#/register
# Plan gratuito: 50,000 requests/mes
IEX_CLOUD_TOKEN = "pk_demo"  # Reemplaza con tu token
IEX_CLOUD_ENABLED = False  # Cambiar a True cuando tengas tu token

# ============================================================================
# POLYGON.IO (Stocks, Forex, Crypto)
# ============================================================================
# Registro: https://polygon.io/
# Plan gratuito: 5 requests/minuto
POLYGON_API_KEY = "demo"  # Reemplaza con tu API key
POLYGON_ENABLED = False  # Cambiar a True cuando tengas tu API key

# ============================================================================
# MARKETSTACK (Stocks, Indices)
# ============================================================================
# Registro: https://marketstack.com/product
# Plan gratuito: 1,000 requests/mes
MARKETSTACK_API_KEY = "demo"  # Reemplaza con tu API key
MARKETSTACK_ENABLED = False  # Cambiar a True cuando tengas tu API key

# ============================================================================
# FIXER.IO / EXCHANGERATE-API (Solo Forex)
# ============================================================================
# Registro: https://fixer.io/ o https://www.exchangerate-api.com/
# Plan gratuito: 1,000-1,500 requests/mes
FIXER_API_KEY = "demo"  # Reemplaza con tu API key
FIXER_ENABLED = False  # Cambiar a True cuando tengas tu API key

# ============================================================================
# CONFIGURACIÓN GENERAL
# ============================================================================

# Timeout para requests (segundos)
API_TIMEOUT = 10

# Número de reintentos en caso de fallo
API_RETRIES = 2

# Delay entre reintentos (segundos)
RETRY_DELAY = 1

# Cache duration (segundos) - para evitar exceso de requests
CACHE_DURATION = 60

# Prioridad de fuentes (menor número = mayor prioridad)
# Ajusta según tu preferencia y plan de cada API
SOURCE_PRIORITY = {
    # Stocks
    'stocks': [
        'yfinance',       # 1. Yahoo Finance (gratis, sin límites)
        'alpha_vantage',  # 2. Alpha Vantage (25/día)
        'finnhub',        # 3. Finnhub (60/min)
        'twelve_data',    # 4. Twelve Data (800/día)
        'iex_cloud',      # 5. IEX Cloud (50k/mes)
        'polygon',        # 6. Polygon.io (5/min)
        'marketstack',    # 7. Marketstack (1000/mes)
    ],
    
    # Forex
    'forex': [
        'yfinance',       # 1. Yahoo Finance (gratis)
        'twelve_data',    # 2. Twelve Data (800/día)
        'alpha_vantage',  # 3. Alpha Vantage (25/día)
        'finnhub',        # 4. Finnhub (60/min)
        'fixer',          # 5. Fixer.io (1000/mes)
        'polygon',        # 6. Polygon.io (5/min)
    ],
    
    # Indices
    'indices': [
        'yfinance',       # 1. Yahoo Finance (gratis)
        'twelve_data',    # 2. Twelve Data (800/día)
        'alpha_vantage',  # 3. Alpha Vantage (25/día)
        'finnhub',        # 4. Finnhub (60/min)
        'marketstack',    # 5. Marketstack (1000/mes)
    ],
    
    # Crypto (ya usamos 6 exchanges, estas son adicionales)
    'crypto': [
        'exchanges',      # 1. 6 exchanges (Binance, Bybit, etc)
        'yfinance',       # 2. Yahoo Finance
        'twelve_data',    # 3. Twelve Data
        'alpha_vantage',  # 4. Alpha Vantage
        'finnhub',        # 5. Finnhub
        'polygon',        # 6. Polygon.io
    ]
}

# Configuración de agregación de datos
AGGREGATION_METHOD = 'weighted_average'  # 'simple_average', 'weighted_average', 'median'

# Pesos para weighted_average (basado en confiabilidad/precisión)
SOURCE_WEIGHTS = {
    'yfinance': 1.0,
    'exchanges': 1.0,
    'alpha_vantage': 0.95,
    'twelve_data': 0.95,
    'finnhub': 0.90,
    'iex_cloud': 0.90,
    'polygon': 0.85,
    'marketstack': 0.80,
    'fixer': 0.85,
}

# URLs base de las APIs
API_ENDPOINTS = {
    'alpha_vantage': 'https://www.alphavantage.co/query',
    'finnhub': 'https://finnhub.io/api/v1',
    'twelve_data': 'https://api.twelvedata.com',
    'iex_cloud': 'https://cloud.iexapis.com/stable',
    'polygon': 'https://api.polygon.io',
    'marketstack': 'http://api.marketstack.com/v1',
    'fixer': 'http://data.fixer.io/api',
}


def get_enabled_sources():
    """Retorna lista de fuentes habilitadas"""
    enabled = ['yfinance', 'exchanges']  # Siempre habilitadas
    
    if ALPHA_VANTAGE_ENABLED:
        enabled.append('alpha_vantage')
    if FINNHUB_ENABLED:
        enabled.append('finnhub')
    if TWELVE_DATA_ENABLED:
        enabled.append('twelve_data')
    if IEX_CLOUD_ENABLED:
        enabled.append('iex_cloud')
    if POLYGON_ENABLED:
        enabled.append('polygon')
    if MARKETSTACK_ENABLED:
        enabled.append('marketstack')
    if FIXER_ENABLED:
        enabled.append('fixer')
    
    return enabled


def get_api_config(source):
    """Retorna configuración de una fuente específica"""
    configs = {
        'alpha_vantage': {
            'api_key': ALPHA_VANTAGE_API_KEY,
            'enabled': ALPHA_VANTAGE_ENABLED,
            'endpoint': API_ENDPOINTS['alpha_vantage'],
            'rate_limit': 5,  # requests por minuto
        },
        'finnhub': {
            'api_key': FINNHUB_API_KEY,
            'enabled': FINNHUB_ENABLED,
            'endpoint': API_ENDPOINTS['finnhub'],
            'rate_limit': 60,
        },
        'twelve_data': {
            'api_key': TWELVE_DATA_API_KEY,
            'enabled': TWELVE_DATA_ENABLED,
            'endpoint': API_ENDPOINTS['twelve_data'],
            'rate_limit': 800,  # por día
        },
        'iex_cloud': {
            'api_key': IEX_CLOUD_TOKEN,
            'enabled': IEX_CLOUD_ENABLED,
            'endpoint': API_ENDPOINTS['iex_cloud'],
            'rate_limit': 50000,  # por mes
        },
        'polygon': {
            'api_key': POLYGON_API_KEY,
            'enabled': POLYGON_ENABLED,
            'endpoint': API_ENDPOINTS['polygon'],
            'rate_limit': 5,
        },
        'marketstack': {
            'api_key': MARKETSTACK_API_KEY,
            'enabled': MARKETSTACK_ENABLED,
            'endpoint': API_ENDPOINTS['marketstack'],
            'rate_limit': 1000,  # por mes
        },
        'fixer': {
            'api_key': FIXER_API_KEY,
            'enabled': FIXER_ENABLED,
            'endpoint': API_ENDPOINTS['fixer'],
            'rate_limit': 1000,  # por mes
        },
    }
    
    return configs.get(source, {})
