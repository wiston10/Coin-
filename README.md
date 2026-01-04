# 📈 Sistema de Análisis de Trading Automatizado

Sistema profesional de análisis técnico con **agregación multi-fuente de datos** para detectar automáticamente señales de trading en mercados financieros.

## ✨ Características Destacadas (v2.0)

### 🌐 Multi-Source Data Aggregation (NUEVO)
- **14 fuentes de datos** para máxima precisión:
  - 6 Crypto Exchanges (Binance, Bybit, Coinbase, OKX, Kraken, KuCoin)
  - 7 Financial APIs (Alpha Vantage, Finnhub, Twelve Data, IEX, Polygon, Marketstack, Fixer)
  - yfinance (Yahoo Finance) - Gratuito

### 🎯 Agregación Inteligente
- Detección automática de outliers (Z-score)
- 3 métodos de agregación (simple, weighted, median)
- Scoring de confianza 0-100%
- Quality rating: Excellent, Good, Fair, Poor

### 📊 Assets Soportados
- **Cryptocurrency**: BTC, ETH, SOL, ADA, etc. (Tiempo real)
- **Stocks**: AAPL, MSFT, GOOGL, TSLA, etc.
- **Forex**: EUR-USD, GBP-USD, JPY-USD, etc.
- **Indices**: SPY, QQQ, DIA, etc.

## 📂 Estructura del Proyecto

```
coin/
├── main.py                 # Punto de entrada principal
├── run_gui.py             # Inicio rápido dashboard web
├── run_dashboard.py       # Dashboard web (alternativo)
├── requirements.txt       # Dependencias del proyecto
├── README.md             # Esta documentación
├── .gitignore           # Archivos ignorados por git
│
├── config/              # ✨ NUEVO: Configuración
│   ├── broker_apis.py          # Config de 7 APIs financieras
│   ├── settings.py             # Configuración principal
│   └── configurar_telegram.py  # Setup de Telegram
│
├── src/                 # Código fuente principal
│   ├── __init__.py
│   ├── core/           # Módulos principales
│   │   ├── trading_app.py      # App de terminal
│   │   ├── trading_signals.py  # Motor de señales
│   │   └── live_trading.py     # Trading en vivo
│   │
│   ├── indicators/     # Indicadores técnicos
│   │   ├── candle_patterns.py      # Patrones de velas
│   │   ├── technical_indicators.py # RSI, MACD, etc.
│   │   └── trend_detector.py       # Detector de tendencias
│   │
│   ├── strategies/     # Estrategias de trading
│   │   └── bounce_strategy.py  # Estrategia de rebotes
│   │
│   ├── data_sources/   # ✨ MEJORADO: Fuentes de datos
│   │   ├── market_data_sources.py   # Yahoo Finance, etc.
│   │   ├── hybrid_data_source.py    # Orchestrator principal
│   │   ├── web_scraper.py           # 6 crypto exchanges
│   │   ├── binomo_scraper.py        # Scraper Binomo
│   │   ├── multi_broker_client.py   # ✨ NUEVO: Cliente multi-API
│   │   └── price_aggregator.py      # ✨ NUEVO: Agregación inteligente
│   │
│   ├── gui/            # Interfaz gráfica
│   │   ├── trading_gui.py  # GUI principal
│   │   └── dashboard.py    # Dashboard web (mejorado)
│   │
│   └── webhooks/       # Webhooks y notificaciones
│       ├── webhook_notifier.py  # Notificador
│       ├── webhook_config.py    # Configuración
│       └── setup_webhooks.py    # Setup webhooks
│
├── docs/               # ✨ NUEVO: Documentación
│   ├── MULTI_BROKER_SETUP.md    # Guía multi-broker
│   ├── SISTEMA_COMPLETO.md      # Resumen completo
│   ├── WEB_SCRAPING_GUIDE.md    # Guía de scraping
│   └── WEBHOOK_GUIDE.md         # Guía de webhooks
│
├── examples/           # Ejemplos de uso
│   ├── quick_start.py          # Inicio rápido
│   ├── ejemplo_rebotes.py      # Ejemplo rebotes
│   ├── ejemplos_avanzados.py   # Ejemplos avanzados
│   └── ...
│
├── tests/              # Tests unitarios
│   ├── test_multi_broker.py    # ✨ NUEVO: Test multi-broker
│   └── test_exchanges.py       # Test exchanges
````
│   ├── test_example.py
│   └── test_telegram.py
│
├── docs/               # Documentación
│   ├── README.md
│   ├── RESUMEN_PROYECTO.md
│   ├── ESTRATEGIA_REBOTES.md
│   ├── GUI_README.md
│   ├── GUIA_COMPLETA_GUI.md
│   ├── MODO_TIEMPO_REAL.md
│   ├── MONITOREO_AUTOMATICO.md
│   ├── WEBHOOK_GUIDE.md
│   ├── WEB_SCRAPING_GUIDE.md
│   ├── BINOMO_INTEGRATION.md
│   └── ... (más documentación)
│
└── templates/          # Templates HTML
    └── dashboard.html
```

## 🚀 Inicio Rápido

### Instalación

```bash
# 1. Clonar el repositorio
git clone <tu-repositorio>
cd coin

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. (Opcional pero RECOMENDADO) Configurar API Keys
# Edita config/broker_apis.py con tus claves API
# Ver MULTI_BROKER_SETUP.md para más detalles
nano config/broker_apis.py
```

### Uso Básico

**Opción 1: Dashboard Web (Recomendado) 🌟**
```bash
python3 dashboard.py
```
Abre tu navegador en: `http://localhost:8080`

**Opción 2: Test Rápido del Sistema Multi-Broker**
```bash
python3 test_multi_broker.py
```

