"""
Otimização de Thresholds para Estratégia WIN

Testa diferentes thresholds de sinal para encontrar
o melhor equilíbrio entre frequência e qualidade.

Autor: Sistema Especialista de Mercado Financeiro
Data: 2025
"""

from src.data.win_data_collector import WinDataCollector
from src.data.feature_engineering import WinFeatureEngineer
from src.models.baseline_models import WinBaselineModels
from src.backtesting.backtester import WinBacktester, create_signals_from_predictions, benchmark_buy_and_hold
import pandas as pd
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def otimizar_threshold_sinais():
    """Testa diferentes thresholds de sinal para otimização."""

    print('🎯 OTIMIZAÇÃO DE THRESHOLDS DE SINAL')
    print('='*50)

    # Preparar dados
    collector = WinDataCollector()
    data = collector.get_win_data()
    engineer = WinFeatureEngineer()
    data_with_features = engineer.create_all_features(data)

    # Split treino/teste
    split_idx = int(len(data_with_features) * 0.7)
    train_data = data_with_features[:split_idx]
    test_data = data_with_features[split_idx:]

    # Treinar modelo
    models = WinBaselineModels()
    results = models.train_baseline_models(train_data[engineer.feature_columns], train_data['Close'])

    # Gerar predições
    X_test = test_data[engineer.feature_columns]
    X_test_scaled = models.scaler.transform(X_test)
    predictions = results['xgboost']['model'].predict(X_test_scaled)

    # Testar diferentes thresholds
    thresholds = [0.001, 0.005, 0.01, 0.015, 0.02, 0.025, 0.03]  # 0.1% a 3.0%

    resultados = []

    print('Testando thresholds...')
    print('Threshold | Trades | Win Rate | Retorno | Sharpe | Drawdown')
    print('-'*65)

    for threshold in thresholds:
        # Criar sinais
        signals = create_signals_from_predictions(predictions, threshold=threshold)

        # Executar backtest
        backtester = WinBacktester(
            initial_capital=100000.0,
            commission_per_trade=5.0,
            slippage_bps=5.0,
            max_position_size=3
        )

        strategy_metrics = backtester.run_backtest(test_data, signals)

        # Calcular benchmark
        benchmark_metrics = benchmark_buy_and_hold(test_data, initial_capital=100000.0)

        # Resultados
        resultado = {
            'threshold': threshold,
            'threshold_pct': threshold * 100,
            'trades': strategy_metrics['total_trades'],
            'win_rate': strategy_metrics['win_rate_pct'],
            'return_pct': strategy_metrics['total_return_pct'],
            'sharpe': strategy_metrics['sharpe_ratio'],
            'drawdown_pct': strategy_metrics['max_drawdown_pct'],
            'benchmark_return': benchmark_metrics['total_return_pct'],
            'excess_return': strategy_metrics['total_return_pct'] - benchmark_metrics['total_return_pct'],
            'compras': len(signals[signals > 0]),
            'vendas': len(signals[signals < 0]),
            'hold': len(signals[signals == 0])
        }

        resultados.append(resultado)

        print(f"{threshold*100:8.1f}% | {resultado['trades']:6d} | {resultado['win_rate']:8.1f}% | {resultado['return_pct']:7.2f}% | {resultado['sharpe']:6.3f} | {resultado['drawdown_pct']:5.1f}%")

    # Análise dos resultados
    print('\n' + '='*50)
    print('📊 ANÁLISE DOS RESULTADOS')
    print('='*50)

    df_resultados = pd.DataFrame(resultados)

    # Melhor threshold por métrica
    melhores = {}

    # Melhor retorno absoluto
    best_return = df_resultados.loc[df_resultados['return_pct'].idxmax()]
    melhores['retorno_absoluto'] = best_return

    # Melhor Sharpe Ratio
    best_sharpe = df_resultados.loc[df_resultados['sharpe'].idxmax()]
    melhores['sharpe_ratio'] = best_sharpe

    # Melhor excesso de retorno vs benchmark
    best_excess = df_resultados.loc[df_resultados['excess_return'].idxmax()]
    melhores['excesso_retorno'] = best_excess

    # Menor drawdown
    best_drawdown = df_resultados.loc[df_resultados['drawdown_pct'].idxmin()]
    melhores['menor_drawdown'] = best_drawdown

    print('🏆 MELHORES THRESHOLDS POR MÉTRICA:')
    print()

    for criterio, melhor in melhores.items():
        print(f"📈 {criterio.upper().replace('_', ' ')}:")
        print(f"   Threshold: {melhor['threshold_pct']:.1f}%")
        print(f"   Trades: {melhor['trades']}")
        print(f"   Win Rate: {melhor['win_rate']:.1f}%")
        print(f"   Retorno: {melhor['return_pct']:+.2f}%")
        print(f"   Sharpe: {melhor['sharpe']:.3f}")
        print(f"   Drawdown: {melhor['drawdown_pct']:.1f}%")
        print(f"   Excesso vs Buy&Hold: {melhor['excess_return']:+.2f}%")
        print()

    # Threshold recomendado (equilíbrio)
    # Critérios: Sharpe > 0, excesso de retorno positivo, win rate > 50%
    candidatos = df_resultados[
        (df_resultados['sharpe'] > 0) &
        (df_resultados['excess_return'] > 0) &
        (df_resultados['win_rate'] > 50) &
        (df_resultados['trades'] > 10)
    ]

    if not candidatos.empty:
        # Escolher o com melhor Sharpe
        recomendado = candidatos.loc[candidatos['sharpe'].idxmax()]
        print('🎯 THRESHOLD RECOMENDADO (EQUILÍBRIO):')
        print(f"   Threshold: {recomendado['threshold_pct']:.1f}%")
        print(f"   Sharpe Ratio: {recomendado['sharpe']:.3f}")
        print(f"   Excesso Retorno: {recomendado['excess_return']:+.2f}%")
        print(f"   Win Rate: {recomendado['win_rate']:.1f}%")
        print(f"   Total Trades: {recomendado['trades']}")
    else:
        print('⚠️ NENHUM THRESHOLD ATENDE CRITÉRIOS MÍNIMOS')
        print('   → Considerar ajustes no modelo ou features')

    # Salvar resultados
    df_resultados.to_csv('otimizacao_thresholds.csv', index=False)
    print('\n💾 Resultados salvos em otimizacao_thresholds.csv')

    return df_resultados

