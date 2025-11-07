"""
Gerenciador de Portfolio Forex
================================

Este módulo fornece funcionalidades completas para gestão de portfolios forex,
incluindo criação, atualização e monitoramento de posições em tempo real.

Funcionalidades principais:
- Carregamento e salvamento de portfolios JSON
- Cálculo de P&L em tempo real
- Gestão de risco e exposição
- Relatórios de performance
- Análise de correlação entre posições

Autor: Agent Especialista Mercado Financeiro
Data: 29/12/2024
"""

import json
import yfinance as yf
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import sys
import os

# Adicionar utils ao path para importar feed_resolver
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))
try:
    from feed_resolver import resolver_cotacao_ouro
except ImportError:
    # Fallback se módulo não existir
    def resolver_cotacao_ouro(ticker):
        return None


@dataclass
class PosicaoForex:
    """Classe para representar uma posição forex individual"""
    position_id: str
    currency_pair: str
    direction: str  # LONG ou SHORT
    entry_price: float
    current_price: float
    lots: float
    lot_size: float
    entry_date: datetime
    stop_loss: Optional[float] = None
    take_profit: Optional[List[Dict]] = None
    strategy: Optional[str] = None
    risk_percentage: Optional[float] = None
    notes: Optional[str] = None
    status: str = "OPEN"

    def calcular_pnl(self) -> float:
        """Calcula P&L não realizado da posição"""
        diferenca_preco = self.current_price - self.entry_price

        if self.direction == "SHORT":
            diferenca_preco = -diferenca_preco

        # Para pares forex, calcular valor do pip
        if "/" in self.currency_pair:
            valor_por_pip = (self.lots * self.lot_size * diferenca_preco)
        else:  # Para commodities como GC=F
            valor_por_pip = (self.lots * self.lot_size * diferenca_preco)

        return valor_por_pip

    def calcular_risco_monetario(self, capital_total: float) -> float:
        """Calcula valor monetário em risco baseado no stop loss"""
        if not self.stop_loss:
            return 0

        diferenca_stop = abs(self.entry_price - self.stop_loss)
        if self.direction == "SHORT":
            diferenca_stop = -diferenca_stop if self.stop_loss > self.entry_price else diferenca_stop

        risco_monetario = self.lots * self.lot_size * diferenca_stop
        return abs(risco_monetario)


