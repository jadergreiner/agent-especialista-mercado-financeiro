#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RECOMENDADOR DE OPERAÇÕES DO FUNDO

Módulo inteligente para geração de recomendações de operações baseado em:
- Análise técnica via calculador_niveis_precisao
- Correlação de mercado via modulo_correlacao_avancada
- Cenário macroeconômico atual
- Risco do portfólio
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

# Imports dos módulos especializados
try:
    from .modulo_correlacao_avancada import ModuloCorrelacaoAvancada
    from .calculador_niveis_precisao import CalculadorNiveisPrecisao
    from .analisador_risco_fundo import AnalisadorRiscoFundo
except ImportError:
    try:
        from modulo_correlacao_avancada import ModuloCorrelacaoAvancada
        from calculador_niveis_precisao import CalculadorNiveisPrecisao
        from analisador_risco_fundo import AnalisadorRiscoFundo
    except ImportError:
        ModuloCorrelacaoAvancada = None
        CalculadorNiveisPrecisao = None
        AnalisadorRiscoFundo = None

class TipoRecomendacao(Enum):
    COMPRA = "COMPRA"
    VENDA = "VENDA"
    HOLD = "HOLD"
    TAKE_PROFIT = "TAKE_PROFIT"
    STOP_LOSS = "STOP_LOSS"
    HEDGE = "HEDGE"
    DIVERSIFICACAO = "DIVERSIFICACAO"

class NivelConfianca(Enum):
    BAIXA = "BAIXA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"
    MUITO_ALTA = "MUITO_ALTA"

@dataclass
class RecomendacaoOperacao:
    """Estrutura para recomendação de operação"""
    tipo: TipoRecomendacao
    ativo: str
    preco_sugerido: Optional[float]
    quantidade_sugerida: Optional[float]
    razao: str
    nivel_confianca: NivelConfianca
    horizonte: str  # INTRADAY, SWING, POSITION
    risco_estimado: float
    reward_estimado: float
    risk_reward_ratio: float
    # Campos adicionais para posições existentes
    ticket: Optional[str] = None
    entry_date: Optional[str] = None
    partial_results: Optional[float] = None
    entry_price: Optional[float] = None
    direction: Optional[str] = None

@dataclass
class AnaliseMercado:
    """Análise completa do mercado para recomendações"""
    tendencia_principal: str
    volatilidade_atual: float
    correlacao_mercado: float
    oportunidades_identificadas: int
    risco_mercado: str

