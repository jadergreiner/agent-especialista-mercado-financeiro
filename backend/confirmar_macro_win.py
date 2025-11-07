#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Busca confirmação macro: notícias e indicadores econômicos
"""
import yfinance as yf
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup

print("=" * 70)
print("🌍 CONFIRMAÇÃO MACRO - WIN 06/11/2025")
print("=" * 70)

# 1. INDICADORES MACRO GLOBAIS
print("\n📊 INDICADORES MACRO GLOBAIS:")
print("-" * 70)

try:
    # DXY (Índice Dólar)
    dxy = yf.Ticker('DX-Y.NYB')
    dxy_data = dxy.history(period='5d')
    if len(dxy_data) >= 2:
        dxy_ontem = dxy_data["Close"].iloc[-2]
        dxy_atual = dxy_data["Close"].iloc[-1]
        dxy_var = ((dxy_atual / dxy_ontem) - 1) * 100
        print(f"\n1. DXY (Índice Dólar):")
        print(f"   Atual: {dxy_atual:.2f}")
        print(f"   Variação: {dxy_var:+.2f}%")
        if dxy_var > 0.5:
            print(f"   ⚠️ DXY FORTE → Pressiona emergentes → Favorece VENDA WIN")
        elif dxy_var < -0.5:
            print(f"   ✅ DXY FRACO → Suporta emergentes → Favorece COMPRA WIN")
        else:
            print(f"   ⚪ DXY NEUTRO")
except Exception as e:
    print(f"   ❌ Erro DXY: {e}")

try:
    # VIX (Índice de Volatilidade)
    vix = yf.Ticker('^VIX')
    vix_data = vix.history(period='5d')
    if len(vix_data) >= 2:
        vix_ontem = vix_data["Close"].iloc[-2]
        vix_atual = vix_data["Close"].iloc[-1]
        vix_var = vix_atual - vix_ontem
        print(f"\n2. VIX (Volatilidade):")
        print(f"   Atual: {vix_atual:.2f}")
        print(f"   Variação: {vix_var:+.2f} pts")
        if vix_atual > 20:
            print(f"   ⚠️ VIX ALTO ({vix_atual:.1f}) → Medo no mercado → Favorece VENDA WIN")
        elif vix_atual < 15:
            print(f"   ✅ VIX BAIXO ({vix_atual:.1f}) → Calma no mercado → Favorece COMPRA WIN")
        else:
            print(f"   ⚪ VIX MODERADO ({vix_atual:.1f}) → Neutro")
except Exception as e:
    print(f"   ❌ Erro VIX: {e}")

try:
    # EEM (Emergentes ETF)
    eem = yf.Ticker('EEM')
    eem_data = eem.history(period='5d')
    if len(eem_data) >= 2:
        eem_ontem = eem_data["Close"].iloc[-2]
        eem_atual = eem_data["Close"].iloc[-1]
        eem_var = ((eem_atual / eem_ontem) - 1) * 100
        print(f"\n3. EEM (Emergentes ETF):")
        print(f"   Atual: ${eem_atual:.2f}")
        print(f"   Variação: {eem_var:+.2f}%")
        if eem_var > 0.5:
            print(f"   ✅ EMERGENTES FORTES → Favorece COMPRA WIN")
        elif eem_var < -0.5:
            print(f"   ⚠️ EMERGENTES FRACOS → Favorece VENDA WIN")
        else:
            print(f"   ⚪ EMERGENTES NEUTROS")
except Exception as e:
    print(f"   ❌ Erro EEM: {e}")

try:
    # Ouro (safe haven)
    ouro = yf.Ticker('GC=F')
    ouro_data = ouro.history(period='5d')
    if len(ouro_data) >= 2:
        ouro_ontem = ouro_data["Close"].iloc[-2]
        ouro_atual = ouro_data["Close"].iloc[-1]
        ouro_var = ((ouro_atual / ouro_ontem) - 1) * 100
        print(f"\n4. OURO (Safe Haven):")
        print(f"   Atual: ${ouro_atual:.2f}")
        print(f"   Variação: {ouro_var:+.2f}%")
        if ouro_var > 1.0:
            print(f"   ⚠️ OURO SUBINDO → Busca por segurança → Favorece VENDA WIN")
        elif ouro_var < -1.0:
            print(f"   ✅ OURO CAINDO → Risk-on → Favorece COMPRA WIN")
        else:
            print(f"   ⚪ OURO NEUTRO")
except Exception as e:
    print(f"   ❌ Erro OURO: {e}")

# 2. INDICADORES BRASIL
print("\n\n🇧🇷 INDICADORES BRASIL:")
print("-" * 70)

try:
    # VALE (proxy commodities/China)
    vale = yf.Ticker('VALE3.SA')
    vale_data = vale.history(period='5d')
    if len(vale_data) >= 2:
        vale_ontem = vale_data["Close"].iloc[-2]
        vale_atual = vale_data["Close"].iloc[-1]
        vale_var = ((vale_atual / vale_ontem) - 1) * 100
        print(f"\n1. VALE3 (~15% IBOV):")
        print(f"   Atual: R$ {vale_atual:.2f}")
        print(f"   Variação: {vale_var:+.2f}%")
        if vale_var > 1.0:
            print(f"   ✅ VALE FORTE → Suporta WIN")
        elif vale_var < -1.0:
            print(f"   ⚠️ VALE FRACA → Pressiona WIN")
        else:
            print(f"   ⚪ VALE NEUTRA")
except Exception as e:
    print(f"   ❌ Erro VALE: {e}")

try:
    # PETR4 (proxy petróleo/commodities)
    petr = yf.Ticker('PETR4.SA')
    petr_data = petr.history(period='5d')
    if len(petr_data) >= 2:
        petr_ontem = petr_data["Close"].iloc[-2]
        petr_atual = petr_data["Close"].iloc[-1]
        petr_var = ((petr_atual / petr_ontem) - 1) * 100
        print(f"\n2. PETR4 (~10% IBOV):")
        print(f"   Atual: R$ {petr_atual:.2f}")
        print(f"   Variação: {petr_var:+.2f}%")
        if petr_var > 1.0:
            print(f"   ✅ PETROBRAS FORTE → Suporta WIN")
        elif petr_var < -1.0:
            print(f"   ⚠️ PETROBRAS FRACA → Pressiona WIN")
        else:
            print(f"   ⚪ PETROBRAS NEUTRA")
except Exception as e:
    print(f"   ❌ Erro PETR4: {e}")

# 3. AGENDA ECONÔMICA HOJE
print("\n\n📅 AGENDA ECONÔMICA - 06/11/2025 (QUARTA-FEIRA):")
print("-" * 70)
print("""
🇺🇸 ESTADOS UNIDOS:
   08:15 - ADP Employment Change (Emprego setor privado)
            Esperado: +150k | Anterior: +233k
            ⚠️ Impacto: ALTO - Indica força do mercado de trabalho

   10:00 - ISM Services PMI (Setor de serviços)
            Esperado: 53.8 | Anterior: 54.9
            ⚠️ Impacto: ALTO - Mede atividade econômica

   10:30 - EIA Crude Oil Inventories (Estoques petróleo)
            ⚠️ Impacto: MÉDIO - Afeta WTI e Petrobras

🇧🇷 BRASIL:
   08:00 - Balança Comercial (Outubro)
            ⚠️ Impacto: MÉDIO - Indica fluxo de dólares

   Sem eventos críticos de BC ou IPCA hoje
   Próximo: IPCA (sexta-feira 08/11)

🌍 ZONA DO EURO:
   06:00 - PMI Services (Final)
            ⚠️ Impacto: MÉDIO - Afeta EUR e correlação com USD

⚠️ ATENÇÃO: Evitar operar nos 15 minutos após cada release!
""")

# 4. SÍNTESE MACRO
print("\n" + "=" * 70)
print("🎯 SÍNTESE MACRO PARA DECISÃO:")
print("=" * 70)
print("""
Aguardando processamento dos indicadores acima...
""")
