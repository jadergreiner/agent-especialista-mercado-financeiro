from src.data.win_data_collector import WinDataCollector
from src.data.feature_engineering import WinFeatureEngineer
from src.models.advanced_models import WinAdvancedModels
from src.evaluation.metrics import WinModelMetrics
import pandas as pd
import numpy as np

def main():
    print('=== TREINAMENTO DE MODELOS AVANÇADOS COM DADOS DE 30 ANOS ===')

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

    # Treinar modelos avançados
    advanced_models = WinAdvancedModels()
    results = advanced_models.train_advanced_models(X, y)

    # Preparar scaler para avaliação
    X_scaled = advanced_models.scaler.transform(X)

    # Avaliar resultados
    evaluator = WinModelMetrics()

    print('\n' + '='*60)
    print('RESULTADOS DOS MODELOS AVANÇADOS')
    print('='*60)

    for model_name, model_info in results.items():
        if 'error' in model_info:
            print(f'\n❌ {model_name.upper()}: Erro - {model_info["error"]}')
            continue

        model = model_info['model']

        # Fazer predições
        if model_name == 'lstm':
            # Para LSTM, ajustar dados
            seq_length = advanced_models.lstm_config['sequence_length']
            X_seq = advanced_models._create_sequences(X_scaled, seq_length)
            predictions = model.predict(X_seq, verbose=0).flatten()
            y_eval = y[seq_length:].values
        else:
            predictions = model.predict(X_scaled)
            y_eval = y.values

        # Calcular métricas
        metrics = evaluator.calculate_all_metrics(y_eval, predictions)

        print(f'\n🚀 {model_name.upper()}')
        print(f'   MAPE: {metrics["mape"]:.2f}%')
        print(f'   RMSE: {metrics["rmse"]:.2f}')
        print(f'   R²: {metrics["r2"]:.4f}')
        print(f'   Directional Accuracy: {metrics["directional_accuracy"]:.2f}%')
        print(f'   Sharpe Ratio (Pred): {metrics.get("sharpe_ratio_pred", "N/A"):.3f}')
        print(f'   Max Drawdown (Pred): {metrics.get("max_drawdown_pred", "N/A"):.2f}%')

    print('\n✅ Modelos avançados treinados com dados de 30 anos!')

if __name__ == "__main__":
    main()