def testar_threshold_otimo(threshold_otimo):
    """Testa o threshold ótimo encontrado."""

    print(f'\n🔬 TESTANDO THRESHOLD ÓTIMO: {threshold_otimo*100:.1f}%')
    print('='*50)

    # Preparar dados
    collector = WinDataCollector()
    data = collector.get_win_data()
    engineer = WinFeatureEngineer()
    data_with_features = engineer.create_all_features(data)

    # Split treino/teste
    split_idx = int(len(data_with_features) * 0.7)
    train_data = data_with_features[:split_idx]
    test_data = data_with_features[split_idx:]

    # Treinar modelo
    models = WinBaselineModels()
    results = models.train_baseline_models(train_data[engineer.feature_columns], train_data['Close'])

    # Gerar predições e sinais
    X_test = test_data[engineer.feature_columns]
    X_test_scaled = models.scaler.transform(X_test)
    predictions = results['xgboost']['model'].predict(X_test_scaled)
    signals = create_signals_from_predictions(predictions, threshold=threshold_otimo)

    # Backtest completo
    backtester = WinBacktester(
        initial_capital=100000.0,
        commission_per_trade=5.0,
        slippage_bps=5.0,
        max_position_size=3
    )

    strategy_metrics = backtester.run_backtest(test_data, signals)
    benchmark_metrics = benchmark_buy_and_hold(test_data, initial_capital=100000.0)

    print('📊 RESULTADO FINAL COM THRESHOLD OTIMIZADO:')
    print(f"Estratégia ML: {strategy_metrics['total_return_pct']:+.2f}% (Sharpe: {strategy_metrics['sharpe_ratio']:.3f})")
    print(f"Buy & Hold:    {benchmark_metrics['total_return_pct']:+.2f}% (Sharpe: {benchmark_metrics['sharpe_ratio']:.3f})")
    print(f"Diferença:     {strategy_metrics['total_return_pct'] - benchmark_metrics['total_return_pct']:+.2f}%")

    return strategy_metrics, benchmark_metrics

if __name__ == "__main__":
    # Otimizar thresholds
    resultados = otimizar_threshold_sinais()

    # Testar threshold ótimo se encontrado
    candidatos = resultados[
        (resultados['sharpe'] > 0) &
        (resultados['excess_return'] > 0) &
        (resultados['win_rate'] > 50) &
        (resultados['trades'] > 10)
    ]

    if not candidatos.empty:
        threshold_otimo = candidatos.loc[candidatos['sharpe'].idxmax(), 'threshold']
        testar_threshold_otimo(threshold_otimo)
    else:
        print('\n⚠️ Nenhum threshold ótimo encontrado que atenda todos os critérios.')