"""
GUÍA RÁPIDA DE USO - Sistema de Análisis de Trading
"""

# ============================================================================
# INSTALACIÓN
# ============================================================================

# 1. Instalar dependencias
pip3 install -r requirements.txt

# ============================================================================
# USO BÁSICO
# ============================================================================

# OPCIÓN 1: Usar la aplicación interactiva
python3 trading_app.py

# OPCIÓN 2: Usar desde código Python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.core.trading_app import TradingAnalyzer

analyzer = TradingAnalyzer()

# Analizar Bitcoin
result = analyzer.analyze_asset('BTC-USD', period='1y', interval='1d')

# ============================================================================
# EJEMPLOS DE USO
# ============================================================================

# 1. ANALIZAR UNA CRIPTOMONEDA
analyzer.analyze_asset('BTC-USD', period='1y')  # Bitcoin
analyzer.analyze_asset('ETH-USD', period='1y')  # Ethereum
analyzer.analyze_asset('SOL-USD', period='6mo') # Solana

# 2. ANALIZAR UNA ACCIÓN
analyzer.analyze_asset('AAPL', period='1y')     # Apple
analyzer.analyze_asset('TSLA', period='1y')     # Tesla
analyzer.analyze_asset('NVDA', period='6mo')    # NVIDIA

# 3. COMPARAR MÚLTIPLES ACTIVOS
crypto_list = ['BTC-USD', 'ETH-USD', 'SOL-USD', 'ADA-USD']
analyzer.compare_assets(crypto_list, period='1y')

stocks_list = ['AAPL', 'GOOGL', 'MSFT', 'TSLA']
analyzer.compare_assets(stocks_list, period='1y')

# 4. USAR DIFERENTES INTERVALOS DE TIEMPO
analyzer.analyze_asset('BTC-USD', period='1mo', interval='1h')   # Últimos 30 días, velas de 1 hora
analyzer.analyze_asset('AAPL', period='5d', interval='15m')      # Últimos 5 días, velas de 15 minutos
analyzer.analyze_asset('ETH-USD', period='2y', interval='1d')    # Últimos 2 años, velas diarias

# ============================================================================
# PERÍODOS DISPONIBLES
# ============================================================================
# '1d'   - 1 día
# '5d'   - 5 días
# '1mo'  - 1 mes
# '3mo'  - 3 meses
# '6mo'  - 6 meses
# '1y'   - 1 año
# '2y'   - 2 años
# '5y'   - 5 años
# 'max'  - Máximo disponible

# ============================================================================
# INTERVALOS DISPONIBLES
# ============================================================================
# '1m'   - 1 minuto
# '5m'   - 5 minutos
# '15m'  - 15 minutos
# '30m'  - 30 minutos
# '1h'   - 1 hora
# '1d'   - 1 día (recomendado)
# '1wk'  - 1 semana
# '1mo'  - 1 mes

# ============================================================================
# SÍMBOLOS COMUNES
# ============================================================================

# CRIPTOMONEDAS (agregar -USD al final)
# BTC-USD  - Bitcoin
# ETH-USD  - Ethereum
# BNB-USD  - Binance Coin
# XRP-USD  - Ripple
# ADA-USD  - Cardano
# SOL-USD  - Solana
# DOGE-USD - Dogecoin
# MATIC-USD - Polygon
# DOT-USD  - Polkadot
# AVAX-USD - Avalanche

# ACCIONES (usar ticker directo)
# AAPL  - Apple
# GOOGL - Google
# MSFT  - Microsoft
# AMZN  - Amazon
# TSLA  - Tesla
# META  - Meta/Facebook
# NVDA  - NVIDIA
# JPM   - JPMorgan Chase
# V     - Visa
# WMT   - Walmart

# ÍNDICES (agregar ^ al inicio)
# ^GSPC - S&P 500
# ^DJI  - Dow Jones
# ^IXIC - NASDAQ

# ============================================================================
# EJEMPLO COMPLETO
# ============================================================================

from trading_app import TradingAnalyzer

# Crear analizador
analyzer = TradingAnalyzer()

# Analizar Bitcoin con período de 1 año
print("Analizando Bitcoin...")
btc_result = analyzer.analyze_asset('BTC-USD', period='1y', interval='1d')

if btc_result:
    signal = btc_result['signal']
    
    print(f"\n📊 RESULTADO DEL ANÁLISIS:")
    print(f"Señal: {signal['signal']}")
    print(f"Confianza: {signal['confidence']}%")
    print(f"Precio actual: ${signal['details']['current_price']}")
    
    if btc_result['levels']:
        levels = btc_result['levels']
        print(f"\n💰 NIVELES DE TRADING:")
        print(f"Entrada: ${levels['entry']}")
        print(f"Stop Loss: ${levels['stop_loss']}")
        print(f"Take Profit: ${levels['take_profit']}")
        print(f"Risk/Reward: {levels['risk_reward_ratio']}:1")
    
    print(f"\n📈 CONDICIONES DEL MERCADO:")
    market = btc_result['market_condition']
    print(f"Tendencia: {market['trend']}")
    print(f"Fase: {market['market_phase']}")
    print(f"Volatilidad: {market['volatility']}")

# ============================================================================
# NOTAS IMPORTANTES
# ============================================================================

# 1. Para análisis completo necesitas al menos 200 velas
#    - Si usas interval='1d', usa period='1y' o más
#    - Si usas interval='1h', usa period='6mo' o más

# 2. Confianza de la señal:
#    - > 70%: Señal fuerte
#    - 60-70%: Señal moderada
#    - < 60%: Señal débil (no recomendado entrar)

# 3. Risk/Reward ratio:
#    - > 2:1: Excelente
#    - 1.5:1 - 2:1: Bueno
#    - < 1.5:1: Evitar

# 4. Siempre usa Stop Loss para proteger tu capital

# 5. Este sistema es una HERRAMIENTA, no asesoría financiera
#    Haz tu propia investigación antes de invertir

# ============================================================================
# SOLUCIÓN DE PROBLEMAS
# ============================================================================

# Problema: "Datos insuficientes"
# Solución: Usa un período más largo (1y en vez de 6mo)

# Problema: "No se pudieron obtener datos"
# Solución: Verifica que el símbolo sea correcto (BTC-USD, no BTC)

# Problema: Error de importación
# Solución: pip3 install -r requirements.txt

# ============================================================================
