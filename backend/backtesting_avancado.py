#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Framework de Backtesting Avançado - Análise de Performance de Estratégias
Sistema completo para teste e validação de estratégias de trading
"""

import os
import sys
import json
import pandas as pd
import numpy as np
import sqlite3
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Adicionar path do projeto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TipoOrdem(Enum):
    """Tipos de ordem"""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"

class DirecaoOperacao(Enum):
    """Direção da operação"""
    COMPRA = "compra"
    VENDA = "venda"

class StatusOperacao(Enum):
    """Status da operação"""
    ABERTA = "aberta"
    FECHADA = "fechada"
    CANCELADA = "cancelada"

@dataclass
class Ordem:
    """Representação de uma ordem"""
    id_ordem: str
    timestamp: datetime
    ativo: str
    tipo: TipoOrdem
    direcao: DirecaoOperacao
    quantidade: float
    preco: Optional[float] = None
    preco_stop: Optional[float] = None
    executada: bool = False
    preco_execucao: Optional[float] = None
    timestamp_execucao: Optional[datetime] = None
    taxa_corretagem: float = 0.0
    slippage: float = 0.0

@dataclass
class Operacao:
    """Representação de uma operação completa"""
    id_operacao: str
    ativo: str
    direcao: DirecaoOperacao
    quantidade: float
    preco_entrada: float
    timestamp_entrada: datetime
    preco_saida: Optional[float] = None
    timestamp_saida: Optional[datetime] = None
    status: StatusOperacao = StatusOperacao.ABERTA
    pnl_bruto: float = 0.0
    pnl_liquido: float = 0.0
    custos_totais: float = 0.0
    retorno_percentual: float = 0.0
    duracao_dias: Optional[float] = None
    drawdown_maximo: float = 0.0
    preco_maximo: float = 0.0
    preco_minimo: float = 0.0

@dataclass
class ConfigBacktest:
    """Configuração do backtesting"""
    capital_inicial: float = 100000.0
    taxa_corretagem: float = 0.001  # 0.1%
    slippage_medio: float = 0.0005  # 0.05%
    margem_disponivel: float = 1.0  # 100% (sem alavancagem)
    risco_maximo_posicao: float = 0.05  # 5% por posição
    drawdown_maximo_permitido: float = 0.20  # 20%
    comissao_fixa: float = 0.0
    taxa_overnight: float = 0.0001  # Taxa para posições overnight
    imposto_renda: float = 0.15  # 15% sobre ganhos
    usar_stops: bool = True
    usar_take_profit: bool = True
    timeframe_base: str = "1d"  # Timeframe para análise
    periodo_lookback: int = 252  # Dias para cálculos de risco

@dataclass
class MetricasPerformance:
    """Métricas de performance calculadas"""
    # Retornos
    retorno_total: float = 0.0
    retorno_anualizado: float = 0.0
    retorno_medio_operacao: float = 0.0

    # Risco
    volatilidade_anualizada: float = 0.0
    drawdown_maximo: float = 0.0
    var_95: float = 0.0  # Value at Risk 95%

    # Índices de risco-retorno
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    calmar_ratio: float = 0.0

    # Estatísticas de operações
    total_operacoes: int = 0
    operacoes_vencedoras: int = 0
    operacoes_perdedoras: int = 0
    taxa_acerto: float = 0.0
    fator_lucro: float = 0.0

    # Duração
    duracao_media_operacao: float = 0.0
    maior_sequencia_vitorias: int = 0
    maior_sequencia_derrotas: int = 0

    # Outros
    expectativa_matematica: float = 0.0
    indice_recuperacao: float = 0.0

class SimuladorMercado:
    """Simulador de condições de mercado"""

    def __init__(self, config: ConfigBacktest):
        self.config = config
        self.dados_mercado = {}
        self.volatilidade_mercado = {}

    def carregar_dados_ativo(self, ativo: str, periodo_inicio: datetime,
                            periodo_fim: datetime) -> pd.DataFrame:
        """Carregar dados históricos de um ativo"""
        try:
            ticker = yf.Ticker(ativo)
            dados = ticker.history(start=periodo_inicio, end=periodo_fim)

            if dados.empty:
                raise ValueError(f"Nenhum dado encontrado para {ativo}")

            # Calcular indicadores técnicos básicos
            dados['SMA_20'] = dados['Close'].rolling(window=20).mean()
            dados['SMA_50'] = dados['Close'].rolling(window=50).mean()
            dados['RSI'] = self._calcular_rsi(dados['Close'])
            dados['Volatilidade'] = dados['Close'].pct_change().rolling(window=20).std() * np.sqrt(252)

            self.dados_mercado[ativo] = dados
            self.volatilidade_mercado[ativo] = dados['Volatilidade'].fillna(0.2)  # 20% padrão

            return dados

        except Exception as e:
            print(f"Erro carregando dados para {ativo}: {e}")
            return pd.DataFrame()

    def _calcular_rsi(self, precos: pd.Series, janela: int = 14) -> pd.Series:
        """Calcular RSI (Relative Strength Index)"""
        delta = precos.diff()
        ganho = (delta.where(delta > 0, 0)).rolling(window=janela).mean()
        perda = (-delta.where(delta < 0, 0)).rolling(window=janela).mean()

        rs = ganho / perda
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def simular_execucao_ordem(self, ordem: Ordem, timestamp: datetime) -> Ordem:
        """Simular execução de uma ordem"""
        if ordem.ativo not in self.dados_mercado:
            return ordem

        dados = self.dados_mercado[ordem.ativo]

        # Encontrar preço no timestamp mais próximo
        data_execucao = dados.index[dados.index <= timestamp]
        if len(data_execucao) == 0:
            return ordem

        preco_mercado = dados.loc[data_execucao[-1], 'Close']
        volatilidade = self.volatilidade_mercado[ordem.ativo].loc[data_execucao[-1]]

        # Simular slippage baseado na volatilidade
        slippage_dinamico = min(volatilidade * 0.1, 0.005)  # Máximo 0.5%

        if ordem.direcao == DirecaoOperacao.COMPRA:
            preco_final = preco_mercado * (1 + slippage_dinamico)
        else:
            preco_final = preco_mercado * (1 - slippage_dinamico)

        # Verificar se ordem seria executada
        executada = True
        if ordem.tipo == TipoOrdem.LIMIT:
            if ordem.direcao == DirecaoOperacao.COMPRA and preco_final > ordem.preco:
                executada = False
            elif ordem.direcao == DirecaoOperacao.VENDA and preco_final < ordem.preco:
                executada = False

        if executada:
            ordem.executada = True
            ordem.preco_execucao = preco_final
            ordem.timestamp_execucao = timestamp
            ordem.slippage = slippage_dinamico
            ordem.taxa_corretagem = self.config.taxa_corretagem

        return ordem

class MotorBacktest:
    """Motor principal de backtesting"""

    def __init__(self, config: ConfigBacktest):
        self.config = config
        self.simulador = SimuladorMercado(config)

        # Estados do backtest
        self.capital_atual = config.capital_inicial
        self.posicoes_abertas: Dict[str, Operacao] = {}
        self.operacoes_fechadas: List[Operacao] = []
        self.historico_capital: List[Tuple[datetime, float]] = []
        self.ordens_pendentes: List[Ordem] = []

        # Contadores
        self.contador_ordem = 0
        self.contador_operacao = 0

        # Métricas em tempo real
        self.pnl_atual = 0.0
        self.drawdown_atual = 0.0
        self.pico_capital = config.capital_inicial

    def executar_backtest(self, estrategia: Callable, ativos: List[str],
                         periodo_inicio: datetime, periodo_fim: datetime) -> Dict[str, Any]:
        """
        Executar backtesting completo de uma estratégia

        Args:
            estrategia: Função que implementa a estratégia de trading
            ativos: Lista de ativos para teste
            periodo_inicio: Data de início do teste
            periodo_fim: Data de fim do teste

        Returns:
            Resultados completos do backtesting
        """
        print(f"🧪 Iniciando backtesting: {periodo_inicio.date()} até {periodo_fim.date()}")
        print(f"📊 Ativos: {', '.join(ativos)}")
        print(f"💰 Capital inicial: ${self.config.capital_inicial:,.2f}")

        # Carregar dados de mercado para todos os ativos
        for ativo in ativos:
            print(f"📈 Carregando dados: {ativo}")
            dados = self.simulador.carregar_dados_ativo(ativo, periodo_inicio, periodo_fim)
            if dados.empty:
                print(f"❌ Erro carregando {ativo}")
                continue

        # Criar index de datas unificado
        todas_datas = set()
        for ativo in ativos:
            if ativo in self.simulador.dados_mercado:
                todas_datas.update(self.simulador.dados_mercado[ativo].index)

        datas_ordenadas = sorted(todas_datas)

        print(f"📅 Simulando {len(datas_ordenadas)} dias de trading...")

        # Simular dia a dia
        for i, data_atual in enumerate(datas_ordenadas):
            # Atualizar posições e calcular P&L
            self._atualizar_posicoes(data_atual)

            # Processar ordens pendentes
            self._processar_ordens_pendentes(data_atual)

            # Executar estratégia
            contexto_mercado = self._criar_contexto_mercado(ativos, data_atual)
            sinais = estrategia(contexto_mercado, self._criar_contexto_portfolio())

            # Processar sinais da estratégia
            if sinais:
                self._processar_sinais_estrategia(sinais, data_atual)

            # Atualizar histórico de capital
            self.historico_capital.append((data_atual, self.capital_atual + self.pnl_atual))

            # Atualizar métricas em tempo real
            self._atualizar_metricas_tempo_real()

            # Verificar limites de risco
            if self._verificar_limite_risco():
                print(f"⚠️  Limite de risco atingido em {data_atual.date()}")
                break

            # Progress update
            if i % 50 == 0:
                progress = (i / len(datas_ordenadas)) * 100
                capital_total = self.capital_atual + self.pnl_atual
                print(f"   {progress:.1f}% - Capital: ${capital_total:,.2f} | Drawdown: {self.drawdown_atual:.1%}")

        # Finalizar backtest
        self._fechar_todas_posicoes(datas_ordenadas[-1])

        # Calcular métricas finais
        metricas = self._calcular_metricas_performance()

        # Compilar resultados
        resultados = {
            'config': asdict(self.config),
            'metricas': asdict(metricas),
            'operacoes': [asdict(op) for op in self.operacoes_fechadas],
            'historico_capital': self.historico_capital,
            'capital_final': self.capital_atual + self.pnl_atual,
            'periodo': {
                'inicio': periodo_inicio.isoformat(),
                'fim': periodo_fim.isoformat(),
                'dias_uteis': len(datas_ordenadas)
            }
        }

        print(f"\n✅ Backtesting concluído!")
        print(f"💰 Capital final: ${resultados['capital_final']:,.2f}")
        print(f"📈 Retorno total: {metricas.retorno_total:.1%}")
        print(f"📊 Sharpe Ratio: {metricas.sharpe_ratio:.2f}")
        print(f"📉 Drawdown máximo: {metricas.drawdown_maximo:.1%}")
        print(f"🎯 Taxa de acerto: {metricas.taxa_acerto:.1%}")

        return resultados

    def _criar_contexto_mercado(self, ativos: List[str], data_atual: datetime) -> Dict[str, Any]:
        """Criar contexto de mercado para a estratégia"""
        contexto = {
            'data_atual': data_atual,
            'ativos': {},
            'indicadores_macro': {}
        }

        for ativo in ativos:
            if ativo in self.simulador.dados_mercado:
                dados = self.simulador.dados_mercado[ativo]
                dados_ate_agora = dados[dados.index <= data_atual]

                if not dados_ate_agora.empty:
                    ultima_linha = dados_ate_agora.iloc[-1]
                    contexto['ativos'][ativo] = {
                        'preco': ultima_linha['Close'],
                        'volume': ultima_linha['Volume'],
                        'sma_20': ultima_linha.get('SMA_20', 0),
                        'sma_50': ultima_linha.get('SMA_50', 0),
                        'rsi': ultima_linha.get('RSI', 50),
                        'volatilidade': ultima_linha.get('Volatilidade', 0.2),
                        'dados_historicos': dados_ate_agora
                    }

        return contexto

    def _criar_contexto_portfolio(self) -> Dict[str, Any]:
        """Criar contexto do portfólio para a estratégia"""
        return {
            'capital_disponivel': self.capital_atual,
            'pnl_atual': self.pnl_atual,
            'posicoes_abertas': dict(self.posicoes_abertas),
            'numero_posicoes': len(self.posicoes_abertas),
            'drawdown_atual': self.drawdown_atual,
            'capital_total': self.capital_atual + self.pnl_atual
        }

    def _processar_sinais_estrategia(self, sinais: List[Dict], data_atual: datetime):
        """Processar sinais gerados pela estratégia"""
        for sinal in sinais:
            if sinal['acao'] == 'comprar':
                self._abrir_posicao_compra(
                    ativo=sinal['ativo'],
                    quantidade=sinal.get('quantidade'),
                    preco_limite=sinal.get('preco_limite'),
                    stop_loss=sinal.get('stop_loss'),
                    take_profit=sinal.get('take_profit'),
                    data_atual=data_atual
                )
            elif sinal['acao'] == 'vender':
                self._abrir_posicao_venda(
                    ativo=sinal['ativo'],
                    quantidade=sinal.get('quantidade'),
                    preco_limite=sinal.get('preco_limite'),
                    stop_loss=sinal.get('stop_loss'),
                    take_profit=sinal.get('take_profit'),
                    data_atual=data_atual
                )
            elif sinal['acao'] == 'fechar':
                self._fechar_posicao(sinal['ativo'], data_atual)

    def _abrir_posicao_compra(self, ativo: str, quantidade: Optional[float],
                            preco_limite: Optional[float], stop_loss: Optional[float],
                            take_profit: Optional[float], data_atual: datetime):
        """Abrir posição de compra"""

        # Calcular quantidade se não especificada (baseada no risco)
        if quantidade is None:
            preco_atual = self._obter_preco_atual(ativo, data_atual)
            if preco_atual is None:
                return

            risco_monetario = self.capital_atual * self.config.risco_maximo_posicao
            quantidade = risco_monetario / preco_atual

        # Criar ordem
        ordem = Ordem(
            id_ordem=f"ORD_{self.contador_ordem:06d}",
            timestamp=data_atual,
            ativo=ativo,
            tipo=TipoOrdem.LIMIT if preco_limite else TipoOrdem.MARKET,
            direcao=DirecaoOperacao.COMPRA,
            quantidade=quantidade,
            preco=preco_limite
        )

        self.contador_ordem += 1

        # Simular execução
        ordem_executada = self.simulador.simular_execucao_ordem(ordem, data_atual)

        if ordem_executada.executada:
            # Criar operação
            operacao = Operacao(
                id_operacao=f"OP_{self.contador_operacao:06d}",
                ativo=ativo,
                direcao=DirecaoOperacao.COMPRA,
                quantidade=quantidade,
                preco_entrada=ordem_executada.preco_execucao,
                timestamp_entrada=data_atual
            )

            self.contador_operacao += 1

            # Debitar capital
            custo_total = (quantidade * ordem_executada.preco_execucao *
                          (1 + ordem_executada.taxa_corretagem))

            if custo_total <= self.capital_atual:
                self.capital_atual -= custo_total
                self.posicoes_abertas[ativo] = operacao

                # Adicionar ordens de stop/take profit se especificadas
                if stop_loss and self.config.usar_stops:
                    self._criar_ordem_stop_loss(ativo, stop_loss, data_atual)

                if take_profit and self.config.usar_take_profit:
                    self._criar_ordem_take_profit(ativo, take_profit, data_atual)
        else:
            # Adicionar à lista de ordens pendentes
            self.ordens_pendentes.append(ordem)

    def _abrir_posicao_venda(self, ativo: str, quantidade: Optional[float],
                           preco_limite: Optional[float], stop_loss: Optional[float],
                           take_profit: Optional[float], data_atual: datetime):
        """Abrir posição de venda (venda a descoberto)"""
        # Implementação similar à compra, mas para venda a descoberto
        # Simplificado para o exemplo
        pass

    def _fechar_posicao(self, ativo: str, data_atual: datetime):
        """Fechar posição existente"""
        if ativo not in self.posicoes_abertas:
            return

        operacao = self.posicoes_abertas[ativo]
        preco_atual = self._obter_preco_atual(ativo, data_atual)

        if preco_atual is None:
            return

        # Calcular P&L
        if operacao.direcao == DirecaoOperacao.COMPRA:
            pnl_bruto = (preco_atual - operacao.preco_entrada) * operacao.quantidade
        else:
            pnl_bruto = (operacao.preco_entrada - preco_atual) * operacao.quantidade

        custos = (operacao.quantidade * preco_atual * self.config.taxa_corretagem +
                 self.config.comissao_fixa)

        pnl_liquido = pnl_bruto - custos

        # Atualizar operação
        operacao.preco_saida = preco_atual
        operacao.timestamp_saida = data_atual
        operacao.status = StatusOperacao.FECHADA
        operacao.pnl_bruto = pnl_bruto
        operacao.pnl_liquido = pnl_liquido
        operacao.custos_totais = custos
        operacao.retorno_percentual = pnl_liquido / (operacao.preco_entrada * operacao.quantidade)
        operacao.duracao_dias = (data_atual - operacao.timestamp_entrada).days

        # Creditar capital
        valor_final = (operacao.quantidade * preco_atual *
                      (1 - self.config.taxa_corretagem)) + pnl_liquido
        self.capital_atual += valor_final

        # Mover para operações fechadas
        self.operacoes_fechadas.append(operacao)
        del self.posicoes_abertas[ativo]

    def _obter_preco_atual(self, ativo: str, data_atual: datetime) -> Optional[float]:
        """Obter preço atual de um ativo"""
        if ativo not in self.simulador.dados_mercado:
            return None

        dados = self.simulador.dados_mercado[ativo]
        dados_ate_agora = dados[dados.index <= data_atual]

        if dados_ate_agora.empty:
            return None

        return dados_ate_agora.iloc[-1]['Close']

    def _atualizar_posicoes(self, data_atual: datetime):
        """Atualizar P&L de posições abertas"""
        self.pnl_atual = 0.0

        for ativo, operacao in self.posicoes_abertas.items():
            preco_atual = self._obter_preco_atual(ativo, data_atual)
            if preco_atual is None:
                continue

            if operacao.direcao == DirecaoOperacao.COMPRA:
                pnl_posicao = (preco_atual - operacao.preco_entrada) * operacao.quantidade
            else:
                pnl_posicao = (operacao.preco_entrada - preco_atual) * operacao.quantidade

            self.pnl_atual += pnl_posicao

            # Atualizar máximos e mínimos da posição
            if preco_atual > operacao.preco_maximo:
                operacao.preco_maximo = preco_atual
            if preco_atual < operacao.preco_minimo or operacao.preco_minimo == 0:
                operacao.preco_minimo = preco_atual

    def _processar_ordens_pendentes(self, data_atual: datetime):
        """Processar ordens pendentes"""
        ordens_executadas = []

        for ordem in self.ordens_pendentes:
            ordem_executada = self.simulador.simular_execucao_ordem(ordem, data_atual)
            if ordem_executada.executada:
                ordens_executadas.append(ordem)
                # Processar execução da ordem...

        # Remover ordens executadas da lista pendente
        for ordem in ordens_executadas:
            self.ordens_pendentes.remove(ordem)

    def _atualizar_metricas_tempo_real(self):
        """Atualizar métricas em tempo real"""
        capital_total = self.capital_atual + self.pnl_atual

        if capital_total > self.pico_capital:
            self.pico_capital = capital_total

        if self.pico_capital > 0:
            self.drawdown_atual = (self.pico_capital - capital_total) / self.pico_capital

    def _verificar_limite_risco(self) -> bool:
        """Verificar se limites de risco foram atingidos"""
        return self.drawdown_atual > self.config.drawdown_maximo_permitido

    def _fechar_todas_posicoes(self, data_final: datetime):
        """Fechar todas as posições abertas no final do backtest"""
        ativos_abertos = list(self.posicoes_abertas.keys())
        for ativo in ativos_abertos:
            self._fechar_posicao(ativo, data_final)

    def _criar_ordem_stop_loss(self, ativo: str, preco_stop: float, data_atual: datetime):
        """Criar ordem de stop loss"""
        # Implementação simplificada
        pass

    def _criar_ordem_take_profit(self, ativo: str, preco_take: float, data_atual: datetime):
        """Criar ordem de take profit"""
        # Implementação simplificada
        pass

    def _calcular_metricas_performance(self) -> MetricasPerformance:
        """Calcular métricas completas de performance"""
        if not self.operacoes_fechadas and not self.historico_capital:
            return MetricasPerformance()

        # Converter histórico para DataFrame
        df_capital = pd.DataFrame(self.historico_capital, columns=['data', 'capital'])
        df_capital.set_index('data', inplace=True)

        # Calcular retornos
        retornos = df_capital['capital'].pct_change().dropna()
        capital_final = df_capital['capital'].iloc[-1]

        # Retornos
        retorno_total = (capital_final / self.config.capital_inicial) - 1
        dias_trading = len(df_capital)
        retorno_anualizado = ((1 + retorno_total) ** (252 / dias_trading)) - 1 if dias_trading > 0 else 0

        # Volatilidade
        volatilidade_anualizada = retornos.std() * np.sqrt(252) if len(retornos) > 1 else 0

        # Drawdown
        capital_acumulado = df_capital['capital']
        pico_rolling = capital_acumulado.expanding().max()
        drawdown_series = (capital_acumulado - pico_rolling) / pico_rolling
        drawdown_maximo = abs(drawdown_series.min())

        # Sharpe Ratio (assumindo taxa livre de risco = 2%)
        taxa_livre_risco = 0.02
        excess_return = retorno_anualizado - taxa_livre_risco
        sharpe_ratio = excess_return / volatilidade_anualizada if volatilidade_anualizada > 0 else 0

        # Sortino Ratio
        retornos_negativos = retornos[retornos < 0]
        downside_deviation = retornos_negativos.std() * np.sqrt(252) if len(retornos_negativos) > 0 else 0
        sortino_ratio = excess_return / downside_deviation if downside_deviation > 0 else 0

        # Calmar Ratio
        calmar_ratio = retorno_anualizado / drawdown_maximo if drawdown_maximo > 0 else 0

        # Estatísticas de operações
        if self.operacoes_fechadas:
            pnls = [op.pnl_liquido for op in self.operacoes_fechadas]
            operacoes_vencedoras = len([pnl for pnl in pnls if pnl > 0])
            operacoes_perdedoras = len([pnl for pnl in pnls if pnl < 0])
            taxa_acerto = operacoes_vencedoras / len(self.operacoes_fechadas)

            lucro_medio_vencedoras = np.mean([pnl for pnl in pnls if pnl > 0]) if operacoes_vencedoras > 0 else 0
            perda_media_perdedoras = abs(np.mean([pnl for pnl in pnls if pnl < 0])) if operacoes_perdedoras > 0 else 1
            fator_lucro = lucro_medio_vencedoras / perda_media_perdedoras if perda_media_perdedoras > 0 else 0

            retorno_medio_operacao = np.mean(pnls)
            duracao_media = np.mean([op.duracao_dias for op in self.operacoes_fechadas if op.duracao_dias])

            # Value at Risk 95%
            var_95 = np.percentile(retornos, 5) * np.sqrt(252) if len(retornos) > 20 else 0

            # Expectativa matemática
            expectativa_matematica = (taxa_acerto * lucro_medio_vencedoras) - ((1 - taxa_acerto) * perda_media_perdedoras)
        else:
            operacoes_vencedoras = operacoes_perdedoras = 0
            taxa_acerto = fator_lucro = retorno_medio_operacao = 0
            duracao_media = var_95 = expectativa_matematica = 0

        return MetricasPerformance(
            retorno_total=retorno_total,
            retorno_anualizado=retorno_anualizado,
            retorno_medio_operacao=retorno_medio_operacao,
            volatilidade_anualizada=volatilidade_anualizada,
            drawdown_maximo=drawdown_maximo,
            var_95=var_95,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            calmar_ratio=calmar_ratio,
            total_operacoes=len(self.operacoes_fechadas),
            operacoes_vencedoras=operacoes_vencedoras,
            operacoes_perdedoras=operacoes_perdedoras,
            taxa_acerto=taxa_acerto,
            fator_lucro=fator_lucro,
            duracao_media_operacao=duracao_media,
            expectativa_matematica=expectativa_matematica,
            indice_recuperacao=retorno_anualizado / drawdown_maximo if drawdown_maximo > 0 else 0
        )

class GeradorRelatorios:
    """Gerador de relatórios de backtesting"""

    def __init__(self):
        os.makedirs('reports/backtesting', exist_ok=True)

    def gerar_relatorio_completo(self, resultados: Dict[str, Any],
                               nome_estrategia: str) -> str:
        """Gerar relatório completo em HTML"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo_relatorio = f"reports/backtesting/relatorio_{nome_estrategia}_{timestamp}.html"

        metricas = resultados['metricas']
        config = resultados['config']

        html_content = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Relatório de Backtesting - {nome_estrategia}</title>
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ text-align: center; border-bottom: 2px solid #007bff; padding-bottom: 20px; margin-bottom: 30px; }}
                .metric-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0; }}
                .metric-card {{ background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #007bff; }}
                .metric-value {{ font-size: 24px; font-weight: bold; color: #007bff; }}
                .metric-label {{ color: #6c757d; font-size: 14px; }}
                .section {{ margin: 30px 0; }}
                .positive {{ color: #28a745; }}
                .negative {{ color: #dc3545; }}
                .neutral {{ color: #6c757d; }}
                table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
                th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #f8f9fa; font-weight: 600; }}
                .summary-stats {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Relatório de Backtesting</h1>
                    <h2>{nome_estrategia}</h2>
                    <p>Gerado em: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}</p>
                </div>

                <div class="summary-stats">
                    <h3>Resumo Executivo</h3>
                    <div class="metric-grid">
                        <div>
                            <div class="metric-value">R$ {resultados['capital_final']:,.2f}</div>
                            <div class="metric-label">Capital Final</div>
                        </div>
                        <div>
                            <div class="metric-value {'positive' if metricas['retorno_total'] > 0 else 'negative'}">{metricas['retorno_total']:.1%}</div>
                            <div class="metric-label">Retorno Total</div>
                        </div>
                        <div>
                            <div class="metric-value">{metricas['sharpe_ratio']:.2f}</div>
                            <div class="metric-label">Sharpe Ratio</div>
                        </div>
                        <div>
                            <div class="metric-value negative">{metricas['drawdown_maximo']:.1%}</div>
                            <div class="metric-label">Drawdown Máximo</div>
                        </div>
                    </div>
                </div>

                <div class="section">
                    <h3>Métricas de Performance</h3>
                    <div class="metric-grid">
                        <div class="metric-card">
                            <div class="metric-value">{metricas['retorno_anualizado']:.1%}</div>
                            <div class="metric-label">Retorno Anualizado</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{metricas['volatilidade_anualizada']:.1%}</div>
                            <div class="metric-label">Volatilidade Anualizada</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{metricas['sortino_ratio']:.2f}</div>
                            <div class="metric-label">Sortino Ratio</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{metricas['calmar_ratio']:.2f}</div>
                            <div class="metric-label">Calmar Ratio</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{metricas['taxa_acerto']:.1%}</div>
                            <div class="metric-label">Taxa de Acerto</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{metricas['fator_lucro']:.2f}</div>
                            <div class="metric-label">Fator Lucro</div>
                        </div>
                    </div>
                </div>

                <div class="section">
                    <h3>Estatísticas de Operações</h3>
                    <table>
                        <tr><th>Métrica</th><th>Valor</th></tr>
                        <tr><td>Total de Operações</td><td>{metricas['total_operacoes']}</td></tr>
                        <tr><td>Operações Vencedoras</td><td class="positive">{metricas['operacoes_vencedoras']}</td></tr>
                        <tr><td>Operações Perdedoras</td><td class="negative">{metricas['operacoes_perdedoras']}</td></tr>
                        <tr><td>Duração Média (dias)</td><td>{metricas['duracao_media_operacao']:.1f}</td></tr>
                        <tr><td>Retorno Médio por Operação</td><td class="{'positive' if metricas['retorno_medio_operacao'] > 0 else 'negative'}">R$ {metricas['retorno_medio_operacao']:,.2f}</td></tr>
                        <tr><td>Expectativa Matemática</td><td class="{'positive' if metricas['expectativa_matematica'] > 0 else 'negative'}">R$ {metricas['expectativa_matematica']:,.2f}</td></tr>
                    </table>
                </div>

                <div class="section">
                    <h3>Configuração do Backtest</h3>
                    <table>
                        <tr><th>Parâmetro</th><th>Valor</th></tr>
                        <tr><td>Capital Inicial</td><td>R$ {config['capital_inicial']:,.2f}</td></tr>
                        <tr><td>Taxa de Corretagem</td><td>{config['taxa_corretagem']:.3%}</td></tr>
                        <tr><td>Slippage Médio</td><td>{config['slippage_medio']:.3%}</td></tr>
                        <tr><td>Risco Máximo por Posição</td><td>{config['risco_maximo_posicao']:.1%}</td></tr>
                        <tr><td>Drawdown Máximo Permitido</td><td>{config['drawdown_maximo_permitido']:.1%}</td></tr>
                        <tr><td>Período</td><td>{resultados['periodo']['inicio'][:10]} até {resultados['periodo']['fim'][:10]}</td></tr>
                        <tr><td>Dias Úteis</td><td>{resultados['periodo']['dias_uteis']}</td></tr>
                    </table>
                </div>

                <div class="section">
                    <h3>Análise de Risco</h3>
                    <div class="metric-grid">
                        <div class="metric-card">
                            <div class="metric-value negative">{metricas['var_95']:.1%}</div>
                            <div class="metric-label">VaR 95% (anualizado)</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{metricas['indice_recuperacao']:.2f}</div>
                            <div class="metric-label">Índice de Recuperação</div>
                        </div>
                    </div>
                </div>

                <div class="section">
                    <p><em>Relatório gerado pelo Framework de Backtesting Avançado</em></p>
                    <p><small>⚠️ Resultados passados não garantem performance futura. Este relatório é apenas para fins educacionais.</small></p>
                </div>
            </div>
        </body>
        </html>
        """

        with open(arquivo_relatorio, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return arquivo_relatorio

    def salvar_resultados_json(self, resultados: Dict[str, Any], nome_estrategia: str) -> str:
        """Salvar resultados em formato JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo_json = f"reports/backtesting/dados_{nome_estrategia}_{timestamp}.json"

        # Converter timestamps para strings
        resultados_serializable = json.loads(json.dumps(resultados, default=str))

        with open(arquivo_json, 'w', encoding='utf-8') as f:
            json.dump(resultados_serializable, f, indent=2, ensure_ascii=False)

        return arquivo_json

# Estratégias de exemplo para teste
def estrategia_media_movel_simples(contexto_mercado: Dict, contexto_portfolio: Dict) -> List[Dict]:
    """
    Estratégia simples baseada em médias móveis
    Compra quando SMA20 > SMA50, vende quando SMA20 < SMA50
    """
    sinais = []

    for ativo, dados in contexto_mercado['ativos'].items():
        sma_20 = dados.get('sma_20', 0)
        sma_50 = dados.get('sma_50', 0)
        preco = dados['preco']

        # Verificar se há dados suficientes
        if sma_20 == 0 or sma_50 == 0:
            continue

        # Sinal de compra: SMA20 cruza acima da SMA50
        if sma_20 > sma_50 and ativo not in contexto_portfolio['posicoes_abertas']:
            # Limitar número de posições abertas
            if contexto_portfolio['numero_posicoes'] < 3:
                sinais.append({
                    'acao': 'comprar',
                    'ativo': ativo,
                    'quantidade': None,  # Será calculado automaticamente
                    'stop_loss': preco * 0.95,  # Stop loss 5% abaixo
                    'take_profit': preco * 1.15  # Take profit 15% acima
                })

        # Sinal de venda: SMA20 cruza abaixo da SMA50
        elif sma_20 < sma_50 and ativo in contexto_portfolio['posicoes_abertas']:
            sinais.append({
                'acao': 'fechar',
                'ativo': ativo
            })

    return sinais

def estrategia_rsi_oversold(contexto_mercado: Dict, contexto_portfolio: Dict) -> List[Dict]:
    """
    Estratégia baseada em RSI oversold/overbought
    Compra quando RSI < 30, vende quando RSI > 70
    """
    sinais = []

    for ativo, dados in contexto_mercado['ativos'].items():
        rsi = dados.get('rsi', 50)
        preco = dados['preco']

        # Sinal de compra: RSI oversold
        if rsi < 30 and ativo not in contexto_portfolio['posicoes_abertas']:
            if contexto_portfolio['numero_posicoes'] < 2:
                sinais.append({
                    'acao': 'comprar',
                    'ativo': ativo,
                    'quantidade': None,
                    'stop_loss': preco * 0.92,
                    'take_profit': preco * 1.20
                })

        # Sinal de venda: RSI overbought
        elif rsi > 70 and ativo in contexto_portfolio['posicoes_abertas']:
            sinais.append({
                'acao': 'fechar',
                'ativo': ativo
            })

    return sinais

def testar_framework_backtesting():
    """Testar o framework de backtesting"""
    print("🧪 Testando Framework de Backtesting Avançado...")

    # Configuração do teste
    config = ConfigBacktest(
        capital_inicial=100000.0,
        taxa_corretagem=0.002,  # 0.2%
        slippage_medio=0.001,   # 0.1%
        risco_maximo_posicao=0.10,  # 10% por posição
        drawdown_maximo_permitido=0.25  # 25%
    )

    # Datas de teste
    periodo_inicio = datetime(2023, 1, 1)
    periodo_fim = datetime(2024, 1, 1)

    # Ativos para teste
    ativos = ['AAPL', 'MSFT', 'GOOGL']

    # Criar motor de backtest
    motor = MotorBacktest(config)

    print("\n📊 Testando Estratégia: Médias Móveis")
    resultados_ma = motor.executar_backtest(
        estrategia=estrategia_media_movel_simples,
        ativos=ativos,
        periodo_inicio=periodo_inicio,
        periodo_fim=periodo_fim
    )

    # Gerar relatórios
    gerador = GeradorRelatorios()

    print("\n📄 Gerando relatórios...")
    arquivo_html = gerador.gerar_relatorio_completo(resultados_ma, "medias_moveis")
    arquivo_json = gerador.salvar_resultados_json(resultados_ma, "medias_moveis")

    print(f"✅ Relatório HTML: {arquivo_html}")
    print(f"✅ Dados JSON: {arquivo_json}")

    # Testar segunda estratégia
    print("\n📊 Testando Estratégia: RSI Oversold")
    motor2 = MotorBacktest(config)  # Novo motor para segunda estratégia

    resultados_rsi = motor2.executar_backtest(
        estrategia=estrategia_rsi_oversold,
        ativos=ativos,
        periodo_inicio=periodo_inicio,
        periodo_fim=periodo_fim
    )

    arquivo_html_rsi = gerador.gerar_relatorio_completo(resultados_rsi, "rsi_oversold")
    arquivo_json_rsi = gerador.salvar_resultados_json(resultados_rsi, "rsi_oversold")

    print(f"✅ Relatório RSI HTML: {arquivo_html_rsi}")
    print(f"✅ Dados RSI JSON: {arquivo_json_rsi}")

    print(f"\n🎯 Comparação das Estratégias:")
    print(f"{'Métrica':<25} {'Médias Móveis':<15} {'RSI Oversold':<15}")
    print(f"{'-'*55}")
    print(f"{'Retorno Total':<25} {resultados_ma['metricas']['retorno_total']:>13.1%} {resultados_rsi['metricas']['retorno_total']:>13.1%}")
    print(f"{'Sharpe Ratio':<25} {resultados_ma['metricas']['sharpe_ratio']:>13.2f} {resultados_rsi['metricas']['sharpe_ratio']:>13.2f}")
    print(f"{'Drawdown Máximo':<25} {resultados_ma['metricas']['drawdown_maximo']:>13.1%} {resultados_rsi['metricas']['drawdown_maximo']:>13.1%}")
    print(f"{'Taxa de Acerto':<25} {resultados_ma['metricas']['taxa_acerto']:>13.1%} {resultados_rsi['metricas']['taxa_acerto']:>13.1%}")
    print(f"{'Total Operações':<25} {resultados_ma['metricas']['total_operacoes']:>13} {resultados_rsi['metricas']['total_operacoes']:>13}")

    print(f"\n✅ Framework de Backtesting Avançado implementado com sucesso!")
    return resultados_ma, resultados_rsi

if __name__ == "__main__":
    testar_framework_backtesting()