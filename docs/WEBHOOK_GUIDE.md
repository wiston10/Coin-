# 🔔 Guía Completa de Webhooks para Trading

## 📋 Descripción

El sistema de webhooks te notifica automáticamente cuando detecta oportunidades de entrada en el mercado, diferenciando entre:

- **📈 COMPRAR en mercado ALCISTA** - Mejores oportunidades
- **📉 VENDER en mercado BAJISTA** - Ideales para shorts
- **⚠️ Señales con precaución** - Contexto de mercado no ideal

## 🌐 Servicios Soportados

### 1. Discord 💬
**Ventajas:**
- Embeds con formato rico
- Colores según señal (verde=compra, rojo=venta)
- Campos organizados
- Enlaces a gráficos

**Configuración:**
1. Ve a tu servidor de Discord
2. Settings del canal → Integrations → Webhooks
3. Click "New Webhook"
4. Copia la URL del webhook
5. Agrega en `webhook_config.py`:

```python
DISCORD_WEBHOOKS = [
    {
        'url': 'https://discord.com/api/webhooks/123456/abcdef...',
        'name': 'Canal Trading',
        'enabled': True
    }
]
```

### 2. Telegram 📱
**Ventajas:**
- Notificaciones push instantáneas
- Formato Markdown
- Muy rápido
- Acceso móvil fácil

**Configuración:**
1. Habla con @BotFather en Telegram
2. Envía `/newbot` y sigue las instrucciones
3. Copia el **bot token** (formato: `123456:ABCdef...`)
4. Inicia chat con tu bot
5. Ve a `https://api.telegram.org/botTU_TOKEN/getUpdates`
6. Copia tu **chat_id** (número)
7. Agrega en `webhook_config.py`:

```python
TELEGRAM_WEBHOOKS = [
    {
        'bot_token': '123456789:ABCdefGHIjklMNOpqrsTUVwxyz',
        'chat_id': '987654321',
        'name': 'Bot Trading',
        'enabled': True
    }
]
```

### 3. Slack 💼
**Ventajas:**
- Integración profesional
- Canales dedicados
- Hilos de conversación
- Buen para equipos

**Configuración:**
1. Ve a https://api.slack.com/apps
2. Click "Create New App" → "From scratch"
3. Activa "Incoming Webhooks"
4. Click "Add New Webhook to Workspace"
5. Selecciona el canal
6. Copia la URL del webhook
7. Agrega en `webhook_config.py`:

```python
SLACK_WEBHOOKS = [
    {
        'url': 'https://hooks.slack.com/services/T00/B00/XXXX',
        'name': 'Canal Trading',
        'enabled': True
    }
]
```

### 4. Webhook Genérico 🔗
**Ventajas:**
- Compatible con cualquier servicio
- Zapier, IFTTT, Make.com, n8n
- Personalizable
- Integración con sistemas propios

**Configuración:**
```python
GENERIC_WEBHOOKS = [
    {
        'url': 'https://tu-servidor.com/webhook',
        'name': 'Sistema Personalizado',
        'headers': {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer tu-token'
        },
        'enabled': True
    }
]
```

## 🚀 Instalación y Configuración

### Paso 1: Copiar archivo de ejemplo

```bash
cd /Users/wistonnavarroaroca/Documents/coin
cp webhook_config_example.py webhook_config.py
```

### Paso 2: Editar configuración

```bash
nano webhook_config.py
# o usa tu editor favorito
```

### Paso 3: Configurar tus webhooks

Edita las secciones que necesites (Discord, Telegram, etc.) con tus URLs y tokens.

### Paso 4: Reiniciar dashboard

```bash
python3 dashboard.py
```

El sistema detectará automáticamente tu configuración.

## ⚙️ Configuración Avanzada

### Confianza Mínima

Solo envía alertas con confianza >= 70%:

```python
MIN_CONFIDENCE = 70  # 0-100
```

### Cooldown

Evita spam estableciendo tiempo mínimo entre alertas del mismo símbolo:

```python
COOLDOWN_DURATION = 300  # 5 minutos en segundos
```

### Filtrar por Contexto de Mercado

Solo alertas en mercados alcistas/bajistas:

