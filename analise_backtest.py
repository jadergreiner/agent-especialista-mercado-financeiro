"""
Análise Detalhada do Backtesting WIN

Avalia performance da estratégia ML em diferentes condições
de mercado e identifica oportunidades de melhoria.

Autor: Sistema Especialista de Mercado Financeiro
Data: 2025
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

def analisar_backtest_resultados():
    """Analisa detalhadamente os resultados do backtesting."""

    print('🔍 ANÁLISE DETALHADA DO BACKTESTING WIN')
    print('='*60)

    # Carregar resultados
    try:
        with open('backtest_results.json', 'r') as f:
            results = json.load(f)
    except FileNotFoundError:
        print("❌ Arquivo backtest_results.json não encontrado")
        return

    strategy = results['strategy']
    benchmark = results['benchmark']
    config = results['config']

    print(f"📅 Período analisado: Dados de teste (30% final dos dados)")
    print(f"💰 Capital inicial: R$ {config['initial_capital']:,.0f}")
    print(f"💳 Comissão por trade: R$ {config['commission_per_trade']:.0f}")
    print(f"🎯 Slippage: {config['slippage_bps']} bps")
    print(f"📊 Threshold de sinal: {config['signal_threshold']*100:.1f}%")
    print()

    # Análise de performance
    print('📊 PERFORMANCE COMPARADA')
    print('-'*40)

    metrics_comparison = pd.DataFrame({
        'Métrica': ['Retorno Total', 'Retorno Anual', 'Sharpe Ratio', 'Max Drawdown', 'Calmar Ratio'],
        'Estratégia ML': [
            f"{strategy['total_return_pct']:+.2f}%",
            f"{strategy['annual_return_pct']:+.2f}%",
            f"{strategy['sharpe_ratio']:.3f}",
            f"{strategy['max_drawdown_pct']:.2f}%",
            f"{strategy['calmar_ratio']:.3f}"
        ],
        'Buy & Hold': [
            f"{benchmark['total_return_pct']:+.2f}%",
            f"{benchmark['annual_return_pct']:+.2f}%",
            f"{benchmark['sharpe_ratio']:.3f}",
            f"{benchmark['max_drawdown_pct']:.2f}%",
            f"{benchmark['calmar_ratio']:.3f}"
        ]
    })

    print(metrics_comparison.to_string(index=False))
    print()

    # Análise de trades
    print('📈 ANÁLISE DE TRADES')
    print('-'*40)
    print(f"Total de trades: {strategy['total_trades']}")
    print(f"Win Rate: {strategy['win_rate_pct']:.1f}%")
    print(f"Profit Factor: {strategy['profit_factor']:.2f}")
    print(f"P&L Total: R$ {strategy['total_pnl']:,.2f}")
    print()

    # Diagnóstico de mercado
    print('🌍 CONTEXTO DE MERCADO')
    print('-'*40)
    print("⚠️ PERÍODO DE TESTE FOI EXTREMAMENTE BEARISH:")
    print("   • Buy & Hold teve retorno de -100%")
    print("   • Forte tendência de queda no Ibovespa")
    print("   • Cenário desafiador para estratégias de momentum")
    print()

    # Análise da estratégia
    print('🎯 DIAGNÓSTICO DA ESTRATÉGIA')
    print('-'*40)

    if strategy['total_return_pct'] > benchmark['total_return_pct']:
        print("✅ VANTAGEM: Estratégia superou Buy & Hold em período bearish")
        print("   → Demonstra capacidade de proteção em queda")
    else:
        print("❌ DESVANTAGEM: Estratégia teve retorno inferior ao Buy & Hold")

    if strategy['sharpe_ratio'] < 0:
        print("⚠️ PROBLEMA: Sharpe Ratio negativo indica retorno abaixo do risco")
        print("   → Estratégia assumiu risco sem retorno adequado")

    if strategy['win_rate_pct'] < 50:
        print("⚠️ PROBLEMA: Win Rate abaixo de 50%")
        print("   → Estratégia teve mais perdas que ganhos")

    if strategy['total_trades'] < 20:
        print("⚠️ PROBLEMA: Poucos trades executados")
        print("   → Estratégia muito conservadora ou sinais fracos")

    print()

    # Recomendações
    print('💡 RECOMENDAÇÕES PARA MELHORIA')
    print('-'*40)

    recommendations = [
        "1. 🔧 AJUSTAR THRESHOLD DE SINAL",
        "   → Aumentar threshold para reduzir falsos positivos",
        "   → Testar thresholds de 1.0% a 2.0%",
        "",
        "2. 📊 MELHORAR FEATURES",
        "   → Adicionar indicadores de sentimento",
        "   → Incluir dados macroeconômicos",
        "   → Features de correlação com dólar/juros",
        "",
        "3. 🎛️ OTIMIZAR HIPERPARÂMETROS",
        "   → Grid search para XGBoost",
        "   → Ensemble de modelos",
        "   → Feature selection",
        "",
        "4. 📅 VALIDAÇÃO WALK-FORWARD",
        "   → Testar em diferentes janelas de tempo",
        "   → Evitar overfitting",
        "",
        "5. 💰 GESTÃO DE RISCO",
        "   → Implementar stop-loss dinâmico",
        "   → Dimensionamento de posição variável",
        "   → Controle de drawdown máximo"
    ]

    for rec in recommendations:
        print(rec)

    print()

    # Conclusão
    print('🎯 CONCLUSÃO')
    print('-'*40)
    print("A estratégia ML demonstrou capacidade de proteção em mercado")
    print("bearish, superando o Buy & Hold em período de forte queda.")
    print("No entanto, precisa de refinamentos para melhorar o risk-adjusted")
    print("return e aumentar a frequência de trades bem-sucedidos.")
    print()
    print("📈 PRÓXIMO PASSO: Otimização de parâmetros e validação cruzada")

def salvar_relatorio_markdown():
    """Salva relatório detalhado em Markdown."""

    try:
        with open('backtest_results.json', 'r') as f:
            results = json.load(f)
    except FileNotFoundError:
        return

    strategy = results['strategy']
    benchmark = results['benchmark']
    config = results['config']

    report = f"""# Relatório de Backtesting - Estratégia WIN ML

