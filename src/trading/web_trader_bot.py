#!/usr/bin/env python3
"""
Bot de Trading Automatizado con Selenium
Ejecuta operaciones de compra/venta en plataformas de trading web según análisis técnicos
Soporta múltiples brokers: Binomo, IQ Option, Quotex, etc.
"""

import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
import pandas as pd
from pathlib import Path

# Importaciones de Selenium - opcionales
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.firefox.service import Service
    from selenium.webdriver.firefox.options import Options
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    from webdriver_manager.firefox import GeckoDriverManager
    SELENIUM_AVAILABLE = True
except ImportError as e:
    SELENIUM_AVAILABLE = False
    logging.warning(f"⚠️ Selenium/Firefox no disponible: {e}")
    logging.warning("   El bot de trading web no funcionará. Instala: pip install selenium webdriver-manager")


class WebTraderBot:
    """
    Bot de trading automatizado que ejecuta operaciones en plataformas web
    usando Selenium para automatización del navegador
    """
    
    def __init__(self, platform: str = 'binomo', headless: bool = False):
        """
        Inicializa el bot de trading web
        
        Args:
            platform: Plataforma de trading ('binomo', 'iqoption', 'quotex')
            headless: Si True, ejecuta en modo headless (sin interfaz gráfica)
        """
        # Verificar si Selenium está disponible
        if not SELENIUM_AVAILABLE:
            raise ImportError(
                "Selenium/Firefox no está instalado. "
                "Instala las dependencias: pip install selenium webdriver-manager"
            )
        
        self.platform = platform.lower()
        self.headless = headless
        self.driver = None
        self.is_logged_in = False
        self.current_balance = 0.0
        self.trade_history = []
        
        # Configuración de logging
        self.logger = logging.getLogger(f'WebTraderBot-{platform}')
        self.logger.setLevel(logging.INFO)
        
        # Configuración específica por plataforma
        self.platform_config = self._get_platform_config()
        
        # Estadísticas
        self.stats = {
            'total_trades': 0,
            'successful_trades': 0,
            'failed_trades': 0,
            'total_profit': 0.0,
            'win_rate': 0.0
        }
        
    def _get_platform_config(self) -> Dict:
        """Obtiene la configuración específica de cada plataforma"""
        configs = {
            'binomo': {
                'url': 'https://binomo.com/',
                'login_url': 'https://binomo.com/trading',
                'selectors': {
                    'email_input': '.way-input_invalid__14Ohy',
                    'password_input': '#qa_auth_LoginPasswordInput > way-input:nth-child(1)',
                    'login_button': '#qa_auth_LoginBtn > button',
                    'asset_selector': '.asset-select',
                    'amount_input': '.deal-amount input',
                    'buy_button': '.btn-purchase-up',
                    'sell_button': '.btn-purchase-down',
                    'time_selector': '.expiration-time',
                    'balance': '.balance-value',
                    'chart_container': '#trading-chart'
                },
                'timeframes': ['1m', '5m', '15m', '30m', '1h']
            },
            'iqoption': {
                'url': 'https://iqoption.com/',
                'login_url': 'https://iqoption.com/traderoom',
                'selectors': {
                    'email_input': 'input[data-test="email"]',
                    'password_input': 'input[data-test="password"]',
                    'login_button': 'button[data-test="login-button"]',
                    'asset_selector': '.instrument-picker',
                    'amount_input': '.investment-amount input',
                    'buy_button': '.call-button',
                    'sell_button': '.put-button',
                    'time_selector': '.expiration-picker',
                    'balance': '.balance-info-value',
                    'chart_container': '#chart'
                },
                'timeframes': ['1m', '5m', '15m', '30m', '1h']
            },
            'quotex': {
                'url': 'https://quotex.io/',
                'login_url': 'https://quotex.io/trading',
                'selectors': {
                    'email_input': 'input[name="email"]',
                    'password_input': 'input[name="password"]',
                    'login_button': '.login-btn',
                    'asset_selector': '.assets__item',
                    'amount_input': 'input.trades-invest__input',
                    'buy_button': '.btn-trade.btn-success',
                    'sell_button': '.btn-trade.btn-danger',
                    'time_selector': '.expiration__item',
                    'balance': '.header__balance',
                    'chart_container': '#chart-container'
                },
                'timeframes': ['1m', '5m', '15m', '30m', '1h']
            }
        }
        
        return configs.get(self.platform, configs['binomo'])
    
    def setup_driver(self) -> None:
        """Configura el driver de Selenium con opciones optimizadas para Firefox"""
        try:
            firefox_options = Options()
            
            # Usar perfil de Firefox existente
            firefox_profile_path = '/Users/wistonnavarroaroca/Library/Application Support/Firefox/Profiles/3qqj3de2.default'
            firefox_options.add_argument('-profile')
            firefox_options.add_argument(firefox_profile_path)
            
            if self.headless:
                firefox_options.add_argument('--headless')
            
            # Opciones para mejor rendimiento y evitar detección
            firefox_options.set_preference('dom.webdriver.enabled', False)
            firefox_options.set_preference('useAutomationExtension', False)
            firefox_options.set_preference('marionette', True)
            
            # User agent real
            firefox_options.set_preference('general.useragent.override', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:122.0) Gecko/20100101 Firefox/122.0')
            
            # Instalar GeckoDriver automáticamente
            service = Service(GeckoDriverManager().install())
            
            self.driver = webdriver.Firefox(service=service, options=firefox_options)
            self.driver.maximize_window()
            
            # Configurar timeouts
            self.driver.implicitly_wait(10)
            
            self.logger.info(f"✅ Driver de Selenium con Firefox configurado para {self.platform}")
            
        except Exception as e:
            self.logger.error(f"❌ Error configurando driver: {e}")
            raise
    
    def login(self, email: str, password: str) -> bool:
        """
        Inicia sesión en la plataforma de trading
        
        Args:
            email: Correo electrónico
            password: Contraseña
            
        Returns:
            True si el login fue exitoso
        """
        try:
            if not self.driver:
                self.setup_driver()

            self.logger.info(f"🔐 Iniciando sesión en {self.platform}...")

            # Navegar a la página de login (fallback a url principal si falla)
            try:
                self.driver.get(self.platform_config.get('login_url') or self.platform_config.get('url'))
            except Exception:
                self.driver.get(self.platform_config.get('url'))

            time.sleep(2)

            wait = WebDriverWait(self.driver, 20)

            # Intentar abrir modal de login si existe (varios selectores comunes)
            login_open_selectors = [
                'a[href*="login"]',
                'button.login',
                '.auth-login',
                '.signin-button',
                '.login-btn',
            ]

            for sel in login_open_selectors:
                try:
                    el = self.driver.find_element(By.CSS_SELECTOR, sel)
                    if el.is_displayed():
                        try:
                            el.click()
                            time.sleep(1)
                        except Exception:
                            pass
                        break
                except Exception:
                    continue

            # Helpers: probar múltiples selectores y buscar dentro de iframes
            def try_find_and_send(selectors, value):
                # Intentar en documento principal
                for s in selectors:
                    try:
                        el = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, s)))
                        el.clear()
                        el.send_keys(value)
                        return True
                    except Exception:
                        continue

                # Intentar dentro de iframes
                iframes = self.driver.find_elements(By.TAG_NAME, 'iframe')
                for i, frame in enumerate(iframes):
                    try:
                        self.driver.switch_to.frame(frame)
                        for s in selectors:
                            try:
                                el = self.driver.find_element(By.CSS_SELECTOR, s)
                                el.clear()
                                el.send_keys(value)
                                self.driver.switch_to.default_content()
                                return True
                            except Exception:
                                continue
                    except Exception:
                        pass
                    finally:
                        try:
                            self.driver.switch_to.default_content()
                        except Exception:
                            pass

                return False

            email_selectors = [
                # Selectores específicos detectados en la página de Binomo
                '#qa_auth_LoginEmailInput > way-input input',
                '#qa_auth_LoginEmailInput way-input-text input',
                self.platform_config['selectors'].get('email_input'),
                'input[type="email"]',
                'input[placeholder*="email"]',
                'input[placeholder*="Email"]',
                'input[id*="email"]',
                'input[name*="email"]',
                'input.login-email'
            ]

            password_selectors = [
                # Selectores específicos detectados en la página de Binomo
                '#qa_auth_LoginPasswordInput > way-input > div > div > way-input-password > input[type=password]',
                '#qa_auth_LoginPasswordInput way-input-password input',
                self.platform_config['selectors'].get('password_input'),
                'input[type="password"]',
                'input[placeholder*="password"]',
                'input[id*="password"]',
                'input[name*="password"]',
                'input.login-password'
            ]

            # Enviar email y password
            sent_email = try_find_and_send([s for s in email_selectors if s], email)
            sent_password = try_find_and_send([s for s in password_selectors if s], password)

            # Si no pudo encontrar inputs, intentar cargar la página de login directamente y reintentar
            if not sent_email or not sent_password:
                try:
                    self.driver.get(self.platform_config.get('login_url') or self.platform_config.get('url'))
                    time.sleep(2)
                    sent_email = sent_email or try_find_and_send([s for s in email_selectors if s], email)
                    sent_password = sent_password or try_find_and_send([s for s in password_selectors if s], password)
                except Exception:
                    pass

            # Intentar hacer click en botón de login con varios selectores
            login_button_selectors = [
                # Selector con id presente en el HTML
                '#qa_auth_LoginBtn > button',
                '#qa_auth_LoginBtn',
                self.platform_config['selectors'].get('login_button'),
                'button[type="submit"]',
                'button.login',
                '.btn-login',
                'button[data-test="login-button"]',
            ]

            for s in login_button_selectors:
                if not s:
                    continue
                try:
                    btn = self.driver.find_element(By.CSS_SELECTOR, s)
                    btn.click()
                    time.sleep(2)
                    break
                except Exception:
                    # intentar en iframes
                    try:
                        iframes = self.driver.find_elements(By.TAG_NAME, 'iframe')
                        for frame in iframes:
                            try:
                                self.driver.switch_to.frame(frame)
                                btn = self.driver.find_element(By.CSS_SELECTOR, s)
                                btn.click()
                                time.sleep(2)
                                self.driver.switch_to.default_content()
                                raise StopIteration
                            except StopIteration:
                                break
                            except Exception:
                                pass
                            finally:
                                try:
                                    self.driver.switch_to.default_content()
                                except Exception:
                                    pass
                    except Exception:
                        pass

            # Esperar a que cargue la plataforma
            time.sleep(4)

            # Verificar si el login fue exitoso buscando elementos de trading
            try:
                wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.platform_config['selectors']['chart_container']))
                )
                self.is_logged_in = True
                self.update_balance()
                self.logger.info(f"✅ Login exitoso. Balance: ${self.current_balance:.2f}")
                return True
            except TimeoutException:
                self.logger.error("❌ Login fallido - No se encontró la plataforma de trading")
                return False

        except Exception as e:
            self.logger.error(f"❌ Error durante login: {e}")
            return False
    
    def update_balance(self) -> float:
        """Actualiza y retorna el balance actual"""
        try:
            balance_element = self.driver.find_element(By.CSS_SELECTOR, self.platform_config['selectors']['balance'])
            balance_text = balance_element.text.strip().replace('$', '').replace(',', '')
            self.current_balance = float(balance_text)
            return self.current_balance
        except Exception as e:
            self.logger.warning(f"⚠️ No se pudo actualizar balance: {e}")
            return self.current_balance
    
    def select_asset(self, symbol: str) -> bool:
        """
        Selecciona el activo para operar
        
        Args:
            symbol: Símbolo del activo (ej: 'EUR/USD', 'BTC')
        """
        try:
            self.logger.info(f"📊 Seleccionando activo: {symbol}")
            
            # Click en selector de activos
            asset_selector = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, self.platform_config['selectors']['asset_selector']))
            )
            asset_selector.click()
            time.sleep(1)
            
            # Buscar el activo (esto varía por plataforma)
            # Buscar en la lista de activos
            assets = self.driver.find_elements(By.CSS_SELECTOR, '.asset-item, .instrument-item, .assets__item')
            
            for asset in assets:
                if symbol.upper() in asset.text.upper():
                    asset.click()
                    time.sleep(1)
                    self.logger.info(f"✅ Activo seleccionado: {symbol}")
                    return True
            
            self.logger.warning(f"⚠️ No se encontró el activo: {symbol}")
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Error seleccionando activo: {e}")
            return False
    
    def set_amount(self, amount: float) -> bool:
        """
        Establece el monto de la inversión
        
        Args:
            amount: Monto a invertir
        """
        try:
            amount_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.platform_config['selectors']['amount_input']))
            )
            
            # Limpiar y establecer monto
            amount_input.clear()
            amount_input.send_keys(str(amount))
            time.sleep(0.5)
            
            self.logger.info(f"💰 Monto establecido: ${amount:.2f}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error estableciendo monto: {e}")
            return False
    
    def set_expiration(self, timeframe: str) -> bool:
        """
        Establece el tiempo de expiración del trade
        
        Args:
            timeframe: Tiempo de expiración ('1m', '5m', '15m', etc.)
        """
        try:
            if timeframe not in self.platform_config['timeframes']:
                self.logger.warning(f"⚠️ Timeframe no soportado: {timeframe}")
                return False
            
            time_selector = self.driver.find_element(By.CSS_SELECTOR, self.platform_config['selectors']['time_selector'])
            time_selector.click()
            time.sleep(0.5)
            
            # Buscar y seleccionar el timeframe
            timeframes = self.driver.find_elements(By.CSS_SELECTOR, '.time-option, .expiration-option, .expiration__item')
            
            for tf in timeframes:
                if timeframe in tf.text.lower():
                    tf.click()
                    time.sleep(0.5)
                    self.logger.info(f"⏱️ Expiración establecida: {timeframe}")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Error estableciendo expiración: {e}")
            return False
    
    def execute_trade(self, direction: str, symbol: str, amount: float, timeframe: str = '5m') -> Dict:
        """
        Ejecuta una operación de trading
        
        Args:
            direction: Dirección del trade ('BUY' o 'SELL')
            symbol: Símbolo del activo
            amount: Monto a invertir
            timeframe: Tiempo de expiración
            
        Returns:
            Diccionario con resultado de la operación
        """
        if not self.is_logged_in:
            return {'success': False, 'error': 'No está logueado'}
        
        try:
            self.logger.info(f"🚀 Ejecutando trade: {direction} {symbol} ${amount} {timeframe}")
            
            # Seleccionar activo
            if not self.select_asset(symbol):
                return {'success': False, 'error': f'No se pudo seleccionar {symbol}'}
            
            # Establecer monto
            if not self.set_amount(amount):
                return {'success': False, 'error': 'No se pudo establecer el monto'}
            
            # Establecer expiración
            if not self.set_expiration(timeframe):
                self.logger.warning("⚠️ No se pudo establecer expiración, usando default")
            
            # Ejecutar trade
            button_selector = self.platform_config['selectors']['buy_button' if direction.upper() == 'BUY' else 'sell_button']
            
            trade_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, button_selector))
            )
            
            trade_button.click()
            time.sleep(1)
            
            # Registrar trade
            trade_info = {
                'success': True,
                'timestamp': datetime.now(),
                'symbol': symbol,
                'direction': direction,
                'amount': amount,
                'timeframe': timeframe,
                'platform': self.platform
            }
            
            self.trade_history.append(trade_info)
            self.stats['total_trades'] += 1
            
            self.logger.info(f"✅ Trade ejecutado: {direction} {symbol}")
            
            # Actualizar balance
            time.sleep(2)
            self.update_balance()
            
            return trade_info
            
        except Exception as e:
            self.logger.error(f"❌ Error ejecutando trade: {e}")
            self.stats['failed_trades'] += 1
            return {'success': False, 'error': str(e)}
    
    def execute_trade_with_analysis(self, analysis_result: Dict) -> Dict:
        """
        Ejecuta un trade basado en el resultado de análisis técnico
        
        Args:
            analysis_result: Resultado del análisis técnico del sistema
            
        Returns:
            Resultado de la ejecución
        """
        try:
            # Extraer información del análisis
            signal = analysis_result.get('signal', 'NEUTRAL')
            symbol = analysis_result.get('symbol', '')
            confidence = analysis_result.get('confidence', 0)
            
            if signal == 'NEUTRAL' or confidence < 0.6:
                self.logger.info(f"⏸️ No hay señal clara para {symbol} (confianza: {confidence:.2%})")
                return {'success': False, 'reason': 'low_confidence'}
            
            # Determinar dirección
            direction = 'BUY' if signal == 'BUY' else 'SELL'
            
            # Calcular monto basado en riesgo
            risk_amount = self.calculate_position_size(confidence)
            
            # Determinar timeframe basado en tendencia
            timeframe = self._determine_timeframe(analysis_result)
            
            # Ejecutar trade
            result = self.execute_trade(
                direction=direction,
                symbol=symbol,
                amount=risk_amount,
                timeframe=timeframe
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error en trade con análisis: {e}")
            return {'success': False, 'error': str(e)}
    
    def calculate_position_size(self, confidence: float) -> float:
        """
        Calcula el tamaño de posición basado en balance y confianza
        
        Args:
            confidence: Nivel de confianza (0-1)
            
        Returns:
            Monto a invertir
        """
        # Riesgo base: 2% del balance
        base_risk = self.current_balance * 0.02
        
        # Ajustar por confianza
        adjusted_risk = base_risk * confidence
        
        # Mínimo $1, máximo 5% del balance
        min_amount = 1.0
        max_amount = self.current_balance * 0.05
        
        return max(min_amount, min(adjusted_risk, max_amount))
    
    def _determine_timeframe(self, analysis: Dict) -> str:
        """Determina el mejor timeframe según el análisis"""
        trend_strength = analysis.get('trend_strength', 0)
        
        if trend_strength > 0.7:
            return '15m'  # Tendencia fuerte, más tiempo
        elif trend_strength > 0.5:
            return '5m'   # Tendencia moderada
        else:
            return '1m'   # Tendencia débil, menos tiempo
    
    def get_statistics(self) -> Dict:
        """Retorna estadísticas del bot"""
        if self.stats['total_trades'] > 0:
            self.stats['win_rate'] = (self.stats['successful_trades'] / self.stats['total_trades']) * 100
        
        return {
            **self.stats,
            'current_balance': self.current_balance,
            'total_profit': self.current_balance - (self.stats.get('initial_balance', self.current_balance)),
            'platform': self.platform,
            'is_logged_in': self.is_logged_in,
            'trade_count': len(self.trade_history)
        }
    
    def close(self) -> None:
        """Cierra el driver y limpia recursos"""
        if self.driver:
            self.logger.info("🔚 Cerrando bot de trading...")
            self.driver.quit()
            self.driver = None
            self.is_logged_in = False


class ScalableWebTrader:
    """
    Sistema escalable para gestionar múltiples bots de trading en paralelo
    """
    
    def __init__(self, platforms: List[str] = None):
        """
        Inicializa el sistema escalable
        
        Args:
            platforms: Lista de plataformas a usar
        """
        self.platforms = platforms or ['binomo', 'iqoption', 'quotex']
        self.bots: Dict[str, WebTraderBot] = {}
        self.active = False
        
        self.logger = logging.getLogger('ScalableWebTrader')
        self.logger.setLevel(logging.INFO)
    
    def add_platform(self, platform: str, email: str, password: str, headless: bool = False) -> bool:
        """
        Agrega una plataforma al sistema
        
        Args:
            platform: Nombre de la plataforma
            email: Credenciales de login
            password: Contraseña
            headless: Modo sin interfaz gráfica
        """
        try:
            bot = WebTraderBot(platform=platform, headless=headless)
            
            if bot.login(email, password):
                self.bots[platform] = bot
                self.logger.info(f"✅ Plataforma agregada: {platform}")
                return True
            else:
                self.logger.error(f"❌ Fallo al agregar {platform}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error agregando plataforma {platform}: {e}")
            return False
    
    def execute_trade_all_platforms(self, analysis_result: Dict) -> Dict[str, Dict]:
        """
        Ejecuta un trade en todas las plataformas conectadas
        
        Args:
            analysis_result: Resultado del análisis técnico
            
        Returns:
            Diccionario con resultados por plataforma
        """
        results = {}
        
        for platform, bot in self.bots.items():
            try:
                result = bot.execute_trade_with_analysis(analysis_result)
                results[platform] = result
            except Exception as e:
                results[platform] = {'success': False, 'error': str(e)}
        
        return results
    
    def get_total_balance(self) -> float:
        """Retorna el balance total de todas las plataformas"""
        return sum(bot.current_balance for bot in self.bots.values())
    
    def get_combined_statistics(self) -> Dict:
        """Retorna estadísticas combinadas de todas las plataformas"""
        combined = {
            'total_trades': 0,
            'successful_trades': 0,
            'failed_trades': 0,
            'total_balance': 0.0,
            'platforms': {}
        }
        
        for platform, bot in self.bots.items():
            stats = bot.get_statistics()
            combined['total_trades'] += stats['total_trades']
            combined['successful_trades'] += stats['successful_trades']
            combined['failed_trades'] += stats['failed_trades']
            combined['total_balance'] += stats['current_balance']
            combined['platforms'][platform] = stats
        
        if combined['total_trades'] > 0:
            combined['overall_win_rate'] = (combined['successful_trades'] / combined['total_trades']) * 100
        
        return combined
    
    def close_all(self) -> None:
        """Cierra todos los bots"""
        for bot in self.bots.values():
            bot.close()
        self.bots.clear()


if __name__ == '__main__':
    # Ejemplo de uso
    print("🤖 Bot de Trading Automatizado con Selenium")
    print("=" * 60)
    
    # Crear bot para Binomo
    bot = WebTraderBot(platform='binomo', headless=False)
    
    # Login (usar credenciales reales)
    # success = bot.login('tu_email@ejemplo.com', 'tu_password')
    
    # if success:
    #     # Ejecutar trade basado en análisis
    #     analysis = {
    #         'symbol': 'EUR/USD',
    #         'signal': 'BUY',
    #         'confidence': 0.75,
    #         'trend_strength': 0.65
    #     }
    #     
    #     result = bot.execute_trade_with_analysis(analysis)
    #     print(f"Resultado: {result}")
    #     
    #     # Ver estadísticas
    #     stats = bot.get_statistics()
    #     print(f"Estadísticas: {stats}")
    
    # Cerrar bot
    # bot.close()
