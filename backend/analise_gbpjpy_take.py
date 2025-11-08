"""
Análise Enriquecida - GBP/JPY LONG - Determinação de TAKE PROFIT
Baseado em Níveis Técnicos de Alta Precisão
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def calcular_niveis_gbpjpy():
    """Calcular níveis técnicos críticos para GBP/JPY"""

    print("="*80)
    print("🎯 ANÁLISE TÉCNICA ENRIQUECIDA - GBP/JPY LONG")
    print("="*80)
    print()

    # Dados do portfolio
    entrada = 190.50
    preco_atual = 201.167
    stop_loss = 185.00
    lucro_atual = 10667.01
    tamanho_posicao = 0.01  # lots

    print("📊 POSIÇÃO ATUAL:")
    print(f"   Entrada: {entrada:.3f}")
    print(f"   Preço Atual: {preco_atual:.3f}")
    print(f"   Stop Loss: {stop_loss:.3f}")
    print(f"   Lucro Não Realizado: ${lucro_atual:,.2f}")
    print(f"   Ganho: +{((preco_atual/entrada - 1)*100):.2f}%")
    print()

    # Carregar dados históricos
    ticker = yf.Ticker('GBPJPY=X')
    dados = ticker.history(period='1y')

    if dados.empty:
        print("❌ Erro ao carregar dados")
        return

    preco_real = dados['Close'].iloc[-1]
    print(f"🔍 Preço Real (Yahoo Finance): {preco_real:.3f}")
    print()

    # === ANÁLISE MULTI-TIMEFRAME ===
    print("="*80)
    print("📈 NÍVEIS TÉCNICOS CRÍTICOS")
    print("="*80)
    print()

    # Máximas e mínimas recentes
    high_5d = dados['High'].tail(5).max()
    low_5d = dados['Low'].tail(5).min()
    high_20d = dados['High'].tail(20).max()
    low_20d = dados['Low'].tail(20).min()
    high_60d = dados['High'].tail(60).max()
    low_60d = dados['Low'].tail(60).min()

    print("🔸 SUPORTE E RESISTÊNCIA POR TIMEFRAME:")
    print(f"   5 Dias:   Máxima {high_5d:.3f}  |  Mínima {low_5d:.3f}")
    print(f"   20 Dias:  Máxima {high_20d:.3f}  |  Mínima {low_20d:.3f}")
    print(f"   60 Dias:  Máxima {high_60d:.3f}  |  Mínima {low_60d:.3f}")
    print()

    # Pivot Points (Clássicos)
    ultimo_dia = dados.iloc[-1]
    high = ultimo_dia['High']
    low = ultimo_dia['Low']
    close = ultimo_dia['Close']

    pp = (high + low + close) / 3
    r1 = 2 * pp - low
    r2 = pp + (high - low)
    r3 = high + 2 * (pp - low)
    s1 = 2 * pp - high
    s2 = pp - (high - low)
    s3 = low - 2 * (high - pp)

    print("🔸 PIVOT POINTS (Sessão Atual):")
    print(f"   R3: {r3:.3f}")
    print(f"   R2: {r2:.3f}")
    print(f"   R1: {r1:.3f}")
    print(f"   PP: {pp:.3f}")
    print(f"   S1: {s1:.3f}")
    print(f"   S2: {s2:.3f}")
    print(f"   S3: {s3:.3f}")
    print()

    # Fibonacci (Retração do último swing)
    fib_high = high_20d
    fib_low = low_20d
    fib_diff = fib_high - fib_low

    fib_1272 = fib_high + fib_diff * 0.272
    fib_1618 = fib_high + fib_diff * 0.618
    fib_2000 = fib_high + fib_diff * 1.0
    fib_2618 = fib_high + fib_diff * 1.618

    print("🔸 FIBONACCI - NÍVEIS DE EXTENSÃO (20 dias):")
    print(f"   Base Swing: {fib_low:.3f} → {fib_high:.3f}")
    print(f"   127.2%: {fib_1272:.3f}")
    print(f"   161.8%: {fib_1618:.3f}  ← TAKE PROFIT CLÁSSICO")
    print(f"   200.0%: {fib_2000:.3f}")
    print(f"   261.8%: {fib_2618:.3f}")
    print()

    # Resistências Psicológicas
    print("🔸 NÍVEIS PSICOLÓGICOS:")
    niveis_psico = [200.00, 202.00, 205.00, 210.00, 215.00, 220.00]
    for nivel in niveis_psico:
        if nivel > preco_atual:
            dist = ((nivel/preco_atual - 1)*100)
            print(f"   {nivel:.2f}  (+{dist:.2f}%)")
    print()

    # Médias Móveis
    sma_20 = dados['Close'].tail(20).mean()
    sma_50 = dados['Close'].tail(50).mean()
    sma_200 = dados['Close'].tail(200).mean()

    print("🔸 MÉDIAS MÓVEIS:")
    print(f"   SMA 20:  {sma_20:.3f}")
    print(f"   SMA 50:  {sma_50:.3f}")
    print(f"   SMA 200: {sma_200:.3f}")
    print()

    # === SUGESTÃO DE TAKE PROFIT ===
    print("="*80)
    print("💡 ANÁLISE DE TAKE PROFIT")
    print("="*80)
    print()

    # Take Profit 1 (Conservador - próximo da resistência imediata)
    take1 = r2  # Resistência R2 dos Pivot Points
    lucro1 = (take1 - entrada) * tamanho_posicao * 100000
    ratio1 = (take1 - entrada) / (entrada - stop_loss)

    # Take Profit 2 (Moderado - Fibonacci 127.2%)
    take2 = fib_1272
    lucro2 = (take2 - entrada) * tamanho_posicao * 100000
    ratio2 = (take2 - entrada) / (entrada - stop_loss)

    # Take Profit 3 (Agressivo - Fibonacci 161.8%)
    take3 = fib_1618
    lucro3 = (take3 - entrada) * tamanho_posicao * 100000
    ratio3 = (take3 - entrada) / (entrada - stop_loss)

    # Take Profit 4 (Muito Agressivo - Máxima 60 dias)
    take4 = high_60d * 1.01  # 1% acima da máxima 60d
    lucro4 = (take4 - entrada) * tamanho_posicao * 100000
    ratio4 = (take4 - entrada) / (entrada - stop_loss)

    print("🎯 CENÁRIOS DE TAKE PROFIT:")
    print()
    print(f"1️⃣ CONSERVADOR - Pivot R2")
    print(f"   Nível: {take1:.3f}")
    print(f"   Lucro Potencial: ${lucro1:,.2f}")
    print(f"   Risco/Recompensa: 1:{ratio1:.2f}")
    print(f"   Distância Atual: +{((take1/preco_atual - 1)*100):.2f}%")
    print(f"   ✅ Executar: {take1 < preco_atual and '50% da posição' or '50% quando atingir'}")
    print()

    print(f"2️⃣ MODERADO - Fibonacci 127.2%")
    print(f"   Nível: {take2:.3f}")
    print(f"   Lucro Potencial: ${lucro2:,.2f}")
    print(f"   Risco/Recompensa: 1:{ratio2:.2f}")
    print(f"   Distância Atual: +{((take2/preco_atual - 1)*100):.2f}%")
    print(f"   ✅ Executar: {take2 < preco_atual and '30% da posição' or '30% quando atingir'}")
    print()

    print(f"3️⃣ AGRESSIVO - Fibonacci 161.8% (CLÁSSICO)")
    print(f"   Nível: {take3:.3f}")
    print(f"   Lucro Potencial: ${lucro3:,.2f}")
    print(f"   Risco/Recompensa: 1:{ratio3:.2f}")
    print(f"   Distância Atual: +{((take3/preco_atual - 1)*100):.2f}%")
    print(f"   ✅ Executar: 20% quando atingir (deixar correr)")
    print()

    print(f"4️⃣ BREAKOUT - Máxima 60d + 1%")
    print(f"   Nível: {take4:.3f}")
    print(f"   Lucro Potencial: ${lucro4:,.2f}")
    print(f"   Risco/Recompensa: 1:{ratio4:.2f}")
    print(f"   Distância Atual: +{((take4/preco_atual - 1)*100):.2f}%")
    print(f"   ✅ Executar: Trailing Stop após romper")
    print()

    # === RECOMENDAÇÃO FINAL ===
    print("="*80)
    print("🏆 RECOMENDAÇÃO FINAL - TAKE PROFIT ESCALONADO")
    print("="*80)
    print()

    # Determinar qual nível usar baseado na posição atual
    if preco_atual > r2:
        print("📍 POSIÇÃO ATUAL: Acima da resistência R2")
        print()
        print("💼 GESTÃO RECOMENDADA:")
        print(f"   1. REALIZAR 50% IMEDIATAMENTE em {preco_atual:.3f}")
        print(f"      → Lucro: ${lucro_atual * 0.5:,.2f}")
        print(f"      → Proteger capital e travar ganho")
        print()
        print(f"   2. TAKE PARCIAL 30% em {take2:.3f} (Fib 127.2%)")
        print(f"      → Distância: +{((take2/preco_atual - 1)*100):.2f}%")
        print()
        print(f"   3. TAKE FINAL 20% em {take3:.3f} (Fib 161.8%)")
        print(f"      → Distância: +{((take3/preco_atual - 1)*100):.2f}%")
        print()
        print(f"   4. TRAILING STOP: Ajustar para {preco_atual - 2.0:.3f}")
        print(f"      → 2.00 pontos abaixo do preço atual")
        print()
        print("⚠️ INVALIDAÇÃO: Fechamento abaixo de 198.00")
        print("   → Realizar 100% e reavaliar")
    else:
        print("📍 POSIÇÃO ATUAL: Entre suporte e resistência")
        print()
        print("💼 GESTÃO RECOMENDADA:")
        print(f"   1. TAKE PARCIAL 50% em {take1:.3f} (Pivot R2)")
        print(f"   2. TAKE PARCIAL 30% em {take2:.3f} (Fib 127.2%)")
        print(f"   3. TAKE FINAL 20% em {take3:.3f} (Fib 161.8%)")
        print()
        print(f"   TRAILING STOP: {preco_atual - 2.0:.3f}")

    print()
    print("="*80)
    print("📊 CONFLUÊNCIA TÉCNICA:")
    print(f"   ✅ Pivot R2: {r2:.3f}")
    print(f"   ✅ Fibonacci 127.2%: {take2:.3f}")
    print(f"   ✅ Resistência Psicológica: 202.00 / 205.00")
    print(f"   ✅ Zona de Consolidação Histórica: 200.00-205.00")
    print("="*80)
    print()

    # Volatilidade
    volatilidade = dados['Close'].pct_change().std() * 100
    atr = dados['High'].sub(dados['Low']).tail(14).mean()

    print("📊 MÉTRICAS DE VOLATILIDADE:")
    print(f"   Volatilidade Diária: {volatilidade:.2f}%")
    print(f"   ATR (14): {atr:.3f} pontos")
    print()

    return {
        'take_conservador': take1,
        'take_moderado': take2,
        'take_agressivo': take3,
        'trailing_stop': preco_atual - 2.0,
        'invalidacao': 198.00
    }

if __name__ == "__main__":
    niveis = calcular_niveis_gbpjpy()
