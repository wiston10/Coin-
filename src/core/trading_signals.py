"""
Motor de señales de trading que combina todos los análisis
"""
from src.indicators.candle_patterns import CandlePatternDetector
from src.indicators.technical_indicators import TechnicalIndicators
from src.indicators.trend_detector import TrendDetector
import pandas as pd


class TradingSignalEngine:
    """
    Motor que genera señales de COMPRA/VENTA basándose en:
    - Patrones de velas
    - Indicadores técnicos
    - Análisis de tendencia
    """
    
    def __init__(self):
        self.pattern_detector = CandlePatternDetector()
        
    def generate_signal(self, df):
        """
        Genera una señal de trading completa analizando todos los factores
        Retorna: señal (BUY/SELL/HOLD), confianza (0-100), razones
        """
        if len(df) < 200:
            return {
                'signal': 'HOLD',
                'confidence': 0,
                'reason': 'Datos insuficientes para análisis completo',
                'details': {}
            }
        
        # Obtener última fila
        last = df.iloc[-1]
        
        # 1. Análisis de patrones de velas
        pattern, pattern_signal = self.pattern_detector.get_current_pattern(df)
        
        # 2. Análisis de indicadores técnicos
        rsi_signal = TechnicalIndicators.get_rsi_signal(last.get('RSI'))
        macd_signal = TechnicalIndicators.get_macd_signal(
            last.get('MACD'), 
            last.get('MACD_Signal')
        )
        bb_signal = TechnicalIndicators.get_bb_signal(
            last['Close'],
            last.get('BB_Upper'),
            last.get('BB_Lower')
        )
        
        # 3. Análisis de tendencia
        trend_analysis = TrendDetector.analyze_trend(df)
        overall_trend = trend_analysis['overall_trend']
        trend_strength = TrendDetector.get_trend_strength_score(df)
        
        # 4. Calcular señal combinada
        buy_score = 0
        sell_score = 0
        reasons = []
        
        # Evaluar patrón de velas (peso: 20)
        if pattern_signal == 'BULLISH':
            buy_score += 20
            reasons.append(f'Patrón alcista detectado: {pattern}')
        elif pattern_signal == 'BEARISH':
            sell_score += 20
            reasons.append(f'Patrón bajista detectado: {pattern}')
        
        # Evaluar RSI (peso: 15)
        if rsi_signal == 'OVERSOLD':
            buy_score += 15
            reasons.append(f'RSI en sobreventa ({last.get("RSI", 0):.2f})')
        elif rsi_signal == 'OVERBOUGHT':
            sell_score += 15
            reasons.append(f'RSI en sobrecompra ({last.get("RSI", 0):.2f})')
        
        # Evaluar MACD (peso: 15)
        if macd_signal == 'BULLISH':
            buy_score += 15
            reasons.append('MACD en señal alcista')
        elif macd_signal == 'BEARISH':
            sell_score += 15
            reasons.append('MACD en señal bajista')
        
        # Evaluar Bandas de Bollinger (peso: 10)
        if bb_signal == 'OVERSOLD':
            buy_score += 10
            reasons.append('Precio tocando banda inferior de Bollinger')
        elif bb_signal == 'OVERBOUGHT':
            sell_score += 10
            reasons.append('Precio tocando banda superior de Bollinger')
        
        # Evaluar tendencia general (peso: 30)
        if 'BULLISH' in overall_trend:
            if 'STRONG' in overall_trend:
                buy_score += 30
                reasons.append('Tendencia alcista fuerte')
            else:
                buy_score += 20
                reasons.append('Tendencia alcista')
        elif 'BEARISH' in overall_trend:
            if 'STRONG' in overall_trend:
                sell_score += 30
                reasons.append('Tendencia bajista fuerte')
            else:
                sell_score += 20
                reasons.append('Tendencia bajista')
        
        # Evaluar soporte/resistencia (peso: 10)
        if trend_analysis['sr_position'] == 'NEAR_SUPPORT':
            buy_score += 10
            reasons.append(f'Cerca de soporte: ${trend_analysis["sr_level"]:.2f}')
        elif trend_analysis['sr_position'] == 'NEAR_RESISTANCE':
            sell_score += 10
            reasons.append(f'Cerca de resistencia: ${trend_analysis["sr_level"]:.2f}')
        
        # Determinar señal final
        total_score = buy_score + sell_score
        
        if total_score == 0:
            signal = 'HOLD'
            confidence = 0
        elif buy_score > sell_score:
            signal = 'BUY'
            confidence = min(100, (buy_score / 100) * 100)
        elif sell_score > buy_score:
            signal = 'SELL'
            confidence = min(100, (sell_score / 100) * 100)
        else:
            signal = 'HOLD'
            confidence = 50
        
        # Ajustar confianza basada en convergencia de señales
        num_bullish = sum(1 for r in reasons if any(word in r.lower() for word in ['alcista', 'bullish', 'compra', 'sobreventa', 'soporte']))
        num_bearish = sum(1 for r in reasons if any(word in r.lower() for word in ['bajista', 'bearish', 'venta', 'sobrecompra', 'resistencia']))
        
        convergence = abs(num_bullish - num_bearish)
        if convergence >= 3:
            confidence = min(100, confidence * 1.2)
        
        return {
            'signal': signal,
            'confidence': round(confidence, 2),
            'buy_score': buy_score,
            'sell_score': sell_score,
            'reasons': reasons,
            'details': {
                'pattern': pattern,
                'pattern_signal': pattern_signal,
                'rsi': round(last.get('RSI', 0), 2) if pd.notna(last.get('RSI')) else None,
                'rsi_signal': rsi_signal,
                'macd_signal': macd_signal,
                'bb_signal': bb_signal,
                'trend': overall_trend,
                'trend_strength': round(trend_strength, 2),
                'support_levels': [round(s, 2) for s in trend_analysis['support_levels']],
                'resistance_levels': [round(r, 2) for r in trend_analysis['resistance_levels']],
                'current_price': round(last['Close'], 2)
            }
        }
    
    def get_entry_exit_levels(self, df, signal_data):
        """
        Calcula niveles de entrada, stop loss y take profit
        """
        last = df.iloc[-1]
        current_price = last['Close']
        atr = last.get('ATR', 0)
        
        if pd.isna(atr) or atr == 0:
            atr = current_price * 0.02  # 2% como fallback
        
        signal = signal_data['signal']
        trend_analysis = TrendDetector.analyze_trend(df)
        
        if signal == 'BUY':
            # Entrada: precio actual o ligeramente por debajo
            entry = current_price
            
            # Stop Loss: 1.5-2 ATR por debajo, o nivel de soporte más cercano
            stop_loss = current_price - (atr * 2)
            if trend_analysis['support_levels']:
                nearest_support = max([s for s in trend_analysis['support_levels'] if s < current_price], default=stop_loss)
                stop_loss = max(stop_loss, nearest_support)
            
            # Take Profit: 2-3 ATR por encima, o nivel de resistencia más cercano
            take_profit = current_price + (atr * 3)
            if trend_analysis['resistance_levels']:
                nearest_resistance = min([r for r in trend_analysis['resistance_levels'] if r > current_price], default=take_profit)
                take_profit = min(take_profit, nearest_resistance)
            
        elif signal == 'SELL':
            # Entrada: precio actual o ligeramente por encima
            entry = current_price
            
            # Stop Loss: 1.5-2 ATR por encima, o nivel de resistencia más cercano
            stop_loss = current_price + (atr * 2)
            if trend_analysis['resistance_levels']:
                nearest_resistance = min([r for r in trend_analysis['resistance_levels'] if r > current_price], default=stop_loss)
                stop_loss = min(stop_loss, nearest_resistance)
            
            # Take Profit: 2-3 ATR por debajo, o nivel de soporte más cercano
            take_profit = current_price - (atr * 3)
            if trend_analysis['support_levels']:
                nearest_support = max([s for s in trend_analysis['support_levels'] if s < current_price], default=take_profit)
                take_profit = max(take_profit, nearest_support)
        
        else:  # HOLD
            return None
        
        # Calcular risk/reward ratio
        risk = abs(entry - stop_loss)
        reward = abs(take_profit - entry)
        risk_reward_ratio = reward / risk if risk > 0 else 0
        
        return {
            'entry': round(entry, 2),
            'stop_loss': round(stop_loss, 2),
            'take_profit': round(take_profit, 2),
            'risk': round(risk, 2),
            'reward': round(reward, 2),
            'risk_reward_ratio': round(risk_reward_ratio, 2)
        }
    
    def should_enter_trade(self, signal_data, min_confidence=60, min_risk_reward=1.5):
        """
        Determina si se debe entrar en una operación basándose en:
        - Confianza mínima
        - Risk/Reward ratio mínimo
        """
        if signal_data['signal'] == 'HOLD':
            return False, 'Sin señal clara de trading'
        
        if signal_data['confidence'] < min_confidence:
            return False, f'Confianza insuficiente ({signal_data["confidence"]}% < {min_confidence}%)'
        
        return True, 'Señal válida para entrar'
    
    def analyze_market_condition(self, df):
        """
        Analiza las condiciones generales del mercado
        """
        trend_analysis = TrendDetector.analyze_trend(df)
        last = df.iloc[-1]
        
        # Volatilidad (usando ATR)
        atr = last.get('ATR', 0)
        avg_price = last['Close']
        volatility_pct = (atr / avg_price * 100) if pd.notna(atr) and avg_price > 0 else 0
        
        if volatility_pct > 3:
            volatility = 'ALTA'
        elif volatility_pct > 1.5:
            volatility = 'MEDIA'
        else:
            volatility = 'BAJA'
        
        # Volumen
        if 'Volume' in df.columns and len(df) >= 20:
            avg_volume = df['Volume'].tail(20).mean()
            current_volume = last['Volume']
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
            
            if volume_ratio > 1.5:
                volume_condition = 'ALTO'
            elif volume_ratio > 0.7:
                volume_condition = 'NORMAL'
            else:
                volume_condition = 'BAJO'
        else:
            volume_condition = 'DESCONOCIDO'
        
        # ADX para fuerza de tendencia
        adx = last.get('ADX', 0)
        if pd.notna(adx):
            if adx > 25:
                trend_strength = 'FUERTE'
            elif adx > 20:
                trend_strength = 'MODERADA'
            else:
                trend_strength = 'DÉBIL'
        else:
            trend_strength = 'DESCONOCIDA'
        
        return {
            'trend': trend_analysis['overall_trend'],
            'volatility': volatility,
            'volatility_pct': round(volatility_pct, 2),
            'volume': volume_condition,
            'trend_strength': trend_strength,
            'adx': round(adx, 2) if pd.notna(adx) else None,
            'market_phase': self._determine_market_phase(trend_analysis['overall_trend'], volatility, trend_strength)
        }
    
    def _determine_market_phase(self, trend, volatility, strength):
        """
        Determina la fase del mercado
        """
        if 'BULLISH' in trend and strength in ['FUERTE', 'MODERADA']:
            return 'TENDENCIA ALCISTA'
        elif 'BEARISH' in trend and strength in ['FUERTE', 'MODERADA']:
            return 'TENDENCIA BAJISTA'
        elif volatility == 'ALTA':
            return 'ALTA VOLATILIDAD'
        elif trend == 'SIDEWAYS' or strength == 'DÉBIL':
            return 'CONSOLIDACIÓN'
        else:
            return 'TRANSICIÓN'
