#!/usr/bin/env python3
"""
Dashboard Web para Trading en Tiempo Real
Muestra análisis de múltiples activos con actualización automática
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import threading
import time
from datetime import datetime
import json
import pandas as pd
import numpy as np
import os
from pathlib import Path

from src.data_sources.hybrid_data_source import HybridDataSource
from src.indicators.technical_indicators import calculate_adaptive_indicators
from src.strategies.bounce_strategy import analyze_bounce_opportunity
from src.core.trading_signals import TradingSignalEngine
from src.webhooks.webhook_notifier import WebhookNotifier

# Configurar rutas para templates
base_dir = Path(__file__).parent.parent.parent
template_dir = base_dir / 'templates'

app = Flask(__name__, template_folder=str(template_dir))
CORS(app)

# Sistema de webhooks global
webhook_notifier = WebhookNotifier()

# Cargar webhooks de Telegram desde configuración
try:
    from src.webhooks.webhook_config import TELEGRAM_WEBHOOKS
    for webhook in TELEGRAM_WEBHOOKS:
        if webhook.get('enabled', False):
            webhook_notifier.add_telegram_webhook(
                bot_token=webhook['bot_token'],
                chat_id=webhook['chat_id'],
                name=webhook.get('name', 'Telegram')
            )
            print(f"✅ Webhook de Telegram cargado: {webhook.get('name', 'Telegram')}")
except ImportError:
    print("⚠️ No se encontró configuración de webhooks de Telegram")
except Exception as e:
    print(f"❌ Error cargando webhooks de Telegram: {e}")

# Sistema de monitoreo automático
auto_monitor = {
    'active': {},  # {symbol: {'thread': thread_obj, 'stop_flag': bool, 'interval': str, 'started_at': datetime}}
    'lock': threading.Lock()
}

# Cache de datos para evitar requests excesivos
cache = {
    'last_update': {},
    'data': {}
}
CACHE_DURATION = 30  # 30 segundos para evitar rate limiting de yfinance

# Configuración completa de activos por categoría (mínimo 20 por categoría)
ASSET_CATEGORIES = {
    'crypto': [
        {'symbol': 'BTC-USD', 'name': 'Bitcoin'},
        {'symbol': 'ETH-USD', 'name': 'Ethereum'},
        {'symbol': 'SOL-USD', 'name': 'Solana'},
        {'symbol': 'MATIC-USD', 'name': 'Polygon'},
        {'symbol': 'ADA-USD', 'name': 'Cardano'},
        {'symbol': 'DOT-USD', 'name': 'Polkadot'},
        {'symbol': 'AVAX-USD', 'name': 'Avalanche'},
        {'symbol': 'LINK-USD', 'name': 'Chainlink'},
        {'symbol': 'UNI-USD', 'name': 'Uniswap'},
        {'symbol': 'LTC-USD', 'name': 'Litecoin'},
        {'symbol': 'XRP-USD', 'name': 'Ripple'},
        {'symbol': 'ATOM-USD', 'name': 'Cosmos'},
        {'symbol': 'XLM-USD', 'name': 'Stellar'},
        {'symbol': 'ALGO-USD', 'name': 'Algorand'},
        {'symbol': 'VET-USD', 'name': 'VeChain'},
        {'symbol': 'ICP-USD', 'name': 'Internet Computer'},
        {'symbol': 'FIL-USD', 'name': 'Filecoin'},
        {'symbol': 'NEAR-USD', 'name': 'NEAR Protocol'},
        {'symbol': 'AAVE-USD', 'name': 'Aave'},
        {'symbol': 'GRT-USD', 'name': 'The Graph'},
    ],
    'stocks': [
        {'symbol': 'AAPL', 'name': 'Apple'},
        {'symbol': 'MSFT', 'name': 'Microsoft'},
        {'symbol': 'GOOGL', 'name': 'Google'},
        {'symbol': 'AMZN', 'name': 'Amazon'},
        {'symbol': 'TSLA', 'name': 'Tesla'},
        {'symbol': 'NVDA', 'name': 'NVIDIA'},
        {'symbol': 'META', 'name': 'Meta'},
        {'symbol': 'NFLX', 'name': 'Netflix'},
        {'symbol': 'AMD', 'name': 'AMD'},
        {'symbol': 'INTC', 'name': 'Intel'},
        {'symbol': 'BABA', 'name': 'Alibaba'},
        {'symbol': 'JPM', 'name': 'JPMorgan'},
        {'symbol': 'V', 'name': 'Visa'},
        {'symbol': 'WMT', 'name': 'Walmart'},
        {'symbol': 'DIS', 'name': 'Disney'},
        {'symbol': 'BA', 'name': 'Boeing'},
        {'symbol': 'PYPL', 'name': 'PayPal'},
        {'symbol': 'ADBE', 'name': 'Adobe'},
        {'symbol': 'CRM', 'name': 'Salesforce'},
        {'symbol': 'ORCL', 'name': 'Oracle'},
    ],
    'forex': [
        {'symbol': 'EUR-USD', 'name': 'EUR/USD'},
        {'symbol': 'GBP-USD', 'name': 'GBP/USD'},
        {'symbol': 'USD-JPY', 'name': 'USD/JPY'},
        {'symbol': 'USD-CAD', 'name': 'USD/CAD'},
        {'symbol': 'AUD-USD', 'name': 'AUD/USD'},
        {'symbol': 'NZD-USD', 'name': 'NZD/USD'},
        {'symbol': 'USD-CHF', 'name': 'USD/CHF'},
        {'symbol': 'EUR-GBP', 'name': 'EUR/GBP'},
        {'symbol': 'EUR-JPY', 'name': 'EUR/JPY'},
        {'symbol': 'GBP-JPY', 'name': 'GBP/JPY'},
        {'symbol': 'AUD-JPY', 'name': 'AUD/JPY'},
        {'symbol': 'EUR-CHF', 'name': 'EUR/CHF'},
        {'symbol': 'GBP-CHF', 'name': 'GBP/CHF'},
        {'symbol': 'CAD-JPY', 'name': 'CAD/JPY'},
        {'symbol': 'NZD-JPY', 'name': 'NZD/JPY'},
        {'symbol': 'EUR-AUD', 'name': 'EUR/AUD'},
        {'symbol': 'GBP-AUD', 'name': 'GBP/AUD'},
        {'symbol': 'EUR-CAD', 'name': 'EUR/CAD'},
        {'symbol': 'AUD-CAD', 'name': 'AUD/CAD'},
        {'symbol': 'CHF-JPY', 'name': 'CHF/JPY'},
    ],
    'indices': [
        {'symbol': 'SPY', 'name': 'S&P 500'},
        {'symbol': 'QQQ', 'name': 'Nasdaq 100'},
        {'symbol': 'DIA', 'name': 'Dow Jones'},
        {'symbol': 'IWM', 'name': 'Russell 2000'},
        {'symbol': 'VIX', 'name': 'Volatility Index'},
        {'symbol': 'EEM', 'name': 'Emerging Markets'},
        {'symbol': 'EFA', 'name': 'EAFE Index'},
        {'symbol': 'XLF', 'name': 'Financial Sector'},
        {'symbol': 'XLE', 'name': 'Energy Sector'},
        {'symbol': 'XLK', 'name': 'Technology Sector'},
        {'symbol': 'XLV', 'name': 'Health Care'},
        {'symbol': 'XLP', 'name': 'Consumer Staples'},
        {'symbol': 'XLY', 'name': 'Consumer Discret.'},
        {'symbol': 'XLI', 'name': 'Industrials'},
        {'symbol': 'XLB', 'name': 'Materials'},
        {'symbol': 'XLRE', 'name': 'Real Estate'},
        {'symbol': 'XLU', 'name': 'Utilities'},
        {'symbol': 'VTI', 'name': 'Total Stock Market'},
        {'symbol': 'VOO', 'name': 'Vanguard S&P 500'},
        {'symbol': 'AGG', 'name': 'Bond Aggregate'},
    ],
    'commodities': [
        {'symbol': 'GOLD', 'name': 'Gold'},
        {'symbol': 'SILVER', 'name': 'Silver'},
        {'symbol': 'OIL', 'name': 'Crude Oil'},
        {'symbol': 'GLD', 'name': 'Gold ETF'},
        {'symbol': 'SLV', 'name': 'Silver ETF'},
        {'symbol': 'USO', 'name': 'Oil ETF'},
        {'symbol': 'UNG', 'name': 'Natural Gas'},
        {'symbol': 'DBA', 'name': 'Agriculture'},
        {'symbol': 'CORN', 'name': 'Corn'},
        {'symbol': 'WEAT', 'name': 'Wheat'},
        {'symbol': 'SOYB', 'name': 'Soybeans'},
        {'symbol': 'UGA', 'name': 'Gasoline'},
        {'symbol': 'BNO', 'name': 'Brent Oil'},
        {'symbol': 'PALL', 'name': 'Palladium'},
        {'symbol': 'PPLT', 'name': 'Platinum'},
        {'symbol': 'CPER', 'name': 'Copper'},
        {'symbol': 'JJC', 'name': 'Copper ETN'},
        {'symbol': 'JJN', 'name': 'Nickel'},
        {'symbol': 'JJT', 'name': 'Tin'},
        {'symbol': 'JO', 'name': 'Coffee'},
    ]
}

# Activos predeterminados (primeros 3 de cada categoría)
DEFAULT_ASSETS = (
    [{'symbol': a['symbol'], 'name': a['name'], 'type': 'crypto'} for a in ASSET_CATEGORIES['crypto'][:3]] +
    [{'symbol': a['symbol'], 'name': a['name'], 'type': 'stock'} for a in ASSET_CATEGORIES['stocks'][:2]] +
    [{'symbol': a['symbol'], 'name': a['name'], 'type': 'forex'} for a in ASSET_CATEGORIES['forex'][:1]] +
    [{'symbol': a['symbol'], 'name': a['name'], 'type': 'index'} for a in ASSET_CATEGORIES['indices'][:1]]
)

DEFAULT_INTERVALS = ['1m', '5m', '15m', '1h']

# Sistema híbrido que combina web scraping + yfinance
hybrid_source = HybridDataSource()
signal_engine = TradingSignalEngine()


def analyze_asset(symbol, interval='5m', use_binomo_fallback=False):
    """Analiza un activo y retorna los resultados"""
    try:
        # Obtener datos usando sistema híbrido (auto-detecta crypto/stock/forex)
        if use_binomo_fallback:
            # Usar Binomo como fallback si la fuente principal falla
            df = hybrid_source.get_data_with_binomo_fallback(symbol, interval, limit=500)
        else:
            df = hybrid_source.get_live_data(symbol, interval, limit=500)
        
        if df is None or len(df) == 0:
            return None
        
        # Calcular indicadores
        df = calculate_adaptive_indicators(df, interval)
        
        # Obtener precio agregado multi-broker con información de calidad
        price_data = hybrid_source.get_aggregated_price(symbol)
        current_price = price_data['price']
        data_quality = price_data['quality']
        data_confidence = price_data['confidence']
        sources_used = price_data['sources_used']
        
        # Fallback al ticker si no hay datos agregados
        if current_price is None or current_price == 0:
            ticker = hybrid_source.get_realtime_ticker(symbol)
            current_price = ticker.get('price', df['Close'].iloc[-1])
            data_quality = 'Unknown'
            data_confidence = 0.5
            sources_used = 1
        
        # Análisis de rebote (estrategia principal)
        bounce_result = analyze_bounce_opportunity(
            df, 
            interval=interval,
            trading_type='scalping' if interval in ['1m', '5m'] else 'medium_term'
        )
        
        # Análisis técnico adicional para contexto
        last_row = df.iloc[-1]
        
        # Determinar tendencia del precio
        if len(df) >= 20:
            sma_20 = df['Close'].rolling(20).mean().iloc[-1]
            if current_price > sma_20 * 1.02:
                trend = 'BULLISH'
            elif current_price < sma_20 * 0.98:
                trend = 'BEARISH'
            else:
                trend = 'NEUTRAL'
        else:
            trend = 'NEUTRAL'
        
        # Determinar volatilidad
        if 'ATR' in df.columns and pd.notna(last_row.get('ATR')):
            atr_pct = (last_row['ATR'] / current_price) * 100
            if atr_pct > 2.5:
                volatility = 'ALTA'
            elif atr_pct > 1.5:
                volatility = 'MEDIA'
            else:
                volatility = 'BAJA'
        else:
            volatility = 'MEDIA'
        
        # Determinar estado del volumen
        if len(df) >= 20:
            avg_volume = df['Volume'].rolling(20).mean().iloc[-1]
            current_volume = df['Volume'].iloc[-1]
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
            
            if volume_ratio > 1.5:
                volume_status = 'ALTO'
            elif volume_ratio > 0.8:
                volume_status = 'NORMAL'
            else:
                volume_status = 'BAJO'
        else:
            volume_status = 'NORMAL'
        
            # Detectar tipo de activo y fuente de datos
        asset_type = hybrid_source.detect_asset_type(symbol)
        data_source = df['source'].iloc[-1] if 'source' in df.columns else 'unknown'
        
        # Compilar resultado completo
        result = {
            'symbol': symbol,
            'interval': interval,
            'timestamp': datetime.now().isoformat(),
            'price': float(current_price),
            'change_24h': ticker.get('change_24h', 0),
            'volume_24h': ticker.get('volume_24h', 0),
            'bid': ticker.get('bid', current_price),
            'ask': ticker.get('ask', current_price),
            'asset_type': asset_type,
            'data_source': data_source,
            
            # ✨ NUEVO: Calidad de datos multi-broker
            'data_quality': data_quality,
            'data_confidence': float(data_confidence),
            'sources_used': sources_used,
            
            # Señal y confianza
            'signal': bounce_result['signal'],
            'confidence': float(bounce_result['confidence']),
            'bounce_probability': float(bounce_result.get('bounce_probability', 0)),
            
            # Niveles de trading
            'entry_price': float(bounce_result['entry_price']),
            'take_profit': float(bounce_result['take_profit']),
            'stop_loss': float(bounce_result['stop_loss']),
            'risk_reward': float(bounce_result['risk_reward']),
            
            # Contexto del mercado
            'trend': trend,
            'volatility': volatility,
            'volume_status': volume_status,
            'volume_signal': bounce_result.get('volume_signal', 'NORMAL'),
            'momentum_signal': bounce_result.get('momentum_signal', 'NEUTRAL'),
            
            # Psicología y patrones
            'pattern': bounce_result.get('pattern', 'No Pattern'),
            'sentiment': bounce_result['psychology']['sentiment'],
            'psychology_desc': bounce_result['psychology']['description'],
            'psychology_score': bounce_result['psychology'].get('score', 0),
            
            # Niveles clave
            'key_levels': {
                'support': [float(x) for x in bounce_result.get('support_levels', [])[:3]],
                'resistance': [float(x) for x in bounce_result.get('resistance_levels', [])[:3]]
            },
            
            # Estadísticas
            'historical_success_rate': float(bounce_result.get('historical_success_rate', 0)),
            'expected_hold_time': bounce_result.get('expected_hold_time', ''),
            'reasons': bounce_result.get('reasons', [])
        }
        
        # Enviar webhook si hay señal de compra/venta con alta confianza
        if result['signal'] in ['BUY', 'SELL'] and result['confidence'] >= webhook_notifier.min_confidence:
            webhook_data = {
                'symbol': result['symbol'],
                'signal': result['signal'],
                'price': result['price'],
                'confidence': result['confidence'],
                'market_context': result['trend'],
                'pattern': result['pattern'],
                'interval': result['interval'],
                'support_levels': result['key_levels']['support'],
                'resistance_levels': result['key_levels']['resistance'],
                'reasons': result['reasons']
            }
            
            # Enviar en segundo plano para no bloquear
            threading.Thread(
                target=webhook_notifier.send_signal,
                args=(webhook_data,),
                daemon=True
            ).start()
        
        return result
        
    except Exception as e:
        print(f"❌ Error analizando {symbol}: {e}")
        return None


def get_cached_data(symbol, interval, use_binomo_fallback=False):
    """Obtiene datos del cache si están disponibles"""
    cache_key = f"{symbol}_{interval}_{'binomo' if use_binomo_fallback else 'normal'}"
    now = time.time()
    
    if cache_key in cache['last_update']:
        last_update = cache['last_update'][cache_key]
        if now - last_update < CACHE_DURATION:
            return cache['data'].get(cache_key)
    
    # Datos no en cache o expirados
    result = analyze_asset(symbol, interval, use_binomo_fallback)
    
    if result:
        cache['last_update'][cache_key] = now
        cache['data'][cache_key] = result
    
    return result


@app.route('/')
def index():
    """Página principal del dashboard"""
    return render_template('dashboard.html')


@app.route('/api/assets')
def get_assets():
    """Obtiene lista de activos disponibles"""
    return jsonify({
        'assets': DEFAULT_ASSETS,
        'intervals': DEFAULT_INTERVALS
    })


@app.route('/api/categories')
def get_categories():
    """Obtiene todas las categorías y sus activos"""
    return jsonify({
        'categories': ASSET_CATEGORIES,
        'intervals': DEFAULT_INTERVALS
    })


@app.route('/api/analyze-category/<category>')
def analyze_category(category):
    """Analiza todos los activos de una categoría con rate limiting"""
    import time
    
    interval = request.args.get('interval', '5m')
    
    if category not in ASSET_CATEGORIES:
        return jsonify({'error': 'Categoría no válida'}), 400
    
    results = []
    
    # Procesar en lotes pequeños con delay para evitar rate limiting
    for i, asset in enumerate(ASSET_CATEGORIES[category]):
        result = get_cached_data(asset['symbol'], interval)
        if result:
            result['name'] = asset['name']
            result['category'] = category
            results.append(result)
        
        # Delay entre activos si no está en caché (especialmente para forex/stocks)
        if i < len(ASSET_CATEGORIES[category]) - 1 and not result:
            time.sleep(0.3)  # 300ms delay entre requests fallidos
    
    return jsonify({
        'category': category,
        'assets': results,
        'total': len(ASSET_CATEGORIES[category]),
        'loaded': len(results),
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/analyze/<symbol>')
def analyze(symbol):
    """Analiza un activo específico"""
    interval = request.args.get('interval', '5m')
    use_binomo = request.args.get('binomo', 'false').lower() == 'true'
    
    result = get_cached_data(symbol, interval, use_binomo_fallback=use_binomo)
    
    if result:
        return jsonify(result)
    else:
        return jsonify({'error': 'No se pudieron obtener datos'}), 500


@app.route('/api/compare-sources/<symbol>')
def compare_sources_endpoint(symbol):
    """Compara todas las fuentes de datos para un símbolo"""
    interval = request.args.get('interval', '5m')
    
    try:
        comparison = hybrid_source.compare_sources(symbol, interval)
        return jsonify({
            'symbol': symbol,
            'interval': interval,
            'sources': comparison,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/analyze-all')
def analyze_all():
    """Analiza todos los activos configurados"""
    interval = request.args.get('interval', '5m')
    
    results = []
    for asset in DEFAULT_ASSETS:
        result = get_cached_data(asset['symbol'], interval)
        if result:
            result['name'] = asset['name']
            results.append(result)
    
    return jsonify({
        'assets': results,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/multi-timeframe/<symbol>')
def multi_timeframe(symbol):
    """Análisis multi-timeframe de un activo"""
    results = {}
    
    for interval in DEFAULT_INTERVALS:
        result = get_cached_data(symbol, interval)
        if result:
            results[interval] = result
    
    return jsonify({
        'symbol': symbol,
        'timeframes': results,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/ticker/<symbol>')
def get_ticker(symbol):
    """Obtiene datos de ticker en tiempo real (híbrido)"""
    try:
        ticker = hybrid_source.get_realtime_ticker(symbol)
        return jsonify(ticker)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/available-assets')
def get_available_assets():
    """Obtiene todos los activos disponibles agrupados por tipo"""
    try:
        assets = hybrid_source.get_available_assets()
        return jsonify(assets)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/compare-sources/<symbol>')
def compare_sources(symbol):
    """Compara datos de diferentes fuentes (solo crypto)"""
    try:
        interval = request.args.get('interval', '5m')
        comparison = hybrid_source.compare_sources(symbol, interval)
        return jsonify(comparison)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/price-quality/<symbol>')
def get_price_quality(symbol):
    """Obtiene precio agregado de múltiples fuentes con información de calidad"""
    try:
        result = hybrid_source.get_aggregated_price(symbol)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/broker-stats')
def get_broker_stats():
    """Obtiene estadísticas de uso de brokers/fuentes"""
    try:
        from src.data_sources.multi_broker_client import multi_broker
        stats = multi_broker.get_statistics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/webhooks/config', methods=['GET', 'POST'])
def webhook_config():
    """Configuración de webhooks"""
    if request.method == 'GET':
        # Obtener configuración actual
        stats = webhook_notifier.get_stats()
        return jsonify(stats)
    
    elif request.method == 'POST':
        # Agregar o modificar webhook
        data = request.json
        webhook_type = data.get('type')
        
        try:
            if webhook_type == 'discord':
                webhook_notifier.add_discord_webhook(
                    data['url'],
                    data.get('name', 'Discord')
                )
            elif webhook_type == 'telegram':
                webhook_notifier.add_telegram_webhook(
                    data['bot_token'],
                    data['chat_id'],
                    data.get('name', 'Telegram')
                )
            elif webhook_type == 'slack':
                webhook_notifier.add_slack_webhook(
                    data['url'],
                    data.get('name', 'Slack')
                )
            elif webhook_type == 'generic':
                webhook_notifier.add_generic_webhook(
                    data['url'],
                    data.get('name', 'Generic'),
                    data.get('headers')
                )
            else:
                return jsonify({'error': 'Tipo de webhook no válido'}), 400
            
            return jsonify({
                'success': True,
                'message': f'Webhook {webhook_type} agregado'
            })
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500


@app.route('/api/webhooks/toggle', methods=['POST'])
def webhook_toggle():
    """Activa/desactiva webhooks"""
    data = request.json
    webhook_notifier.enabled = data.get('enabled', True)
    
    return jsonify({
        'success': True,
        'enabled': webhook_notifier.enabled
    })


@app.route('/api/webhooks/test', methods=['POST'])
def webhook_test():
    """Envía un webhook de prueba"""
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
        'reasons': ['Test de webhook', 'Verificación de sistema']
    }
    
    results = webhook_notifier.send_signal(test_signal)
    
    return jsonify({
        'success': True,
        'results': results
    })


def monitor_asset_loop(symbol, interval='5m'):
    """Función que monitorea un activo y envía notificaciones cada minuto"""
    print(f"🔔 Iniciando monitoreo automático: {symbol} ({interval})")
    
    while True:
        # Verificar si debe detenerse
        with auto_monitor['lock']:
            if symbol not in auto_monitor['active'] or auto_monitor['active'][symbol]['stop_flag']:
                print(f"⏹️  Deteniendo monitoreo: {symbol}")
                break
        
        try:
            # Analizar activo
            result = analyze_asset(symbol, interval, use_binomo_fallback=True)
            
            if result:
                # Preparar datos del webhook
                webhook_data = {
                    'symbol': result['symbol'],
                    'signal': result['signal'],
                    'price': result['price'],
                    'confidence': result['confidence'],
                    'market_context': result['trend'],
                    'pattern': result['pattern'],
                    'interval': result['interval'],
                    'support_levels': result['key_levels']['support'],
                    'resistance_levels': result['key_levels']['resistance'],
                    'reasons': result['reasons']
                }
                
                # Enviar notificación con force_send=True para ignorar filtros
                results = webhook_notifier.send_signal(webhook_data, force_send=True)
                
                if results['success'] > 0:
                    print(f"✅ Notificación enviada a Telegram: {symbol} | {result['signal']} @ ${result['price']:,.2f} | {result['confidence']}%")
                elif results['error'] > 0:
                    print(f"❌ Error enviando notificación: {symbol}")
                else:
                    print(f"⏭️ Webhooks desactivados o sin configurar: {symbol}")
            
        except Exception as e:
            print(f"❌ Error monitoreando {symbol}: {e}")
        
        # Esperar 60 segundos antes de la próxima notificación
        time.sleep(60)


@app.route('/api/auto-monitor/start', methods=['POST'])
def start_auto_monitor():
    """Inicia monitoreo automático de un activo"""
    data = request.get_json()
    symbol = data.get('symbol')
    interval = data.get('interval', '5m')
    
    if not symbol:
        return jsonify({'error': 'Symbol is required'}), 400
    
    with auto_monitor['lock']:
        # Si ya está monitoreando, detenerlo primero
        if symbol in auto_monitor['active']:
            auto_monitor['active'][symbol]['stop_flag'] = True
            time.sleep(0.5)  # Dar tiempo para que se detenga
        
        # Crear nuevo thread de monitoreo
        stop_flag = False
        thread = threading.Thread(
            target=monitor_asset_loop,
            args=(symbol, interval),
            daemon=True
        )
        
        auto_monitor['active'][symbol] = {
            'thread': thread,
            'stop_flag': stop_flag,
            'interval': interval,
            'started_at': datetime.now().isoformat()
        }
        
        thread.start()
    
    return jsonify({
        'success': True,
        'symbol': symbol,
        'interval': interval,
        'message': f'Monitoreo iniciado para {symbol} - notificaciones cada 60 segundos'
    })


@app.route('/api/auto-monitor/stop', methods=['POST'])
def stop_auto_monitor():
    """Detiene monitoreo automático de un activo"""
    data = request.get_json()
    symbol = data.get('symbol')
    
    if not symbol:
        return jsonify({'error': 'Symbol is required'}), 400
    
    with auto_monitor['lock']:
        if symbol in auto_monitor['active']:
            auto_monitor['active'][symbol]['stop_flag'] = True
            del auto_monitor['active'][symbol]
            
            return jsonify({
                'success': True,
                'symbol': symbol,
                'message': f'Monitoreo detenido para {symbol}'
            })
        else:
            return jsonify({
                'success': False,
                'symbol': symbol,
                'message': f'{symbol} no está siendo monitoreado'
            }), 404


@app.route('/api/auto-monitor/status')
def get_auto_monitor_status():
    """Obtiene el estado de todos los activos monitoreados"""
    with auto_monitor['lock']:
        status = {}
        for symbol, info in auto_monitor['active'].items():
            if not info['stop_flag']:
                status[symbol] = {
                    'interval': info['interval'],
                    'started_at': info['started_at'],
                    'active': True
                }
    
    return jsonify({
        'monitored_assets': status,
        'total': len(status)
    })


@app.route('/health')
def health():
    """Endpoint de salud"""
    webhook_stats = webhook_notifier.get_stats()
    
    with auto_monitor['lock']:
        monitored_count = sum(1 for info in auto_monitor['active'].values() if not info['stop_flag'])
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'cache_size': len(cache['data']),
        'webhooks': webhook_stats,
        'auto_monitor': {
            'active_assets': monitored_count
        }
    })


def run_dashboard(host='127.0.0.1', port=5000, debug=False):
    """Inicia el servidor del dashboard"""
    # Cargar webhooks desde configuración
    try:
        from setup_webhooks import load_webhooks_from_config
        load_webhooks_from_config(webhook_notifier)
    except Exception as e:
        print(f"ℹ️  Webhooks no configurados: {e}")
    
    print("=" * 80)
    print("🚀 DASHBOARD DE TRADING EN TIEMPO REAL")
    print("=" * 80)
    print(f"\n📊 Servidor iniciado en: http://{host}:{port}")
    print(f"🔴 Caché de datos: {CACHE_DURATION} segundos")
    print(f"💹 Monitoreando {len(DEFAULT_ASSETS)} activos por defecto")
    print(f"📂 5 categorías con 20 activos cada una")
    print(f"⏱️  {len(DEFAULT_INTERVALS)} intervalos disponibles")
    print(f"⚡ Rate limiting: Delays automáticos para evitar bloqueos")
    print(f"\n🌐 FUENTES DE DATOS:")
    print(f"   🔴 6 Exchanges Crypto - Tiempo real <1s")
    print(f"      • Binance (Principal)")
    print(f"      • Bybit")
    print(f"      • Coinbase Advanced")
    print(f"      • OKX")
    print(f"      • Kraken")
    print(f"      • KuCoin")
    print(f"   📊 Yahoo Finance (Stocks/Forex) - 15-60s latency")
    print(f"   🟣 Binomo (Velas Japonesas) - Fallback automático")
    print(f"   ⚙️  Fallback automático entre exchanges")
    print("\n⚠️  Presiona Ctrl+C para detener el servidor\n")
    print("=" * 80)
    
    app.run(host=host, port=port, debug=debug, threaded=True)


if __name__ == '__main__':
    import sys
    
    # Configuración desde argumentos
    host = sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 5000
    
    run_dashboard(host=host, port=port, debug=False)
