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
Coin-/
├── iniciar.command        # ⭐ Doble clic (Mac): instala todo e inicia el dashboard
├── run_gui.py             # Inicia el dashboard web (abre el navegador)
├── main.py                # Menú: dashboard o interfaz de terminal
├── requirements.txt       # Dependencias
├── .env.example           # Plantilla de configuración (cópiala a .env)
│
├── config/
│   ├── broker_apis.py     # API keys opcionales (Alpha Vantage, Finnhub...)
│   └── settings.py        # Parámetros de indicadores y señales
│
├── src/
│   ├── core/              # trading_app (terminal), trading_signals, live_trading
│   ├── indicators/        # RSI, MACD, Bollinger, ATR, ADX, patrones de velas, tendencia
│   ├── strategies/        # bounce_strategy.py (estrategia de rebotes)
│   ├── data_sources/      # exchanges (ccxt), yfinance, multi-broker, agregador, Binomo
│   ├── gui/dashboard.py   # Servidor web Flask + API
│   ├── trading/           # Bot Selenium (desactivado por defecto)
│   ├── webhooks/          # Alertas Telegram/Discord/Slack
│   └── env_loader.py      # Lee el archivo .env
│
├── templates/             # Páginas HTML del dashboard
├── tests/                 # Tests automáticos (sin red)
├── scripts/               # Comprobaciones manuales de conexión (requieren internet)
├── examples/              # Ejemplos de uso desde código
└── docs/                  # Guías
```

## 🔐 Configuración (archivo `.env`)

Las claves ya **no** van dentro del código. Copia la plantilla y rellénala:

```bash
cp .env.example .env
```

| Variable | Para qué sirve | Por defecto |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID` | Alertas a tu grupo de Telegram | vacío (alertas apagadas) |
| `DASHBOARD_HOST` / `DASHBOARD_PORT` | Dónde escucha el dashboard | `127.0.0.1` / `8080` |
| `ENABLE_LIVE_TRADING` | Permite que `/api/trade` opere con dinero real vía Selenium | `false` |
| `ALLOW_SIMULATED_DATA` | Permite velas simuladas (aleatorias) de Binomo. Nunca se usan para señales | `false` |

`.env` está en `.gitignore`, así que no se sube a GitHub.

### Tests

```bash
python3 -m unittest discover -s tests -v
```

## 🚀 Inicio Rápido

### Opción A — Mac, sin terminal (recomendado)

Haz **doble clic en `iniciar.command`**. La primera vez crea un entorno virtual
(`.venv`), instala las dependencias (tarda unos minutos) y abre el dashboard en el
navegador. Las siguientes veces arranca directamente.

> Si macOS dice que no puede abrirlo: clic derecho → **Abrir** → **Abrir**.
> Si dice "permiso denegado", abre Terminal en la carpeta y ejecuta `chmod +x iniciar.command`.

### Opción B — Terminal

```bash
cd ~/Documents/Coin-
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 run_gui.py          # dashboard web → se abre http://localhost:8080
# o
python3 main.py             # menú: dashboard o interfaz de terminal
```

Si el puerto 8080 está ocupado, `run_gui.py` usa automáticamente el siguiente libre.

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

En la carpeta `docs/`:
- [MULTI_BROKER_SETUP.md](docs/MULTI_BROKER_SETUP.md) — sistema multi-broker y API keys
- [ESTRATEGIA_REBOTES.md](docs/ESTRATEGIA_REBOTES.md) — estrategia de trading
- [WEBHOOK_GUIDE.md](docs/WEBHOOK_GUIDE.md) — alertas por Telegram/Discord/Slack
- [MONITOREO_AUTOMATICO.md](docs/MONITOREO_AUTOMATICO.md), [MODO_TIEMPO_REAL.md](docs/MODO_TIEMPO_REAL.md)
- [GUIA_COMPLETA_GUI.md](docs/GUIA_COMPLETA_GUI.md), [WEB_SCRAPING_GUIDE.md](docs/WEB_SCRAPING_GUIDE.md), [BINOMO_INTEGRATION.md](docs/BINOMO_INTEGRATION.md)

## 🔧 Configuración

### Configuración Básica (Gratuito)
Solo requiere las dependencias instaladas. Usa yfinance y exchanges gratuitos.

```bash
# Ya funciona después de pip install -r requirements.txt
python3 run_gui.py
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

Ver [MULTI_BROKER_SETUP.md](docs/MULTI_BROKER_SETUP.md) para configuración completa.

## 📝 Ejemplos de Uso

### Desde Python
```python
from src.data_sources.hybrid_data_source import HybridDataSource
from src.indicators.technical_indicators import calculate_adaptive_indicators
from src.strategies.bounce_strategy import analyze_bounce_opportunity

ds = HybridDataSource()
df = ds.get_live_data('BTC-USD', '5m')
df = calculate_adaptive_indicators(df, '5m')
analysis = analyze_bounce_opportunity(df, interval='5m')
print(analysis['signal'], analysis['confidence'])
```

### API del dashboard
```bash
curl http://localhost:8080/api/health
curl "http://localhost:8080/api/analyze/BTC-USD?interval=5m"
curl http://localhost:8080/api/price-quality/AAPL
```

## 🧪 Tests

```bash
python3 -m unittest discover -s tests -v   # tests automáticos (sin internet)
python3 scripts/check_exchanges.py         # comprueba conexión con exchanges
python3 scripts/check_multi_broker.py      # comprueba el sistema multi-broker
```

## ⚠️ Disclaimer

Este sistema es para fines educativos y de investigación. No constituye asesoramiento
financiero. La estrategia no está validada con backtesting: no operes con dinero real
basándote solo en sus señales.

## 📄 Licencia

Proyecto de código abierto para análisis de trading.

---

**¿Necesitas ayuda?** Consulta la documentación en la carpeta `docs/` o revisa los ejemplos en `examples/`.
