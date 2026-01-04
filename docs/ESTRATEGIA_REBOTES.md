# 🎯 ESTRATEGIA AVANZADA DE REBOTES

## 📖 Descripción General

Esta estrategia identifica oportunidades de trading basadas en **rebotes en niveles clave** de soporte y resistencia, combinando:

- **Análisis de patrones de velas** históricos y actuales
- **Psicología del mercado** a través del volumen
- **Datos históricos** para calcular probabilidad de éxito
- **Análisis de momentum** para detectar agotamiento

## 🎲 Tipos de Trading Soportados

### 1. **SCALPING** (1m - 5m)
- **Objetivo de ganancia**: 0.5% por operación
- **Stop loss**: 0.3%
- **Tiempo de retención**: Máximo 5 velas
- **Volumen requerido**: 50% más que el promedio
- **Ideal para**: Traders activos que buscan ganancias rápidas

### 2. **MEDIANO PLAZO** (15m - 1h)
- **Objetivo de ganancia**: 2% por operación
- **Stop loss**: 1%
- **Tiempo de retención**: Máximo 20 velas
- **Volumen requerido**: 30% más que el promedio
- **Ideal para**: Traders que prefieren menos operaciones pero más rentables

## 🔍 Cómo Funciona

### Paso 1: Identificación de Niveles Clave

La estrategia identifica soportes y resistencias usando **3 métodos combinados**:

1. **Pivot Points**: Máximos y mínimos locales en el historial
2. **Niveles Psicológicos**: Números redondos que los traders observan
3. **Niveles de Volumen**: Zonas con alto volumen histórico (zonas de lucha)

#### Ejemplo:
```
Bitcoin en $85,000

RESISTENCIAS DETECTADAS:
- $86,500 (Pivot + Volumen alto)
- $88,000 (Número redondo psicológico)
- $90,000 (Número redondo fuerte)

SOPORTES DETECTADOS:
- $83,500 (Pivot + Volumen alto)
- $82,000 (Número redondo)
- $80,000 (Número redondo fuerte)
```

### Paso 2: Análisis de Proximidad

El sistema verifica si el precio actual está **cerca** (±0.5%) de algún nivel clave:

- **Cerca de SOPORTE** → Buscar señal de COMPRA (rebote alcista)
- **Cerca de RESISTENCIA** → Buscar señal de VENTA (rebote bajista)

### Paso 3: Detección de Patrones de Velas

#### Patrones Alcistas (Comprar en soporte):
- ✅ **Hammer**: Vela con sombra inferior larga = rechazo de precios bajos
- ✅ **Bullish Engulfing**: Vela alcista que envuelve la anterior = fuerza compradora
- ✅ **Morning Star**: Tres velas indicando cambio de tendencia bajista a alcista
- ✅ **Three White Soldiers**: Tres velas alcistas consecutivas = momentum fuerte

#### Patrones Bajistas (Vender en resistencia):
- ⛔ **Shooting Star**: Vela con sombra superior larga = rechazo de precios altos
- ⛔ **Bearish Engulfing**: Vela bajista que envuelve la anterior = fuerza vendedora
- ⛔ **Evening Star**: Tres velas indicando cambio de tendencia alcista a bajista
- ⛔ **Three Black Crows**: Tres velas bajistas consecutivas = momentum fuerte

### Paso 4: Psicología del Mercado (Análisis de Volumen)

El volumen revela la **convicción** del mercado:

| Volumen | Ratio | Psicología |
|---------|-------|------------|
| MUY ALTO | >2.0x | 💪 Convicción fuerte - Los traders están comprometidos |
| ALTO | 1.5-2.0x | ✓ Convicción moderada - Buen momento para entrar |
| NORMAL | 0.8-1.5x | • Mercado normal - Neutral |
| BAJO | 0.5-0.8x | ⚠️ Indecisión - Esperar confirmación |
| MUY BAJO | <0.5x | ⛔ Desinterés - Evitar operar |

