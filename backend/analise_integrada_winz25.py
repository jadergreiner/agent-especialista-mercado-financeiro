#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análise Integrada Completa WINZ25
Framework Assimétrico + Dados Técnicos + Boletim B3
"""

import sys
import os
sys.path.append('.')

from extrator_boletim_b3_melhorado import extrair_dados_win_boletim_melhorado, analisar_impacto_boletim_melhorado
from framework_assimetrico import FrameworkAssimetrico
import pandas as pd
import yfinance as yf
from datetime import datetime

def main():
    print('🤖 ANÁLISE INTEGRADA COMPLETA WINZ25')
    print('=' * 70)
    print('Framework Assimétrico + Dados Técnicos + Boletim B3')
    print('=' * 70)

    # 1. EXTRAÇÃO DE DADOS DO BOLETIM B3
    print('\n1️⃣ EXTRAÇÃO BOLETIM B3:')
    arquivo_boletim = r'data\boletins_b3\raw\2024-11\BDI_00_20251106.pdf'
    dados_boletim = extrair_dados_win_boletim_melhorado(arquivo_boletim)

    if dados_boletim:
        print('✅ Boletim processado com sucesso')
        analise_boletim = analisar_impacto_boletim_melhorado(dados_boletim)
    else:
        print('❌ Erro no processamento do boletim')
        analise_boletim = {'score': 0, 'recomendacao_win': 'N/A'}

    # 2. COLETA DE DADOS DE MERCADO ATUAIS
    print('\n2️⃣ COLETA DADOS MERCADO:')
    dados_mercado = {}
    ativos = ['WIN', 'IBOV', 'DOL']

    for ativo in ativos:
        try:
            ticker = {'WIN': '^BVSP', 'IBOV': '^BVSP', 'DOL': 'USDBRL=X'}[ativo]
            data = yf.download(ticker, period='3mo', interval='1d')
            if not data.empty:
                dados_mercado[ativo] = data
                print(f'   ✅ {ativo}: {len(data)} dias coletados')
            else:
                print(f'   ❌ {ativo}: Sem dados')
        except Exception as e:
            print(f'   ❌ {ativo}: Erro - {e}')

    # 3. ANÁLISE TÉCNICA BÁSICA
    print('\n3️⃣ ANÁLISE TÉCNICA BÁSICA:')
    win_data = dados_mercado.get('WIN', pd.DataFrame())
    rsi_atual = 50  # default

    if not win_data.empty:
        preco_atual = float(win_data['Close'].iloc[-1])

        # Pivot points
        high = float(win_data['High'].iloc[-1])
        low = float(win_data['Low'].iloc[-1])
        close = float(win_data['Close'].iloc[-1])
        pivot = (high + low + close) / 3
        r1 = 2 * pivot - low
        s1 = 2 * pivot - high

        print(f'   Preço Atual WIN: {preco_atual:,.0f}')
        print(f'   Pivot: {pivot:,.0f}')
        print(f'   Resistência 1: {r1:,.0f}')
        print(f'   Suporte 1: {s1:,.0f}')

        # RSI
        if len(win_data) >= 14:
            delta = win_data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            rsi_atual = float(rsi.iloc[-1]) if not rsi.empty else 50.0
            print(f'   RSI: {rsi_atual:.1f}')

            if rsi_atual > 70:
                print('   📊 RSI: SOBRECOMPRADO')
            elif rsi_atual < 30:
                print('   📊 RSI: SOBREVENDIDO')
            else:
                print('   📊 RSI: NEUTRO')

        # Posição vs pivot
        if preco_atual > pivot:
            print('   📈 Posição: ACIMA do pivot (vies bullish)')
        else:
            print('   📉 Posição: ABAIXO do pivot (vies bearish)')

    # 4. EXECUÇÃO DO FRAMEWORK ASSIMÉTRICO
    print('\n4️⃣ FRAMEWORK ASSIMÉTRICO:')
    framework = FrameworkAssimetrico()
    resultado = framework.analisar_oportunidades(dados_mercado)

    print(f'   Status: {resultado.status}')
    print(f'   Setups identificados: {len(resultado.setups_identificados)}')
    print(f'   Tempo processamento: {resultado.tempo_processamento:.2f}s')

    # 5. ANÁLISE INTEGRADA E RECOMENDAÇÃO
    print('\n5️⃣ ANÁLISE INTEGRADA WINZ25:')
    print('=' * 50)

    # Dados do boletim
    if dados_boletim:
        print('📊 DADOS BOLETIM B3:')
        if dados_boletim.get('win_preco_liquidacao'):
            print(f'   WIN Liquidação: {dados_boletim["win_preco_liquidacao"]:,.0f} pts')
        if dados_boletim.get('win_volume_financeiro'):
            print(f'   Volume WIN: R$ {dados_boletim["win_volume_financeiro"]:,.0f}')
        if dados_boletim.get('taxa_cambio_cupom'):
            print(f'   Câmbio: R$ {dados_boletim["taxa_cambio_cupom"]:.4f}')
        print(f'   Score Boletim: {analise_boletim["score"]}')
        print(f'   Recomendação Boletim: {analise_boletim["recomendacao_win"]}')

    # Framework
    print('\n🤖 FRAMEWORK ASSIMÉTRICO:')
    if resultado.setups_identificados:
        for i, setup in enumerate(resultado.setups_identificados[:2]):
            print(f'   Setup {i+1}: {setup.direcao} (Score: {setup.pontuacao_assimetria:.1f})')
    else:
        print('   Nenhum setup identificado')

    # Análise técnica
    print('\n📈 ANÁLISE TÉCNICA:')
    if not win_data.empty:
        status_rsi = "SOBRECOMPRADO" if rsi_atual > 70 else "SOBREVENDIDO" if rsi_atual < 30 else "NEUTRO"
        print(f'   RSI: {rsi_atual:.1f} ({status_rsi})')
        posicao_pivot = "ACIMA" if preco_atual > pivot else "ABAIXO"
        print(f'   Posição vs Pivot: {posicao_pivot}')

    # RECOMENDAÇÃO FINAL
    print('\n🎯 RECOMENDAÇÃO FINAL WINZ25:')
    print('=' * 50)

    # Lógica de decisão integrada
    score_final = 0
    fatores_decisao = []

    # Fator 1: Boletim B3
    if analise_boletim['score'] <= -2:
        score_final -= 2
        fatores_decisao.append('Boletim B3 negativo (-2)')
    elif analise_boletim['score'] >= 2:
        score_final += 2
        fatores_decisao.append('Boletim B3 positivo (+2)')
    else:
        fatores_decisao.append('Boletim B3 neutro (0)')

    # Fator 2: RSI
    if rsi_atual > 70:
        score_final -= 1
        fatores_decisao.append('RSI sobrecomprado (-1)')
    elif rsi_atual < 30:
        score_final += 1
        fatores_decisao.append('RSI sobrevendido (+1)')
    else:
        fatores_decisao.append('RSI neutro (0)')

    # Fator 3: Framework
    if resultado.setups_identificados:
        melhor_setup = max(resultado.setups_identificados, key=lambda x: x.pontuacao_assimetria)
        if melhor_setup.direcao == 'LONG' and melhor_setup.pontuacao_assimetria > 65:
            score_final += 1
            fatores_decisao.append('Framework indica LONG (+1)')
        elif melhor_setup.direcao == 'SHORT' and melhor_setup.pontuacao_assimetria > 65:
            score_final -= 1
            fatores_decisao.append('Framework indica SHORT (-1)')
        else:
            fatores_decisao.append('Framework inconclusivo (0)')
    else:
        fatores_decisao.append('Framework sem setups (0)')

    # Fator 4: Posição técnica
    if not win_data.empty:
        if preco_atual < pivot and rsi_atual > 70:
            score_final -= 1
            fatores_decisao.append('Confluência bearish (-1)')
        elif preco_atual > pivot and rsi_atual < 30:
            score_final += 1
            fatores_decisao.append('Confluência bullish (+1)')

    print(f'Score Final: {score_final}')
    print('\nFatores de Decisão:')
    for fator in fatores_decisao:
        print(f'   • {fator}')

    print('\n' + '='*50)
    if score_final >= 2:
        print('🟢 RECOMENDAÇÃO: LONG no WINZ25')
        print('   Entrada: Próximo suporte ou pullback')
        print('   Alvo: Resistência 156.000-158.000')
        print('   Stop: Suporte 150.000')
    elif score_final <= -2:
        print('🔴 RECOMENDAÇÃO: SHORT no WINZ25')
        print('   Entrada: Próxima resistência ou rally')
        print('   Alvo: Suporte 148.000-146.000')
        print('   Stop: Resistência 156.000')
    else:
        print('🟡 RECOMENDAÇÃO: AGUARDAR')
        print('   Sinais não conclusivos - aguardar melhor configuração')

    print('\n⚠️  CONSIDERAÇÕES WINZ25:')
    print('   • Vencimento dezembro 2025 (~1 mês)')
    print('   • Custo carregamento: R$ 300-500/dia por contrato')
    print('   • Volume B3: Alto liquidez')
    print('   • Gap risco: Monitorar abertura')
    print('   • Stop Loss: Mínimo 1% (R$ 1.500-2.000)')

    print('\n📅 Data da Análise: ' + datetime.now().strftime('%d/%m/%Y %H:%M'))

if __name__ == '__main__':
    main()