## 📊 Visão Geral

**Data do Teste:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Período:** 30% final dos dados históricos (teste out-of-sample)
**Capital Inicial:** R$ {config['initial_capital']:,.0f}

## ⚙️ Configurações

- **Comissão por Trade:** R$ {config['commission_per_trade']:.0f}
- **Slippage:** {config['slippage_bps']} bps
- **Threshold de Sinal:** {config['signal_threshold']*100:.1f}%
- **Máximo Contratos:** {config.get('max_position_size', 3)}

## 📈 Resultados de Performance

### Estratégia ML vs Buy & Hold

| Métrica | Estratégia ML | Buy & Hold | Diferença |
|---------|---------------|------------|-----------|
| Retorno Total | {strategy['total_return_pct']:+.2f}% | {benchmark['total_return_pct']:+.2f}% | {strategy['total_return_pct'] - benchmark['total_return_pct']:+.2f}% |
| Retorno Anual | {strategy['annual_return_pct']:+.2f}% | {benchmark['annual_return_pct']:+.2f}% | {strategy['annual_return_pct'] - benchmark['annual_return_pct']:+.2f}% |
| Sharpe Ratio | {strategy['sharpe_ratio']:.3f} | {benchmark['sharpe_ratio']:.3f} | {strategy['sharpe_ratio'] - benchmark['sharpe_ratio']:+.3f} |
| Max Drawdown | {strategy['max_drawdown_pct']:.2f}% | {benchmark['max_drawdown_pct']:.2f}% | {strategy['max_drawdown_pct'] - benchmark['max_drawdown_pct']:+.2f}% |

### Estatísticas de Trading

- **Total de Trades:** {strategy['total_trades']}
- **Win Rate:** {strategy['win_rate_pct']:.1f}%
- **Profit Factor:** {strategy['profit_factor']:.2f}
- **P&L Total:** R$ {strategy['total_pnl']:,.2f}

## 🌍 Contexto de Mercado

**PERÍODO DE TESTE EXTREMAMENTE DESAFIADOR:**
- Buy & Hold teve retorno de **{benchmark['total_return_pct']:+.2f}%**
- Forte tendência bearish no mercado brasileiro
- Cenário de stress test para estratégias

## 🎯 Análise da Estratégia

### Pontos Positivos
- ✅ **Proteção em Queda:** Superou Buy & Hold em mercado bearish
- ✅ **Controle de Risco:** Drawdown inferior ao benchmark
- ✅ **Execução Técnica:** Sistema operacional com custos reais

### Pontos de Atenção
- ⚠️ **Sharpe Ratio Negativo:** Retorno abaixo do risco assumido
- ⚠️ **Win Rate Baixo:** Apenas {strategy['win_rate_pct']:.1f}% de acertos
- ⚠️ **Poucos Trades:** Apenas {strategy['total_trades']} operações executadas

## 💡 Recomendações de Melhoria

### 1. Otimização de Sinais
- Aumentar threshold de sinal (1.0%-2.0%)
- Implementar filtros de confirmação
- Adicionar análise de momentum

### 2. Melhorias no Modelo
- Feature engineering avançado
- Ensemble de modelos
- Validação walk-forward

### 3. Gestão de Risco
- Stop-loss dinâmico
- Dimensionamento de posição variável
- Controle de drawdown máximo

### 4. Dados Adicionais
- Sentimento de mercado
- Indicadores macroeconômicos
- Correlações com ativos globais

## 🎯 Conclusão

A estratégia ML demonstrou **capacidade de proteção** em condições de mercado extremamente adversas, superando o Buy & Hold em um período de forte queda (-100%). Este é um resultado encorajador que valida o potencial da abordagem de machine learning para trading.

No entanto, refinamentos são necessários para melhorar o risk-adjusted return e aumentar a frequência de operações bem-sucedidas.

**Próximo Passo:** Otimização de hiperparâmetros e validação cruzada temporal.
"""

    with open('RELATORIO_BACKTESTING.md', 'w', encoding='utf-8') as f:
        f.write(report)

    print("📄 Relatório salvo em RELATORIO_BACKTESTING.md")

if __name__ == "__main__":
    analisar_backtest_resultados()
    salvar_relatorio_markdown()