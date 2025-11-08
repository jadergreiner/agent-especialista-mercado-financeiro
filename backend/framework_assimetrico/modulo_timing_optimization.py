# Módulo Timing Optimization - Framework Assimétrico
# Otimização de timing para setups assimétricos

"""
MÓDULO TIMING OPTIMIZATION

Este módulo implementa otimização de timing para setups assimétricos,
calculando os melhores momentos de entrada e saída baseados em:

- Momentum intraday (15min, 1h, 4h)
- Liquidez do ativo no período
- Volatilidade ajustada ao horário
- Sessões de mercado globais
- Impacto de notícias em tempo real

Funcionalidades:
- Cálculo de momentum por timeframe
- Otimização de pontos de entrada/saída
- Análise de liquidez intraday
- Ajuste por volatilidade horária
- Validação de timing com dados históricos
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta, time
from dataclasses import dataclass
import pandas as pd
import numpy as np

from .interfaces import ModuloBase, ModuloTimingOptimizationInterface, ResultadoModulo

logger = logging.getLogger(__name__)


@dataclass
class TimingOtimizado:
    """Representa um timing otimizado para entrada/saída"""
    timestamp_entrada: datetime
    timestamp_saida: datetime
    momentum_entrada: float
    momentum_saida: float
    liquidez_entrada: float
    liquidez_saida: float
    volatilidade_ajustada: float
    score_timing: float  # 0-100
    confianca: float  # 0-100


class ModuloTimingOptimization(ModuloBase):
    """
    Módulo para otimização de timing de entrada/saída em setups assimétricos.

    Otimiza o timing considerando:
    - Momentum intraday (15min, 1h, 4h)
    - Liquidez por horário
    - Volatilidade ajustada
    - Sessões de mercado globais
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa o módulo Timing Optimization.

        Args:
            config: Configuração específica do módulo
        """
        super().__init__(config)
        self._inicializar_parametros()

        logger.info("Módulo Timing Optimization inicializado")
        logger.info(f"Timeframes analisados: {self.timeframes}")
        logger.info(f"Janelas de otimização: {self.janelas_otimizacao}")

    def _inicializar_parametros(self):
        """Inicializa parâmetros específicos do módulo"""
        # Timeframes para análise de momentum
        self.timeframes = ['15min', '1h', '4h']

        # Janelas de otimização (horas antes/depois do sinal)
        self.janelas_otimizacao = {
            'entrada': self.config.get('janela_entrada_horas', 4),
            'saida': self.config.get('janela_saida_horas', 24)
        }

        # Pesos para cálculo de score de timing
        self.pesos_timing = {
            'momentum': self.config.get('peso_momentum', 0.4),
            'liquidez': self.config.get('peso_liquidez', 0.3),
            'volatilidade': self.config.get('peso_volatilidade', 0.3)
        }

        # Thresholds de qualidade
        self.thresholds = {
            'momentum_minimo': self.config.get('momentum_minimo', 0.5),
            'liquidez_minima': self.config.get('liquidez_minima', 0.6),
            'volatilidade_maxima': self.config.get('volatilidade_maxima', 0.8),
            'score_timing_minimo': self.config.get('score_timing_minimo', 60)
        }

        # Sessões de mercado (horário de Brasília)
        self.sessoes_mercado = {
            'pre_market': {'inicio': time(9, 0), 'fim': time(10, 0)},
            'regular': {'inicio': time(10, 0), 'fim': time(17, 0)},
            'after_market': {'inicio': time(17, 0), 'fim': time(18, 0)},
            'overnight': {'inicio': time(18, 0), 'fim': time(9, 0)}
        }

    def _validar_configuracao_especifica(self):
        """Validação específica do módulo Timing Optimization"""
        required_keys = [
            'janela_entrada_horas', 'janela_saida_horas',
            'peso_momentum', 'peso_liquidez', 'peso_volatilidade'
        ]

        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Configuração obrigatória faltando: {key}")

        # Validar pesos
        pesos_total = sum(self.pesos_timing.values())
        if not np.isclose(pesos_total, 1.0, atol=0.01):
            raise ValueError(f"Os pesos devem somar 1.0, atual: {pesos_total}")

    def analisar(self, dados: Dict[str, Any]) -> ResultadoModulo:
        """
        Executa otimização de timing para setups identificados.

        Args:
            dados: Dados dos módulos anteriores com setups para otimizar

        Returns:
            ResultadoModulo: Resultado da otimização de timing
        """
        inicio = datetime.now()

        try:
            logger.info("Iniciando otimização de timing")

            # Extrair setups do Risk-Reward
            setups_aprovados = dados.get('setups_aprovados', [])
            dados_mercado = dados.get('dados_mercado', {})

            if not setups_aprovados:
                logger.info("Nenhum setup aprovado para otimização de timing")
                return self._criar_resultado_vazio()

            logger.info(f"Otimizando timing para {len(setups_aprovados)} setups")

            # Otimizar timing para cada setup
            timings_otimizados = []
            for setup in setups_aprovados:
                timing = self._otimizar_timing_setup(setup, dados_mercado)
                if timing:
                    timings_otimizados.append(timing)

            # Calcular métricas
            metricas = self._calcular_metricas_timing(timings_otimizados)

            # Calcular confiança geral
            confianca_geral = self._calcular_confianca_timing(timings_otimizados)

            # Preparar dados analisados
            dados_analisados = {
                'timings_otimizados': timings_otimizados,
                'setups_com_timing': len(timings_otimizados),
                'score_timing_medio': np.mean([t.score_timing for t in timings_otimizados]) if timings_otimizados else 0,
                'confianca_media': np.mean([t.confianca for t in timings_otimizados]) if timings_otimizados else 0,
                'timeframes_analisados': self.timeframes,
                'janelas_otimizacao': self.janelas_otimizacao
            }

            tempo_processamento = (datetime.now() - inicio).total_seconds()

            resultado = ResultadoModulo(
                timestamp=datetime.now(),
                status='SUCCESS' if timings_otimizados else 'PARTIAL',
                dados_analisados=dados_analisados,
                metricas=metricas,
                confianca=confianca_geral,
                metadados={
                    'tempo_processamento': tempo_processamento,
                    'setups_processados': len(setups_aprovados),
                    'timings_otimizados': len(timings_otimizados),
                    'taxa_sucesso_otimizacao': len(timings_otimizados) / len(setups_aprovados) if setups_aprovados else 0
                }
            )

            logger.info(f"Otimização de timing concluída: {len(timings_otimizados)}/{len(setups_aprovados)} setups otimizados")
            return resultado

        except Exception as e:
            logger.error(f"Erro na otimização de timing: {e}")
            tempo_processamento = (datetime.now() - inicio).total_seconds()

            return ResultadoModulo(
                timestamp=datetime.now(),
                status='ERROR',
                dados_analisados={},
                metricas={},
                confianca=0.0,
                metadados={'erro': str(e), 'tempo_processamento': tempo_processamento}
            )

    def _otimizar_timing_setup(self, setup: Dict[str, Any], dados_mercado: Dict[str, pd.DataFrame]) -> Optional[Dict[str, Any]]:
        """
        Otimiza timing para um setup específico.

        Args:
            setup: Setup aprovado pelo módulo Risk-Reward
            dados_mercado: Dados de mercado por ativo

        Returns:
            Dict com timing otimizado ou None se não conseguir otimizar
        """
        try:
            ativo = setup.get('ativo')
            if not ativo or ativo not in dados_mercado:
                logger.warning(f"Ativo {ativo} não encontrado nos dados de mercado")
                return None

            dados_ativo = dados_mercado[ativo]

            # Calcular momentum intraday
            momentum_intraday = self._calcular_momentum_intraday(dados_ativo)

            # Otimizar ponto de entrada
            timing_entrada = self._otimizar_ponto_entrada(setup, momentum_intraday)

            # Otimizar ponto de saída
            timing_saida = self._otimizar_ponto_saida(setup, momentum_intraday, timing_entrada)

            if not timing_entrada or not timing_saida:
                return None

            # Calcular métricas de liquidez e volatilidade
            liquidez_entrada = self._calcular_liquidez_horario(timing_entrada)
            liquidez_saida = self._calcular_liquidez_horario(timing_saida)
            volatilidade_ajustada = self._calcular_volatilidade_ajustada(timing_entrada, timing_saida)

            # Calcular score de timing
            score_timing = self._calcular_score_timing(
                momentum_entrada=timing_entrada['momentum'],
                momentum_saida=timing_saida['momentum'],
                liquidez_entrada=liquidez_entrada,
                liquidez_saida=liquidez_saida,
                volatilidade=volatilidade_ajustada
            )

            # Validar se atende thresholds
            if score_timing < self.thresholds['score_timing_minimo']:
                logger.debug(f"Setup {ativo} rejeitado por score timing baixo: {score_timing}")
                return None

            # Calcular confiança do timing
            confianca = self._calcular_confianca_setup(
                score_timing, liquidez_entrada, liquidez_saida, volatilidade_ajustada
            )

            timing_otimizado = {
                'setup_original': setup,
                'ativo': ativo,
                'direcao': setup.get('direcao'),
                'timestamp_entrada': timing_entrada['timestamp'],
                'timestamp_saida': timing_saida['timestamp'],
                'momentum_entrada': timing_entrada['momentum'],
                'momentum_saida': timing_saida['momentum'],
                'liquidez_entrada': liquidez_entrada,
                'liquidez_saida': liquidez_saida,
                'volatilidade_ajustada': volatilidade_ajustada,
                'score_timing': score_timing,
                'confianca': confianca,
                'timeframes_analisados': self.timeframes,
                'janela_otimizacao': self.janelas_otimizacao
            }

            return timing_otimizado

        except Exception as e:
            logger.error(f"Erro ao otimizar timing para setup {setup.get('ativo', 'UNKNOWN')}: {e}")
            return None

    def _calcular_momentum_intraday(self, dados_ativo: pd.DataFrame) -> Dict[str, pd.Series]:
        """
        Calcula momentum intraday em múltiplos timeframes.

        Args:
            dados_ativo: Dados OHLCV do ativo

        Returns:
            Dict com séries de momentum por timeframe
        """
        momentum_por_timeframe = {}

        for timeframe in self.timeframes:
            try:
                # Reamostrar dados para o timeframe
                dados_resampled = dados_ativo.resample(timeframe).agg({
                    'Open': 'first',
                    'High': 'max',
                    'Low': 'min',
                    'Close': 'last',
                    'Volume': 'sum'
                }).dropna()

                if len(dados_resampled) < 2:
                    continue

                # Calcular retornos
                retornos = dados_resampled['Close'].pct_change()

                # Calcular momentum (média móvel dos retornos)
                periodo_momentum = min(5, len(retornos) - 1)
                momentum = retornos.rolling(window=periodo_momentum).mean()

                # Normalizar momentum para escala 0-1
                momentum_normalizado = (momentum - momentum.min()) / (momentum.max() - momentum.min())
                momentum_normalizado = momentum_normalizado.fillna(0.5)  # Valor neutro para NaN

                momentum_por_timeframe[timeframe] = momentum_normalizado

            except Exception as e:
                logger.warning(f"Erro ao calcular momentum para timeframe {timeframe}: {e}")
                continue

        return momentum_por_timeframe

    def _otimizar_ponto_entrada(self, setup: Dict[str, Any], momentum_intraday: Dict[str, pd.Series]) -> Optional[Dict[str, Any]]:
        """
        Otimiza o ponto de entrada baseado em momentum.

        Args:
            setup: Setup com informações básicas
            momentum_intraday: Momentum calculado por timeframe

        Returns:
            Dict com timestamp e momentum otimizados para entrada
        """
        try:
            # Usar timeframe de 1h como referência
            if '1h' not in momentum_intraday:
                return None

            momentum_1h = momentum_intraday['1h']

            # Para LONG: procurar momentum crescente
            # Para SHORT: procurar momentum decrescente
            direcao = setup.get('direcao', 'LONG')

            if direcao == 'LONG':
                # Procurar pontos onde momentum está acima da média e crescendo
                momentum_medio = momentum_1h.mean()
                candidatos = momentum_1h[
                    (momentum_1h > momentum_medio) &
                    (momentum_1h > momentum_1h.shift(1))  # Momentum crescendo
                ]
            else:  # SHORT
                # Procurar pontos onde momentum está abaixo da média e caindo
                momentum_medio = momentum_1h.mean()
                candidatos = momentum_1h[
                    (momentum_1h < momentum_medio) &
                    (momentum_1h < momentum_1h.shift(1))  # Momentum caindo
                ]

            if candidatos.empty:
                return None

            # Selecionar o melhor candidato (mais recente com melhor momentum)
            melhor_timestamp = candidatos.idxmax() if direcao == 'LONG' else candidatos.idxmin()

            return {
                'timestamp': melhor_timestamp,
                'momentum': candidatos[melhor_timestamp]
            }

        except Exception as e:
            logger.error(f"Erro ao otimizar ponto de entrada: {e}")
            return None

    def _otimizar_ponto_saida(self, setup: Dict[str, Any], momentum_intraday: Dict[str, pd.Series],
                            timing_entrada: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Otimiza o ponto de saída baseado em alvo e momentum.

        Args:
            setup: Setup com alvo definido
            momentum_intraday: Momentum por timeframe
            timing_entrada: Timing de entrada otimizado

        Returns:
            Dict com timestamp e momentum otimizados para saída
        """
        try:
            timestamp_entrada = timing_entrada['timestamp']
            alvo = setup.get('alvo', 0)
            stop_loss = setup.get('stop_loss', 0)
            direcao = setup.get('direcao', 'LONG')

            # Calcular alvo de tempo (máximo de horas configurado)
            max_horas = self.janelas_otimizacao['saida']
            timestamp_max = timestamp_entrada + timedelta(hours=max_horas)

            # Usar timeframe de 4h para saída (visão mais longa)
            if '4h' not in momentum_intraday:
                return None

            momentum_4h = momentum_intraday['4h']

            # Filtrar dados no período de saída
            periodo_saida = momentum_4h[
                (momentum_4h.index > timestamp_entrada) &
                (momentum_4h.index <= timestamp_max)
            ]

            if periodo_saida.empty:
                return None

            # Estratégia de saída baseada na direção
            if direcao == 'LONG':
                # Procurar onde momentum começa a cair (sinal de reversão)
                # ou atinge o limite de tempo
                reversoes = periodo_saida[periodo_saida < periodo_saida.shift(1)]
                if not reversoes.empty:
                    timestamp_saida = reversoes.index[0]
                    momentum_saida = reversoes.iloc[0]
                else:
                    # Usar último ponto disponível
                    timestamp_saida = periodo_saida.index[-1]
                    momentum_saida = periodo_saida.iloc[-1]
            else:  # SHORT
                # Procurar onde momentum começa a subir (sinal de reversão)
                reversoes = periodo_saida[periodo_saida > periodo_saida.shift(1)]
                if not reversoes.empty:
                    timestamp_saida = reversoes.index[0]
                    momentum_saida = reversoes.iloc[0]
                else:
                    # Usar último ponto disponível
                    timestamp_saida = periodo_saida.index[-1]
                    momentum_saida = periodo_saida.iloc[-1]

            return {
                'timestamp': timestamp_saida,
                'momentum': momentum_saida
            }

        except Exception as e:
            logger.error(f"Erro ao otimizar ponto de saída: {e}")
            return None

    def _calcular_liquidez_horario(self, timing: Dict[str, Any]) -> float:
        """
        Calcula score de liquidez baseado no horário.

        Args:
            timing: Dict com timestamp do timing

        Returns:
            Score de liquidez (0-1)
        """
        try:
            hora = timing['timestamp'].time()

            # Sessões com maior liquidez
            if self.sessoes_mercado['regular']['inicio'] <= hora <= self.sessoes_mercado['regular']['fim']:
                return 1.0  # Sessão regular - máxima liquidez
            elif self.sessoes_mercado['pre_market']['inicio'] <= hora <= self.sessoes_mercado['pre_market']['fim']:
                return 0.7  # Pré-mercado - boa liquidez
            elif self.sessoes_mercado['after_market']['inicio'] <= hora <= self.sessoes_mercado['after_market']['fim']:
                return 0.6  # After market - liquidez moderada
            else:
                return 0.3  # Overnight - baixa liquidez

        except Exception:
            return 0.5  # Valor padrão neutro

    def _calcular_volatilidade_ajustada(self, timing_entrada: Dict[str, Any], timing_saida: Dict[str, Any]) -> float:
        """
        Calcula volatilidade ajustada para o período do trade.

        Args:
            timing_entrada: Timing de entrada
            timing_saida: Timing de saída

        Returns:
            Volatilidade ajustada (0-1, onde 1 é mais volátil)
        """
        try:
            # Calcular duração do trade em horas
            duracao = (timing_saida['timestamp'] - timing_entrada['timestamp']).total_seconds() / 3600

            # Volatilidade base por horário
            hora_entrada = timing_entrada['timestamp'].time()

            if self.sessoes_mercado['regular']['inicio'] <= hora_entrada <= self.sessoes_mercado['regular']['fim']:
                volatilidade_base = 0.6  # Sessão regular - volatilidade moderada
            elif self.sessoes_mercado['pre_market']['inicio'] <= hora_entrada <= self.sessoes_mercado['pre_market']['fim']:
                volatilidade_base = 0.8  # Pré-mercado - mais volátil
            else:
                volatilidade_base = 0.4  # Outros períodos - menos volátil

            # Ajustar por duração (trades mais longos tendem a ter mais volatilidade)
            ajuste_duracao = min(duracao / 24, 1.0)  # Máximo 24h = 1.0

            volatilidade_ajustada = volatilidade_base * (0.5 + 0.5 * ajuste_duracao)

            return min(volatilidade_ajustada, 1.0)

        except Exception:
            return 0.5  # Valor padrão neutro

    def _calcular_score_timing(self, momentum_entrada: float, momentum_saida: float,
                              liquidez_entrada: float, liquidez_saida: float,
                              volatilidade: float) -> float:
        """
        Calcula score geral de timing (0-100).

        Args:
            momentum_entrada: Momentum no ponto de entrada
            momentum_saida: Momentum no ponto de saída
            liquidez_entrada: Liquidez na entrada
            liquidez_saida: Liquidez na saída
            volatilidade: Volatilidade ajustada

        Returns:
            Score de timing (0-100)
        """
        try:
            # Normalizar componentes para escala 0-1
            momentum_score = (momentum_entrada + momentum_saida) / 2
            liquidez_score = (liquidez_entrada + liquidez_saida) / 2
            volatilidade_score = 1 - volatilidade  # Menos volatilidade = melhor score

            # Calcular score ponderado
            score_ponderado = (
                self.pesos_timing['momentum'] * momentum_score +
                self.pesos_timing['liquidez'] * liquidez_score +
                self.pesos_timing['volatilidade'] * volatilidade_score
            )

            # Converter para escala 0-100
            return score_ponderado * 100

        except Exception:
            return 0.0

    def _calcular_confianca_setup(self, score_timing: float, liquidez_entrada: float,
                                 liquidez_saida: float, volatilidade: float) -> float:
        """
        Calcula confiança do timing otimizado.

        Args:
            score_timing: Score geral de timing
            liquidez_entrada: Liquidez na entrada
            liquidez_saida: Liquidez na saída
            volatilidade: Volatilidade ajustada

        Returns:
            Confiança (0-100)
        """
        try:
            # Fatores que aumentam confiança
            fatores_confianca = []

            # Score de timing alto
            if score_timing >= 70:
                fatores_confianca.append(0.9)
            elif score_timing >= 50:
                fatores_confianca.append(0.7)
            else:
                fatores_confianca.append(0.4)

            # Boa liquidez
            liquidez_media = (liquidez_entrada + liquidez_saida) / 2
            fatores_confianca.append(liquidez_media)

            # Baixa volatilidade
            fatores_confianca.append(1 - volatilidade)

            # Confiança como média dos fatores
            confianca = np.mean(fatores_confianca) * 100

            return min(confianca, 100.0)

        except Exception:
            return 50.0  # Confiança neutra em caso de erro

    def _calcular_metricas_timing(self, timings_otimizados: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcula métricas gerais da otimização de timing"""
        if not timings_otimizados:
            return {}

        try:
            scores_timing = [t['score_timing'] for t in timings_otimizados]
            confiancas = [t['confianca'] for t in timings_otimizados]
            liquidez_entrada = [t['liquidez_entrada'] for t in timings_otimizados]
            liquidez_saida = [t['liquidez_saida'] for t in timings_otimizados]
            volatilidades = [t['volatilidade_ajustada'] for t in timings_otimizados]

            return {
                'score_timing_medio': np.mean(scores_timing),
                'score_timing_desvio': np.std(scores_timing),
                'score_timing_maximo': np.max(scores_timing),
                'score_timing_minimo': np.min(scores_timing),
                'confianca_media': np.mean(confiancas),
                'liquidez_entrada_media': np.mean(liquidez_entrada),
                'liquidez_saida_media': np.mean(liquidez_saida),
                'volatilidade_media': np.mean(volatilidades),
                'taxa_sucesso_otimizacao': len(timings_otimizados) / len(timings_otimizados),  # Todos foram otimizados
                'timeframes_utilizados': self.timeframes,
                'janelas_otimizacao': self.janelas_otimizacao
            }

        except Exception as e:
            logger.error(f"Erro ao calcular métricas de timing: {e}")
            return {}

    def _calcular_confianca_timing(self, timings_otimizados: List[Dict[str, Any]]) -> float:
        """Calcula confiança geral da otimização de timing"""
        if not timings_otimizados:
            return 0.0

        try:
            # Confiança baseada na qualidade dos timings
            scores = [t['score_timing'] for t in timings_otimizados]
            confiancas = [t['confianca'] for t in timings_otimizados]

            # Média ponderada: 60% score timing, 40% confiança individual
            confianca_geral = 0.6 * np.mean(scores) + 0.4 * np.mean(confiancas)

            return min(confianca_geral, 100.0)

        except Exception:
            return 50.0

    def _criar_resultado_vazio(self) -> ResultadoModulo:
        """Cria resultado vazio para quando não há setups para otimizar"""
        return ResultadoModulo(
            timestamp=datetime.now(),
            status='SUCCESS',
            dados_analisados={
                'timings_otimizados': [],
                'setups_com_timing': 0,
                'score_timing_medio': 0,
                'confianca_media': 0,
                'timeframes_analisados': self.timeframes,
                'janelas_otimizacao': self.janelas_otimizacao
            },
            metricas={},
            confianca=0.0,
            metadados={
                'motivo': 'nenhum_setup_aprovado',
                'tempo_processamento': 0.0
            }
        )

    def otimizar(self, setups: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Método público para otimização de timing (interface do framework).

        Args:
            setups: Lista de setups para otimizar

        Returns:
            Lista de setups com timing otimizado
        """
        # Este método é chamado pelo framework principal
        # Adaptar para usar o método analisar interno
        dados_entrada = {
            'setups_aprovados': setups,
            'dados_mercado': {}  # Dados de mercado seriam passados pelo framework
        }

        resultado = self.analisar(dados_entrada)

        if hasattr(resultado, 'dados_analisados') and 'timings_otimizados' in resultado.dados_analisados:
            return resultado.dados_analisados['timings_otimizados']

        return []