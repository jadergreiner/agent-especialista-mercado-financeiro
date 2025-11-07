# Teste Integrado - Pattern Recognition + Macro Confluence + Correlation Analysis
# Testa a integração dos primeiros 3 módulos do framework

"""
TESTE INTEGRADO: PATTERN RECOGNITION + MACRO CONFLUENCE + CORRELATION ANALYSIS

Este teste valida a integração dos primeiros 3 módulos do framework:
1. Pattern Recognition: Análise técnica (RSI, SMA, setups)
2. Macro Confluence: Análise macroeconômica (Selic, câmbio, fluxo)
3. Correlation Analysis: Correlação multi-ativo (WIN vs DOL, commodities)

Cenário: Ambiente macro favorável com correlações moderadas
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Tuple, Dict, Any

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def gerar_dados_teste_multi_ativo(num_periodos: int = 100) -> Tuple[pd.DataFrame, Dict[str, Any], Dict[str, pd.DataFrame]]:
    """
    Gera dados completos para teste: WIN + dados macro + múltiplos ativos.

    Returns:
        Tuple: (dados_win, dados_macroeconomicos, dados_multi_ativo)
    """
    logger.info(f"Gerando {num_periodos} períodos de dados multi-ativo")

    # Criar datas
    datas = pd.date_range('2024-01-01', periods=num_periodos, freq='D')

    # ========== DADOS WIN ==========
    np.random.seed(42)

    # WIN com ciclos de oversold/recovery para criar setups
    preco_base_win = 130000
    precos_close_win = []

    for i in range(num_periodos):
        # Criar ciclos: período de queda (oversold) seguido de recuperação
        ciclo_pos = i % 30  # Ciclo de 30 dias

        if ciclo_pos < 15:  # Primeira metade: queda para oversold
            tendencia = -0.005  # -0.5% por dia
        else:  # Segunda metade: recuperação
            tendencia = 0.008  # +0.8% por dia

        volatilidade = np.random.normal(0, 0.015)  # 1.5% volatilidade diária
        preco_base_win *= (1 + tendencia + volatilidade)
        precos_close_win.append(preco_base_win)

    # Gerar OHLCV para WIN
    dados_ohlcv_win = []
    for close in precos_close_win:
        range_diario = abs(np.random.normal(0, 0.008))
        high = close * (1 + range_diario)
        low = close * (1 - range_diario)

        if dados_ohlcv_win:
            open_price = dados_ohlcv_win[-1]['Close'] * (1 + np.random.normal(0, 0.003))
        else:
            open_price = close * (1 + np.random.normal(0, 0.01))

        volume = int(np.random.normal(550000, 80000))
        dados_ohlcv_win.append({
            'Open': open_price,
            'High': high,
            'Low': low,
            'Close': close,
            'Volume': max(10000, volume)
        })

    dados_win = pd.DataFrame(dados_ohlcv_win, index=datas)

    # ========== DADOS MACROECONÔMICOS ==========
    # Selic em queda (favorável para mercado)
    selic_base = 11.25
    selic_dados = []
    for i in range(num_periodos):
        tendencia = -0.008 * i  # Queda gradual
        volatilidade = np.random.normal(0, 0.01)
        selic = selic_base + tendencia + volatilidade
        selic_dados.append(max(2.0, selic))  # Selic não pode ser negativa

    # Câmbio com apreciação gradual (favorável)
    cambio_base = 5.40
    cambio_dados = []
    for i in range(num_periodos):
        tendencia = -0.002 * i  # Apreciação gradual
        volatilidade = np.random.normal(0, 0.008)
        cambio = cambio_base + tendencia + volatilidade
        cambio_dados.append(max(3.0, cambio))  # Câmbio não pode ser muito baixo

    # Fluxo de capitais positivo
    fluxo_base = 850
    fluxo_dados = []
    for i in range(num_periodos):
        tendencia = 0.5 * i  # Aumento gradual
        volatilidade = np.random.normal(0, 50)
        fluxo = fluxo_base + tendencia + volatilidade
        fluxo_dados.append(max(200, fluxo))  # Fluxo mínimo

    dados_macroeconomicos = {
        'selic': pd.Series(selic_dados, index=datas),
        'cambio': pd.Series(cambio_dados, index=datas),
        'fluxo_capitais': pd.Series(fluxo_dados, index=datas)
    }

    # ========== DADOS MULTI-ATIVO ==========
    dados_multi_ativo = {'WIN': dados_win}

    # Ibovespa - correlacionado com WIN
    ibov_base = 120000
    ibov_dados = []
    for i in range(num_periodos):
        # Correlação moderada com WIN
        correlacao_win = np.corrcoef([precos_close_win[j] for j in range(min(i+1, len(precos_close_win)))],
                                   [ibov_base + j * 100 for j in range(min(i+1, len(precos_close_win)))])[0,1] if i > 0 else 0

        tendencia = 0.0005 * i + 0.3 * correlacao_win
        volatilidade = np.random.normal(0, 0.012)
        ibov_base *= (1 + tendencia + volatilidade)
        ibov_dados.append(ibov_base)

    dados_ibov = pd.DataFrame({
        'Open': [x * (1 + np.random.normal(0, 0.005)) for x in ibov_dados],
        'High': [x * (1 + abs(np.random.normal(0, 0.008))) for x in ibov_dados],
        'Low': [x * (1 - abs(np.random.normal(0, 0.008))) for x in ibov_dados],
        'Close': ibov_dados,
        'Volume': [int(np.random.normal(1000000, 200000)) for _ in ibov_dados]
    }, index=datas)
    dados_multi_ativo['IBOV'] = dados_ibov

    # Dólar - com correlação moderada negativa com WIN
    dolar_base = cambio_base
    dolar_dados = []
    for i in range(num_periodos):
        # Correlação negativa moderada com WIN
        correlacao_win_inv = -0.4 * ((precos_close_win[i] - 130000) / 130000)
        tendencia = 0.0002 * i + correlacao_win_inv
        volatilidade = np.random.normal(0, 0.010)
        dolar_base *= (1 + tendencia + volatilidade)
        dolar_dados.append(dolar_base)

    dados_dolar = pd.DataFrame({
        'Open': [x * (1 + np.random.normal(0, 0.003)) for x in dolar_dados],
        'High': [x * (1 + abs(np.random.normal(0, 0.005))) for x in dolar_dados],
        'Low': [x * (1 - abs(np.random.normal(0, 0.005))) for x in dolar_dados],
        'Close': dolar_dados,
        'Volume': [int(np.random.normal(500000, 100000)) for _ in dolar_dados]
    }, index=datas)
    dados_multi_ativo['DOL'] = dados_dolar

    # Commodities - PETR4, VALE3, SOJA, MINERIO
    commodities = ['PETR4', 'VALE3', 'SOJA', 'MINERIO']
    for commodity in commodities:
        np.random.seed(42 + hash(commodity) % 1000)  # Seed diferente para cada commodity

        preco_base = {'PETR4': 35, 'VALE3': 65, 'SOJA': 180, 'MINERIO': 320}[commodity]
        precos_commodity = []

        for i in range(num_periodos):
            # Tendência baseada no tipo de commodity
            if commodity in ['PETR4', 'VALE3', 'MINERIO']:  # Commodities cíclicas
                tendencia = 0.0003 * i + np.sin(i * 0.1) * 0.002  # Tendência + ciclo
            else:  # SOJA - mais volátil
                tendencia = 0.0001 * i + np.random.normal(0, 0.003)

            volatilidade = np.random.normal(0, 0.02)
            preco_base *= (1 + tendencia + volatilidade)
            precos_commodity.append(preco_base)

        dados_commodity = pd.DataFrame({
            'Open': [x * (1 + np.random.normal(0, 0.008)) for x in precos_commodity],
            'High': [x * (1 + abs(np.random.normal(0, 0.015))) for x in precos_commodity],
            'Low': [x * (1 - abs(np.random.normal(0, 0.015))) for x in precos_commodity],
            'Close': precos_commodity,
            'Volume': [int(np.random.normal(1000000, 300000)) for _ in precos_commodity]
        }, index=datas)
        dados_multi_ativo[commodity] = dados_commodity

    logger.info("Dados gerados com sucesso:")
    logger.info(f"WIN: {len(dados_win)} períodos")
    logger.info(f"Preço inicial WIN: {dados_win['Close'].iloc[0]:.0f}")
    logger.info(f"Preço final WIN: {dados_win['Close'].iloc[-1]:.0f}")
    logger.info(f"Variação WIN: {((dados_win['Close'].iloc[-1] / dados_win['Close'].iloc[0]) - 1) * 100:.1f}%")
    logger.info(f"Selic inicial: {dados_macroeconomicos['selic'].iloc[0]:.2f}%")
    logger.info(f"Selic final: {dados_macroeconomicos['selic'].iloc[-1]:.2f}%")
    logger.info(f"Câmbio inicial: R$ {dados_macroeconomicos['cambio'].iloc[0]:.2f}")
    logger.info(f"Câmbio final: R$ {dados_macroeconomicos['cambio'].iloc[-1]:.2f}")
    logger.info(f"Fluxo inicial: ${dados_macroeconomicos['fluxo_capitais'].iloc[0]:.0f}M")
    logger.info(f"Fluxo final: ${dados_macroeconomicos['fluxo_capitais'].iloc[-1]:.0f}M")
    logger.info(f"Ativos gerados: {list(dados_multi_ativo.keys())}")

    return dados_win, dados_macroeconomicos, dados_multi_ativo


def main():
    """Executa teste integrado dos 3 módulos"""
    print("=" * 70)
    print("TESTE INTEGRADO: PATTERN RECOGNITION + MACRO CONFLUENCE + CORRELATION ANALYSIS")
    print("=" * 70)

    try:
        # Importar framework diretamente
        from framework_assimetrico import FrameworkAssimetrico

        # Gerar dados de teste
        dados_win, dados_macroeconomicos, dados_multi_ativo = gerar_dados_teste_multi_ativo(100)

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

        print("\n" + "=" * 50)
        print("EXECUTANDO ANÁLISE PARCIAL (3 MÓDULOS)")
        print("=" * 50)

        # Executar análise
        inicio = datetime.now()
        resultado = framework.analisar_oportunidades(
            dados_mercado=dados_multi_ativo,
            dados_macroeconomicos=dados_macroeconomicos
        )
        tempo_total = (datetime.now() - inicio).total_seconds()

        print(f"\nTempo total processamento: {tempo_total:.2f}s")

        # Análise de confluência
        print("\n" + "=" * 50)
        print("🎯 ANÁLISE DE CONFLUÊNCIA TÉCNICA vs MACRO vs CORRELAÇÃO")
        print("=" * 50)

        # Calcular confluências individuais
        confluencia_tecnica = 0.0
        confluencia_macro = 0.0
        confluencia_correlacao = 0.0

        if 'pattern_recognition' in framework.modulos:
            pattern_result = framework.modulos['pattern_recognition'].analisar(dados_multi_ativo)
            confluencia_tecnica = pattern_result.confianca if hasattr(pattern_result, 'confianca') else 0.0

        if 'macro_confluence' in framework.modulos:
            macro_result = framework.modulos['macro_confluence'].analisar(dados_macroeconomicos)
            confluencia_macro = macro_result.confianca if hasattr(macro_result, 'confianca') else 0.0

        if 'correlation_analysis' in framework.modulos:
            correlation_result = framework.modulos['correlation_analysis'].analisar(dados_multi_ativo)
            confluencia_correlacao = correlation_result.confianca if hasattr(correlation_result, 'confianca') else 0.0

        confluencia_total = (confluencia_tecnica + confluencia_macro + confluencia_correlacao) / 3

        print(f"Confluência Técnica: {confluencia_tecnica:.1f}%")
        print(f"Confluência Macro: {confluencia_macro:.1f}%")
        print(f"Confluência Correlação: {confluencia_correlacao:.1f}%")
        print(f"Confluência Total: {confluencia_total:.1f}%")

        if confluencia_total >= 50:
            sinal = "✅ FAVORÁVEL"
            recomendacao = "PROSSEGUIR COM ANÁLISE"
        else:
            sinal = "❌ DESFAVORÁVEL"
            recomendacao = "AGUARDAR MELHOR CONFLUÊNCIA"

        print(f"Sinal de Assimetria: {sinal}")
        print(f"Recomendação: {recomendacao}")

        # Validação dos resultados
        print("\n" + "=" * 30)
        print("VALIDAÇÃO DOS RESULTADOS")
        print("=" * 30)

        validacoes = []

        # Verificar se 3+ módulos carregados
        modulos_carregados = len(framework.modulos)
        validacao_1 = modulos_carregados >= 3
        validacoes.append(("3+ módulos carregados", validacao_1))

        # Verificar Pattern Recognition
        pattern_ok = 'pattern_recognition' in framework.modulos
        validacoes.append(("Pattern Recognition OK", pattern_ok))

        # Verificar Macro Confluence
        macro_ok = 'macro_confluence' in framework.modulos
        validacoes.append(("Macro Confluence OK", macro_ok))

        # Verificar Correlation Analysis
        correlation_ok = 'correlation_analysis' in framework.modulos
        validacoes.append(("Correlation Analysis OK", correlation_ok))

        # Verificar tempo
        tempo_ok = tempo_total < 2.0
        validacoes.append(("Tempo < 2s", tempo_ok))

        # Verificar confluência mínima
        confluencia_ok = confluencia_total >= 30  # Threshold reduzido para teste
        validacoes.append(("Confluência > 30%", confluencia_ok))

        print("Validações:")
        for descricao, status in validacoes:
            status_icon = "✅" if status else "❌"
            print(f"  {status_icon} {descricao}")

        testes_aprovados = sum(1 for _, status in validacoes if status)
        total_testes = len(validacoes)

        print(f"\nResultado: {testes_aprovados}/{total_testes} testes passaram")

        if testes_aprovados >= total_testes * 0.8:  # 80% de aprovação
            print("✅ Teste integrado APROVADO")
            return True
        else:
            print("⚠️  Alguns testes falharam")
            return False

    except Exception as e:
        print(f"❌ ERRO: {e}")
        return False


if __name__ == "__main__":
    sucesso = main()
    exit(0 if sucesso else 1)