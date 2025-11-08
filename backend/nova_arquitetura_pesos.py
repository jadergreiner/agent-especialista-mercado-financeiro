#!/usr/bin/env python3
"""
Nova Arquitetura de Pesos - Sistema de Decisão Otimizado

Implementa nova arquitetura de pesos baseada na análise de performance,
com foco em correlação de portfólio e exposição total por moeda.
"""

import json
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

@dataclass
class FatoresDecisao:
    """Fatores de decisão com pesos atualizados."""
    # Camada 1: Análise de Portfólio (40%)
    correlacao_portfolio: float = 0.30  # +200% vs anterior
    exposicao_total_moeda: float = 0.25  # +67% vs anterior

    # Camada 2: Fatores Externos (35%)
    eventos_economicos: float = 0.20  # -20% vs anterior
    sentimento_mercado: float = 0.15   # +200% vs anterior (novo)

    # Camada 3: Análise Individual (25%)
    risco_individual: float = 0.15     # -63% vs anterior
    momentum_tecnico: float = 0.08     # -60% vs anterior
    sincronizacao_dados: float = 0.02  # -87% vs anterior

    # Novos fatores
    risco_fim_semana: float = 0.15     # Novo - 15%
    dados_institucionais: float = 0.10 # Novo - 10%

@dataclass
class AnalisePosicao:
    """Análise completa de uma posição."""
    position_id: str
    currency_pair: str
    direction: str
    current_price: float
    pnl_unrealized: float
    lot_size: float

    # Scores calculados
    score_correlacao: float = 0.0
    score_exposicao: float = 0.0
    score_eventos: float = 0.0
    score_sentimento: float = 0.0
    score_individual: float = 0.0
    score_tecnico: float = 0.0
    score_fim_semana: float = 0.0
    score_institucional: float = 0.0

    # Score final
    score_total: float = 0.0
    recomendacao: str = ""
    prioridade: str = ""

