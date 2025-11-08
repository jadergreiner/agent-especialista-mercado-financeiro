#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ANALISADOR DE RISCO DO FUNDO

Módulo especializado para análise de risco do portfólio do fundo,
integrando com modulo_correlacao_avancada para análise de exposição
sistêmica e cálculo de Value at Risk (VaR).
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# Imports dos módulos especializados
try:
    from .modulo_correlacao_avancada import ModuloCorrelacaoAvancada
    from .calculador_niveis_precisao import CalculadorNiveisPrecisao
except ImportError:
    try:
        from modulo_correlacao_avancada import ModuloCorrelacaoAvancada
        from calculador_niveis_precisao import CalculadorNiveisPrecisao
    except ImportError:
        ModuloCorrelacaoAvancada = None
        CalculadorNiveisPrecisao = None

@dataclass
class AnaliseRisco:
    """Estrutura para análise de risco"""
    var_95: float  # Value at Risk 95%
    var_99: float  # Value at Risk 99%
    volatilidade_portfolio: float
    correlacao_maxima: float
    exposicao_concentrada: float
    risco_sistemico: float
    recomendacao_risco: str
    nivel_alerta: str  # BAIXO, MODERADO, ALTO, CRITICO
    concentracao_maxima: float = 0.0  # Concentração máxima em uma moeda
    moeda_concentrada: str = "N/A"  # Moeda com maior concentração
    recomendacoes: List[str] = None  # Lista de recomendações de risco

    def __post_init__(self):
        """Inicializar lista vazia se None"""
        if self.recomendacoes is None:
            self.recomendacoes = []

@dataclass
class PosicaoRisco:
    """Estrutura para posição com análise de risco"""
    ativo: str
    exposicao: float
    risco_individual: float
    correlacao_media: float
    contribuicao_var: float
    nivel_risco: str

