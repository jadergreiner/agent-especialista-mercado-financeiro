# -*- coding: utf-8 -*-
"""
Exemplo de Integração: Correlações no Motor de Backtest

Este módulo demonstra como integrar os 3 pilares de dados (Boletim B3,
Notícias, Correlações) na lógica de decisão do motor_backtest.py.

NÃO EXECUTAR DIRETAMENTE - Este é um exemplo de código para referência.
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple


CAMINHO_DB = Path(__file__).parent / "data" / "recomendacoes.sqlite"


# ============================================================================
# PILAR 1: BOLETIM B3 - MICROESTRUTURA DO MERCADO
# ============================================================================

def verificar_qualidade_mercado_boletim(data: datetime) -> Tuple[bool, str]:
    """
    Verifica se microestrutura permite operação no dia.

    Returns:
        (pode_operar: bool, motivo: str)
    """

    conn = sqlite3.connect(CAMINHO_DB)
    cur = conn.cursor()

    # Buscar boletim do dia
    cur.execute("""
        SELECT volume_total, volume_relativo, liquidez_score
        FROM boletins_diarios
        WHERE DATE(data_pregao) = DATE(?)
    """, (data.isoformat(),))

    resultado = cur.fetchone()
    conn.close()

    if not resultado:
        return (True, "Sem boletim - OK")  # Sem dados, não bloqueia

    volume_total, volume_rel, liquidez = resultado

    # FILTRO: Volume muito baixo (< 50% da média)
    if volume_rel and volume_rel < 0.5:
        return (False, f"Volume baixo: {volume_rel:.2f}x média")

    # FILTRO: Liquidez crítica
    if liquidez and liquidez < 0.3:
        return (False, f"Liquidez crítica: {liquidez:.2f}")

    return (True, "Microestrutura OK")


# ============================================================================
# PILAR 2: NOTÍCIAS - SENTIMENTO DE MERCADO
# ============================================================================

def verificar_sentimento_noticias(data: datetime, horas_lookback: int = 6) -> Tuple[bool, float, str]:
    """
    Verifica sentimento das notícias recentes.

    Returns:
        (pode_operar: bool, score_sentimento: float, motivo: str)
    """

    conn = sqlite3.connect(CAMINHO_DB)
    cur = conn.cursor()

    # Buscar sentimento das últimas N horas
    data_inicio = data - timedelta(hours=horas_lookback)

    cur.execute("""
        SELECT
            AVG(score_sentimento) as sentimento_medio,
            COUNT(*) as total_noticias,
            SUM(CASE WHEN score_sentimento > 0.3 THEN 1 ELSE 0 END) as positivas,
            SUM(CASE WHEN score_sentimento < -0.3 THEN 1 ELSE 0 END) as negativas
        FROM noticias
        WHERE data_publicacao BETWEEN ? AND ?
        AND relevancia >= 0.7
    """, (data_inicio.isoformat(), data.isoformat()))

    resultado = cur.fetchone()
    conn.close()

    if not resultado or not resultado[1]:  # Sem notícias
        return (True, 0.0, "Sem notícias relevantes")

    sentimento, total, positivas, negativas = resultado
    sentimento = sentimento or 0.0

    # FILTRO: Sentimento extremamente negativo
    if sentimento < -0.5:
        return (False, sentimento, f"Sentimento muito negativo: {sentimento:.2f}")

    # FILTRO: Muitas notícias negativas (>70%)
    if total >= 5 and (negativas / total) > 0.7:
        return (False, sentimento, f"70%+ notícias negativas ({negativas}/{total})")

    return (True, sentimento, f"Sentimento: {sentimento:.2f}")


def calcular_multiplicador_sentimento(score: float) -> float:
    """
    Calcula multiplicador de confiança baseado em sentimento.

    Score: -1.0 (muito negativo) a +1.0 (muito positivo)
    Returns: 0.7 a 1.3 (ajuste de target)
    """

    if score > 0.5:  # Muito positivo
        return 1.3
    elif score > 0.2:  # Positivo
        return 1.15
    elif score > -0.2:  # Neutro
        return 1.0
    elif score > -0.5:  # Negativo
        return 0.85
    else:  # Muito negativo
        return 0.7


# ============================================================================
# PILAR 3: CORRELAÇÕES - CONTEXTO MACRO
# ============================================================================

def verificar_condicoes_macro_correlacoes(data: datetime) -> Tuple[bool, Dict, str]:
    """
    Verifica se condições macro permitem operação.

    Returns:
        (pode_operar: bool, variacoes: Dict, motivo: str)
    """

    conn = sqlite3.connect(CAMINHO_DB)
    cur = conn.cursor()

    # Buscar últimas cotações dos ativos críticos
    data_limite = data - timedelta(hours=2)

    cur.execute("""
        SELECT c.simbolo, c.variacao_dia, c.fechamento
        FROM cotacoes_correlacoes c
        INNER JOIN (
            SELECT simbolo, MAX(data_hora) as ultima_data
            FROM cotacoes_correlacoes
            WHERE data_hora BETWEEN ? AND ?
            GROUP BY simbolo
        ) ultimas ON c.simbolo = ultimas.simbolo AND c.data_hora = ultimas.ultima_data
        WHERE c.simbolo IN ('^BVSP', '^GSPC', '^VIX', 'USDBRL=X', 'VALE3.SA', 'PETR4.SA')
    """, (data_limite.isoformat(), data.isoformat()))

    variacoes = {row[0]: row[1] for row in cur.fetchall()}
    conn.close()

    if not variacoes:
        return (True, {}, "Sem dados de correlação - OK")

    # FILTRO: VIX muito alto (pânico)
    vix_var = variacoes.get('^VIX', 0) or 0
    if vix_var > 5.0:
        return (False, variacoes, f"VIX disparando: +{vix_var:.1f}%")

    # FILTRO: Dólar disparando (fuga de capital)
    dolar_var = variacoes.get('USDBRL=X', 0) or 0
    if dolar_var > 2.0:
        return (False, variacoes, f"Dólar disparando: +{dolar_var:.1f}%")

    # FILTRO: S&P caindo forte E IBOV caindo junto
    sp_var = variacoes.get('^GSPC', 0) or 0
    ibov_var = variacoes.get('^BVSP', 0) or 0
    if sp_var < -1.5 and ibov_var < -1.0:
        return (False, variacoes, "S&P e IBOV caindo forte")

    return (True, variacoes, "Macro OK")


def calcular_score_confirmacao_correlacoes(sinal: int, variacoes: Dict) -> float:
    """
    Calcula score de confirmação do sinal pelas correlações.

    Args:
        sinal: +1 (compra) ou -1 (venda)
        variacoes: Dict com variações dos ativos

    Returns:
        Score de 0.5 (nenhuma confirmação) a 1.5 (todas confirmam)
    """

    if not variacoes:
        return 1.0  # Neutro

    confirmacoes = 0
    total = 0

    # Verificar correlações diretas
    ativos_diretos = ['^BVSP', '^GSPC', 'VALE3.SA', 'PETR4.SA']

    for ativo in ativos_diretos:
        if ativo in variacoes and variacoes[ativo] is not None:
            var = variacoes[ativo]

            if sinal > 0:  # Sinal de COMPRA
                if var > 0.2:  # Correlação direta positiva
                    confirmacoes += 1
            else:  # Sinal de VENDA
                if var < -0.2:  # Correlação direta negativa
                    confirmacoes += 1

            total += 1

    # Verificar correlações inversas
    ativos_inversos = ['USDBRL=X', '^VIX']

    for ativo in ativos_inversos:
        if ativo in variacoes and variacoes[ativo] is not None:
            var = variacoes[ativo]

            if sinal > 0:  # Sinal de COMPRA
                if var < -0.2:  # Correlação inversa deve ser negativa
                    confirmacoes += 1
            else:  # Sinal de VENDA
                if var > 0.2:  # Correlação inversa deve ser positiva
                    confirmacoes += 1

            total += 1

    if total == 0:
        return 1.0

    # Score: 0.5 (0% confirmação) a 1.5 (100% confirmação)
    taxa_confirmacao = confirmacoes / total
    return 0.5 + taxa_confirmacao


def calcular_score_macro_geral(variacoes: Dict) -> float:
    """
    Calcula score geral do ambiente macro (-1.0 a +1.0).

    Usado para ajustar target dinamicamente.
    """

    if not variacoes:
        return 0.0

    score = 0.0
    pesos = 0.0

    # Correlações diretas (peso positivo)
    if '^BVSP' in variacoes and variacoes['^BVSP'] is not None:
        score += variacoes['^BVSP'] * 0.4  # IBOV tem peso 40%
        pesos += 0.4

    if '^GSPC' in variacoes and variacoes['^GSPC'] is not None:
        score += variacoes['^GSPC'] * 0.3  # S&P tem peso 30%
        pesos += 0.3

    if 'VALE3.SA' in variacoes and variacoes['VALE3.SA'] is not None:
        score += variacoes['VALE3.SA'] * 0.1
        pesos += 0.1

    if 'PETR4.SA' in variacoes and variacoes['PETR4.SA'] is not None:
        score += variacoes['PETR4.SA'] * 0.1
        pesos += 0.1

    # Correlações inversas (peso negativo)
    if 'USDBRL=X' in variacoes and variacoes['USDBRL=X'] is not None:
        score -= variacoes['USDBRL=X'] * 0.15
        pesos += 0.15

    if '^VIX' in variacoes and variacoes['^VIX'] is not None:
        score -= variacoes['^VIX'] * 0.10
        pesos += 0.10

    if pesos > 0:
        score = score / pesos  # Normalizar

    # Limitar entre -1.0 e +1.0
    return max(-1.0, min(1.0, score))


# ============================================================================
# INTEGRAÇÃO COMPLETA - FLUXO DE DECISÃO
# ============================================================================

def pode_operar_hoje_completo(data: datetime) -> Tuple[bool, str]:
    """
    Verifica se todos os 3 pilares permitem operação.

    Returns:
        (pode_operar: bool, motivo_detalhado: str)
    """

    # PILAR 1: Boletim B3
    pode_boletim, motivo_boletim = verificar_qualidade_mercado_boletim(data)
    if not pode_boletim:
        return (False, f"BOLETIM: {motivo_boletim}")

    # PILAR 2: Notícias
    pode_noticias, score_sent, motivo_noticias = verificar_sentimento_noticias(data)
    if not pode_noticias:
        return (False, f"NOTÍCIAS: {motivo_noticias}")

    # PILAR 3: Correlações
    pode_macro, variacoes, motivo_macro = verificar_condicoes_macro_correlacoes(data)
    if not pode_macro:
        return (False, f"MACRO: {motivo_macro}")

    # Tudo OK
    return (True, f"OK - {motivo_boletim} | {motivo_noticias} | {motivo_macro}")


def calcular_confianca_sinal_completa(
    sinal: int,
    data: datetime
) -> Tuple[float, Dict[str, float]]:
    """
    Calcula confiança completa do sinal usando os 3 pilares.

    Returns:
        (confianca_total: float, detalhes: Dict)
    """

    # Buscar dados de cada pilar
    _, score_sentimento, _ = verificar_sentimento_noticias(data)
    _, variacoes, _ = verificar_condicoes_macro_correlacoes(data)

    # Calcular scores individuais
    mult_sentimento = calcular_multiplicador_sentimento(score_sentimento)
    score_correlacao = calcular_score_confirmacao_correlacoes(sinal, variacoes)

    # Combinar (média ponderada)
    confianca = (mult_sentimento * 0.4) + (score_correlacao * 0.6)

    detalhes = {
        'sentimento': mult_sentimento,
        'correlacao': score_correlacao,
        'combinado': confianca
    }

    return (confianca, detalhes)


def calcular_target_ajustado_completo(
    target_base: int,
    sinal: int,
    data: datetime
) -> Tuple[int, Dict[str, any]]:
    """
    Ajusta target baseado nos 3 pilares.

    Returns:
        (target_ajustado: int, detalhes: Dict)
    """

    # Buscar dados
    _, score_sentimento, _ = verificar_sentimento_noticias(data)
    _, variacoes, _ = verificar_condicoes_macro_correlacoes(data)

    # Calcular multiplicadores
    mult_sentimento = calcular_multiplicador_sentimento(score_sentimento)
    score_macro = calcular_score_macro_geral(variacoes)

    # Macro: -1.0 a +1.0 → 0.7 a 1.3
    mult_macro = 1.0 + (score_macro * 0.3)

    # Combinar multiplicadores (média)
    mult_total = (mult_sentimento + mult_macro) / 2

    # Aplicar no target
    target_ajustado = int(target_base * mult_total)

    detalhes = {
        'mult_sentimento': mult_sentimento,
        'score_macro': score_macro,
        'mult_macro': mult_macro,
        'mult_total': mult_total,
        'target_base': target_base,
        'target_ajustado': target_ajustado
    }

    return (target_ajustado, detalhes)


# ============================================================================
# EXEMPLO DE USO NO MOTOR DE BACKTEST
# ============================================================================

def exemplo_integracao_motor_backtest():
    """
    Pseudocódigo mostrando como integrar no motor_backtest.py
    """

    # No loop principal do backtest:
    for data, preco in dados_historicos:

        # 1. FILTRO PRÉ-OPERAÇÃO (3 pilares)
        pode_operar, motivo = pode_operar_hoje_completo(data)
        if not pode_operar:
            print(f"[{data}] Não operar: {motivo}")
            continue  # Pula o dia

        # 2. GERAÇÃO DE SINAL (estratégia original)
        sinal = estrategia.gerar_sinal(preco)

        if sinal == 0:
            continue  # Sem sinal

        # 3. CONFIRMAÇÃO DO SINAL (correlações)
        confianca, detalhes_conf = calcular_confianca_sinal_completa(sinal, data)

        if confianca < 0.7:  # Baixa confirmação
            print(f"[{data}] Sinal {sinal} com baixa confiança: {confianca:.2f}")
            continue  # Não operar

        # 4. AJUSTE DINÂMICO DE TARGET (sentimento + macro)
        target_base = estrategia.calcular_target(preco)
        target_ajustado, detalhes_target = calcular_target_ajustado_completo(
            target_base, sinal, data
        )

        # 5. EXECUTAR OPERAÇÃO
        print(f"[{data}] Operar {sinal} | Confiança: {confianca:.2f} | " +
              f"Target: {target_base} → {target_ajustado} | {motivo}")

        resultado = executar_operacao(
            data=data,
            sinal=sinal,
            preco_entrada=preco,
            target=target_ajustado,
            stop=estrategia.calcular_stop(preco)
        )


# ============================================================================
# MÉTRICAS DE IMPACTO
# ============================================================================

def comparar_com_sem_pilares(dados_historicos):
    """
    Backtesting comparativo: estratégia pura vs estratégia + 3 pilares.

    Métricas esperadas:
    - Redução de trades ruins: 30-40%
    - Aumento de expectativa: +50-80%
    - Melhoria de Sharpe: +0.3-0.5
    - Redução de drawdown: -30%
    """

    # SEM PILARES (baseline)
    resultados_sem = backtest_simples(dados_historicos)

    # COM PILARES (enhanced)
    resultados_com = backtest_com_pilares(dados_historicos)

    print("\n" + "="*80)
    print("COMPARAÇÃO: SEM PILARES vs COM PILARES")
    print("="*80)

    print(f"\nTrades executados:")
    print(f"  Sem pilares: {resultados_sem['total_trades']}")
    print(f"  Com pilares: {resultados_com['total_trades']} " +
          f"({resultados_com['total_trades'] / resultados_sem['total_trades'] * 100:.1f}%)")

    print(f"\nExpectativa (pts/op):")
    print(f"  Sem pilares: {resultados_sem['expectativa']:+.1f}")
    print(f"  Com pilares: {resultados_com['expectativa']:+.1f} " +
          f"({(resultados_com['expectativa'] / resultados_sem['expectativa'] - 1) * 100:+.1f}%)")

    print(f"\nDrawdown máximo:")
    print(f"  Sem pilares: {resultados_sem['drawdown_max']:.1f}%")
    print(f"  Com pilares: {resultados_com['drawdown_max']:.1f}% " +
          f"({(resultados_com['drawdown_max'] / resultados_sem['drawdown_max'] - 1) * 100:+.1f}%)")

    print(f"\nÍndice de Sharpe:")
    print(f"  Sem pilares: {resultados_sem['sharpe']:.2f}")
    print(f"  Com pilares: {resultados_com['sharpe']:.2f} " +
          f"({resultados_com['sharpe'] - resultados_sem['sharpe']:+.2f})")


if __name__ == "__main__":
    print("="*80)
    print("EXEMPLO DE INTEGRAÇÃO - 3 PILARES NO MOTOR DE BACKTEST")
    print("="*80)
    print()
    print("Este arquivo contém código de exemplo para integração.")
    print("NÃO deve ser executado diretamente.")
    print()
    print("Funções principais:")
    print("  1. pode_operar_hoje_completo() - Filtro pré-operação")
    print("  2. calcular_confianca_sinal_completa() - Confirmação")
    print("  3. calcular_target_ajustado_completo() - Ajuste dinâmico")
    print()
    print("Próximo passo: Integrar no motor_backtest.py")
    print("="*80)
