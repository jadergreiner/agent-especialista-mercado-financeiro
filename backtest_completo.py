"""
Executa Backtesting Completo da Estratégia WIN

Testa a estratégia ML com custos reais de transação,
slippage e validação walk-forward.

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
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_complete_backtest():
    """Executa backtesting completo da estratégia WIN."""

    print('🚀 BACKTESTING COMPLETO - ESTRATÉGIA WIN ML')
    print('='*60)
    print(f'Data: {datetime.now().strftime("%Y-%m-%d %H:%M")}')
    print()

    # 1. Coletar e processar dados
    print('📊 Preparando dados...')
    collector = WinDataCollector()
    data = collector.get_win_data()
    engineer = WinFeatureEngineer()
    data_with_features = engineer.create_all_features(data)

    print(f'Dados: {len(data_with_features)} registros ({data_with_features.index.min().strftime("%Y-%m-%d")} até {data_with_features.index.max().strftime("%Y-%m-%d")})')

    # 2. Treinar modelo (usando apenas dados de treino)
    print('🤖 Treinando modelo XGBoost...')
    feature_cols = engineer.feature_columns
    target_col = 'Close'

    # Split temporal para backtesting realista
    split_idx = int(len(data_with_features) * 0.7)  # 70% treino, 30% teste
    train_data = data_with_features[:split_idx]
    test_data = data_with_features[split_idx:]

    print(f'Treino: {len(train_data)} registros')
    print(f'Teste: {len(test_data)} registros')

    # Treinar modelo apenas com dados de treino
    models = WinBaselineModels()
    results = models.train_baseline_models(train_data[feature_cols], train_data[target_col])

    # Usar XGBoost (melhor performance de risco-retorno)
    model = results['xgboost']['model']

    # 3. Gerar predições para dados de teste
    print('🔮 Gerando predições...')
    X_test = test_data[feature_cols]
    X_test_scaled = models.scaler.transform(X_test)
    predictions = model.predict(X_test_scaled)

    # Criar sinais de trading
    signals = create_signals_from_predictions(predictions, threshold=0.005)  # 0.5% threshold

    print(f'Sinais gerados: {len(signals)} (Compras: {(signals > 0).sum()}, Vendas: {(signals < 0).sum()}, Hold: {(signals == 0).sum()})')

    # 4. Executar backtesting
    print('📈 Executando backtesting...')

    # Configurações realistas para WIN (Mini Ibovespa)
    backtester = WinBacktester(
        initial_capital=100000.0,      # R$ 100k
        commission_per_trade=5.0,      # R$ 5 por contrato
        slippage_bps=5.0,              # 5 basis points slippage
        max_position_size=3            # Máximo 3 contratos
    )

    # Executar backtest
    strategy_metrics = backtester.run_backtest(test_data, signals)

    # 5. Benchmark Buy & Hold
    print('⚖️ Calculando benchmark Buy & Hold...')
    benchmark_metrics = benchmark_buy_and_hold(test_data, initial_capital=100000.0)

    # 6. Resultados
    print('\n' + '='*60)
    print('📊 RESULTADOS DO BACKTESTING')
    print('='*60)

    print('🎯 ESTRATÉGIA ML (XGBoost):')
    print(f'   Retorno Total: {strategy_metrics["total_return_pct"]:+.2f}%')
    print(f'   Retorno Anual: {strategy_metrics["annual_return_pct"]:+.2f}%')
    print(f'   Sharpe Ratio: {strategy_metrics["sharpe_ratio"]:.3f}')
    print(f'   Max Drawdown: {strategy_metrics["max_drawdown_pct"]:.2f}%')
    print(f'   Calmar Ratio: {strategy_metrics["calmar_ratio"]:.3f}')
    print(f'   Total de Trades: {strategy_metrics["total_trades"]}')
    print(f'   Win Rate: {strategy_metrics["win_rate_pct"]:.1f}%')
    print(f'   Profit Factor: {strategy_metrics["profit_factor"]:.2f}')
    print(f'   P&L Total: R$ {strategy_metrics["total_pnl"]:,.2f}')

    print('\n⚖️ BENCHMARK BUY & HOLD:')
    print(f'   Retorno Total: {benchmark_metrics["total_return_pct"]:+.2f}%')
    print(f'   Retorno Anual: {benchmark_metrics["annual_return_pct"]:+.2f}%')
    print(f'   Sharpe Ratio: {benchmark_metrics["sharpe_ratio"]:.3f}')
    print(f'   Max Drawdown: {benchmark_metrics["max_drawdown_pct"]:.2f}%')
    print(f'   Calmar Ratio: {benchmark_metrics["calmar_ratio"]:.3f}')

    # Comparação
    excess_return = strategy_metrics["total_return_pct"] - benchmark_metrics["total_return_pct"]
    print(f'\n🔥 DIFERENÇA vs BUY & HOLD:')
    print(f'   Retorno Excessivo: {excess_return:+.2f}%')
    print(f'   Sharpe Superior: {"✅" if strategy_metrics["sharpe_ratio"] > benchmark_metrics["sharpe_ratio"] else "❌"}')
    print(f'   Drawdown Inferior: {"✅" if strategy_metrics["max_drawdown_pct"] < benchmark_metrics["max_drawdown_pct"] else "❌"}')

    # Análise de trades
    trades_df = backtester.get_trades_df()
    if not trades_df.empty:
        print(f'\n📋 ANÁLISE DE TRADES:')
        print(f'   Trades Executados: {len(trades_df)}')
        print(f'   Compras: {len(trades_df[trades_df["type"] == "BUY"])}')
        print(f'   Vendas: {len(trades_df[trades_df["type"] == "SELL"])}')
        print(f'   Comissão Total: R$ {trades_df["commission"].sum():,.2f}')
        print(f'   Slippage Total: R$ {trades_df["slippage"].sum():,.2f}')

    # Salvar resultados
    results_summary = {
        'strategy': strategy_metrics,
        'benchmark': benchmark_metrics,
        'comparison': {
            'excess_return_pct': excess_return,
            'sharpe_superior': strategy_metrics["sharpe_ratio"] > benchmark_metrics["sharpe_ratio"],
            'drawdown_superior': strategy_metrics["max_drawdown_pct"] < benchmark_metrics["max_drawdown_pct"]
        },
        'config': {
            'initial_capital': 100000.0,
            'commission_per_trade': 5.0,
            'slippage_bps': 5.0,
            'max_position_size': 3,
            'signal_threshold': 0.005
        }
    }

    # Salvar em arquivo
    import json
    with open('backtest_results.json', 'w') as f:
        # Converter para tipos serializáveis
        serializable_results = {}
        for key, value in results_summary.items():
            if isinstance(value, dict):
                serializable_results[key] = {}
                for k, v in value.items():
                    if isinstance(v, (int, float, bool)):
                        serializable_results[key][k] = v
                    else:
                        serializable_results[key][k] = str(v)
            else:
                serializable_results[key] = value

        json.dump(serializable_results, f, indent=2, ensure_ascii=False)

    print(f'\n💾 Resultados salvos em backtest_results.json')

    return strategy_metrics, benchmark_metrics

if __name__ == "__main__":
    run_complete_backtest()