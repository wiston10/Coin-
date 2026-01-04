#!/usr/bin/env python3
"""
Sistema de Webhooks para Notificaciones de Trading
Envía alertas cuando se detectan oportunidades de entrada
"""

import requests
import json
from datetime import datetime
import time
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')


class WebhookNotifier:
    """
    Sistema de notificaciones por webhook para señales de trading
    Soporta: Discord, Telegram, Slack, y webhooks genéricos
    """
    
    def __init__(self):
        self.webhooks = {
            'discord': [],
            'telegram': [],
            'slack': [],
            'generic': []
        }
        
        # Configuración
        self.enabled = True
        self.min_confidence = 60  # Mínimo 60% de confianza para enviar alerta
        self.cooldown = {}  # Para evitar spam
        self.cooldown_duration = 300  # 5 minutos entre alertas del mismo símbolo
        
        # Estadísticas
        self.sent_count = 0
        self.error_count = 0
    
    def add_discord_webhook(self, url: str, name: str = "Discord"):
        """Agrega un webhook de Discord"""
        self.webhooks['discord'].append({
            'url': url,
            'name': name,
            'enabled': True
        })
        print(f"✅ Discord webhook agregado: {name}")
    
    def add_telegram_webhook(self, bot_token: str, chat_id: str, name: str = "Telegram"):
        """Agrega un webhook de Telegram"""
        self.webhooks['telegram'].append({
            'bot_token': bot_token,
            'chat_id': chat_id,
            'name': name,
            'enabled': True
        })
        print(f"✅ Telegram webhook agregado: {name}")
    
    def add_slack_webhook(self, url: str, name: str = "Slack"):
        """Agrega un webhook de Slack"""
        self.webhooks['slack'].append({
            'url': url,
            'name': name,
            'enabled': True
        })
        print(f"✅ Slack webhook agregado: {name}")
    
    def add_generic_webhook(self, url: str, name: str = "Generic", headers: dict = None):
        """Agrega un webhook genérico"""
        self.webhooks['generic'].append({
            'url': url,
            'name': name,
            'headers': headers or {'Content-Type': 'application/json'},
            'enabled': True
        })
        print(f"✅ Webhook genérico agregado: {name}")
    
    def _is_in_cooldown(self, symbol: str) -> bool:
        """Verifica si el símbolo está en cooldown"""
        if symbol in self.cooldown:
            elapsed = time.time() - self.cooldown[symbol]
            return elapsed < self.cooldown_duration
        return False
    
    def _set_cooldown(self, symbol: str):
        """Establece cooldown para un símbolo"""
        self.cooldown[symbol] = time.time()
    
    def _format_discord_message(self, signal_data: dict) -> dict:
        """Formatea mensaje para Discord"""
        signal = signal_data['signal']
        symbol = signal_data['symbol']
        price = signal_data['price']
        confidence = signal_data['confidence']
        market_context = signal_data.get('market_context', 'NEUTRAL')
        pattern = signal_data.get('pattern', 'No Pattern')
        
        # Color según señal
        color = 0x00ff00 if signal == 'BUY' else 0xff0000 if signal == 'SELL' else 0xffaa00
        
        # Emoji según contexto
        emoji = "📈" if market_context == 'ALCISTA' else "📉" if market_context == 'BAJISTA' else "⏸️"
        
        # Recomendación
        if signal == 'BUY' and market_context == 'ALCISTA':
            recommendation = "💰 **COMPRAR EN MERCADO ALCISTA**"
            action = "Entrar en posición LONG"
        elif signal == 'SELL' and market_context == 'BAJISTA':
            recommendation = "💸 **VENDER EN MERCADO BAJISTA**"
            action = "Entrar en posición SHORT"
        elif signal == 'BUY':
            recommendation = "⚠️ Compra con precaución (mercado no alcista)"
            action = "Considerar esperar mejor momento"
        elif signal == 'SELL':
            recommendation = "⚠️ Venta con precaución (mercado no bajista)"
            action = "Considerar esperar mejor momento"
        else:
            recommendation = "⏸️ Mantener posición"
            action = "Esperar señal más clara"
        
        embed = {
            "title": f"{emoji} Señal de Trading: {symbol}",
            "description": recommendation,
            "color": color,
            "fields": [
                {
                    "name": "🎯 Señal",
                    "value": signal,
                    "inline": True
                },
                {
                    "name": "💰 Precio",
                    "value": f"${price:,.2f}",
                    "inline": True
                },
                {
                    "name": "📊 Confianza",
                    "value": f"{confidence}%",
                    "inline": True
                },
                {
                    "name": "📈 Contexto",
                    "value": market_context,
                    "inline": True
                },
                {
                    "name": "🎯 Patrón",
                    "value": pattern,
                    "inline": True
                },
                {
                    "name": "⏱️ Intervalo",
                    "value": signal_data.get('interval', '5m'),
                    "inline": True
                },
                {
                    "name": "💡 Acción Recomendada",
                    "value": action,
                    "inline": False
                }
            ],
            "footer": {
                "text": f"Trading Bot • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # Agregar niveles de soporte/resistencia si están disponibles
        if 'support_levels' in signal_data and signal_data['support_levels']:
            support_text = ", ".join([f"${x:,.2f}" for x in signal_data['support_levels'][:3]])
            embed['fields'].append({
                "name": "🟢 Soportes",
                "value": support_text,
                "inline": False
            })
        
        if 'resistance_levels' in signal_data and signal_data['resistance_levels']:
            resistance_text = ", ".join([f"${x:,.2f}" for x in signal_data['resistance_levels'][:3]])
            embed['fields'].append({
                "name": "🔴 Resistencias",
                "value": resistance_text,
                "inline": False
            })
        
        # Agregar razones
        if 'reasons' in signal_data and signal_data['reasons']:
            reasons_text = "\n".join([f"• {r}" for r in signal_data['reasons'][:5]])
            embed['fields'].append({
                "name": "📋 Razones",
                "value": reasons_text,
                "inline": False
            })
        
        return {
            "embeds": [embed],
            "username": "Trading Bot",
            "avatar_url": "https://cdn-icons-png.flaticon.com/512/891/891462.png"
        }
    
    def _format_telegram_message(self, signal_data: dict) -> str:
        """Formatea mensaje para Telegram"""
        signal = signal_data['signal']
        symbol = signal_data['symbol']
        price = signal_data['price']
        confidence = signal_data['confidence']
        market_context = signal_data.get('market_context', 'NEUTRAL')
        pattern = signal_data.get('pattern', 'No Pattern')
        
        emoji = "📈" if market_context == 'ALCISTA' else "📉" if market_context == 'BAJISTA' else "⏸️"
        
        message = f"{emoji} *SEÑAL DE TRADING*\n\n"
        message += f"*Símbolo:* {symbol}\n"
        message += f"*Señal:* {signal}\n"
        message += f"*Precio:* ${price:,.2f}\n"
        message += f"*Confianza:* {confidence}%\n"
        message += f"*Contexto:* {market_context}\n"
        message += f"*Patrón:* {pattern}\n"
        message += f"*Intervalo:* {signal_data.get('interval', '5m')}\n\n"
        
        # Recomendación
        if signal == 'BUY' and market_context == 'ALCISTA':
            message += "💰 *COMPRAR EN MERCADO ALCISTA*\n"
            message += "Acción: Entrar en posición LONG\n"
        elif signal == 'SELL' and market_context == 'BAJISTA':
            message += "💸 *VENDER EN MERCADO BAJISTA*\n"
            message += "Acción: Entrar en posición SHORT\n"
        else:
            message += "⚠️ *Señal con precaución*\n"
        
        # Niveles
        if 'support_levels' in signal_data and signal_data['support_levels']:
            message += f"\n🟢 *Soportes:* {', '.join([f'${x:,.2f}' for x in signal_data['support_levels'][:3]])}"
        
        if 'resistance_levels' in signal_data and signal_data['resistance_levels']:
            message += f"\n🔴 *Resistencias:* {', '.join([f'${x:,.2f}' for x in signal_data['resistance_levels'][:3]])}"
        
        # Razones
        if 'reasons' in signal_data and signal_data['reasons']:
            message += "\n\n📋 *Razones:*\n"
            for reason in signal_data['reasons'][:5]:
                message += f"• {reason}\n"
        
        message += f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return message
    
    def _send_discord(self, webhook: dict, signal_data: dict) -> bool:
        """Envía notificación a Discord"""
        try:
            message = self._format_discord_message(signal_data)
            response = requests.post(
                webhook['url'],
                json=message,
                timeout=10
            )
            return response.status_code == 204
        except Exception as e:
            print(f"❌ Error enviando a Discord ({webhook['name']}): {e}")
            return False
    
    def _send_telegram(self, webhook: dict, signal_data: dict) -> bool:
        """Envía notificación a Telegram"""
        try:
            message = self._format_telegram_message(signal_data)
            url = f"https://api.telegram.org/bot{webhook['bot_token']}/sendMessage"
            
            response = requests.post(
                url,
                json={
                    'chat_id': webhook['chat_id'],
                    'text': message,
                    'parse_mode': 'Markdown'
                },
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Error enviando a Telegram ({webhook['name']}): {e}")
            return False
    
    def _send_slack(self, webhook: dict, signal_data: dict) -> bool:
        """Envía notificación a Slack"""
        try:
            signal = signal_data['signal']
            symbol = signal_data['symbol']
            price = signal_data['price']
            confidence = signal_data['confidence']
            market_context = signal_data.get('market_context', 'NEUTRAL')
            
            color = "good" if signal == 'BUY' else "danger" if signal == 'SELL' else "warning"
            
            message = {
                "text": f"Señal de Trading: {symbol}",
                "attachments": [{
                    "color": color,
                    "fields": [
                        {"title": "Señal", "value": signal, "short": True},
                        {"title": "Precio", "value": f"${price:,.2f}", "short": True},
                        {"title": "Confianza", "value": f"{confidence}%", "short": True},
                        {"title": "Contexto", "value": market_context, "short": True}
                    ],
                    "footer": "Trading Bot",
                    "ts": int(time.time())
                }]
            }
            
            response = requests.post(
                webhook['url'],
                json=message,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Error enviando a Slack ({webhook['name']}): {e}")
            return False
    
    def _send_generic(self, webhook: dict, signal_data: dict) -> bool:
        """Envía notificación a webhook genérico"""
        try:
            response = requests.post(
                webhook['url'],
                json=signal_data,
                headers=webhook.get('headers', {}),
                timeout=10
            )
            return response.status_code in [200, 201, 204]
        except Exception as e:
            print(f"❌ Error enviando a webhook genérico ({webhook['name']}): {e}")
            return False
    
    def send_signal(self, signal_data: dict, force_send: bool = False) -> Dict[str, int]:
        """
        Envía señal de trading a todos los webhooks configurados
        
        Args:
            signal_data: Diccionario con:
                - symbol: Símbolo del activo
                - signal: BUY/SELL/HOLD
                - price: Precio actual
                - confidence: Confianza de la señal (0-100)
                - market_context: ALCISTA/BAJISTA/NEUTRAL
                - pattern: Patrón de vela detectado
                - interval: Intervalo de tiempo
                - support_levels: Lista de soportes
                - resistance_levels: Lista de resistencias
                - reasons: Lista de razones
            force_send: Si True, ignora filtros de confianza, cooldown y HOLD
        
        Returns:
            Dict con contadores de éxito/error
        """
        if not self.enabled:
            return {'success': 0, 'error': 0, 'skipped': 1}
        
        if not force_send:
            # Verificar confianza mínima
            confidence = signal_data.get('confidence', 0)
            if confidence < self.min_confidence:
                print(f"⚠️ Señal ignorada: confianza {confidence}% < {self.min_confidence}%")
                return {'success': 0, 'error': 0, 'skipped': 1}
            
            # Verificar cooldown
            symbol = signal_data['symbol']
            if self._is_in_cooldown(symbol):
                print(f"⏳ Señal ignorada: {symbol} en cooldown")
                return {'success': 0, 'error': 0, 'skipped': 1}
            
            # Solo enviar señales de compra/venta, no HOLD
            if signal_data['signal'] == 'HOLD':
                return {'success': 0, 'error': 0, 'skipped': 1}
        
        results = {'success': 0, 'error': 0, 'skipped': 0}
        
        # Enviar a Discord
        for webhook in self.webhooks['discord']:
            if webhook['enabled']:
                if self._send_discord(webhook, signal_data):
                    results['success'] += 1
                    print(f"✅ Enviado a Discord: {webhook['name']}")
                else:
                    results['error'] += 1
        
        # Enviar a Telegram
        for webhook in self.webhooks['telegram']:
            if webhook['enabled']:
                if self._send_telegram(webhook, signal_data):
                    results['success'] += 1
                    print(f"✅ Enviado a Telegram: {webhook['name']}")
                else:
                    results['error'] += 1
        
        # Enviar a Slack
        for webhook in self.webhooks['slack']:
            if webhook['enabled']:
                if self._send_slack(webhook, signal_data):
                    results['success'] += 1
                    print(f"✅ Enviado a Slack: {webhook['name']}")
                else:
                    results['error'] += 1
        
        # Enviar a webhooks genéricos
        for webhook in self.webhooks['generic']:
            if webhook['enabled']:
                if self._send_generic(webhook, signal_data):
                    results['success'] += 1
                    print(f"✅ Enviado a webhook: {webhook['name']}")
                else:
                    results['error'] += 1
        
        # Actualizar estadísticas
        if results['success'] > 0:
            self.sent_count += 1
            symbol = signal_data.get('symbol', '')
            if symbol:
                self._set_cooldown(symbol)
        
        self.error_count += results['error']
        
        return results
    
    def get_stats(self) -> dict:
        """Obtiene estadísticas de envíos"""
        total_webhooks = sum(len(hooks) for hooks in self.webhooks.values())
        
        return {
            'enabled': self.enabled,
            'webhooks_configured': total_webhooks,
            'signals_sent': self.sent_count,
            'errors': self.error_count,
            'min_confidence': self.min_confidence,
            'cooldown_duration': self.cooldown_duration
        }


if __name__ == '__main__':
    print("=" * 80)
    print("🔔 SISTEMA DE WEBHOOKS - TEST")
    print("=" * 80)
    
    # Crear notificador
    notifier = WebhookNotifier()
    
    # Agregar webhook de ejemplo (descomentarlos con tus URLs reales)
    # notifier.add_discord_webhook("https://discord.com/api/webhooks/YOUR_WEBHOOK", "Canal Trading")
    # notifier.add_telegram_webhook("YOUR_BOT_TOKEN", "YOUR_CHAT_ID", "Alertas Trading")
    
    # Agregar webhook genérico de prueba (webhook.site)
    print("\n📝 Para probar, crea un webhook en: https://webhook.site/")
    print("   Luego usa: notifier.add_generic_webhook('TU_URL', 'Test')\n")
    
    # Señal de ejemplo
    test_signal = {
        'symbol': 'BTC-USD',
        'signal': 'BUY',
        'price': 92450.50,
        'confidence': 85,
        'market_context': 'ALCISTA',
        'pattern': 'Hammer',
        'interval': '5m',
        'support_levels': [91000, 90500, 90000],
        'resistance_levels': [93000, 94000, 95000],
        'reasons': [
            'RSI indica sobreventa',
            'Precio rebota en soporte',
            'Volumen creciente',
            'Patrón alcista confirmado'
        ]
    }
    
    print("\n📊 Señal de ejemplo:")
    print(json.dumps(test_signal, indent=2))
    
    print("\n✅ Sistema de webhooks listo!")
    print("   Configura tus webhooks y llama a notifier.send_signal(signal_data)")
