"""
Módulo de indicadores técnicos para análisis de mercado
"""
import pandas as pd
import numpy as np


class TechnicalIndicators:
    """Clase para calcular indicadores técnicos"""
    
    @staticmethod
    def calculate_sma(df, period=20, column='Close'):
        """
        Calcula la Media Móvil Simple (SMA)
        """
        return df[column].rolling(window=period).mean()
    
    @staticmethod
    def calculate_ema(df, period=20, column='Close'):
        """
        Calcula la Media Móvil Exponencial (EMA)
        Más sensible a los cambios recientes de precio
        """
        return df[column].ewm(span=period, adjust=False).mean()
    
    @staticmethod
    def calculate_rsi(df, period=14, column='Close'):
        """
        Calcula el Índice de Fuerza Relativa (RSI)
        RSI > 70: Sobrecomprado (posible venta)
        RSI < 30: Sobrevendido (posible compra)
        """
        delta = df[column].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        # Mercado plano (sin subidas ni bajadas): RSI neutral en vez de NaN
        rsi = rsi.mask((gain == 0) & (loss == 0), 50.0)
        
        return rsi
    
    @staticmethod
    def calculate_macd(df, fast=12, slow=26, signal=9, column='Close'):
        """
        Calcula el MACD (Moving Average Convergence Divergence)
        Retorna: MACD line, Signal line, Histogram
        
        Señales:
        - MACD cruza por encima de Signal: Compra
        - MACD cruza por debajo de Signal: Venta
        - Histograma positivo: momentum alcista
        - Histograma negativo: momentum bajista
        """
        ema_fast = df[column].ewm(span=fast, adjust=False).mean()
        ema_slow = df[column].ewm(span=slow, adjust=False).mean()
        
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    @staticmethod
    def calculate_bollinger_bands(df, period=20, std_dev=2, column='Close'):
        """
        Calcula las Bandas de Bollinger
        Retorna: Upper Band, Middle Band (SMA), Lower Band
        
        Señales:
        - Precio toca banda superior: Sobrecomprado
        - Precio toca banda inferior: Sobrevendido
        - Bandas estrechas: baja volatilidad, posible breakout
        - Bandas anchas: alta volatilidad
        """
        sma = df[column].rolling(window=period).mean()
        std = df[column].rolling(window=period).std()
        
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        return upper_band, sma, lower_band
    
    @staticmethod
    def calculate_stochastic(df, period=14, smooth_k=3, smooth_d=3):
        """
        Calcula el Oscilador Estocástico
        Retorna: %K, %D
        
        Señales:
        - %K > 80: Sobrecomprado
        - %K < 20: Sobrevendido
        - %K cruza por encima de %D: Compra
        - %K cruza por debajo de %D: Venta
        """
        low_min = df['Low'].rolling(window=period).min()
        high_max = df['High'].rolling(window=period).max()
        
        k_percent = 100 * ((df['Close'] - low_min) / (high_max - low_min))
        k_smooth = k_percent.rolling(window=smooth_k).mean()
        d_smooth = k_smooth.rolling(window=smooth_d).mean()
        
        return k_smooth, d_smooth
    
    @staticmethod
    def calculate_atr(df, period=14):
        """
        Calcula el Average True Range (ATR)
        Mide la volatilidad del mercado
        ATR alto: alta volatilidad
        ATR bajo: baja volatilidad
        """
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        
        atr = true_range.rolling(window=period).mean()
        
        return atr
    
    @staticmethod
    def calculate_obv(df):
        """
        Calcula el On-Balance Volume (OBV)
        Relaciona volumen con cambios de precio
        
        OBV subiendo: presión compradora
        OBV bajando: presión vendedora
        """
        obv = [0]
        
        for i in range(1, len(df)):
            if df['Close'].iloc[i] > df['Close'].iloc[i-1]:
                obv.append(obv[-1] + df['Volume'].iloc[i])
            elif df['Close'].iloc[i] < df['Close'].iloc[i-1]:
                obv.append(obv[-1] - df['Volume'].iloc[i])
            else:
                obv.append(obv[-1])
        
        return pd.Series(obv, index=df.index)
    
    @staticmethod
    def calculate_adx(df, period=14):
        """
        Calcula el Average Directional Index (ADX)
        Mide la fuerza de la tendencia (no la dirección)
        
        ADX > 25: Tendencia fuerte
        ADX < 20: Tendencia débil o lateral
        """
        high_diff = df['High'].diff()
        low_diff = -df['Low'].diff()
        
        plus_dm = high_diff.where((high_diff > low_diff) & (high_diff > 0), 0)
        minus_dm = low_diff.where((low_diff > high_diff) & (low_diff > 0), 0)
        
        atr = TechnicalIndicators.calculate_atr(df, period)
        
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
        
        dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()
        
        return adx, plus_di, minus_di
    
    @staticmethod
    def calculate_ichimoku(df):
        """
        Calcula las líneas del Ichimoku Cloud
        Retorna: Tenkan-sen, Kijun-sen, Senkou Span A, Senkou Span B, Chikou Span
        
        Señales:
        - Precio sobre la nube: tendencia alcista
        - Precio bajo la nube: tendencia bajista
        - Precio en la nube: consolidación
        """
        # Tenkan-sen (línea de conversión): 9 periodos
        nine_period_high = df['High'].rolling(window=9).max()
        nine_period_low = df['Low'].rolling(window=9).min()
        tenkan_sen = (nine_period_high + nine_period_low) / 2
        
        # Kijun-sen (línea base): 26 periodos
        period26_high = df['High'].rolling(window=26).max()
        period26_low = df['Low'].rolling(window=26).min()
        kijun_sen = (period26_high + period26_low) / 2
        
        # Senkou Span A (Leading Span A)
        senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(26)
        
        # Senkou Span B (Leading Span B): 52 periodos
        period52_high = df['High'].rolling(window=52).max()
        period52_low = df['Low'].rolling(window=52).min()
        senkou_span_b = ((period52_high + period52_low) / 2).shift(26)
        
        # Chikou Span (Lagging Span)
        chikou_span = df['Close'].shift(-26)
        
        return tenkan_sen, kijun_sen, senkou_span_a, senkou_span_b, chikou_span
    
    @staticmethod
    def calculate_all_indicators(df):
        """
        Calcula todos los indicadores técnicos y los agrega al dataframe
        """
        df_result = df.copy()
        
        # Medias Móviles
        df_result['SMA_20'] = TechnicalIndicators.calculate_sma(df, 20)
        df_result['SMA_50'] = TechnicalIndicators.calculate_sma(df, 50)
        df_result['SMA_200'] = TechnicalIndicators.calculate_sma(df, 200)
        df_result['EMA_12'] = TechnicalIndicators.calculate_ema(df, 12)
        df_result['EMA_26'] = TechnicalIndicators.calculate_ema(df, 26)
        
        # RSI
        df_result['RSI'] = TechnicalIndicators.calculate_rsi(df, 14)
        
        # MACD
        macd, signal, hist = TechnicalIndicators.calculate_macd(df)
        df_result['MACD'] = macd
        df_result['MACD_Signal'] = signal
        df_result['MACD_Hist'] = hist
        
        # Bandas de Bollinger
        upper, middle, lower = TechnicalIndicators.calculate_bollinger_bands(df)
        df_result['BB_Upper'] = upper
        df_result['BB_Middle'] = middle
        df_result['BB_Lower'] = lower
        
        # Estocástico
        k, d = TechnicalIndicators.calculate_stochastic(df)
        df_result['Stoch_K'] = k
        df_result['Stoch_D'] = d
        
        # ATR
        df_result['ATR'] = TechnicalIndicators.calculate_atr(df)
        
        # OBV
        df_result['OBV'] = TechnicalIndicators.calculate_obv(df)
        
        # ADX
        adx, plus_di, minus_di = TechnicalIndicators.calculate_adx(df)
        df_result['ADX'] = adx
        df_result['Plus_DI'] = plus_di
        df_result['Minus_DI'] = minus_di
        
        return df_result
    
    @staticmethod
    def get_rsi_signal(rsi):
        """Interpreta la señal del RSI"""
        if pd.isna(rsi):
            return 'NEUTRAL'
        if rsi > 70:
            return 'OVERBOUGHT'  # Sobrecomprado - posible venta
        elif rsi < 30:
            return 'OVERSOLD'  # Sobrevendido - posible compra
        else:
            return 'NEUTRAL'
    
    @staticmethod
    def get_macd_signal(macd, signal):
        """Interpreta la señal del MACD"""
        if pd.isna(macd) or pd.isna(signal):
            return 'NEUTRAL'
        if macd > signal:
            return 'BULLISH'  # MACD sobre señal - alcista
        else:
            return 'BEARISH'  # MACD bajo señal - bajista
    
    @staticmethod
    def get_bb_signal(close, upper, lower):
        """Interpreta la señal de Bandas de Bollinger"""
        if pd.isna(close) or pd.isna(upper) or pd.isna(lower):
            return 'NEUTRAL'
        if close >= upper:
            return 'OVERBOUGHT'  # Precio en banda superior
        elif close <= lower:
            return 'OVERSOLD'  # Precio en banda inferior
        else:
            return 'NEUTRAL'


