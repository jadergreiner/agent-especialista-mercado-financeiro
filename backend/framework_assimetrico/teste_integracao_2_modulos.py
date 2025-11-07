# Teste Integrado - Pattern Recognition + Macro Confluence
# Testa a integração dos primeiros 2 módulos do framework

"""
TESTE INTEGRADO: PATTERN RECOGNITION + MACRO CONFLUENCE

Este teste valida a integração dos primeiros 2 módulos do framework:
1. Pattern Recognition: Análise técnica (RSI, SMA, setups)
2. Macro Confluence: Análise macroeconômica (Selic, câmbio, fluxo)

Cenário: Ambiente macro favorável com setups técnicos positivos
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Tuple, Dict, Any

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def gerar_dados_teste_completos(num_periodos: int = 100) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Gera dados completos para teste: OHLCV + dados macroeconômicos.

    Returns:
        Tuple: (dados_mercado, dados_macroeconomicos)
    """
    logger.info(f"Gerando {num_periodos} períodos de dados completos")

    # Criar datas
    datas = pd.date_range('2024-01-01', periods=num_periodos, freq='D')

    # ========== DADOS DE MERCADO (WIN) ==========
    np.random.seed(42)

    # Preço WIN com ciclos de oversold/recovery para criar setups
    preco_base = 130000
    precos_close = []

    for i in range(num_periodos):
        # Criar ciclos: período de queda (oversold) seguido de recuperação
        ciclo_pos = i % 30  # Ciclo de 30 dias

        if ciclo_pos < 15:  # Primeira metade: queda para oversold
            tendencia = -0.005  # -0.5% por dia
        else:  # Segunda metade: recuperação
            tendencia = 0.008  # +0.8% por dia

        volatilidade = np.random.normal(0, 0.015)  # 1.5% volatilidade diária
        preco_base *= (1 + tendencia + volatilidade)
        precos_close.append(preco_base)

    # Gerar OHLCV baseado no Close
    dados_ohlcv = []
    for close in precos_close:
        range_diario = abs(np.random.normal(0, 0.008))
        high = close * (1 + range_diario)
        low = close * (1 - range_diario)

        if dados_ohlcv:
            open_price = dados_ohlcv[-1]['Close'] * (1 + np.random.normal(0, 0.003))
        else:
            open_price = close * (1 + np.random.normal(0, 0.01))

        volume = int(np.random.normal(550000, 80000))
        dados_ohlcv.append({
            'Open': open_price,
            'High': high,
            'Low': low,
            'Close': close,
            'Volume': max(10000, volume)
        })

    dados_mercado = {'WIN': pd.DataFrame(dados_ohlcv, index=datas)}

    # ========== DADOS MACROECONÔMICOS ==========
    # Selic em queda (favorável para mercado)
    selic_base = 11.25
    selic_dados = []
    for i in range(num_periodos):
        tendencia = -0.008 * i  # Queda gradual
        volatilidade = np.random.normal(0, 0.01)
        selic = selic_base + tendencia + volatilidade
        selic_dados.append(max(8.0, selic))

    # Câmbio com depreciação (favorável para exportações)
    cambio_base = 5.40
    cambio_dados = []
    for i in range(num_periodos):
        tendencia = 0.002 * i  # Depreciação gradual
        volatilidade = np.random.normal(0, 0.015)
        cambio = cambio_base + tendencia + volatilidade
        cambio_dados.append(max(4.5, cambio))

    # Fluxo de capitais positivo e crescente
    fluxo_base = 800
    fluxo_dados = []
    for i in range(num_periodos):
        tendencia = 3 * i  # Entrada crescente
        volatilidade = np.random.normal(0, 80)
        fluxo = fluxo_base + tendencia + volatilidade
        fluxo_dados.append(max(200, fluxo))

    dados_macroeconomicos = {
        'selic': selic_dados,
        'cambio': cambio_dados,
        'fluxo_capitais': fluxo_dados
    }

    logger.info("Dados gerados com sucesso:")
    logger.info(f"WIN: {len(dados_mercado['WIN'])} períodos")
    logger.info(f"Preço inicial WIN: {dados_mercado['WIN']['Close'].iloc[0]:.0f}")
    logger.info(f"Preço final WIN: {dados_mercado['WIN']['Close'].iloc[-1]:.0f}")
    logger.info(f"Variação WIN: {((dados_mercado['WIN']['Close'].iloc[-1] / dados_mercado['WIN']['Close'].iloc[0]) - 1) * 100:.1f}%")

    logger.info(f"Selic inicial: {selic_dados[0]:.2f}%")
    logger.info(f"Selic final: {selic_dados[-1]:.2f}%")
    logger.info(f"Câmbio inicial: R$ {cambio_dados[0]:.2f}")
    logger.info(f"Câmbio final: R$ {cambio_dados[-1]:.2f}")
    logger.info(f"Fluxo inicial: ${fluxo_dados[0]:.0f}M")
    logger.info(f"Fluxo final: ${fluxo_dados[-1]:.0f}M")

    return dados_mercado, dados_macroeconomicos

