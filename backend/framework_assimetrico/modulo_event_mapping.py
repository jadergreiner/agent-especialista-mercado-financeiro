# Módulo Event Mapping - Framework Assimétrico
# Mapeia eventos econômicos e avalia seu impacto no mercado

"""
MÓDULO EVENT MAPPING

Este módulo implementa o mapeamento de eventos econômicos e avaliação
de seu impacto no mercado brasileiro. Identifica eventos de alto impacto
e calcula probabilidade de volatilidade baseada no calendário econômico.

Funcionalidades principais:
- Carregamento de calendário econômico (FOMC, PIB, inflação, etc.)
- Pontuação de risco por evento baseada em relevância histórica
- Análise de impacto histórico no mercado
- Previsão de volatilidade baseada em eventos próximos
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
import pandas as pd
import numpy as np

from .interfaces import (
    ModuloEventMappingInterface,
    ResultadoModulo
)

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class EventoEconomico:
    """Representa um evento econômico"""
    nome: str
    data: datetime
    pais: str
    importancia: str  # 'alta', 'media', 'baixa'
    valor_anterior: Optional[float]
    valor_previsto: Optional[float]
    valor_atual: Optional[float]
    unidade: str
    impacto_mercado: float  # 0-100


class ModuloEventMapping(ModuloEventMappingInterface):
    """
    Implementação do módulo de mapeamento de eventos.

    Analisa calendário econômico e avalia impacto de eventos
    no mercado brasileiro, especialmente Ibovespa e câmbio.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa módulo Event Mapping.

        Args:
            config: Configuração do módulo
        """
        super().__init__(config)
        self.eventos_carregados = {}
        self.impactos_historicos = {}
        self._carregar_base_conhecimento()

    def _validar_configuracao_especifica(self):
        """Validação específica do módulo Event Mapping"""
        required_keys = [
            'paises_foco',  # ['BR', 'US', 'EU', 'CN']
            'eventos_criticos',  # Lista de eventos críticos
            'janela_analise_dias'
        ]

        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Configuração obrigatória faltando: {key}")

        # Validar países suportados
        paises_suportados = ['BR', 'US', 'EU', 'CN', 'GB', 'JP']
        for pais in self.config['paises_foco']:
            if pais not in paises_suportados:
                raise ValueError(f"País não suportado: {pais}")

    def _carregar_base_conhecimento(self):
        """Carrega base de conhecimento de impactos históricos"""
        # Base de conhecimento simplificada - em produção viria de DB
        self.impactos_historicos = {
            'US': {
                'FOMC': {'impacto_medio': 85, 'volatilidade_esperada': 2.1},
                'NFP': {'impacto_medio': 78, 'volatilidade_esperada': 1.8},
                'GDP': {'impacto_medio': 65, 'volatilidade_esperada': 1.4},
                'CPI': {'impacto_medio': 72, 'volatilidade_esperada': 1.6},
                'PCE': {'impacto_medio': 68, 'volatilidade_esperada': 1.5}
            },
            'BR': {
                'IPCA': {'impacto_medio': 75, 'volatilidade_esperada': 1.7},
                'PIB': {'impacto_medio': 70, 'volatilidade_esperada': 1.5},
                'SELIC': {'impacto_medio': 80, 'volatilidade_esperada': 1.9},
                'CAGED': {'impacto_medio': 45, 'volatilidade_esperada': 0.9}
            },
            'EU': {
                'ECB': {'impacto_medio': 82, 'volatilidade_esperada': 2.0},
                'CPI_EU': {'impacto_medio': 68, 'volatilidade_esperada': 1.4}
            }
        }

    def analisar(self, dados: Any) -> ResultadoModulo:
        """
        Método principal de análise do módulo Event Mapping.

        Args:
            dados: Dados de entrada (pode incluir calendário ou período específico)

        Returns:
            ResultadoModulo com análise de eventos
        """
        try:
            logger.info("Iniciando análise de eventos econômicos")

            # Carregar calendário de eventos
            calendario = self.carregar_calendario_eventos()

            # Filtrar eventos próximos (próximos 7 dias)
            eventos_proximos = self._filtrar_eventos_proximos(calendario)

            # Analisar impacto de cada evento
            analises_eventos = []
            for _, evento in eventos_proximos.iterrows():
                analise = self._analisar_evento_individual(evento)
                analises_eventos.append(analise)

            # Calcular métricas agregadas
            metricas_agregadas = self._calcular_metricas_agregadas(analises_eventos)

            # Prever volatilidade baseada nos eventos
            volatilidade_prevista = self.prever_volatilidade(analises_eventos)

            # Calcular confiança da análise
            confianca = self._calcular_confianca_analise(analises_eventos)

            dados_analisados = {
                'eventos_proximos': len(eventos_proximos),
                'eventos_criticos': len([e for e in analises_eventos if e.get('risco', 0) > 70]),
                'volatilidade_prevista': volatilidade_prevista,
                'paises_afetados': list(set([e.get('pais', 'BR') for e in analises_eventos])),
                'analises_detalhadas': analises_eventos
            }

            metricas = {
                'eventos_analisados': len(analises_eventos),
                'risco_medio_eventos': np.mean([e.get('risco', 0) for e in analises_eventos]) if analises_eventos else 0,
                'volatilidade_maxima': max([e.get('volatilidade_esperada', 0) for e in analises_eventos]) if analises_eventos else 0,
                'impacto_total_mercado': metricas_agregadas.get('impacto_total', 0),
                **metricas_agregadas
            }

            return ResultadoModulo(
                timestamp=datetime.now(),
                status='SUCCESS',
                dados_analisados=dados_analisados,
                metricas=metricas,
                confianca=confianca,
                metadados={
                    'periodo_analisado': f"Próximos {self.config.get('janela_analise_dias', 7)} dias",
                    'fonte_dados': 'Calendário Econômico Simulado',
                    'ultima_atualizacao': datetime.now().isoformat()
                }
            )

        except Exception as e:
            logger.error(f"Erro na análise de eventos: {str(e)}")
            return ResultadoModulo(
                timestamp=datetime.now(),
                status='ERROR',
                dados_analisados={},
                metricas={'erro': str(e)},
                confianca=0.0,
                metadados={'erro': str(e)}
            )

    def carregar_calendario_eventos(self) -> pd.DataFrame:
        """
        Carrega calendário de eventos econômicos.

        Returns:
            DataFrame com eventos econômicos
        """
        logger.info("Carregando calendário de eventos econômicos")

        # Simulação de calendário econômico - em produção viria de API
        eventos = []

        # Eventos dos próximos 7 dias
        hoje = datetime.now()
        for i in range(7):
            data_evento = hoje + timedelta(days=i)

            # Adicionar eventos baseados no dia da semana e padrão histórico
            if data_evento.weekday() == 2:  # Quarta-feira - dia comum de dados econômicos
                eventos.extend(self._gerar_eventos_quarta(data_evento))
            elif data_evento.weekday() == 3:  # Quinta-feira
                eventos.extend(self._gerar_eventos_quinta(data_evento))
            elif data_evento.weekday() == 4:  # Sexta-feira
                eventos.extend(self._gerar_eventos_sexta(data_evento))

        # Criar DataFrame
        df_eventos = pd.DataFrame(eventos)

        # Adicionar coluna de data como datetime se não existir
        if 'data' in df_eventos.columns:
            df_eventos['data'] = pd.to_datetime(df_eventos['data'])

        logger.info(f"Carregados {len(df_eventos)} eventos econômicos")
        return df_eventos

    def _gerar_eventos_quarta(self, data: datetime) -> List[Dict[str, Any]]:
        """Gera eventos típicos de quarta-feira"""
        eventos = [
            {
                'nome': 'IPCA (Brasil)',
                'data': data.replace(hour=9, minute=0),
                'pais': 'BR',
                'importancia': 'alta',
                'categoria': 'inflacao',
                'unidade': '%',
                'valor_anterior': 0.42,
                'valor_previsto': 0.38,
                'valor_atual': None
            },
            {
                'nome': 'PCE (EUA)',
                'data': data.replace(hour=13, minute=30),
                'pais': 'US',
                'importancia': 'alta',
                'categoria': 'inflacao',
                'unidade': '%',
                'valor_anterior': 0.3,
                'valor_previsto': 0.3,
                'valor_atual': None
            }
        ]
        return eventos

    def _gerar_eventos_quinta(self, data: datetime) -> List[Dict[str, Any]]:
        """Gera eventos típicos de quinta-feira"""
        eventos = [
            {
                'nome': 'PIB Trimestral (Brasil)',
                'data': data.replace(hour=9, minute=0),
                'pais': 'BR',
                'importancia': 'alta',
                'categoria': 'crescimento',
                'unidade': '%',
                'valor_anterior': 0.5,
                'valor_previsto': 0.3,
                'valor_atual': None
            },
            {
                'nome': 'Reunião FOMC (EUA)',
                'data': data.replace(hour=21, minute=0),
                'pais': 'US',
                'importancia': 'alta',
                'categoria': 'juros',
                'unidade': 'bps',
                'valor_anterior': 25,
                'valor_previsto': 0,
                'valor_atual': None
            }
        ]
        return eventos

    def _gerar_eventos_sexta(self, data: datetime) -> List[Dict[str, Any]]:
        """Gera eventos típicos de sexta-feira"""
        eventos = [
            {
                'nome': 'CAGED (Brasil)',
                'data': data.replace(hour=8, minute=0),
                'pais': 'BR',
                'importancia': 'media',
                'categoria': 'emprego',
                'unidade': 'mil',
                'valor_anterior': 150.5,
                'valor_previsto': 140.0,
                'valor_atual': None
            }
        ]
        return eventos

    def pontuar_risco_evento(self, evento: Dict[str, Any]) -> float:
        """
        Atribui pontuação de risco a um evento (0-100).

        Args:
            evento: Dict com dados do evento

        Returns:
            float: Pontuação de risco (0-100)
        """
        try:
            # Fatores de pontuação
            importancia_base = {
                'alta': 80,
                'media': 50,
                'baixa': 20
            }

            # Base score pela importância
            score = importancia_base.get(evento.get('importancia', 'baixa'), 20)

            # Ajuste por país (impacto no Brasil)
            impacto_pais = {
                'BR': 1.0,   # Eventos brasileiros têm impacto direto
                'US': 0.9,   # EUA tem alto impacto
                'EU': 0.7,   # Europa médio impacto
                'CN': 0.8,   # China alto impacto via commodities
                'GB': 0.6,
                'JP': 0.5
            }

            multiplicador_pais = impacto_pais.get(evento.get('pais', 'BR'), 0.5)
            score *= multiplicador_pais

            # Ajuste por categoria de evento
            categoria_ajuste = {
                'juros': 1.2,      # Decisões de juros têm alto impacto
                'inflacao': 1.1,   # Inflação afeta expectativas
                'emprego': 1.0,    # Emprego importante mas menos volátil
                'crescimento': 1.1 # PIB afeta sentiment
            }

            multiplicador_categoria = categoria_ajuste.get(evento.get('categoria', 'outros'), 1.0)
            score *= multiplicador_categoria

            # Ajuste por surpresa esperada (diferença previsto vs anterior)
            if evento.get('valor_previsto') is not None and evento.get('valor_anterior') is not None:
                try:
                    diferenca = abs(evento['valor_previsto'] - evento['valor_anterior'])
                    if diferenca > 0:
                        # Eventos com maior diferença têm maior risco
                        score *= min(1.3, 1.0 + (diferenca / evento['valor_anterior']) * 0.5)
                except:
                    pass

            # Garantir limites 0-100
            return max(0, min(100, score))

        except Exception as e:
            logger.warning(f"Erro ao pontuar risco do evento {evento.get('nome', 'desconhecido')}: {str(e)}")
            return 25.0  # Score conservador em caso de erro

    def analisar_impacto_historico(self, evento: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analisa impacto histórico do evento no mercado.

        Args:
            evento: Dict com dados do evento

        Returns:
            Dict com análise histórica
        """
        try:
            nome_evento = evento.get('nome', '').split(' (')[0]  # Remove país do nome
            pais = evento.get('pais', 'BR')

            # Buscar na base de conhecimento
            if pais in self.impactos_historicos and nome_evento in self.impactos_historicos[pais]:
                dados_historicos = self.impactos_historicos[pais][nome_evento]

                return {
                    'impacto_medio': dados_historicos['impacto_medio'],
                    'volatilidade_esperada': dados_historicos['volatilidade_esperada'],
                    'eventos_analisados': 50,  # Simulação
                    'periodo_analise': '24 meses',
                    'tendencia_impacto': 'estavel',
                    'fonte': 'base_conhecimento_historico'
                }
            else:
                # Valores padrão para eventos não mapeados
                return {
                    'impacto_medio': 40,
                    'volatilidade_esperada': 1.0,
                    'eventos_analisados': 10,
                    'periodo_analise': '12 meses',
                    'tendencia_impacto': 'desconhecida',
                    'fonte': 'estimativa_padrao'
                }

        except Exception as e:
            logger.warning(f"Erro ao analisar impacto histórico: {str(e)}")
            return {
                'impacto_medio': 30,
                'volatilidade_esperada': 0.8,
                'erro': str(e)
            }

    def prever_volatilidade(self, eventos_proximos: List[Dict[str, Any]]) -> float:
        """
        Prevê volatilidade esperada baseada em eventos próximos.

        Args:
            eventos_proximos: Lista de eventos próximos

        Returns:
            float: Volatilidade prevista (%)
        """
        try:
            if not eventos_proximos:
                return 0.5  # Volatilidade mínima

            # Calcular volatilidade baseada nos eventos
            volatilidades = []
            pesos = []

            for evento in eventos_proximos:
                volatilidade_evento = evento.get('volatilidade_esperada', 1.0)
                risco_evento = evento.get('risco', 25)

                # Peso baseado no risco e proximidade temporal
                dias_para_evento = evento.get('dias_para_evento', 7)
                peso_temporal = max(0.1, 1.0 - (dias_para_evento / 7.0))  # Maior peso para eventos próximos

                peso_total = (risco_evento / 100.0) * peso_temporal

                volatilidades.append(volatilidade_evento)
                pesos.append(peso_total)

            if not pesos:
                return 0.8

            # Calcular média ponderada
            volatilidade_total = np.average(volatilidades, weights=pesos)

            # Ajustar por interações entre eventos
            num_eventos_criticos = sum(1 for e in eventos_proximos if e.get('risco', 0) > 70)
            if num_eventos_criticos > 1:
                # Eventos múltiplos aumentam volatilidade
                volatilidade_total *= (1 + (num_eventos_criticos - 1) * 0.2)

            return min(5.0, max(0.3, volatilidade_total))  # Limitar entre 0.3% e 5%

        except Exception as e:
            logger.warning(f"Erro ao prever volatilidade: {str(e)}")
            return 1.0  # Valor conservador

    def _filtrar_eventos_proximos(self, calendario: pd.DataFrame) -> pd.DataFrame:
        """Filtra eventos dos próximos dias"""
        hoje = datetime.now()
        dias_frente = self.config.get('janela_analise_dias', 7)
        data_limite = hoje + timedelta(days=dias_frente)

        # Filtrar por data e países de foco
        eventos_filtrados = calendario[
            (calendario['data'] >= hoje) &
            (calendario['data'] <= data_limite) &
            (calendario['pais'].isin(self.config.get('paises_foco', ['BR', 'US'])))
        ].copy()

        # Adicionar coluna de dias para o evento
        eventos_filtrados['dias_para_evento'] = (
            eventos_filtrados['data'] - hoje
        ).dt.days

        return eventos_filtrados

    def _analisar_evento_individual(self, evento: pd.Series) -> Dict[str, Any]:
        """Analisa um evento individual"""
        try:
            evento_dict = evento.to_dict()

            # Pontuar risco
            risco = self.pontuar_risco_evento(evento_dict)

            # Analisar impacto histórico
            impacto_historico = self.analisar_impacto_historico(evento_dict)

            # Combinar análises
            analise = {
                'nome': evento_dict.get('nome', 'Desconhecido'),
                'data': evento_dict.get('data'),
                'pais': evento_dict.get('pais', 'BR'),
                'importancia': evento_dict.get('importancia', 'baixa'),
                'categoria': evento_dict.get('categoria', 'outros'),
                'risco': risco,
                'dias_para_evento': evento_dict.get('dias_para_evento', 7),
                **impacto_historico
            }

            return analise

        except Exception as e:
            logger.warning(f"Erro ao analisar evento {evento.get('nome', 'desconhecido')}: {str(e)}")
            return {
                'nome': evento.get('nome', 'Erro'),
                'risco': 0,
                'erro': str(e)
            }

    def _calcular_metricas_agregadas(self, analises_eventos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcula métricas agregadas dos eventos"""
        try:
            if not analises_eventos:
                return {'impacto_total': 0, 'risco_medio': 0, 'volatilidade_agregada': 0}

            riscos = [e.get('risco', 0) for e in analises_eventos]
            impactos = [e.get('impacto_medio', 0) for e in analises_eventos]
            volatilidades = [e.get('volatilidade_esperada', 0) for e in analises_eventos]

            return {
                'impacto_total': np.mean(impactos) if impactos else 0,
                'risco_medio': np.mean(riscos) if riscos else 0,
                'volatilidade_agregada': np.mean(volatilidades) if volatilidades else 0,
                'evento_maior_risco': max(riscos) if riscos else 0,
                'num_eventos_criticos': sum(1 for r in riscos if r > 70)
            }

        except Exception as e:
            logger.warning(f"Erro ao calcular métricas agregadas: {str(e)}")
            return {'erro': str(e)}

    def _calcular_confianca_analise(self, analises_eventos: List[Dict[str, Any]]) -> float:
        """Calcula confiança da análise baseada na qualidade dos dados"""
        try:
            if not analises_eventos:
                return 30.0

            # Fatores de confiança
            confianca_base = 60.0

            # + baseado no número de eventos analisados
            bonus_volume = min(20, len(analises_eventos) * 2)

            # + baseado na qualidade dos dados históricos
            eventos_com_historico = sum(1 for e in analises_eventos
                                       if e.get('fonte') == 'base_conhecimento_historico')
            bonus_historico = (eventos_com_historico / len(analises_eventos)) * 15

            # - penalidade por eventos sem dados históricos
            eventos_sem_historico = len(analises_eventos) - eventos_com_historico
            penalidade = eventos_sem_historico * 5

            confianca_total = confianca_base + bonus_volume + bonus_historico - penalidade

            return max(20, min(95, confianca_total))

        except Exception as e:
            logger.warning(f"Erro ao calcular confiança: {str(e)}")
            return 40.0