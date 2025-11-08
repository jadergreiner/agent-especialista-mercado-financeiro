from src.data.win_data_collector import WinDataCollector
from src.data.feature_engineering import WinFeatureEngineer
from src.evaluation.metrics import WinModelMetrics
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WinXGBoostModel:
    """Modelo XGBoost simplificado para WIN."""

    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = None
        self.is_trained = False

        self.xgb_params = {
            'objective': 'reg:squarederror',
            'eval_metric': 'rmse',
            'max_depth': 6,
            'learning_rate': 0.1,
            'n_estimators': 500,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'random_state': random_state,
            'early_stopping_rounds': 50
        }

    def train_xgboost(self, X: pd.DataFrame, y: pd.Series, test_size: float = 0.2):
        """Treina modelo XGBoost."""
        logger.info("Treinando XGBoost...")

        # Salvar nomes das features
        self.feature_columns = X.columns.tolist()

        # Divisão temporal
        split_idx = int(len(X) * (1 - test_size))
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]

        logger.info(f"Treino: {len(X_train)} amostras, Teste: {len(X_test)} amostras")

        # Escalar features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Treinar XGBoost
        model = xgb.XGBRegressor(**self.xgb_params)
        model.fit(
            X_train_scaled, y_train,
            eval_set=[(X_test_scaled, y_test)],
            verbose=False
        )

        self.model = model
        self.is_trained = True

        # Avaliar
        predictions = model.predict(X_test_scaled)
        evaluator = WinModelMetrics()
        metrics = evaluator.calculate_all_metrics(y_test, predictions)

        return {
            'model': model,
            'metrics': metrics,
            'predictions': predictions,
            'X_test': X_test_scaled,
            'y_test': y_test
        }

def main():
    print('=== TREINAMENTO XGBoost COM DADOS DE 30 ANOS ===')

    # Coletar e processar dados
    collector = WinDataCollector()
    data = collector.get_win_data()
    engineer = WinFeatureEngineer()
    data_with_features = engineer.create_all_features(data)

    print('Shape dos dados:', data_with_features.shape)
    print('Período:', data_with_features.index.min().strftime('%Y-%m-%d'), 'até', data_with_features.index.max().strftime('%Y-%m-%d'))

    # Preparar dados para ML
    feature_cols = engineer.feature_columns
    target_col = 'Close'

    # Remover NaN e preparar X, y
    data_clean = data_with_features.dropna()
    X = data_clean[feature_cols]
    y = data_clean[target_col]

    print('Dados de treinamento:', X.shape, 'Target shape:', y.shape)

    # Treinar XGBoost
    xgb_model = WinXGBoostModel()
    results = xgb_model.train_xgboost(X, y)

    print('\n' + '='*50)
    print('RESULTADOS XGBoost')
    print('='*50)

    metrics = results['metrics']
    print(f'MAPE: {metrics["mape"]:.2f}%')
    print(f'RMSE: {metrics["rmse"]:.2f}')
    print(f'R²: {metrics["r2"]:.4f}')
    print(f'Directional Accuracy: {metrics["directional_accuracy"]:.2f}%')
    print(f'Sharpe Ratio (Pred): {metrics.get("sharpe_ratio_pred", "N/A"):.3f}')
    print(f'Max Drawdown (Pred): {metrics.get("max_drawdown_pred", "N/A"):.2f}%')

    print('\n✅ XGBoost treinado com dados de 30 anos!')

if __name__ == "__main__":
    main()