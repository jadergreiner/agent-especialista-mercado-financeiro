"""
Métricas de Avaliação para Modelos de Predição WIN

Implementa métricas específicas para avaliação de modelos de predição
de séries temporais financeiras, incluindo métricas de risco e directional accuracy.

Autor: Sistema Especialista de Mercado Financeiro
Data: 2025
"""

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from typing import Dict, List, Tuple, Optional
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WinModelMetrics:
    """
    Métricas especializadas para avaliação de modelos de predição WIN.

    Inclui métricas tradicionais de ML e métricas específicas para
    avaliação de performance em mercados financeiros.
    """

    def __init__(self):
        """Inicializa o avaliador de métricas."""
        pass

    def calculate_all_metrics(self, y_true: np.ndarray, y_pred: np.ndarray,
                            y_train: Optional[np.ndarray] = None) -> Dict[str, float]:
        """
        Calcula todas as métricas de avaliação disponíveis.

        Args:
            y_true: Valores reais
            y_pred: Valores preditos
            y_train: Valores de treino (para cálculo de benchmark)

        Returns:
            Dicionário com todas as métricas
        """
        metrics = {}

        # Métricas básicas de erro
        metrics.update(self._calculate_error_metrics(y_true, y_pred))

        # Métricas de directional accuracy
        metrics.update(self._calculate_directional_metrics(y_true, y_pred))

        # Métricas de risco e volatilidade
        metrics.update(self._calculate_risk_metrics(y_true, y_pred))

        # Métricas de distribuição
        metrics.update(self._calculate_distribution_metrics(y_true, y_pred))

        # Benchmark comparison (se treino disponível)
        if y_train is not None:
            metrics.update(self._calculate_benchmark_metrics(y_true, y_pred, y_train))

        return metrics

    def _calculate_error_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """Calcula métricas básicas de erro."""
        # MAE (Mean Absolute Error)
        mae = mean_absolute_error(y_true, y_pred)

        # RMSE (Root Mean Square Error)
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))

        # MAPE (Mean Absolute Percentage Error)
        mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100

        # SMAPE (Symmetric Mean Absolute Percentage Error)
        smape = np.mean(2 * np.abs(y_true - y_pred) / (np.abs(y_true) + np.abs(y_pred))) * 100

        # R² Score
        r2 = r2_score(y_true, y_pred)

        # MSE (Mean Square Error)
        mse = mean_squared_error(y_true, y_pred)

        # RMSLE (Root Mean Square Logarithmic Error) - para valores positivos
        if np.all(y_true > 0) and np.all(y_pred > 0):
            rmsle = np.sqrt(np.mean((np.log(y_true + 1) - np.log(y_pred + 1))**2))
        else:
            rmsle = np.nan

        return {
            'mae': mae,
            'rmse': rmse,
            'mape': mape,
            'smape': smape,
            'r2': r2,
            'mse': mse,
            'rmsle': rmsle
        }

    def _calculate_directional_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """Calcula métricas de directional accuracy."""
        # Directional Accuracy (acertos na direção do movimento)
        actual_direction = np.sign(np.diff(y_true))
        pred_direction = np.sign(np.diff(y_pred))

        # Remover NaN que podem surgir se houver zeros
        valid_idx = ~(np.isnan(actual_direction) | np.isnan(pred_direction))
        actual_direction = actual_direction[valid_idx]
        pred_direction = pred_direction[valid_idx]

        if len(actual_direction) > 0:
            directional_accuracy = np.mean(actual_direction == pred_direction) * 100
        else:
            directional_accuracy = np.nan

        # Directional Accuracy for significant moves (> threshold)
        threshold = np.std(y_true) * 0.01  # 1% do desvio padrão
        significant_moves = np.abs(np.diff(y_true)) > threshold

        if np.any(significant_moves):
            # Ajustar índices corretamente
            actual_sig = actual_direction[significant_moves]
            pred_sig = pred_direction[significant_moves]
            directional_accuracy_sig = np.mean(actual_sig == pred_sig) * 100
        else:
            directional_accuracy_sig = np.nan

        # Hit Rate (proporção de predições corretas em magnitude)
        hits = np.abs(y_true - y_pred) <= np.std(y_true) * 0.5  # dentro de 0.5 desvio padrão
        hit_rate = np.mean(hits) * 100

        return {
            'directional_accuracy': directional_accuracy,
            'directional_accuracy_significant': directional_accuracy_sig,
            'hit_rate': hit_rate
        }

    def _calculate_risk_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """Calcula métricas de risco e volatilidade."""
        # Sharpe Ratio do modelo (retorno ajustado ao risco)
        returns_actual = np.diff(y_true) / y_true[:-1]
        returns_pred = np.diff(y_pred) / y_pred[:-1]

        if len(returns_actual) > 1 and np.std(returns_actual) > 0:
            sharpe_actual = np.mean(returns_actual) / np.std(returns_actual) * np.sqrt(252)  # anualizado
        else:
            sharpe_actual = np.nan

        if len(returns_pred) > 1 and np.std(returns_pred) > 0:
            sharpe_pred = np.mean(returns_pred) / np.std(returns_pred) * np.sqrt(252)
        else:
            sharpe_pred = np.nan

        # Sortino Ratio (foca apenas em downside risk)
        downside_returns_actual = returns_actual[returns_actual < 0]
        downside_returns_pred = returns_pred[returns_pred < 0]

        if len(downside_returns_actual) > 0 and np.std(downside_returns_actual) > 0:
            sortino_actual = np.mean(returns_actual) / np.std(downside_returns_actual) * np.sqrt(252)
        else:
            sortino_actual = np.nan

        if len(downside_returns_pred) > 0 and np.std(downside_returns_pred) > 0:
            sortino_pred = np.mean(returns_pred) / np.std(downside_returns_pred) * np.sqrt(252)
        else:
            sortino_pred = np.nan

        # Maximum Drawdown
        def calculate_max_drawdown(prices):
            """Calcula maximum drawdown de uma série de preços."""
            peak = prices[0]
            max_drawdown = 0

            for price in prices:
                if price > peak:
                    peak = price
                drawdown = (peak - price) / peak
                max_drawdown = max(max_drawdown, drawdown)

            return max_drawdown * 100

        max_drawdown_actual = calculate_max_drawdown(y_true)
        max_drawdown_pred = calculate_max_drawdown(y_pred)

        # Volatility (desvio padrão dos retornos)
        volatility_actual = np.std(returns_actual) * np.sqrt(252) * 100  # anualizada em %
        volatility_pred = np.std(returns_pred) * np.sqrt(252) * 100

        return {
            'sharpe_ratio_actual': sharpe_actual,
            'sharpe_ratio_pred': sharpe_pred,
            'sortino_ratio_actual': sortino_actual,
            'sortino_ratio_pred': sortino_pred,
            'max_drawdown_actual': max_drawdown_actual,
            'max_drawdown_pred': max_drawdown_pred,
            'volatility_actual': volatility_actual,
            'volatility_pred': volatility_pred
        }

    def _calculate_distribution_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """Calcula métricas de distribuição dos erros."""
        errors = y_true - y_pred

        # Estatísticas dos erros
        mean_error = np.mean(errors)
        std_error = np.std(errors)
        skewness_error = pd.Series(errors).skew()
        kurtosis_error = pd.Series(errors).kurtosis()

        # Percentis dos erros
        percentiles = np.percentile(errors, [5, 25, 50, 75, 95])

        # Mean Absolute Deviation
        mad = np.mean(np.abs(errors))

        # Theil's U statistic (comparação com naive forecast)
        naive_forecast = y_true[:-1]  # predição ingênua: valor anterior
        actual_next = y_true[1:]

        if len(naive_forecast) > 0:
            mae_naive = mean_absolute_error(actual_next, naive_forecast)
            theils_u = mean_absolute_error(y_true[1:], y_pred[1:]) / mae_naive if mae_naive > 0 else np.nan
        else:
            theils_u = np.nan

        return {
            'mean_error': mean_error,
            'std_error': std_error,
            'skewness_error': skewness_error,
            'kurtosis_error': kurtosis_error,
            'error_percentile_5': percentiles[0],
            'error_percentile_25': percentiles[1],
            'error_percentile_50': percentiles[2],
            'error_percentile_75': percentiles[3],
            'error_percentile_95': percentiles[4],
            'mad': mad,
            'theils_u': theils_u
        }

    def _calculate_benchmark_metrics(self, y_true: np.ndarray, y_pred: np.ndarray,
                                   y_train: np.ndarray) -> Dict[str, float]:
        """Calcula métricas de comparação com benchmark."""
        # Benchmark: média dos valores de treino
        benchmark_pred = np.full_like(y_true, np.mean(y_train))

        mae_benchmark = mean_absolute_error(y_true, benchmark_pred)
        mae_model = mean_absolute_error(y_true, y_pred)

        improvement_over_benchmark = (mae_benchmark - mae_model) / mae_benchmark * 100

        # Benchmark: último valor conhecido (naive forecast)
        naive_pred = np.roll(y_true, 1)  # shift para frente
        naive_pred[0] = y_train[-1]  # usar último valor de treino

        mae_naive = mean_absolute_error(y_true, naive_pred)
        improvement_over_naive = (mae_naive - mae_model) / mae_naive * 100

        return {
            'mae_benchmark': mae_benchmark,
            'mae_naive': mae_naive,
            'improvement_over_benchmark': improvement_over_benchmark,
            'improvement_over_naive': improvement_over_naive
        }

    def calculate_walk_forward_metrics(self, y_true: pd.Series, y_pred: pd.Series,
                                     window_size: int = 30) -> pd.DataFrame:
        """
        Calcula métricas em janelas rolantes (walk-forward analysis).

        Args:
            y_true: Valores reais (com índice temporal)
            y_pred: Valores preditos (com índice temporal)
            window_size: Tamanho da janela para cálculo rolante

        Returns:
            DataFrame com métricas por período
        """
        results = []

        for i in range(window_size, len(y_true)):
            window_true = y_true.iloc[i-window_size:i]
            window_pred = y_pred.iloc[i-window_size:i]

            metrics = self.calculate_all_metrics(window_true.values, window_pred.values)

            # Adicionar data do período
            metrics['date'] = y_true.index[i]
            metrics['window_start'] = y_true.index[i-window_size]
            metrics['window_end'] = y_true.index[i-1]

            results.append(metrics)

        return pd.DataFrame(results)

    def generate_metrics_report(self, metrics: Dict[str, float]) -> str:
        """
        Gera relatório formatado das métricas.

        Args:
            metrics: Dicionário com métricas

        Returns:
            String com relatório formatado
        """
        report = []
        report.append("=" * 60)
        report.append("RELATÓRIO DE MÉTRICAS - MODELO WIN")
        report.append("=" * 60)

        # Métricas de Erro
        report.append("\n📊 MÉTRICAS DE ERRO:")
        report.append("-" * 30)
        report.append(".2f")
        report.append(".2f")
        report.append(".2f")
        report.append(".2f")
        report.append(".4f")
        if not np.isnan(metrics.get('rmsle', np.nan)):
            report.append(".4f")

        # Métricas de Direção
        report.append("\n🎯 MÉTRICAS DE DIREÇÃO:")
        report.append("-" * 30)
        if not np.isnan(metrics.get('directional_accuracy', np.nan)):
            report.append(".2f")
        if not np.isnan(metrics.get('directional_accuracy_significant', np.nan)):
            report.append(".2f")
        report.append(".2f")

        # Métricas de Risco
        report.append("\n⚠️ MÉTRICAS DE RISCO:")
        report.append("-" * 30)
        if not np.isnan(metrics.get('sharpe_ratio_actual', np.nan)):
            report.append(".2f")
        if not np.isnan(metrics.get('sharpe_ratio_pred', np.nan)):
            report.append(".2f")
        if not np.isnan(metrics.get('sortino_ratio_actual', np.nan)):
            report.append(".2f")
        if not np.isnan(metrics.get('sortino_ratio_pred', np.nan)):
            report.append(".2f")
        report.append(".2f")
        report.append(".2f")
        report.append(".2f")
        report.append(".2f")

        # Benchmark Comparison
        if 'improvement_over_naive' in metrics:
            report.append("\n🏆 COMPARAÇÃO COM BENCHMARK:")
            report.append("-" * 30)
            report.append(".2f")
            report.append(".2f")
            report.append(".2f")
            report.append(".2f")

        report.append("\n" + "=" * 60)

        return "\n".join(report)

