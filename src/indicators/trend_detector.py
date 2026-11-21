"""
Módulo para detectar tendencias del mercado
"""
import pandas as pd
import numpy as np


class TrendDetector:
    """Detector de tendencias de mercado"""
    
    @staticmethod
    def detect_trend_by_moving_averages(df):
        """
        Detecta la tendencia usando medias móviles
        - SMA_20 > SMA_50 > SMA_200: Tendencia alcista fuerte
        - SMA_20 < SMA_50 < SMA_200: Tendencia bajista fuerte
        - Precio > todas las SMAs: Muy alcista
        - Precio < todas las SMAs: Muy bajista
        """
        if len(df) < 200:
            return 'INSUFFICIENT_DATA'
        
        last = df.iloc[-1]
        
        # Verificar que los indicadores existan
        if 'SMA_20' not in df.columns or 'SMA_50' not in df.columns or 'SMA_200' not in df.columns:
            return 'NEUTRAL'
        
        sma_20 = last['SMA_20']
        sma_50 = last['SMA_50']
        sma_200 = last['SMA_200']
        close = last['Close']
        
        # Validar que no sean NaN
        if pd.isna(sma_20) or pd.isna(sma_50) or pd.isna(sma_200):
            return 'NEUTRAL'
        
        # Tendencia alcista fuerte
        if sma_20 > sma_50 > sma_200 and close > sma_20:
            return 'STRONG_BULLISH'
        
        # Tendencia alcista
        if sma_20 > sma_50 or (close > sma_20 and close > sma_50):
            return 'BULLISH'
        
        # Tendencia bajista fuerte
        if sma_20 < sma_50 < sma_200 and close < sma_20:
            return 'STRONG_BEARISH'
        
        # Tendencia bajista
        if sma_20 < sma_50 or (close < sma_20 and close < sma_50):
            return 'BEARISH'
        
        # Tendencia lateral/neutral
        return 'SIDEWAYS'
    
    @staticmethod
    def detect_trend_by_adx(df, threshold_strong=25, threshold_weak=20):
        """
        Detecta la fuerza de la tendencia usando ADX
        - ADX > 25: Tendencia fuerte
        - ADX < 20: Tendencia débil o lateral
        - +DI > -DI: Tendencia alcista
        - +DI < -DI: Tendencia bajista
        """
        if 'ADX' not in df.columns or 'Plus_DI' not in df.columns or 'Minus_DI' not in df.columns:
            return 'NEUTRAL', 0
        
        last = df.iloc[-1]
        adx = last['ADX']
        plus_di = last['Plus_DI']
        minus_di = last['Minus_DI']
        
        if pd.isna(adx) or pd.isna(plus_di) or pd.isna(minus_di):
            return 'NEUTRAL', 0
        
        # Determinar dirección
        if plus_di > minus_di:
            direction = 'BULLISH'
        else:
            direction = 'BEARISH'
        
        # Determinar fuerza
        if adx > threshold_strong:
            strength = 'STRONG'
        elif adx > threshold_weak:
            strength = 'MODERATE'
        else:
            strength = 'WEAK'
        
        return f'{strength}_{direction}', adx
    
    @staticmethod
    def detect_trend_by_highs_lows(df, period=20):
        """
        Detecta la tendencia analizando máximos y mínimos
        - Máximos y mínimos crecientes: Tendencia alcista
        - Máximos y mínimos decrecientes: Tendencia bajista
        """
        if len(df) < period * 2:
            return 'INSUFFICIENT_DATA'
        
        # Dividir en dos mitades
        mid = len(df) - period
        first_half = df.iloc[mid-period:mid]
        second_half = df.iloc[mid:]
        
        first_high = first_half['High'].max()
        first_low = first_half['Low'].min()
        
        second_high = second_half['High'].max()
        second_low = second_half['Low'].min()
        
        # Tendencia alcista: máximos y mínimos crecientes
        if second_high > first_high and second_low > first_low:
            return 'BULLISH'
        
        # Tendencia bajista: máximos y mínimos decrecientes
        if second_high < first_high and second_low < first_low:
            return 'BEARISH'
        
        # Tendencia lateral
        return 'SIDEWAYS'
    
    @staticmethod
    def detect_trend_by_slope(df, period=20):
        """
        Detecta la tendencia calculando la pendiente de la línea de regresión
        Pendiente positiva: alcista
        Pendiente negativa: bajista
        """
        if len(df) < period:
            return 'INSUFFICIENT_DATA', 0
        
        recent_data = df['Close'].tail(period)
        x = np.arange(len(recent_data))
        y = recent_data.values
        
        # Calcular pendiente usando regresión lineal
        slope = np.polyfit(x, y, 1)[0]
        
        # Normalizar la pendiente por el precio promedio
        avg_price = recent_data.mean()
        normalized_slope = (slope / avg_price) * 100
        
        if normalized_slope > 0.5:
            return 'BULLISH', normalized_slope
        elif normalized_slope < -0.5:
            return 'BEARISH', normalized_slope
        else:
            return 'SIDEWAYS', normalized_slope
    
    @staticmethod
    def detect_support_resistance(df, window=20, num_levels=3):
        """
        Detecta niveles de soporte y resistencia
        """
        if len(df) < window:
            return [], []
        
        # Encontrar máximos locales (resistencias)
        highs = df['High'].rolling(window=window, center=True).max()
        resistance_levels = []
        
        for i in range(window, len(df) - window):
            if df['High'].iloc[i] == highs.iloc[i]:
                resistance_levels.append(df['High'].iloc[i])
        
        # Encontrar mínimos locales (soportes)
        lows = df['Low'].rolling(window=window, center=True).min()
        support_levels = []
        
        for i in range(window, len(df) - window):
            if df['Low'].iloc[i] == lows.iloc[i]:
                support_levels.append(df['Low'].iloc[i])
        
        # Agrupar niveles similares
        def cluster_levels(levels, tolerance=0.02):
            if not levels:
                return []
            
            levels = sorted(levels)
            clusters = []
            current_cluster = [levels[0]]
            
            for level in levels[1:]:
                if abs(level - current_cluster[-1]) / current_cluster[-1] < tolerance:
                    current_cluster.append(level)
                else:
                    clusters.append(np.mean(current_cluster))
                    current_cluster = [level]
            
            clusters.append(np.mean(current_cluster))
            return clusters
        
        resistance_levels = cluster_levels(resistance_levels)
        support_levels = cluster_levels(support_levels)
        
        # Retornar los niveles más relevantes
        # Clasificar por posición respecto al precio actual y quedarse con los
        # niveles más cercanos (antes se tomaban los más altos de cada lista)
        price = df['Close'].iloc[-1]
        levels = {float(l) for l in resistance_levels + support_levels if pd.notna(l)}
        resistance_levels = sorted(l for l in levels if l > price)[:num_levels]
        support_levels = sorted((l for l in levels if l < price), reverse=True)[:num_levels]
        
        return support_levels, resistance_levels
    
    @staticmethod
    def is_near_support_resistance(current_price, support_levels, resistance_levels, tolerance=0.01):
        """
        Verifica si el precio actual está cerca de un nivel de soporte o resistencia
        """
        candidates = [(abs(current_price - l) / l, 'NEAR_SUPPORT', l) for l in support_levels if l] + \
                     [(abs(current_price - l) / l, 'NEAR_RESISTANCE', l) for l in resistance_levels if l]
        candidates = [c for c in candidates if c[0] < tolerance]
        if candidates:
            _, kind, level = min(candidates)  # el nivel más cercano gana
            return kind, level
        
        return 'NONE', None
    
    @staticmethod
    def analyze_trend(df):
        """
        Análisis completo de tendencia combinando múltiples métodos
        Retorna un diccionario con toda la información de tendencia
        """
        analysis = {}
        
        # Tendencia por medias móviles
        analysis['ma_trend'] = TrendDetector.detect_trend_by_moving_averages(df)
        
        # Tendencia por ADX
        analysis['adx_trend'], analysis['adx_value'] = TrendDetector.detect_trend_by_adx(df)
        
        # Tendencia por máximos/mínimos
        analysis['highs_lows_trend'] = TrendDetector.detect_trend_by_highs_lows(df)
        
        # Tendencia por pendiente
        analysis['slope_trend'], analysis['slope_value'] = TrendDetector.detect_trend_by_slope(df)
        
        # Soportes y resistencias
        analysis['support_levels'], analysis['resistance_levels'] = \
            TrendDetector.detect_support_resistance(df)
        
        # Verificar si está cerca de soporte/resistencia
        current_price = df['Close'].iloc[-1]
        analysis['sr_position'], analysis['sr_level'] = \
            TrendDetector.is_near_support_resistance(
                current_price,
                analysis['support_levels'],
                analysis['resistance_levels']
            )
        
        # Tendencia general (consenso)
        trends = [
            analysis['ma_trend'],
            analysis['adx_trend'],
            analysis['highs_lows_trend'],
            analysis['slope_trend']
        ]
        
        # Contar tendencias alcistas y bajistas
        bullish_count = sum(1 for t in trends if 'BULLISH' in t)
        bearish_count = sum(1 for t in trends if 'BEARISH' in t)
        
        if bullish_count > bearish_count:
            if bullish_count >= 3:
                analysis['overall_trend'] = 'STRONG_BULLISH'
            else:
                analysis['overall_trend'] = 'BULLISH'
        elif bearish_count > bullish_count:
            if bearish_count >= 3:
                analysis['overall_trend'] = 'STRONG_BEARISH'
            else:
                analysis['overall_trend'] = 'BEARISH'
        else:
            analysis['overall_trend'] = 'SIDEWAYS'
        
        return analysis
    
    @staticmethod
    def get_trend_strength_score(df):
        """
        Calcula un score de 0-100 indicando la fuerza de la tendencia
        100: Tendencia alcista muy fuerte
        0: Tendencia bajista muy fuerte
        50: Neutral/Lateral
        """
        analysis = TrendDetector.analyze_trend(df)
        score = 50  # Neutral
        
        # Ajustar por tendencia de medias móviles
        ma_trend = analysis['ma_trend']
        if ma_trend == 'STRONG_BULLISH':
            score += 20
        elif ma_trend == 'BULLISH':
            score += 10
        elif ma_trend == 'STRONG_BEARISH':
            score -= 20
        elif ma_trend == 'BEARISH':
            score -= 10
        
        # Ajustar por ADX
        adx_trend = analysis['adx_trend']
        if 'BULLISH' in adx_trend:
            if 'STRONG' in adx_trend:
                score += 15
            elif 'MODERATE' in adx_trend:
                score += 10
        elif 'BEARISH' in adx_trend:
            if 'STRONG' in adx_trend:
                score -= 15
            elif 'MODERATE' in adx_trend:
                score -= 10
        
        # Ajustar por pendiente
        if analysis['slope_trend'] == 'BULLISH':
            score += 10
        elif analysis['slope_trend'] == 'BEARISH':
            score -= 10
        
        # Limitar entre 0 y 100
        score = max(0, min(100, score))
        
        return score
