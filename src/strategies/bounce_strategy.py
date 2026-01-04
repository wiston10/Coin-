"""
Estrategia Avanzada de Rebotes con Psicología del Mercado
Soporta: Scalping (1m-5m) y Mediano Plazo (15m-1h)
"""
import pandas as pd
import numpy as np
import warnings
from src.indicators.technical_indicators import TechnicalIndicators
from src.indicators.candle_patterns import CandlePatternDetector
from src.indicators.trend_detector import TrendDetector

# Suprimir FutureWarning de pandas
warnings.filterwarnings('ignore', category=FutureWarning)


class BounceStrategy:
    """Estrategia de rebotes con análisis de patrones históricos"""
    
    def __init__(self):
        self.pattern_detector = CandlePatternDetector()
        
        # Patrones de rebote alcistas (comprar en soporte)
        self.bullish_bounce_patterns = [
            'Hammer',
            'Bullish Engulfing',
            'Morning Star',
            'Three White Soldiers'
        ]
        
        # Patrones de rebote bajistas (vender en resistencia)
        self.bearish_bounce_patterns = [
            'Shooting Star',
            'Bearish Engulfing',
            'Evening Star',
            'Three Black Crows'
        ]
        
        # Configuración por tipo de trading
        self.config = {
            'scalping': {
                'intervals': ['1m', '5m'],
                'profit_target': 0.5,  # 0.5% por operación
                'stop_loss': 0.3,       # 0.3% stop loss
                'min_volume_spike': 1.5,  # 50% más volumen que promedio
                'hold_time': 5,         # Máximo 5 velas
            },
            'medium_term': {
                'intervals': ['15m', '30m', '1h'],
                'profit_target': 2.0,   # 2% por operación
                'stop_loss': 1.0,       # 1% stop loss
                'min_volume_spike': 1.3,  # 30% más volumen
                'hold_time': 20,        # Máximo 20 velas
            }
        }
    
    def analyze_bounce(self, df, interval='5m', trading_type='scalping'):
        """
        Analiza oportunidades de rebote en soportes/resistencias
        
        Args:
            df: DataFrame con datos OHLCV e indicadores
            interval: Intervalo de tiempo
            trading_type: 'scalping' o 'medium_term'
        
        Returns:
            dict con análisis de rebote
        """
        config = self.config.get(trading_type, self.config['scalping'])
        
        # 1. Identificar niveles clave
        support_levels, resistance_levels = self._identify_key_levels(df)
        
        # 2. Detectar proximidad a niveles
        current_price = df['Close'].iloc[-1]
        near_support = self._is_near_level(current_price, support_levels, tolerance=0.005)
        near_resistance = self._is_near_level(current_price, resistance_levels, tolerance=0.005)
        
        # 3. Analizar patrón de vela actual
        current_pattern, pattern_signal = self.pattern_detector.get_current_pattern(df)
        
        # 4. Análisis de volumen (psicología del mercado)
        volume_analysis = self._analyze_volume_psychology(df)
        
        # 5. Análisis de momentum
        momentum = self._analyze_momentum(df)
        
        # 6. Contar rebotes históricos en niveles
        bounce_history = self._analyze_historical_bounces(df, support_levels, resistance_levels)
        
        # 7. Análisis de velas previas (contexto)
        candle_context = self._analyze_candle_context(df)
        
        # 8. Generar señal de rebote
        signal = self._generate_bounce_signal(
            current_price=current_price,
            near_support=near_support,
            near_resistance=near_resistance,
            pattern=current_pattern,
            pattern_signal=pattern_signal,
            volume_analysis=volume_analysis,
            momentum=momentum,
            bounce_history=bounce_history,
            candle_context=candle_context,
            config=config,
            df=df
        )
        
        return {
            'signal': signal['action'],
            'confidence': signal['confidence'],
            'entry_price': current_price,
            'take_profit': signal['take_profit'],
            'stop_loss': signal['stop_loss'],
            'expected_hold_time': signal['hold_time'],
            'risk_reward': signal['risk_reward'],
            'support_levels': support_levels,
            'resistance_levels': resistance_levels,
            'pattern': current_pattern,
            'volume_signal': volume_analysis['signal'],
            'momentum_signal': momentum['signal'],
            'bounce_probability': signal['bounce_probability'],
            'historical_success_rate': bounce_history['success_rate'],
            'psychology': self._market_psychology(volume_analysis, momentum, candle_context),
            'reasons': signal['reasons']
        }
    
    def _identify_key_levels(self, df, lookback=100):
        """Identifica soportes y resistencias clave usando múltiples métodos"""
        df_lookback = df.tail(lookback)
        
        # Método 1: Pivot points
        pivots_high = self._find_pivot_points(df_lookback, 'High')
        pivots_low = self._find_pivot_points(df_lookback, 'Low')
        
        # Método 2: Niveles psicológicos (números redondos)
        current_price = df['Close'].iloc[-1]
        psychological = self._find_psychological_levels(current_price)
        
        # Método 3: Niveles de volumen
        volume_levels = self._find_volume_levels(df_lookback)
        
        # Combinar todos los niveles
        resistance_levels = sorted(set(pivots_high + psychological['resistance'] + volume_levels['resistance']))[-5:]
        support_levels = sorted(set(pivots_low + psychological['support'] + volume_levels['support']))[-5:]
        
        return support_levels, resistance_levels
    
    def _find_pivot_points(self, df, column, window=5):
        """Encuentra puntos pivot (máximos/mínimos locales)"""
        pivots = []
        
        for i in range(window, len(df) - window):
            if column == 'High':
                # Buscar máximos locales
                is_pivot = all(df[column].iloc[i] >= df[column].iloc[i-j] for j in range(1, window+1)) and \
                          all(df[column].iloc[i] >= df[column].iloc[i+j] for j in range(1, window+1))
            else:
                # Buscar mínimos locales
                is_pivot = all(df[column].iloc[i] <= df[column].iloc[i-j] for j in range(1, window+1)) and \
                          all(df[column].iloc[i] <= df[column].iloc[i+j] for j in range(1, window+1))
            
            if is_pivot:
                pivots.append(df[column].iloc[i])
        
        # Agrupar niveles cercanos
        return self._cluster_levels(pivots)
    
    def _cluster_levels(self, levels, tolerance=0.002):
        """Agrupa niveles cercanos (dentro del 0.2%)"""
        if not levels:
            return []
        
        clustered = []
        sorted_levels = sorted(levels)
        current_cluster = [sorted_levels[0]]
        
        for level in sorted_levels[1:]:
            if abs(level - current_cluster[-1]) / current_cluster[-1] <= tolerance:
                current_cluster.append(level)
            else:
                clustered.append(np.mean(current_cluster))
                current_cluster = [level]
        
        clustered.append(np.mean(current_cluster))
        return clustered
    
    def _find_psychological_levels(self, price):
        """Encuentra niveles psicológicos (números redondos)"""
        # Redondear a diferentes magnitudes
        magnitude = 10 ** (len(str(int(price))) - 2)
        
        psychological_levels = []
        for multiplier in [0.5, 1, 2, 5, 10]:
            level = round(price / (magnitude * multiplier)) * (magnitude * multiplier)
            psychological_levels.append(level)
        
        resistance = [l for l in psychological_levels if l > price]
        support = [l for l in psychological_levels if l < price]
        
        return {
            'resistance': sorted(resistance)[:3],
            'support': sorted(support, reverse=True)[:3]
        }
    
    def _find_volume_levels(self, df):
        """Encuentra niveles con alto volumen histórico"""
        # Agrupar precios en bins y sumar volumen
        price_bins = pd.cut(df['Close'], bins=50)
        volume_by_price = df.groupby(price_bins)['Volume'].sum()
        
        # Tomar los 5 niveles con mayor volumen
        top_volume_levels = volume_by_price.nlargest(5)
        
        current_price = df['Close'].iloc[-1]
        all_levels = [interval.mid for interval in top_volume_levels.index]
        
        resistance = [l for l in all_levels if l > current_price]
        support = [l for l in all_levels if l < current_price]
        
        return {
            'resistance': sorted(resistance)[:3],
            'support': sorted(support, reverse=True)[:3]
        }
    
    def _is_near_level(self, price, levels, tolerance=0.005):
        """Verifica si el precio está cerca de algún nivel (0.5% por defecto)"""
        for level in levels:
            # Evitar división por cero
            if level == 0:
                continue
            
            if abs(price - level) / level <= tolerance:
                return {
                    'is_near': True,
                    'level': level,
                    'distance_pct': abs(price - level) / level * 100
                }
        return {'is_near': False, 'level': None, 'distance_pct': None}
    
    def _analyze_volume_psychology(self, df, window=20):
        """
        Analiza el volumen para entender la psicología del mercado
        Alto volumen = convicción, Bajo volumen = indecisión
        """
        current_volume = df['Volume'].iloc[-1]
        avg_volume = df['Volume'].tail(window).mean()
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
        
        # Analizar volumen en las últimas 5 velas
        recent_volumes = df['Volume'].tail(5).values
        volume_trend = 'increasing' if recent_volumes[-1] > recent_volumes[0] else 'decreasing'
        
        # Clasificar intensidad
        if volume_ratio > 2.0:
            intensity = 'VERY_HIGH'
            psychology = 'Convicción fuerte'
        elif volume_ratio > 1.5:
            intensity = 'HIGH'
            psychology = 'Convicción moderada'
        elif volume_ratio > 0.8:
            intensity = 'NORMAL'
            psychology = 'Mercado normal'
        elif volume_ratio > 0.5:
            intensity = 'LOW'
            psychology = 'Indecisión'
        else:
            intensity = 'VERY_LOW'
            psychology = 'Desinterés / Consolidación'
        
        return {
            'signal': intensity,
            'ratio': volume_ratio,
            'trend': volume_trend,
            'psychology': psychology,
            'avg_volume': avg_volume
        }
    
    def _analyze_momentum(self, df):
        """Analiza el momentum para detectar agotamiento o aceleración"""
        # RSI para momentum
        rsi = df['RSI'].iloc[-1] if 'RSI' in df else 50
        
        # MACD para dirección
        macd = df['MACD'].iloc[-1] if 'MACD' in df else 0
        macd_signal = df['MACD_Signal'].iloc[-1] if 'MACD_Signal' in df else 0
        
        # Análisis de velas recientes
        last_5_closes = df['Close'].tail(5).values
        price_momentum = (last_5_closes[-1] - last_5_closes[0]) / last_5_closes[0] * 100
        
        # Determinar señal de momentum
        if rsi > 70 and price_momentum > 0:
            signal = 'OVERBOUGHT'
            description = 'Sobrecomprado - posible agotamiento alcista'
        elif rsi < 30 and price_momentum < 0:
            signal = 'OVERSOLD'
            description = 'Sobrevendido - posible agotamiento bajista'
        elif macd > macd_signal and rsi > 50:
            signal = 'BULLISH'
            description = 'Momentum alcista'
        elif macd < macd_signal and rsi < 50:
            signal = 'BEARISH'
            description = 'Momentum bajista'
        else:
            signal = 'NEUTRAL'
            description = 'Momentum neutral'
        
        return {
            'signal': signal,
            'rsi': rsi,
            'price_momentum': price_momentum,
            'description': description
        }
    
    def _analyze_historical_bounces(self, df, support_levels, resistance_levels, window=100):
        """
        Analiza rebotes históricos en niveles para calcular probabilidad de éxito
        """
        df_history = df.tail(window)
        
        successful_bounces = 0
        total_touches = 0
        
        # Analizar cada nivel de soporte
        for support in support_levels:
            touches = self._count_level_touches(df_history, support, tolerance=0.01)
            bounces = self._count_successful_bounces(df_history, support, direction='up')
            
            total_touches += touches
            successful_bounces += bounces
        
        # Analizar cada nivel de resistencia
        for resistance in resistance_levels:
            touches = self._count_level_touches(df_history, resistance, tolerance=0.01)
            bounces = self._count_successful_bounces(df_history, resistance, direction='down')
            
            total_touches += touches
            successful_bounces += bounces
        
        success_rate = (successful_bounces / total_touches * 100) if total_touches > 0 else 50
        
        return {
            'success_rate': success_rate,
            'total_touches': total_touches,
            'successful_bounces': successful_bounces
        }
    
    def _count_level_touches(self, df, level, tolerance=0.01):
        """Cuenta cuántas veces el precio tocó un nivel"""
        # Evitar división por cero
        if level == 0:
            return 0
        
        touches = 0
        for i in range(len(df)):
            low = df['Low'].iloc[i]
            high = df['High'].iloc[i]
            
            # Verificar si la vela tocó el nivel
            if abs(low - level) / level <= tolerance or abs(high - level) / level <= tolerance:
                touches += 1
        
        return touches
    
    def _count_successful_bounces(self, df, level, direction='up', tolerance=0.01):
        """Cuenta rebotes exitosos (precio se aleja del nivel después de tocarlo)"""
        # Evitar división por cero
        if level == 0:
            return 0
        
        bounces = 0
        
        for i in range(len(df) - 5):  # Necesitamos 5 velas después para verificar
            low = df['Low'].iloc[i]
            high = df['High'].iloc[i]
            
            # Verificar si tocó el nivel
            touched = abs(low - level) / level <= tolerance or abs(high - level) / level <= tolerance
            
            if touched:
                # Verificar si hubo rebote en las siguientes 5 velas
                if direction == 'up':
                    next_high = df['High'].iloc[i+1:i+6].max()
                    if next_high > level * 1.005:  # 0.5% de rebote
                        bounces += 1
                else:  # direction == 'down'
                    next_low = df['Low'].iloc[i+1:i+6].min()
                    if next_low < level * 0.995:  # 0.5% de rebote
                        bounces += 1
        
        return bounces
    
    def _analyze_candle_context(self, df, lookback=10):
        """
        Analiza el contexto de las velas previas
        Busca patrones de indecisión, agotamiento, o acumulación
        """
        recent_candles = df.tail(lookback)
        
        # Analizar tamaño de cuerpos
        bodies = abs(recent_candles['Close'] - recent_candles['Open'])
        avg_body = bodies.mean()
        current_body = bodies.iloc[-1]
        
        # Analizar sombras
        upper_shadows = recent_candles['High'] - recent_candles[['Close', 'Open']].max(axis=1)
        lower_shadows = recent_candles[['Close', 'Open']].min(axis=1) - recent_candles['Low']
        
        # Detectar indecisión (cuerpos pequeños, sombras largas)
        indecision_candles = sum((bodies < avg_body * 0.5) & ((upper_shadows > bodies * 2) | (lower_shadows > bodies * 2)))
        
        # Detectar velas de momentum (cuerpos grandes, sombras pequeñas)
        momentum_candles = sum((bodies > avg_body * 1.5) & (upper_shadows < bodies * 0.5) & (lower_shadows < bodies * 0.5))
        
        context = {
            'indecision_count': indecision_candles,
            'momentum_count': momentum_candles,
            'avg_body_size': avg_body,
            'current_body_size': current_body,
        }
        
        # Interpretación
        if indecision_candles >= 3:
            context['interpretation'] = 'Consolidación - mercado indeciso'
            context['signal'] = 'CONSOLIDATION'
        elif momentum_candles >= 3:
            context['interpretation'] = 'Tendencia fuerte - momentum claro'
            context['signal'] = 'MOMENTUM'
        else:
            context['interpretation'] = 'Mercado mixto'
            context['signal'] = 'MIXED'
        
        return context
    
    def _market_psychology(self, volume_analysis, momentum, candle_context):
        """Interpreta la psicología del mercado combinando todos los factores"""
        psychology_score = 0
        description = []
        
        # Factor volumen
        if volume_analysis['signal'] in ['VERY_HIGH', 'HIGH']:
            psychology_score += 2
            description.append(f"✓ {volume_analysis['psychology']}")
        elif volume_analysis['signal'] == 'NORMAL':
            psychology_score += 1
            description.append(f"• {volume_analysis['psychology']}")
        else:
            description.append(f"✗ {volume_analysis['psychology']}")
        
        # Factor momentum
        if momentum['signal'] in ['OVERBOUGHT', 'OVERSOLD']:
            psychology_score += 2
            description.append(f"✓ {momentum['description']} (oportunidad)")
        elif momentum['signal'] in ['BULLISH', 'BEARISH']:
            psychology_score += 1
            description.append(f"• {momentum['description']}")
        
        # Factor contexto de velas
        if candle_context['signal'] == 'CONSOLIDATION':
            psychology_score += 1
            description.append(f"✓ {candle_context['interpretation']} (setup ideal)")
        elif candle_context['signal'] == 'MOMENTUM':
            description.append(f"• {candle_context['interpretation']}")
        
        # Clasificar psicología general
        if psychology_score >= 4:
            sentiment = 'MUY_FAVORABLE'
        elif psychology_score >= 3:
            sentiment = 'FAVORABLE'
        elif psychology_score >= 2:
            sentiment = 'NEUTRAL'
        else:
            sentiment = 'DESFAVORABLE'
        
        return {
            'sentiment': sentiment,
            'score': psychology_score,
            'description': ' | '.join(description)
        }
    
    def _generate_bounce_signal(self, current_price, near_support, near_resistance,
                                pattern, pattern_signal, volume_analysis, momentum,
                                bounce_history, candle_context, config, df):
        """Genera la señal final de trading basada en todos los análisis"""
        
        confidence = 0
        reasons = []
        action = 'HOLD'
        bounce_probability = 0
        
        # ANÁLISIS DE REBOTE EN SOPORTE (señal de COMPRA)
        if near_support['is_near']:
            confidence += 15
            reasons.append(f"Cerca de soporte en ${near_support['level']:,.2f}")
            
            # Patrón alcista en soporte = muy buena señal
            if pattern in self.bullish_bounce_patterns:
                confidence += 20
                reasons.append(f"Patrón alcista '{pattern}' en soporte")
                action = 'BUY'
            
            # Momentum sobrevendido en soporte = excelente
            if momentum['signal'] == 'OVERSOLD':
                confidence += 15
                reasons.append("RSI sobrevendido - agotamiento bajista")
            
            # Volumen alto = convicción
            if volume_analysis['signal'] in ['HIGH', 'VERY_HIGH']:
                confidence += 10
                reasons.append(f"Volumen {volume_analysis['ratio']:.1f}x promedio")
            
            # Historial de rebotes exitosos
            if bounce_history['success_rate'] > 60:
                confidence += 10
                reasons.append(f"Historial: {bounce_history['success_rate']:.0f}% rebotes exitosos")
            
            bounce_probability = min(confidence, 95)
            
            if confidence >= 50:
                action = 'BUY'
        
        # ANÁLISIS DE REBOTE EN RESISTENCIA (señal de VENTA)
        elif near_resistance['is_near']:
            confidence += 15
            reasons.append(f"Cerca de resistencia en ${near_resistance['level']:,.2f}")
            
            # Patrón bajista en resistencia = muy buena señal
            if pattern in self.bearish_bounce_patterns:
                confidence += 20
                reasons.append(f"Patrón bajista '{pattern}' en resistencia")
                action = 'SELL'
            
            # Momentum sobrecomprado en resistencia = excelente
            if momentum['signal'] == 'OVERBOUGHT':
                confidence += 15
                reasons.append("RSI sobrecomprado - agotamiento alcista")
            
            # Volumen alto = convicción
            if volume_analysis['signal'] in ['HIGH', 'VERY_HIGH']:
                confidence += 10
                reasons.append(f"Volumen {volume_analysis['ratio']:.1f}x promedio")
            
            # Historial de rebotes exitosos
            if bounce_history['success_rate'] > 60:
                confidence += 10
                reasons.append(f"Historial: {bounce_history['success_rate']:.0f}% rebotes exitosos")
            
            bounce_probability = min(confidence, 95)
            
            if confidence >= 50:
                action = 'SELL'
        
        # Calcular niveles de salida
        if action == 'BUY':
            take_profit = current_price * (1 + config['profit_target'] / 100)
            stop_loss = current_price * (1 - config['stop_loss'] / 100)
        elif action == 'SELL':
            take_profit = current_price * (1 - config['profit_target'] / 100)
            stop_loss = current_price * (1 + config['stop_loss'] / 100)
        else:
            take_profit = current_price
            stop_loss = current_price
        
        risk = abs(current_price - stop_loss)
        reward = abs(take_profit - current_price)
        risk_reward = reward / risk if risk > 0 else 0
        
        return {
            'action': action,
            'confidence': min(confidence, 100),
            'take_profit': take_profit,
            'stop_loss': stop_loss,
            'hold_time': config['hold_time'],
            'risk_reward': risk_reward,
            'bounce_probability': bounce_probability,
            'reasons': reasons
        }


# Función de conveniencia
def analyze_bounce_opportunity(df, interval='5m', trading_type='scalping'):
    """
    Analiza oportunidad de rebote en un DataFrame
    
    Args:
        df: DataFrame con datos OHLCV e indicadores
        interval: Intervalo de tiempo
        trading_type: 'scalping' o 'medium_term'
    
    Returns:
        dict con análisis completo
    """
    strategy = BounceStrategy()
    return strategy.analyze_bounce(df, interval, trading_type)
