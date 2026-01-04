# 📲 Monitoreo Automático de Activos

## ¿Qué es?

Sistema de notificaciones automáticas que envía alertas de trading a tu grupo de Telegram **cada 60 segundos** para los activos que selecciones.

## 🎯 Características

- ✅ **Activación por activo**: Elige qué activos monitorear desde el dashboard
- ⏰ **Notificaciones cada minuto**: Recibe actualizaciones constantes
- 🔔 **Envío a Telegram**: Las alertas llegan directamente a tu grupo
- 🎛️ **Control total**: Activa/desactiva monitoreo con un click
- 📊 **Análisis completo**: Cada notificación incluye señal, precio, confianza, niveles clave
- 🔄 **Sin límite de confianza**: En modo auto-monitor se envían todas las señales (ignora MIN_CONFIDENCE)

## 📋 Cómo Usar

### 1. Asegúrate de tener configurado Telegram

```bash
# Si aún no tienes configurado Telegram, ejecuta:
python3 configurar_telegram.py
```

### 2. Abre el Dashboard

```bash
python3 dashboard.py
```

Abre en tu navegador: http://127.0.0.1:5000

### 3. Activar Monitoreo

En cada tarjeta de activo verás un botón:

- **📲 Activar Notificaciones (cada 1 min)** - Click para activar
- **🔔 Detener Notificaciones** - Click para desactivar (aparece cuando está activo)

### 4. Recibir Notificaciones

Una vez activado, recibirás en tu grupo de Telegram cada 60 segundos:

```
🟢 SEÑAL DE COMPRA - BTC-USD

📊 Precio: $92,450.50
📈 Confianza: 85%
🎯 Contexto: ALCISTA
🔨 Patrón: Hammer
⏱️ Intervalo: 5m

🟢 Soportes:
   • $91,000.00
   • $90,500.00

🔴 Resistencias:
   • $93,000.00
   • $94,000.00

💡 Razones:
• Rebote confirmado en soporte
• Momentum alcista fuerte
• Volumen en aumento
```

## 🎮 API REST (Opcional)

También puedes controlar el monitoreo por código:

### Iniciar Monitoreo

```bash
curl -X POST http://127.0.0.1:5000/api/auto-monitor/start \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTC-USD", "interval": "5m"}'
```

### Detener Monitoreo

```bash
curl -X POST http://127.0.0.1:5000/api/auto-monitor/stop \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTC-USD"}'
```

### Ver Estado de Monitoreo

```bash
curl http://127.0.0.1:5000/api/auto-monitor/status
```

Respuesta:
```json
{
  "monitored_assets": {
    "BTC-USD": {
      "interval": "5m",
      "started_at": "2025-12-14T21:30:00",
      "active": true
    },
    "ETH-USD": {
      "interval": "5m",
      "started_at": "2025-12-14T21:31:15",
      "active": true
    }
  },
  "total": 2
}
```

## ⚙️ Configuración

### Cambiar Intervalo de Notificaciones

Por defecto las notificaciones se envían cada **60 segundos**. Para cambiar esto, edita [dashboard.py](dashboard.py):

```python
def monitor_asset_loop(symbol, interval='5m'):
    # ...
    
    # Cambiar este valor (en segundos)
    time.sleep(60)  # <-- Cambia aquí (ej: 30 para 30 segundos, 120 para 2 minutos)
```

### Cambiar Confianza Mínima

El monitoreo automático **ignora** la confianza mínima configurada para enviar todas las señales. Si quieres filtrar por confianza, edita [dashboard.py](dashboard.py):

```python
def monitor_asset_loop(symbol, interval='5m'):
    # ...
    
    # Para respetar confianza mínima, comenta estas líneas:
    # original_min_confidence = webhook_notifier.min_confidence
    # webhook_notifier.min_confidence = 0  # <-- Comentar
    
    results = webhook_notifier.send_signal(webhook_data)
    
    # webhook_notifier.min_confidence = original_min_confidence  # <-- Comentar
```

## 💡 Consejos de Uso

### ✅ Buenas Prácticas

1. **No monitorear demasiados activos**: 3-5 activos máximo para no saturar tu Telegram
2. **Usar intervalos cortos**: 5m o 15m son ideales para señales rápidas
3. **Combinar con análisis manual**: Las notificaciones son herramientas, no decisiones automáticas
4. **Desactivar cuando no operes**: Ahorra notificaciones cuando no estés activo

### ⚠️ Qué Evitar

- ❌ Monitorear más de 10 activos simultáneamente
- ❌ Usar intervalos muy cortos (1m) sin necesidad
- ❌ Confiar ciegamente en las señales sin análisis
- ❌ Dejar monitoreo activo 24/7 sin supervisión

## 📊 Ejemplo de Flujo Completo

