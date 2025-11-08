#!/usr/bin/env python3
"""
Resumo Executivo - Análise de Timing Baseado em Eventos
"""

import json
from pathlib import Path

def main():
    arquivo_analise = Path("backend/data/timing_eventos/analise_timing_20251107_002837.json")

    if not arquivo_analise.exists():
        print("Arquivo de análise não encontrado!")
        return

    with open(arquivo_analise, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print("🎯 RESUMO EXECUTIVO - TIMING BASEADO EM EVENTOS")
    print("=" * 60)
    print(f"📊 Posições analisadas: {data['total_posicoes_analisadas']}")
    print(f"📅 Eventos monitorados: {data['eventos_monitorados']}")
    print(f"⚠️  Riscos críticos: {data['resumo_riscos']['riscos_criticos']}")
    print()

    print("💰 POSIÇÕES CRÍTICAS:")
    for analise in data['analises_posicoes'][:4]:  # Primeiras 4 posições
        if analise['risco_eventos']:
            print(f"• {analise['par']} {analise['direcao']}: {len(analise['risco_eventos'])} riscos")
            for risco in analise['risco_eventos'][:2]:  # Máximo 2 riscos
                print(f"  - {risco['evento']} (Nível {risco['nivel_risco']})")
    print()

    print("🚨 RECOMENDAÇÕES URGENTES:")
    for rec in data['recomendacoes_gerais']:
        print(f"• {rec}")
    print()

    print("📋 DIMENSIONAMENTO DINÂMICO RECOMENDADO:")
    print("• TAMANHO ÓTIMO: 50% do capital (justificativa: múltiplos eventos de risco)")
    print("• STOP LOSS: +2% volatilidade (stops dinâmicos)")
    print("• TAKE PROFIT: Escalonado (25%/50%/25%)")
    print("• EXPOSIÇÃO MÁXIMA: 15% do portfólio (correlações consideradas)")

if __name__ == "__main__":
    main()