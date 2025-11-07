from src.data.win_data_collector import WinDataCollector
from src.data.feature_engineering import WinFeatureEngineer
from src.models.baseline_models import WinBaselineModels
from src.evaluation.metrics import WinModelMetrics
import pandas as pd
import numpy as np

def main():
    # Coletar e processar dados
    collector = WinDataCollector()
    data = collector.get_win_data()
    engineer = WinFeatureEngineer()
    data_with_features = engineer.create_all_features(data)

    print('=== TREINAMENTO COM DADOS DE 30 ANOS ===')
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

    # Treinar modelos baseline
    models = WinBaselineModels()
    results = models.train_baseline_models(X, y)

    # Preparar scaler para avaliação (usar o mesmo scaler do treinamento)
    X_scaled = models.scaler.transform(X)

    # Avaliar resultados
    evaluator = WinModelMetrics()
    for model_name, model_info in results.items():
        model = model_info['model']
        predictions = model.predict(X_scaled)  # Usar dados escalados!
        metrics = evaluator.calculate_all_metrics(y, predictions)

        print(f'\n=== {model_name.upper()} ===')
        print(f'MAPE: {metrics["mape"]:.2f}%')
        print(f'RMSE: {metrics["rmse"]:.2f}')
        print(f'Directional Accuracy: {metrics["directional_accuracy"]:.2f}%')
        print(f'Sharpe Ratio (Pred): {metrics.get("sharpe_ratio_pred", "N/A"):.3f}')
        print(f'Max Drawdown (Pred): {metrics.get("max_drawdown_pred", "N/A"):.2f}%')

    print('\n✅ Modelos treinados com dados de 30 anos!')

if __name__ == "__main__":
    main()