```python
ALLOWED_MARKET_CONTEXTS = ['ALCISTA', 'BAJISTA']
# Omite 'NEUTRAL' para evitar señales ambiguas
```

### Filtrar por Tipo de Señal

Solo compras/ventas, sin holds:

```python
ALLOWED_SIGNALS = ['BUY', 'SELL']
# No incluir 'HOLD'
```

## 📊 Formato de las Notificaciones

### Información Incluida

Cada webhook contiene:

- **🎯 Señal**: BUY, SELL, o HOLD
- **💰 Precio**: Precio actual del activo
- **📊 Confianza**: Porcentaje de confianza (0-100%)
- **📈 Contexto**: ALCISTA, BAJISTA, o NEUTRAL
- **🎯 Patrón**: Patrón de vela detectado
- **⏱️ Intervalo**: Timeframe analizado
- **🟢 Soportes**: Niveles de soporte cercanos
- **🔴 Resistencias**: Niveles de resistencia cercanos
- **📋 Razones**: Justificación de la señal
- **💡 Acción Recomendada**: Qué hacer

### Ejemplo de Notificación

```
📈 SEÑAL DE TRADING: BTC-USD

💰 COMPRAR EN MERCADO ALCISTA

Señal: BUY
Precio: $92,450.50
Confianza: 85%
Contexto: ALCISTA
Patrón: Hammer
Intervalo: 5m

🟢 Soportes: $91,000, $90,500, $90,000
🔴 Resistencias: $93,000, $94,000, $95,000

💡 Acción Recomendada: Entrar en posición LONG

📋 Razones:
• RSI indica sobreventa
• Precio rebota en soporte
• Volumen creciente
• Patrón alcista confirmado
• Momentum positivo

⏰ 2025-12-14 20:30:15
```

## 🔧 Uso por API REST

### Configurar webhook via API

```bash
curl -X POST http://127.0.0.1:5000/api/webhooks/config \
  -H "Content-Type: application/json" \
  -d '{
    "type": "discord",
    "url": "https://discord.com/api/webhooks/...",
    "name": "Canal Trading"
  }'
```

### Ver configuración actual

```bash
curl http://127.0.0.1:5000/api/webhooks/config
```

### Activar/Desactivar webhooks

```bash
curl -X POST http://127.0.0.1:5000/api/webhooks/toggle \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'
```

### Enviar webhook de prueba

```bash
curl -X POST http://127.0.0.1:5000/api/webhooks/test
```

## 🧪 Testing

### Test desde línea de comandos

```bash
python3 setup_webhooks.py
```

Esto:
1. Carga tu configuración
2. Envía una señal de prueba
3. Muestra estadísticas

### Test desde Python

```python
from webhook_notifier import WebhookNotifier

notifier = WebhookNotifier()

# Agregar Discord
notifier.add_discord_webhook(
    'https://discord.com/api/webhooks/...',
    'Test'
)

# Enviar señal de prueba
signal = {
    'symbol': 'BTC-USD',
    'signal': 'BUY',
    'price': 92450.50,
    'confidence': 85,
    'market_context': 'ALCISTA',
    'pattern': 'Hammer',
    'interval': '5m',
    'support_levels': [91000],
    'resistance_levels': [93000],
    'reasons': ['Test']
}

results = notifier.send_signal(signal)
print(f"Exitosos: {results['success']}")
```

### Test con webhook.site

Para testing sin configurar servicios reales:

1. Ve a https://webhook.site/
2. Copia tu URL única
3. Agrégala como webhook genérico
4. Verás todas las notificaciones en la web

```python
GENERIC_WEBHOOKS = [
    {
        'url': 'https://webhook.site/tu-uuid',
        'name': 'Test',
        'enabled': True
    }
]
```

## 📈 Casos de Uso

### Caso 1: Scalping con Discord

```python
MIN_CONFIDENCE = 75  # Alta confianza
COOLDOWN_DURATION = 60  # 1 minuto (señales frecuentes)
ALLOWED_SIGNALS = ['BUY', 'SELL']
```

### Caso 2: Swing Trading con Telegram

```python
MIN_CONFIDENCE = 80  # Muy alta confianza
COOLDOWN_DURATION = 3600  # 1 hora (señales espaciadas)
ALLOWED_MARKET_CONTEXTS = ['ALCISTA', 'BAJISTA']
```