class GerenciadorPortfolio:
    """Classe principal para gerenciamento do portfolio forex"""

    def __init__(self, caminho_portfolio: str):
        """
        Inicializa o gerenciador com o caminho do arquivo JSON

        Args:
            caminho_portfolio: Caminho para o arquivo JSON do portfolio
        """
        self.caminho_portfolio = Path(caminho_portfolio)
        self.portfolio_data = self._carregar_portfolio()

    def _carregar_portfolio(self) -> Dict:
        """Carrega dados do portfolio do arquivo JSON"""
        try:
            with open(self.caminho_portfolio, 'r', encoding='utf-8') as arquivo:
                return json.load(arquivo)
        except FileNotFoundError:
            print(f"Arquivo não encontrado: {self.caminho_portfolio}")
            return self._criar_portfolio_vazio()
        except json.JSONDecodeError as e:
            print(f"Erro ao decodificar JSON: {e}")
            return self._criar_portfolio_vazio()

    def _criar_portfolio_vazio(self) -> Dict:
        """Cria estrutura básica de um portfolio vazio"""
        return {
            "portfolio_metadata": {
                "portfolio_id": "new_portfolio",
                "name": "Novo Portfolio",
                "creation_date": datetime.now(timezone.utc).isoformat(),
                "last_update": datetime.now(timezone.utc).isoformat(),
                "base_currency": "USD",
                "total_capital": 100000,
                "risk_tolerance": "moderate"
            },
            "positions": [],
            "performance": {
                "total_pnl": 0,
                "total_pnl_percentage": 0,
                "open_positions_count": 0,
                "daily_pnl": 0,
                "max_drawdown": 0,
                "sharpe_ratio": 0,
                "total_risk_exposure": 0
            }
        }

    def salvar_portfolio(self):
        """Salva o portfolio atual no arquivo JSON"""
        self.portfolio_data["portfolio_metadata"]["last_update"] = datetime.now(timezone.utc).isoformat()

        try:
            with open(self.caminho_portfolio, 'w', encoding='utf-8') as arquivo:
                json.dump(self.portfolio_data, arquivo, indent=2, ensure_ascii=False)
            print(f"✅ Portfolio salvo com sucesso em {self.caminho_portfolio}")
        except Exception as e:
            print(f"❌ Erro ao salvar portfolio: {e}")

    def buscar_cotacoes_atuais(self) -> Dict[str, float]:
        """
        Busca cotações atuais para todos os instrumentos do portfolio
        Com suporte a feed resolver para tickers problemáticos

        Returns:
            Dict com pares e seus preços atuais
        """
        cotacoes = {}

        for posicao in self.portfolio_data["positions"]:
            par = posicao["currency_pair"]
            ticker_yf = self._converter_para_ticker_yfinance(par)

            try:
                # Verificar se precisa usar feed resolver para ouro
                if ticker_yf == "RESOLVER_OURO":
                    preco_ouro = resolver_cotacao_ouro(par)
                    if preco_ouro:
                        cotacoes[par] = round(float(preco_ouro), 5)
                        print(f"📊 {par}: {preco_ouro:.5f}")
                    else:
                        print(f"⚠️  Feed resolver falhou para {par}")
                        cotacoes[par] = posicao["current_price"]  # Manter preço anterior
                    continue

                # Processo normal para outros tickers
                ticker = yf.Ticker(ticker_yf)
                info = ticker.history(period="1d", interval="1m")

                if not info.empty:
                    preco_atual = info['Close'].iloc[-1]
                    cotacoes[par] = round(float(preco_atual), 5)
                    print(f"📊 {par}: {preco_atual:.5f}")
                else:
                    print(f"⚠️  Sem dados para {par}")
                    cotacoes[par] = posicao["current_price"]  # Manter preço anterior

            except Exception as e:
                print(f"❌ Erro ao buscar {par}: {e}")
                cotacoes[par] = posicao["current_price"]  # Manter preço anterior

        return cotacoes

    def _converter_para_ticker_yfinance(self, currency_pair: str) -> str:
        """Converte par de moeda para formato yfinance com suporte a feed resolver"""

        # Verificar se é ticker de ouro que precisa de resolução especial
        if currency_pair in ['XAUUSD', 'XAU/USD']:
            print(f"🥇 Ticker de ouro detectado: {currency_pair}")
            return "RESOLVER_OURO"  # Sinal especial para usar feed resolver

        # Mapeamento de pares forex para yfinance
        mapeamento = {
            "EUR/USD": "EURUSD=X",
            "GBP/USD": "GBPUSD=X",
            "USD/JPY": "USDJPY=X",
            "GBP/JPY": "GBPJPY=X",
            "EUR/JPY": "EURJPY=X",
            "CHF/JPY": "CHFJPY=X",
            "USD/CHF": "USDCHF=X",
            "EUR/CHF": "EURCHF=X",
            "GBP/CHF": "GBPCHF=X",
            "AUD/USD": "AUDUSD=X",
            "NZD/USD": "NZDUSD=X",
            "USD/CAD": "USDCAD=X",
            "GC=F": "GC=F",  # Gold Futures
            "SI=F": "SI=F",  # Silver Futures
            "CL=F": "CL=F"   # Crude Oil Futures
        }

        return mapeamento.get(currency_pair, currency_pair)

    def atualizar_precos(self):
        """Atualiza preços atuais de todas as posições"""
        print("🔄 Atualizando cotações do portfolio...")
        cotacoes = self.buscar_cotacoes_atuais()

        for posicao in self.portfolio_data["positions"]:
            par = posicao["currency_pair"]
            if par in cotacoes:
                posicao["current_price"] = cotacoes[par]

        self._recalcular_performance()
        print("✅ Preços atualizados com sucesso!")

    def _recalcular_performance(self):
        """Recalcula métricas de performance do portfolio"""
        total_pnl = 0
        posicoes_abertas = 0
        total_risco = 0
        capital_total = self.portfolio_data["portfolio_metadata"]["total_capital"]

        for posicao_data in self.portfolio_data["positions"]:
            if posicao_data["status"] == "OPEN":
                posicoes_abertas += 1

                # Criar objeto PosicaoForex para cálculos
                posicao = PosicaoForex(
                    position_id=posicao_data["position_id"],
                    currency_pair=posicao_data["currency_pair"],
                    direction=posicao_data["direction"],
                    entry_price=posicao_data["entry_price"],
                    current_price=posicao_data["current_price"],
                    lots=posicao_data["lots"],
                    lot_size=posicao_data["lot_size"],
                    entry_date=datetime.fromisoformat(posicao_data["entry_date"]),
                    stop_loss=posicao_data.get("stop_loss"),
                    strategy=posicao_data.get("strategy"),
                    risk_percentage=posicao_data.get("risk_percentage")
                )

                pnl_posicao = posicao.calcular_pnl()
                total_pnl += pnl_posicao

                # Atualizar P&L na estrutura
                posicao_data["pnl_unrealized"] = round(pnl_posicao, 2)

                # Calcular risco
                if posicao.risk_percentage:
                    total_risco += posicao.risk_percentage

        # Atualizar métricas de performance
        self.portfolio_data["performance"].update({
            "total_pnl": round(total_pnl, 2),
            "total_pnl_percentage": round((total_pnl / capital_total) * 100, 3),
            "open_positions_count": posicoes_abertas,
            "total_risk_exposure": round(total_risco, 2)
        })

    def gerar_relatorio_portfolio(self) -> str:
        """
        Gera relatório detalhado do portfolio

        Returns:
            String formatada com relatório completo
        """
        self.atualizar_precos()

        metadata = self.portfolio_data["portfolio_metadata"]
        performance = self.portfolio_data["performance"]

        relatorio = f"""
📊 RELATÓRIO PORTFOLIO FOREX
{'='*50}

💼 Informações Gerais:
   Portfolio: {metadata['name']}
   Capital Total: ${metadata['total_capital']:,.2f}
   Moeda Base: {metadata['base_currency']}
   Última Atualização: {metadata['last_update'][:19]}

📈 Performance:
   P&L Total: ${performance['total_pnl']:,.2f} ({performance['total_pnl_percentage']:+.3f}%)
   Posições Abertas: {performance['open_positions_count']}
   Exposição de Risco: {performance['total_risk_exposure']:.1f}%

🎯 POSIÇÕES DETALHADAS:
{'='*50}
"""

        for i, posicao in enumerate(self.portfolio_data["positions"], 1):
            if posicao["status"] == "OPEN":
                pnl = posicao.get("pnl_unrealized", 0)
                emoji_pnl = "🟢" if pnl >= 0 else "🔴"

                relatorio += f"""
{i}. {posicao['currency_pair']} - {posicao['direction']}
   📥 Entrada: {posicao['entry_price']:.5f} | 📊 Atual: {posicao['current_price']:.5f}
   💰 Lotes: {posicao['lots']} | {emoji_pnl} P&L: ${pnl:,.2f}
   🛡️  Stop: {posicao.get('stop_loss', 'N/A')} | 🎯 Risco: {posicao.get('risk_percentage', 0):.1f}%
   📝 Estratégia: {posicao.get('strategy', 'N/A')}
   💬 Notas: {posicao.get('notes', 'N/A')}
"""

        return relatorio

    def adicionar_posicao(self, currency_pair: str, direction: str, entry_price: float,
                         lots: float, lot_size: float = 100000, **kwargs):
        """
        Adiciona nova posição ao portfolio

        Args:
            currency_pair: Par de moeda (ex: EUR/USD)
            direction: LONG ou SHORT
            entry_price: Preço de entrada
            lots: Quantidade de lotes
            lot_size: Tamanho do lote
            **kwargs: Parâmetros opcionais (stop_loss, strategy, etc.)
        """
        nova_posicao = {
            "position_id": f"pos_{len(self.portfolio_data['positions']) + 1:03d}",
            "currency_pair": currency_pair,
            "direction": direction.upper(),
            "entry_price": entry_price,
            "current_price": entry_price,  # Iniciar com preço de entrada
            "lots": lots,
            "lot_size": lot_size,
            "entry_date": datetime.now(timezone.utc).isoformat(),
            "pnl_unrealized": 0,
            "pnl_realized": 0,
            "status": "OPEN"
        }

        # Adicionar parâmetros opcionais
        for key, value in kwargs.items():
            if value is not None:
                nova_posicao[key] = value

        self.portfolio_data["positions"].append(nova_posicao)
        print(f"✅ Posição adicionada: {currency_pair} {direction} {lots} lotes @ {entry_price}")

        # Atualizar performance
        self._recalcular_performance()
        self.salvar_portfolio()


def main():
    """Função principal para demonstração do sistema"""
    print("🚀 Iniciando Gerenciador de Portfolio Forex...")

    # Caminho para o portfolio
    caminho_portfolio = r"c:\repo\projetos\agent-especialista-mercado-financeiro\backend\data\portfolio\portfolio_atual.json"

    # Criar gerenciador
    gerenciador = GerenciadorPortfolio(caminho_portfolio)

    # Gerar e exibir relatório
    relatorio = gerenciador.gerar_relatorio_portfolio()
    print(relatorio)

    # Salvar dados atualizados
    gerenciador.salvar_portfolio()


if __name__ == "__main__":
    main()