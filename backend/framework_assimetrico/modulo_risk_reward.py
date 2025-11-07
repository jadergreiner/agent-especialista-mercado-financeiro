# Módulo Risk-Reward - Framework Assimétrico
# Cálculo de risco-recompensa e pontuação de assimetria

"""
MÓDULO RISK-REWARD

Este módulo implementa o cálculo de risco-recompensa e pontuação de assimetria
para setups identificados pelo framework. Avalia a atratividade de oportunidades
baseando-se em múltiplas dimensões de análise.

Funcionalidades principais:
- Cálculo de ratio risco-recompensa para setups
- Pontuação de assimetria baseada em confluência técnica/macro/correlação/eventos
- Validação histórica de probabilidade de sucesso
- Filtragem de setups por critérios de assimetria
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
import pandas as pd
import numpy as np

from .interfaces import (
    ModuloRiskRewardInterface,
    ResultadoModulo
)

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SetupAssimetrico:
    """Representa um setup assimétrico identificado"""
    id: str
    ativo: str
    direcao: str  # 'LONG', 'SHORT'
    preco_entrada: float
    stop_loss: float
    alvo: float
    risk_reward_ratio: float
    pontuacao_assimetria: float
    probabilidade_historica: float
    componentes_analise: Dict[str, Any]
    timestamp: datetime
    validade: datetime


class ModuloRiskReward(ModuloRiskRewardInterface):
    """
    Implementação do módulo de cálculo risco-recompensa.

    Avalia setups identificados pelos módulos anteriores e calcula
    métricas de risco-recompensa e assimetria para filtrar oportunidades.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa módulo Risk-Reward.

        Args:
            config: Configuração do módulo
        """
        super().__init__(config)
        self.setups_identificados = []
        self.base_historica = {}
        self._carregar_base_historica()

    def _validar_configuracao_especifica(self):
        """Validação específica do módulo Risk-Reward"""
        required_keys = [
            'min_risk_reward_ratio',  # Mínimo 1.5
            'min_pontuacao_assimetria',  # Mínimo para considerar setup
            'max_risco_por_operacao',  # Máximo 2% do capital
            'janela_historica_dias'  # Dias para análise histórica
        ]

        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Configuração obrigatória faltando: {key}")

        # Validar valores mínimos
        if self.config['min_risk_reward_ratio'] < 1.0:
            raise ValueError("min_risk_reward_ratio deve ser >= 1.0")

        if self.config['min_pontuacao_assimetria'] < 0 or self.config['min_pontuacao_assimetria'] > 100:
            raise ValueError("min_pontuacao_assimetria deve estar entre 0-100")

    def _carregar_base_historica(self):
        """Carrega base histórica de performance de setups"""
        # Base de conhecimento simplificada - em produção viria de DB
        self.base_historica = {
            'WIN': {
                'LONG': {
                    'confluencia_alta': {'win_rate': 0.68, 'avg_rr': 2.1, 'total_trades': 150},
                    'confluencia_media': {'win_rate': 0.55, 'avg_rr': 1.8, 'total_trades': 200},
                    'confluencia_baixa': {'win_rate': 0.42, 'avg_rr': 1.4, 'total_trades': 300}
                },
                'SHORT': {
                    'confluencia_alta': {'win_rate': 0.65, 'avg_rr': 2.0, 'total_trades': 120},
                    'confluencia_media': {'win_rate': 0.52, 'avg_rr': 1.7, 'total_trades': 180},
                    'confluencia_baixa': {'win_rate': 0.38, 'avg_rr': 1.3, 'total_trades': 250}
                }
            },
            'IBOVESPA': {
                'LONG': {
                    'confluencia_alta': {'win_rate': 0.62, 'avg_rr': 1.9, 'total_trades': 100},
                    'confluencia_media': {'win_rate': 0.48, 'avg_rr': 1.6, 'total_trades': 150},
                    'confluencia_baixa': {'win_rate': 0.35, 'avg_rr': 1.2, 'total_trades': 200}
                },
                'SHORT': {
                    'confluencia_alta': {'win_rate': 0.58, 'avg_rr': 1.8, 'total_trades': 80},
                    'confluencia_media': {'win_rate': 0.45, 'avg_rr': 1.5, 'total_trades': 120},
                    'confluencia_baixa': {'win_rate': 0.32, 'avg_rr': 1.1, 'total_trades': 180}
                }
            }
        }

    def analisar(self, dados: Any) -> ResultadoModulo:
        """
        Método principal de análise do módulo Risk-Reward.

        Args:
            dados: Dados de entrada contendo setups dos módulos anteriores

        Returns:
            ResultadoModulo com análise risco-recompensa
        """
        try:
            logger.info("Iniciando análise de risco-recompensa")

            # Verificar se dados contém informações dos módulos anteriores
            if not isinstance(dados, dict) or 'componentes_analise' not in dados:
                logger.warning("Dados insuficientes para análise risco-recompensa")
                return self._resultado_vazio("Dados insuficientes")

            componentes = dados['componentes_analise']

            # Verificar se temos setups para analisar
            setups_entrada = componentes.get('setups_tecnicos', [])
            if not setups_entrada:
                logger.info("Nenhum setup identificado pelos módulos anteriores")
                return self._resultado_vazio("Sem setups para análise")

            # Processar cada setup
            setups_avaliados = []
            for setup in setups_entrada:
                setup_avaliado = self._avaliar_setup_completo(setup, componentes)
                if setup_avaliado:
                    setups_avaliados.append(setup_avaliado)

            # Filtrar setups por critérios mínimos
            setups_filtrados = self._filtrar_setups_por_criterios(setups_avaliados)

            # Calcular métricas agregadas
            metricas_agregadas = self._calcular_metricas_agregadas(setups_avaliados, setups_filtrados)

            # Calcular confiança da análise
            confianca = self._calcular_confianca_analise(setups_avaliados)

            dados_analisados = {
                'setups_analisados': len(setups_avaliados),
                'setups_aprovados': len(setups_filtrados),
                'taxa_aprovacao': len(setups_filtrados) / len(setups_avaliados) if setups_avaliados else 0,
                'melhor_setup': self._identificar_melhor_setup(setups_filtrados),
                'distribuicao_assimetria': self._calcular_distribuicao_assimetria(setups_avaliados)
            }

            metricas = {
                'total_setups_analisados': len(setups_avaliados),
                'setups_com_bom_rr': sum(1 for s in setups_avaliados if s.risk_reward_ratio >= self.config['min_risk_reward_ratio']),
                'setups_alta_assimetria': sum(1 for s in setups_avaliados if s.pontuacao_assimetria >= 70),
                'media_risk_reward': np.mean([s.risk_reward_ratio for s in setups_avaliados]) if setups_avaliados else 0,
                'media_assimetria': np.mean([s.pontuacao_assimetria for s in setups_avaliados]) if setups_avaliados else 0,
                'media_probabilidade': np.mean([s.probabilidade_historica for s in setups_avaliados]) if setups_avaliados else 0,
                **metricas_agregadas
            }

            # Preparar setups para retorno (converter para dict)
            setups_dict = [self._setup_para_dict(setup) for setup in setups_filtrados]

            return ResultadoModulo(
                timestamp=datetime.now(),
                status='SUCCESS' if setups_filtrados else 'PARTIAL',
                dados_analisados={**dados_analisados, 'setups_aprovados': setups_dict},
                metricas=metricas,
                confianca=confianca,
                metadados={
                    'criterios_filtragem': {
                        'min_rr': self.config['min_risk_reward_ratio'],
                        'min_assimetria': self.config['min_pontuacao_assimetria'],
                        'max_risco': self.config['max_risco_por_operacao']
                    },
                    'base_historica_utilizada': len(self.base_historica),
                    'algoritmo_version': '1.0',
                    'ultima_atualizacao': datetime.now().isoformat()
                }
            )

        except Exception as e:
            logger.error(f"Erro na análise risco-recompensa: {str(e)}")
            return ResultadoModulo(
                timestamp=datetime.now(),
                status='ERROR',
                dados_analisados={},
                metricas={'erro': str(e)},
                confianca=0.0,
                metadados={'erro': str(e)}
            )

    def calcular_risk_reward_ratio(self, setup: Dict[str, Any]) -> float:
        """
        Calcula ratio risco-recompensa para um setup.

        Args:
            setup: Dict com dados do setup (preço entrada, stop, alvo)

        Returns:
            float: Ratio risco-recompensa
        """
        try:
            preco_entrada = setup.get('preco_entrada', 0)
            stop_loss = setup.get('stop_loss', 0)
            alvo = setup.get('alvo', 0)

            if preco_entrada <= 0 or stop_loss <= 0 or alvo <= 0:
                return 0.0

            # Calcular risco e recompensa
            if setup.get('direcao') == 'LONG':
                risco = abs(preco_entrada - stop_loss)
                recompensa = abs(alvo - preco_entrada)
            else:  # SHORT
                risco = abs(stop_loss - preco_entrada)
                recompensa = abs(preco_entrada - alvo)

            if risco == 0:
                return 0.0

            ratio = recompensa / risco

            # Limitar ratio máximo (evitar setups irreais)
            return min(ratio, 10.0)

        except Exception as e:
            logger.warning(f"Erro ao calcular risk-reward ratio: {str(e)}")
            return 1.0  # Ratio neutro em caso de erro

    def pontuar_assimetria(self, componentes: Dict[str, Any]) -> float:
        """
        Calcula pontuação de assimetria (0-100) baseada em todos os componentes.

        Args:
            componentes: Dict com resultados de todos os módulos

        Returns:
            float: Pontuação de assimetria (0-100)
        """
        try:
            # Pesos para cada componente (total = 1.0)
            pesos = {
                'confluencia_tecnica': 0.25,
                'confluencia_macro': 0.20,
                'confluencia_correlacao': 0.20,
                'impacto_eventos': 0.15,
                'momentum_geral': 0.10,
                'qualidade_setup': 0.10
            }

            # Extrair confluências (com valores padrão se não disponíveis)
            confluencia_tecnica = componentes.get('confluencia_tecnica', 50)
            confluencia_macro = componentes.get('confluencia_macro', 50)
            confluencia_correlacao = componentes.get('confluencia_correlacao', 50)
            impacto_eventos = componentes.get('impacto_eventos', 50)

            # Calcular momentum geral (baseado em tendência de preços)
            momentum_geral = self._calcular_momentum_geral(componentes)

            # Avaliar qualidade do setup técnico
            qualidade_setup = self._avaliar_qualidade_setup(componentes)

            # Calcular pontuação ponderada
            pontuacao = (
                confluencia_tecnica * pesos['confluencia_tecnica'] +
                confluencia_macro * pesos['confluencia_macro'] +
                confluencia_correlacao * pesos['confluencia_correlacao'] +
                impacto_eventos * pesos['impacto_eventos'] +
                momentum_geral * pesos['momentum_geral'] +
                qualidade_setup * pesos['qualidade_setup']
            )

            # Garantir limites 0-100
            return max(0, min(100, pontuacao))

        except Exception as e:
            logger.warning(f"Erro ao pontuar assimetria: {str(e)}")
            return 50.0  # Pontuação neutra em caso de erro

    def validar_probabilidade_historica(self, setup: Dict[str, Any]) -> float:
        """
        Valida probabilidade histórica de sucesso do setup.

        Args:
            setup: Dict com dados do setup

        Returns:
            float: Probabilidade histórica de sucesso (0-100)
        """
        try:
            ativo = setup.get('ativo', 'WIN')
            direcao = setup.get('direcao', 'LONG')
            pontuacao_assimetria = setup.get('pontuacao_assimetria', 50)

            # Classificar nível de confluência
            if pontuacao_assimetria >= 75:
                nivel_confluencia = 'confluencia_alta'
            elif pontuacao_assimetria >= 60:
                nivel_confluencia = 'confluencia_media'
            else:
                nivel_confluencia = 'confluencia_baixa'

            # Buscar na base histórica
            if (ativo in self.base_historica and
                direcao in self.base_historica[ativo] and
                nivel_confluencia in self.base_historica[ativo][direcao]):

                dados_historicos = self.base_historica[ativo][direcao][nivel_confluencia]
                win_rate = dados_historicos['win_rate']
                total_trades = dados_historicos['total_trades']

                # Ajustar por tamanho da amostra (mais trades = mais confiança)
                ajuste_amostra = min(1.0, total_trades / 100.0)

                return (win_rate * 100) * ajuste_amostra
            else:
                # Valores padrão para setups não mapeados
                return 45.0  # Probabilidade neutra

        except Exception as e:
            logger.warning(f"Erro ao validar probabilidade histórica: {str(e)}")
            return 40.0  # Probabilidade conservadora

    def _avaliar_setup_completo(self, setup: Dict[str, Any], componentes: Dict[str, Any]) -> Optional[SetupAssimetrico]:
        """Avalia um setup completo com todas as métricas"""
        try:
            # Calcular risk-reward ratio
            rr_ratio = self.calcular_risk_reward_ratio(setup)

            # Calcular pontuação de assimetria
            pontuacao_assimetria = self.pontuar_assimetria(componentes)

            # Validar probabilidade histórica
            probabilidade_historica = self.validar_probabilidade_historica({
                **setup,
                'pontuacao_assimetria': pontuacao_assimetria
            })

            # Criar objeto SetupAssimetrico
            setup_completo = SetupAssimetrico(
                id=f"{setup.get('ativo', 'UNKNOWN')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                ativo=setup.get('ativo', 'UNKNOWN'),
                direcao=setup.get('direcao', 'LONG'),
                preco_entrada=setup.get('preco_entrada', 0),
                stop_loss=setup.get('stop_loss', 0),
                alvo=setup.get('alvo', 0),
                risk_reward_ratio=rr_ratio,
                pontuacao_assimetria=pontuacao_assimetria,
                probabilidade_historica=probabilidade_historica,
                componentes_analise=componentes,
                timestamp=datetime.now(),
                validade=datetime.now() + timedelta(hours=24)  # Válido por 24h
            )

            return setup_completo

        except Exception as e:
            logger.warning(f"Erro ao avaliar setup completo: {str(e)}")
            return None

    def _filtrar_setups_por_criterios(self, setups: List[SetupAssimetrico]) -> List[SetupAssimetrico]:
        """Filtra setups por critérios mínimos de qualidade"""
        min_rr = self.config.get('min_risk_reward_ratio', 1.5)
        min_assimetria = self.config.get('min_pontuacao_assimetria', 60)

        setups_filtrados = []
        for setup in setups:
            if (setup.risk_reward_ratio >= min_rr and
                setup.pontuacao_assimetria >= min_assimetria):
                setups_filtrados.append(setup)

        return setups_filtrados

    def _calcular_momentum_geral(self, componentes: Dict[str, Any]) -> float:
        """Calcula momentum geral baseado nos componentes"""
        try:
            # Momentum baseado em indicadores técnicos
            momentum_tecnico = componentes.get('momentum_tecnico', 50)

            # Momentum macro (taxas, câmbio)
            momentum_macro = componentes.get('momentum_macro', 50)

            # Momentum de correlação
            momentum_correlacao = componentes.get('momentum_correlacao', 50)

            # Média ponderada
            momentum_geral = (
                momentum_tecnico * 0.4 +
                momentum_macro * 0.3 +
                momentum_correlacao * 0.3
            )

            return momentum_geral

        except Exception:
            return 50.0

    def _avaliar_qualidade_setup(self, componentes: Dict[str, Any]) -> float:
        """Avalia qualidade técnica do setup"""
        try:
            qualidade = 50.0  # Base neutra

            # Bônus por confluência de indicadores
            if componentes.get('rsi_alinhado', False):
                qualidade += 10
            if componentes.get('sma_alinhada', False):
                qualidade += 10
            if componentes.get('momentum_positivo', False):
                qualidade += 10

            # Penalização por condições adversas
            if componentes.get('volatilidade_alta', False):
                qualidade -= 15
            if componentes.get('evento_proximo', False):
                qualidade -= 10

            return max(0, min(100, qualidade))

        except Exception:
            return 50.0

    def _calcular_metricas_agregadas(self, setups_avaliados: List[SetupAssimetrico],
                                    setups_filtrados: List[SetupAssimetrico]) -> Dict[str, Any]:
        """Calcula métricas agregadas dos setups"""
        try:
            if not setups_avaliados:
                return {'expectativa_matematica': 0, 'melhor_oportunidade': None}

            # Expectativa matemática média
            expectativa_total = 0
            for setup in setups_avaliados:
                win_rate = setup.probabilidade_historica / 100
                loss_rate = 1 - win_rate
                rr = setup.risk_reward_ratio
                expectativa = (win_rate * rr) - (loss_rate * 1)  # Perde 1x no loss
                expectativa_total += expectativa

            expectativa_media = expectativa_total / len(setups_avaliados)

            # Melhor oportunidade
            melhor_setup = max(setups_filtrados, key=lambda x: x.pontuacao_assimetria) if setups_filtrados else None

            return {
                'expectativa_matematica': round(expectativa_media, 2),
                'melhor_oportunidade': melhor_setup.ativo if melhor_setup else None,
                'range_assimetria': f"{min(s.pontuacao_assimetria for s in setups_avaliados):.1f}-{max(s.pontuacao_assimetria for s in setups_avaliados):.1f}",
                'range_rr': f"{min(s.risk_reward_ratio for s in setups_avaliados):.1f}-{max(s.risk_reward_ratio for s in setups_avaliados):.1f}"
            }

        except Exception as e:
            logger.warning(f"Erro ao calcular métricas agregadas: {str(e)}")
            return {'erro_metricas': str(e)}

    def _identificar_melhor_setup(self, setups: List[SetupAssimetrico]) -> Optional[Dict[str, Any]]:
        """Identifica o melhor setup baseado em pontuação composta"""
        try:
            if not setups:
                return None

            # Pontuação composta: 40% assimetria + 30% RR + 30% probabilidade
            melhor_setup = max(setups, key=lambda x:
                x.pontuacao_assimetria * 0.4 +
                min(x.risk_reward_ratio, 5) * 0.3 +  # Limitar RR para evitar bias
                x.probabilidade_historica * 0.3
            )

            return {
                'ativo': melhor_setup.ativo,
                'direcao': melhor_setup.direcao,
                'pontuacao_total': melhor_setup.pontuacao_assimetria,
                'rr_ratio': melhor_setup.risk_reward_ratio,
                'probabilidade': melhor_setup.probabilidade_historica
            }

        except Exception as e:
            return None

    def _calcular_distribuicao_assimetria(self, setups: List[SetupAssimetrico]) -> Dict[str, int]:
        """Calcula distribuição de setups por faixa de assimetria"""
        distribuicao = {'alta': 0, 'media': 0, 'baixa': 0}

        for setup in setups:
            if setup.pontuacao_assimetria >= 75:
                distribuicao['alta'] += 1
            elif setup.pontuacao_assimetria >= 60:
                distribuicao['media'] += 1
            else:
                distribuicao['baixa'] += 1

        return distribuicao

    def _calcular_confianca_analise(self, setups: List[SetupAssimetrico]) -> float:
        """Calcula confiança da análise baseada na qualidade dos dados"""
        try:
            if not setups:
                return 30.0

            confianca_base = 60.0

            # Bônus por volume de setups analisados
            bonus_volume = min(15, len(setups) * 1.5)

            # Bônus por qualidade dos setups (alta assimetria)
            setups_alta_qualidade = sum(1 for s in setups if s.pontuacao_assimetria >= 75)
            bonus_qualidade = (setups_alta_qualidade / len(setups)) * 20

            # Bônus por diversidade de ativos
            ativos_unicos = len(set(setups))
            bonus_diversidade = min(10, ativos_unicos * 2)

            confianca_total = confianca_base + bonus_volume + bonus_qualidade + bonus_diversidade

            return max(25, min(95, confianca_total))

        except Exception as e:
            logger.warning(f"Erro ao calcular confiança: {str(e)}")
            return 45.0

    def _setup_para_dict(self, setup: SetupAssimetrico) -> Dict[str, Any]:
        """Converte SetupAssimetrico para dicionário"""
        return {
            'id': setup.id,
            'ativo': setup.ativo,
            'direcao': setup.direcao,
            'preco_entrada': setup.preco_entrada,
            'stop_loss': setup.stop_loss,
            'alvo': setup.alvo,
            'risk_reward_ratio': setup.risk_reward_ratio,
            'pontuacao_assimetria': setup.pontuacao_assimetria,
            'probabilidade_historica': setup.probabilidade_historica,
            'timestamp': setup.timestamp.isoformat(),
            'validade': setup.validade.isoformat()
        }

    def _resultado_vazio(self, motivo: str) -> ResultadoModulo:
        """Retorna resultado vazio com motivo"""
        return ResultadoModulo(
            timestamp=datetime.now(),
            status='PARTIAL',
            dados_analisados={'motivo': motivo},
            metricas={'setups_analisados': 0, 'setups_aprovados': 0},
            confianca=30.0,
            metadados={'status': 'sem_setups', 'motivo': motivo}
        )