def testar_integracao_dois_modulos():
    """Testa integração Pattern Recognition + Macro Confluence"""
    print("=" * 70)
    print("TESTE INTEGRADO: PATTERN RECOGNITION + MACRO CONFLUENCE")
    print("=" * 70)

    try:
        # Importar framework diretamente
        from framework_assimetrico import FrameworkAssimetrico

        # Gerar dados de teste
        dados_mercado, dados_macroeconomicos = gerar_dados_teste_completos(100)

        # Configuração do framework
        config = {
            'ativos_principais': ['WIN'],
            'janela_analise_dias': 90,
            'threshold_assimetria': 50,
            'max_setups_por_analise': 5,
            'timeout_processamento': 30,
            'cache_resultados': False,
            'validade_setup_horas': 24
        }

        # Inicializar framework
        framework = FrameworkAssimetrico(config)
        print(f"Módulos carregados: {list(framework.modulos.keys())}")

        # Executar análise parcial (apenas módulos implementados)
        print("\n" + "=" * 50)
        print("EXECUTANDO ANÁLISE PARCIAL (2 MÓDULOS)")
        print("=" * 50)

        inicio = datetime.now()

        # Executar módulos individualmente
        resultado_pr = None
        resultado_mc = None

        if 'pattern_recognition' in framework.modulos:
            resultado_pr = framework.modulos['pattern_recognition'].analisar(dados_mercado)
            print(f"✓ Pattern Recognition: {resultado_pr.status} (Confiança: {resultado_pr.confianca:.1f}%)")

        if 'macro_confluence' in framework.modulos:
            resultado_mc = framework.modulos['macro_confluence'].analisar(dados_macroeconomicos)
            print(f"✓ Macro Confluence: {resultado_mc.status} (Confiança: {resultado_mc.confianca:.1f}%)")

        tempo_total = (datetime.now() - inicio).total_seconds()

        # Apresentar resultados consolidados
        print(f"\nTempo total processamento: {tempo_total:.2f}s")

        # ========== ANÁLISE PATTERN RECOGNITION ==========
        if resultado_pr and resultado_pr.status == 'SUCCESS':
            print("\n" + "-" * 40)
            print("📊 PATTERN RECOGNITION RESULTS")
            print("-" * 40)

            dados_pr = resultado_pr.dados_analisados['WIN']
            print(f"Setups identificados: {len(dados_pr['setups'])}")
            print(f"Pontos analisados: {dados_pr['pontos_dados']}")

            if dados_pr['setups']:
                for i, setup in enumerate(dados_pr['setups'][:2]):
                    print(f"Setup {i+1}: {setup['tipo']} - {setup['direcao']} (Força: {setup['forca']:.2f})")

        # ========== ANÁLISE MACRO CONFLUENCE ==========
        if resultado_mc and resultado_mc.status == 'SUCCESS':
            print("\n" + "-" * 40)
            print("🌍 MACRO CONFLUENCE RESULTS")
            print("-" * 40)

            dados_mc = resultado_mc.dados_analisados
            print(f"Confluência Geral: {dados_mc['pontuacao_confluencia']:.1f}%")
            print(f"Tendência Macro: {dados_mc['impacto_mercado']['tendencia_geral']}")
            print(f"Força do Sinal: {dados_mc['impacto_mercado']['forca_sinal']}%")
            print(f"Impacto Esperado: {dados_mc['impacto_mercado']['impacto_esperado']}")

            # Detalhes por indicador
            print("\nIndicadores Macro:")
            selic = dados_mc['analise_selic']
            cambio = dados_mc['analise_cambio']
            fluxo = dados_mc['analise_fluxo']

            print(f"  Selic: {selic['selic_atual']:.2f}% ({selic['classificacao']}) - Pontuação: {selic['pontuacao']}")
            print(f"  Câmbio: R$ {cambio['cambio_atual']:.2f} ({cambio['classificacao']}) - Pontuação: {cambio['pontuacao']}")
            print(f"  Fluxo: ${fluxo['fluxo_atual']:,.0f}M ({fluxo['classificacao']}) - Pontuação: {fluxo['pontuacao']}")

        # ========== ANÁLISE DE CONFLUÊNCIA ==========
        print("\n" + "=" * 50)
        print("🎯 ANÁLISE DE CONFLUÊNCIA TÉCNICA vs MACRO")
        print("=" * 50)

        confluencia_tecnica = 0
        confluencia_macro = 0

        if resultado_pr and resultado_pr.status == 'SUCCESS':
            # Calcular força técnica baseada nos setups
            dados_pr = resultado_pr.dados_analisados['WIN']
            num_setups = len(dados_pr['setups'])
            forca_setups = sum(setup['forca'] for setup in dados_pr['setups']) / max(1, num_setups)
            confluencia_tecnica = min(100, (num_setups * 10) + (forca_setups * 20))

        if resultado_mc and resultado_mc.status == 'SUCCESS':
            confluencia_macro = resultado_mc.dados_analisados['pontuacao_confluencia']

        print(f"Confluência Técnica: {confluencia_tecnica:.1f}%")
        print(f"Confluência Macro: {confluencia_macro:.1f}%")

        # Análise de assimetria
        confluencia_total = (confluencia_tecnica + confluencia_macro) / 2

        if confluencia_total >= 75:
            sinal_assimetria = "🚀 ALTAMENTE ASSIMÉTRICO (FAVORÁVEL)"
            recomendacao = "OPORTUNIDADE DE COMPRA FORTE"
        elif confluencia_total >= 60:
            sinal_assimetria = "✅ ASSIMÉTRICO (FAVORÁVEL)"
            recomendacao = "OPORTUNIDADE DE COMPRA"
        elif confluencia_total >= 40:
            sinal_assimetria = "⚪ NEUTRO"
            recomendacao = "AGUARDAR MELHOR CONFLUÊNCIA"
        else:
            sinal_assimetria = "❌ DESFAVORÁVEL"
            recomendacao = "EVITAR POSIÇÃO"

        print(f"Confluência Total: {confluencia_total:.1f}%")
        print(f"Sinal de Assimetria: {sinal_assimetria}")
        print(f"Recomendação: {recomendacao}")

        # ========== VALIDAÇÃO ==========
        print("\n" + "=" * 40)
        print("VALIDAÇÃO DOS RESULTADOS")
        print("=" * 40)

        validacoes = []

        # Módulos carregados
        modulos_ok = len(framework.modulos) >= 2
        validacoes.append(("2+ módulos carregados", modulos_ok))

        # Resultados válidos
        pr_ok = resultado_pr and resultado_pr.status == 'SUCCESS' if resultado_pr else False
        mc_ok = resultado_mc and resultado_mc.status == 'SUCCESS' if resultado_mc else False
        validacoes.append(("Pattern Recognition OK", pr_ok))
        validacoes.append(("Macro Confluence OK", mc_ok))

        # Performance
        tempo_ok = tempo_total < 1.0
        validacoes.append(("Tempo < 1s", tempo_ok))

        # Confluência razoável
        confluencia_ok = confluencia_total > 50
        validacoes.append(("Confluência > 50%", confluencia_ok))

        print("Validações:")
        for teste, passou in validacoes:
            status = "✅" if passou else "❌"
            print(f"  {status} {teste}")

        testes_aprovados = sum(1 for _, passou in validacoes if passou)
        total_testes = len(validacoes)

        print(f"\nResultado: {testes_aprovados}/{total_testes} testes passaram")

        if testes_aprovados == total_testes:
            print("🎉 INTEGRAÇÃO BEM-SUCEDIDA!")
            return True
        else:
            print("⚠️  Alguns testes falharam")
            return False

    except Exception as e:
        logger.error(f"Erro no teste integrado: {e}")
        print(f"\n❌ ERRO: {e}")
        return False

if __name__ == "__main__":
    sucesso = testar_integracao_dois_modulos()
    exit(0 if sucesso else 1)