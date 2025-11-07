"""CLI para testar estratégias avançadas."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.backtest.motor_backtest import BacktestEngine
from src.backtest.estrategias_avancadas import (
    EstrategiaEnsemble,
    EstrategiaMultiIndicador,
    EstrategiaRegimeMercado
)

def testar_ensemble():
    """Testa estratégia Ensemble."""
    print("\n🔬 TESTANDO ESTRATÉGIA ENSEMBLE")
    print("="*80)

    engine = BacktestEngine()
    estrategia = EstrategiaEnsemble(
        usar_ma=True,
        usar_rsi=True,
        usar_bollinger=True,
        usar_macd=True,
        limiar_consenso=0.6
    )

    resultado = engine.executar_backtest(
        estrategia=estrategia,
        instrumento='WIN',
        data_inicio='2024-01-01',
        data_fim='2024-12-31',
        salvar_recomendacoes=True
    )

    return resultado

def testar_multi_indicador():
    """Testa estratégia Multi-Indicador."""
    print("\n🔬 TESTANDO ESTRATÉGIA MULTI-INDICADOR")
    print("="*80)

    engine = BacktestEngine()
    estrategia = EstrategiaMultiIndicador(
        periodo_ma_curta=9,
        periodo_ma_longa=21,
        periodo_rsi=14
    )

    resultado = engine.executar_backtest(
        estrategia=estrategia,
        instrumento='WIN',
        data_inicio='2024-01-01',
        data_fim='2024-12-31',
        salvar_recomendacoes=True
    )

    return resultado

def testar_regime_mercado():
    """Testa estratégia de Regime de Mercado."""
    print("\n🔬 TESTANDO ESTRATÉGIA REGIME ADAPTATIVO")
    print("="*80)

    engine = BacktestEngine()
    estrategia = EstrategiaRegimeMercado(
        periodo_atr=14,
        limiar_volatilidade=1.5
    )

    resultado = engine.executar_backtest(
        estrategia=estrategia,
        instrumento='WIN',
        data_inicio='2024-01-01',
        data_fim='2024-12-31',
        salvar_recomendacoes=True
    )

    return resultado

if __name__ == '__main__':
    print("\n" + "="*80)
    print("🚀 TESTANDO ESTRATÉGIAS AVANÇADAS - 2024")
    print("="*80)

    # Testar todas
    testar_ensemble()
    testar_multi_indicador()
    testar_regime_mercado()

    print("\n" + "="*80)
    print("✅ TODOS OS TESTES CONCLUÍDOS!")
    print("="*80)
    print("\n💡 Execute 'python comparar_estrategias.py' para ver a comparação completa.")
