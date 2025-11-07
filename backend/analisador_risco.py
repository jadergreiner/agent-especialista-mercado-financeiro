"""
Análise de Risco do Portfolio Forex
==================================

Módulo especializado para cálculo e análise de riscos do portfolio,
incluindo VaR, correlações, concentração e exposição cambial.
Agora com suporte especializado para monitoramento de ouro (XAUUSD).

Autor: Agent Especialista Mercado Financeiro
Data: 06/11/2025
"""

import json
import numpy as np
import yfinance as yf
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import sys
import os

# Adicionar utils ao path para importar feed_resolver
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))
try:
    from feed_resolver import resolver_cotacao_ouro
except ImportError:
    def resolver_cotacao_ouro(ticker):
        return None


class AnalisadorRiscoPortfolio:
    """Analisador de risco completo para portfolio forex"""

    def __init__(self, caminho_portfolio: str):
        """Inicializa o analisador com dados do portfolio"""
        with open(caminho_portfolio, 'r', encoding='utf-8') as arquivo:
            self.portfolio_data = json.load(arquivo)

    def calcular_exposicao_cambial(self) -> Dict[str, float]:
        """Calcula exposição líquida por moeda"""
        exposicao = {}
        capital_total = self.portfolio_data["portfolio_metadata"]["total_capital"]

        for posicao in self.portfolio_data["positions"]:
            if posicao["status"] == "OPEN":
                par = posicao["currency_pair"]
                lots = posicao["lots"]
                lot_size = posicao["lot_size"]
                direction = posicao["direction"]

                if "/" in par:  # Par forex
                    moeda_base, moeda_cotacao = par.split("/")
                    valor_posicao = lots * lot_size * posicao["current_price"]
                    percentual = (valor_posicao / capital_total) * 100

                    if direction == "LONG":
                        exposicao[moeda_base] = exposicao.get(moeda_base, 0) + percentual
                        exposicao[moeda_cotacao] = exposicao.get(moeda_cotacao, 0) - percentual
                    else:  # SHORT
                        exposicao[moeda_base] = exposicao.get(moeda_base, 0) - percentual
                        exposicao[moeda_cotacao] = exposicao.get(moeda_cotacao, 0) + percentual

                elif par in ["XAUUSD", "XAU/USD"]:  # Ouro - tratamento especial
                    # Atualizar cotação de ouro em tempo real
                    cotacao_atual = resolver_cotacao_ouro(par)
                    if cotacao_atual:
                        posicao["current_price"] = cotacao_atual
                        print(f"🥇 Ouro atualizado: {par} = ${cotacao_atual:.2f}")

                    # CORREÇÃO: Para XAUUSD, lot_size = 100 (onças), não 100.000
                    # Cada 0.01 lote = 1 onça de ouro
                    lot_size_ouro = 100  # 100 onças por lote padrão para XAU
                    valor_posicao = lots * lot_size_ouro * posicao["current_price"]
                    percentual = (valor_posicao / capital_total) * 100

                    print(f"🔧 Debug XAU: lots={lots}, lot_size={lot_size_ouro}, preço={posicao['current_price']:.2f}")
                    print(f"🔧 Valor posição XAU: ${valor_posicao:.2f}, Percentual: {percentual:.2f}%")

                    if direction == "LONG":
                        exposicao["XAU"] = exposicao.get("XAU", 0) + percentual
                        exposicao["USD"] = exposicao.get("USD", 0) - percentual
                    else:  # SHORT
                        exposicao["XAU"] = exposicao.get("XAU", 0) - percentual
                        exposicao["USD"] = exposicao.get("USD", 0) + percentual

                else:  # Outras commodities
                    valor_posicao = lots * lot_size * posicao["current_price"]
                    percentual = (valor_posicao / capital_total) * 100
                    exposicao[par] = exposicao.get(par, 0) + percentual

        return exposicao

    def calcular_concentracao_risco(self) -> Dict[str, float]:
        """Analisa concentração de risco por posição"""
        concentracao = {}
        pnl_total = abs(self.portfolio_data["performance"]["total_pnl"])

        for posicao in self.portfolio_data["positions"]:
            if posicao["status"] == "OPEN":
                pnl_posicao = abs(posicao.get("pnl_unrealized", 0))
                if pnl_total > 0:
                    concentracao[posicao["currency_pair"]] = (pnl_posicao / pnl_total) * 100
                else:
                    concentracao[posicao["currency_pair"]] = 0

        return concentracao

    def calcular_risco_drawdown(self) -> Dict[str, float]:
        """Calcula risco potencial de drawdown por posição"""
        riscos_drawdown = {}
        capital_total = self.portfolio_data["portfolio_metadata"]["total_capital"]

        for posicao in self.portfolio_data["positions"]:
            if posicao["status"] == "OPEN" and posicao.get("stop_loss"):
                entry = posicao["entry_price"]
                stop = posicao["stop_loss"]
                lots = posicao["lots"]
                lot_size = posicao["lot_size"]
                direction = posicao["direction"]

                # Calcular perda potencial
                diferenca = abs(entry - stop)
                perda_potencial = lots * lot_size * diferenca

                # Percentual do capital
                percentual_risco = (perda_potencial / capital_total) * 100
                riscos_drawdown[posicao["currency_pair"]] = percentual_risco

        return riscos_drawdown

    def avaliar_correlacao_portfolio(self) -> Dict[str, float]:
        """Avalia correlações entre posições do portfolio"""
        pares = [pos["currency_pair"] for pos in self.portfolio_data["positions"]
                if pos["status"] == "OPEN"]

        correlacoes_criticas = {}

        # Correlações conhecidas de alto risco
        correlacoes_altas = {
            ("GBP/JPY", "CHF/JPY"): 0.85,  # Ambas vs JPY
            ("EUR/USD", "EUR/CHF"): 0.75,   # Ambas com EUR
            ("GBP/JPY", "EUR/CHF"): -0.15,  # Correlação inversa
        }

        for (par1, par2), correlacao in correlacoes_altas.items():
            if par1 in pares and par2 in pares:
                correlacoes_criticas[f"{par1} vs {par2}"] = correlacao

        return correlacoes_criticas

    def calcular_metricas_risco(self) -> Dict[str, any]:
        """Calcula métricas consolidadas de risco"""
        exposicao = self.calcular_exposicao_cambial()
        concentracao = self.calcular_concentracao_risco()
        drawdown_risk = self.calcular_risco_drawdown()
        correlacoes = self.avaliar_correlacao_portfolio()

        # Risco total
        risco_total = sum(pos.get("risk_percentage", 0)
                         for pos in self.portfolio_data["positions"]
                         if pos["status"] == "OPEN")

        # Maior exposição individual
        maior_exposicao = max(abs(exp) for exp in exposicao.values()) if exposicao else 0

        # Maior concentração
        maior_concentracao = max(concentracao.values()) if concentracao else 0

        # Avaliação de risco
        nivel_risco = "BAIXO"
        if risco_total > 10 or maior_exposicao > 50 or maior_concentracao > 40:
            nivel_risco = "ALTO"
        elif risco_total > 5 or maior_exposicao > 30 or maior_concentracao > 25:
            nivel_risco = "MÉDIO"

        return {
            "exposicao_cambial": exposicao,
            "concentracao_posicoes": concentracao,
            "risco_drawdown": drawdown_risk,
            "correlacoes_criticas": correlacoes,
            "risco_total_percentual": round(risco_total, 2),
            "maior_exposicao_individual": round(maior_exposicao, 2),
            "maior_concentracao": round(maior_concentracao, 2),
            "nivel_risco_geral": nivel_risco,
            "posicoes_abertas": len([p for p in self.portfolio_data["positions"] if p["status"] == "OPEN"])
        }

    def gerar_relatorio_risco(self) -> str:
        """Gera relatório detalhado de risco"""
        metricas = self.calcular_metricas_risco()

        # Emoji para nível de risco
        emoji_risco = {"BAIXO": "🟢", "MÉDIO": "🟡", "ALTO": "🔴"}[metricas["nivel_risco_geral"]]

        relatorio = f"""
🛡️  ANÁLISE DE RISCO DO PORTFOLIO
{'='*50}

📊 RESUMO EXECUTIVO:
   Nível de Risco: {emoji_risco} {metricas['nivel_risco_geral']}
   Risco Total: {metricas['risco_total_percentual']}%
   Posições Abertas: {metricas['posicoes_abertas']}
   Maior Exposição: {metricas['maior_exposicao_individual']:.1f}%

💱 EXPOSIÇÃO CAMBIAL:
{'='*30}"""

        for moeda, exposicao in metricas["exposicao_cambial"].items():
            emoji = "🟢" if abs(exposicao) < 30 else "🟡" if abs(exposicao) < 50 else "🔴"
            relatorio += f"\n   {emoji} {moeda}: {exposicao:+.1f}%"

        relatorio += f"""

🎯 CONCENTRAÇÃO DE POSIÇÕES:
{'='*35}"""

        for par, concentracao in metricas["concentracao_posicoes"].items():
            emoji = "🟢" if concentracao < 25 else "🟡" if concentracao < 40 else "🔴"
            relatorio += f"\n   {emoji} {par}: {concentracao:.1f}%"

        relatorio += f"""

⚠️  RISCO DE DRAWDOWN:
{'='*25}"""

        if metricas["risco_drawdown"]:
            for par, risco in metricas["risco_drawdown"].items():
                emoji = "🟢" if risco < 2 else "🟡" if risco < 5 else "🔴"
                relatorio += f"\n   {emoji} {par}: {risco:.1f}% do capital"
        else:
            relatorio += "\n   ✅ Nenhum stop loss definido"

        relatorio += f"""

🔗 CORRELAÇÕES CRÍTICAS:
{'='*28}"""

        for correlacao, valor in metricas["correlacoes_criticas"].items():
            if abs(valor) > 0.7:
                emoji = "🔴"
            elif abs(valor) > 0.5:
                emoji = "🟡"
            else:
                emoji = "🟢"
            relatorio += f"\n   {emoji} {correlacao}: {valor:+.2f}"

        # Recomendações
        relatorio += f"""

💡 RECOMENDAÇÕES:
{'='*20}"""

        if metricas["nivel_risco_geral"] == "ALTO":
            relatorio += """
   🔴 AÇÃO NECESSÁRIA:
   • Reduzir exposição em moedas > 50%
   • Diversificar concentração de posições
   • Revisar correlações altas entre posições"""
        elif metricas["nivel_risco_geral"] == "MÉDIO":
            relatorio += """
   🟡 MONITORAMENTO:
   • Acompanhar exposições cambiais
   • Considerar hedges para correlações altas
   • Manter stops atualizados"""
        else:
            relatorio += """
   🟢 PORTFOLIO EQUILIBRADO:
   • Risco dentro dos parâmetros
   • Diversificação adequada
   • Continue monitoramento regular"""

        return relatorio


def main():
    """Função principal para demonstração"""
    print("🔍 Iniciando Análise de Risco do Portfolio...")

    caminho = r"c:\repo\projetos\agent-especialista-mercado-financeiro\backend\data\portfolio\portfolio_atual.json"
    analisador = AnalisadorRiscoPortfolio(caminho)

    relatorio = analisador.gerar_relatorio_risco()
    print(relatorio)


if __name__ == "__main__":
    main()