class RecomendadorOperacoesFundo:
    """
    Recomendador de Operações do Fundo - Sistema inteligente de sugestões
    """

    def __init__(self):
        # Logger dedicado para auditoria de cálculos
        self.logger = logging.getLogger('RecomendadorOperacoesFundo')
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

        self.modulo_correlacao = ModuloCorrelacaoAvancada() if ModuloCorrelacaoAvancada else None
        self.calculador_niveis = CalculadorNiveisPrecisao() if CalculadorNiveisPrecisao else None
        self.analisador_risco = AnalisadorRiscoFundo() if AnalisadorRiscoFundo else None

        # Parâmetros de recomendação
        self.min_confianca = 0.6  # 60% mínimo
        self.max_risk_reward_ratio = 3.0  # Máximo 1:3
        self.capital_base = 100000

        # Cenário macro atual (simulado - em produção viria de API)
        self.cenario_macro = self._carregar_cenario_macro_atual()

    def _carregar_cenario_macro_atual(self) -> Dict:
        """Carrega cenário macroeconômico atual"""
        # Em produção, isso viria de APIs econômicas
        return {
            "vix": 21.05,  # Índice de volatilidade
            "dxy": 99.53,  # Índice dólar
            "sp500_trend": "BEARISH",  # Tendência S&P 500
            "fed_rate": 5.25,  # Taxa Fed
            "ecb_rate": 4.25,  # Taxa ECB
            "usd_trend": "STABLE",
            "risk_sentiment": "NEUTRAL",
            "volatility_regime": "MODERATE"
        }

    def gerar_recomendacoes_completas(self, portfolio: dict) -> Dict[str, List[RecomendacaoOperacao]]:
        """
        Gera recomendações completas para o portfólio
        """
        print("🧠 ANALISANDO MERCADO PARA RECOMENDAÇÕES...")

        # 1. Análise do mercado atual
        analise_mercado = self._analisar_mercado_atual()

        # 2. Análise do portfólio atual
        analise_portfolio = self.analisador_risco.analisar_risco_portfolio(portfolio) if self.analisador_risco else None

        # 3. Recomendações por categoria
        recomendacoes = {
            "posicoes_existentes": self._recomendacoes_posicoes_existentes(portfolio, analise_mercado),
            "novas_oportunidades": self._recomendacoes_novas_oportunidades(portfolio, analise_mercado),
            "gestao_risco": self._recomendacoes_gestao_risco(portfolio, analise_portfolio),
            "balanceamento": self._recomendacoes_balanceamento(portfolio, analise_mercado)
        }

        return recomendacoes

    def _analisar_mercado_atual(self) -> AnaliseMercado:
        """Analisa condições atuais do mercado"""
        # Análise baseada no cenário macro
        macro = self.cenario_macro

        # Determinar tendência principal
        if macro["sp500_trend"] == "BEARISH" and macro["vix"] > 20:
            tendencia = "BEARISH_HIGH_VOL"
        elif macro["usd_trend"] == "STABLE" and macro["volatility_regime"] == "MODERATE":
            tendencia = "SIDEWAYS_MODERATE_VOL"
        else:
            tendencia = "BULLISH_LOW_VOL"

        # Calcular volatilidade atual
        volatilidade = macro["vix"] / 100  # Normalizar

        # Correlação de mercado (simplificada)
        correlacao = 0.6 if macro["volatility_regime"] == "HIGH" else 0.3

        # Oportunidades baseadas no regime
        oportunidades = 3 if macro["volatility_regime"] == "MODERATE" else 1

        # Nível de risco
        if volatilidade > 0.25:
            risco = "ALTO"
        elif volatilidade > 0.15:
            risco = "MODERADO"
        else:
            risco = "BAIXO"

        return AnaliseMercado(
            tendencia_principal=tendencia,
            volatilidade_atual=volatilidade,
            correlacao_mercado=correlacao,
            oportunidades_identificadas=oportunidades,
            risco_mercado=risco
        )

    def _recomendacoes_posicoes_existentes(self, portfolio: dict,
                                         analise_mercado: AnaliseMercado) -> List[RecomendacaoOperacao]:
        """Recomendações para posições já existentes"""
        recomendacoes = []
        positions = portfolio.get('positions', [])
        posicoes_abertas = [p for p in positions if p.get('status') == 'OPEN']

        for pos in posicoes_abertas:
            # Análise técnica da posição
            analise_tecnica = self._analisar_posicao_tecnica(pos, analise_mercado)

            if analise_tecnica:
                recomendacoes.append(analise_tecnica)

        return recomendacoes

    def _analisar_posicao_tecnica(self, posicao: dict,
                                analise_mercado: AnaliseMercado) -> Optional[RecomendacaoOperacao]:
        """Análise técnica detalhada de uma posição"""
        ativo = posicao['currency_pair']
        # Garantir sempre utilização do preço de entrada real para cálculo de níveis
        preco_atual = posicao.get('current_price', posicao['entry_price'])
        preco_entrada = posicao['entry_price']
        direcao = posicao['direction']

        # Calcular P&L parcial
        pnl_atual = self._calcular_pnl_posicao(posicao)

        # Calcular níveis técnicos SEM usar preço atual como referência (evita erro de deslocamento de base)
        niveis_tecnicos = self._calcular_niveis_tecnicos_posicao(preco_entrada, direcao)

        # Auditoria: log dos níveis calculados para rastreabilidade
        self.logger.info(
            f"[AUDITORIA NÍVEIS] Ativo={ativo} Direção={direcao} PreçoEntrada={preco_entrada} "
            f"StopLossCalc={niveis_tecnicos['stop_loss']} TakeProfitCalc={niveis_tecnicos['take_profit']} PreçoAtual={preco_atual}"
        )

        # Lógica de recomendação baseada na análise
        if direcao == 'LONG':
            # Para posições compradas
            if preco_atual >= niveis_tecnicos['take_profit']:
                # Preço atingiu take profit - sugerir fechar posição
                return RecomendacaoOperacao(
                    tipo=TipoRecomendacao.TAKE_PROFIT,
                    ativo=ativo,
                    preco_sugerido=niveis_tecnicos['take_profit'],
                    quantidade_sugerida=None,  # Fechar parcial
                    razao=f"Preço atingiu take profit em {niveis_tecnicos['take_profit']:.4f}",
                    nivel_confianca=NivelConfianca.ALTA,
                    horizonte="INTRADAY",
                    risco_estimado=0.001,  # Risco mínimo (já em lucro)
                    reward_estimado=0.0,    # Já realizado
                    risk_reward_ratio=float('inf'),
                    ticket=posicao.get('ticket'),
                    entry_date=posicao.get('entry_date'),
                    partial_results=pnl_atual,
                    entry_price=preco_entrada,
                    direction=direcao
                )
            elif preco_atual <= niveis_tecnicos['stop_loss']:
                # Preço atingiu stop loss - sugerir fechar posição
                return RecomendacaoOperacao(
                    tipo=TipoRecomendacao.STOP_LOSS,
                    ativo=ativo,
                    preco_sugerido=niveis_tecnicos['stop_loss'],
                    quantidade_sugerida=None,  # Fechar tudo
                    razao=f"Stop loss acionado em {niveis_tecnicos['stop_loss']:.4f}",
                    nivel_confianca=NivelConfianca.MUITO_ALTA,
                    horizonte="INTRADAY",
                    risco_estimado=0.02,  # Perda máxima
                    reward_estimado=0.0,
                    risk_reward_ratio=0.0,
                    ticket=posicao.get('ticket'),
                    entry_date=posicao.get('entry_date'),
                    partial_results=pnl_atual,
                    entry_price=preco_entrada,
                    direction=direcao
                )
            else:
                # Hold - posição ainda válida
                return RecomendacaoOperacao(
                    tipo=TipoRecomendacao.HOLD,
                    ativo=ativo,
                    preco_sugerido=None,
                    quantidade_sugerida=None,
                    razao=f"Posição dentro da faixa válida. Stop Loss: {niveis_tecnicos['stop_loss']:.4f}, Take Profit: {niveis_tecnicos['take_profit']:.4f}",
                    nivel_confianca=NivelConfianca.MEDIA,
                    horizonte="SWING",
                    risco_estimado=0.01,
                    reward_estimado=0.02,
                    risk_reward_ratio=2.0,
                    ticket=posicao.get('ticket'),
                    entry_date=posicao.get('entry_date'),
                    partial_results=pnl_atual,
                    entry_price=preco_entrada,
                    direction=direcao
                )

        else:  # SHORT
            # Para posições vendidas
            if preco_atual <= niveis_tecnicos['take_profit']:
                # Preço atingiu take profit - sugerir fechar posição
                return RecomendacaoOperacao(
                    tipo=TipoRecomendacao.TAKE_PROFIT,
                    ativo=ativo,
                    preco_sugerido=niveis_tecnicos['take_profit'],
                    quantidade_sugerida=None,
                    razao=f"Preço atingiu take profit em {niveis_tecnicos['take_profit']:.4f}",
                    nivel_confianca=NivelConfianca.ALTA,
                    horizonte="INTRADAY",
                    risco_estimado=0.001,
                    reward_estimado=0.0,
                    risk_reward_ratio=float('inf'),
                    ticket=posicao.get('ticket'),
                    entry_date=posicao.get('entry_date'),
                    partial_results=pnl_atual,
                    entry_price=preco_entrada,
                    direction=direcao
                )
            elif preco_atual >= niveis_tecnicos['stop_loss']:
                # Preço atingiu stop loss - sugerir fechar posição
                return RecomendacaoOperacao(
                    tipo=TipoRecomendacao.STOP_LOSS,
                    ativo=ativo,
                    preco_sugerido=niveis_tecnicos['stop_loss'],
                    quantidade_sugerida=None,
                    razao=f"Stop loss acionado em {niveis_tecnicos['stop_loss']:.4f}",
                    nivel_confianca=NivelConfianca.MUITO_ALTA,
                    horizonte="INTRADAY",
                    risco_estimado=0.02,
                    reward_estimado=0.0,
                    risk_reward_ratio=0.0,
                    ticket=posicao.get('ticket'),
                    entry_date=posicao.get('entry_date'),
                    partial_results=pnl_atual,
                    entry_price=preco_entrada,
                    direction=direcao
                )
            else:
                # Hold
                return RecomendacaoOperacao(
                    tipo=TipoRecomendacao.HOLD,
                    ativo=ativo,
                    preco_sugerido=None,
                    quantidade_sugerida=None,
                    razao=f"Posição dentro da faixa válida. Stop Loss: {niveis_tecnicos['stop_loss']:.4f}, Take Profit: {niveis_tecnicos['take_profit']:.4f}",
                    nivel_confianca=NivelConfianca.MEDIA,
                    horizonte="SWING",
                    risco_estimado=0.01,
                    reward_estimado=0.02,
                    risk_reward_ratio=2.0,
                    ticket=posicao.get('ticket'),
                    entry_date=posicao.get('entry_date'),
                    partial_results=pnl_atual,
                    entry_price=preco_entrada,
                    direction=direcao
                )

    def _calcular_niveis_tecnicos_simulados(self, ativo: str, preco_atual: float) -> Dict[str, float]:
        """Calcula níveis técnicos simulados para um ativo"""
        # Em produção, isso usaria dados reais e cálculos técnicos
        variacao_base = 0.02  # 2% de variação típica

        return {
            'suporte_1': preco_atual * (1 - variacao_base),
            'resistencia_1': preco_atual * (1 + variacao_base),
            'suporte_2': preco_atual * (1 - variacao_base * 2),
            'resistencia_2': preco_atual * (1 + variacao_base * 2),
            'stop_loss_sugerido': preco_atual * (1 - variacao_base * 1.5) if 'SHORT' in str(ativo).upper() else preco_atual * (1 + variacao_base * 1.5)
        }

    def _calcular_niveis_tecnicos_posicao(self, preco_entrada: float, direcao: str) -> Dict[str, float]:
        """Calcula níveis técnicos baseados no preço de entrada e direção da posição"""
        # Risco de 2% por posição (stop loss)
        # Reward de 4% por posição (take profit)
        risco_percentual = 0.02  # 2%
        reward_percentual = 0.04  # 4%

        if direcao == 'LONG':
            # Para posições compradas: stop loss abaixo, take profit acima
            stop_loss = preco_entrada * (1 - risco_percentual)
            take_profit = preco_entrada * (1 + reward_percentual)
        else:  # SHORT
            # Para posições vendidas: stop loss acima, take profit abaixo
            stop_loss = preco_entrada * (1 + risco_percentual)
            take_profit = preco_entrada * (1 - reward_percentual)

        niveis = {
            'stop_loss': round(stop_loss, 4),
            'take_profit': round(take_profit, 4)
        }

        # Validação adicional: garantir que para LONG stop < entrada < take, para SHORT take < entrada < stop
        if direcao == 'LONG' and not (niveis['stop_loss'] < preco_entrada < niveis['take_profit']):
            self.logger.warning(f"[INCONSISTÊNCIA NÍVEIS] LONG com ordem incorreta: {niveis} entrada={preco_entrada}")
        if direcao == 'SHORT' and not (niveis['take_profit'] < preco_entrada < niveis['stop_loss']):
            self.logger.warning(f"[INCONSISTÊNCIA NÍVEIS] SHORT com ordem incorreta: {niveis} entrada={preco_entrada}")

        return niveis

    def _calcular_pnl_posicao(self, posicao: dict) -> float:
        """Calcula P&L atual da posição"""
        try:
            current_price = posicao.get('current_price', posicao['entry_price'])
            diferenca = current_price - posicao['entry_price']

            if posicao['direction'] == 'SHORT':
                diferenca = -diferenca

            return posicao['lots'] * posicao.get('lot_size', 100000) * diferenca
        except:
            return 0.0

    def _recomendacoes_novas_oportunidades(self, portfolio: dict,
                                         analise_mercado: AnaliseMercado) -> List[RecomendacaoOperacao]:
        """Recomendações para novas oportunidades de investimento"""
        recomendacoes = []

        # Análise baseada no cenário macro atual
        macro = self.cenario_macro

        # Oportunidades baseadas no regime de mercado
        if analise_mercado.tendencia_principal == "BEARISH_HIGH_VOL":
            # Mercado em baixa com alta volatilidade - oportunidades em defensivos
            recomendacoes.extend(self._oportunidades_defensivas())

        elif analise_mercado.tendencia_principal == "SIDEWAYS_MODERATE_VOL":
            # Mercado lateral - oportunidades em pares com momentum
            recomendacoes.extend(self._oportunidades_momentum())

        else:
            # Mercado bullish - oportunidades em risco
            recomendacoes.extend(self._oportunidades_risco())

        # Filtrar baseado no portfólio atual (evitar duplicatas)
        recomendacoes_filtradas = self._filtrar_oportunidades_existentes(recomendacoes, portfolio)

        return recomendacoes_filtradas[:3]  # Máximo 3 oportunidades

    def _oportunidades_defensivas(self) -> List[RecomendacaoOperacao]:
        """Oportunidades em ativos defensivos"""
        return [
            RecomendacaoOperacao(
                tipo=TipoRecomendacao.COMPRA,
                ativo="USDJPY",
                preco_sugerido=145.50,
                quantidade_sugerida=0.01,
                razao="Carry trade defensivo em ambiente de risk-off. JPY como moeda refúgio.",
                nivel_confianca=NivelConfianca.ALTA,
                horizonte="POSITION",
                risco_estimado=0.015,
                reward_estimado=0.045,
                risk_reward_ratio=3.0
            ),
            RecomendacaoOperacao(
                tipo=TipoRecomendacao.COMPRA,
                ativo="XAUUSD",
                preco_sugerido=1950.00,
                quantidade_sugerida=0.001,
                razao="Ouro como hedge contra volatilidade elevada do mercado.",
                nivel_confianca=NivelConfianca.MEDIA,
                horizonte="SWING",
                risco_estimado=0.025,
                reward_estimado=0.050,
                risk_reward_ratio=2.0
            )
        ]

    def _oportunidades_momentum(self) -> List[RecomendacaoOperacao]:
        """Oportunidades em pares com momentum"""
        return [
            RecomendacaoOperacao(
                tipo=TipoRecomendacao.COMPRA,
                ativo="EURUSD",
                preco_sugerido=1.0850,
                quantidade_sugerida=0.02,
                razao="Momentum positivo em EUR com dados econômicos europeus favoráveis.",
                nivel_confianca=NivelConfianca.MEDIA,
                horizonte="SWING",
                risco_estimado=0.020,
                reward_estimado=0.040,
                risk_reward_ratio=2.0
            ),
            RecomendacaoOperacao(
                tipo=TipoRecomendacao.VENDA,
                ativo="GBPUSD",
                preco_sugerido=1.2650,
                quantidade_sugerida=0.015,
                razao="Momentum negativo em GBP devido a pressões inflacionárias.",
                nivel_confianca=NivelConfianca.ALTA,
                horizonte="INTRADAY",
                risco_estimado=0.018,
                reward_estimado=0.036,
                risk_reward_ratio=2.0
            )
        ]

    def _oportunidades_risco(self) -> List[RecomendacaoOperacao]:
        """Oportunidades em ativos de risco"""
        return [
            RecomendacaoOperacao(
                tipo=TipoRecomendacao.COMPRA,
                ativo="AUDUSD",
                preco_sugerido=0.6650,
                quantidade_sugerido=0.025,
                razao="Risk-on trade com recuperação das commodities.",
                nivel_confianca=NivelConfianca.MEDIA,
                horizonte="POSITION",
                risco_estimado=0.022,
                reward_estimado=0.055,
                risk_reward_ratio=2.5
            )
        ]

    def _filtrar_oportunidades_existentes(self, recomendacoes: List[RecomendacaoOperacao],
                                        portfolio: dict) -> List[RecomendacaoOperacao]:
        """Filtra oportunidades que já existem no portfólio"""
        positions = portfolio.get('positions', [])
        ativos_existentes = {p['currency_pair'] for p in positions if p.get('status') == 'OPEN'}

        recomendacoes_filtradas = []
        for rec in recomendacoes:
            if rec.ativo not in ativos_existentes:
                recomendacoes_filtradas.append(rec)

        return recomendacoes_filtradas

    def _recomendacoes_gestao_risco(self, portfolio: dict,
                                  analise_risco) -> List[RecomendacaoOperacao]:
        """Recomendações para gestão de risco"""
        recomendacoes = []

        if not analise_risco:
            return recomendacoes

        # Recomendações baseadas no nível de risco
        if analise_risco.nivel_alerta == "CRITICO":
            recomendacoes.append(RecomendacaoOperacao(
                tipo=TipoRecomendacao.STOP_LOSS,
                ativo="PORTFOLIO",
                preco_sugerido=None,
                quantidade_sugerida=None,
                razao="RISCO CRÍTICO: Fechar posições mais arriscadas imediatamente",
                nivel_confianca=NivelConfianca.MUITO_ALTA,
                horizonte="INTRADAY",
                risco_estimado=0.0,  # Reduzindo risco
                reward_estimado=0.0,
                risk_reward_ratio=float('inf')
            ))

        elif analise_risco.nivel_alerta == "ALTO":
            recomendacoes.append(RecomendacaoOperacao(
                tipo=TipoRecomendacao.HEDGE,
                ativo="PORTFOLIO",
                preco_sugerido=None,
                quantidade_sugerida=None,
                razao="RISCO ALTO: Implementar hedges adicionais (opções ou posições contrárias)",
                nivel_confianca=NivelConfianca.ALTA,
                horizonte="INTRADAY",
                risco_estimado=0.0,
                reward_estimado=0.0,
                risk_reward_ratio=float('inf')
            ))

        # Recomendações baseadas em correlação
        if analise_risco.correlacao_maxima > 0.8:
            recomendacoes.append(RecomendacaoOperacao(
                tipo=TipoRecomendacao.DIVERSIFICACAO,
                ativo="PORTFOLIO",
                preco_sugerido=None,
                quantidade_sugerida=None,
                razao=f"CORRELAÇÃO ELEVADA ({analise_risco.correlacao_maxima:.2f}): Diversificar para ativos não correlacionados",
                nivel_confianca=NivelConfianca.ALTA,
                horizonte="SWING",
                risco_estimado=0.0,
                reward_estimado=0.0,
                risk_reward_ratio=float('inf')
            ))

        return recomendacoes

    def _recomendacoes_balanceamento(self, portfolio: dict,
                                   analise_mercado: AnaliseMercado) -> List[RecomendacaoOperacao]:
        """Recomendações para balanceamento do portfólio"""
        recomendacoes = []
        positions = portfolio.get('positions', [])
        posicoes_abertas = [p for p in positions if p.get('status') == 'OPEN']

        # Análise de concentração
        if len(posicoes_abertas) > 0:
            # Calcular exposição por moeda
            exposicao_moeda = {}
            for pos in posicoes_abertas:
                moeda = pos['currency_pair'][:3]  # Primeiras 3 letras
                valor = pos['lots'] * pos['lot_size'] * pos['entry_price']
                exposicao_moeda[moeda] = exposicao_moeda.get(moeda, 0) + valor

            # Verificar concentração excessiva
            total_exposicao = sum(exposicao_moeda.values())
            for moeda, exposicao in exposicao_moeda.items():
                percentual = exposicao / total_exposicao
                if percentual > 0.4:  # Mais de 40% em uma moeda
                    recomendacoes.append(RecomendacaoOperacao(
                        tipo=TipoRecomendacao.DIVERSIFICACAO,
                        ativo=f"EXPOSICAO_{moeda}",
                        preco_sugerido=None,
                        quantidade_sugerida=None,
                        razao=f"CONCENTRAÇÃO EXCESSIVA: {percentual:.1%} em {moeda}. Reduzir exposição.",
                        nivel_confianca=NivelConfianca.ALTA,
                        horizonte="POSITION",
                        risco_estimado=0.0,
                        reward_estimado=0.0,
                        risk_reward_ratio=float('inf')
                    ))

        # Recomendações baseadas no regime de mercado
        if analise_mercado.risco_mercado == "ALTO" and len(posicoes_abertas) > 3:
            recomendacoes.append(RecomendacaoOperacao(
                tipo=TipoRecomendacao.DIVERSIFICACAO,
                ativo="PORTFOLIO",
                preco_sugerido=None,
                quantidade_sugerida=None,
                razao="RISCO DE MERCADO ALTO: Reduzir número de posições para 2-3",
                nivel_confianca=NivelConfianca.MEDIA,
                horizonte="SWING",
                risco_estimado=0.0,
                reward_estimado=0.0,
                risk_reward_ratio=float('inf')
            ))

        return recomendacoes

    def gerar_relatorio_recomendacoes(self, recomendacoes: Dict[str, List[RecomendacaoOperacao]]) -> str:
        """Gera relatório formatado das recomendações"""
        relatorio = []
        relatorio.append("# 🤖 RECOMENDAÇÕES INTELIGENTES DO FUNDO")
        relatorio.append(f"**Data:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        relatorio.append("")

        total_recomendacoes = sum(len(recs) for recs in recomendacoes.values())
        relatorio.append(f"**Total de Recomendações:** {total_recomendacoes}")
        relatorio.append("")

        # Recomendações por categoria
        for categoria, recs in recomendacoes.items():
            if not recs:
                continue

            titulo_categoria = categoria.replace('_', ' ').title()
            relatorio.append(f"## {titulo_categoria}")
            relatorio.append("")

            for i, rec in enumerate(recs, 1):
                relatorio.append(f"### {i}. {rec.tipo.value} - {rec.ativo}")

                # Informações da posição (se disponível)
                if rec.ticket:
                    relatorio.append(f"**Ticket:** #{rec.ticket}")
                if rec.entry_date:
                    # Formatar data para exibição
                    try:
                        data_formatada = rec.entry_date[:10] if len(rec.entry_date) > 10 else rec.entry_date
                        relatorio.append(f"**Data Entrada:** {data_formatada}")
                    except:
                        relatorio.append(f"**Data Entrada:** {rec.entry_date}")
                if rec.entry_price is not None:
                    relatorio.append(f"**Preço Entrada:** {rec.entry_price:.4f}")
                if rec.direction:
                    relatorio.append(f"**Direção:** {rec.direction}")
                if rec.partial_results is not None:
                    relatorio.append(f"**Resultado Parcial:** ${rec.partial_results:+.2f}")

                if rec.preco_sugerido:
                    relatorio.append(f"**Preço Sugerido:** {rec.preco_sugerido:.4f}")

                if rec.quantidade_sugerida:
                    relatorio.append(f"**Quantidade Sugerida:** {rec.quantidade_sugerida:.4f}")

                relatorio.append(f"**Confiança:** {rec.nivel_confianca.value}")
                relatorio.append(f"**Horizonte:** {rec.horizonte}")
                relatorio.append(f"**Risk/Reward:** 1:{rec.risk_reward_ratio:.1f}")
                relatorio.append(f"**Razão:** {rec.razao}")
                relatorio.append("")

        return "\n".join(relatorio)