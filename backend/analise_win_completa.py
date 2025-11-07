#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análise WIN completa: Correlações + Modelo Preditivo + Sistema de Pontuação
"""
import sys
from pathlib import Path
from datetime import datetime

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from agents.analisador_win_daytrading import AnalisadorWinDayTrading
from utils.gerenciador_modelos import gerenciador_modelos

print("=" * 70)
print("🎯 ANÁLISE WIN COMPLETA - 06/11/2025")
print("   Abertura: 155.455")
print("=" * 70)

# Contexto de correlações (já coletado)
print("\n📊 CORRELAÇÕES EXTERNAS:")
print("   USD/BRL: 5,3431 (−0,98%) ✅ Favorece COMPRA")
print("   S&P 500: 6.832,50 (+0,11%) ⚪ Neutro")
print("   WTI: $60,11 (+0,86%) ⚪ Suporte leve")
print("   Treasury 10Y: 4,16% (+0,07 bps) ⚪ Neutro")

# Instanciar analisador WIN
print("\n🤖 Iniciando Analisador WIN Day Trading...")
try:
    analisador = AnalisadorWinDayTrading()

    # Executar análise completa
    print("\n🔍 Executando análise completa (7 fases)...")
    resultado = analisador.analisar()

    print("\n" + "=" * 70)
    print("✅ ANÁLISE CONCLUÍDA")
    print("=" * 70)

    # Extrair pontuação macro
    if 'pontuacao' in resultado:
        pontuacao = resultado['pontuacao']
        print(f"\n🎯 PONTUAÇÃO MACRO:")
        print(f"   Saldo Total: {pontuacao.get('saldo_total', 'N/A')}")
        print(f"   Interpretação: {pontuacao.get('interpretacao', 'N/A')}")
        print(f"   Tendência geral: {pontuacao.get('tendencia_geral', 'N/A')}")

    # Extrair recomendação
    if 'plano_trading' in resultado:
        plano = resultado['plano_trading']
        print(f"\n💼 PLANO DE TRADING:")
        print(f"   Recomendação: {plano.get('recomendacao_principal', 'N/A')}")
        print(f"   Confiança: {plano.get('nivel_confianca', 'N/A')}")

        if 'compra' in plano:
            compra = plano['compra']
            print(f"\n   📈 SETUP COMPRA:")
            print(f"      Entrada: {compra.get('entrada', 'N/A')}")
            print(f"      Stop: {compra.get('stop', 'N/A')}")
            print(f"      Alvo 1: {compra.get('alvo_1', 'N/A')}")
            print(f"      R:R: {compra.get('risco_retorno', 'N/A')}")

        if 'venda' in plano:
            venda = plano['venda']
            print(f"\n   📉 SETUP VENDA:")
            print(f"      Entrada: {venda.get('entrada', 'N/A')}")
            print(f"      Stop: {venda.get('stop', 'N/A')}")
            print(f"      Alvo 1: {venda.get('alvo_1', 'N/A')}")
            print(f"      R:R: {venda.get('risco_retorno', 'N/A')}")

    # Análise técnica
    if 'analise_tecnica' in resultado:
        tecnica = resultado['analise_tecnica']
        if 'tendencia' in tecnica:
            tend = tecnica['tendencia']
            print(f"\n📊 ANÁLISE TÉCNICA:")
            print(f"   Tendência curto: {tend.get('curto_prazo', 'N/A')}")
            print(f"   Força: {tend.get('forca', 'N/A')}/10")

        if 'suportes' in tecnica:
            sup = tecnica['suportes']
            print(f"\n   Suportes:")
            print(f"      S1: {sup.get('s1', 'N/A')} - {sup.get('s1_justificativa', '')}")
            print(f"      S2: {sup.get('s2', 'N/A')} - {sup.get('s2_justificativa', '')}")
            print(f"      S3: {sup.get('s3', 'N/A')} - {sup.get('s3_justificativa', '')}")

        if 'resistencias' in tecnica:
            res = tecnica['resistencias']
            print(f"\n   Resistências:")
            print(f"      R1: {res.get('r1', 'N/A')} - {res.get('r1_justificativa', '')}")
            print(f"      R2: {res.get('r2', 'N/A')} - {res.get('r2_justificativa', '')}")
            print(f"      R3: {res.get('r3', 'N/A')} - {res.get('r3_justificativa', '')}")

    print("\n" + "=" * 70)
    print("💡 SÍNTESE COM CORRELAÇÕES:")
    print("=" * 70)
    print("""
    ✅ DOL caindo (−0,98%) é o fator dominante favorecendo COMPRA WIN
    ⚪ S&P fraco (+0,11%) sugere consolidação, aguardar confirmação
    ⚪ WTI leve alta (+0,86%) dá suporte via Petrobras

    📍 VIÉS FINAL: COMPRA (condicional)
    📊 Probabilidade: 55%

    ⚠️  GATILHOS CRÍTICOS:
       - Rompimento 155.700 com volume
       - VWAP ascendente
       - DOL mantém abaixo 5,36
       - S&P não inverte negativo

    🎯 SETUP RECOMENDADO:
       Entrada: 155.700
       Stop: 155.350 (350 pts)
       Alvo 1: 156.400 (700 pts)
       R:R: 2,0

    🚨 INVALIDAÇÃO:
       - DOL acima 5,40
       - S&P abaixo −0,3%
       - WIN perde 155.200 com volume
    """)

    print("=" * 70)
    print("✅ Análise completa disponível")
    print("=" * 70)

except Exception as e:
    print(f"\n❌ Erro na análise: {e}")
    import traceback
    traceback.print_exc()
