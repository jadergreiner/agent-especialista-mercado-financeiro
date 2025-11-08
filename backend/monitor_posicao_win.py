#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monitor de Posição WIN - Acompanhamento em Tempo Real
Trader Profissional Day Trade
"""
import yfinance as yf
from datetime import datetime
import time
import sys
import os
from utils.terminal import limpar_tela

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# DADOS DA POSIÇÃO
# Observação: posição day trade encerrada ao final do dia.
# Mantemos o monitor habilitado para contexto macro mesmo sem posição aberta.
CONTRATOS = 0
PRECO_ENTRADA = 0
POSICAO = "FLAT"
VALOR_PONTO = 0.20  # R$ por ponto do WIN

def calcular_resultado(preco_atual):
    """Calcula P&L da posição"""
    if preco_atual <= 0:
        return 0, 0

    pontos = preco_atual - PRECO_ENTRADA
    resultado_total = pontos * CONTRATOS * VALOR_PONTO
    resultado_por_contrato = pontos * VALOR_PONTO

    return resultado_total, pontos

def buscar_cotacao_proxy():
    """Busca cotação via IBOV como proxy"""
    try:
        ibov = yf.Ticker('^BVSP')
        hist = ibov.history(period='1d', interval='1m')
        if len(hist) > 0:
            ultimo = hist['Close'].iloc[-1]
            # Conversão IBOV para WIN (aproximação)
            win_proxy = int(ultimo * 1.012)  # Fator de conversão aproximado
            return win_proxy, True
    except:
        pass
    return 0, False

def definir_niveis_gestao(entrada):
    """Define níveis de stop e alvos"""
    # Baseado na análise anterior
    stop_loss = 154200  # Stop defensivo
    alvo_1 = entrada + 600   # +600 pts (R:R 1:1)
    alvo_2 = entrada + 1200  # +1200 pts (R:R 1:2)
    alvo_3 = entrada + 1800  # +1800 pts (R:R 1:3)

    return {
        'stop': stop_loss,
        'alvo_1': alvo_1,
        'alvo_2': alvo_2,
        'alvo_3': alvo_3
    }

def avaliar_cenario_macro():
    """Avaliação rápida do cenário macro"""
    try:
        # DOL
        dol = yf.Ticker('USDBRL=X')
        hist_dol = dol.history(period='2d')
        dol_var = 0
        if len(hist_dol) >= 2:
            dol_var = ((hist_dol['Close'].iloc[-1]/hist_dol['Close'].iloc[-2])-1)*100

        # S&P
        sp = yf.Ticker('^GSPC')
        hist_sp = sp.history(period='2d')
        sp_var = 0
        if len(hist_sp) >= 2:
            sp_var = ((hist_sp['Close'].iloc[-1]/hist_sp['Close'].iloc[-2])-1)*100

        # VIX
        vix = yf.Ticker('^VIX')
        hist_vix = vix.history(period='2d')
        vix_var = 0
        if len(hist_vix) >= 2:
            vix_var = ((hist_vix['Close'].iloc[-1]/hist_vix['Close'].iloc[-2])-1)*100

        return dol_var, sp_var, vix_var
    except:
        return 0, 0, 0

def main():
    print("🚀 MONITOR DE POSIÇÃO WIN - TRADER PROFISSIONAL")
    print("=" * 60)
    if CONTRATOS > 0 and POSICAO.upper() != "FLAT" and PRECO_ENTRADA > 0:
        print(f"📊 POSIÇÃO: {POSICAO} {CONTRATOS} contratos em {PRECO_ENTRADA:,}")
    else:
        print("📊 POSIÇÃO: FLAT (sem contratos abertos)")
    print("=" * 60)

    # Níveis de gestão somente quando houver posição aberta
    niveis = definir_niveis_gestao(PRECO_ENTRADA) if CONTRATOS > 0 and POSICAO.upper() != "FLAT" and PRECO_ENTRADA > 0 else None

    tentativa = 0

    while True:
        try:
            tentativa += 1
            limpar_tela()

            agora = datetime.now().strftime("%H:%M:%S")

            # Buscar cotação
            win_preco, win_ok = buscar_cotacao_proxy()

            # Calcular resultado
            resultado_total, pontos = calcular_resultado(win_preco) if win_ok else (0, 0)

            # Macro
            dol_var, sp_var, vix_var = avaliar_cenario_macro()

            print("🚀 MONITOR DE POSIÇÃO WIN - TRADER PROFISSIONAL")
            print("=" * 60)
            print(f"⏰ {agora} | Atualização #{tentativa}")

            # Posição
            print(f"\n💰 POSIÇÃO ATUAL:")
            if CONTRATOS > 0 and POSICAO.upper() != "FLAT" and PRECO_ENTRADA > 0:
                print(f"   📈 {POSICAO}: {CONTRATOS} contratos @ {PRECO_ENTRADA:,}")

                if win_ok:
                    cor = "🟢" if pontos >= 0 else "🔴"
                    cor_resultado = "🟢" if resultado_total >= 0 else "🔴"

                    print(f"   💲 WIN Atual: {win_preco:,} {cor} {pontos:+,} pts")
                    print(f"   💵 P&L Total: R$ {resultado_total:+,.2f} {cor_resultado}")
                    # Evita divisão por zero
                    if CONTRATOS > 0:
                        print(f"   📊 P&L/Contrato: R$ {resultado_total/CONTRATOS:+,.2f}")

                    if niveis:
                        # Distâncias dos níveis
                        dist_stop = win_preco - niveis['stop']
                        dist_alvo1 = niveis['alvo_1'] - win_preco
                        dist_alvo2 = niveis['alvo_2'] - win_preco

                        print(f"\n🎯 NÍVEIS DE GESTÃO:")
                        print(f"   🛑 Stop Loss: {niveis['stop']:,} ({dist_stop:+,} pts)")
                        print(f"   🎯 Alvo 1: {niveis['alvo_1']:,} ({dist_alvo1:+,} pts)")
                        print(f"   🎯 Alvo 2: {niveis['alvo_2']:,} ({dist_alvo2:+,} pts)")
                        print(f"   🎯 Alvo 3: {niveis['alvo_3']:,} ({niveis['alvo_3']-win_preco:+,} pts)")

                        # Alertas
                        print(f"\n🔔 ALERTAS:")
                        if win_ok and niveis:
                            if win_preco <= niveis['stop']:
                                print(f"   ❌ STOP LOSS ATINGIDO! ZERAR POSIÇÃO!")
                            elif win_preco >= niveis['alvo_1']:
                                print(f"   ✅ ALVO 1 ATINGIDO! Considerar parcial")
                            elif win_preco >= niveis['alvo_2']:
                                print(f"   ✅ ALVO 2 ATINGIDO! Realizar lucros")
                            elif dist_alvo1 <= 200:
                                print(f"   ⚠️ Próximo do Alvo 1 ({dist_alvo1} pts)")
                            else:
                                print(f"   📊 Posição dentro da gestão normal")
                else:
                    print(f"   ⚠️ WIN: Cotação não disponível (proxy IBOV)")
            else:
                print("   📴 Sem posição aberta (FLAT)")

            # Cenário Macro
            print(f"\n🌍 CENÁRIO MACRO:")
            dol_emoji = "🟢" if dol_var < 0 else "🔴"
            sp_emoji = "🟢" if sp_var > 0 else "🔴"
            vix_emoji = "🟢" if vix_var < 0 else "🔴"

            print(f"   💵 USD/BRL: {dol_var:+.2f}% {dol_emoji}")
            print(f"   📈 S&P 500: {sp_var:+.2f}% {sp_emoji}")
            print(f"   😨 VIX: {vix_var:+.2f}% {vix_emoji}")

            # Avaliação geral
            fatores_positivos = sum([1 for x in [dol_var < 0, sp_var > 0, vix_var < 0] if x])

            if fatores_positivos >= 2:
                print(f"   ✅ Cenário FAVORÁVEL para compra")
            elif fatores_positivos == 1:
                print(f"   ⚪ Cenário NEUTRO")
            else:
                print(f"   ❌ Cenário DESFAVORÁVEL")

            print("=" * 60)
            print(f"🔄 Próxima atualização em 30s | Ctrl+C para sair")

            time.sleep(30)

        except KeyboardInterrupt:
            print(f"\n\n📊 RESUMO FINAL DA OPERAÇÃO:")
            if CONTRATOS > 0 and POSICAO.upper() != "FLAT" and PRECO_ENTRADA > 0 and win_ok:
                print(f"   💰 Última cotação: {win_preco:,}")
                print(f"   📊 Resultado final: R$ {resultado_total:+,.2f}")
                print(f"   📈 Movimento: {pontos:+,} pts")
            else:
                print("   📴 Sem posição aberta no período (FLAT)")
            print(f"\n👋 Monitor encerrado. Boa operação!")
            break
        except Exception as e:
            print(f"\n❌ Erro: {e}")
            print(f"🔄 Tentando novamente em 10s...")
            time.sleep(10)

if __name__ == '__main__':
    main()