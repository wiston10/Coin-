"""
Tests básicos sin red: indicadores, estrategia y configuración.
Ejecutar:  python3 -m unittest discover -s tests -v
"""
import os
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.indicators.technical_indicators import TechnicalIndicators, calculate_adaptive_indicators
from src.strategies.bounce_strategy import analyze_bounce_opportunity
from src.env_loader import env_flag


def make_df(n=300, seed=0):
    rng = np.random.default_rng(seed)
    p = 100 + np.cumsum(rng.standard_normal(n))
    close = p + rng.standard_normal(n) * 0.3
    return pd.DataFrame({
        'Open': p,
        'High': np.maximum(p, close) + np.abs(rng.standard_normal(n)),
        'Low': np.minimum(p, close) - np.abs(rng.standard_normal(n)),
        'Close': close,
        'Volume': rng.uniform(1e3, 1e4, n),
    })


class TestIndicators(unittest.TestCase):
    def test_rsi_in_range(self):
        rsi = TechnicalIndicators.calculate_rsi(make_df()).dropna()
        self.assertTrue(((rsi >= 0) & (rsi <= 100)).all())

    def test_rsi_flat_market_is_neutral(self):
        df = make_df()
        df[['Open', 'High', 'Low', 'Close']] = 100.0
        self.assertEqual(TechnicalIndicators.calculate_rsi(df).iloc[-1], 50.0)

    def test_rsi_only_up_is_100(self):
        df = make_df()
        df['Close'] = np.arange(len(df)) + 100.0
        self.assertEqual(TechnicalIndicators.calculate_rsi(df).iloc[-1], 100.0)

    def test_atr_positive(self):
        atr = TechnicalIndicators.calculate_atr(make_df()).dropna()
        self.assertTrue((atr > 0).all())


class TestStrategy(unittest.TestCase):
    def test_bounce_returns_valid_signal(self):
        for interval in ['1m', '5m', '15m', '1h', '1d']:
            df = calculate_adaptive_indicators(make_df(), interval)
            r = analyze_bounce_opportunity(df, interval=interval)
            self.assertIn(r['signal'], ('BUY', 'SELL', 'HOLD'))
            self.assertGreaterEqual(r['confidence'], 0)
            self.assertLessEqual(r['confidence'], 100)
            if r['signal'] == 'BUY':
                self.assertLess(r['stop_loss'], r['entry_price'])
                self.assertGreater(r['take_profit'], r['entry_price'])
            if r['signal'] == 'SELL':
                self.assertGreater(r['stop_loss'], r['entry_price'])
                self.assertLess(r['take_profit'], r['entry_price'])


class TestSafety(unittest.TestCase):
    def test_no_hardcoded_telegram_token(self):
        text = (ROOT / 'src' / 'webhooks' / 'webhook_config.py').read_text()
        self.assertNotRegex(text, r"\d{8,10}:[A-Za-z0-9_-]{30,}")

    def test_env_flag(self):
        os.environ['X_TEST_FLAG'] = 'true'
        self.assertTrue(env_flag('X_TEST_FLAG'))
        os.environ['X_TEST_FLAG'] = 'no'
        self.assertFalse(env_flag('X_TEST_FLAG'))
        self.assertFalse(env_flag('X_TEST_UNSET_FLAG'))

    def test_simulated_binomo_data_disabled_by_default(self):
        os.environ.pop('ALLOW_SIMULATED_DATA', None)
        from src.data_sources.binomo_scraper import BinomoScraper
        scraper = BinomoScraper()
        scraper.get_candles_api = lambda *a, **k: None  # simula que la API falla
        self.assertIsNone(scraper.get_live_data('BTC-USD', '5m', 50))

    def test_simulation_interval_parsing(self):
        from src.data_sources.binomo_scraper import BinomoScraper
        df = BinomoScraper().get_candles_websocket_simulation('BTC-USD', '1h', 3)
        delta = df['timestamp'].iloc[1] - df['timestamp'].iloc[0]
        self.assertEqual(delta, pd.Timedelta(hours=1))


if __name__ == '__main__':
    unittest.main()
