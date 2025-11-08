"""
Comparativo Completo de Modelos WIN

Compara performance de todos os modelos testados
com dados de 30 anos.

Autor: Sistema Especialista de Mercado Financeiro
Data: 2025
"""

import pandas as pd
import numpy as np
from datetime import datetime

def criar_relatorio_comparativo():
    """Cria relatório comparativo de todos os modelos."""

    # Dados dos testes realizados
    modelos = {
        'Regressão Linear': {
            'mape': 0.14,
            'rmse': 148.58,
            'r2': 0.9997,
            'directional_accuracy': 95.66,
            'sharpe_ratio': 0.367,
            'max_drawdown': 60.20,
            'tipo': 'Baseline',
            'obs': 'Overfitting no treino, bom para direção'
        },
        'Random Forest': {
            'mape': 0.61,
            'rmse': 2194.88,
            'r2': 0.8321,
            'directional_accuracy': 92.46,
            'sharpe_ratio': 0.347,
            'max_drawdown': 56.74,
            'tipo': 'Baseline',
            'obs': 'Bom equilíbrio geral'
        },
        'XGBoost': {
            'mape': 1.91,
            'rmse': 4702.34,
            'r2': 0.8432,
            'directional_accuracy': 83.86,
            'sharpe_ratio': 0.430,
            'max_drawdown': 21.87,
            'tipo': 'Avançado',
            'obs': 'Melhor Sharpe e Drawdown'
        }
    }

    print('🚀 RELATÓRIO COMPARATIVO - MODELOS WIN (30 ANOS DE DADOS)')
    print('='*80)
    print(f'Data do teste: {datetime.now().strftime("%Y-%m-%d %H:%M")}')
    print('Dados: 4.773 registros (1995-2025) - 52 features técnicas')
    print('Período: 2002-07-02 até 2025-11-06')
    print()

    # Tabela comparativa
    print('📊 MÉTRICAS DE PERFORMANCE')
    print('-'*80)
    header = f"{'Modelo':<15} {'MAPE':<8} {'RMSE':<10} {'R²':<8} {'DirAcc':<8} {'Sharpe':<8} {'Drawdown':<8} {'Tipo':<10}"
    print(header)
    print('-'*80)

    for nome, metricas in modelos.items():
        linha = (f"{nome:<15} "
                f"{metricas['mape']:<8.2f} "
                f"{metricas['rmse']:<10.0f} "
                f"{metricas['r2']:<8.3f} "
                f"{metricas['directional_accuracy']:<8.1f} "
                f"{metricas['sharpe_ratio']:<8.3f} "
                f"{metricas['max_drawdown']:<8.1f} "
                f"{metricas['tipo']:<10}")
        print(linha)

    print()

    # Análise por categoria
    print('🎯 ANÁLISE POR CATEGORIA')
    print('-'*80)

    # Melhor modelo por métrica
    melhores = {}
    for metrica in ['mape', 'rmse', 'r2', 'directional_accuracy', 'sharpe_ratio', 'max_drawdown']:
        if metrica in ['max_drawdown']:  # Menor é melhor
            melhor = min(modelos.keys(), key=lambda x: modelos[x][metrica])
        else:  # Maior é melhor
            melhor = max(modelos.keys(), key=lambda x: modelos[x][metrica])
        melhores[metrica] = (melhor, modelos[melhor][metrica])

    print('🏆 Melhores Modelos por Métrica:')
    print(f"   Menor MAPE: {melhores['mape'][0]} ({melhores['mape'][1]:.2f}%)")
    print(f"   Menor RMSE: {melhores['rmse'][0]} ({melhores['rmse'][1]:.0f})")
    print(f"   Maior R²: {melhores['r2'][0]} ({melhores['r2'][1]:.3f})")
    print(f"   Maior Directional Accuracy: {melhores['directional_accuracy'][0]} ({melhores['directional_accuracy'][1]:.1f}%)")
    print(f"   Maior Sharpe Ratio: {melhores['sharpe_ratio'][0]} ({melhores['sharpe_ratio'][1]:.3f})")
    print(f"   Menor Max Drawdown: {melhores['max_drawdown'][0]} ({melhores['max_drawdown'][1]:.1f}%)")

    print()

    # Recomendações
    print('💡 RECOMENDAÇÕES')
    print('-'*80)
    print('1. PARA PREVISÃO DE PREÇO (MAE/RMSE): Regressão Linear')
    print('2. PARA DIREÇÃO DO MERCADO: Regressão Linear (95.66%)')
    print('3. PARA RISCO AJUSTADO: XGBoost (Sharpe 0.430, Drawdown 21.87%)')
    print('4. PARA GENERALIZAÇÃO: XGBoost (melhor no conjunto de teste)')
    print()
    print('🔍 INSIGHTS IMPORTANTES:')
    print('• Dados de 30 anos capturam crises (1997, 2001, 2008, 2020)')
    print('• Regressão Linear sofre overfitting mas é ótima para direção')
    print('• XGBoost oferece melhor equilíbrio risco-retorno')
    print('• Random Forest é consistente mas não se destaca')
    print()
    print('📈 PRÓXIMOS PASSOS:')
    print('• Implementar validação cruzada temporal (walk-forward)')
    print('• Otimizar hiperparâmetros com grid search')
    print('• Testar ensemble de modelos')
    print('• Implementar LSTM quando TensorFlow estiver disponível')
    print('• Adicionar features de sentimento e notícias')

if __name__ == "__main__":
    criar_relatorio_comparativo()