### Scenario: Trading de BTC durante sesión activa

**1. Inicio de sesión (9:00 AM)**
```bash
python3 dashboard.py
```

**2. Abrir dashboard en navegador**
- Ve a http://127.0.0.1:5000
- Selecciona intervalo: **5m**
- Busca **BTC-USD** en la lista

**3. Activar monitoreo**
- Click en **"📲 Activar Notificaciones"**
- Confirmación: "✅ Notificaciones activadas para BTC-USD"

**4. Durante la sesión (9:00 AM - 5:00 PM)**
- Recibes notificaciones cada 60 segundos en Telegram
- Analizas señales y tomas decisiones
- Dashboard sigue actualizándose cada 5 segundos

**5. Fin de sesión (5:00 PM)**
- Click en **"🔔 Detener Notificaciones"**
- Confirmación: "✅ Notificaciones detenidas para BTC-USD"
- Cierras el dashboard

## 🔧 Troubleshooting

### Las notificaciones no llegan

1. **Verificar configuración de Telegram**:
   ```bash
   python3 setup_webhooks.py
   ```
   Debería mostrar: "✅ Telegram webhook agregado"

2. **Verificar estado de monitoreo**:
   ```bash
   curl http://127.0.0.1:5000/api/auto-monitor/status
   ```

3. **Ver logs del dashboard**:
   Busca en la terminal del dashboard mensajes como:
   ```
   🔔 Iniciando monitoreo automático: BTC-USD (5m)
   📤 Notificación enviada: BTC-USD | BUY @ $92,450.50 | 85%
   ```

### El botón no responde

1. **Recargar página**: Presiona F5
2. **Verificar consola del navegador**: F12 → Console
3. **Verificar que el dashboard esté corriendo**: http://127.0.0.1:5000/health

### Monitoreo se detiene solo

- El monitoreo se detiene automáticamente si:
  - El dashboard se cierra
  - Se pierde conexión con las fuentes de datos
  - Hay un error en el análisis

**Solución**: Simplemente vuelve a activar el monitoreo con el botón.

## 📈 Estadísticas y Monitoreo

### Ver activos monitoreados en Health Check

```bash
curl http://127.0.0.1:5000/health
```

Respuesta incluye:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-14T21:30:00",
  "auto_monitor": {
    "active_assets": 2
  }
}
```

### Logs en Terminal

El dashboard muestra en tiempo real:
```
🔔 Iniciando monitoreo automático: BTC-USD (5m)
📤 Notificación enviada: BTC-USD | BUY @ $92,450.50 | 85%
📤 Notificación enviada: ETH-USD | SELL @ $3,250.00 | 78%
⏹️  Deteniendo monitoreo: BTC-USD
```

## 🎯 Casos de Uso

### 1. Scalping Activo (1-5 minutos)

```python
# Configuración recomendada:
- Intervalo: 5m
- Activos: 1-2 (máximo 3)
- Notificaciones: Cada 60s
- Duración: 2-4 horas
```

### 2. Day Trading (15 minutos - 1 hora)

```python
# Configuración recomendada:
- Intervalo: 15m
- Activos: 3-5
- Notificaciones: Cada 60s
- Duración: Todo el día
```

### 3. Swing Trading (4 horas - 1 día)

```python
# Configuración recomendada:
- Intervalo: 1h
- Activos: 5-10
- Notificaciones: Cada 120s (2 minutos)
- Duración: Días/Semanas
```

## 🔐 Seguridad

- ⚠️ **Nunca compartas tu bot_token**: Está en webhook_config.py
- 🔒 **Bot solo puede enviar a grupos donde esté agregado**
- 👥 **Control de grupo**: Solo administradores deberían poder agregar bots
- 📱 **Notificaciones privadas**: Solo miembros del grupo ven las alertas

## 📚 Archivos Relacionados

- [dashboard.py](dashboard.py) - Lógica de monitoreo automático
- [templates/dashboard.html](templates/dashboard.html) - Interfaz con botones
- [webhook_notifier.py](webhook_notifier.py) - Sistema de envío de notificaciones
- [webhook_config.py](webhook_config.py) - Configuración de Telegram
- [configurar_telegram.py](configurar_telegram.py) - Script de configuración inicial

## 🆘 Soporte

Si tienes problemas:

1. **Revisa logs**: Terminal del dashboard muestra errores
2. **Verifica configuración**: `python3 setup_webhooks.py`
3. **Prueba webhook**: Endpoint `/api/webhooks/test`
4. **Reinicia dashboard**: `Ctrl+C` y vuelve a ejecutar `python3 dashboard.py`

---

**¡Listo para recibir alertas automáticas!** 🚀

Abre el dashboard, activa monitoreo en tus activos favoritos y empieza a recibir notificaciones cada minuto en tu Telegram.