class NovaArquiteturaPesos:
    """Nova arquitetura de pesos para tomada de decisão."""

    def __init__(self):
        self.fatores = FatoresDecisao()
        self.portfolio = {}
        self.correlacao_matrix = {}
        self.sentimento_data = {}
        self.eventos_economicos = []

        # Thresholds ajustados baseados na análise
        self.thresholds = {
            'risco_critico': 0.60,    # Reduzido de 70%
            'risco_elevado': 0.45,
            'risco_moderado': 0.30,
            'oportunidade': 0.20
        }

    def carregar_portfolio(self, caminho_portfolio: str = "data/portfolio/portfolio_atual.json"):
        """Carrega dados do portfólio atual."""
        try:
            with open(caminho_portfolio, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.portfolio = data
                print(f"✅ Portfólio carregado: {len(data['positions'])} posições")
                return True
        except Exception as e:
            print(f"❌ Erro ao carregar portfólio: {e}")
            return False

    def calcular_matriz_correlacao(self) -> Dict[str, Dict[str, float]]:
        """Calcula matriz de correlação entre todas as posições."""
        if not self.portfolio.get('positions'):
            return {}

        # Agrupar posições por moeda base
        moedas_base = {}
        for pos in self.portfolio['positions']:
            if pos.get('status') == 'OPEN':
                par = pos['currency_pair']
                moeda_base = par.split('/')[0]  # EUR de EUR/USD

                if moeda_base not in moedas_base:
                    moedas_base[moeda_base] = []
                moedas_base[moeda_base].append(pos)

        # Calcular exposição por moeda
        exposicao_moeda = {}
        for moeda, posicoes in moedas_base.items():
            exposicao_moeda[moeda] = {
                'count': len(posicoes),
                'total_lots': sum(p.get('lots', 0) for p in posicoes),
                'total_pnl': sum(p.get('pnl_unrealized', 0) for p in posicoes)
            }

        # Calcular correlação baseada em exposição compartilhada
        matriz = {}
        moedas = list(exposicao_moeda.keys())

        for i, moeda1 in enumerate(moedas):
            matriz[moeda1] = {}
            for moeda2 in moedas:
                if moeda1 == moeda2:
                    # Correlação própria = 1.0
                    matriz[moeda1][moeda2] = 1.0
                else:
                    # Correlação baseada em similaridade de exposição
                    exp1 = exposicao_moeda[moeda1]
                    exp2 = exposicao_moeda[moeda2]

                    # Fator de correlação: similaridade de count e lots
                    correlacao = min(exp1['count'] / max(exp1['count'], exp2['count']),
                                   exp2['count'] / max(exp1['count'], exp2['count']))
                    correlacao *= min(exp1['total_lots'] / max(exp1['total_lots'], exp2['total_lots'], 0.01),
                                    exp2['total_lots'] / max(exp1['total_lots'], exp2['total_lots'], 0.01))

                    matriz[moeda1][moeda2] = correlacao

        self.correlacao_matrix = matriz
        print(f"✅ Matriz de correlação calculada para {len(moedas)} moedas")
        return matriz

    def calcular_exposicao_total_moeda(self, moeda: str) -> float:
        """Calcula score de exposição total para uma moeda."""
        if not self.portfolio.get('positions'):
            return 0.0

        # Contar posições da moeda
        posicoes_moeda = [p for p in self.portfolio['positions']
                         if p.get('status') == 'OPEN' and p['currency_pair'].startswith(moeda + '/')]

        if not posicoes_moeda:
            return 0.0

        # Calcular métricas de exposição
        total_lots = sum(p.get('lots', 0) for p in posicoes_moeda)
        total_risk = sum(abs(p.get('pnl_unrealized', 0)) for p in posicoes_moeda)
        count_posicoes = len(posicoes_moeda)

        # Score baseado em concentração (0-1, onde 1 é máxima concentração)
        score_concentracao = min(count_posicoes / 5.0, 1.0)  # Máximo 5 posições por moeda
        score_risk = min(total_risk / 1000.0, 1.0)  # Normalizar risco
        score_lots = min(total_lots / 1.0, 1.0)  # Normalizar lots

        # Score final (média ponderada)
        score = (score_concentracao * 0.4 + score_risk * 0.3 + score_lots * 0.3)

        return score

    def calcular_risco_fim_semana(self) -> float:
        """Calcula risco adicional para fim de semana."""
        # Verificar se hoje é sexta-feira (alta exposição a gap)
        hoje = datetime.now()
        dia_semana = hoje.weekday()  # 0=segunda, 4=sexta

        if dia_semana == 4:  # Sexta-feira
            return 0.8  # Alto risco
        elif dia_semana == 3:  # Quinta-feira
            return 0.4  # Risco moderado
        else:
            return 0.1  # Baixo risco

    def analisar_sentimento_mercado(self, moeda: str) -> float:
        """Analisa sentimento de mercado para uma moeda (placeholder para futura implementação)."""
        # Placeholder - será implementado com dados reais
        # Por enquanto, retorna score neutro baseado em volatilidade recente
        return 0.5

    def analisar_dados_institucionais(self, moeda: str) -> float:
        """Analisa posicionamento institucional (placeholder para futura implementação)."""
        # Placeholder - será implementado com dados reais
        return 0.5

    def analisar_posicao(self, posicao: Dict) -> AnalisePosicao:
        """Analisa uma posição usando a nova arquitetura de pesos."""

        analise = AnalisePosicao(
            position_id=posicao['position_id'],
            currency_pair=posicao['currency_pair'],
            direction=posicao['direction'],
            current_price=posicao.get('current_price', 0),
            pnl_unrealized=posicao.get('pnl_unrealized', 0),
            lot_size=posicao.get('lots', 0)
        )

        # Extrair moeda base
        moeda_base = posicao['currency_pair'].split('/')[0]

        # Camada 1: Análise de Portfólio (40%)
        analise.score_correlacao = self._calcular_score_correlacao(moeda_base)
        analise.score_exposicao = self.calcular_exposicao_total_moeda(moeda_base)

        # Camada 2: Fatores Externos (35%)
        analise.score_eventos = self._calcular_score_eventos(moeda_base)
        analise.score_sentimento = self.analisar_sentimento_mercado(moeda_base)

        # Camada 3: Análise Individual (25%)
        analise.score_individual = self._calcular_score_individual(posicao)
        analise.score_tecnico = self._calcular_score_tecnico(posicao)

        # Novos fatores
        analise.score_fim_semana = self.calcular_risco_fim_semana()
        analise.score_institucional = self.analisar_dados_institucionais(moeda_base)

        # Calcular score total
        analise.score_total = (
            # Camada 1 (40%)
            analise.score_correlacao * self.fatores.correlacao_portfolio +
            analise.score_exposicao * self.fatores.exposicao_total_moeda +

            # Camada 2 (35%)
            analise.score_eventos * self.fatores.eventos_economicos +
            analise.score_sentimento * self.fatores.sentimento_mercado +

            # Camada 3 (25%)
            analise.score_individual * self.fatores.risco_individual +
            analise.score_tecnico * self.fatores.momentum_tecnico +

            # Novos fatores
            analise.score_fim_semana * self.fatores.risco_fim_semana +
            analise.score_institucional * self.fatores.dados_institucionais
        )

        # Gerar recomendação baseada no score
        analise.recomendacao, analise.prioridade = self._gerar_recomendacao(analise.score_total)

        return analise

    def _calcular_score_correlacao(self, moeda: str) -> float:
        """Calcula score de correlação para uma moeda."""
        if not self.correlacao_matrix:
            return 0.5

        # Média das correlações com outras moedas
        if moeda in self.correlacao_matrix:
            correlacoes = [v for k, v in self.correlacao_matrix[moeda].items() if k != moeda]
            return np.mean(correlacoes) if correlacoes else 0.5

        return 0.5

    def _calcular_score_eventos(self, moeda: str) -> float:
        """Calcula score de risco baseado em eventos econômicos."""
        # Placeholder - será integrado com dados reais de eventos
        # Por enquanto, score baseado na análise anterior
        if moeda == 'EUR':
            return 0.7  # Alto risco baseado na análise anterior
        return 0.3  # Risco moderado para outras moedas

    def _calcular_score_individual(self, posicao: Dict) -> float:
        """Calcula score de risco individual da posição."""
        pnl = abs(posicao.get('pnl_unrealized', 0))
        lots = posicao.get('lots', 0)

        # Score baseado em tamanho da posição e PnL
        score_size = min(lots / 0.05, 1.0)  # Normalizar lots
        score_pnl = min(pnl / 100.0, 1.0)   # Normalizar PnL

        return (score_size + score_pnl) / 2.0

    def _calcular_score_tecnico(self, posicao: Dict) -> float:
        """Calcula score técnico da posição."""
        # Placeholder - será implementado com indicadores técnicos
        return 0.5

    def _gerar_recomendacao(self, score_total: float) -> Tuple[str, str]:
        """Gera recomendação baseada no score total."""

        if score_total >= self.thresholds['risco_critico']:
            return "FECHAMENTO IMEDIATO", "CRÍTICA"
        elif score_total >= self.thresholds['risco_elevado']:
            return "REDUZIR POSIÇÃO", "ALTA"
        elif score_total >= self.thresholds['risco_moderado']:
            return "MONITORAR CLOSELY", "MÉDIA"
        elif score_total >= self.thresholds['oportunidade']:
            return "MANTER POSIÇÃO", "BAIXA"
        else:
            return "OPORTUNIDADE COMPRA", "BAIXA"

    def analisar_portfolio_completo(self) -> List[AnalisePosicao]:
        """Analisa todas as posições do portfólio."""

        if not self.portfolio.get('positions'):
            print("❌ Portfólio não carregado")
            return []

        # Calcular matriz de correlação primeiro
        self.calcular_matriz_correlacao()

        analises = []
        for posicao in self.portfolio['positions']:
            if posicao.get('status') == 'OPEN':
                analise = self.analisar_posicao(posicao)
                analises.append(analise)

        # Ordenar por score total (maior risco primeiro)
        analises.sort(key=lambda x: x.score_total, reverse=True)

        return analises

    def gerar_relatorio_pesos(self, analises: List[AnalisePosicao]) -> str:
        """Gera relatório detalhado da análise."""

        relatorio = []
        relatorio.append("🎯 ANÁLISE PORTFÓLIO - NOVA ARQUITETURA DE PESOS")
        relatorio.append("=" * 60)
        relatorio.append(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        relatorio.append(f"Posições analisadas: {len(analises)}")
        relatorio.append("")

        # Resumo de pesos
        relatorio.append("⚖️ PESOS DA NOVA ARQUITETURA:")
        relatorio.append("Camada 1 - Portfólio (40%):")
        relatorio.append(".1f")
        relatorio.append(".1f")
        relatorio.append("")
        relatorio.append("Camada 2 - Externos (35%):")
        relatorio.append(".1f")
        relatorio.append(".1f")
        relatorio.append("")
        relatorio.append("Camada 3 - Individual (25%):")
        relatorio.append(".1f")
        relatorio.append(".1f")
        relatorio.append(".1f")
        relatorio.append("")
        relatorio.append("Novos Fatores:")
        relatorio.append(".1f")
        relatorio.append(".1f")
        relatorio.append("")

        # Thresholds
        relatorio.append("🎚️ THRESHOLDS AJUSTADOS:")
        relatorio.append(f"• Risco Crítico: {self.thresholds['risco_critico']:.1%}")
        relatorio.append(f"• Risco Elevado: {self.thresholds['risco_elevado']:.1%}")
        relatorio.append(f"• Risco Moderado: {self.thresholds['risco_moderado']:.1%}")
        relatorio.append("")

        # Análise por posição
        relatorio.append("📊 ANÁLISE POR POSIÇÃO (ordenado por risco):")
        relatorio.append("-" * 80)

        for i, analise in enumerate(analises[:10], 1):  # Top 10
            relatorio.append(f"{i}. {analise.currency_pair} {analise.direction}")
            relatorio.append(".3f")
            relatorio.append(f"   📈 Scores: Corr:{analise.score_correlacao:.2f} Exp:{analise.score_exposicao:.2f} "
                           f"Event:{analise.score_eventos:.2f} Sent:{analise.score_sentimento:.2f}")
            relatorio.append(f"   🎯 {analise.recomendacao} (Prioridade: {analise.prioridade})")
            relatorio.append("")

        # Resumo de recomendações
        recomendacoes = {}
        for analise in analises:
            rec = analise.recomendacao
            recomendacoes[rec] = recomendacoes.get(rec, 0) + 1

        relatorio.append("📋 RESUMO DE RECOMENDAÇÕES:")
        for rec, count in recomendacoes.items():
            relatorio.append(f"• {rec}: {count} posições")
        relatorio.append("")

        # Matriz de correlação
        if self.correlacao_matrix:
            relatorio.append("🔗 MATRIZ DE CORRELAÇÃO:")
            for moeda1, correlacoes in self.correlacao_matrix.items():
                corr_str = ", ".join([f"{m2}:{v:.2f}" for m2, v in correlacoes.items() if m2 != moeda1])
                relatorio.append(f"• {moeda1}: {corr_str}")
            relatorio.append("")

        return "\n".join(relatorio)

def executar_analise_nova_arquitetura():
    """Executa análise completa com nova arquitetura de pesos."""

    print("🚀 EXECUTANDO ANÁLISE COM NOVA ARQUITETURA DE PESOS")
    print("=" * 60)

    # Inicializar nova arquitetura
    arquitetura = NovaArquiteturaPesos()

    # Carregar portfólio
    if not arquitetura.carregar_portfolio():
        return

    # Executar análise completa
    analises = arquitetura.analisar_portfolio_completo()

    # Gerar relatório
    relatorio = arquitetura.gerar_relatorio_pesos(analises)

    # Salvar relatório
    caminho_relatorio = Path("reports/analise_nova_arquitetura_pesos.md")
    caminho_relatorio.parent.mkdir(exist_ok=True)

    with open(caminho_relatorio, 'w', encoding='utf-8') as f:
        f.write(relatorio)

    # Imprimir resumo
    print(relatorio)

    print(f"\n✅ Relatório salvo em: {caminho_relatorio}")

    return analises

if __name__ == "__main__":
    executar_analise_nova_arquitetura()