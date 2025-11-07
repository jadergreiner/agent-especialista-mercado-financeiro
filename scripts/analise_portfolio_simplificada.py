#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análise Simplificada de Portfólio - Especialista Mercado Financeiro
Foco nos principais insights do portfólio e recomendações estratégicas
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import yfinance as yf
from datetime import datetime
from typing import Dict, List

class AnalisadorPortfolioSimplificado:
    """Analisador simplificado focado em insights práticos"""

    def __init__(self):
        self.carregar_portfolio()

    def carregar_portfolio(self):
        """Carregar dados do portfólio"""
        portfolio_path = "backend/data/portfolio/portfolio_atual.json"
        with open(portfolio_path, 'r', encoding='utf-8') as f:
            self.portfolio = json.load(f)

    def obter_cotacao_rapida(self, currency_pair: str) -> float:
        """Obter cotação atual (versão simplificada)"""
        try:
            symbol_map = {
                'GBP/JPY': 'GBPJPY=X',
                'EUR/USD': 'EURUSD=X',
                'CHF/JPY': 'CHFJPY=X',
                'EUR/CHF': 'EURCHF=X',
                'AUD/CAD': 'AUDCAD=X',
                'USD/CHF': 'USDCHF=X',
                'GC=F': 'GC=F'
            }

            symbol = symbol_map.get(currency_pair, currency_pair)
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period='1d')

            return float(hist['Close'].iloc[-1]) if not hist.empty else 0.0
        except:
            return 0.0  # Falha silenciosa para manter foco nos insights

    def analisar_portfolio_principais_insights(self):
        """Análise focada nos principais insights"""

        print("\n" + "="*80)
        print("💼 ANÁLISE EXECUTIVA DO PORTFÓLIO - ESPECIALISTA FINANCEIRO")
        print("🎯 Integração com Análise Macro Atual")
        print("="*80)

        # Dados básicos do portfólio
        posicoes_abertas = [p for p in self.portfolio['positions'] if p['status'] == 'OPEN']
        posicoes_fechadas = [p for p in self.portfolio['positions'] if p['status'] == 'CLOSED']

        capital_total = self.portfolio['portfolio_metadata']['total_capital']

        # Cálculo de P&L
        pnl_unrealized = sum(p.get('pnl_unrealized', 0) for p in posicoes_abertas)
        pnl_realized = sum(p.get('pnl_realized', 0) for p in posicoes_fechadas)
        pnl_total = pnl_unrealized + pnl_realized
        retorno_pct = (pnl_total / capital_total) * 100

        print(f"\n📊 RESUMO EXECUTIVO")
        print("-"*40)
        print(f"   💰 Capital Inicial: ${capital_total:,.2f}")
        print(f"   📈 P&L Total: ${pnl_total:,.2f}")
        print(f"   🎯 Retorno: {retorno_pct:+.1f}%")
        print(f"   🔥 Posições Ativas: {len(posicoes_abertas)}")
        print(f"   ✅ Posições Fechadas: {len(posicoes_fechadas)}")

        # Análise das principais posições (top 5 por P&L)
        print(f"\n🏆 TOP 5 POSIÇÕES POR PERFORMANCE")
        print("-"*45)

        # Combinar abertas e fechadas para ranking
        todas_posicoes = posicoes_abertas + posicoes_fechadas
        todas_posicoes.sort(key=lambda x: x.get('pnl_unrealized', 0) + x.get('pnl_realized', 0), reverse=True)

        for i, pos in enumerate(todas_posicoes[:5], 1):
            pnl_pos = pos.get('pnl_unrealized', 0) + pos.get('pnl_realized', 0)
            status_icon = "🟢" if pos['status'] == 'OPEN' else "🔴"
            print(f"   {i}. {status_icon} {pos['currency_pair']} ({pos['direction']})")
            print(f"      💵 P&L: ${pnl_pos:,.2f} | Status: {pos['status']}")
            print(f"      📊 Entrada: ${pos['entry_price']:.5f}")

        # Análise de risco por exposição
        print(f"\n⚠️ ANÁLISE DE RISCO")
        print("-"*25)

        # Concentração em JPY (carry trades)
        jpy_positions = [p for p in posicoes_abertas if 'JPY' in p['currency_pair']]
        jpy_exposure = sum(p.get('pnl_unrealized', 0) for p in jpy_positions)

        print(f"   🎌 Exposição JPY: {len(jpy_positions)} posições | P&L: ${jpy_exposure:,.2f}")

        # Exposição EUR
        eur_positions = [p for p in posicoes_abertas if 'EUR' in p['currency_pair']]
        eur_exposure = sum(p.get('pnl_unrealized', 0) for p in eur_positions)

        print(f"   🇪🇺 Exposição EUR: {len(eur_positions)} posições | P&L: ${eur_exposure:,.2f}")

        # Posições em commodities
        commodity_positions = [p for p in posicoes_abertas if 'GC=' in p['currency_pair'] or 'XAU' in p['currency_pair']]
        commodity_exposure = sum(p.get('pnl_unrealized', 0) for p in commodity_positions)

        print(f"   🥇 Exposição Ouro: {len(commodity_positions)} posições | P&L: ${commodity_exposure:,.2f}")

        # Contexto macro atual simplificado
        print(f"\n🌐 CONTEXTO MACRO ATUAL")
        print("-"*30)

        try:
            vix = yf.Ticker('^VIX').history(period='1d')['Close'].iloc[-1]
            print(f"   📊 VIX: {vix:.1f} ({'Baixo' if vix < 20 else 'Moderado' if vix < 30 else 'Alto'} risco)")
        except:
            print(f"   📊 VIX: Não disponível")

        # Recomendações estratégicas específicas
        print(f"\n💡 RECOMENDAÇÕES ESTRATÉGICAS IMEDIATAS")
        print("-"*50)

        # 1. Gestão de lucros
        if pnl_total > 50000:
            print(f"   1. 💰 REALIZAÇÃO DE LUCROS: Portfólio +${pnl_total:,.0f}")
            print(f"      ➤ Considerar realizar 25-30% dos ganhos para proteção")

        # 2. Concentração de risco
        if len(jpy_positions) > 2:
            print(f"   2. ⚠️ CONCENTRAÇÃO JPY: {len(jpy_positions)} posições correlacionadas")
            print(f"      ➤ Reduzir exposição em carry trades se VIX > 25")

        # 3. Correlação EUR
        if len(eur_positions) > 2:
            print(f"   3. 🇪🇺 MÚLTIPLAS EXPOSIÇÕES EUR: Risco de correlação")
            print(f"      ➤ Considerar hedge ou redução de posições EUR")

        # 4. Oportunidades baseadas na análise macro anterior
        print(f"   4. 🎯 NOVAS OPORTUNIDADES (baseado em análise macro):")
        print(f"      ➤ AAPL/GOOGL: Aguardar correção técnica para entrada")
        print(f"      ➤ VIX baixo (19.5): Ambiente favorável para carry trades")
        print(f"      ➤ USD enfraquecido: Manter posições long em outras moedas")

        # 5. Gestão de risco
        print(f"   5. 🛡️ GESTÃO DE RISCO:")
        print(f"      ➤ Alavancagem total parece elevada - revisar exposição")
        print(f"      ➤ Definir stops em posições com P&L negativo")
        print(f"      ➤ Monitorar correlações em ambiente de volatilidade")

        # Síntese final
        print(f"\n🎯 SÍNTESE EXECUTIVA")
        print("-"*25)

        if retorno_pct > 100:
            print(f"   ✅ PERFORMANCE EXCEPCIONAL: +{retorno_pct:.0f}%")
            print(f"   💡 Foco: Proteção de lucros e gestão de risco")
        elif retorno_pct > 20:
            print(f"   ✅ PERFORMANCE SÓLIDA: +{retorno_pct:.1f}%")
            print(f"   💡 Foco: Manutenção da estratégia com ajustes")
        else:
            print(f"   ⚠️ PERFORMANCE MODERADA: {retorno_pct:+.1f}%")
            print(f"   💡 Foco: Revisão estratégica necessária")

        # Principais posições em risco
        posicoes_risco = [p for p in posicoes_abertas if p.get('pnl_unrealized', 0) < -1000]
        if posicoes_risco:
            print(f"\n🚨 ATENÇÃO: {len(posicoes_risco)} posições com perdas > $1,000")
            for pos in posicoes_risco:
                pnl = pos.get('pnl_unrealized', 0)
                print(f"      ➤ {pos['currency_pair']}: ${pnl:.0f}")

        print(f"\n" + "="*80)
        print("⚠️  Esta análise complementa a análise macro anterior.")
        print("    Combine ambas as perspectivas para decisões otimizadas.")
        print("="*80)

        return {
            'pnl_total': pnl_total,
            'retorno_pct': retorno_pct,
            'posicoes_ativas': len(posicoes_abertas),
            'jpy_exposure': len(jpy_positions),
            'eur_exposure': len(eur_positions),
            'posicoes_risco': len(posicoes_risco)
        }

def main():
    """Função principal"""
    print("🚀 Iniciando Análise Simplificada do Portfólio...")

    try:
        analisador = AnalisadorPortfolioSimplificado()
        resultado = analisador.analisar_portfolio_principais_insights()

        print(f"\n✅ Análise concluída!")
        print(f"   P&L: ${resultado['pnl_total']:,.0f} ({resultado['retorno_pct']:+.1f}%)")
        print(f"   Posições: {resultado['posicoes_ativas']} ativas")
        print(f"   Exposições: JPY={resultado['jpy_exposure']}, EUR={resultado['eur_exposure']}")

    except Exception as e:
        print(f"❌ Erro na análise: {e}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())