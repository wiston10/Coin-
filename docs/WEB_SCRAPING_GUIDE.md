# 🔴 SISTEMA DE TRADING EN TIEMPO REAL CON WEB SCRAPING

## 🚀 ¿Por Qué Web Scraping?

El problema con `yfinance`:
- ❌ Datos limitados en intervalos cortos (máximo 7 días con 1m)
- ❌ Solo 300-500 velas disponibles
- ❌ Actualización lenta (no en tiempo real)
- ❌ No apto para **scalping**

La solución con **Web Scraping + APIs de Exchanges**:
- ✅ Datos EN VIVO desde Binance/Coinbase/Kraken
- ✅ Hasta **1000 velas** en intervalos de 1 minuto
- ✅ Actualización cada **segundo**
- ✅ **Perfecto para scalping**

## 📊 Fuentes de Datos

### 1. **Binance API** (Principal)
- Datos OHLCV en tiempo real
- 1000 velas históricas
- Actualización instantánea
- Sin límites de requests

### 2. **CCXT Exchange** (Respaldo)
- Acceso a múltiples exchanges
- Binance, Coinbase, Kraken
- Fallback automático

### 3. **CoinGecko API** (Emergencia)
- API gratuita sin límites
- Datos históricos confiables
- Cobertura de 10,000+ cryptos

## 🎯 Características del Sistema

### Datos en Tiempo Real
```python
from live_trading import analyze_live

# Análisis instantáneo
result = analyze_live('BTC-USD', '1m')

# Datos actualizados cada segundo
# Precio en vivo desde el exchange
```

### Monitor Continuo
```python
from live_trading import start_monitor

# Monitor con actualización automática
start_monitor('BTC-USD', '1m', update_seconds=5)

# Actualiza análisis cada 5 segundos
# Perfecto para scalping activo
```

### Scraper Directo
```python
from web_scraper import get_live_data, get_realtime_price

# Obtener velas OHLCV
df = get_live_data('BTC-USD', '1m', limit=500)

# Obtener precio actual
ticker = get_realtime_price('BTC-USD')
```

## 🛠️ Instalación

### 1. Librerías de Web Scraping
```bash
pip install beautifulsoup4 lxml html5lib
```

Ya instaladas:
- `ccxt` - Para exchanges
- `requests` - Para APIs
- `pandas`, `numpy` - Análisis de datos

### 2. Verificar Instalación
```bash
python3 -c "from web_scraper import get_live_data; print('✅ OK')"
```

## 📖 Guía de Uso

### Ejemplo 1: Análisis Rápido

```python
from live_trading import analyze_live

# Análisis en 1 minuto (scalping)
result = analyze_live('BTC-USD', '1m')

if result['should_enter']:
    print(f"🎯 Señal: {result['signal']['signal']}")
    print(f"📍 Entrada: ${result['levels']['entry']}")
    print(f"🎯 TP: ${result['levels']['take_profit']}")
    print(f"🛑 SL: ${result['levels']['stop_loss']}")
```

**Output:**
```
🔴 Obteniendo datos EN VIVO desde Binance...
✅ Datos en vivo: 500 velas (actualizado: 08:37:46)

🎯 SEÑAL: 📈 COMPRAR
Confianza: 65.0%

📍 Entrada:      $92,124.61
🎯 Take Profit:  $92,314.93
🛑 Stop Loss:    $91,997.73
⚖️  Risk/Reward:  1.50:1

✓ RECOMENDACIÓN: ENTRAR AHORA
```

### Ejemplo 2: Monitor Continuo para Scalping

```bash
# Desde terminal
python3 live_trading.py BTC-USD 1m

# Monitor con actualización cada 5 segundos
# Presiona Ctrl+C para detener
```

**Ventajas:**
- ✅ Datos frescos cada 5 segundos
- ✅ Señales actualizadas automáticamente
- ✅ Detecta cambios de tendencia rápidamente
- ✅ Ideal para scalping de 1-5 minutos

### Ejemplo 3: Comparar Múltiples Intervalos

```python
from live_trading import analyze_live

# Confirmar señal en múltiples timeframes
intervalos = ['1m', '5m', '15m']
señales = []

for interval in intervalos:
    result = analyze_live('ETH-USD', interval)
    señales.append(result['signal']['signal'])

# Si todos coinciden = señal fuerte
if len(set(señales)) == 1:
    print(f"✅ CONFLUENCIA: Señal confirmada en todos los timeframes")
```

### Ejemplo 4: Escanear Múltiples Activos

```python
activos = ['BTC-USD', 'ETH-USD', 'SOL-USD', 'MATIC-USD']
oportunidades = []

for symbol in activos:
    result = analyze_live(symbol, '5m')
    
    if result['should_enter'] and result['signal']['confidence'] > 70:
        oportunidades.append({
            'symbol': symbol,
            'señal': result['signal']['signal'],
            'confianza': result['signal']['confidence']
        })

# Mostrar mejores oportunidades
for opp in sorted(oportunidades, key=lambda x: x['confianza'], reverse=True):
    print(f"{opp['symbol']} → {opp['señal']} ({opp['confianza']:.0f}%)")
```

