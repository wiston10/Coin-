"""
Aplicación principal de análisis de trading
Obtiene datos de mercado en tiempo real y genera señales de trading
"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from src.indicators.technical_indicators import TechnicalIndicators, calculate_adaptive_indicators
from src.core.trading_signals import TradingSignalEngine
from src.data_sources.market_data_sources import get_market_data, get_realtime_price
from src.strategies.bounce_strategy import BounceStrategy
from colorama import Fore, Style, init
import sys

# Inicializar colorama para colores en terminal
init(autoreset=True)


class TradingAnalyzer:
    """Aplicación principal de análisis de trading"""
    
    def __init__(self, data_source='auto'):
        self.signal_engine = TradingSignalEngine()
        self.bounce_strategy = BounceStrategy()
        self.data_source = data_source  # 'auto', 'ccxt', 'yfinance'
        
    def get_market_data(self, symbol, period='6mo', interval='1d', auto_adjust=True):
        """
        Obtiene datos del mercado usando múltiples fuentes con fallback automático
        
        Args:
            symbol: Símbolo del activo (ej: 'BTC-USD', 'AAPL', 'TSLA')
            period: Período de datos ('1mo', '3mo', '6mo', '1y', '2y', etc.)
            interval: Intervalo de tiempo ('1m', '5m', '15m', '1h', '1d', etc.)
            auto_adjust: Si True, ajusta automáticamente el período según el intervalo
        """
        try:
            # Auto-ajuste de período según intervalo para datos en tiempo real
            if auto_adjust:
                period = self._adjust_period_for_interval(interval, period)
            
            print(f"{Fore.CYAN}📊 Obteniendo datos de {symbol}...{Style.RESET_ALL}")
            
            # Usar el sistema multi-fuente (ya valida el símbolo internamente)
            df = get_market_data(symbol, period, interval, source=self.data_source)
            
            # Si el símbolo es inválido, get_market_data retorna None y ya mostró el error
            if df is None:
                print(f"{Fore.RED}❌ No se pudieron obtener datos para {symbol}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}💡 Verifica que el símbolo sea correcto{Style.RESET_ALL}")
                return None
            
            # Si hay muy pocos datos, intentar con yfinance directo como último recurso
            if df.empty or len(df) < 50:
                print(f"{Fore.YELLOW}⚠️ Pocos datos desde fuente principal, intentando yfinance...{Style.RESET_ALL}")
                ticker = yf.Ticker(symbol)
                df = ticker.history(period=period, interval=interval)
            
            if df is None or df.empty:
                print(f"{Fore.RED}❌ No hay datos disponibles para {symbol}{Style.RESET_ALL}")
                return None
            
            print(f"{Fore.GREEN}✓ Datos obtenidos: {len(df)} velas{Style.RESET_ALL}")
            return df
            
        except Exception as e:
            print(f"{Fore.RED}❌ Error al obtener datos: {str(e)}{Style.RESET_ALL}")
            return None
    
    def _adjust_period_for_interval(self, interval, period):
        """Ajusta el período automáticamente según el intervalo para maximizar datos"""
        # Mapeo de intervalos a períodos óptimos
        interval_map = {
            '1m': '7d',   # 1 minuto: máximo 7 días
            '2m': '7d',   # 2 minutos: máximo 7 días  
            '5m': '7d',   # 5 minutos: máximo 60 días pero usamos 7d para más detalle
            '15m': '7d',  # 15 minutos: máximo 60 días
            '30m': '7d',  # 30 minutos: máximo 60 días
            '60m': '7d',  # 60 minutos: máximo 730 días
            '1h': '7d',   # 1 hora: máximo 730 días
        }
        
        # Si el intervalo está en el mapa, usar el período recomendado
        if interval in interval_map:
            recommended = interval_map[interval]
            # Solo ajustar si el período solicitado es más largo
            period_days = {'1d': 1, '5d': 5, '7d': 7, '1mo': 30, '3mo': 90, '6mo': 180, '1y': 365, '2y': 730, '5y': 1825}
            
            current_days = period_days.get(period, 365)
            recommended_days = period_days.get(recommended, 7)
            
            if current_days > recommended_days and interval in ['1m', '2m', '5m']:
                return recommended
        
        return period
    
    def _combine_with_bounce(self, signal_data, bounce_analysis, df):
        """Combina la señal base con el análisis de rebotes"""
        # Si el análisis de rebotes tiene alta confianza, considerarlo
        if bounce_analysis['confidence'] >= 70 and bounce_analysis['signal'] != 'HOLD':
            # Si coinciden, aumentar confianza
            if signal_data['signal'] == bounce_analysis['signal']:
                signal_data['confidence'] = min(
                    (signal_data['confidence'] * 0.5 + bounce_analysis['confidence'] * 0.5 + 15), 
                    100
                )
                signal_data['details']['signal_source'] = 'COMBINED (Base + Rebote)'
            # Si el rebote tiene más confianza, usarlo
            elif bounce_analysis['confidence'] > signal_data['confidence'] + 15:
                signal_data['signal'] = bounce_analysis['signal']
                signal_data['confidence'] = bounce_analysis['confidence']
                signal_data['details']['signal_source'] = 'BOUNCE STRATEGY'
        
        return signal_data
    
    def _get_min_data_required(self, interval):
        """Calcula el mínimo de datos requerido según el intervalo"""
        # Para intervalos muy cortos, necesitamos menos datos históricos
        interval_requirements = {
            '1m': 100,   # 100 minutos = ~1.5 horas
            '5m': 100,   # 500 minutos = ~8 horas
            '15m': 100,  # 1500 minutos = ~1 día
            '30m': 100,  # 3000 minutos = ~2 días
            '1h': 150,   # 150 horas = ~6 días
            '4h': 150,   # 600 horas = ~25 días
            '1d': 200,   # 200 días = ~6 meses
            '1wk': 150,  # 150 semanas = ~3 años
        }
        return interval_requirements.get(interval, 200)
    
    def analyze_asset(self, symbol, period='6mo', interval='1d', show_details=True):
        """
        Analiza un activo y genera señales de trading
        """
        # Obtener datos
        df = self.get_market_data(symbol, period, interval)
        
        if df is None or df.empty:
            return None
        
        # Verificar cantidad mínima de datos según intervalo
        min_data_required = self._get_min_data_required(interval)
        if len(df) < min_data_required:
            print(f"{Fore.YELLOW}⚠️  Datos insuficientes: {len(df)}/{min_data_required} velas mínimas{Style.RESET_ALL}")
            return None
        
        # Calcular indicadores técnicos
        print(f"{Fore.CYAN}🔍 Calculando indicadores técnicos...{Style.RESET_ALL}")
        
        # Usar indicadores adaptativos para intervalos cortos
        if interval in ['1m', '5m', '15m', '30m']:
            df = calculate_adaptive_indicators(df, interval)
        else:
            df = TechnicalIndicators.calculate_all_indicators(df)
        
        # Análisis de estrategia de rebotes
        print(f"{Fore.CYAN}🎯 Analizando oportunidades de rebote...{Style.RESET_ALL}")
        trading_type = 'scalping' if interval in ['1m', '5m'] else 'medium_term'
        bounce_analysis = self.bounce_strategy.analyze_bounce(df, interval, trading_type)
        
        # Generar señal (combinando análisis base + rebotes)
        print(f"{Fore.CYAN}📈 Generando señal de trading...{Style.RESET_ALL}\n")
        signal_data = self.signal_engine.generate_signal(df)
        
        # Combinar con análisis de rebotes si tiene alta confianza
        signal_data = self._combine_with_bounce(signal_data, bounce_analysis, df)
        
        # Analizar condiciones del mercado
        market_condition = self.signal_engine.analyze_market_condition(df)
        
        # Calcular niveles de entrada/salida (usar niveles de rebotes si están disponibles)
        if bounce_analysis['signal'] != 'HOLD' and bounce_analysis['confidence'] >= 60:
            levels = {
                'entry': signal_data['details']['current_price'],
                'take_profit': bounce_analysis['take_profit'],
                'stop_loss': bounce_analysis['stop_loss'],
                'risk_reward': bounce_analysis['risk_reward']
            }
        else:
            levels = self.signal_engine.get_entry_exit_levels(df, signal_data)
        
        # Verificar si se debe entrar
        should_enter, enter_reason = self.signal_engine.should_enter_trade(signal_data)
        
        # Añadir información de rebotes al resultado
        signal_data['bounce_analysis'] = bounce_analysis
        
        # Mostrar resultados
        self._display_analysis(symbol, signal_data, market_condition, levels, should_enter, enter_reason, show_details)
        
        return {
            'symbol': symbol,
            'signal': signal_data,
            'market_condition': market_condition,
            'levels': levels,
            'should_enter': should_enter,
            'dataframe': df
        }
    
    def _display_analysis(self, symbol, signal_data, market_condition, levels, should_enter, enter_reason, show_details):
        """
        Muestra el análisis de forma formateada en la terminal
        """
        # Encabezado
        print("=" * 80)
        print(f"{Fore.CYAN}{Style.BRIGHT}{'ANÁLISIS DE TRADING':^80}{Style.RESET_ALL}")
        print("=" * 80)
        print(f"{Fore.YELLOW}Activo: {Style.BRIGHT}{symbol}{Style.RESET_ALL}")
        print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Precio actual: ${signal_data['details']['current_price']}")
        print("=" * 80)
        
        # Señal principal
        signal = signal_data['signal']
        confidence = signal_data['confidence']
        
        if signal == 'BUY':
            signal_color = Fore.GREEN
            signal_icon = "📈 COMPRAR"
        elif signal == 'SELL':
            signal_color = Fore.RED
            signal_icon = "📉 VENDER"
        else:
            signal_color = Fore.YELLOW
            signal_icon = "⏸️  MANTENER"
        
        print(f"\n{signal_color}{Style.BRIGHT}🎯 SEÑAL: {signal_icon}{Style.RESET_ALL}")
        print(f"{signal_color}Confianza: {confidence}%{Style.RESET_ALL}")
        
        # Barra de confianza
        bar_length = 40
        filled = int((confidence / 100) * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"{signal_color}[{bar}]{Style.RESET_ALL}\n")
        
        # Recomendación
        if should_enter:
            print(f"{Fore.GREEN}✓ RECOMENDACIÓN: Entrar en la operación{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}⚠️  RECOMENDACIÓN: No entrar - {enter_reason}{Style.RESET_ALL}")
        
        print("\n" + "-" * 80)
        
        # Condiciones del mercado
        print(f"\n{Fore.CYAN}{Style.BRIGHT}📊 CONDICIONES DEL MERCADO:{Style.RESET_ALL}")
        print(f"   Tendencia: {self._format_trend(market_condition['trend'])}")
        print(f"   Fase: {market_condition['market_phase']}")
        print(f"   Volatilidad: {market_condition['volatility']} ({market_condition['volatility_pct']}%)")
        print(f"   Volumen: {market_condition['volume']}")
        print(f"   Fuerza de tendencia: {market_condition['trend_strength']}")
        if market_condition['adx']:
            print(f"   ADX: {market_condition['adx']}")
        
        # Niveles de trading
        if levels:
            print(f"\n{Fore.CYAN}{Style.BRIGHT}🎯 NIVELES DE TRADING:{Style.RESET_ALL}")
            print(f"   Entrada: ${levels['entry']}")
            print(f"   Stop Loss: ${levels['stop_loss']}")
            print(f"   Take Profit: ${levels['take_profit']}")
            print(f"   Riesgo: ${levels['risk']}")
            print(f"   Recompensa: ${levels['reward']}")
            print(f"   Risk/Reward: {levels['risk_reward_ratio']}:1")
        
        # Razones de la señal
        print(f"\n{Fore.CYAN}{Style.BRIGHT}📋 RAZONES DE LA SEÑAL:{Style.RESET_ALL}")
        for i, reason in enumerate(signal_data['reasons'], 1):
            print(f"   {i}. {reason}")
        
        # Análisis de rebotes (si está disponible)
        if 'bounce_analysis' in signal_data:
            bounce = signal_data['bounce_analysis']
            if bounce['signal'] != 'HOLD' and bounce['confidence'] >= 50:
                print(f"\n{Fore.MAGENTA}{Style.BRIGHT}🎯 ESTRATEGIA DE REBOTES:{Style.RESET_ALL}")
                print(f"   Señal: {bounce['signal']} (Confianza: {bounce['confidence']:.0f}%)")
                print(f"   Probabilidad de rebote: {bounce['bounce_probability']:.0f}%")
                print(f"   Éxito histórico: {bounce['historical_success_rate']:.0f}%")
                print(f"   Psicología del mercado: {bounce['psychology']['sentiment']}")
                print(f"   {bounce['psychology']['description']}")
                
                if bounce['support_levels']:
                    print(f"   Soportes clave: {', '.join(f'${s:,.2f}' for s in bounce['support_levels'][-3:])}")
                if bounce['resistance_levels']:
                    print(f"   Resistencias clave: {', '.join(f'${r:,.2f}' for r in bounce['resistance_levels'][:3])}")
                
                print(f"\n   {Fore.MAGENTA}Razones del rebote:{Style.RESET_ALL}")
                for i, reason in enumerate(bounce['reasons'], 1):
                    print(f"   {i}. {reason}")
        
        if show_details:
            # Detalles técnicos
            print(f"\n{Fore.CYAN}{Style.BRIGHT}🔧 DETALLES TÉCNICOS:{Style.RESET_ALL}")
            details = signal_data['details']
            
            if details['pattern']:
                print(f"   Patrón de vela: {details['pattern']} ({details['pattern_signal']})")
            
            if details['rsi']:
                print(f"   RSI: {details['rsi']} - {details['rsi_signal']}")
            
            print(f"   MACD: {details['macd_signal']}")
            print(f"   Bandas de Bollinger: {details['bb_signal']}")
            print(f"   Tendencia general: {details['trend']}")
            print(f"   Fuerza de tendencia: {details['trend_strength']}/100")
            
            if details['support_levels']:
                print(f"   Soportes: {', '.join(f'${s}' for s in details['support_levels'])}")
            
            if details['resistance_levels']:
                print(f"   Resistencias: {', '.join(f'${r}' for r in details['resistance_levels'])}")
        
        print("\n" + "=" * 80 + "\n")
    
    def _format_trend(self, trend):
        """Formatea la tendencia con colores"""
        if 'BULLISH' in trend:
            return f"{Fore.GREEN}{trend}{Style.RESET_ALL}"
        elif 'BEARISH' in trend:
            return f"{Fore.RED}{trend}{Style.RESET_ALL}"
        else:
            return f"{Fore.YELLOW}{trend}{Style.RESET_ALL}"
    
    def compare_assets(self, symbols, period='6mo', interval='1d'):
        """
        Compara múltiples activos y muestra una tabla comparativa
        """
        print(f"\n{Fore.CYAN}{Style.BRIGHT}🔄 ANÁLISIS COMPARATIVO{Style.RESET_ALL}\n")
        
        results = []
        
        for symbol in symbols:
            print(f"\n{Fore.YELLOW}Analizando {symbol}...{Style.RESET_ALL}")
            result = self.analyze_asset(symbol, period, interval, show_details=False)
            if result:
                results.append(result)
        
        # Mostrar tabla comparativa
        if results:
            print("\n" + "=" * 120)
            print(f"{Fore.CYAN}{Style.BRIGHT}{'RESUMEN COMPARATIVO':^120}{Style.RESET_ALL}")
            print("=" * 120)
            
            # Encabezados
            headers = f"{'SÍMBOLO':<15} {'SEÑAL':<12} {'CONFIANZA':<12} {'TENDENCIA':<20} {'PRECIO':<12} {'R/R':<8}"
            print(f"{Fore.CYAN}{Style.BRIGHT}{headers}{Style.RESET_ALL}")
            print("-" * 120)
            
            # Datos
            for result in results:
                symbol = result['symbol']
                signal = result['signal']['signal']
                confidence = result['signal']['confidence']
                trend = result['market_condition']['trend']
                price = result['signal']['details']['current_price']
                rr = result['levels']['risk_reward_ratio'] if result['levels'] else 0
                
                # Colorear según señal
                if signal == 'BUY':
                    signal_str = f"{Fore.GREEN}COMPRAR{Style.RESET_ALL}"
                elif signal == 'SELL':
                    signal_str = f"{Fore.RED}VENDER{Style.RESET_ALL}"
                else:
                    signal_str = f"{Fore.YELLOW}MANTENER{Style.RESET_ALL}"
                
                print(f"{symbol:<15} {signal_str:<20} {confidence:<12.2f} {trend:<20} ${price:<11.2f} {rr:<8.2f}")
            
            print("=" * 120 + "\n")


def main():
    """Función principal"""
    analyzer = TradingAnalyzer()
    
    print(f"{Fore.CYAN}{Style.BRIGHT}")
    print("=" * 80)
    print(" " * 20 + "SISTEMA DE ANÁLISIS DE TRADING")
    print(" " * 15 + "Detección automática de señales de compra/venta")
    print("=" * 80)
    print(Style.RESET_ALL)
    
    # Menú interactivo
    while True:
        print(f"\n{Fore.YELLOW}OPCIONES:{Style.RESET_ALL}")
        print("1. Analizar un activo")
        print("2. Comparar múltiples activos")
        print("3. Analizar criptomonedas populares")
        print("4. Analizar acciones populares")
        print("5. Salir")
        
        choice = input(f"\n{Fore.CYAN}Selecciona una opción (1-5): {Style.RESET_ALL}").strip()
        
        if choice == '1':
            symbol = input(f"\n{Fore.CYAN}Ingresa el símbolo del activo (ej: BTC-USD, AAPL, TSLA): {Style.RESET_ALL}").strip().upper()
            period = input(f"{Fore.CYAN}Período (1mo/3mo/6mo/1y/2y) [6mo]: {Style.RESET_ALL}").strip() or '6mo'
            interval = input(f"{Fore.CYAN}Intervalo (1d/1h/30m/15m) [1d]: {Style.RESET_ALL}").strip() or '1d'
            
            analyzer.analyze_asset(symbol, period, interval)
            
        elif choice == '2':
            symbols_input = input(f"\n{Fore.CYAN}Ingresa los símbolos separados por comas (ej: BTC-USD,ETH-USD,AAPL): {Style.RESET_ALL}").strip().upper()
            symbols = [s.strip() for s in symbols_input.split(',')]
            period = input(f"{Fore.CYAN}Período (1mo/3mo/6mo/1y) [6mo]: {Style.RESET_ALL}").strip() or '6mo'
            
            analyzer.compare_assets(symbols, period=period)
            
        elif choice == '3':
            crypto_symbols = ['BTC-USD', 'ETH-USD', 'BNB-USD', 'ADA-USD', 'SOL-USD']
            print(f"\n{Fore.CYAN}Analizando criptomonedas: {', '.join(crypto_symbols)}{Style.RESET_ALL}")
            analyzer.compare_assets(crypto_symbols)
            
        elif choice == '4':
            stock_symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN']
            print(f"\n{Fore.CYAN}Analizando acciones: {', '.join(stock_symbols)}{Style.RESET_ALL}")
            analyzer.compare_assets(stock_symbols)
            
        elif choice == '5':
            print(f"\n{Fore.GREEN}¡Hasta luego! 👋{Style.RESET_ALL}\n")
            break
            
        else:
            print(f"{Fore.RED}❌ Opción inválida{Style.RESET_ALL}")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Programa interrumpido por el usuario{Style.RESET_ALL}\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}\n")
        sys.exit(1)
