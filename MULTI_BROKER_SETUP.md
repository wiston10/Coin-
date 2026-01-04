# 🌐 Sistema Multi-Broker - Guía de Configuración

## 📋 Descripción

El sistema multi-broker agrega datos de **14 fuentes diferentes** para obtener la máxima precisión en precios:

### 🔗 Fuentes de Datos

#### Cryptocurrency (6 Exchanges)
- **Binance** - Exchange #1 global
- **Bybit** - Derivados y spot
- **Coinbase Advanced** - Exchange regulado US
- **OKX** - Trading avanzado
- **Kraken** - Exchange europeo
- **KuCoin** - Altcoins

#### Stocks, Forex & Indices (7 APIs + 1 Free)
- **yfinance** (Gratuito) - Yahoo Finance API
- **Alpha Vantage** - Stocks, Forex, Crypto
- **Finnhub** - Stocks en tiempo real
- **Twelve Data** - Multi-asset coverage
- **IEX Cloud** - US stocks
- **Polygon.io** - Market data profesional
- **Marketstack** - Stocks & indices
- **Fixer.io** - Forex rates

---

## 🎯 Características del Sistema

### ✨ Agregación Inteligente
- **Múltiples métodos**: Promedio simple, promedio ponderado, mediana
- **Detección de outliers**: Algoritmo Z-score (threshold 2.5)
- **Scoring de confianza**: 0.0 - 1.0 basado en:
  - Spread porcentual entre fuentes
  - Desviación estándar
  - Número de fuentes disponibles

### 📊 Calidad de Datos
| Rating | Confianza | Descripción |
|--------|-----------|-------------|
| **Excellent** | ≥ 90% | Máxima precisión, múltiples fuentes concordantes |
| **Good** | ≥ 75% | Buena precisión, fuentes mayormente alineadas |
| **Fair** | ≥ 60% | Precisión aceptable, algo de dispersión |
| **Poor** | < 60% | Baja precisión, pocas fuentes o alta dispersión |

---

## 🔧 Configuración de API Keys

### 1. Alpha Vantage (Stocks, Forex, Crypto)
📝 **Registro**: https://www.alphavantage.co/support/#api-key
- ✅ **Plan gratuito**: 25 requests/día
- 💰 **Premium**: Desde $49.99/mes (75 req/min)

```python
# config/broker_apis.py
ALPHA_VANTAGE_API_KEY = "TU_CLAVE_AQUI"
```

### 2. Finnhub (Stocks, Forex, Crypto)
📝 **Registro**: https://finnhub.io/register
- ✅ **Plan gratuito**: 60 requests/min
- 💰 **Premium**: Desde $59.99/mes

```python
FINNHUB_API_KEY = "TU_CLAVE_AQUI"
```

### 3. Twelve Data (Multi-asset)
📝 **Registro**: https://twelvedata.com/pricing
- ✅ **Plan gratuito**: 800 requests/día
- 💰 **Premium**: Desde $79/mes

```python
TWELVE_DATA_API_KEY = "TU_CLAVE_AQUI"
```

### 4. IEX Cloud (US Stocks)
📝 **Registro**: https://iexcloud.io/console/home
- ✅ **Plan gratuito**: 50,000 mensajes/mes
- 💰 **Premium**: Desde $9/mes

```python
IEX_CLOUD_API_KEY = "TU_CLAVE_AQUI"
```

### 5. Polygon.io (Market Data Profesional)
📝 **Registro**: https://polygon.io/dashboard/signup
- ✅ **Plan gratuito**: No disponible
- 💰 **Starter**: $29/mes (5 req/min, delayed data)
- 💰 **Developer**: $99/mes (100 req/min, real-time)

```python
POLYGON_API_KEY = "TU_CLAVE_AQUI"
```

### 6. Marketstack (Stocks & Indices)
📝 **Registro**: https://marketstack.com/product
- ✅ **Plan gratuito**: 1,000 requests/mes
- 💰 **Premium**: Desde $49/mes

```python
MARKETSTACK_API_KEY = "TU_CLAVE_AQUI"
```

### 7. Fixer.io (Forex Rates)
📝 **Registro**: https://fixer.io/signup/free
- ✅ **Plan gratuito**: 1,000 requests/mes
- 💰 **Premium**: Desde $9.99/mes

```python
FIXER_API_KEY = "TU_CLAVE_AQUI"
```

---

## 🚀 Uso Básico

### Obtener Precio Agregado

```python
from src.data_sources.hybrid_data_source import HybridDataSource

ds = HybridDataSource()

# Obtener precio con múltiples fuentes
result = ds.get_aggregated_price('AAPL')

print(f"Precio: ${result['price']:.2f}")
print(f"Confianza: {result['confidence']:.1%} - {result['quality']}")
print(f"Fuentes usadas: {result['sources_used']}")
print(f"Spread: {result['spread_pct']:.3f}%")
print(f"Precios individuales: {result['individual_prices']}")
```