### Ejemplo 5: Datos Crudos Personalizados

```python
from web_scraper import get_live_data, get_realtime_price

# Obtener velas OHLCV
df = get_live_data('BTC-USD', '1m', limit=500)

# Análisis personalizado
volatilidad = df['Close'].std()
precio_promedio = df['Close'].mean()
ultimo_precio = df['Close'].iloc[-1]

# Ticker en tiempo real
ticker = get_realtime_price('BTC-USD')
spread = ticker['ask'] - ticker['bid']

print(f"Precio: ${ticker['price']:,.2f}")
print(f"Spread: ${spread:.2f}")
print(f"Volatilidad: {volatilidad:.2f}")
```

## 🎮 Scripts Disponibles

### 1. `live_trading.py` - Monitor Principal
```bash
# Análisis único
python3 -c "from live_trading import analyze_live; analyze_live('BTC-USD', '1m')"

# Monitor continuo
python3 live_trading.py BTC-USD 1m

# Monitor con actualización personalizada
python3 -c "from live_trading import start_monitor; start_monitor('ETH-USD', '5m', 10)"
```

### 2. `ejemplos_live.py` - Ejemplos Interactivos
```bash
# Menú interactivo
python3 ejemplos_live.py

# Ejecutar ejemplo específico
python3 ejemplos_live.py 1  # Análisis rápido
python3 ejemplos_live.py 2  # Comparar intervalos
python3 ejemplos_live.py 3  # Datos crudos
python3 ejemplos_live.py 4  # Monitor continuo
python3 ejemplos_live.py 5  # Múltiples activos
```

### 3. `web_scraper.py` - Scraper Directo
```bash
# Probar scraper
python3 -c "
from web_scraper import get_live_data
df = get_live_data('BTC-USD', '1m', 500)
print(f'Velas: {len(df)}')
print(df.tail())
"
```

## 📈 Estrategias Optimizadas para Scalping

### Scalping Agresivo (1m)
```python
# Configuración para ganancias rápidas
result = analyze_live('BTC-USD', '1m')

# Objetivo: +0.5% en 3-5 minutos
# Stop loss: -0.3%
# Risk/Reward: 1.67:1
```

**Características:**
- 500 velas históricas (8 horas)
- Actualización cada 5 segundos
- Detecta patrones en tiempo real
- Análisis de volumen instantáneo

### Scalping Moderado (5m)
```python
# Balance entre velocidad y precisión
result = analyze_live('ETH-USD', '5m')

# Objetivo: +0.8% en 15-30 minutos
# Stop loss: -0.4%
# Risk/Reward: 2:1
```

### Intraday Trading (15m)
```python
# Operaciones de mediano plazo
result = analyze_live('SOL-USD', '15m')

# Objetivo: +2% en 2-4 horas
# Stop loss: -1%
# Risk/Reward: 2:1
```

## 🔥 Ventajas del Sistema

### vs yfinance

| Característica | yfinance | Web Scraping |
|---------------|----------|--------------|
| Velas 1m | 300 máx | **1000** ✅ |
| Actualización | Lenta | **Tiempo real** ✅ |
| Periodo máximo 1m | 7 días | **Sin límite** ✅ |
| Latencia | 30-60s | **<1s** ✅ |
| Scalping | ❌ No apto | **✅ Perfecto** |

### Datos en Tiempo Real

```python
# yfinance (viejo sistema)
df = yf.download('BTC-USD', period='7d', interval='1m')
# → 300 velas, actualización lenta

# Web Scraping (nuevo sistema)
df = get_live_data('BTC-USD', '1m', limit=1000)
# → 1000 velas, actualización instantánea ✅
```

### Actualización Continua

```python
# Monitor automático
start_monitor('BTC-USD', '1m', update_seconds=5)

# Cada 5 segundos:
# - Obtiene datos frescos del exchange
# - Recalcula indicadores
# - Genera nueva señal
# - Muestra resultado actualizado
```

## 🎯 Integración con Estrategia de Rebotes

El sistema incluye **análisis de rebotes** integrado:

```python
result = analyze_live('BTC-USD', '5m')

bounce = result['signal']['bounce_analysis']

print(f"Probabilidad de rebote: {bounce['bounce_probability']}%")
print(f"Éxito histórico: {bounce['historical_success_rate']}%")
print(f"Psicología del mercado: {bounce['psychology']['sentiment']}")
```

