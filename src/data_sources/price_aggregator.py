"""
Agregador de datos multi-source para obtener precio consenso
Combina múltiples fuentes para mejorar precisión
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import time

try:
    from config.broker_apis import SOURCE_PRIORITY, SOURCE_WEIGHTS, AGGREGATION_METHOD, get_enabled_sources
except ImportError:
    SOURCE_PRIORITY = {'stocks': ['yfinance'], 'forex': ['yfinance'], 'indices': ['yfinance'], 'crypto': ['exchanges']}
    SOURCE_WEIGHTS = {'yfinance': 1.0, 'exchanges': 1.0}
    AGGREGATION_METHOD = 'weighted_average'
    get_enabled_sources = lambda: ['yfinance']


class PriceAggregator:
    """
    Agregador inteligente de precios de múltiples fuentes
    Calcula precio consenso, detecta outliers, y provee estadísticas
    """
    
    def __init__(self):
        self.price_history = {}  # Historial de precios por símbolo
        self.source_reliability = {}  # Score de confiabilidad por fuente
        
    def aggregate_prices(self, prices: Dict[str, float], method: str = None) -> Tuple[float, Dict]:
        """
        Agrega precios de múltiples fuentes
        
        Args:
            prices: Dict con {source: price}
            method: 'simple_average', 'weighted_average', 'median'
            
        Returns:
            (precio_consenso, metadatos)
        """
        if not prices:
            return None, {'error': 'No prices available'}
        
        method = method or AGGREGATION_METHOD
        
        # Filtrar valores None o inválidos
        valid_prices = {k: v for k, v in prices.items() if v is not None and v > 0}
        
        if not valid_prices:
            return None, {'error': 'No valid prices'}
        
        # Si solo hay una fuente, retornarla
        if len(valid_prices) == 1:
            source, price = list(valid_prices.items())[0]
            return price, {
                'sources_used': 1,
                'method': 'single',
                'primary_source': source,
                'std_dev': 0.0,
                'spread_pct': 0.0
            }
        
        # Detectar y remover outliers
        cleaned_prices, outliers = self._remove_outliers(valid_prices)
        
        # Calcular precio consenso
        if method == 'simple_average':
            consensus_price = np.mean(list(cleaned_prices.values()))
            
        elif method == 'weighted_average':
            total_weight = 0
            weighted_sum = 0
            for source, price in cleaned_prices.items():
                weight = SOURCE_WEIGHTS.get(source, 0.5)
                weighted_sum += price * weight
                total_weight += weight
            consensus_price = weighted_sum / total_weight if total_weight > 0 else np.mean(list(cleaned_prices.values()))
            
        elif method == 'median':
            consensus_price = np.median(list(cleaned_prices.values()))
            
        else:
            consensus_price = np.mean(list(cleaned_prices.values()))
        
        # Calcular estadísticas
        prices_array = np.array(list(cleaned_prices.values()))
        std_dev = np.std(prices_array)
        min_price = np.min(prices_array)
        max_price = np.max(prices_array)
        spread_pct = ((max_price - min_price) / consensus_price * 100) if consensus_price > 0 else 0
        
        metadata = {
            'sources_used': len(cleaned_prices),
            'method': method,
            'std_dev': float(std_dev),
            'min_price': float(min_price),
            'max_price': float(max_price),
            'spread_pct': float(spread_pct),
            'outliers_removed': len(outliers),
            'outliers': outliers,
            'individual_prices': cleaned_prices,
            'timestamp': datetime.now().isoformat()
        }
        
        return float(consensus_price), metadata
    
    def _remove_outliers(self, prices: Dict[str, float], z_threshold: float = 2.5) -> Tuple[Dict, List]:
        """
        Remueve outliers usando z-score
        
        Args:
            prices: Dict con {source: price}
            z_threshold: Umbral de z-score para considerar outlier
            
        Returns:
            (precios_limpios, lista_de_outliers)
        """
        if len(prices) < 3:
            return prices, []
        
        prices_array = np.array(list(prices.values()))
        sources_array = np.array(list(prices.keys()))
        
        mean = np.mean(prices_array)
        std = np.std(prices_array)
        
        if std == 0:
            return prices, []
        
        z_scores = np.abs((prices_array - mean) / std)
        
        # Identificar outliers
        outliers = []
        cleaned_prices = {}
        
        for i, (source, price) in enumerate(prices.items()):
            if z_scores[i] > z_threshold:
                outliers.append({
                    'source': source,
                    'price': price,
                    'z_score': float(z_scores[i])
                })
            else:
                cleaned_prices[source] = price
        
        # Si se removieron demasiados, mantener al menos 2 fuentes
        if len(cleaned_prices) < 2 and len(prices) >= 2:
            # Mantener las dos fuentes más cercanas a la mediana
            median = np.median(prices_array)
            distances = {source: abs(price - median) for source, price in prices.items()}
            sorted_sources = sorted(distances.items(), key=lambda x: x[1])
            cleaned_prices = {source: prices[source] for source, _ in sorted_sources[:2]}
            outliers = [{'source': source, 'price': prices[source], 'z_score': 0} for source, _ in sorted_sources[2:]]
        
        return cleaned_prices, outliers
    
    def calculate_confidence_score(self, metadata: Dict) -> float:
        """
        Calcula score de confianza basado en metadata
        
        Returns:
            Score entre 0.0 y 1.0
        """
        if not metadata or 'sources_used' not in metadata:
            return 0.0
        
        score = 0.0
        
        # Más fuentes = mayor confianza (hasta 0.4)
        sources_score = min(metadata['sources_used'] / 5.0, 1.0) * 0.4
        score += sources_score
        
        # Menor spread = mayor confianza (hasta 0.3)
        spread_pct = metadata.get('spread_pct', 100)
        spread_score = max(0, 1.0 - (spread_pct / 5.0)) * 0.3  # spread > 5% reduce confianza
        score += spread_score
        
        # Menor desviación estándar = mayor confianza (hasta 0.2)
        std_dev = metadata.get('std_dev', float('inf'))
        consensus_price = metadata.get('min_price', 0) + (metadata.get('max_price', 0) - metadata.get('min_price', 0)) / 2
        if consensus_price > 0:
            std_pct = (std_dev / consensus_price) * 100
            std_score = max(0, 1.0 - (std_pct / 2.0)) * 0.2  # std > 2% reduce confianza
            score += std_score
        
        # Sin outliers = mayor confianza (hasta 0.1)
        outliers_removed = metadata.get('outliers_removed', 0)
        outliers_score = max(0, 1.0 - (outliers_removed / 3.0)) * 0.1
        score += outliers_score
        
        return min(score, 1.0)
    
    def get_price_quality_rating(self, confidence: float) -> str:
        """
        Convierte score de confianza a rating
        
        Returns:
            'Excellent', 'Good', 'Fair', 'Poor'
        """
        if confidence >= 0.9:
            return 'Excellent'
        elif confidence >= 0.75:
            return 'Good'
        elif confidence >= 0.6:
            return 'Fair'
        else:
            return 'Poor'
    
    def save_price_to_history(self, symbol: str, price: float, sources: List[str], metadata: Dict):
        """Guarda precio en historial para análisis"""
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        
        self.price_history[symbol].append({
            'price': price,
            'sources': sources,
            'metadata': metadata,
            'timestamp': time.time()
        })
        
        # Mantener solo últimos 100 registros
        if len(self.price_history[symbol]) > 100:
            self.price_history[symbol] = self.price_history[symbol][-100:]
    
    def get_price_trend(self, symbol: str, window: int = 10) -> Optional[str]:
        """
        Analiza tendencia de precio reciente
        
        Returns:
            'rising', 'falling', 'stable', o None
        """
        if symbol not in self.price_history or len(self.price_history[symbol]) < window:
            return None
        
        recent_prices = [p['price'] for p in self.price_history[symbol][-window:]]
        
        # Calcular pendiente usando regresión lineal simple
        x = np.arange(len(recent_prices))
        y = np.array(recent_prices)
        
        slope = np.polyfit(x, y, 1)[0]
        avg_price = np.mean(y)
        
        # Calcular cambio porcentual
        slope_pct = (slope / avg_price) * 100 if avg_price > 0 else 0
        
        if slope_pct > 0.1:
            return 'rising'
        elif slope_pct < -0.1:
            return 'falling'
        else:
            return 'stable'
    
    def compare_sources_accuracy(self, symbol: str) -> Dict[str, float]:
        """
        Compara accuracy de diferentes fuentes contra el consenso
        
        Returns:
            Dict con {source: accuracy_score}
        """
        if symbol not in self.price_history or len(self.price_history[symbol]) < 5:
            return {}
        
        source_errors = {}
        
        for record in self.price_history[symbol]:
            consensus = record['price']
            individual = record['metadata'].get('individual_prices', {})
            
            for source, price in individual.items():
                if source not in source_errors:
                    source_errors[source] = []
                
                # Error absoluto porcentual
                error_pct = abs((price - consensus) / consensus * 100) if consensus > 0 else 0
                source_errors[source].append(error_pct)
        
        # Calcular accuracy (1 - error_promedio)
        accuracy_scores = {}
        for source, errors in source_errors.items():
            avg_error = np.mean(errors)
            accuracy = max(0, 100 - avg_error)  # 0-100 scale
            accuracy_scores[source] = round(accuracy, 2)
        
        return accuracy_scores


# Instancia global
price_aggregator = PriceAggregator()


def get_aggregated_price(prices: Dict[str, float], method: str = None) -> Tuple[Optional[float], Dict]:
    """
    Función de conveniencia para agregar precios
    
    Args:
        prices: Dict con {source: price}
        method: 'simple_average', 'weighted_average', 'median'
        
    Returns:
        (precio_consenso, metadata)
    """
    return price_aggregator.aggregate_prices(prices, method)
