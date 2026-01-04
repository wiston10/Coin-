# 📈 Sistema de Análisis de Trading Automatizado

Sistema completo de análisis técnico que detecta automáticamente señales de **COMPRA** y **VENTA** en mercados financieros (acciones, criptomonedas, ETFs, etc.).

## 🎯 Características

### Análisis de Patrones de Velas Japonesas
- **Martillo (Hammer)** - Señal alcista de reversión
- **Estrella Fugaz (Shooting Star)** - Señal bajista de reversión
- **Doji** - Señal de indecisión del mercado
- **Envolvente Alcista/Bajista** - Señales fuertes de reversión
- **Estrella de la Mañana/Tarde** - Patrones de tres velas
- **Tres Soldados Blancos/Cuervos Negros** - Tendencias fuertes

### Indicadores Técnicos
- **RSI (Índice de Fuerza Relativa)** - Detecta sobrecompra/sobreventa
- **MACD** - Convergencia/Divergencia de medias móviles
- **Bandas de Bollinger** - Volatilidad y niveles extremos
- **Medias Móviles** (SMA, EMA) - Tendencias del mercado
- **Estocástico** - Momentum del precio
- **ATR** - Volatilidad del mercado
- **ADX** - Fuerza de la tendencia
- **OBV** - Volumen acumulado
- **Ichimoku Cloud** - Sistema completo de trading

### Detección de Tendencias
- Análisis de tendencia alcista/bajista/lateral
- Identificación de soportes y resistencias
- Cálculo de fuerza de tendencia (0-100)
- Detección de máximos y mínimos

### Motor de Señales de Trading
- **Señales automáticas**: BUY / SELL / HOLD
- **Nivel de confianza** (0-100%)
- **Niveles de entrada, Stop Loss y Take Profit**
- **Risk/Reward ratio** calculado automáticamente
- Análisis de condiciones del mercado
- Recomendaciones basadas en múltiples factores

## 📦 Instalación

### 1. Clonar o descargar el proyecto

```bash
cd /Users/wistonnavarroaroca/Documents/coin
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

O instalar manualmente:

```bash
pip install yfinance pandas numpy colorama
```

## 🚀 Uso

### Método 1: Launcher (Recomendado)

```bash
python3 launcher.py
```

Selecciona entre:
1. 🖥️ **Interfaz Gráfica (GUI)** - Con auto-actualización cada 2 minutos
2. 💻 Interfaz de Terminal (CLI)
3. 📝 Ejemplo Rápido
4. 🎓 Ejemplos Avanzados

### Método 2: Interfaz Gráfica Directa ⭐ NUEVO

```bash
python3 run_gui.py
```

**Características de la GUI:**
- ✅ **Auto-actualización cada 2 minutos** (configurable 1-60 min)
- ✅ Visualización completa con gráficos en tiempo real
- ✅ Cambio de intervalos y períodos en vivo
- ✅ Panel de señales con nivel de confianza visual
- ✅ Indicadores técnicos completos
- ✅ Comparación de múltiples activos
- ✅ Log de actividad en tiempo real

### Método 3: Terminal Interactiva

```bash
python3 trading_app.py
```

### Menú interactivo (CLI)

La aplicación de terminal ofrece 4 opciones:

1. **Analizar un activo** - Análisis detallado de un símbolo específico
2. **Comparar múltiples activos** - Tabla comparativa de varios símbolos
3. **Analizar criptomonedas populares** - BTC, ETH, BNB, ADA, SOL
4. **Analizar acciones populares** - AAPL, GOOGL, MSFT, TSLA, AMZN

### Ejemplos de símbolos válidos

#### Criptomonedas
- `BTC-USD` - Bitcoin
- `ETH-USD` - Ethereum
- `BNB-USD` - Binance Coin
- `ADA-USD` - Cardano
- `SOL-USD` - Solana
- `DOGE-USD` - Dogecoin

#### Acciones de EE.UU.
- `AAPL` - Apple
- `GOOGL` - Google/Alphabet
- `MSFT` - Microsoft
- `TSLA` - Tesla
- `AMZN` - Amazon
- `META` - Meta/Facebook
- `NVDA` - NVIDIA

#### Índices
- `^GSPC` - S&P 500
- `^DJI` - Dow Jones
- `^IXIC` - NASDAQ

## 📊 Ejemplo de salida

```
================================================================================
                           ANÁLISIS DE TRADING                                
================================================================================
Activo: BTC-USD
Fecha: 2025-12-07 10:30:45
Precio actual: $42,150.50
================================================================================

🎯 SEÑAL: 📈 COMPRAR
Confianza: 78.5%
[████████████████████████████████░░░░░░░░]

✓ RECOMENDACIÓN: Entrar en la operación

--------------------------------------------------------------------------------

📊 CONDICIONES DEL MERCADO:
   Tendencia: STRONG_BULLISH
   Fase: TENDENCIA ALCISTA
   Volatilidad: MEDIA (2.3%)
   Volumen: ALTO
   Fuerza de tendencia: FUERTE
   ADX: 32.5