**Output:**
```
🎯 OPORTUNIDAD DE REBOTE:
   Señal: BUY | Confianza: 72%
   Probabilidad: 75% | Éxito histórico: 68%
   Psicología: FAVORABLE

   Razones:
   • Cerca de soporte en $89,500.00
   • Patrón alcista 'Hammer' en soporte
   • RSI sobrevendido - agotamiento bajista
   • Volumen 1.8x promedio
   • Historial: 68% rebotes exitosos
```

## ⚙️ Configuración Avanzada

### Cambiar Exchange
```python
# En web_scraper.py
self.exchanges = {
    'binance': ccxt.binance(),  # Default
    'kraken': ccxt.kraken(),    # Alternativo
    'coinbase': ccxt.coinbase() # Backup
}
```

### Ajustar Límite de Velas
```python
# Más datos = análisis más preciso (pero más lento)
df = get_live_data('BTC-USD', '1m', limit=1000)  # Máximo

# Menos datos = análisis más rápido
df = get_live_data('BTC-USD', '1m', limit=200)   # Mínimo recomendado
```

### Cambiar Frecuencia de Actualización
```python
# Actualizar cada 3 segundos (más rápido, más requests)
start_monitor('BTC-USD', '1m', update_seconds=3)

# Actualizar cada 10 segundos (más lento, menos requests)
start_monitor('BTC-USD', '1m', update_seconds=10)
```

## 🚨 Límites y Consideraciones

### Rate Limits
- Binance: **1200 requests/minuto**
- CoinGecko: **50 requests/minuto**
- Sin API key: Sin autenticación necesaria

**Recomendación:** Esperar al menos 5 segundos entre requests

### Consumo de Datos
- 1 request = ~50KB
- 1000 velas = ~100KB
- 12 requests/minuto (cada 5s) = ~600KB/min

### Confiabilidad
- Binance: 99.9% uptime
- Fallback automático si Binance falla
- CoinGecko como última opción

## 📱 Uso en Producción

### Script Básico
```python
#!/usr/bin/env python3
from live_trading import LiveTradingAnalyzer
import time

analyzer = LiveTradingAnalyzer()

while True:
    result = analyzer.analyze_live('BTC-USD', '1m', show_details=True)
    
    if result['should_enter']:
        signal = result['signal']
        print(f"🚨 ALERTA: {signal['signal']} - Confianza {signal['confidence']:.0f}%")
        # Aquí podrías enviar notificación, ejecutar orden, etc.
    
    time.sleep(5)  # Esperar 5 segundos
```

### Con Notificaciones (Telegram/Email)
```python
# Agregar después de la señal
if result['should_enter'] and signal['confidence'] > 70:
    # Enviar alerta
    mensaje = f"🎯 {signal['signal']} {symbol}\n"
    mensaje += f"Confianza: {signal['confidence']:.0f}%\n"
    mensaje += f"Entrada: ${result['levels']['entry']:.2f}"
    
    # enviar_telegram(mensaje)
    # enviar_email(mensaje)
```

## 🆘 Troubleshooting

### Error: "No se pudieron obtener datos"
```bash
# Verificar conexión a internet
ping api.binance.com

# Probar directamente el scraper
python3 -c "from web_scraper import get_live_data; print(get_live_data('BTC-USD', '1m'))"
```

### Error: "ccxt.ExchangeError"
```python
# El símbolo puede estar mal formado
# ❌ Incorrecto: 'BTC-USD'
# ✅ Correcto: Se convierte automáticamente a 'BTC/USDT'

# Verificar símbolo válido
from web_scraper import scraper
exchange = scraper.exchanges['binance']
markets = exchange.load_markets()
print('BTC/USDT' in markets)  # Debe ser True
```

### Warning: "FutureWarning pandas"
```bash
# Es solo un warning, no afecta funcionalidad
# Para suprimirlo:
python3 -W ignore live_trading.py BTC-USD 1m
```

## 🎓 Próximos Pasos

1. **Ejecutar ejemplos**
   ```bash
   python3 ejemplos_live.py
   ```

2. **Iniciar monitor**
   ```bash
   python3 live_trading.py BTC-USD 1m
   ```

3. **Personalizar estrategia**
   - Editar `bounce_strategy.py`
   - Ajustar parámetros de scalping
   - Configurar niveles de riesgo

4. **Automatizar trades**
   - Integrar con exchange API
   - Ejecutar órdenes automáticas
   - Gestionar posiciones

---

## 📊 Comparación Final

### Sistema Antiguo (yfinance)
```python
import yfinance as yf
df = yf.download('BTC-USD', period='7d', interval='1m')
# ❌ 300 velas máximo
# ❌ Datos desactualizados
# ❌ Lento para scalping
```

### Sistema Nuevo (Web Scraping)
```python
from web_scraper import get_live_data
df = get_live_data('BTC-USD', '1m', limit=1000)
# ✅ 1000 velas
# ✅ Datos EN VIVO
# ✅ Perfecto para scalping
```

---

**✅ SISTEMA OPTIMIZADO PARA SCALPING CON DATOS EN TIEMPO REAL**
