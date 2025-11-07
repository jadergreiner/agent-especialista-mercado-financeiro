#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Visualizador de Resultados de Backtesting
Gera gráficos e análises visuais dos resultados
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from datetime import datetime
import json
import os
from typing import Dict, List, Any

class VisualizadorBacktesting:
    """Gerador de visualizações para resultados de backtesting"""

    def __init__(self):
        plt.style.use('seaborn-v0_8')
        self.cores = {
            'primaria': '#2E86AB',
            'secundaria': '#A23B72',
            'sucesso': '#F18F01',
            'perigo': '#C73E1D',
            'neutro': '#6C757D'
        }

        os.makedirs('reports/backtesting/charts', exist_ok=True)

    def criar_dashboard_visual(self, resultados: Dict[str, Any], nome_estrategia: str) -> str:
        """Criar dashboard visual completo"""

        # Configurar figura com subplots
        fig = plt.figure(figsize=(20, 16))
        gs = fig.add_gridspec(4, 3, hspace=0.3, wspace=0.3)

        # 1. Evolução do Capital
        ax1 = fig.add_subplot(gs[0, :])
        self._plot_evolucao_capital(ax1, resultados)

        # 2. Drawdown
        ax2 = fig.add_subplot(gs[1, :])
        self._plot_drawdown(ax2, resultados)

        # 3. Distribuição de Retornos
        ax3 = fig.add_subplot(gs[2, 0])
        self._plot_distribuicao_retornos(ax3, resultados)

        # 4. Métricas de Risco-Retorno
        ax4 = fig.add_subplot(gs[2, 1])
        self._plot_metricas_risco_retorno(ax4, resultados)

        # 5. Performance por Operação
        ax5 = fig.add_subplot(gs[2, 2])
        self._plot_performance_operacoes(ax5, resultados)

        # 6. Análise Temporal
        ax6 = fig.add_subplot(gs[3, 0])
        self._plot_analise_temporal(ax6, resultados)

        # 7. Estatísticas de Duração
        ax7 = fig.add_subplot(gs[3, 1])
        self._plot_estatisticas_duracao(ax7, resultados)

        # 8. Resumo de Métricas
        ax8 = fig.add_subplot(gs[3, 2])
        self._plot_resumo_metricas(ax8, resultados)

        # Título geral
        fig.suptitle(f'Dashboard de Backtesting - {nome_estrategia}',
                    fontsize=20, fontweight='bold', y=0.98)

        # Salvar
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo = f"reports/backtesting/charts/dashboard_{nome_estrategia}_{timestamp}.png"
        plt.savefig(arquivo, dpi=300, bbox_inches='tight')
        plt.close()

        return arquivo

    def _plot_evolucao_capital(self, ax, resultados):
        """Gráfico de evolução do capital"""
        historico = resultados['historico_capital']
        if not historico:
            return

        datas = [h[0] for h in historico]
        capitais = [h[1] for h in historico]

        # Capital inicial como linha de referência
        capital_inicial = resultados['config']['capital_inicial']

        ax.plot(datas, capitais, linewidth=2, color=self.cores['primaria'], label='Capital Total')
        ax.axhline(y=capital_inicial, color=self.cores['neutro'], linestyle='--', alpha=0.7, label='Capital Inicial')

        # Destacar capital final
        capital_final = capitais[-1]
        cor_final = self.cores['sucesso'] if capital_final > capital_inicial else self.cores['perigo']
        ax.plot(datas[-1], capital_final, 'o', color=cor_final, markersize=8, zorder=5)

        # Formatação
        ax.set_title('Evolução do Capital ao Longo do Tempo', fontsize=14, fontweight='bold')
        ax.set_ylabel('Capital ($)', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend()

        # Formatar eixo x para datas
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%Y'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))

        # Formatar valores monetários
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))

    def _plot_drawdown(self, ax, resultados):
        """Gráfico de drawdown"""
        historico = resultados['historico_capital']
        if not historico:
            return

        datas = [h[0] for h in historico]
        capitais = [h[1] for h in historico]

        # Calcular drawdown
        capital_df = pd.DataFrame({'data': datas, 'capital': capitais})
        capital_df.set_index('data', inplace=True)

        pico_rolling = capital_df['capital'].expanding().max()
        drawdown = (capital_df['capital'] - pico_rolling) / pico_rolling * 100

        # Plot
        ax.fill_between(datas, drawdown, 0, alpha=0.3, color=self.cores['perigo'])
        ax.plot(datas, drawdown, color=self.cores['perigo'], linewidth=2)

        # Destacar drawdown máximo
        idx_max_dd = drawdown.idxmin()
        max_dd = drawdown.min()
        ax.plot(idx_max_dd, max_dd, 'o', color='red', markersize=8, zorder=5)
        ax.annotate(f'Max DD: {max_dd:.1f}%',
                   xy=(idx_max_dd, max_dd),
                   xytext=(10, 10),
                   textcoords='offset points',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8),
                   arrowprops=dict(arrowstyle='->', color='red'))

        ax.set_title('Drawdown ao Longo do Tempo', fontsize=14, fontweight='bold')
        ax.set_ylabel('Drawdown (%)', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%Y'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))

    def _plot_distribuicao_retornos(self, ax, resultados):
        """Distribuição de retornos das operações"""
        operacoes = resultados['operacoes']
        if not operacoes:
            return

        retornos = [op['retorno_percentual'] * 100 for op in operacoes]

        # Histograma
        ax.hist(retornos, bins=20, alpha=0.7, color=self.cores['primaria'], edgecolor='black')

        # Linha vertical no zero
        ax.axvline(x=0, color='red', linestyle='--', alpha=0.7)

        # Estatísticas
        media = np.mean(retornos)
        mediana = np.median(retornos)

        ax.axvline(x=media, color=self.cores['sucesso'], linestyle='-', alpha=0.8, label=f'Média: {media:.1f}%')
        ax.axvline(x=mediana, color=self.cores['secundaria'], linestyle='-', alpha=0.8, label=f'Mediana: {mediana:.1f}%')

        ax.set_title('Distribuição de Retornos', fontsize=12, fontweight='bold')
        ax.set_xlabel('Retorno (%)', fontsize=10)
        ax.set_ylabel('Frequência', fontsize=10)
        ax.legend()
        ax.grid(True, alpha=0.3)

    def _plot_metricas_risco_retorno(self, ax, resultados):
        """Scatter plot de métricas risco-retorno"""
        metricas = resultados['metricas']

        # Dados para o scatter
        retorno = metricas['retorno_anualizado'] * 100
        volatilidade = metricas['volatilidade_anualizada'] * 100

        # Plot principal
        ax.scatter(volatilidade, retorno, s=200, color=self.cores['primaria'], alpha=0.7, edgecolor='black')

        # Linhas de referência
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax.axvline(x=0, color='black', linestyle='-', alpha=0.3)

        # Anotações
        ax.annotate(f'Sharpe: {metricas["sharpe_ratio"]:.2f}',
                   xy=(volatilidade, retorno),
                   xytext=(10, 10),
                   textcoords='offset points',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))

        ax.set_title('Perfil Risco-Retorno', fontsize=12, fontweight='bold')
        ax.set_xlabel('Volatilidade Anualizada (%)', fontsize=10)
        ax.set_ylabel('Retorno Anualizado (%)', fontsize=10)
        ax.grid(True, alpha=0.3)

    def _plot_performance_operacoes(self, ax, resultados):
        """Performance acumulada por operação"""
        operacoes = resultados['operacoes']
        if not operacoes:
            return

        # Calcular performance acumulada
        pnls = [op['pnl_liquido'] for op in operacoes]
        pnl_acumulado = np.cumsum(pnls)

        numeros_operacao = range(1, len(pnls) + 1)

        # Plot
        ax.plot(numeros_operacao, pnl_acumulado, linewidth=2, color=self.cores['primaria'], marker='o', markersize=4)
        ax.axhline(y=0, color='red', linestyle='--', alpha=0.7)

        # Destacar operações vencedoras e perdedoras
        for i, pnl in enumerate(pnls):
            cor = self.cores['sucesso'] if pnl > 0 else self.cores['perigo']
            ax.plot(i+1, pnl_acumulado[i], 'o', color=cor, markersize=6, alpha=0.8)

        ax.set_title('P&L Acumulado por Operação', fontsize=12, fontweight='bold')
        ax.set_xlabel('Número da Operação', fontsize=10)
        ax.set_ylabel('P&L Acumulado ($)', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))

    def _plot_analise_temporal(self, ax, resultados):
        """Análise temporal das operações"""
        operacoes = resultados['operacoes']
        if not operacoes:
            return

        # Extrair mês de cada operação
        meses = []
        pnls = []

        for op in operacoes:
            if 'timestamp_entrada' in op:
                try:
                    data = datetime.fromisoformat(op['timestamp_entrada'])
                    mes = data.strftime('%m/%Y')
                    meses.append(mes)
                    pnls.append(op['pnl_liquido'])
                except:
                    continue

        if not meses:
            return

        # Agrupar por mês
        df_temporal = pd.DataFrame({'mes': meses, 'pnl': pnls})
        pnl_mensal = df_temporal.groupby('mes')['pnl'].sum()

        # Plot
        cores_barras = [self.cores['sucesso'] if x > 0 else self.cores['perigo'] for x in pnl_mensal.values]
        ax.bar(range(len(pnl_mensal)), pnl_mensal.values, color=cores_barras, alpha=0.7, edgecolor='black')

        ax.set_title('P&L por Mês', fontsize=12, fontweight='bold')
        ax.set_xlabel('Mês', fontsize=10)
        ax.set_ylabel('P&L ($)', fontsize=10)
        ax.set_xticks(range(len(pnl_mensal)))
        ax.set_xticklabels(pnl_mensal.index, rotation=45)
        ax.grid(True, alpha=0.3)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))

    def _plot_estatisticas_duracao(self, ax, resultados):
        """Estatísticas de duração das operações"""
        operacoes = resultados['operacoes']
        if not operacoes:
            return

        duracoes = [op.get('duracao_dias', 0) for op in operacoes if op.get('duracao_dias', 0) > 0]

        if not duracoes:
            return

        # Histograma
        ax.hist(duracoes, bins=15, alpha=0.7, color=self.cores['secundaria'], edgecolor='black')

        # Estatísticas
        media_duracao = np.mean(duracoes)
        ax.axvline(x=media_duracao, color='red', linestyle='--', alpha=0.8,
                  label=f'Média: {media_duracao:.1f} dias')

        ax.set_title('Distribuição de Duração', fontsize=12, fontweight='bold')
        ax.set_xlabel('Duração (dias)', fontsize=10)
        ax.set_ylabel('Frequência', fontsize=10)
        ax.legend()
        ax.grid(True, alpha=0.3)

    def _plot_resumo_metricas(self, ax, resultados):
        """Resumo visual das principais métricas"""
        metricas = resultados['metricas']

        # Métricas para exibir
        metricas_principais = {
            'Retorno Total': f"{metricas['retorno_total']:.1%}",
            'Sharpe Ratio': f"{metricas['sharpe_ratio']:.2f}",
            'Max Drawdown': f"{metricas['drawdown_maximo']:.1%}",
            'Taxa Acerto': f"{metricas['taxa_acerto']:.1%}",
            'Fator Lucro': f"{metricas['fator_lucro']:.2f}",
            'Total Ops': f"{metricas['total_operacoes']}"
        }

        # Criar tabela visual
        ax.axis('off')

        y_pos = 0.9
        for metrica, valor in metricas_principais.items():
            ax.text(0.1, y_pos, metrica + ':', fontsize=12, fontweight='bold',
                   verticalalignment='center')
            ax.text(0.7, y_pos, valor, fontsize=12,
                   verticalalignment='center', horizontalalignment='right')
            y_pos -= 0.15

        ax.set_title('Resumo de Métricas', fontsize=12, fontweight='bold')
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)

    def comparar_estrategias(self, resultados_lista: List[Dict], nomes: List[str]) -> str:
        """Comparar múltiplas estratégias visualmente"""

        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Comparação de Estratégias', fontsize=16, fontweight='bold')

        cores_estrategias = [self.cores['primaria'], self.cores['secundaria'],
                           self.cores['sucesso'], self.cores['perigo']]

        # 1. Evolução do Capital
        ax1 = axes[0, 0]
        for i, (resultados, nome) in enumerate(zip(resultados_lista, nomes)):
            historico = resultados['historico_capital']
            if historico:
                datas = [h[0] for h in historico]
                capitais = [h[1] for h in historico]
                ax1.plot(datas, capitais, linewidth=2,
                        color=cores_estrategias[i % len(cores_estrategias)],
                        label=nome)

        ax1.set_title('Evolução do Capital')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))

        # 2. Comparação de Métricas
        ax2 = axes[0, 1]
        metricas_nomes = ['Retorno Total', 'Sharpe Ratio', 'Max Drawdown', 'Taxa Acerto']
        x_pos = np.arange(len(metricas_nomes))
        width = 0.35

        for i, (resultados, nome) in enumerate(zip(resultados_lista, nomes)):
            metricas = resultados['metricas']
            valores = [
                metricas['retorno_total'] * 100,
                metricas['sharpe_ratio'] * 10,  # Escalar para visualização
                metricas['drawdown_maximo'] * 100,
                metricas['taxa_acerto'] * 100
            ]

            ax2.bar(x_pos + i * width, valores, width,
                   color=cores_estrategias[i % len(cores_estrategias)],
                   alpha=0.7, label=nome)

        ax2.set_title('Comparação de Métricas')
        ax2.set_xticks(x_pos + width/2)
        ax2.set_xticklabels(metricas_nomes, rotation=45)
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        # 3. Risco vs Retorno
        ax3 = axes[1, 0]
        for i, (resultados, nome) in enumerate(zip(resultados_lista, nomes)):
            metricas = resultados['metricas']
            retorno = metricas['retorno_anualizado'] * 100
            risco = metricas['volatilidade_anualizada'] * 100

            ax3.scatter(risco, retorno, s=150,
                       color=cores_estrategias[i % len(cores_estrategias)],
                       alpha=0.7, label=nome, edgecolor='black')

        ax3.set_title('Perfil Risco vs Retorno')
        ax3.set_xlabel('Risco (Volatilidade %)')
        ax3.set_ylabel('Retorno Anualizado (%)')
        ax3.legend()
        ax3.grid(True, alpha=0.3)

        # 4. Resumo Comparativo
        ax4 = axes[1, 1]
        ax4.axis('off')

        y_start = 0.9
        for i, (resultados, nome) in enumerate(zip(resultados_lista, nomes)):
            metricas = resultados['metricas']
            capital_final = resultados['capital_final']

            texto = f"{nome}:\n"
            texto += f"  Capital Final: ${capital_final:,.0f}\n"
            texto += f"  Retorno: {metricas['retorno_total']:.1%}\n"
            texto += f"  Sharpe: {metricas['sharpe_ratio']:.2f}\n"

            ax4.text(0.05, y_start - i * 0.25, texto, fontsize=10,
                    verticalalignment='top',
                    bbox=dict(boxstyle='round,pad=0.5',
                             facecolor=cores_estrategias[i % len(cores_estrategias)],
                             alpha=0.2))

        ax4.set_title('Resumo Comparativo')

        plt.tight_layout()

        # Salvar
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo = f"reports/backtesting/charts/comparacao_estrategias_{timestamp}.png"
        plt.savefig(arquivo, dpi=300, bbox_inches='tight')
        plt.close()

        return arquivo

