#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Busca dados de correlação para análise do WIN
"""
import yfinance as yf
from datetime import datetime

print("=" * 70)
print("CORRELAÇÕES WIN - 06/11/2025")
print("=" * 70)

# 1. USD/BRL (correlação inversa com WIN)
print("\n1. USD/BRL (DOL) - Correlação INVERSA com WIN:")
try:
    dol = yf.Ticker('USDBRL=X')
    dol_data = dol.history(period='5d')
    if len(dol_data) >= 2:
        ontem = dol_data["Close"].iloc[-2]
        atual = dol_data["Close"].iloc[-1]
        var_dol = ((atual / ontem) - 1) * 100
        print(f"   Ontem: R$ {ontem:.4f}")
        print(f"   Atual: R$ {atual:.4f}")
        print(f"   Variação: {var_dol:+.2f}%")
        if var_dol < -0.3:
            print("   ✅ DOL CAINDO → Favorece COMPRA WIN")
        elif var_dol > 0.3:
            print("   ⚠️ DOL SUBINDO → Favorece VENDA WIN")
        else:
            print("   ⚪ DOL NEUTRO")
    else:
        print("   ⚠️ Dados insuficientes")
except Exception as e:
    print(f"   ❌ Erro: {e}")

# 2. S&P 500 Futuro (correlação direta com WIN)
print("\n2. S&P 500 Futuro (ES) - Correlação DIRETA com WIN:")
try:
    sp = yf.Ticker('ES=F')
    sp_data = sp.history(period='5d')
    if len(sp_data) >= 2:
        ontem = sp_data["Close"].iloc[-2]
        atual = sp_data["Close"].iloc[-1]
        var_sp = ((atual / ontem) - 1) * 100
        print(f"   Ontem: {ontem:.2f}")
        print(f"   Atual: {atual:.2f}")
        print(f"   Variação: {var_sp:+.2f}%")
        if var_sp > 0.3:
            print("   ✅ S&P SUBINDO → Favorece COMPRA WIN")
        elif var_sp < -0.3:
            print("   ⚠️ S&P CAINDO → Favorece VENDA WIN")
        else:
            print("   ⚪ S&P NEUTRO")
    else:
        print("   ⚠️ Dados insuficientes")
except Exception as e:
    print(f"   ❌ Erro: {e}")

# 3. Petróleo WTI (impacta Petrobras ~10% IBOV)
print("\n3. Petróleo WTI - Impacta Petrobras (~10% IBOV):")
try:
    wti = yf.Ticker('CL=F')
    wti_data = wti.history(period='5d')
    if len(wti_data) >= 2:
        ontem = wti_data["Close"].iloc[-2]
        atual = wti_data["Close"].iloc[-1]
        var_wti = ((atual / ontem) - 1) * 100
        print(f"   Ontem: $ {ontem:.2f}")
        print(f"   Atual: $ {atual:.2f}")
        print(f"   Variação: {var_wti:+.2f}%")
        if var_wti > 1.0:
            print("   ✅ WTI SUBINDO → Suporte ao WIN")
        elif var_wti < -1.0:
            print("   ⚠️ WTI CAINDO → Pressão no WIN")
        else:
            print("   ⚪ WTI NEUTRO")
    else:
        print("   ⚠️ Dados insuficientes")
except Exception as e:
    print(f"   ❌ Erro: {e}")

# 4. Treasury 10Y (yields altos = dólar forte)
print("\n4. Treasury 10Y - Yields altos = Dólar forte:")
try:
    treasury = yf.Ticker('^TNX')
    treasury_data = treasury.history(period='5d')
    if len(treasury_data) >= 2:
        ontem = treasury_data["Close"].iloc[-2]
        atual = treasury_data["Close"].iloc[-1]
        var_treasury = atual - ontem
        print(f"   Ontem: {ontem:.2f}%")
        print(f"   Atual: {atual:.2f}%")
        print(f"   Variação: {var_treasury:+.2f} bps")
        if var_treasury > 5:
            print("   ⚠️ YIELDS SUBINDO → Dólar forte → Pressão WIN")
        elif var_treasury < -5:
            print("   ✅ YIELDS CAINDO → Dólar fraco → Suporte WIN")
        else:
            print("   ⚪ YIELDS NEUTROS")
    else:
        print("   ⚠️ Dados insuficientes")
except Exception as e:
    print(f"   ❌ Erro: {e}")

print("\n" + "=" * 70)
print("SÍNTESE DE CORRELAÇÕES")
print("=" * 70)
print("Aguardando cálculo baseado nos dados acima...")
