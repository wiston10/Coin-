"""
Módulo para detectar patrones de velas japonesas (candlestick patterns)
"""
import pandas as pd
import numpy as np


class CandlePatternDetector:
    """Detector de patrones de velas japonesas"""
    
    def __init__(self):
        self.patterns = []
    
    @staticmethod
    def is_bullish_candle(open_price, close_price):
        """Verifica si la vela es alcista (cierre > apertura)"""
        return close_price > open_price
    
    @staticmethod
    def is_bearish_candle(open_price, close_price):
        """Verifica si la vela es bajista (cierre < apertura)"""
        return close_price < open_price
    
    @staticmethod
    def body_size(open_price, close_price):
        """Calcula el tamaño del cuerpo de la vela"""
        return abs(close_price - open_price)
    
    @staticmethod
    def upper_shadow(high, open_price, close_price):
        """Calcula el tamaño de la sombra superior"""
        return high - max(open_price, close_price)
    
    @staticmethod
    def lower_shadow(low, open_price, close_price):
        """Calcula el tamaño de la sombra inferior"""
        return min(open_price, close_price) - low
    
    @staticmethod
    def candle_range(high, low):
        """Calcula el rango total de la vela"""
        return high - low
    
    def detect_hammer(self, df, index):
        """
        Detecta patrón Martillo (Hammer) - Señal alcista de reversión
        - Cuerpo pequeño en la parte superior
        - Sombra inferior larga (al menos 2x el cuerpo)
        - Sombra superior pequeña o inexistente
        """
        if index < 1:
            return False
        
        row = df.iloc[index]
        prev_row = df.iloc[index - 1]
        
        body = self.body_size(row['Open'], row['Close'])
        lower = self.lower_shadow(row['Low'], row['Open'], row['Close'])
        upper = self.upper_shadow(row['High'], row['Open'], row['Close'])
        candle_range = self.candle_range(row['High'], row['Low'])
        
        # Condiciones del martillo
        is_hammer = (
            lower >= body * 2 and  # Sombra inferior al menos 2x el cuerpo
            upper <= body * 0.3 and  # Sombra superior pequeña
            body <= candle_range * 0.3 and  # Cuerpo pequeño
            self.is_bearish_candle(prev_row['Open'], prev_row['Close'])  # Tendencia bajista previa
        )
        
        return is_hammer
    
    def detect_shooting_star(self, df, index):
        """
        Detecta patrón Estrella Fugaz (Shooting Star) - Señal bajista de reversión
        - Cuerpo pequeño en la parte inferior
        - Sombra superior larga (al menos 2x el cuerpo)
        - Sombra inferior pequeña o inexistente
        """
        if index < 1:
            return False
        
        row = df.iloc[index]
        prev_row = df.iloc[index - 1]
        
        body = self.body_size(row['Open'], row['Close'])
        lower = self.lower_shadow(row['Low'], row['Open'], row['Close'])
        upper = self.upper_shadow(row['High'], row['Open'], row['Close'])
        candle_range = self.candle_range(row['High'], row['Low'])
        
        # Condiciones de la estrella fugaz
        is_shooting_star = (
            upper >= body * 2 and  # Sombra superior al menos 2x el cuerpo
            lower <= body * 0.3 and  # Sombra inferior pequeña
            body <= candle_range * 0.3 and  # Cuerpo pequeño
            self.is_bullish_candle(prev_row['Open'], prev_row['Close'])  # Tendencia alcista previa
        )
        
        return is_shooting_star
    
    def detect_doji(self, df, index):
        """
        Detecta patrón Doji - Señal de indecisión
        - Apertura y cierre casi iguales
        - Puede tener sombras largas
        """
        row = df.iloc[index]
        
        body = self.body_size(row['Open'], row['Close'])
        candle_range = self.candle_range(row['High'], row['Low'])
        
        # El cuerpo debe ser muy pequeño comparado con el rango
        is_doji = body <= candle_range * 0.1
        
        return is_doji
    
    def detect_bullish_engulfing(self, df, index):
        """
        Detecta patrón Envolvente Alcista (Bullish Engulfing) - Señal alcista fuerte
        - Primera vela bajista
        - Segunda vela alcista que envuelve completamente a la primera
        """
        if index < 1:
            return False
        
        current = df.iloc[index]
        previous = df.iloc[index - 1]
        
        is_engulfing = (
            self.is_bearish_candle(previous['Open'], previous['Close']) and
            self.is_bullish_candle(current['Open'], current['Close']) and
            current['Open'] <= previous['Close'] and
            current['Close'] >= previous['Open']
        )
        
        return is_engulfing
    
    def detect_bearish_engulfing(self, df, index):
        """
        Detecta patrón Envolvente Bajista (Bearish Engulfing) - Señal bajista fuerte
        - Primera vela alcista
        - Segunda vela bajista que envuelve completamente a la primera
        """
        if index < 1:
            return False
        
        current = df.iloc[index]
        previous = df.iloc[index - 1]
        
        is_engulfing = (
            self.is_bullish_candle(previous['Open'], previous['Close']) and
            self.is_bearish_candle(current['Open'], current['Close']) and
            current['Open'] >= previous['Close'] and
            current['Close'] <= previous['Open']
        )
        
        return is_engulfing
    
    def detect_morning_star(self, df, index):
        """
        Detecta patrón Estrella de la Mañana (Morning Star) - Señal alcista de reversión
        - Tres velas: bajista, pequeña (gap down), alcista fuerte
        """
        if index < 2:
            return False
        
        first = df.iloc[index - 2]
        second = df.iloc[index - 1]
        third = df.iloc[index]
        
        first_body = self.body_size(first['Open'], first['Close'])
        second_body = self.body_size(second['Open'], second['Close'])
        third_body = self.body_size(third['Open'], third['Close'])
        
        is_morning_star = (
            self.is_bearish_candle(first['Open'], first['Close']) and
            second_body < first_body * 0.5 and  # Segunda vela pequeña
            self.is_bullish_candle(third['Open'], third['Close']) and
            third['Close'] > (first['Open'] + first['Close']) / 2  # Tercera vela cierra por encima del punto medio de la primera
        )
        
        return is_morning_star
    
    def detect_evening_star(self, df, index):
        """
        Detecta patrón Estrella de la Tarde (Evening Star) - Señal bajista de reversión
        - Tres velas: alcista, pequeña (gap up), bajista fuerte
        """
        if index < 2:
            return False
        
        first = df.iloc[index - 2]
        second = df.iloc[index - 1]
        third = df.iloc[index]
        
        first_body = self.body_size(first['Open'], first['Close'])
        second_body = self.body_size(second['Open'], second['Close'])
        third_body = self.body_size(third['Open'], third['Close'])
        
        is_evening_star = (
            self.is_bullish_candle(first['Open'], first['Close']) and
            second_body < first_body * 0.5 and  # Segunda vela pequeña
            self.is_bearish_candle(third['Open'], third['Close']) and
            third['Close'] < (first['Open'] + first['Close']) / 2  # Tercera vela cierra por debajo del punto medio de la primera
        )
        
        return is_evening_star
    
    def detect_three_white_soldiers(self, df, index):
        """
        Detecta patrón Tres Soldados Blancos - Señal alcista fuerte
        - Tres velas alcistas consecutivas con cierres progresivamente más altos
        """
        if index < 2:
            return False
        
        first = df.iloc[index - 2]
        second = df.iloc[index - 1]
        third = df.iloc[index]
        
        is_pattern = (
            self.is_bullish_candle(first['Open'], first['Close']) and
            self.is_bullish_candle(second['Open'], second['Close']) and
            self.is_bullish_candle(third['Open'], third['Close']) and
            second['Close'] > first['Close'] and
            third['Close'] > second['Close'] and
            second['Open'] > first['Open'] and
            third['Open'] > second['Open']
        )
        
        return is_pattern
    
    def detect_three_black_crows(self, df, index):
        """
        Detecta patrón Tres Cuervos Negros - Señal bajista fuerte
        - Tres velas bajistas consecutivas con cierres progresivamente más bajos
        """
        if index < 2:
            return False
        
        first = df.iloc[index - 2]
        second = df.iloc[index - 1]
        third = df.iloc[index]
        
        is_pattern = (
            self.is_bearish_candle(first['Open'], first['Close']) and
            self.is_bearish_candle(second['Open'], second['Close']) and
            self.is_bearish_candle(third['Open'], third['Close']) and
            second['Close'] < first['Close'] and
            third['Close'] < second['Close'] and
            second['Open'] < first['Open'] and
            third['Open'] < second['Open']
        )
        
        return is_pattern
    
    def analyze_patterns(self, df):
        """
        Analiza todos los patrones en el dataframe
        Retorna un diccionario con los patrones detectados
        """
        patterns = {
            'Hammer': [],
            'Shooting Star': [],
            'Doji': [],
            'Bullish Engulfing': [],
            'Bearish Engulfing': [],
            'Morning Star': [],
            'Evening Star': [],
            'Three White Soldiers': [],
            'Three Black Crows': []
        }
        
        for i in range(len(df)):
            if self.detect_hammer(df, i):
                patterns['Hammer'].append(i)
            if self.detect_shooting_star(df, i):
                patterns['Shooting Star'].append(i)
            if self.detect_doji(df, i):
                patterns['Doji'].append(i)
            if self.detect_bullish_engulfing(df, i):
                patterns['Bullish Engulfing'].append(i)
            if self.detect_bearish_engulfing(df, i):
                patterns['Bearish Engulfing'].append(i)
            if self.detect_morning_star(df, i):
                patterns['Morning Star'].append(i)
            if self.detect_evening_star(df, i):
                patterns['Evening Star'].append(i)
            if self.detect_three_white_soldiers(df, i):
                patterns['Three White Soldiers'].append(i)
            if self.detect_three_black_crows(df, i):
                patterns['Three Black Crows'].append(i)
        
        return patterns
    
    def get_current_pattern(self, df):
        """
        Obtiene el patrón más reciente detectado
        """
        index = len(df) - 1
        
        if self.detect_hammer(df, index):
            return 'Hammer', 'BULLISH'
        elif self.detect_shooting_star(df, index):
            return 'Shooting Star', 'BEARISH'
        elif self.detect_doji(df, index):
            return 'Doji', 'NEUTRAL'
        elif self.detect_bullish_engulfing(df, index):
            return 'Bullish Engulfing', 'BULLISH'
        elif self.detect_bearish_engulfing(df, index):
            return 'Bearish Engulfing', 'BEARISH'
        elif self.detect_morning_star(df, index):
            return 'Morning Star', 'BULLISH'
        elif self.detect_evening_star(df, index):
            return 'Evening Star', 'BEARISH'
        elif self.detect_three_white_soldiers(df, index):
            return 'Three White Soldiers', 'BULLISH'
        elif self.detect_three_black_crows(df, index):
            return 'Three Black Crows', 'BEARISH'
        
        return None, 'NONE'