class AnalisadorRiscoFundo:
    """
    Analisador de Risco do Fundo - Análise completa de exposição e risco
    """

    def __init__(self):
        self.modulo_correlacao = ModuloCorrelacaoAvancada() if ModuloCorrelacaoAvancada else None
        self.calculador_niveis = CalculadorNiveisPrecisao() if CalculadorNiveisPrecisao else None

        # Parâmetros de risco
        self.confidence_levels = [0.95, 0.99]
        self.holding_period = 1  # 1 dia
        self.capital_base = 100000  # USD

    def analisar_risco_portfolio(self, portfolio: dict) -> AnaliseRisco:
        """
        Análise completa de risco do portfólio
        """
        positions = portfolio.get('positions', [])
        posicoes_abertas = [p for p in positions if p.get('status') == 'OPEN']

        if not posicoes_abertas:
            return self._analise_risco_vazio()

        # 1. Calcular retornos históricos simulados
        retornos_historicos = self._gerar_retornos_historicos(posicoes_abertas)

        # 2. Calcular pesos do portfólio
        pesos = self._calcular_pesos_portfolio(posicoes_abertas)

        # 3. Calcular VaR
        var_95, var_99 = self._calcular_var_portfolio(retornos_historicos, pesos)

        # 4. Calcular volatilidade do portfólio
        volatilidade = self._calcular_volatilidade_portfolio(retornos_historicos, pesos)

        # 5. Análise de correlação
        correlacao_maxima = self._analisar_correlacao_maxima(posicoes_abertas)

        # 6. Exposição concentrada
        exposicao_concentrada = self._calcular_exposicao_concentrada(posicoes_abertas)

        # 7. Risco sistêmico
        risco_sistemico = self._calcular_risco_sistemico(posicoes_abertas, correlacao_maxima)

        # 8. Calcular concentração por moeda
        concentracao_maxima, moeda_concentrada = self._calcular_concentracao_moeda(posicoes_abertas)

        # 9. Recomendação baseada na análise
        recomendacao, nivel_alerta = self._gerar_recomendacao_risco(
            var_95, var_99, volatilidade, correlacao_maxima,
            exposicao_concentrada, risco_sistemico
        )

        # 10. Gerar recomendações específicas
        recomendacoes = self._gerar_recomendacoes_especificas(
            var_95, volatilidade, correlacao_maxima,
            exposicao_concentrada, concentracao_maxima
        )

        return AnaliseRisco(
            var_95=var_95,
            var_99=var_99,
            volatilidade_portfolio=volatilidade,
            correlacao_maxima=correlacao_maxima,
            exposicao_concentrada=exposicao_concentrada,
            risco_sistemico=risco_sistemico,
            recomendacao_risco=recomendacao,
            nivel_alerta=nivel_alerta,
            concentracao_maxima=concentracao_maxima,
            moeda_concentrada=moeda_concentrada,
            recomendacoes=recomendacoes
        )

    def _analise_risco_vazio(self) -> AnaliseRisco:
        """Análise de risco para portfólio vazio"""
        return AnaliseRisco(
            var_95=0.0,
            var_99=0.0,
            volatilidade_portfolio=0.0,
            correlacao_maxima=0.0,
            exposicao_concentrada=0.0,
            risco_sistemico=0.0,
            recomendacao_risco="✅ PORTFÓLIO SEM RISCO - Nenhuma posição aberta",
            nivel_alerta="BAIXO",
            concentracao_maxima=0.0,
            moeda_concentrada="N/A",
            recomendacoes=[]
        )

    def _gerar_retornos_historicos(self, posicoes: List[dict],
                                  dias: int = 252) -> pd.DataFrame:
        """
        Gera retornos históricos simulados para as posições
        Em produção, usaria dados reais de mercado
        """
        np.random.seed(42)  # Para reprodutibilidade

        ativos = [pos['currency_pair'] for pos in posicoes]
        retornos = pd.DataFrame(index=range(dias), columns=ativos)

        # Volatilidades típicas por ativo (anualizadas)
        volatilidades = {
            'EURUSD': 0.08,
            'GBPUSD': 0.10,
            'USDJPY': 0.09,
            'AUDUSD': 0.11,
            'USDCAD': 0.07,
            'USDCHF': 0.08,
            'NZDUSD': 0.12,
            'XAUUSD': 0.15,  # Ouro
            'default': 0.10
        }

        # Gerar retornos simulados
        for ativo in ativos:
            vol_anual = volatilidades.get(ativo, volatilidades['default'])
            vol_diaria = vol_anual / np.sqrt(252)  # Volatilidade diária

            # Retornos normais com drift
            drift = 0.0001  # Drift diário pequeno
            retornos_ativos = np.random.normal(drift, vol_diaria, dias)
            retornos[ativo] = retornos_ativos

        return retornos

    def _calcular_pesos_portfolio(self, posicoes: List[dict]) -> np.ndarray:
        """Calcula pesos do portfólio baseado na exposição"""
        exposicoes = []
        for pos in posicoes:
            valor_posicao = pos['lots'] * pos['lot_size'] * pos['entry_price']
            exposicoes.append(valor_posicao)

        exposicoes = np.array(exposicoes)
        pesos = exposicoes / exposicoes.sum()

        return pesos

    def _calcular_var_portfolio(self, retornos: pd.DataFrame,
                               pesos: np.ndarray) -> Tuple[float, float]:
        """
        Calcula Value at Risk (VaR) do portfólio
        """
        # Calcular retornos do portfólio
        retornos_portfolio = retornos.dot(pesos)

        # VaR histórico
        var_95 = np.percentile(retornos_portfolio, 5) * self.capital_base
        var_99 = np.percentile(retornos_portfolio, 1) * self.capital_base

        return abs(var_95), abs(var_99)  # Retornar valores positivos

    def _calcular_volatilidade_portfolio(self, retornos: pd.DataFrame,
                                       pesos: np.ndarray) -> float:
        """Calcula volatilidade anualizada do portfólio"""
        retornos_portfolio = retornos.dot(pesos)
        volatilidade_diaria = retornos_portfolio.std()
        volatilidade_anualizada = volatilidade_diaria * np.sqrt(252)

        return volatilidade_anualizada

    def _analisar_correlacao_maxima(self, posicoes: List[dict]) -> float:
        """Analisa correlação máxima entre posições"""
        if len(posicoes) < 2:
            return 0.0

        # Matriz de correlação simplificada
        # Em produção, usaria dados históricos reais
        correlacoes_base = {
            ('EURUSD', 'GBPUSD'): 0.75,
            ('EURUSD', 'USDCHF'): 0.65,
            ('GBPUSD', 'USDCHF'): 0.55,
            ('USDJPY', 'USDCHF'): -0.60,
            ('EURUSD', 'USDJPY'): -0.45,
            ('GBPUSD', 'USDJPY'): -0.40,
        }

        max_correlacao = 0.0
        ativos = [pos['currency_pair'] for pos in posicoes]

        for i, ativo1 in enumerate(ativos):
            for ativo2 in ativos[i+1:]:
                chave = tuple(sorted([ativo1, ativo2]))
                correlacao = correlacoes_base.get(chave, 0.3)  # Correlação padrão
                max_correlacao = max(max_correlacao, abs(correlacao))

        return max_correlacao

    def _calcular_exposicao_concentrada(self, posicoes: List[dict]) -> float:
        """Calcula exposição concentrada (maior exposição individual)"""
        if not posicoes:
            return 0.0

        exposicoes = []
        for pos in posicoes:
            valor_posicao = pos['lots'] * pos['lot_size'] * pos['entry_price']
            exposicoes.append(valor_posicao)

        max_exposicao = max(exposicoes)
        total_exposicao = sum(exposicoes)

        return max_exposicao / total_exposicao if total_exposicao > 0 else 0.0

    def _calcular_risco_sistemico(self, posicoes: List[dict],
                                 correlacao_maxima: float) -> float:
        """Calcula risco sistêmico baseado na exposição e correlação"""
        concentracao = self._calcular_exposicao_concentrada(posicoes)
        num_posicoes = len(posicoes)

        # Fórmula simplificada de risco sistêmico
        # Maior concentração + impacto da correlação
        risco_base = concentracao * (1 + correlacao_maxima)

        # Penalidade por número excessivo de posições
        if num_posicoes > 10:
            risco_base *= 1.5
        elif num_posicoes > 5:
            risco_base *= 1.2

        return min(risco_base, 1.0)  # Limitar a 100%

    def _gerar_recomendacao_risco(self, var_95: float, var_99: float,
                                 volatilidade: float, correlacao_max: float,
                                 exposicao_concentrada: float,
                                 risco_sistemico: float) -> Tuple[str, str]:
        """Gera recomendação baseada nos indicadores de risco"""

        # Limites de alerta
        var_95_limite = self.capital_base * 0.05  # 5% do capital
        var_99_limite = self.capital_base * 0.10  # 10% do capital
        vol_limite = 0.25  # 25% anualizada
        correlacao_limite = 0.8
        concentracao_limite = 0.3  # 30%
        risco_sistemico_limite = 0.6  # 60%

        alertas = []

        # Análise VaR
        if var_95 > var_95_limite:
            alertas.append("VaR 95% elevado")
        if var_99 > var_99_limite:
            alertas.append("VaR 99% crítico")

        # Análise volatilidade
        if volatilidade > vol_limite:
            alertas.append("Volatilidade excessiva")

        # Análise correlação
        if correlacao_max > correlacao_limite:
            alertas.append("Correlação elevada entre ativos")

        # Análise concentração
        if exposicao_concentrada > concentracao_limite:
            alertas.append("Concentração excessiva")

        # Análise risco sistêmico
        if risco_sistemico > risco_sistemico_limite:
            alertas.append("Risco sistêmico alto")

        # Determinar nível de alerta
        if len(alertas) >= 3:
            nivel = "CRITICO"
            recomendacao = "🚨 RISCO CRÍTICO: Reduzir exposição imediatamente. " \
                          "Fechar posições concentradas e diversificar."
        elif len(alertas) >= 2:
            nivel = "ALTO"
            recomendacao = "⚠️ RISCO ALTO: Implementar proteções adicionais. " \
                          "Revisar stops e considerar redução de posições correlacionadas."
        elif len(alertas) >= 1:
            nivel = "MODERADO"
            recomendacao = "⚠️ RISCO MODERADO: Monitorar de perto. " \
                          "Ajustar stops e avaliar diversificação."
        else:
            nivel = "BAIXO"
            recomendacao = "✅ RISCO CONTROLADO: Manter estratégia atual. " \
                          "Continuar monitoramento regular."

        if alertas:
            recomendacao += f" Alertas: {', '.join(alertas)}."

        return recomendacao, nivel

    def analisar_posicoes_risco(self, portfolio: dict) -> List[PosicaoRisco]:
        """
        Análise detalhada de risco por posição
        """
        positions = portfolio.get('positions', [])
        posicoes_abertas = [p for p in positions if p.get('status') == 'OPEN']

        analises_posicoes = []

        for pos in posicoes_abertas:
            # Calcular exposição
            exposicao = pos['lots'] * pos['lot_size'] * pos['entry_price']

            # Calcular risco individual (baseado em stop loss)
            risco_individual = self._calcular_risco_posicao(pos)

            # Calcular correlação média (simplificada)
            correlacao_media = self._calcular_correlacao_media_posicao(pos, posicoes_abertas)

            # Contribuição para VaR (simplificada)
            contribuicao_var = exposicao / self.capital_base * 0.02  # 2% estimado

            # Determinar nível de risco da posição
            nivel_risco = self._determinar_nivel_risco_posicao(
                risco_individual, correlacao_media, exposicao
            )

            analise = PosicaoRisco(
                ativo=pos['currency_pair'],
                exposicao=exposicao,
                risco_individual=risco_individual,
                correlacao_media=correlacao_media,
                contribuicao_var=contribuicao_var,
                nivel_risco=nivel_risco
            )

            analises_posicoes.append(analise)

        return analises_posicoes

    def _calcular_risco_posicao(self, posicao: dict) -> float:
        """Calcula risco individual da posição baseado em stop loss"""
        if posicao.get('stop_loss'):
            diferenca = abs(posicao['entry_price'] - posicao['stop_loss'])
            return diferenca * posicao['lots'] * posicao['lot_size']
        return 0.0

    def _calcular_correlacao_media_posicao(self, posicao: dict,
                                          todas_posicoes: List[dict]) -> float:
        """Calcula correlação média da posição com outras"""
        if len(todas_posicoes) <= 1:
            return 0.0

        # Correlações simplificadas
        correlacoes_base = {
            'EURUSD': 0.6,
            'GBPUSD': 0.7,
            'USDJPY': -0.5,
            'USDCHF': -0.4,
            'AUDUSD': 0.5,
            'default': 0.3
        }

        ativo = posicao['currency_pair']
        correlacao_base = correlacoes_base.get(ativo, correlacoes_base['default'])

        # Média ponderada com outras posições
        outras_posicoes = [p for p in todas_posicoes if p != posicao]
        if not outras_posicoes:
            return correlacao_base

        # Simplificação: média das correlações
        return correlacao_base * 0.7  # Fator de redução

    def _determinar_nivel_risco_posicao(self, risco_individual: float,
                                       correlacao: float, exposicao: float) -> str:
        """Determina nível de risco da posição"""

        # Normalizar valores
        risco_relativo = risco_individual / self.capital_base
        exposicao_relativa = exposicao / self.capital_base

        # Critérios de classificação
        if risco_relativo > 0.05 or exposicao_relativa > 0.2 or correlacao > 0.8:
            return "CRÍTICO"
        elif risco_relativo > 0.03 or exposicao_relativa > 0.1 or correlacao > 0.6:
            return "ALTO"
        elif risco_relativo > 0.01 or exposicao_relativa > 0.05 or correlacao > 0.4:
            return "MODERADO"
        else:
            return "BAIXO"

    def calcular_stress_test(self, portfolio: dict,
                           cenarios: List[str] = None) -> Dict[str, float]:
        """
        Executa stress test em diferentes cenários
        """
        if cenarios is None:
            cenarios = [
                "crash_2008",      # -50% em ações
                "flash_crash",     # Movimento extremo intraday
                "high_volatility", # Volatilidade extrema
                "currency_crisis", # Crise cambial
                "interest_rate_hike" # Alta de juros
            ]

        resultados = {}

        for cenario in cenarios:
            perda_estimada = self._simular_cenario_stress(portfolio, cenario)
            resultados[cenario] = perda_estimada

        return resultados

    def _simular_cenario_stress(self, portfolio: dict, cenario: str) -> float:
        """Simula perda em cenário de stress"""
        positions = portfolio.get('positions', [])
        posicoes_abertas = [p for p in positions if p.get('status') == 'OPEN']

        perda_total = 0

        # Impactos por cenário (simplificados)
        impactos = {
            "crash_2008": {
                "EURUSD": -0.05,
                "GBPUSD": -0.08,
                "USDJPY": 0.03,
                "default": -0.10
            },
            "flash_crash": {
                "EURUSD": -0.02,
                "GBPUSD": -0.03,
                "USDJPY": 0.01,
                "default": -0.05
            },
            "high_volatility": {
                "EURUSD": -0.03,
                "GBPUSD": -0.04,
                "USDJPY": 0.02,
                "default": -0.06
            },
            "currency_crisis": {
                "EURUSD": -0.15,
                "GBPUSD": -0.12,
                "USDJPY": 0.08,
                "default": -0.20
            },
            "interest_rate_hike": {
                "EURUSD": 0.02,
                "GBPUSD": 0.03,
                "USDJPY": -0.05,
                "default": -0.03
            }
        }

        impacto_cenario = impactos.get(cenario, impactos["high_volatility"])

        for pos in posicoes_abertas:
            ativo = pos['currency_pair']
            impacto = impacto_cenario.get(ativo, impacto_cenario['default'])

            # Aplicar impacto à posição
            if pos['direction'] == 'SHORT':
                impacto = -impacto

            valor_posicao = pos['lots'] * pos['lot_size'] * pos['entry_price']
            perda_posicao = valor_posicao * abs(impacto)
            perda_total += perda_posicao

        return perda_total

    def _calcular_concentracao_moeda(self, posicoes: List[dict]) -> Tuple[float, str]:
        """Calcular concentração máxima por moeda"""
        exposicao_moedas = {}
        exposicao_total = 0

        for pos in posicoes:
            pair = pos['currency_pair']
            direction = pos['direction']
            valor_posicao = pos['lots'] * pos['lot_size'] * pos['entry_price']
            exposicao_total += abs(valor_posicao)

            # Extrair moedas do par (ex: EUR/USD -> EUR, USD)
            if '/' in pair:
                moeda_base, moeda_cotacao = pair.split('/')
            else:
                # Tentar formatos como EURUSD, XAUUSD
                if len(pair) == 6:
                    moeda_base = pair[:3]
                    moeda_cotacao = pair[3:]
                else:
                    continue

            # Calcular exposição por moeda
            if direction == 'LONG':
                exposicao_moedas[moeda_base] = exposicao_moedas.get(moeda_base, 0) + valor_posicao
                exposicao_moedas[moeda_cotacao] = exposicao_moedas.get(moeda_cotacao, 0) - valor_posicao
            else:  # SHORT
                exposicao_moedas[moeda_base] = exposicao_moedas.get(moeda_base, 0) - valor_posicao
                exposicao_moedas[moeda_cotacao] = exposicao_moedas.get(moeda_cotacao, 0) + valor_posicao

        if not exposicao_moedas or exposicao_total == 0:
            return 0.0, "N/A"

        # Encontrar moeda com maior exposição absoluta
        moeda_max = max(exposicao_moedas.items(), key=lambda x: abs(x[1]))
        concentracao = abs(moeda_max[1]) / exposicao_total if exposicao_total > 0 else 0

        return concentracao, moeda_max[0]

    def _gerar_recomendacoes_especificas(self, var_95: float, volatilidade: float,
                                        correlacao: float, exposicao: float,
                                        concentracao: float) -> List[str]:
        """Gerar lista de recomendações específicas baseadas nas métricas"""
        recomendacoes = []

        # Limites de risco
        LIMITE_VAR = self.capital_base * 0.02  # 2% do capital
        LIMITE_VOLATILIDADE = 0.15  # 15%
        LIMITE_CORRELACAO = 0.7  # 70%
        LIMITE_EXPOSICAO = 0.25  # 25%
        LIMITE_CONCENTRACAO = 0.30  # 30%

        if var_95 > LIMITE_VAR:
            recomendacoes.append(f"⚠️ VaR excede limite: ${var_95:,.0f} > ${LIMITE_VAR:,.0f} - Reduzir posições")

        if volatilidade > LIMITE_VOLATILIDADE:
            recomendacoes.append(f"⚠️ Volatilidade alta: {volatilidade:.1%} > {LIMITE_VOLATILIDADE:.1%} - Diversificar")

        if correlacao > LIMITE_CORRELACAO:
            recomendacoes.append(f"⚠️ Correlação alta: {correlacao:.1%} > {LIMITE_CORRELACAO:.1%} - Descorrelacionar posições")

        if exposicao > LIMITE_EXPOSICAO:
            recomendacoes.append(f"⚠️ Exposição concentrada: {exposicao:.1%} > {LIMITE_EXPOSICAO:.1%} - Redistribuir")

        if concentracao > LIMITE_CONCENTRACAO:
            recomendacoes.append(f"⚠️ Concentração em moeda: {concentracao:.1%} > {LIMITE_CONCENTRACAO:.1%} - Balancear exposição")

        if not recomendacoes:
            recomendacoes.append("✅ Risco dentro dos limites aceitáveis")

        return recomendacoes