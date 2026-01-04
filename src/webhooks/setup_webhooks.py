#!/usr/bin/env python3
"""
Script para configurar webhooks desde archivo de configuración
"""

from src.webhooks.webhook_notifier import WebhookNotifier


def load_webhooks_from_config(notifier: WebhookNotifier):
    """
    Carga webhooks desde archivo de configuración
    """
    try:
        import webhook_config as config
        
        # Configuración general
        notifier.enabled = config.WEBHOOKS_ENABLED
        notifier.min_confidence = config.MIN_CONFIDENCE
        notifier.cooldown_duration = config.COOLDOWN_DURATION
        
        print("=" * 80)
        print("🔔 CONFIGURANDO WEBHOOKS")
        print("=" * 80)
        print(f"Estado: {'✅ ACTIVADO' if notifier.enabled else '❌ DESACTIVADO'}")
        print(f"Confianza mínima: {notifier.min_confidence}%")
        print(f"Cooldown: {notifier.cooldown_duration}s")
        print()
        
        # Cargar Discord webhooks
        for webhook in config.DISCORD_WEBHOOKS:
            if webhook.get('enabled', True):
                notifier.add_discord_webhook(
                    webhook['url'],
                    webhook.get('name', 'Discord')
                )
        
        # Cargar Telegram webhooks
        for webhook in config.TELEGRAM_WEBHOOKS:
            if webhook.get('enabled', True):
                notifier.add_telegram_webhook(
                    webhook['bot_token'],
                    webhook['chat_id'],
                    webhook.get('name', 'Telegram')
                )
        
        # Cargar Slack webhooks
        for webhook in config.SLACK_WEBHOOKS:
            if webhook.get('enabled', True):
                notifier.add_slack_webhook(
                    webhook['url'],
                    webhook.get('name', 'Slack')
                )
        
        # Cargar webhooks genéricos
        for webhook in config.GENERIC_WEBHOOKS:
            if webhook.get('enabled', True):
                notifier.add_generic_webhook(
                    webhook['url'],
                    webhook.get('name', 'Generic'),
                    webhook.get('headers')
                )
        
        print()
        print("=" * 80)
        print(f"✅ Configuración cargada exitosamente")
        print("=" * 80)
        
        return True
        
    except ImportError:
        print("=" * 80)
        print("⚠️  ARCHIVO webhook_config.py NO ENCONTRADO")
        print("=" * 80)
        print()
        print("📝 Para configurar webhooks:")
        print("   1. Copia webhook_config_example.py a webhook_config.py")
        print("   2. Edita webhook_config.py con tus URLs y tokens")
        print("   3. Reinicia el dashboard")
        print()
        print("O usa la API REST:")
        print("   POST /api/webhooks/config con JSON:")
        print("   {")
        print('     "type": "discord",')
        print('     "url": "https://discord.com/api/webhooks/...",')
        print('     "name": "Canal Trading"')
        print("   }")
        print()
        print("=" * 80)
        return False
    
    except Exception as e:
        print(f"❌ Error cargando configuración: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    # Test de carga de configuración
    notifier = WebhookNotifier()
    
    if load_webhooks_from_config(notifier):
        print("\n🧪 Ejecutando test...")
        
        # Señal de prueba
        test_signal = {
            'symbol': 'BTC-USD',
            'signal': 'BUY',
            'price': 92450.50,
            'confidence': 85,
            'market_context': 'ALCISTA',
            'pattern': 'Hammer',
            'interval': '5m',
            'support_levels': [91000, 90500],
            'resistance_levels': [93000, 94000],
            'reasons': ['Test de configuración']
        }
        
        print("\n📤 Enviando señal de prueba...")
        results = notifier.send_signal(test_signal)
        
        print(f"\n✅ Exitosos: {results['success']}")
        print(f"❌ Errores: {results['error']}")
        print(f"⏭️  Omitidos: {results['skipped']}")
        
        if results['success'] > 0:
            print("\n🎉 ¡Webhooks funcionando correctamente!")
        elif results['skipped'] > 0:
            print("\n⚠️  Señal omitida (verifica confianza mínima o cooldown)")
        else:
            print("\n❌ Todos los webhooks fallaron (verifica URLs y tokens)")