#### Ejemplo Real:
```
Volumen actual: 2,500 BTC
Volumen promedio: 1,200 BTC
Ratio: 2.08x

→ VOLUMEN MUY ALTO
→ Psicología: "Convicción fuerte"
→ Interpretación: Los traders están tomando posiciones con convicción
```

### Paso 5: Análisis de Momentum

Detecta **agotamiento** o **aceleración** del precio:

| Momentum | Condición | Interpretación |
|----------|-----------|----------------|
| OVERBOUGHT | RSI > 70 + precio subiendo | 🔴 Agotamiento alcista - posible rebote bajista |
| OVERSOLD | RSI < 30 + precio bajando | 🟢 Agotamiento bajista - posible rebote alcista |
| BULLISH | MACD > Signal + RSI > 50 | 📈 Momentum alcista |
| BEARISH | MACD < Signal + RSI < 50 | 📉 Momentum bajista |
| NEUTRAL | Sin señales claras | ⚪ Esperar |

### Paso 6: Historial de Rebotes

El sistema analiza los **últimos 100 datos** para calcular:

- **Toques en el nivel**: Cuántas veces el precio tocó ese soporte/resistencia
- **Rebotes exitosos**: Cuántas veces rebotó efectivamente (>0.5% de movimiento)
- **Tasa de éxito**: % de rebotes exitosos vs toques totales

#### Ejemplo:
```
SOPORTE en $83,500:
- Tocado: 8 veces en los últimos 100 períodos
- Rebotes exitosos: 6 veces
- Tasa de éxito: 75%

→ ALTO NIVEL DE CONFIANZA para rebote alcista
```

### Paso 7: Contexto de Velas Previas

Analiza las últimas 10 velas para entender el contexto:

**Señales de CONSOLIDACIÓN** (ideal para rebotes):
- Cuerpos pequeños (indecisión)
- Sombras largas (rechazo de precios)
- 3+ velas de indecisión → Mercado preparándose para rebote

**Señales de MOMENTUM**:
- Cuerpos grandes
- Sombras pequeñas
- 3+ velas de momentum → Tendencia fuerte en curso

### Paso 8: Generación de Señal Final

La señal se genera sumando **puntos de confianza**:

| Factor | Puntos | Condición |
|--------|--------|-----------|
| **Proximidad a nivel** | +15 | Precio cerca de soporte/resistencia |
| **Patrón alcista/bajista** | +20 | Patrón correcto en el nivel correcto |
| **Momentum favorable** | +15 | RSI sobrevendido en soporte (o sobrecomprado en resistencia) |
| **Volumen alto** | +10 | Volumen >1.5x promedio |
| **Historial exitoso** | +10 | Tasa de éxito >60% |

**Total necesario para operar**: 50+ puntos (50% confianza)

#### Ejemplo de Señal COMPRA:
```
Bitcoin en $83,480 (soporte en $83,500)

ANÁLISIS:
✅ Cerca de soporte +15 pts
✅ Patrón Hammer detectado +20 pts
✅ RSI = 28 (sobrevendido) +15 pts
✅ Volumen 2.1x promedio +10 pts
✅ Historial 75% éxito +10 pts

TOTAL: 70 puntos

🎯 SEÑAL: COMPRAR
Confianza: 70%
Take Profit: $84,315 (+1%)
Stop Loss: $83,145 (-0.4%)
Risk/Reward: 2.5:1
```

## 📊 Métricas e Interpretación

### Confianza de la Señal

- **90-100%**: 🟢 Excelente - Máxima probabilidad, todos los factores alineados
- **70-89%**: 🟢 Muy Buena - Alta probabilidad, mayoría de factores favorables
- **50-69%**: 🟡 Moderada - Probabilidad aceptable, algunos factores favorables
- **30-49%**: 🟠 Baja - Poca confianza, pocos factores alineados
- **0-29%**: 🔴 Muy Baja - No operar