🎯 NIVELES DE TRADING:
   Entrada: $42,150.50
   Stop Loss: $40,800.00
   Take Profit: $44,200.00
   Riesgo: $1,350.50
   Recompensa: $2,049.50
   Risk/Reward: 1.52:1

📋 RAZONES DE LA SEÑAL:
   1. Patrón alcista detectado: Bullish Engulfing
   2. MACD en señal alcista
   3. Tendencia alcista fuerte
   4. RSI en sobreventa (28.5)

🔧 DETALLES TÉCNICOS:
   Patrón de vela: Bullish Engulfing (BULLISH)
   RSI: 28.5 - OVERSOLD
   MACD: BULLISH
   Bandas de Bollinger: OVERSOLD
   Tendencia general: STRONG_BULLISH
   Fuerza de tendencia: 82/100
   Soportes: $40,500, $39,800, $38,900
   Resistencias: $44,200, $45,600, $47,100

================================================================================
```

## 🏗️ Estructura del Proyecto

```
coin/
├── candle_patterns.py       # Detector de patrones de velas
├── technical_indicators.py  # Cálculo de indicadores técnicos
├── trend_detector.py        # Detector de tendencias
├── trading_signals.py       # Motor de señales de trading
├── trading_app.py           # Aplicación principal
├── requirements.txt         # Dependencias
└── README.md               # Documentación
```

## 🔧 Uso Programático

### Analizar un activo

```python
from trading_app import TradingAnalyzer

analyzer = TradingAnalyzer()
result = analyzer.analyze_asset('BTC-USD', period='6mo', interval='1d')

print(f"Señal: {result['signal']['signal']}")
print(f"Confianza: {result['signal']['confidence']}%")
```

### Comparar múltiples activos

```python
symbols = ['BTC-USD', 'ETH-USD', 'AAPL', 'TSLA']
analyzer.compare_assets(symbols)
```

### Obtener datos específicos

```python
from technical_indicators import TechnicalIndicators
import yfinance as yf

# Obtener datos
df = yf.Ticker('BTC-USD').history(period='6mo')

# Calcular indicadores
df = TechnicalIndicators.calculate_all_indicators(df)

# Acceder a indicadores
print(f"RSI: {df['RSI'].iloc[-1]}")
print(f"MACD: {df['MACD'].iloc[-1]}")
```

## 📈 Interpretación de Señales

### Señal COMPRAR (BUY)
- **Confianza > 70%**: Señal fuerte de compra
- **Confianza 60-70%**: Señal moderada
- **Confianza < 60%**: Señal débil (considerar esperar)

### Señal VENDER (SELL)
- **Confianza > 70%**: Señal fuerte de venta
- **Confianza 60-70%**: Señal moderada
- **Confianza < 60%**: Señal débil (considerar esperar)

### Señal MANTENER (HOLD)
- Sin señal clara de compra o venta
- Mercado en consolidación o transición

## ⚠️ Advertencias

1. **Este sistema es una herramienta de análisis**, NO es asesoría financiera
2. **Siempre haz tu propia investigación** antes de invertir
3. **Los mercados son impredecibles** - ningún sistema garantiza ganancias
4. **Usa Stop Loss** - protege tu capital
5. **Gestiona el riesgo** - no inviertas más de lo que puedes perder
6. **Practica primero** - usa cuentas demo antes de operar con dinero real

## 🎓 Conceptos Clave

### Risk/Reward Ratio
- **> 2:1**: Excelente - El potencial de ganancia duplica el riesgo
- **1.5:1 - 2:1**: Bueno - Ratio aceptable
- **< 1.5:1**: Evitar - Riesgo demasiado alto para la recompensa

### RSI (Relative Strength Index)
- **> 70**: Sobrecomprado - Posible corrección bajista
- **< 30**: Sobrevendido - Posible rebote alcista
- **50**: Neutral

### MACD
- **Línea MACD > Línea Señal**: Momentum alcista
- **Línea MACD < Línea Señal**: Momentum bajista
- **Histograma positivo creciente**: Fuerza alcista aumentando

### Tendencia
- **STRONG_BULLISH**: Tendencia alcista fuerte
- **BULLISH**: Tendencia alcista
- **SIDEWAYS**: Mercado lateral (consolidación)
- **BEARISH**: Tendencia bajista
- **STRONG_BEARISH**: Tendencia bajista fuerte

## 🛠️ Personalización

Puedes modificar los parámetros en `trading_signals.py`:

```python
# Cambiar confianza mínima para entrar
should_enter = self.signal_engine.should_enter_trade(
    signal_data, 
    min_confidence=70,  # Cambiar este valor
    min_risk_reward=2.0  # Cambiar este valor
)
```

## 📝 Licencia

Este proyecto es de código abierto y está disponible para uso personal y educativo.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Haz un fork del proyecto
2. Crea una rama para tu feature
3. Haz commit de tus cambios
4. Haz push a la rama
5. Abre un Pull Request

## 📧 Soporte

Para preguntas o problemas, abre un issue en el repositorio.

---

**Disclaimer**: Este software se proporciona "tal cual", sin garantías de ningún tipo. El autor no se hace responsable de pérdidas financieras derivadas del uso de este sistema.
