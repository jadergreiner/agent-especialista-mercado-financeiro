"""
Engenharia de Features para Modelo de Predição WIN

Este módulo implementa todas as features técnicas necessárias para
o modelo de machine learning do WIN, incluindo indicadores técnicos,
features temporais e transformações de dados.

Autor: Sistema Especialista de Mercado Financeiro
Data: 2025
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging
from datetime import datetime

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WinFeatureEngineer:
    """
    Engenharia de features para dados do WIN.

    Implementa indicadores técnicos, features temporais e transformações
    necessárias para o modelo de predição.
    """

    def __init__(self):
        """Inicializa o engenheiro de features."""
        self.feature_columns = []

    def create_all_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Cria todas as features necessárias para o modelo.

        Args:
            data: DataFrame com dados OHLCV

        Returns:
            DataFrame com todas as features criadas
        """
        logger.info("Iniciando engenharia de features...")

        # Fazer cópia para não modificar dados originais
        df = data.copy()

        # Features básicas de preço
        df = self._create_price_features(df)

        # Features de volatilidade
        df = self._create_volatility_features(df)

        # Features de volume
        df = self._create_volume_features(df)

        # Features temporais
        df = self._create_temporal_features(df)

        # Indicadores técnicos
        df = self._create_technical_indicators(df)

        # Features de momentum
        df = self._create_momentum_features(df)

        # Limpar dados finais
        df = self._clean_features(df)

        # Atualizar lista de features
        self.feature_columns = [col for col in df.columns if col not in ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']]

        logger.info(f"Features criadas: {len(self.feature_columns)}")
        logger.info(f"Shape final: {df.shape}")

        return df

    def _create_price_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Cria features básicas baseadas em preços."""
        logger.info("Criando features de preço...")

        # Retornos diários
        df['returns_daily'] = df['Close'].pct_change()

        # Range diário
        df['range_daily'] = (df['High'] - df['Low']) / df['Close']

        # Gap de abertura
        df['gap_open'] = (df['Open'] - df['Close'].shift(1)) / df['Close'].shift(1)

        # Body do candle
        df['body_size'] = abs(df['Close'] - df['Open']) / df['Close']

        # Upper/Lower shadow
        df['upper_shadow'] = (df['High'] - np.maximum(df['Open'], df['Close'])) / df['Close']
        df['lower_shadow'] = (np.minimum(df['Open'], df['Close']) - df['Low']) / df['Close']

        return df

    def _create_volatility_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Cria features de volatilidade."""
        logger.info("Criando features de volatilidade...")

        # Volatilidade histórica (desvio padrão dos retornos)
        for period in [7, 14, 30, 60]:
            df[f'volatility_{period}d'] = df['returns_daily'].rolling(window=period).std()

        # Average True Range (ATR)
        df['tr'] = np.maximum(
            df['High'] - df['Low'],
            np.maximum(
                abs(df['High'] - df['Close'].shift(1)),
                abs(df['Low'] - df['Close'].shift(1))
            )
        )
        df['atr_14'] = df['tr'].rolling(window=14).mean()

        # Bollinger Bands
        df['sma_20'] = df['Close'].rolling(window=20).mean()
        df['std_20'] = df['Close'].rolling(window=20).std()
        df['bb_upper'] = df['sma_20'] + (df['std_20'] * 2)
        df['bb_lower'] = df['sma_20'] - (df['std_20'] * 2)
        df['bb_position'] = (df['Close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])

        return df

    def _create_volume_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Cria features baseadas em volume."""
        logger.info("Criando features de volume...")

        # Volume relativo
        df['volume_sma_20'] = df['Volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['Volume'] / df['volume_sma_20']

        # Volume Force
        df['volume_force'] = df['returns_daily'] * df['Volume']

        # On Balance Volume (OBV)
        df['obv'] = np.where(df['Close'] > df['Close'].shift(1), df['Volume'],
                           np.where(df['Close'] < df['Close'].shift(1), -df['Volume'], 0))
        df['obv'] = df['obv'].cumsum()

        return df

    def _create_temporal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Cria features temporais."""
        logger.info("Criando features temporais...")

        # Features de data
        df['day_of_week'] = df.index.dayofweek  # 0=Monday, 6=Sunday
        df['month'] = df.index.month
        df['quarter'] = df.index.quarter
        df['day_of_month'] = df.index.day
        df['week_of_year'] = df.index.isocalendar().week

        # Features sazonais
        df['is_month_start'] = df.index.is_month_start.astype(int)
        df['is_month_end'] = df.index.is_month_end.astype(int)
        df['is_quarter_start'] = df.index.is_quarter_start.astype(int)
        df['is_quarter_end'] = df.index.is_quarter_end.astype(int)

        return df

    def _create_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Cria indicadores técnicos."""
        logger.info("Criando indicadores técnicos...")

        # Médias móveis
        for period in [5, 10, 20, 50, 100]:
            df[f'sma_{period}'] = df['Close'].rolling(window=period).mean()
            df[f'ema_{period}'] = df['Close'].ewm(span=period).mean()

        # RSI (Relative Strength Index)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi_14'] = 100 - (100 / (1 + rs))

        # MACD (Moving Average Convergence Divergence)
        ema_12 = df['Close'].ewm(span=12).mean()
        ema_26 = df['Close'].ewm(span=26).mean()
        df['macd'] = ema_12 - ema_26
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']

        # Stochastic Oscillator
        low_14 = df['Low'].rolling(window=14).min()
        high_14 = df['High'].rolling(window=14).max()
        df['stoch_k'] = 100 * ((df['Close'] - low_14) / (high_14 - low_14))
        df['stoch_d'] = df['stoch_k'].rolling(window=3).mean()

        return df

    def _create_momentum_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Cria features de momentum."""
        logger.info("Criando features de momentum...")

        # Momentum
        for period in [5, 10, 20]:
            df[f'momentum_{period}'] = (df['Close'] - df['Close'].shift(period)) / df['Close'].shift(period)

        # Rate of Change (ROC)
        for period in [10, 20, 30]:
            df[f'roc_{period}'] = (df['Close'] - df['Close'].shift(period)) / df['Close'].shift(period) * 100

        # Williams %R
        highest_high = df['High'].rolling(window=14).max()
        lowest_low = df['Low'].rolling(window=14).min()
        df['williams_r'] = -100 * ((highest_high - df['Close']) / (highest_high - lowest_low))

        return df

    def _clean_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Limpa e finaliza as features."""
        logger.info("Limpando features...")

        # Remover NaN resultantes dos cálculos
        df = df.dropna()

        # Remover features com alta correlação (para evitar multicolinearidade)
        # Manter apenas uma versão de cada tipo de indicador

        # Arredondar valores numéricos para evitar problemas de precisão
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        df[numeric_columns] = df[numeric_columns].round(6)

        # Validar que não há valores infinitos
        df = df.replace([np.inf, -np.inf], np.nan).dropna()

        return df

    def get_feature_importance_template(self) -> Dict[str, List[str]]:
        """
        Retorna template de importância de features por categoria.

        Returns:
            Dicionário com categorias e suas features
        """
        return {
            'price_features': ['returns_daily', 'range_daily', 'gap_open', 'body_size', 'upper_shadow', 'lower_shadow'],
            'volatility_features': ['volatility_7d', 'volatility_14d', 'volatility_30d', 'volatility_60d', 'atr_14', 'bb_position'],
            'volume_features': ['volume_ratio', 'volume_force', 'obv'],
            'temporal_features': ['day_of_week', 'month', 'quarter', 'is_month_start', 'is_month_end'],
            'technical_indicators': ['rsi_14', 'macd', 'macd_signal', 'macd_histogram', 'stoch_k', 'stoch_d', 'williams_r'],
            'momentum_features': ['momentum_5', 'momentum_10', 'momentum_20', 'roc_10', 'roc_20', 'roc_30'],
            'moving_averages': ['sma_5', 'sma_10', 'sma_20', 'sma_50', 'ema_5', 'ema_10', 'ema_20', 'ema_50']
        }

    def prepare_for_modeling(self, df: pd.DataFrame,
                           target_column: str = 'Close',
                           prediction_horizon: int = 1) -> tuple:
        """
        Prepara dados para modelagem, criando target e features.

        Args:
            df: DataFrame com features
            target_column: Coluna target
            prediction_horizon: Horizonte de predição (dias à frente)

        Returns:
            Tuple (X, y) para modelagem
        """
        # Criar target (preço de fechamento do próximo dia)
        df['target'] = df[target_column].shift(-prediction_horizon)

        # Remover linhas com target NaN
        df = df.dropna()

        # Separar features e target
        feature_cols = self.feature_columns
        X = df[feature_cols]
        y = df['target']

        logger.info(f"Dados preparados: {X.shape[0]} amostras, {X.shape[1]} features")

        return X, y

def main():
    """Função principal para teste do feature engineering."""
    from win_data_collector import WinDataCollector

    # Coletar dados
    collector = WinDataCollector()
    data = collector.get_win_data()

    if not data.empty:
        # Criar features
        engineer = WinFeatureEngineer()
        data_with_features = engineer.create_all_features(data)

        print(f"Features criadas: {len(engineer.feature_columns)}")
        print(f"Shape dos dados: {data_with_features.shape}")
        print(f"Features: {engineer.feature_columns[:10]}...")  # Mostrar primeiras 10

        # Preparar para modelagem
        X, y = engineer.prepare_for_modeling(data_with_features)

        # Salvar dados processados
        output_file = "data/win_features_data.csv"
        data_with_features.to_csv(output_file)
        print(f"Dados com features salvos em: {output_file}")

        # Salvar features separadamente
        features_file = "data/win_features_only.csv"
        X.to_csv(features_file)
        print(f"Features salvas em: {features_file}")

    else:
        print("Erro: Não foi possível coletar dados")

if __name__ == "__main__":
    main()