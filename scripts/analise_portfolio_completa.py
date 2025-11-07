#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análise Completa de Portfólio - Especialista Mercado Financeiro
Integra análise macro atual com avaliação detalhada do portfólio existente
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import yfinance as yf
from datetime import datetime
import pandas as pd
from typing import Dict, List, Tuple
import logging
from dataclasses import dataclass

@dataclass
class AnalisePortfolio:
    """Estrutura para análise do portfólio"""
    total_posicoes: int
    pnl_total_unrealized: float
    pnl_total_realized: float
    pnl_total: float
    retorno_percentual: float
    capital_total: float
    exposicao_total: float
    maior_ganho: Dict
    maior_perda: Dict
    distribuicao_moedas: Dict
    risco_correlacao: str
    recomendacoes: List[str]

class AnalisadorPortfolioEspecialista:
    """
    Analisador de Portfólio Especialista - Integração Macro + Portfólio
    """

    def __init__(self):
        self.logger = self._setup_logger()
        self.carregar_portfolio()

    def _setup_logger(self) -> logging.Logger:
        """Configurar logger"""
        logger = logging.getLogger('AnalisadorPortfolio')
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%H:%M:%S'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def carregar_portfolio(self):
        """Carregar dados do portfólio"""
        try:
            portfolio_path = "backend/data/portfolio/portfolio_atual.json"
            with open(portfolio_path, 'r', encoding='utf-8') as f:
                self.portfolio = json.load(f)

            self.logger.info("✅ Portfólio carregado com sucesso")
        except Exception as e:
            self.logger.error(f"❌ Erro carregando portfólio: {e}")
            raise

    def obter_cotacao_atual(self, currency_pair: str) -> float:
        """Obter cotação atual do par"""
        try:
            # Mapeamento de símbolos
            symbol_map = {
                'GBP/JPY': 'GBPJPY=X',
                'EUR/USD': 'EURUSD=X',
                'CHF/JPY': 'CHFJPY=X',
                'EUR/CHF': 'EURCHF=X',
                'AUD/CAD': 'AUDCAD=X',
                'USD/CHF': 'USDCHF=X',
                'GC=F': 'GC=F',  # Ouro já está correto
                'BTC/USD': 'BTC-USD'
            }

            symbol = symbol_map.get(currency_pair, currency_pair)
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period='1d')

            if not hist.empty:
                return float(hist['Close'].iloc[-1])
            else:
                self.logger.warning(f"⚠️ Sem dados para {currency_pair}")
                return 0.0

        except Exception as e:
            self.logger.error(f"❌ Erro obtendo cotação {currency_pair}: {e}")
            return 0.0

    def atualizar_precos_portfolio(self):
        """Atualizar preços atuais de todas as posições"""
        self.logger.info("🔄 Atualizando preços do portfólio...")

        for posicao in self.portfolio['positions']:
            if posicao['status'] == 'OPEN':
                currency_pair = posicao['currency_pair']
                preco_atual = self.obter_cotacao_atual(currency_pair)

                if preco_atual > 0:
                    posicao['current_price'] = preco_atual

                    # Recalcular P&L não realizado
                    entry_price = posicao['entry_price']
                    lots = posicao['lots']
                    lot_size = posicao['lot_size']
                    direction = posicao['direction']

                    if direction == 'LONG':
                        pnl = lots * lot_size * (preco_atual - entry_price)
                    else:
                        pnl = lots * lot_size * (entry_price - preco_atual)

                    posicao['pnl_unrealized'] = pnl

                    self.logger.info(f"✅ {currency_pair}: ${preco_atual:.5f} | P&L: ${pnl:.2f}")

    def analisar_portfolio_completo(self) -> AnalisePortfolio:
        """Análise completa do portfólio"""
        self.logger.info("📊 Iniciando análise completa do portfólio...")

        # Atualizar preços primeiro
        self.atualizar_precos_portfolio()

        posicoes_abertas = [p for p in self.portfolio['positions'] if p['status'] == 'OPEN']
        posicoes_fechadas = [p for p in self.portfolio['positions'] if p['status'] == 'CLOSED']

        # Cálculos básicos
        total_posicoes = len(posicoes_abertas)
        pnl_unrealized = sum(p['pnl_unrealized'] for p in posicoes_abertas)
        pnl_realized = sum(p['pnl_realized'] for p in posicoes_fechadas)
        pnl_total = pnl_unrealized + pnl_realized

        capital_total = self.portfolio['portfolio_metadata']['total_capital']
        retorno_pct = (pnl_total / capital_total) * 100

        # Exposição total (valor nocional)
        exposicao_total = 0
        for p in posicoes_abertas:
            valor_nocional = p['lots'] * p['lot_size'] * p['current_price']
            exposicao_total += valor_nocional

        # Maior ganho e perda
        maior_ganho = max(posicoes_abertas, key=lambda x: x['pnl_unrealized'], default={'currency_pair': 'N/A', 'pnl_unrealized': 0})
        maior_perda = min(posicoes_abertas, key=lambda x: x['pnl_unrealized'], default={'currency_pair': 'N/A', 'pnl_unrealized': 0})

        # Distribuição por moedas
        distribuicao_moedas = self._analisar_distribuicao_moedas(posicoes_abertas)

        # Análise de correlação
        risco_correlacao = self._avaliar_risco_correlacao(posicoes_abertas)

        # Recomendações
        recomendacoes = self._gerar_recomendacoes_portfolio(posicoes_abertas, pnl_total, exposicao_total)

        return AnalisePortfolio(
            total_posicoes=total_posicoes,
            pnl_total_unrealized=pnl_unrealized,
            pnl_total_realized=pnl_realized,
            pnl_total=pnl_total,
            retorno_percentual=retorno_pct,
            capital_total=capital_total,
            exposicao_total=exposicao_total,
            maior_ganho=maior_ganho,
            maior_perda=maior_perda,
            distribuicao_moedas=distribuicao_moedas,
            risco_correlacao=risco_correlacao,
            recomendacoes=recomendacoes
        )

    def _analisar_distribuicao_moedas(self, posicoes: List[Dict]) -> Dict:
        """Analisar distribuição por moedas"""
        distribuicao = {}

        for posicao in posicoes:
            pair = posicao['currency_pair']
            direction = posicao['direction']
            valor_nocional = posicao['lots'] * posicao['lot_size'] * posicao['current_price']

            # Extrair moedas do par
            if '/' in pair:
                base_currency = pair.split('/')[0]
                quote_currency = pair.split('/')[1]

                # Ajustar exposição baseado na direção
                if direction == 'LONG':
                    distribuicao[base_currency] = distribuicao.get(base_currency, 0) + valor_nocional
                    distribuicao[quote_currency] = distribuicao.get(quote_currency, 0) - valor_nocional
                else:
                    distribuicao[base_currency] = distribuicao.get(base_currency, 0) - valor_nocional
                    distribuicao[quote_currency] = distribuicao.get(quote_currency, 0) + valor_nocional
            else:
                # Commodities como ouro
                distribuicao[pair] = distribuicao.get(pair, 0) + valor_nocional

        return distribuicao

    def _avaliar_risco_correlacao(self, posicoes: List[Dict]) -> str:
        """Avaliar risco de correlação entre posições"""
        pares = [p['currency_pair'] for p in posicoes]

        # Identificar exposições correlacionadas
        correlacoes_altas = []

        # JPY exposure (carry trades)
        jpy_positions = [p for p in pares if 'JPY' in p]
        if len(jpy_positions) > 1:
            correlacoes_altas.append(f"Múltiplas exposições JPY: {', '.join(jpy_positions)}")

        # EUR exposure
        eur_positions = [p for p in pares if 'EUR' in p]
        if len(eur_positions) > 1:
            correlacoes_altas.append(f"Múltiplas exposições EUR: {', '.join(eur_positions)}")

        # CHF exposure
        chf_positions = [p for p in pares if 'CHF' in p]
        if len(chf_positions) > 1:
            correlacoes_altas.append(f"Múltiplas exposições CHF: {', '.join(chf_positions)}")

        if correlacoes_altas:
            return "RISCO ELEVADO: " + " | ".join(correlacoes_altas)
        else:
            return "RISCO MODERADO: Portfolio bem diversificado"

    def _gerar_recomendacoes_portfolio(self, posicoes: List[Dict], pnl_total: float, exposicao_total: float) -> List[str]:
        """Gerar recomendações específicas para o portfólio"""
        recomendacoes = []

        # Análise de performance
        if pnl_total > 0:
            recomendacoes.append(f"✅ Portfólio rentável: +${pnl_total:,.2f}")
        else:
            recomendacoes.append(f"⚠️ Portfólio em prejuízo: ${pnl_total:,.2f}")

        # Análise de exposição
        capital_total = self.portfolio['portfolio_metadata']['total_capital']
        leverage_ratio = exposicao_total / capital_total

        if leverage_ratio > 5:
            recomendacoes.append("🚨 ATENÇÃO: Alavancagem muito alta, considere reduzir exposição")
        elif leverage_ratio > 2:
            recomendacoes.append("⚠️ Alavancagem moderada, monitorar riscos")
        else:
            recomendacoes.append("✅ Alavancagem conservadora")

        # Análise específica de posições
        for posicao in posicoes:
            pnl = posicao['pnl_unrealized']
            pair = posicao['currency_pair']

            if pnl > 5000:  # Grandes ganhos
                recomendacoes.append(f"💰 {pair}: Considerar realização parcial de lucros (+${pnl:.0f})")
            elif pnl < -2000:  # Grandes perdas
                recomendacoes.append(f"🛑 {pair}: Avaliar stop-loss ou saída (-${abs(pnl):.0f})")

        # Recomendações macro-técnicas
        recomendacoes.append("📊 Integrar análise macro atual para novas posições")
        recomendacoes.append("🎯 Monitorar correlações entre carry trades (JPY)")

        return recomendacoes

    def avaliar_impacto_macro_portfolio(self) -> Dict:
        """Avaliar impacto das condições macro no portfólio atual"""

        # Coletar contexto macro atual (simplificado)
        try:
            vix = yf.Ticker('^VIX').history(period='1d')['Close'].iloc[-1]
            dxy = yf.Ticker('DX-Y.NYB').history(period='1d')['Close'].iloc[-1] if len(yf.Ticker('DX-Y.NYB').history(period='1d')) > 0 else 100

            impactos = {
                'vix_atual': vix,
                'dxy_atual': dxy,
                'impactos_identificados': []
            }

            # Análise de impactos
            if vix > 25:  # Alta volatilidade
                impactos['impactos_identificados'].append("🚨 VIX elevado: Risk-off pode afetar carry trades negativamente")

            if dxy > 105:  # USD muito forte
                impactos['impactos_identificados'].append("💪 USD muito forte: Pressão em posições long de outras moedas")
            elif dxy < 95:  # USD fraco
                impactos['impactos_identificados'].append("📉 USD fraco: Favorável para commodities e carry trades")

            # Impacto específico em JPY positions
            jpy_positions = [p for p in self.portfolio['positions'] if 'JPY' in p['currency_pair'] and p['status'] == 'OPEN']
            if jpy_positions and vix > 20:
                impactos['impactos_identificados'].append("🎌 Posições JPY: Risk-off pode favorecer JPY (safe haven)")

            return impactos

        except Exception as e:
            self.logger.error(f"❌ Erro na análise macro: {e}")
            return {'impactos_identificados': ['Erro coletando dados macro']}

    def gerar_relatorio_completo(self):
        """Gerar relatório completo integrando portfólio + macro"""
        print("\n" + "="*80)
        print("💼 RELATÓRIO COMPLETO - PORTFÓLIO + ANÁLISE MACRO")
        print("🎯 Especialista Mercado Financeiro | Análise Integrada")
        print("="*80)

        # Análise do portfólio
        analise = self.analisar_portfolio_completo()

        print(f"\n📊 RESUMO EXECUTIVO DO PORTFÓLIO")
        print("-"*50)
        print(f"   💰 Capital Total: ${analise.capital_total:,.2f}")
        print(f"   📈 P&L Total: ${analise.pnl_total:,.2f}")
        print(f"   📊 Retorno: {analise.retorno_percentual:+.2f}%")
        print(f"   🎯 Posições Ativas: {analise.total_posicoes}")
        print(f"   💎 Exposição Total: ${analise.exposicao_total:,.2f}")
        print(f"   ⚖️ Alavancagem: {analise.exposicao_total/analise.capital_total:.1f}x")

        print(f"\n🏆 PERFORMANCE DETALHADA")
        print("-"*30)
        print(f"   💚 P&L Não Realizado: ${analise.pnl_total_unrealized:,.2f}")
        print(f"   💙 P&L Realizado: ${analise.pnl_total_realized:,.2f}")
        print(f"   🥇 Maior Ganho: {analise.maior_ganho['currency_pair']} (+${analise.maior_ganho['pnl_unrealized']:.2f})")
        print(f"   🥴 Maior Perda: {analise.maior_perda['currency_pair']} (${analise.maior_perda['pnl_unrealized']:.2f})")

        print(f"\n💱 EXPOSIÇÃO POR MOEDA")
        print("-"*25)
        for moeda, exposicao in analise.distribuicao_moedas.items():
            sinal = "+" if exposicao >= 0 else ""
            print(f"   {moeda}: {sinal}${exposicao:,.0f}")

        print(f"\n🔗 ANÁLISE DE CORRELAÇÃO")
        print("-"*25)
        print(f"   {analise.risco_correlacao}")

        print(f"\n🌐 IMPACTO MACROECONÔMICO")
        print("-"*30)
        impacto_macro = self.avaliar_impacto_macro_portfolio()
        print(f"   VIX Atual: {impacto_macro['vix_atual']:.1f}")
        print(f"   DXY Atual: {impacto_macro['dxy_atual']:.1f}")

        for impacto in impacto_macro['impactos_identificados']:
            print(f"   {impacto}")

        print(f"\n💡 RECOMENDAÇÕES ESTRATÉGICAS")
        print("-"*35)
        for i, rec in enumerate(analise.recomendacoes, 1):
            print(f"   {i}. {rec}")

        # Posições detalhadas
        print(f"\n📋 DETALHAMENTO DAS POSIÇÕES ATIVAS")
        print("-"*40)

        posicoes_abertas = [p for p in self.portfolio['positions'] if p['status'] == 'OPEN']

        for i, pos in enumerate(posicoes_abertas, 1):
            print(f"\n   {i}. 📊 {pos['currency_pair']} ({pos['direction']})")
            print(f"      💰 Entrada: ${pos['entry_price']:.5f} | Atual: ${pos['current_price']:.5f}")
            print(f"      📊 Volume: {pos['lots']} lotes | P&L: ${pos['pnl_unrealized']:,.2f}")
            print(f"      📅 Entrada: {pos['entry_date'][:10]}")
            print(f"      🎯 Estratégia: {pos['strategy']}")

            # Análise individual da posição
            dias_aberta = (datetime.now() - datetime.fromisoformat(pos['entry_date'].replace('Z', '+00:00'))).days
            print(f"      ⏰ Dias em aberto: {dias_aberta}")

            if pos['pnl_unrealized'] > 0:
                print(f"      ✅ Posição lucrativa")
            else:
                print(f"      ⚠️ Posição em prejuízo")

        print(f"\n" + "="*80)
        print("⚠️  DISCLAIMER: Análise para fins educacionais e de acompanhamento.")
        print("    Sempre considere seu perfil de risco antes de tomar decisões.")
        print("="*80)

        return analise

def main():
    """Função principal"""
    print("🚀 Iniciando Análise Completa do Portfólio...")

    try:
        analisador = AnalisadorPortfolioEspecialista()
        analise = analisador.gerar_relatorio_completo()

        print(f"\n✅ Análise completa finalizada!")
        print(f"   Portfólio analisado: {analise.total_posicoes} posições ativas")
        print(f"   P&L Total: ${analise.pnl_total:,.2f} ({analise.retorno_percentual:+.2f}%)")

    except Exception as e:
        print(f"❌ Erro na análise: {e}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())