def main():
    """Função principal para teste das métricas."""
    import sys
    import os

    # Adicionar src ao path
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

    from models.baseline_models import WinBaselineModels
    from data.feature_engineering import WinFeatureEngineer
    from data.win_data_collector import WinDataCollector

    # Coletar dados e treinar modelo
    collector = WinDataCollector()
    data = collector.get_win_data()

    if not data.empty:
        engineer = WinFeatureEngineer()
        data_with_features = engineer.create_all_features(data)
        X, y = engineer.prepare_for_modeling(data_with_features)

        baseline = WinBaselineModels()
        results = baseline.train_baseline_models(X, y)

        # Calcular métricas detalhadas
        metrics_calculator = WinModelMetrics()

        print("\n=== ANÁLISE DETALHADA DE MÉTRICAS ===\n")

        for model_name, model_data in results.items():
            predictions = model_data['predictions']
            y_test = y.iloc[-len(predictions):]  # últimos valores correspondentes

            print(f"MODELO: {model_name.upper()}")
            print("-" * 50)

            detailed_metrics = metrics_calculator.calculate_all_metrics(
                y_test.values, predictions, y.iloc[:-len(predictions)].values
            )

            report = metrics_calculator.generate_metrics_report(detailed_metrics)
            print(report)
            print("\n")

        # Análise walk-forward (se houver dados suficientes)
        if len(y) > 60:
            print("=== ANÁLISE WALK-FORWARD ===")
            y_test_full = y.iloc[-len(results['random_forest']['predictions']):]
            y_pred_full = pd.Series(results['random_forest']['predictions'],
                                  index=y_test_full.index)

            walk_forward = metrics_calculator.calculate_walk_forward_metrics(
                y_test_full, y_pred_full, window_size=30
            )

            print(f"Análise em {len(walk_forward)} janelas rolantes")
            print(".2f")
            print(".2f")
            print(".2f")

if __name__ == "__main__":
    main()