def calculate_adaptive_indicators(df, interval):
    """
    Calcula indicadores técnicos con períodos adaptativos para tiempo real
    Usa períodos más cortos para intervalos pequeños
    
    Args:
        df: DataFrame con datos OHLCV
        interval: Intervalo de tiempo ('1m', '5m', '15m', '30m', etc.)
    
    Returns:
        DataFrame con indicadores calculados
    """
    # Mapeo de períodos adaptativos según intervalo
    period_map = {
        '1m': {
            'sma_short': 10,    # ~10 minutos
            'sma_medium': 20,   # ~20 minutos  
            'sma_long': 50,     # ~50 minutos
            'rsi': 14,
            'macd_fast': 8,
            'macd_slow': 17,
            'macd_signal': 9,
            'bb_period': 15,
            'atr': 10,
            'adx': 10
        },
        '5m': {
            'sma_short': 12,    # ~1 hora
            'sma_medium': 24,   # ~2 horas
            'sma_long': 60,     # ~5 horas
            'rsi': 14,
            'macd_fast': 10,
            'macd_slow': 20,
            'macd_signal': 9,
            'bb_period': 20,
            'atr': 12,
            'adx': 12
        },
        '15m': {
            'sma_short': 12,    # ~3 horas
            'sma_medium': 26,   # ~6.5 horas
            'sma_long': 50,     # ~12.5 horas
            'rsi': 14,
            'macd_fast': 12,
            'macd_slow': 24,
            'macd_signal': 9,
            'bb_period': 20,
            'atr': 14,
            'adx': 14
        },
        '30m': {
            'sma_short': 12,    # ~6 horas
            'sma_medium': 24,   # ~12 horas
            'sma_long': 50,     # ~1 día
            'rsi': 14,
            'macd_fast': 12,
            'macd_slow': 26,
            'macd_signal': 9,
            'bb_period': 20,
            'atr': 14,
            'adx': 14
        }
    }
    
    # Obtener períodos para el intervalo
    periods = period_map.get(interval, period_map['30m'])
    
    # Calcular SMAs con períodos adaptativos
    df['SMA_20'] = TechnicalIndicators.calculate_sma(df, periods['sma_short'])
    df['SMA_50'] = TechnicalIndicators.calculate_sma(df, periods['sma_medium'])
    df['SMA_200'] = TechnicalIndicators.calculate_sma(df, periods['sma_long'])
    
    # EMAs
    df['EMA_12'] = TechnicalIndicators.calculate_ema(df, periods['macd_fast'])
    df['EMA_26'] = TechnicalIndicators.calculate_ema(df, periods['macd_slow'])
    
    # RSI
    df['RSI'] = TechnicalIndicators.calculate_rsi(df, periods['rsi'])
    
    # MACD con períodos adaptativos
    macd_result = TechnicalIndicators.calculate_macd(
        df, 
        fast=periods['macd_fast'],
        slow=periods['macd_slow'],
        signal=periods['macd_signal']
    )
    df['MACD'] = macd_result[0]
    df['MACD_Signal'] = macd_result[1]
    df['MACD_Histogram'] = macd_result[2]
    
    # Bandas de Bollinger
    bb_result = TechnicalIndicators.calculate_bollinger_bands(df, periods['bb_period'])
    df['BB_Upper'] = bb_result[0]
    df['BB_Middle'] = bb_result[1]
    df['BB_Lower'] = bb_result[2]
    
    # Stochastic
    stoch_result = TechnicalIndicators.calculate_stochastic(df)
    df['Stoch_K'] = stoch_result[0]
    df['Stoch_D'] = stoch_result[1]
    
    # ATR
    df['ATR'] = TechnicalIndicators.calculate_atr(df, periods['atr'])
    
    # ADX (retorna 3 valores: adx, +DI, -DI)
    adx_result = TechnicalIndicators.calculate_adx(df, periods['adx'])
    df['ADX'] = adx_result[0]
    df['Plus_DI'] = adx_result[1]
    df['Minus_DI'] = adx_result[2]
    
    # OBV
    df['OBV'] = TechnicalIndicators.calculate_obv(df)
    
    # Ichimoku (usar método estándar)
    try:
        ichimoku_result = TechnicalIndicators.calculate_ichimoku(df)
        df['Ichimoku_Tenkan'] = ichimoku_result[0]
        df['Ichimoku_Kijun'] = ichimoku_result[1]
        df['Ichimoku_SenkouA'] = ichimoku_result[2]
        df['Ichimoku_SenkouB'] = ichimoku_result[3]
    except:
        # Si falla Ichimoku, continuar sin él
        pass
    
    return df