### Resultado Ejemplo

```python
{
    'symbol': 'AAPL',
    'asset_type': 'stock',
    'price': 271.01,
    'sources_used': 4,
    'confidence': 0.92,  # 92%
    'quality': 'Excellent',
    'spread_pct': 0.05,
    'std_dev': 0.12,
    'individual_prices': {
        'yfinance': 271.01,
        'alpha_vantage': 271.02,
        'finnhub': 270.98,
        'iex': 271.03
    },
    'outliers': [],
    'timestamp': '2026-01-04 17:30:00'
}
```

---

## ⚙️ Configuración Avanzada

### Prioridad de Fuentes

Edita `config/broker_apis.py` para cambiar el orden de prioridad:

```python
SOURCE_PRIORITY = {
    'stocks': [
        'iex',           # US stocks en tiempo real
        'finnhub',       # Global stocks
        'alpha_vantage', # Backup
        'yfinance'       # Gratuito
    ],
    'forex': [
        'fixer',         # Especializado en forex
        'twelve_data',   # Multi-asset
        'alpha_vantage',
        'yfinance'
    ],
    'indices': [
        'marketstack',
        'twelve_data',
        'yfinance'
    ],
    'crypto': [
        'exchanges',     # 6 crypto exchanges
        'polygon',
        'finnhub',
        'yfinance'
    ]
}
```

### Método de Agregación

```python
from src.data_sources.price_aggregator import aggregate_prices

# Promedio simple (default)
result = aggregate_prices(prices, method='simple_average')

# Promedio ponderado
result = aggregate_prices(prices, method='weighted_average')

# Mediana (más resistente a outliers)
result = aggregate_prices(prices, method='median')
```

### Umbral de Outliers

```python
# En config/broker_apis.py
OUTLIER_Z_THRESHOLD = 2.5  # Default
# Valores más bajos = más estricto
# Valores más altos = más permisivo
```

---

## 📈 Dashboard Integration

El dashboard automáticamente usa el sistema multi-broker cuando está configurado:

```python
# dashboard.py ya integrado
result = hybrid_source.get_aggregated_price(symbol)

# El resultado incluye calidad y confianza
quality_badge = result['quality']  # Excellent, Good, Fair, Poor
confidence = result['confidence']  # 0.0 - 1.0
```

---

## 🔍 Monitoreo y Estadísticas

```python
from src.data_sources.multi_broker_client import multi_broker

# Ver estadísticas de uso
stats = multi_broker.get_statistics()

print(f"Total requests: {stats['total_requests']}")
print(f"Cache hits: {stats['cache_hits']}")
print(f"Requests por fuente:")
for source, count in stats['requests_by_source'].items():
    print(f"  {source}: {count}")
```

---

## 💡 Recomendaciones

### Para Trading Básico
- ✅ yfinance (gratuito)
- ✅ Alpha Vantage (plan gratuito: 25 req/día)
- ✅ Finnhub (plan gratuito: 60 req/min)
- **Total**: $0/mes, suficiente para análisis básico

### Para Trading Profesional
- ✅ Polygon.io ($99/mes) - Real-time US stocks
- ✅ IEX Cloud ($9/mes) - US stocks
- ✅ Fixer.io ($9.99/mes) - Forex profesional
- ✅ Twelve Data ($79/mes) - Cobertura global
- **Total**: ~$197/mes, datos de nivel profesional

### Para Crypto Trading
- ✅ Exchanges (gratuito via ccxt)
- ✅ yfinance (gratuito)
- ✅ Polygon.io (crypto incluido en plan)
- **Confianza**: 75-85% con 3+ fuentes

---

## 🐛 Troubleshooting

### "No hay fuentes disponibles"
- ✅ Verifica que las API keys estén correctamente configuradas
- ✅ Revisa los límites de rate en `config/broker_apis.py`
- ✅ Confirma que el asset type sea soportado por la fuente

### "Low confidence score"
- ✅ Agrega más fuentes de datos (más API keys)
- ✅ Verifica que las fuentes sean apropiadas para el asset type
- ✅ Revisa si hay outliers siendo removidos

### Rate Limit Exceeded
- ✅ Aumenta el `CACHE_DURATION` en broker_apis.py
- ✅ Reduce la frecuencia de actualización del dashboard
- ✅ Considera upgrade a plan premium

---

## 📚 Recursos

- [Web Scraping Guide](WEB_SCRAPING_GUIDE.md)
- [Exchange Integration](CORRECCIONES_SIMBOLOS.md)
- [API Documentation](https://github.com/usuario/coin/wiki)

---

## 🆘 Soporte

Si necesitas ayuda:
1. Revisa los logs del sistema
2. Verifica las API keys
3. Consulta la documentación de cada API
4. Abre un issue en GitHub

---

**Última actualización**: Enero 2026