### Caso 3: Alertas Selectivas

```python
MIN_CONFIDENCE = 90  # Solo señales excepcionales
COOLDOWN_DURATION = 7200  # 2 horas
# Solo compras en alcista
ALLOWED_SIGNALS = ['BUY']
ALLOWED_MARKET_CONTEXTS = ['ALCISTA']
```

## 🔒 Seguridad

### Proteger Tokens

**NUNCA** subas `webhook_config.py` a Git:

```bash
# Agregar a .gitignore
echo "webhook_config.py" >> .gitignore
```

### Variables de Entorno

Para mayor seguridad, usa variables de entorno:

```python
import os

DISCORD_WEBHOOKS = [
    {
        'url': os.getenv('DISCORD_WEBHOOK_URL'),
        'name': 'Trading',
        'enabled': True
    }
]
```

Luego:

```bash
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."
```

## 📊 Monitoreo

### Ver estadísticas

```bash
curl http://127.0.0.1:5000/health
```

Respuesta:
```json
{
  "status": "healthy",
  "webhooks": {
    "enabled": true,
    "webhooks_configured": 2,
    "signals_sent": 45,
    "errors": 2,
    "min_confidence": 70,
    "cooldown_duration": 300
  }
}
```

### Logs en Dashboard

El dashboard muestra:
- ✅ Webhook enviado exitosamente
- ❌ Error enviando webhook
- ⏳ Señal en cooldown
- ⚠️ Señal ignorada (baja confianza)

## 🐛 Troubleshooting

### No recibo notificaciones

1. **Verifica que webhooks estén activados:**
   ```python
   WEBHOOKS_ENABLED = True
   ```

2. **Verifica confianza mínima:**
   ```python
   MIN_CONFIDENCE = 60  # Reducir temporalmente
   ```

3. **Verifica cooldown:**
   ```python
   COOLDOWN_DURATION = 60  # Reducir temporalmente
   ```

4. **Ejecuta test:**
   ```bash
   python3 setup_webhooks.py
   ```

### Error "Invalid Webhook"

- Discord: Verifica que la URL sea correcta y el webhook exista
- Telegram: Verifica bot_token y chat_id
- Slack: Regenera el webhook si es necesario

### Error "Rate Limited"

Los servicios tienen límites:
- Discord: ~30 webhooks/minuto
- Telegram: ~30 mensajes/segundo
- Slack: ~1 webhook/segundo

Aumenta `COOLDOWN_DURATION` si recibes muchas señales.

## 🎯 Mejores Prácticas

1. **Empieza con alta confianza** (80%+) y ajusta
2. **Usa cooldown apropiado** para tu estrategia
3. **Prueba con webhook.site** antes de producción
4. **Monitorea estadísticas** regularmente
5. **Filtra por contexto** (alcista/bajista solo)
6. **No uses credenciales reales** en testing
7. **Protege tu configuración** (no subir a Git)

## 📚 Referencias

- [Discord Webhooks](https://discord.com/developers/docs/resources/webhook)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Slack Incoming Webhooks](https://api.slack.com/messaging/webhooks)
- [webhook.site](https://webhook.site/) - Testing

## ✅ Checklist de Configuración

- [ ] Copiar `webhook_config_example.py` a `webhook_config.py`
- [ ] Configurar al menos un webhook (Discord/Telegram/Slack)
- [ ] Ajustar `MIN_CONFIDENCE` a tu preferencia
- [ ] Configurar `COOLDOWN_DURATION` apropiado
- [ ] Filtrar `ALLOWED_SIGNALS` y `ALLOWED_MARKET_CONTEXTS`
- [ ] Ejecutar `python3 setup_webhooks.py` para test
- [ ] Verificar que lleguen notificaciones
- [ ] Agregar `webhook_config.py` a `.gitignore`
- [ ] Reiniciar dashboard
- [ ] Monitorear primeras señales reales

## 🎉 ¡Listo!

Tu sistema de webhooks está configurado. Recibirás notificaciones automáticas cuando se detecten oportunidades de trading con alta confianza en mercados alcistas o bajistas.

Para support adicional, revisa los logs del dashboard o ejecuta los tests de configuración.
