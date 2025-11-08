# Teste de Integração: Framework Assimétrico + Playbook WIN
# Demonstração da integração completa entre análise técnica avançada e playbook operacional

"""
TESTE DE INTEGRAÇÃO - FRAMEWORK ASSIMÉTRICO + PLAYBOOK WIN

Este script demonstra a integração completa entre:
1. Framework de Detecção Assimétrica (6 módulos)
2. Gerador de Playbook Quantitativo WIN

Fluxo de teste:
- Gera dados de mercado simulados
- Executa análise completa do framework
- Gera playbook operacional integrado
- Exibe resultados consolidados
"""

import sys
import os
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Adicionar backend ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from framework_assimetrico import FrameworkAssimetrico
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def gerar_dados_teste_playbook() -> dict:
    """
    Gera dados de mercado simulados para teste do playbook.

    Returns:
        Dict com dados de mercado simulados
    """
    logger.info("Gerando dados de teste para playbook")

    # Simular dados de 60 dias
    np.random.seed(42)  # Para reprodutibilidade
    datas = pd.date_range(start='2024-01-01', periods=60, freq='D')

    dados_mercado = {}

    # WIN (Mini Ibovespa)
    win_base = 130000
    win_volatility = 0.02
    win_trend = 0.0005  # Tendência ligeira de alta
    win_prices = []
    price = win_base

    for i in range(60):
        change = np.random.normal(win_trend, win_volatility)
        price *= (1 + change)
        win_prices.append(price)

    win_df = pd.DataFrame({
        'Open': win_prices,
        'High': [p * (1 + abs(np.random.normal(0, 0.01))) for p in win_prices],
        'Low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in win_prices],
        'Close': win_prices,
        'Volume': [np.random.randint(100000, 500000) for _ in range(60)]
    }, index=datas)
    dados_mercado['WIN'] = win_df

    # Dólar
    dol_base = 5.20
    dol_volatility = 0.015
    dol_prices = []
    price = dol_base

    for i in range(60):
        change = np.random.normal(0, dol_volatility)
        price *= (1 + change)
        dol_prices.append(price)

    dol_df = pd.DataFrame({
        'Open': dol_prices,
        'High': [p * (1 + abs(np.random.normal(0, 0.008))) for p in dol_prices],
        'Low': [p * (1 - abs(np.random.normal(0, 0.008))) for p in dol_prices],
        'Close': dol_prices,
        'Volume': [np.random.randint(50000, 200000) for _ in range(60)]
    }, index=datas)
    dados_mercado['DOL'] = dol_df

    # Ibovespa
    ibov_base = 125000
    ibov_prices = []
    price = ibov_base

    for i in range(60):
        # Correlação com WIN
        win_change = (win_prices[i] - win_prices[i-1]) / win_prices[i-1] if i > 0 else 0
        change = win_change * 0.8 + np.random.normal(0, 0.018)
        price *= (1 + change)
        ibov_prices.append(price)

    ibov_df = pd.DataFrame({
        'Open': ibov_prices,
        'High': [p * (1 + abs(np.random.normal(0, 0.012))) for p in ibov_prices],
        'Low': [p * (1 - abs(np.random.normal(0, 0.012))) for p in ibov_prices],
        'Close': ibov_prices,
        'Volume': [np.random.randint(2000000, 8000000) for _ in range(60)]
    }, index=datas)
    dados_mercado['IBOV'] = ibov_df

    logger.info(f"Dados gerados para {len(dados_mercado)} ativos")
    return dados_mercado

def executar_teste_integracao():
    """Executa teste completo de integração"""
    print("🧭 TESTE DE INTEGRAÇÃO - FRAMEWORK ASSIMÉTRICO + PLAYBOOK WIN")
    print("=" * 70)

    try:
        # 1. Gerar dados de teste
        print("\n📊 1. Gerando dados de mercado simulados...")
        dados_mercado = gerar_dados_teste_playbook()

        # 2. Inicializar framework
        print("\n🏗️ 2. Inicializando Framework de Detecção Assimétrica...")
        config = {
            'ativos_principais': ['WIN', 'IBOV', 'DOL'],
            'janela_analise_dias': 30,
            'threshold_assimetria': 50,
            'max_setups_por_analise': 2
        }
        framework = FrameworkAssimetrico(config)

        # 3. Executar análise assimétrica
        print("\n🔍 3. Executando análise de oportunidades assimétricas...")
        resultado_analise = framework.analisar_oportunidades(dados_mercado)

        print("   Status:", resultado_analise.status)
        print(f"   Tempo processamento: {resultado_analise.tempo_processamento:.2f}s")
        print(f"   Setups identificados: {len(resultado_analise.setups_identificados)}")

        # 4. Gerar playbook operacional
        print("\n📝 4. Gerando playbook operacional integrado...")
        playbook = framework.gerar_playbook_operacional(dados_mercado, salvar_arquivo=False)

        # 5. Exibir resultados
        print("\n📋 5. RESULTADOS DA INTEGRAÇÃO")
        print("-" * 40)

        print(f"\n🎯 Setups Assimétricos Identificados: {len(resultado_analise.setups_identificados)}")
        for i, setup in enumerate(resultado_analise.setups_identificados, 1):
            print(f"   {i}. {setup.ativo} - {setup.direcao} "
                  f"(Assimetria: {setup.pontuacao_assimetria:.1f}, "
                  f"Risk/Reward: {setup.risk_reward_ratio:.2f})")

        print("\n📊 Insights Técnicos Integrados:")
        # Extrair insights do playbook
        linhas_playbook = playbook.split('\n')
        in_secao_insights = False
        for linha in linhas_playbook:
            if 'INSIGHTS DA ANÁLISE ASSIMÉTRICA' in linha:
                in_secao_insights = True
                continue
            elif linha.startswith('##') and in_secao_insights:
                break
            elif in_secao_insights and linha.strip():
                print(f"   {linha}")

        print("\n📈 Métricas do Framework:")
        metricas = framework.obter_metricas_framework()
        print(f"   Módulos carregados: {len(metricas['modulos_carregados'])}")
        print(f"   Status módulos: {metricas['status_modulos']}")

        # 6. Salvar playbook final
        nome_arquivo = f"playbook_integrado_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            f.write(playbook)

        print(f"\n💾 Playbook salvo: {nome_arquivo}")

        print("\n✅ TESTE DE INTEGRAÇÃO CONCLUÍDO COM SUCESSO!")
        print("   Framework Assimétrico: Funcional")
        print("   Playbook WIN: Integrado")
        print("   Análise Combinada: Operacional")

        return True

    except Exception as e:
        logger.error(f"Erro no teste de integração: {e}")
        print(f"\n❌ ERRO NO TESTE: {e}")
        return False

if __name__ == "__main__":
    sucesso = executar_teste_integracao()
    sys.exit(0 if sucesso else 1)