### Probabilidad de Rebote

Calculada combinando:
- Historial de rebotes en ese nivel
- Fuerza del patrón de vela
- Intensidad del volumen
- Estado del momentum

### Risk/Reward Ratio

Relación entre ganancia potencial y pérdida máxima:

- **3:1 o superior**: Excelente
- **2:1 a 3:1**: Muy bueno
- **1.5:1 a 2:1**: Aceptable
- **Menor a 1.5:1**: Evitar

## 🎯 Ejemplos de Uso

### Caso 1: Scalping BTC 1m

```python
from bounce_strategy import analyze_bounce_opportunity

# Obtener datos con indicadores
df = get_market_data('BTC-USD', '7d', '1m')
df = calculate_adaptive_indicators(df, '1m')

# Analizar rebote
result = analyze_bounce_opportunity(df, interval='1m', trading_type='scalping')

print(f"Señal: {result['signal']}")
print(f"Confianza: {result['confidence']:.0f}%")
print(f"Take Profit: ${result['take_profit']:,.2f}")
print(f"Stop Loss: ${result['stop_loss']:,.2f}")
print(f"Risk/Reward: {result['risk_reward']:.2f}:1")
```

### Caso 2: Mediano Plazo ETH 15m

```python
result = analyze_bounce_opportunity(df, interval='15m', trading_type='medium_term')

if result['confidence'] >= 70:
    print(f"🎯 Oportunidad detectada!")
    print(f"Probabilidad de rebote: {result['bounce_probability']:.0f}%")
    print(f"Éxito histórico: {result['historical_success_rate']:.0f}%")
    print(f"\nPsicología del mercado:")
    print(f"  {result['psychology']['description']}")
    print(f"\nRazones:")
    for reason in result['reasons']:
        print(f"  - {reason}")
```

## ⚙️ Configuración Avanzada

Puedes personalizar la estrategia modificando `bounce_strategy.py`:

### Ajustar Parámetros de Scalping

```python
'scalping': {
    'profit_target': 0.5,    # Cambiar a 0.8% para más ganancia
    'stop_loss': 0.3,        # Cambiar a 0.4% para más margen
    'min_volume_spike': 1.5, # Cambiar a 2.0 para mayor filtro
    'hold_time': 5,          # Cambiar a 3 para salir más rápido
}
```

### Ajustar Tolerancia de Niveles

```python
# En _is_near_level()
tolerance = 0.005  # 0.5% - Cambiar a 0.01 para detectar más cerca (1%)
```

### Añadir Patrones Personalizados

```python
self.bullish_bounce_patterns = [
    'Hammer',
    'Bullish Engulfing',
    'Morning Star',
    'Three White Soldiers',
    'Inverted Hammer',  # Añadir patrón
    'Piercing Line'     # Añadir patrón
]
```

## 📈 Integración en el Sistema

La estrategia está completamente integrada en:

### 1. CLI (`trading_app.py`)

```bash
python3 trading_app.py
```

Al analizar un activo, verás:
```
🎯 ESTRATEGIA DE REBOTES:
   Señal: BUY (Confianza: 72%)
   Probabilidad de rebote: 75%
   Éxito histórico: 68%
   Psicología del mercado: FAVORABLE
   ✓ Convicción moderada | ✓ RSI sobrevendido (oportunidad)
   
   Soportes clave: $83,500.00, $82,000.00, $80,000.00
   
   Razones del rebote:
   1. Cerca de soporte en $83,500.00
   2. Patrón alcista 'Hammer' en soporte
   3. RSI sobrevendido - agotamiento bajista
   4. Volumen 1.8x promedio
   5. Historial: 68% rebotes exitosos
```

### 2. GUI (`trading_gui.py`)

En la interfaz gráfica verás una nueva sección:

```
🎯 ESTRATEGIA DE REBOTES:
  Señal:               BUY
  Confianza:           72%
  Prob. Rebote:        75%
  Éxito Histórico:     68%
  Psicología:          FAVORABLE
  Volumen:             HIGH
  Risk/Reward:         2.80:1
  
  Soportes Clave:
    • $83,500.00
    • $82,000.00
  
  Razones del Rebote:
    1. Cerca de soporte en $83,500.00
    2. Patrón alcista 'Hammer' en soporte
    3. RSI sobrevendido - agotamiento bajista
```

**En el gráfico**:
- Líneas discontinuas verdes: Soportes base
- Líneas discontinuas rojas: Resistencias base
- Líneas punteadas moradas: Soportes clave de rebotes
- Líneas punteadas rosas: Resistencias clave de rebotes

## 🧠 Psicología de Trading

### ¿Por qué funcionan los rebotes?

1. **Memoria del mercado**: Los traders recuerdan niveles previos
2. **Órdenes pendientes**: Stop losses y take profits agrupados en niveles
3. **Psicología de números redondos**: $80,000 es más memorable que $79,847
4. **Profecía autocumplida**: Si todos esperan rebote en $80k, todos compran allí

### Señales de Mayor Confianza

Busca estas **combinaciones**:

✅ **COMBO 1: Patrón + Volumen**
- Hammer en soporte + Volumen 2x = Muy fuerte

✅ **COMBO 2: Historial + Momentum**
- 75%+ éxito histórico + RSI sobrevendido = Alta probabilidad

✅ **COMBO 3: Consolidación + Nivel**
- 3+ velas indecisas + toque de soporte = Preparado para rebote

⚠️ **EVITAR**:
- Bajo volumen + sin patrón = Rebote débil
- Historial <50% + momentum neutral = Probabilidad baja
- Nivel tocado >10 veces = Soporte/resistencia débil

## 🎓 Mejores Prácticas

### Para Scalping (1m-5m)

1. ✅ Opera solo con volumen >1.5x promedio
2. ✅ Sal rápido - no esperes al take profit si hay ganancia
3. ✅ Respeta el stop loss - no muevas la orden
4. ✅ Opera en horas de alto volumen (sesión USA/Europa)
5. ⛔ No operes más de 5 posiciones simultáneas
6. ⛔ No operes en noticias importantes

### Para Mediano Plazo (15m-1h)

1. ✅ Espera confirmación del rebote (2-3 velas)
2. ✅ Usa trailing stop después de +1%
3. ✅ Verifica confluencia con análisis diario
4. ✅ Opera con confianza >60%
5. ⛔ No entres tarde (>1% del nivel)
6. ⛔ No operes contra tendencia diaria

### Gestión de Riesgo

- **No arriesgues más del 1-2% por operación**
- **Diversifica**: No pongas todo en una operación
- **Tamaño de posición**: Calcula según stop loss
  ```
  Tamaño = (Capital × % Riesgo) / (Entrada - Stop Loss)
  ```
- **No operes emociones**: Si pierdes 2 seguidas, para

## 📚 Recursos Adicionales

- [MODO_TIEMPO_REAL.md](./MODO_TIEMPO_REAL.md) - Guía de trading en tiempo real
- [README.md](./README.md) - Documentación general del sistema
- `bounce_strategy.py` - Código fuente con comentarios detallados

## 🚀 Próximas Mejoras

- [ ] Detección de falsos breakouts
- [ ] Análisis de correlación entre activos
- [ ] Backtesting automático
- [ ] Alertas por Telegram/Discord
- [ ] Machine Learning para mejorar predicciones
- [ ] Integración con exchanges para trading automático

---

**⚠️ DISCLAIMER**: Esta estrategia es educativa. El trading conlleva riesgos. Nunca operes con dinero que no puedas perder. Practica primero en cuentas demo.

**✅ VENTAJA**: Esta estrategia combina múltiples factores para predicciones más precisas que el análisis técnico tradicional.
