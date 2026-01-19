#!/usr/bin/env python3
"""
Fuentes de Datos Extendidas para Análisis de Trading
Incluye: CoinGecko, CryptoCompare, Tiingo, NewsAPI, y análisis de horarios óptimos
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, List, Tuple
import time
import warnings
warnings.filterwarnings('ignore')

# Configuración de APIs (gratuitas)
EXTENDED_APIS = {
    'coingecko': {
        'enabled': True,
        'endpoint': 'https://api.coingecko.com/api/v3',
        'rate_limit': 10,  # requests por minuto (gratis)
        'requires_key': False
    },
    'cryptocompare': {
        'enabled': True,
        'endpoint': 'https://min-api.cryptocompare.com/data',
        'rate_limit': 50,
        'requires_key': False
    },
    'tiingo': {
        'enabled': True,
        'endpoint': 'https://api.tiingo.com',
        'rate_limit': 500,  # por día en plan gratis
        'api_key': '',  # Opcional: agregar tu API key
        'requires_key': False  # Funciona sin key para algunos endpoints
    },
    'newsapi': {
        'enabled': True,
        'endpoint': 'https://newsapi.org/v2',
        'rate_limit': 100,  # por día gratis
        'api_key': '',  # Opcional: agregar tu API key
        'requires_key': True
    },
    'alternative_me': {
        'enabled': True,
        'endpoint': 'https://api.alternative.me',
        'rate_limit': 100,
        'requires_key': False
    }
}


class ExtendedDataSources:
    """Fuentes de datos extendidas para análisis completo"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'TradingBot/1.0',
            'Accept': 'application/json'
        })
        
        # Cache
        self.cache = {}
        self.cache_timestamps = {}
        self.cache_duration = 60
        
        # Rate limiting
        self.last_request = {}
        
        # Mapeo de símbolos para CoinGecko
        self.coingecko_ids = {
            'BTC-USD': 'bitcoin',
            'ETH-USD': 'ethereum',
            'SOL-USD': 'solana',
            'ADA-USD': 'cardano',
            'DOT-USD': 'polkadot',
            'MATIC-USD': 'matic-network',
            'AVAX-USD': 'avalanche-2',
            'LINK-USD': 'chainlink',
            'UNI-USD': 'uniswap',
            'LTC-USD': 'litecoin',
            'XRP-USD': 'ripple',
            'ATOM-USD': 'cosmos',
            'XLM-USD': 'stellar',
            'ALGO-USD': 'algorand',
            'VET-USD': 'vechain',
            'NEAR-USD': 'near',
            'FTM-USD': 'fantom',
            'AAVE-USD': 'aave',
            'GRT-USD': 'the-graph',
            'DOGE-USD': 'dogecoin',
            'SHIB-USD': 'shiba-inu',
        }
        
        # Horarios óptimos de trading por mercado
        self.optimal_hours = {
            'crypto': {
                'best_hours': [(8, 12), (14, 18), (20, 24)],  # UTC - Alta volatilidad
                'worst_hours': [(2, 6)],  # Baja liquidez
                'description': 'Crypto opera 24/7. Mejor volatilidad: apertura Asia (00-02 UTC), apertura Europa (07-09 UTC), apertura USA (13-16 UTC)'
            },
            'stocks': {
                'best_hours': [(14, 16), (19, 21)],  # NYSE abre 14:30 UTC, cierra 21:00 UTC
                'worst_hours': [(0, 14), (21, 24)],
                'description': 'NYSE: 9:30-16:00 EST (14:30-21:00 UTC). Mejor: primera y última hora'
            },
            'forex': {
                'best_hours': [(7, 12), (13, 17)],  # Londres + NY overlap
                'worst_hours': [(21, 24), (0, 5)],
                'description': 'Mejor: Overlap Londres-NY (13-17 UTC). Sydney-Tokyo (22-07 UTC), Londres (07-16 UTC)'
            },
            'indices': {
                'best_hours': [(14, 16), (19, 21)],
                'worst_hours': [(0, 14)],
                'description': 'Sigue horarios de bolsas locales. SPY/QQQ: 14:30-21:00 UTC'
            }
        }
    
    def _check_cache(self, key):
        if key in self.cache:
            if time.time() - self.cache_timestamps.get(key, 0) < self.cache_duration:
                return self.cache[key]
        return None
    
    def _update_cache(self, key, data):
        self.cache[key] = data
        self.cache_timestamps[key] = time.time()
    
    def _rate_limit(self, source):
        """Control de rate limit"""
        min_interval = 60 / EXTENDED_APIS.get(source, {}).get('rate_limit', 60)
        if source in self.last_request:
            elapsed = time.time() - self.last_request[source]
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
        self.last_request[source] = time.time()
    
    # ========================================================================
    # COINGECKO - Datos gratuitos de crypto
    # ========================================================================
    
    def get_coingecko_price(self, symbol: str) -> Optional[Dict]:
        """Obtiene precio y datos de mercado desde CoinGecko"""
        if not EXTENDED_APIS['coingecko']['enabled']:
            return None
        
        cache_key = f"coingecko:{symbol}"
        cached = self._check_cache(cache_key)
        if cached:
            return cached
        
        coin_id = self.coingecko_ids.get(symbol)
        if not coin_id:
            return None
        
        try:
            self._rate_limit('coingecko')
            url = f"{EXTENDED_APIS['coingecko']['endpoint']}/simple/price"
            params = {
                'ids': coin_id,
                'vs_currencies': 'usd',
                'include_market_cap': 'true',
                'include_24hr_vol': 'true',
                'include_24hr_change': 'true',
                'include_last_updated_at': 'true'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if coin_id in data:
                result = {
                    'source': 'coingecko',
                    'price': data[coin_id].get('usd'),
                    'market_cap': data[coin_id].get('usd_market_cap'),
                    'volume_24h': data[coin_id].get('usd_24h_vol'),
                    'change_24h': data[coin_id].get('usd_24h_change'),
                    'last_updated': data[coin_id].get('last_updated_at')
                }
                self._update_cache(cache_key, result)
                return result
                
        except Exception as e:
            print(f"❌ CoinGecko error {symbol}: {e}")
        
        return None
    
    def get_coingecko_market_data(self, symbol: str) -> Optional[Dict]:
        """Obtiene datos de mercado extendidos desde CoinGecko"""
        if not EXTENDED_APIS['coingecko']['enabled']:
            return None
        
        coin_id = self.coingecko_ids.get(symbol)
        if not coin_id:
            return None
        
        try:
            self._rate_limit('coingecko')
            url = f"{EXTENDED_APIS['coingecko']['endpoint']}/coins/{coin_id}"
            params = {
                'localization': 'false',
                'tickers': 'false',
                'market_data': 'true',
                'community_data': 'true',
                'developer_data': 'false'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            market_data = data.get('market_data', {})
            
            return {
                'source': 'coingecko',
                'name': data.get('name'),
                'symbol': data.get('symbol', '').upper(),
                'price': market_data.get('current_price', {}).get('usd'),
                'market_cap': market_data.get('market_cap', {}).get('usd'),
                'market_cap_rank': data.get('market_cap_rank'),
                'total_volume': market_data.get('total_volume', {}).get('usd'),
                'high_24h': market_data.get('high_24h', {}).get('usd'),
                'low_24h': market_data.get('low_24h', {}).get('usd'),
                'price_change_24h': market_data.get('price_change_24h'),
                'price_change_percentage_24h': market_data.get('price_change_percentage_24h'),
                'price_change_percentage_7d': market_data.get('price_change_percentage_7d'),
                'price_change_percentage_30d': market_data.get('price_change_percentage_30d'),
                'circulating_supply': market_data.get('circulating_supply'),
                'total_supply': market_data.get('total_supply'),
                'ath': market_data.get('ath', {}).get('usd'),
                'ath_change_percentage': market_data.get('ath_change_percentage', {}).get('usd'),
                'atl': market_data.get('atl', {}).get('usd'),
                'sentiment_votes_up_percentage': data.get('sentiment_votes_up_percentage'),
                'sentiment_votes_down_percentage': data.get('sentiment_votes_down_percentage'),
            }
            
        except Exception as e:
            print(f"❌ CoinGecko market data error: {e}")
        
        return None
    
    # ========================================================================
    # CRYPTOCOMPARE - Social y datos históricos
    # ========================================================================
    
    def get_cryptocompare_price(self, symbol: str) -> Optional[Dict]:
        """Obtiene precio desde CryptoCompare"""
        if not EXTENDED_APIS['cryptocompare']['enabled']:
            return None
        
        cache_key = f"cryptocompare:{symbol}"
        cached = self._check_cache(cache_key)
        if cached:
            return cached
        
        # Extraer símbolo base
        base_symbol = symbol.replace('-USD', '').replace('/USDT', '')
        
        try:
            self._rate_limit('cryptocompare')
            url = f"{EXTENDED_APIS['cryptocompare']['endpoint']}/price"
            params = {
                'fsym': base_symbol,
                'tsyms': 'USD,BTC,ETH'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'USD' in data:
                result = {
                    'source': 'cryptocompare',
                    'price': data.get('USD'),
                    'price_btc': data.get('BTC'),
                    'price_eth': data.get('ETH')
                }
                self._update_cache(cache_key, result)
                return result
                
        except Exception as e:
            print(f"❌ CryptoCompare error {symbol}: {e}")
        
        return None
    
    def get_cryptocompare_social(self, symbol: str) -> Optional[Dict]:
        """Obtiene datos sociales desde CryptoCompare"""
        base_symbol = symbol.replace('-USD', '').replace('/USDT', '')
        
        try:
            self._rate_limit('cryptocompare')
            url = f"{EXTENDED_APIS['cryptocompare']['endpoint']}/social/coin/latest"
            params = {'coinId': base_symbol}
            
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'Data' in data:
                social = data['Data']
                return {
                    'source': 'cryptocompare_social',
                    'twitter_followers': social.get('Twitter', {}).get('followers'),
                    'reddit_subscribers': social.get('Reddit', {}).get('subscribers'),
                    'reddit_active_users': social.get('Reddit', {}).get('active_users'),
                    'github_stars': social.get('CodeRepository', {}).get('stars'),
                    'github_forks': social.get('CodeRepository', {}).get('forks'),
                }
                
        except Exception as e:
            pass
        
        return None
    
    # ========================================================================
    # FEAR & GREED INDEX - Sentimiento del mercado
    # ========================================================================
    
    def get_fear_greed_index(self) -> Optional[Dict]:
        """Obtiene el índice de miedo y codicia del mercado crypto"""
        if not EXTENDED_APIS['alternative_me']['enabled']:
            return None
        
        cache_key = "fear_greed_index"
        cached = self._check_cache(cache_key)
        if cached:
            return cached
        
        try:
            self._rate_limit('alternative_me')
            url = f"{EXTENDED_APIS['alternative_me']['endpoint']}/fng/"
            params = {'limit': 7}  # Últimos 7 días
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'data' in data and len(data['data']) > 0:
                current = data['data'][0]
                history = data['data']
                
                result = {
                    'value': int(current.get('value', 50)),
                    'classification': current.get('value_classification', 'Neutral'),
                    'timestamp': current.get('timestamp'),
                    'history_7d': [
                        {'value': int(d['value']), 'date': d['timestamp']}
                        for d in history
                    ],
                    'trend': self._calculate_fng_trend(history)
                }
                self._update_cache(cache_key, result)
                return result
                
        except Exception as e:
            print(f"❌ Fear & Greed Index error: {e}")
        
        return None
    
    def _calculate_fng_trend(self, history: List) -> str:
        """Calcula la tendencia del índice de miedo y codicia"""
        if len(history) < 2:
            return 'stable'
        
        values = [int(h['value']) for h in history[:7]]
        avg_recent = np.mean(values[:3]) if len(values) >= 3 else values[0]
        avg_old = np.mean(values[3:]) if len(values) > 3 else avg_recent
        
        diff = avg_recent - avg_old
        if diff > 10:
            return 'increasing_greed'
        elif diff < -10:
            return 'increasing_fear'
        else:
            return 'stable'
    
    # ========================================================================
    # ANÁLISIS DE HORARIOS ÓPTIMOS
    # ========================================================================
    
    def get_optimal_trading_time(self, asset_type: str = 'crypto') -> Dict:
        """Analiza si es buen momento para hacer trading"""
        now = datetime.now(timezone.utc)
        current_hour = now.hour
        current_weekday = now.weekday()  # 0 = Monday
        
        market_info = self.optimal_hours.get(asset_type, self.optimal_hours['crypto'])
        
        # Verificar si es fin de semana (para stocks/forex)
        is_weekend = current_weekday >= 5
        
        # Verificar si estamos en horario óptimo
        is_optimal = False
        is_avoid = False
        
        for start, end in market_info['best_hours']:
            if start <= current_hour < end:
                is_optimal = True
                break
        
        for start, end in market_info['worst_hours']:
            if start <= current_hour < end:
                is_avoid = True
                break
        
        # Calcular score de timing (0-100)
        timing_score = 50  # Base
        
        if is_optimal:
            timing_score = 85
        elif is_avoid:
            timing_score = 25
        
        # Penalizar fin de semana para mercados tradicionales
        if is_weekend and asset_type in ['stocks', 'indices', 'forex']:
            timing_score = 10
            is_avoid = True
        
        # Determinar próxima ventana óptima
        next_optimal = self._get_next_optimal_window(current_hour, market_info['best_hours'])
        
        return {
            'current_hour_utc': current_hour,
            'current_time_utc': now.strftime('%H:%M UTC'),
            'is_optimal_time': is_optimal,
            'should_avoid': is_avoid,
            'timing_score': timing_score,
            'timing_emoji': self._get_timing_emoji(timing_score),
            'timing_label': self._get_timing_label(timing_score, is_weekend, asset_type),
            'market_description': market_info['description'],
            'next_optimal_window': next_optimal,
            'is_weekend': is_weekend,
            'asset_type': asset_type
        }
    
    def _get_next_optimal_window(self, current_hour: int, best_hours: List[Tuple]) -> str:
        """Calcula la próxima ventana óptima de trading"""
        for start, end in sorted(best_hours):
            if current_hour < start:
                hours_until = start - current_hour
                return f"En {hours_until}h ({start}:00 UTC)"
        
        # Si ya pasaron todas, la primera del día siguiente
        first_window = min(best_hours, key=lambda x: x[0])
        hours_until = 24 - current_hour + first_window[0]
        return f"Mañana {first_window[0]}:00 UTC (en {hours_until}h)"
    
    def _get_timing_emoji(self, score: int) -> str:
        if score >= 80:
            return "🟢"
        elif score >= 60:
            return "🟡"
        elif score >= 40:
            return "🟠"
        else:
            return "🔴"
    
    def _get_timing_label(self, score: int, is_weekend: bool, asset_type: str) -> str:
        if is_weekend and asset_type in ['stocks', 'indices', 'forex']:
            return "MERCADO CERRADO (Fin de semana)"
        elif score >= 80:
            return "MOMENTO ÓPTIMO"
        elif score >= 60:
            return "Buen momento"
        elif score >= 40:
            return "Momento regular"
        else:
            return "Evitar trading"
    
    # ========================================================================
    # ANÁLISIS DE NOTICIAS SIMULADO (sin API key)
    # ========================================================================
    
    def get_market_news_sentiment(self, symbol: str = None, asset_type: str = 'crypto') -> Dict:
        """
        Obtiene sentimiento basado en datos disponibles públicamente
        Sin API key, usamos Fear & Greed y datos de mercado como proxy
        """
        sentiment_data = {
            'source': 'market_analysis',
            'symbol': symbol,
            'asset_type': asset_type,
            'timestamp': datetime.now().isoformat()
        }
        
        # Para crypto, usar Fear & Greed como proxy de sentimiento
        if asset_type == 'crypto':
            fng = self.get_fear_greed_index()
            if fng:
                sentiment_data['fear_greed'] = fng
                
                # Traducir a sentimiento
                value = fng['value']
                if value <= 25:
                    sentiment_data['sentiment'] = 'EXTREME_FEAR'
                    sentiment_data['sentiment_score'] = 20
                    sentiment_data['recommendation'] = 'Posible oportunidad de compra (mercado muy temeroso)'
                elif value <= 45:
                    sentiment_data['sentiment'] = 'FEAR'
                    sentiment_data['sentiment_score'] = 35
                    sentiment_data['recommendation'] = 'Mercado temeroso - considerar acumulación'
                elif value <= 55:
                    sentiment_data['sentiment'] = 'NEUTRAL'
                    sentiment_data['sentiment_score'] = 50
                    sentiment_data['recommendation'] = 'Mercado neutral - seguir análisis técnico'
                elif value <= 75:
                    sentiment_data['sentiment'] = 'GREED'
                    sentiment_data['sentiment_score'] = 65
                    sentiment_data['recommendation'] = 'Mercado codicioso - precaución en compras'
                else:
                    sentiment_data['sentiment'] = 'EXTREME_GREED'
                    sentiment_data['sentiment_score'] = 85
                    sentiment_data['recommendation'] = 'Posible techo - considerar toma de ganancias'
        else:
            # Para otros activos, sentimiento neutral por defecto
            sentiment_data['sentiment'] = 'NEUTRAL'
            sentiment_data['sentiment_score'] = 50
            sentiment_data['recommendation'] = 'Usar análisis técnico para decisiones'
        
        return sentiment_data
    
    # ========================================================================
    # AGREGADOR DE PRECIOS MULTI-FUENTE
    # ========================================================================
    
    def get_aggregated_crypto_price(self, symbol: str) -> Dict:
        """Obtiene precio agregado de múltiples fuentes para crypto"""
        prices = []
        sources = []
        
        # CoinGecko
        cg_data = self.get_coingecko_price(symbol)
        if cg_data and cg_data.get('price'):
            prices.append(cg_data['price'])
            sources.append('coingecko')
        
        # CryptoCompare
        cc_data = self.get_cryptocompare_price(symbol)
        if cc_data and cc_data.get('price'):
            prices.append(cc_data['price'])
            sources.append('cryptocompare')
        
        if not prices:
            return {'error': 'No se pudo obtener precio de ninguna fuente'}
        
        # Calcular precio consenso
        avg_price = np.mean(prices)
        std_price = np.std(prices) if len(prices) > 1 else 0
        
        return {
            'symbol': symbol,
            'price': avg_price,
            'std_deviation': std_price,
            'sources_count': len(sources),
            'sources': sources,
            'individual_prices': dict(zip(sources, prices)),
            'confidence': min(100, 50 + len(sources) * 25),  # Más fuentes = más confianza
            'timestamp': datetime.now().isoformat()
        }
    
    # ========================================================================
    # ANÁLISIS COMPLETO
    # ========================================================================
    
    def get_complete_analysis(self, symbol: str, asset_type: str = 'crypto') -> Dict:
        """Obtiene análisis completo con todas las fuentes disponibles"""
        analysis = {
            'symbol': symbol,
            'asset_type': asset_type,
            'timestamp': datetime.now().isoformat()
        }
        
        # Datos de precio
        if asset_type == 'crypto':
            price_data = self.get_aggregated_crypto_price(symbol)
            analysis['price_data'] = price_data
            
            # Datos de mercado extendidos
            market_data = self.get_coingecko_market_data(symbol)
            if market_data:
                analysis['market_data'] = market_data
        
        # Horario óptimo
        timing = self.get_optimal_trading_time(asset_type)
        analysis['timing'] = timing
        
        # Sentimiento del mercado
        sentiment = self.get_market_news_sentiment(symbol, asset_type)
        analysis['sentiment'] = sentiment
        
        return analysis


# Instancia global
extended_sources = ExtendedDataSources()


# Funciones de utilidad
def get_optimal_trading_info(asset_type: str = 'crypto') -> Dict:
    """Función rápida para obtener info de horarios"""
    return extended_sources.get_optimal_trading_time(asset_type)


def get_market_sentiment(symbol: str = None, asset_type: str = 'crypto') -> Dict:
    """Función rápida para obtener sentimiento"""
    return extended_sources.get_market_news_sentiment(symbol, asset_type)


def get_crypto_price_multi_source(symbol: str) -> Dict:
    """Función rápida para obtener precio multi-fuente"""
    return extended_sources.get_aggregated_crypto_price(symbol)