def demonstrar_visualizacoes():
    """Demonstrar as visualizações"""
    print("📊 Criando visualizações dos resultados de backtesting...")

    # Carregar resultados dos testes anteriores
    import glob

    arquivos_json = glob.glob("reports/backtesting/dados_*.json")

    if len(arquivos_json) >= 2:
        # Carregar dois resultados mais recentes
        arquivos_json.sort(reverse=True)

        with open(arquivos_json[0], 'r', encoding='utf-8') as f:
            resultado1 = json.load(f)

        with open(arquivos_json[1], 'r', encoding='utf-8') as f:
            resultado2 = json.load(f)

        # Extrair nomes das estratégias dos nomes dos arquivos
        nome1 = arquivos_json[0].split('dados_')[1].split('_2025')[0]
        nome2 = arquivos_json[1].split('dados_')[1].split('_2025')[0]

        # Criar visualizador
        visualizador = VisualizadorBacktesting()

        # Dashboard individual para cada estratégia
        print(f"📈 Criando dashboard para {nome1}...")
        arquivo1 = visualizador.criar_dashboard_visual(resultado1, nome1)
        print(f"✅ Dashboard salvo: {arquivo1}")

        print(f"📈 Criando dashboard para {nome2}...")
        arquivo2 = visualizador.criar_dashboard_visual(resultado2, nome2)
        print(f"✅ Dashboard salvo: {arquivo2}")

        # Comparação entre estratégias
        print(f"⚖️  Criando comparação entre estratégias...")
        arquivo_comp = visualizador.comparar_estrategias(
            [resultado1, resultado2],
            [nome1.replace('_', ' ').title(), nome2.replace('_', ' ').title()]
        )
        print(f"✅ Comparação salva: {arquivo_comp}")

    else:
        print("❌ Não foram encontrados resultados de backtesting para visualizar.")
        print("   Execute primeiro o script de backtesting.")

if __name__ == "__main__":
    demonstrar_visualizacoes()