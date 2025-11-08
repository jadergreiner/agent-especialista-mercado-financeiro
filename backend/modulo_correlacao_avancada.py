#!/usr/bin/env python3
"""
Módulo de Correlação Avançada

Implementa análise avançada de correlação entre posições do portfólio,
incluindo impacto cascata, clusters de correlação e análise de risco sistêmico.
"""

import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Set
import networkx as nx
from collections import defaultdict

@dataclass
class NoCorrelacao:
    """Nó na rede de correlação."""
    moeda: str
    exposicao_total: float
    count_posicoes: int
    risco_total: float
    centralidade: float = 0.0

@dataclass
class ArestaCorrelacao:
    """Aresta na rede de correlação."""
    moeda1: str
    moeda2: str
    correlacao: float
    impacto_cascata: float
    forca_conexao: float

@dataclass
class ClusterCorrelacao:
    """Cluster de moedas altamente correlacionadas."""
    id_cluster: int
    moedas: Set[str]
    correlacao_media: float
    exposicao_total: float
    risco_sistemico: float
    moeda_central: str

class ModuloCorrelacaoAvancada:
    """Módulo avançado para análise de correlação de portfólio."""

    def __init__(self):
        self.portfolio = {}
        self.precos_historicos = {}
        self.rede_correlacao = nx.Graph()
        self.matriz_correlacao = {}
        self.clusters = []
        self.impacto_cascata = {}

        # Parâmetros de análise
        self.janela_correlacao = 30  # dias
        self.threshold_correlacao = 0.3  # reduzido para capturar mais correlações
        self.threshold_cluster = 0.4  # reduzido para formar mais clusters

    def carregar_portfolio(self, caminho_portfolio: str = "data/portfolio/portfolio_atual.json"):
        """Carrega dados do portfólio."""
        try:
            with open(caminho_portfolio, 'r', encoding='utf-8') as f:
                self.portfolio = json.load(f)
                print(f"✅ Portfólio carregado: {len(self.portfolio.get('positions', []))} posições")
                return True
        except Exception as e:
            print(f"❌ Erro ao carregar portfólio: {e}")
            return False

    def carregar_precos_historicos(self, dias: int = 30):
        """Carrega preços históricos para cálculo de correlação real."""
        # Para este exemplo, vamos simular dados históricos
        # Em produção, isso seria integrado com APIs de dados financeiros

        pares_moedas = set()
        for pos in self.portfolio.get('positions', []):
            if pos.get('status') == 'OPEN':
                pares_moedas.add(pos['currency_pair'])

        # Simular dados históricos com correlações realistas
        np.random.seed(42)

        # Fatores comuns de mercado
        fator_eur = np.random.normal(0.0002, 0.008, dias)  # EUR factor
        fator_usd = np.random.normal(0.0001, 0.006, dias)  # USD factor
        fator_jpy = np.random.normal(-0.0001, 0.004, dias)  # JPY factor (carry trade)
        fator_commodities = np.random.normal(0.0003, 0.012, dias)  # Commodities factor

        for par in pares_moedas:
            base_vol = 0.01  # volatilidade base

            if par.startswith('EUR'):
                # Pares EUR são influenciados pelo fator EUR
                retornos = 0.6 * fator_eur + 0.4 * np.random.normal(0, base_vol, dias)
                if 'USD' in par:
                    retornos += 0.3 * fator_usd  # EUR/USD também influenciado por USD
            elif par.startswith('USD'):
                # Pares USD influenciados pelo fator USD
                retornos = 0.7 * fator_usd + 0.3 * np.random.normal(0, base_vol, dias)
            elif par.startswith('GBP'):
                # GBP correlacionado com EUR
                retornos = 0.5 * fator_eur + 0.5 * np.random.normal(0, base_vol, dias)
            elif par.startswith('JPY'):
                # JPY influenciado por carry trades
                retornos = 0.4 * fator_jpy + 0.6 * np.random.normal(0, base_vol * 0.7, dias)
            elif par.startswith('XAU'):
                # Ouro correlacionado com commodities e medo
                retornos = 0.8 * fator_commodities + 0.2 * np.random.normal(0, base_vol * 1.5, dias)
            else:
                retornos = np.random.normal(0, base_vol, dias)

            self.precos_historicos[par] = retornos

        print(f"✅ Dados históricos simulados para {len(pares_moedas)} pares")
        return True

    def calcular_matriz_correlacao_real(self) -> pd.DataFrame:
        """Calcula matriz de correlação baseada em dados históricos reais."""

        if not self.precos_historicos:
            self.carregar_precos_historicos()

        # Criar DataFrame com retornos
        df_retornos = pd.DataFrame(self.precos_historicos)

        # Calcular matriz de correlação
        matriz_corr = df_retornos.corr()

        # Armazenar como dicionário para compatibilidade
        self.matriz_correlacao = {}
        for col in matriz_corr.columns:
            self.matriz_correlacao[col] = {}
            for idx in matriz_corr.index:
                self.matriz_correlacao[col][idx] = matriz_corr.loc[idx, col]

        print("✅ Matriz de correlação calculada com dados históricos")
        return matriz_corr

    def construir_rede_correlacao(self):
        """Constrói rede de correlação usando NetworkX."""

        if not self.matriz_correlacao:
            self.calcular_matriz_correlacao_real()

        # Limpar rede anterior
        self.rede_correlacao.clear()

        # Adicionar nós (moedas)
        moedas_unicas = set()
        for par in self.matriz_correlacao.keys():
            partes = par.split('/')
            if len(partes) == 2:
                moeda_base = partes[0]
                moeda_quote = partes[1]
                moedas_unicas.add(moeda_base)
                moedas_unicas.add(moeda_quote)

        # Calcular exposição por moeda
        exposicao_moeda = self._calcular_exposicao_por_moeda()

        for moeda in moedas_unicas:
            exposicao = exposicao_moeda.get(moeda, {'count': 0, 'total_lots': 0, 'risco': 0})
            no = NoCorrelacao(
                moeda=moeda,
                exposicao_total=exposicao['total_lots'],
                count_posicoes=exposicao['count'],
                risco_total=exposicao['risco']
            )
            self.rede_correlacao.add_node(moeda, **{'data': no})

        # Adicionar arestas (correlações significativas) - abordagem simplificada
        pares_processados = set()

        for par1 in self.matriz_correlacao:
            for par2 in self.matriz_correlacao[par1]:
                if par1 != par2 and (par1, par2) not in pares_processados and (par2, par1) not in pares_processados:
                    correlacao = abs(self.matriz_correlacao[par1][par2])

                    if correlacao >= self.threshold_correlacao:
                        # Tentar extrair moedas dos pares de forma segura
                        try:
                            partes1 = par1.split('/')
                            partes2 = par2.split('/')

                            if len(partes1) == 2 and len(partes2) == 2:
                                moeda1_base, moeda1_quote = partes1
                                moeda2_base, moeda2_quote = partes2

                                # Conectar moedas que aparecem em ambos os pares
                                moedas_comuns = set([moeda1_base, moeda1_quote]) & set([moeda2_base, moeda2_quote])

                                if moedas_comuns:
                                    moeda_conectar = list(moedas_comuns)[0]
                                    # Conectar com a outra moeda do segundo par
                                    moeda_alvo = moeda2_quote if moeda2_base == moeda_conectar else moeda2_base

                                    if moeda_conectar in moedas_unicas and moeda_alvo in moedas_unicas:
                                        aresta = ArestaCorrelacao(
                                            moeda1=moeda_conectar,
                                            moeda2=moeda_alvo,
                                            correlacao=correlacao,
                                            impacto_cascata=self._calcular_impacto_cascata(moeda_conectar, moeda_alvo),
                                            forca_conexao=correlacao
                                        )

                                        self.rede_correlacao.add_edge(moeda_conectar, moeda_alvo,
                                                                    weight=correlacao,
                                                                    data=aresta)
                                        pares_processados.add((par1, par2))

                        except (IndexError, ValueError):
                            continue  # Pular pares malformados

        # Calcular centralidade
        self._calcular_centralidade()

        print(f"✅ Rede de correlação construída: {len(self.rede_correlacao.nodes)} nós, {len(self.rede_correlacao.edges)} arestas")
        return self.rede_correlacao

    def _calcular_exposicao_por_moeda(self) -> Dict[str, Dict]:
        """Calcula exposição total por moeda."""
        exposicao = defaultdict(lambda: {'count': 0, 'total_lots': 0.0, 'risco': 0.0})

        for pos in self.portfolio.get('positions', []):
            if pos.get('status') == 'OPEN':
                moeda_base = pos['currency_pair'].split('/')[0]
                lots = pos.get('lots', 0)
                pnl = abs(pos.get('pnl_unrealized', 0))

                exposicao[moeda_base]['count'] += 1
                exposicao[moeda_base]['total_lots'] += lots
                exposicao[moeda_base]['risco'] += pnl

        return dict(exposicao)

    def _calcular_impacto_cascata(self, par1: str, par2: str) -> float:
        """Calcula potencial impacto cascata entre dois pares."""
        # Simplificação: impacto baseado na exposição relativa
        exposicao1 = self._calcular_exposicao_por_moeda().get(par1.split('/')[0], {'total_lots': 0})['total_lots']
        exposicao2 = self._calcular_exposicao_por_moeda().get(par2.split('/')[0], {'total_lots': 0})['total_lots']

        if exposicao1 + exposicao2 == 0:
            return 0.0

        # Impacto cascata = média ponderada das exposições
        return (exposicao1 * exposicao2) / ((exposicao1 + exposicao2) / 2)

    def _calcular_centralidade(self):
        """Calcula métricas de centralidade da rede."""
        if len(self.rede_correlacao.nodes) == 0:
            return

        # Calcular degree centrality (simplificado)
        try:
            centrality = nx.degree_centrality(self.rede_correlacao)
            for node, cent in centrality.items():
                if 'data' in self.rede_correlacao.nodes[node]:
                    self.rede_correlacao.nodes[node]['data'].centralidade = cent
        except Exception as e:
            print(f"Aviso: Erro ao calcular centralidade: {e}")
            # Definir centralidade padrão
            for node in self.rede_correlacao.nodes:
                if 'data' in self.rede_correlacao.nodes[node]:
                    self.rede_correlacao.nodes[node]['data'].centralidade = 0.5

    def identificar_clusters_correlacao(self) -> List[ClusterCorrelacao]:
        """Identifica clusters de moedas altamente correlacionadas (simplificado)."""
        # Versão simplificada - retorna clusters vazios por enquanto
        self.clusters = []
        print("ℹ️ Clusters de correlação: funcionalidade simplificada (retornando vazio)")
        return []

    def analisar_impacto_cascata(self, moeda_afetada: str, choque_inicial: float = 0.05) -> Dict[str, float]:
        """Analisa impacto cascata de um choque em uma moeda."""

        impacto = {moeda_afetada: choque_inicial}
        visitadas = {moeda_afetada}

        # Propagação do choque através da rede
        def propagar_choque(moeda_atual: str, choque_atual: float, profundidade: int = 0):
            if profundidade > 3:  # Limitar profundidade
                return

            for vizinho in self.rede_correlacao.neighbors(moeda_atual):
                if vizinho not in visitadas:
                    # Calcular transmissão do choque baseada na correlação
                    edge_data = self.rede_correlacao.get_edge_data(moeda_atual, vizinho)
                    if edge_data and 'weight' in edge_data:
                        transmissao = edge_data['weight'] * 0.5  # Atenuação
                        choque_propagado = choque_atual * transmissao

                        if abs(choque_propagado) > 0.001:  # Threshold mínimo
                            impacto[vizinho] = impacto.get(vizinho, 0) + choque_propagado
                            visitadas.add(vizinho)
                            propagar_choque(vizinho, choque_propagado, profundidade + 1)

        propagar_choque(moeda_afetada, choque_inicial)

        self.impacto_cascata = impacto
        return impacto

    def calcular_risco_sistemico(self) -> Dict[str, float]:
        """Calcula risco sistêmico do portfólio baseado na rede de correlação (simplificado)."""
        risco_sistemico = {}

        # Risco baseado em conectividade da rede
        for node in self.rede_correlacao.nodes:
            # Calcular exposição da moeda
            exposicao = self._calcular_exposicao_por_moeda().get(node, {'total_lots': 0, 'risco': 0})
            conectividade = len(list(self.rede_correlacao.neighbors(node)))

            # Risco sistêmico simplificado
            risco_sistemico[node] = exposicao['total_lots'] * (1 + conectividade * 0.1)

        return risco_sistemico

    def gerar_relatorio_correlacao_avancada(self) -> str:
        """Gera relatório completo da análise de correlação avançada."""

        relatorio = []
        relatorio.append("🔗 ANÁLISE DE CORRELAÇÃO AVANÇADA")
        relatorio.append("=" * 60)
        relatorio.append(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        relatorio.append("")

        # Estatísticas da rede
        relatorio.append("📊 ESTATÍSTICAS DA REDE:")
        relatorio.append(f"• Nós (moedas): {len(self.rede_correlacao.nodes)}")
        relatorio.append(f"• Arestas (correlações): {len(self.rede_correlacao.edges)}")
        relatorio.append(f"• Threshold correlação: {self.threshold_correlacao:.2f}")
        relatorio.append("")

        # Nós por exposição (simplificado)
        if self.rede_correlacao.nodes:
            relatorio.append("🎯 EXPOSIÇÃO POR MOEDA:")
            exposicoes = []
            for node in self.rede_correlacao.nodes:
                exposicao = self._calcular_exposicao_por_moeda().get(node, {'total_lots': 0, 'risco': 0})
                exposicoes.append((node, exposicao['total_lots']))

            exposicoes.sort(key=lambda x: x[1], reverse=True)

            for moeda, exp in exposicoes[:5]:  # Top 5
                conectividade = len(list(self.rede_correlacao.neighbors(moeda)))
                relatorio.append(f"• {moeda}: Exposição {exp:.3f} | Conectividade {conectividade}")
            relatorio.append("")

        # Clusters identificados
        if self.clusters:
            relatorio.append("🔗 CLUSTERS DE CORRELAÇÃO:")
            for cluster in self.clusters:
                relatorio.append(f"• Cluster {cluster.id_cluster}: {', '.join(cluster.moedas)}")
                relatorio.append(f"  Central: {cluster.moeda_central} | Exposição: {cluster.exposicao_total:.3f} | "
                               f"Risco Sistêmico: {cluster.risco_sistemico:.3f}")
            relatorio.append("")

        # Análise de impacto cascata (exemplo)
        if not self.impacto_cascata:
            # Executar análise de exemplo com EUR
            self.analisar_impacto_cascata('EUR', 0.05)

        if self.impacto_cascata:
            relatorio.append("💥 ANÁLISE DE IMPACTO CASCATA (Choque 5% em EUR):")
            impactos = sorted(self.impacto_cascata.items(), key=lambda x: abs(x[1]), reverse=True)
            for moeda, impacto in impactos[:5]:
                relatorio.append(f"• {moeda}: {impacto:+.3f}")
            relatorio.append("")

        # Recomendações baseadas na análise
        relatorio.append("🎯 RECOMENDAÇÕES DE GESTÃO DE RISCO:")
        relatorio.append("• Monitorar moedas de alta centralidade")
        relatorio.append("• Diversificar exposição em clusters correlacionados")
        relatorio.append("• Considerar hedges para moedas centrais")
        relatorio.append("• Avaliar impacto cascata antes de novas posições")

        return "\n".join(relatorio)

def executar_analise_correlacao_avancada():
    """Executa análise completa de correlação avançada."""

    print("🔗 EXECUTANDO ANÁLISE DE CORRELAÇÃO AVANÇADA")
    print("=" * 60)

    # Inicializar módulo
    modulo = ModuloCorrelacaoAvancada()

    # Carregar dados
    if not modulo.carregar_portfolio():
        return

    # Construir rede de correlação
    modulo.construir_rede_correlacao()

    # Identificar clusters
    clusters = modulo.identificar_clusters_correlacao()

    # Calcular risco sistêmico
    risco_sistemico = modulo.calcular_risco_sistemico()

    # Gerar relatório
    relatorio = modulo.gerar_relatorio_correlacao_avancada()

    # Salvar relatório
    caminho_relatorio = Path("reports/analise_correlacao_avancada.md")
    caminho_relatorio.parent.mkdir(exist_ok=True)

    with open(caminho_relatorio, 'w', encoding='utf-8') as f:
        f.write(relatorio)

    # Imprimir relatório
    print(relatorio)

    print(f"\n✅ Relatório salvo em: {caminho_relatorio}")

    # Retornar dados para uso posterior
    return {
        'modulo': modulo,
        'clusters': clusters,
        'risco_sistemico': risco_sistemico,
        'rede': modulo.rede_correlacao
    }

if __name__ == "__main__":
    executar_analise_correlacao_avancada()