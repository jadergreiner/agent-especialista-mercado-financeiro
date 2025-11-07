"""
Motor de Níveis de Preço para Reutilização
Sistema de consulta rápida e integração com gestão de portfolio

Funcionalidades:
1. API de consulta rápida de níveis
2. Integração com sistema de risco
3. Alertas de proximidade de níveis
4. Atualização incremental
5. Cache inteligente
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from decimal import Decimal
import numpy as np

class MotorNiveisPortfolio:
    """Motor de consulta e gestão de níveis para o portfolio"""

    def __init__(self):
        self.caminho_niveis = "data/niveis_precos"
        self.caminho_portfolio = "data/portfolio/portfolio_atual.json"
        self.logger = self._configurar_logger()

        # Cache de níveis
        self.cache_niveis = {}
        self.timestamp_cache = {}

        # Configurações
        self.tolerancia_proximidade = 0.005  # 0.5% para alertas
        self.tempo_cache = 300  # 5 minutos

    def _configurar_logger(self) -> logging.Logger:
        """Configurar logging"""
        logger = logging.getLogger('MotorNiveis')
        logger.setLevel(logging.INFO)
        return logger

    def obter_niveis_ativo(self, ticker: str, forcar_reload: bool = False) -> Dict:
        """Obter níveis de um ativo com cache inteligente"""

        # Verificar cache
        if not forcar_reload and ticker in self.cache_niveis:
            timestamp_cache = self.timestamp_cache.get(ticker, datetime.min)
            if datetime.now() - timestamp_cache < timedelta(seconds=self.tempo_cache):
                return self.cache_niveis[ticker]

        # Carregar do arquivo
        nome_arquivo = f"{ticker.replace('=', '_').replace('/', '_')}_niveis.json"
        caminho_arquivo = os.path.join(self.caminho_niveis, nome_arquivo)

        try:
            if os.path.exists(caminho_arquivo):
                with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                    niveis = json.load(f)

                # Atualizar cache
                self.cache_niveis[ticker] = niveis
                self.timestamp_cache[ticker] = datetime.now()

                return niveis
            else:
                return {}

        except Exception as e:
            self.logger.error(f"Erro ao carregar níveis {ticker}: {e}")
            return {}

    def obter_nivel_mais_proximo(self, ticker: str, preco_atual: float,
                                tipo: str = 'ambos') -> Dict:
        """Encontrar nível mais próximo (suporte ou resistência)"""
        niveis = self.obter_niveis_ativo(ticker)

        if not niveis or 'niveis_consolidados' not in niveis:
            return {}

        consolidados = niveis['niveis_consolidados']
        suportes = consolidados.get('suportes_chave', [])
        resistencias = consolidados.get('resistencias_chave', [])

        resultado = {
            'ticker': ticker,
            'preco_atual': preco_atual,
            'nivel_mais_proximo': None,
            'tipo_nivel': None,
            'distancia_pct': None,
            'distancia_pontos': None
        }

        candidatos = []

        # Analisar suportes (abaixo do preço)
        if tipo in ['ambos', 'suporte']:
            for suporte in suportes:
                if suporte <= preco_atual:
                    distancia = abs(preco_atual - suporte)
                    distancia_pct = (distancia / preco_atual) * 100
                    candidatos.append({
                        'nivel': suporte,
                        'tipo': 'suporte',
                        'distancia': distancia,
                        'distancia_pct': distancia_pct
                    })

        # Analisar resistências (acima do preço)
        if tipo in ['ambos', 'resistencia']:
            for resistencia in resistencias:
                if resistencia >= preco_atual:
                    distancia = abs(resistencia - preco_atual)
                    distancia_pct = (distancia / preco_atual) * 100
                    candidatos.append({
                        'nivel': resistencia,
                        'tipo': 'resistencia',
                        'distancia': distancia,
                        'distancia_pct': distancia_pct
                    })

        # Encontrar o mais próximo
        if candidatos:
            mais_proximo = min(candidatos, key=lambda x: x['distancia'])

            resultado.update({
                'nivel_mais_proximo': mais_proximo['nivel'],
                'tipo_nivel': mais_proximo['tipo'],
                'distancia_pct': round(mais_proximo['distancia_pct'], 3),
                'distancia_pontos': round(mais_proximo['distancia'], 5)
            })

        return resultado

    def verificar_proximidade_niveis(self, ticker: str, preco_atual: float) -> Dict:
        """Verificar se preço está próximo de níveis críticos"""
        niveis_proximos = self.obter_nivel_mais_proximo(ticker, preco_atual)

        alerta = {
            'ticker': ticker,
            'preco_atual': preco_atual,
            'alertas': [],
            'nivel_critico': False
        }

        if niveis_proximos and niveis_proximos.get('distancia_pct'):
            distancia_pct = niveis_proximos['distancia_pct']

            # Verificar proximidade crítica
            if distancia_pct <= (self.tolerancia_proximidade * 100):
                alerta['nivel_critico'] = True
                alerta['alertas'].append({
                    'tipo': 'PROXIMIDADE_CRITICA',
                    'nivel': niveis_proximos['nivel_mais_proximo'],
                    'tipo_nivel': niveis_proximos['tipo_nivel'],
                    'distancia_pct': distancia_pct,
                    'severidade': 'ALTA' if distancia_pct <= 0.2 else 'MEDIA'
                })

        return alerta

    def analisar_portfolio_niveis(self) -> Dict:
        """Análise completa de níveis para todo o portfolio"""
        try:
            # Carregar portfolio
            with open(self.caminho_portfolio, 'r', encoding='utf-8') as f:
                portfolio = json.load(f)

            analise_completa = {
                'timestamp_analise': datetime.now().isoformat(),
                'posicoes_analisadas': 0,
                'alertas_criticos': [],
                'resumo_niveis': {},
                'recomendacoes': []
            }

            for posicao in portfolio['positions']:
                if posicao.get('status') != 'OPEN':
                    continue

                ticker_yahoo = self._converter_para_ticker_yahoo(posicao['currency_pair'])
                if not ticker_yahoo:
                    continue

                preco_atual = posicao.get('current_price', 0)
                if not preco_atual:
                    continue

                # Análise de proximidade
                alerta = self.verificar_proximidade_niveis(ticker_yahoo, preco_atual)

                if alerta['nivel_critico']:
                    analise_completa['alertas_criticos'].extend(alerta['alertas'])

                # Obter níveis completos
                niveis = self.obter_niveis_ativo(ticker_yahoo)

                if niveis and 'niveis_consolidados' in niveis:
                    analise_completa['resumo_niveis'][posicao['currency_pair']] = {
                        'ticket': posicao.get('ticket', 'N/A'),
                        'direction': posicao['direction'],
                        'entry_price': posicao['entry_price'],
                        'current_price': preco_atual,
                        'pnl': posicao.get('pnl_unrealized', 0),
                        'suportes_chave': niveis['niveis_consolidados'].get('suportes_chave', []),
                        'resistencias_chave': niveis['niveis_consolidados'].get('resistencias_chave', []),
                        'nivel_mais_proximo': self.obter_nivel_mais_proximo(ticker_yahoo, preco_atual)
                    }

                analise_completa['posicoes_analisadas'] += 1

            # Gerar recomendações
            analise_completa['recomendacoes'] = self._gerar_recomendacoes(analise_completa)

            return analise_completa

        except Exception as e:
            self.logger.error(f"Erro na análise do portfolio: {e}")
            return {}

    def _gerar_recomendacoes(self, analise: Dict) -> List[Dict]:
        """Gerar recomendações baseadas na análise de níveis"""
        recomendacoes = []

        # Alertas críticos
        if analise['alertas_criticos']:
            recomendacoes.append({
                'tipo': 'ALERTA_CRITICO',
                'prioridade': 'ALTA',
                'acao': 'MONITORAR_PROXIMIDADE',
                'detalhes': f"{len(analise['alertas_criticos'])} posições próximas de níveis críticos"
            })

        # Análise de posições
        for par, dados in analise['resumo_niveis'].items():
            nivel_proximo = dados['nivel_mais_proximo']

            if nivel_proximo and nivel_proximo.get('distancia_pct'):
                distancia = nivel_proximo['distancia_pct']

                # Posições LONG próximas de resistência
                if dados['direction'] == 'LONG' and nivel_proximo['tipo_nivel'] == 'resistencia':
                    if distancia <= 1.0:  # Dentro de 1%
                        recomendacoes.append({
                            'tipo': 'TAKE_PROFIT_SUGERIDO',
                            'par': par,
                            'prioridade': 'MEDIA',
                            'acao': 'CONSIDERAR_REALIZACAO_PARCIAL',
                            'nivel_alvo': nivel_proximo['nivel_mais_proximo'],
                            'distancia_pct': distancia
                        })

                # Posições SHORT próximas de suporte
                elif dados['direction'] == 'SHORT' and nivel_proximo['tipo_nivel'] == 'suporte':
                    if distancia <= 1.0:
                        recomendacoes.append({
                            'tipo': 'TAKE_PROFIT_SUGERIDO',
                            'par': par,
                            'prioridade': 'MEDIA',
                            'acao': 'CONSIDERAR_REALIZACAO_PARCIAL',
                            'nivel_alvo': nivel_proximo['nivel_mais_proximo'],
                            'distancia_pct': distancia
                        })

        return recomendacoes

    def _converter_para_ticker_yahoo(self, par_moeda: str) -> Optional[str]:
        """Converter par de moedas para ticker Yahoo Finance"""
        conversoes = {
            'GBP/JPY': 'GBPJPY=X',
            'EUR/USD': 'EURUSD=X',
            'CHF/JPY': 'CHFJPY=X',
            'GBP/USD': 'GBPUSD=X',
            'USD/JPY': 'USDJPY=X',
            'USD/CAD': 'USDCAD=X',
            'USD/CHF': 'USDCHF=X',
            'AUD/USD': 'AUDUSD=X',
            'AUD/CHF': 'AUDCHF=X',
            'AUD/JPY': 'AUDJPY=X',
            'AUD/NZD': 'AUDNZD=X',
            'NZD/USD': 'NZDUSD=X',
            'CAD/CHF': 'CADCHF=X',
            'CAD/JPY': 'CADJPY=X',
            'NZD/CAD': 'NZDCAD=X',
            'EUR/GBP': 'EURGBP=X',
            'EUR/JPY': 'EURJPY=X',
            'EUR/CHF': 'EURCHF=X',
            'NZD/JPY': 'NZDJPY=X',
            'XAU/USD': 'GC=F',
            'GC=F': 'GC=F'
        }
        return conversoes.get(par_moeda)

    def gerar_relatorio_posicoes_niveis(self) -> str:
        """Gerar relatório executivo das posições vs níveis"""
        analise = self.analisar_portfolio_niveis()

        if not analise:
            return "❌ Erro na análise. Verifique se os níveis foram calculados."

        relatorio = []
        relatorio.append("🎯 ANÁLISE DE POSIÇÕES vs NÍVEIS DE PREÇO")
        relatorio.append("=" * 55)
        relatorio.append(f"📅 Análise: {analise['timestamp_analise'][:19]}")
        relatorio.append(f"📊 Posições Analisadas: {analise['posicoes_analisadas']}")
        relatorio.append("")

        # Alertas críticos
        if analise['alertas_criticos']:
            relatorio.append("🚨 ALERTAS CRÍTICOS:")
            relatorio.append("-" * 20)
            for i, alerta in enumerate(analise['alertas_criticos'][:5], 1):
                relatorio.append(f"   {i}. {alerta['tipo_nivel'].upper()}: {alerta['nivel']}")
                relatorio.append(f"      📏 Distância: {alerta['distancia_pct']:.2f}%")
                relatorio.append(f"      ⚠️  Severidade: {alerta['severidade']}")
            relatorio.append("")

        # Resumo por posição
        relatorio.append("📈 ANÁLISE POR POSIÇÃO:")
        relatorio.append("-" * 25)

        for par, dados in analise['resumo_niveis'].items():
            nivel_proximo = dados['nivel_mais_proximo']

            relatorio.append(f"")
            relatorio.append(f"🔹 {par} ({dados['direction']})")
            relatorio.append(f"   💰 Preço: {dados['current_price']} (Entry: {dados['entry_price']})")
            relatorio.append(f"   💵 P&L: {dados['pnl']:+.2f}")

            if nivel_proximo and nivel_proximo.get('nivel_mais_proximo'):
                simbolo = "🔴" if nivel_proximo['tipo_nivel'] == 'resistencia' else "🟢"
                relatorio.append(f"   {simbolo} Nível próximo: {nivel_proximo['nivel_mais_proximo']}")
                relatorio.append(f"      📏 Distância: {nivel_proximo['distancia_pct']:.2f}%")

            # Suportes e resistências
            if dados['suportes_chave']:
                relatorio.append(f"   🟢 Suportes: {dados['suportes_chave'][-2:]}")
            if dados['resistencias_chave']:
                relatorio.append(f"   🔴 Resistências: {dados['resistencias_chave'][-2:]}")

        # Recomendações
        if analise['recomendacoes']:
            relatorio.append("")
            relatorio.append("💡 RECOMENDAÇÕES:")
            relatorio.append("-" * 15)
            for i, rec in enumerate(analise['recomendacoes'][:5], 1):
                prioridade_icon = "🔴" if rec['prioridade'] == 'ALTA' else "🟡"
                relatorio.append(f"   {i}. {prioridade_icon} {rec['acao']}")
                if 'par' in rec:
                    relatorio.append(f"      💱 {rec['par']}")
                if 'nivel_alvo' in rec:
                    relatorio.append(f"      🎯 Nível: {rec['nivel_alvo']}")

        relatorio.append("")
        relatorio.append("✅ MOTOR DE NÍVEIS OPERACIONAL")
        relatorio.append("🔄 Atualização automática de cache a cada 5 minutos")

        return "\n".join(relatorio)


# Classe utilitária para consultas rápidas
class ConsultaNiveisRapida:
    """Interface simplificada para consultas rápidas"""

    def __init__(self):
        self.motor = MotorNiveisPortfolio()

    def nivel_mais_proximo(self, par_moeda: str, preco: float) -> str:
        """Consulta rápida do nível mais próximo"""
        ticker = self.motor._converter_para_ticker_yahoo(par_moeda)
        if not ticker:
            return f"❌ Par {par_moeda} não reconhecido"

        resultado = self.motor.obter_nivel_mais_proximo(ticker, preco)

        if not resultado.get('nivel_mais_proximo'):
            return f"⚠️ Níveis não disponíveis para {par_moeda}"

        tipo_icon = "🔴" if resultado['tipo_nivel'] == 'resistencia' else "🟢"

        return (f"{tipo_icon} {par_moeda}: "
                f"{resultado['tipo_nivel']} {resultado['nivel_mais_proximo']} "
                f"({resultado['distancia_pct']:.2f}% distante)")

    def alertas_portfolio(self) -> List[str]:
        """Lista rápida de alertas do portfolio"""
        analise = self.motor.analisar_portfolio_niveis()

        alertas = []

        # Alertas críticos
        for alerta in analise.get('alertas_criticos', [])[:3]:
            alertas.append(f"🚨 Proximidade crítica: {alerta['distancia_pct']:.2f}%")

        # Recomendações prioritárias
        for rec in analise.get('recomendacoes', [])[:2]:
            if rec['prioridade'] == 'ALTA':
                alertas.append(f"⚠️ {rec['acao']}")

        return alertas if alertas else ["✅ Nenhum alerta crítico"]


def main():
    """Função principal de teste"""
    print("🎯 Testando Motor de Níveis...")

    motor = MotorNiveisPortfolio()
    consulta_rapida = ConsultaNiveisRapida()

    # Gerar relatório completo
    relatorio = motor.gerar_relatorio_posicoes_niveis()
    print(relatorio)

    print("\n" + "="*50)
    print("🚀 CONSULTAS RÁPIDAS:")
    print("="*50)

    # Teste de consultas rápidas
    alertas = consulta_rapida.alertas_portfolio()
    for alerta in alertas:
        print(alerta)

    return motor, consulta_rapida


if __name__ == "__main__":
    motor, consulta = main()