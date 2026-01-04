"""
Sistema de Trading en Tiempo Real con Web Scraping
Optimizado para Scalping con datos actualizados cada segundo
"""
import pandas as pd
import numpy as np
from datetime import datetime
from src.data_sources.web_scraper import get_live_data, get_realtime_price
from src.indicators.technical_indicators import TechnicalIndicators, calculate_adaptive_indicators
from src.strategies.bounce_strategy import BounceStrategy
from src.core.trading_signals import TradingSignalEngine
from colorama import Fore, Style, init
import time

init(autoreset=True)


class LiveTradingAnalyzer:
    """
    Analizador de trading en tiempo real
    Usa web scraping para datos actualizados constantemente
    """
    
    def __init__(self):
        self.signal_engine = TradingSignalEngine()
        self.bounce_strategy = BounceStrategy()
        
    def analyze_live(self, symbol, interval='1m', show_details=True):
        """
        Análisis en tiempo real con datos frescos del exchange
        
        Args:
            symbol: 'BTC-USD', 'ETH-USD', etc.
            interval: '1m', '5m', '15m' (para scalping usar 1m o 5m)
            show_details: Mostrar detalles completos
        
        Returns:
            dict con análisis completo
        """
        try:
            # Obtener datos en vivo
            print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{Style.BRIGHT}📊 ANÁLISIS EN TIEMPO REAL: {symbol}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
            
            # Determinar límite de velas según intervalo
            limits = {'1m': 500, '5m': 300, '15m': 200, '30m': 150, '1h': 100}
            limit = limits.get(interval, 300)
            
            df = get_live_data(symbol, interval, limit=limit)
            
            if df is None or df.empty:
                print(f"{Fore.RED}❌ No se pudieron obtener datos en vivo{Style.RESET_ALL}")
                return None
            
            if len(df) < 50:
                print(f"{Fore.YELLOW}⚠️ Pocos datos: {len(df)} velas. Recomendado: 100+{Style.RESET_ALL}")
            
            # Calcular indicadores técnicos
            print(f"{Fore.CYAN}🔍 Calculando indicadores técnicos...{Style.RESET_ALL}")
            
            if interval in ['1m', '5m', '15m', '30m']:
                df = calculate_adaptive_indicators(df, interval)
            else:
                df = TechnicalIndicators.calculate_all_indicators(df)
            
            # Análisis de estrategia de rebotes
            print(f"{Fore.CYAN}🎯 Analizando oportunidades de rebote...{Style.RESET_ALL}")
            trading_type = 'scalping' if interval in ['1m', '5m'] else 'medium_term'
            bounce_analysis = self.bounce_strategy.analyze_bounce(df, interval, trading_type)
            
            # Generar señal
            print(f"{Fore.CYAN}📈 Generando señal de trading...{Style.RESET_ALL}\n")
            signal_data = self.signal_engine.generate_signal(df)
            
            # Combinar con análisis de rebotes
            signal_data = self._combine_with_bounce(signal_data, bounce_analysis, df)
            signal_data['bounce_analysis'] = bounce_analysis
            
            # Condiciones del mercado
            market_condition = self.signal_engine.analyze_market_condition(df)
            
            # Niveles de entrada/salida
            if bounce_analysis['signal'] != 'HOLD' and bounce_analysis['confidence'] >= 60:
                levels = {
                    'entry': signal_data['details']['current_price'],
                    'take_profit': bounce_analysis['take_profit'],
                    'stop_loss': bounce_analysis['stop_loss'],
                    'risk_reward': bounce_analysis['risk_reward']
                }
            else:
                levels = self.signal_engine.get_entry_exit_levels(df, signal_data)
            
            should_enter, enter_reason = self.signal_engine.should_enter_trade(signal_data)
            
            # Mostrar resultados
            if show_details:
                self._display_live_analysis(symbol, signal_data, market_condition, 
                                           levels, should_enter, enter_reason, interval)
            
            return {
                'symbol': symbol,
                'signal': signal_data,
                'market_condition': market_condition,
                'levels': levels,
                'should_enter': should_enter,
                'dataframe': df,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            print(f"{Fore.RED}❌ Error en análisis: {str(e)}{Style.RESET_ALL}")
            import traceback
            traceback.print_exc()
            return None
    
    def _combine_with_bounce(self, signal_data, bounce_analysis, df):
        """Combina señal base con análisis de rebotes"""
        if bounce_analysis['confidence'] >= 70 and bounce_analysis['signal'] != 'HOLD':
            if signal_data['signal'] == bounce_analysis['signal']:
                signal_data['confidence'] = min(
                    (signal_data['confidence'] * 0.5 + bounce_analysis['confidence'] * 0.5 + 15), 
                    100
                )
                signal_data['details']['signal_source'] = 'COMBINED (Base + Rebote)'
            elif bounce_analysis['confidence'] > signal_data['confidence'] + 15:
                signal_data['signal'] = bounce_analysis['signal']
                signal_data['confidence'] = bounce_analysis['confidence']
                signal_data['details']['signal_source'] = 'BOUNCE STRATEGY'
        
        return signal_data
    
    def _display_live_analysis(self, symbol, signal_data, market_condition, 
                               levels, should_enter, enter_reason, interval):
        """Muestra análisis en terminal con formato para scalping"""
        
        # Ticker en tiempo real
        ticker = get_realtime_price(symbol)
        
        print("=" * 80)
        print(f"{Fore.GREEN}{Style.BRIGHT}{'🔴 ANÁLISIS EN VIVO':^80}{Style.RESET_ALL}")
        print("=" * 80)
        
        # Información del activo
        print(f"{Fore.YELLOW}Activo: {Style.BRIGHT}{symbol}{Style.RESET_ALL}")
        print(f"Intervalo: {interval} {'(SCALPING)' if interval in ['1m', '5m'] else '(MEDIANO PLAZO)'}")
        print(f"Hora: {datetime.now().strftime('%H:%M:%S')}")
        
        if ticker:
            print(f"Precio actual: ${ticker['price']:,.2f}")
            change_color = Fore.GREEN if ticker['change_24h'] > 0 else Fore.RED
            print(f"Cambio 24h: {change_color}{ticker['change_24h']:+.2f}%{Style.RESET_ALL}")
            print(f"Bid/Ask: ${ticker['bid']:,.2f} / ${ticker['ask']:,.2f}")
            print(f"Volumen 24h: ${ticker['volume_24h']:,.0f}")
        else:
            print(f"Precio actual: ${signal_data['details']['current_price']}")
        
        print("=" * 80)
        
        # Señal principal
        signal = signal_data['signal']
        confidence = signal_data['confidence']
        
        signal_colors = {'BUY': Fore.GREEN, 'SELL': Fore.RED, 'HOLD': Fore.YELLOW}
        signal_icons = {'BUY': "📈 COMPRAR", 'SELL': "📉 VENDER", 'HOLD': "⏸️ MANTENER"}
        
        color = signal_colors.get(signal, Fore.WHITE)
        icon = signal_icons.get(signal, signal)
        
        print(f"\n{color}{Style.BRIGHT}🎯 SEÑAL: {icon}{Style.RESET_ALL}")
        print(f"{color}Confianza: {confidence:.1f}%{Style.RESET_ALL}")
        
        # Barra visual
        bar_length = 40
        filled = int((confidence / 100) * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"{color}[{bar}]{Style.RESET_ALL}\n")
        
        # Recomendación de entrada
        if should_enter:
            print(f"{Fore.GREEN}✓ RECOMENDACIÓN: ENTRAR AHORA{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}⚠️ RECOMENDACIÓN: No entrar - {enter_reason}{Style.RESET_ALL}")
        
        print("\n" + "-" * 80)
        
        # Análisis de rebotes (destacado para scalping)
        if 'bounce_analysis' in signal_data:
            bounce = signal_data['bounce_analysis']
            if bounce['signal'] != 'HOLD' and bounce['confidence'] >= 50:
                print(f"\n{Fore.MAGENTA}{Style.BRIGHT}🎯 OPORTUNIDAD DE REBOTE:{Style.RESET_ALL}")
                print(f"   Señal: {bounce['signal']} | Confianza: {bounce['confidence']:.0f}%")
                print(f"   Probabilidad: {bounce['bounce_probability']:.0f}% | Éxito histórico: {bounce['historical_success_rate']:.0f}%")
                print(f"   Psicología: {bounce['psychology']['sentiment']}")
                
                if bounce['reasons']:
                    print(f"\n   {Fore.MAGENTA}Razones:{Style.RESET_ALL}")
                    for reason in bounce['reasons'][:3]:
                        print(f"   • {reason}")
                
                print("-" * 80)
        
        # Niveles de trading (crítico para scalping)
        if levels and signal != 'HOLD':
            print(f"\n{Fore.CYAN}{Style.BRIGHT}🎯 NIVELES DE TRADING:{Style.RESET_ALL}")
            print(f"   📍 Entrada:      ${levels['entry']:,.2f}")
            print(f"   🎯 Take Profit:  ${levels['take_profit']:,.2f}")
            print(f"   🛑 Stop Loss:    ${levels['stop_loss']:,.2f}")
            
            if 'risk' in levels and 'reward' in levels:
                print(f"   ⚠️  Riesgo:       ${levels['risk']:,.2f}")
                print(f"   💰 Recompensa:   ${levels['reward']:,.2f}")
            
            print(f"   ⚖️  Risk/Reward:  {levels['risk_reward_ratio'] if 'risk_reward_ratio' in levels else levels.get('risk_reward', 0):.2f}:1")
        
        # Condiciones del mercado
        print(f"\n{Fore.CYAN}{Style.BRIGHT}📊 MERCADO:{Style.RESET_ALL}")
        print(f"   Tendencia: {market_condition['trend']} | Fase: {market_condition['market_phase']}")
        print(f"   Volatilidad: {market_condition['volatility']} ({market_condition['volatility_pct']:.2f}%)")
        print(f"   Volumen: {market_condition['volume']} | Fuerza: {market_condition['trend_strength']}")
        
        print("\n" + "=" * 80 + "\n")
    
    def monitor_continuous(self, symbol, interval='1m', update_seconds=5):
        """
        Monitoreo continuo con actualizaciones automáticas
        Ideal para scalping activo
        
        Args:
            symbol: Par de trading
            interval: Intervalo de velas
            update_seconds: Segundos entre actualizaciones
        """
        print(f"{Fore.GREEN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{Style.BRIGHT}🔴 MONITOR EN VIVO INICIADO{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'='*80}{Style.RESET_ALL}\n")
        print(f"Activo: {symbol}")
        print(f"Intervalo: {interval}")
        print(f"Actualización: cada {update_seconds} segundos")
        print(f"\n⏹️  Presiona Ctrl+C para detener\n")
        
        iteration = 0
        try:
            while True:
                iteration += 1
                print(f"\n{Fore.CYAN}{'─'*80}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}Actualización #{iteration} - {datetime.now().strftime('%H:%M:%S')}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}{'─'*80}{Style.RESET_ALL}\n")
                
                # Análisis actualizado
                result = self.analyze_live(symbol, interval, show_details=True)
                
                if result is None:
                    print(f"{Fore.RED}⚠️ Error en análisis, reintentando...{Style.RESET_ALL}")
                
                # Esperar antes de siguiente actualización
                print(f"\n⏳ Próxima actualización en {update_seconds} segundos...")
                time.sleep(update_seconds)
                
        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}⏹️ Monitor detenido por usuario{Style.RESET_ALL}")
            print(f"{Fore.GREEN}Total de análisis: {iteration}{Style.RESET_ALL}\n")


# Función de conveniencia
def analyze_live(symbol, interval='1m'):
    """
    Analiza un activo en tiempo real
    
    Args:
        symbol: 'BTC-USD', 'ETH-USD', etc.
        interval: '1m', '5m', '15m'
    
    Returns:
        dict con análisis completo
    """
    analyzer = LiveTradingAnalyzer()
    return analyzer.analyze_live(symbol, interval)


def start_monitor(symbol, interval='1m', update_seconds=5):
    """
    Inicia monitor continuo en tiempo real
    
    Args:
        symbol: Par de trading
        interval: Intervalo de velas
        update_seconds: Segundos entre actualizaciones
    """
    analyzer = LiveTradingAnalyzer()
    analyzer.monitor_continuous(symbol, interval, update_seconds)


if __name__ == "__main__":
    import sys
    
    # Si se ejecuta directamente, iniciar monitor
    if len(sys.argv) > 1:
        symbol = sys.argv[1]
        interval = sys.argv[2] if len(sys.argv) > 2 else '1m'
        start_monitor(symbol, interval)
    else:
        print("Uso: python3 live_trading.py BTC-USD 1m")
        print("\nEjemplo rápido:")
        result = analyze_live('BTC-USD', '5m')
