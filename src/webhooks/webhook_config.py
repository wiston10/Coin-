# Configuración de Webhooks para Telegram
import os
from src.env_loader import load_env

load_env()
# Este archivo contiene la configuración para enviar alertas de trading a tu grupo

# ============================================================================
# TELEGRAM - Configuración para tu grupo
# ============================================================================

# PASO 1: Crear un bot (si aún no lo tienes)
# 1. Abre Telegram y busca @BotFather
# 2. Envía el comando: /newbot
# 3. Dale un nombre y username a tu bot
# 4. BotFather te dará un TOKEN como: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz
# 5. COPIA ESE TOKEN en el archivo .env como TELEGRAM_BOT_TOKEN=...
#    (copia .env.example a .env; .env está en .gitignore y no se sube a GitHub)

# PASO 2: Agregar el bot a tu grupo
# 1. Ve a tu grupo de Telegram
# 2. Click en el nombre del grupo → "Agregar miembros"
# 3. Busca el nombre de tu bot y agrégalo al grupo
# 4. Dale permisos de administrador (opcional pero recomendado)

# PASO 3: Obtener el chat_id de tu grupo
# 1. Envía un mensaje cualquiera en tu grupo
# 2. Ve a esta URL en tu navegador (reemplaza TU_BOT_TOKEN):
#    https://api.telegram.org/botTU_BOT_TOKEN/getUpdates
# 3. Busca "chat":{"id": y verás un número negativo (ej: -1001234567890)
# 4. ESE ES TU chat_id, ponlo en .env como TELEGRAM_CHAT_ID=...

TELEGRAM_WEBHOOKS = [
    {
        # Token del bot (de @BotFather)
        'bot_token': os.environ.get('TELEGRAM_BOT_TOKEN', ''),  # definir en .env, NUNCA en el código
        
        # ID del grupo (número negativo, ej: -1001234567890)
        'chat_id': os.environ.get('TELEGRAM_CHAT_ID', ''),
        
        # Nombre descriptivo
        'name': 'Bot',
        
        # Mantener en True para activar
        'enabled': bool(os.environ.get('TELEGRAM_BOT_TOKEN')),
    }
]

# ============================================================================
# OTROS WEBHOOKS (Opcional - puedes dejar estos vacíos)
# ============================================================================

DISCORD_WEBHOOKS = []
SLACK_WEBHOOKS = []
GENERIC_WEBHOOKS = []

# ============================================================================
# CONFIGURACIÓN DE ALERTAS
# ============================================================================

# Activar sistema de webhooks
WEBHOOKS_ENABLED = True

# Confianza mínima para enviar alerta (0-100)
# 70 = solo señales con alta confianza
MIN_CONFIDENCE = 70

# Tiempo mínimo entre alertas del mismo símbolo (en segundos)
# 300 = 5 minutos (evita spam)
COOLDOWN_DURATION = 300

# Solo enviar alertas en estos contextos de mercado
# ['ALCISTA'] = solo compras en alcista
# ['BAJISTA'] = solo ventas en bajista
# ['ALCISTA', 'BAJISTA'] = ambos (recomendado)
ALLOWED_MARKET_CONTEXTS = ['ALCISTA', 'BAJISTA']

# Solo enviar estas señales
# ['BUY', 'SELL'] = compras y ventas (recomendado)
# No incluir 'HOLD' para evitar señales sin acción
ALLOWED_SIGNALS = ['BUY', 'SELL']