**Opción 3: Uso Programático**
```python
from src.data_sources.hybrid_data_source import HybridDataSource

ds = HybridDataSource()

# Obtener precio agregado de múltiples fuentes
result = ds.get_aggregated_price('AAPL')
print(f"Precio: ${result['price']:.2f}")
print(f"Confianza: {result['confidence']:.1%} - {result['quality']}")
print(f"Fuentes: {result['sources_used']}")
```

## 🎯 Características Principales

### ✨ Sistema Multi-Broker (v2.0 - NUEVO)
- **14 fuentes de datos**: 6 exchanges + 7 APIs + yfinance
- **Agregación inteligente**: Detección de outliers, múltiples métodos
- **Scoring de confianza**: 0-100% basado en spread, std dev, sources
- **Quality rating**: Excellent (≥90%), Good (≥75%), Fair (≥60%), Poor (<60%)
- **Fallback automático**: Si una fuente falla, usa la siguiente

### 📊 Análisis Técnico Completo
- **12+ Indicadores**: RSI, MACD, Bollinger Bands, Estocástico, ATR, ADX, OBV, Ichimoku
- **Patrones de Velas**: Martillo, Estrella Fugaz, Doji, Envolventes, etc.
- **Detección de Tendencias**: Alcista, Bajista, Lateral con fuerza 0-100
- **Soportes y Resistencias**: Identificación automática de niveles clave

### 🎲 Motor de Señales Inteligente
- Señales automáticas: **BUY** / **SELL** / **HOLD**
- Nivel de confianza calculado (0-100%)
- Niveles automáticos de Stop Loss y Take Profit
- Risk/Reward ratio calculado

### 🖥️ Múltiples Interfaces
- **Dashboard Web**: Interfaz web moderna con actualización en tiempo real
- **CLI**: Terminal interactiva con menús
- **API REST**: Endpoints para integración externa

### 🔔 Sistema de Notificaciones
- Webhooks configurables (Discord, Slack, Generic)
- Integración con Telegram Bot
- Alertas personalizables por confianza mínima
- Notificaciones automáticas de señales

## 📚 Documentación

### Documentación Principal
- **[MULTI_BROKER_SETUP.md](MULTI_BROKER_SETUP.md)** - 🌟 Guía completa del sistema multi-broker
- **[SISTEMA_COMPLETO.md](SISTEMA_COMPLETO.md)** - Resumen del sistema completo
- [WEB_SCRAPING_GUIDE.md](WEB_SCRAPING_GUIDE.md) - Guía de web scraping
- [WEBHOOK_GUIDE.md](WEBHOOK_GUIDE.md) - Configuración de webhooks
- [ESTRATEGIA_REBOTES.md](ESTRATEGIA_REBOTES.md) - Estrategia de trading

### Documentación Adicional
Consulta la carpeta `docs/` para más documentación:
- Modo tiempo real
- Monitoreo automático
- Integración con Binomo
- GUI completa

## 🔧 Configuración

### Configuración Básica (Gratuito)
Solo requiere las dependencias instaladas. Usa yfinance y exchanges gratuitos.

```bash
# Ya funciona después de pip install -r requirements.txt
python3 dashboard.py
```

**Confianza típica**: 
- Crypto: 75-85% (Good) ✅
- Stocks/Forex: 40-50% (Poor) ⚠️

### Configuración Avanzada (Recomendado)
Agregar API keys para mejorar la precisión:

1. Registrarse en APIs gratuitas:
   - [Alpha Vantage](https://www.alphavantage.co/support/#api-key) (25 req/día)
   - [Finnhub](https://finnhub.io/register) (60 req/min)

2. Editar `config/broker_apis.py`:
```python
ALPHA_VANTAGE_API_KEY = "TU_CLAVE_AQUI"
FINNHUB_API_KEY = "TU_CLAVE_AQUI"
```

**Confianza típica**: 
- Crypto: 80-90% (Excellent) ⭐
- Stocks/Forex: 70-85% (Good-Excellent) ⭐

Ver [MULTI_BROKER_SETUP.md](MULTI_BROKER_SETUP.md) para configuración completa.

## 📝 Ejemplos de Uso

### Test del Sistema Multi-Broker
```bash
python3 test_multi_broker.py
```

### Desde Python
```python
from src.data_sources.hybrid_data_source import HybridDataSource

ds = HybridDataSource()

# Precio agregado con calidad
result = ds.get_aggregated_price('AAPL')

# Datos históricos
df = ds.get_historical_data('BTC-USD', '5m')

# Análisis completo
from src.strategies.bounce_strategy import analyze_bounce_opportunity
analysis = analyze_bounce_opportunity(df, 'BTC-USD')
```

### Dashboard API
```bash
# Precio con calidad
curl http://localhost:8080/api/price-quality/AAPL

# Estadísticas de brokers
curl http://localhost:8080/api/broker-stats

# Análisis completo
curl http://localhost:8080/api/analyze/BTC-USD?interval=5m
```

## 🧪 Tests

```bash
# Test sistema multi-broker
python3 test_multi_broker.py

# Test exchanges
python3 test_exchanges.py
```

## 📦 Dependencias

- **yfinance**: Datos de mercado
- **pandas**: Análisis de datos
- **numpy**: Cálculos numéricos
- **matplotlib**: Gráficos
- **colorama**: Colores en terminal

## ⚠️ Disclaimer

Este sistema es para fines educativos y de investigación. No constituye asesoramiento financiero. Opera bajo tu propio riesgo.

## 📄 Licencia

Proyecto de código abierto para análisis de trading.

---

**¿Necesitas ayuda?** Consulta la documentación en la carpeta `docs/` o revisa los ejemplos en `examples/`.
