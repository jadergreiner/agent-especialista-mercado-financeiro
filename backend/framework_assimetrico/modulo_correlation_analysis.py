# Módulo Correlation Analysis
# Etapa 3 do Framework Assimétrico
# Responsável por análise de correlação multi-ativo

"""
MÓDULO CORRELATION ANALYSIS

Este módulo implementa a terceira etapa do framework de detecção assimétrica:
análise de correlação entre múltiplos ativos para identificação de regimes
de mercado e oportunidades de diversificação.

Correlações Analisadas:
- Ibovespa vs Dólar (USD/BRL)
- WIN vs Commodities (PETR4, VALE3, SOJA, MINERIO)
- Detecção de regimes de correlação (alta, baixa, neutra)
- Janelas de correlação rolling (30d, 90d, 1y)

Objetivos:
- Identificar regimes de correlação entre ativos
- Detectar oportunidades de arbitragem entre mercados
- Avaliar impacto de commodities no mercado brasileiro
- Calcular pontuação de correlação para confluência
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Imports para execução direta (quando não usado como módulo)
try:
    from .interfaces import (
        ModuloCorrelationAnalysisInterface,
        ResultadoModulo,
        CONFIG_PADRAO_CORRELATION_ANALYSIS
    )
except ImportError:
    # Para execução direta do arquivo
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

    from interfaces import (
        ModuloCorrelationAnalysisInterface,
        ResultadoModulo,
        CONFIG_PADRAO_CORRELATION_ANALYSIS
    )

logger = logging.getLogger(__name__)


class ModuloCorrelationAnalysis(ModuloCorrelationAnalysisInterface):
    """
    Módulo responsável por análise de correlação multi-ativo.
    Avalia relacionamentos entre Ibovespa, dólar e commodities.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Inicializa o módulo Correlation Analysis.

        Args:
            config: Configuração específica do módulo
        """
        config_completo = {**CONFIG_PADRAO_CORRELATION_ANALYSIS, **(config or {})}
        super().__init__(config_completo)

        logger.info("Módulo Correlation Analysis inicializado")
        logger.info(f"Janela correlação: {self.config['janela_correlacao_dias']} dias")
        logger.info(f"Commodities analisadas: {self.config['commodities_analisadas']}")

    def _validar_configuracao_especifica(self):
        """Validação específica do módulo Correlation Analysis"""
        required_keys = ['janela_correlacao_dias', 'commodities_analisadas', 'threshold_correlacao_alta']

        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Configuração obrigatória não encontrada: {key}")

        # Validar janela de correlação
        if not (7 <= self.config.get('janela_correlacao_dias', 30) <= 365):
            raise ValueError("Janela de correlação deve estar entre 7 e 365 dias")

        # Validar threshold de correlação
        if not (0.3 <= self.config.get('threshold_correlacao_alta', 0.7) <= 1.0):
            raise ValueError("Threshold de correlação deve estar entre 0.3 e 1.0")

    def analisar(self, dados_multi_ativo: Dict[str, pd.DataFrame]) -> ResultadoModulo:
        """
        Executa análise completa de correlação multi-ativo.

        Args:
            dados_multi_ativo: Dict com dados de múltiplos ativos
                              (IBOV, DOL, PETR4, VALE3, etc.)

        Returns:
            ResultadoModulo: Resultado da análise de correlação
        """
        try:
            logger.info("Iniciando análise de correlação multi-ativo")

            # Validar dados de entrada
            if not self._validar_dados_entrada(dados_multi_ativo):
                return self._criar_resultado_erro("Dados de entrada insuficientes ou inválidos")

            # Calcular correlações principais
            correlacao_ibov_dolar = self.calcular_correlacao_ibov_dolar(
                dados_multi_ativo.get('IBOV', pd.DataFrame()),
                dados_multi_ativo.get('DOL', pd.DataFrame())
            )

            # Analisar impacto de commodities
            analise_commodities = self.analisar_commodities({
                commodity: dados_multi_ativo.get(commodity, pd.DataFrame())
                for commodity in self.config['commodities_analisadas']
            })

            # Detectar regime de correlação
            regime_atual = self.detectar_regime_correlacao(
                pd.DataFrame({'ibov_dolar': correlacao_ibov_dolar})
            )

            # Calcular pontuação de correlação
            pontuacao_correlacao = self._calcular_pontuacao_correlacao(
                correlacao_ibov_dolar, analise_commodities, regime_atual
            )

            # Preparar resultado
            resultado = {
                'correlacao_ibov_dolar': correlacao_ibov_dolar,
                'analise_commodities': analise_commodities,
                'regime_correlacao': regime_atual,
                'pontuacao_correlacao': pontuacao_correlacao,
                'timestamp_analise': datetime.now(),
                'janela_analisada': self.config['janela_correlacao_dias']
            }

            logger.info(f"Análise Correlation concluída: Regime {regime_atual}, Pontuação {pontuacao_correlacao:.1f}%")

            return ResultadoModulo(
                timestamp=datetime.now(),
                status='SUCCESS',
                dados_analisados=resultado,
                metricas={
                    'correlacao_ibov_dolar_media': correlacao_ibov_dolar.mean() if not correlacao_ibov_dolar.empty else 0,
                    'commodities_analisadas': len(analise_commodities.get('commodities_analisadas', [])),
                    'regime_detectado': regime_atual
                },
                confianca=pontuacao_correlacao,
                metadados={
                    'modulo': 'correlation_analysis',
                    'ativos_analisados': list(dados_multi_ativo.keys()),
                    'regime_correlacao': regime_atual,
                    'confluencia_geral': pontuacao_correlacao
                }
            )

        except Exception as e:
            logger.error(f"Erro na análise Correlation: {e}")
            return self._criar_resultado_erro(str(e))

    def calcular_correlacao_ibov_dolar(self, dados_ibov: pd.DataFrame,
                                     dados_dolar: pd.DataFrame) -> pd.Series:
        """
        Calcula correlação rolling Ibovespa vs Dólar.

        Args:
            dados_ibov: DataFrame com dados do Ibovespa
            dados_dolar: DataFrame com dados do dólar

        Returns:
            pd.Series: Correlação rolling
        """
        try:
            if dados_ibov.empty or dados_dolar.empty:
                logger.warning("Dados insuficientes para correlação Ibov-Dólar")
                return pd.Series(dtype=float)

            # Usar retornos para correlação (mais estável que preços)
            retornos_ibov = dados_ibov['Close'].pct_change().dropna()
            retornos_dolar = dados_dolar['Close'].pct_change().dropna()

            # Alinhar datas
            dados_alinhados = pd.concat([retornos_ibov, retornos_dolar], axis=1, keys=['IBOV', 'DOL']).dropna()

            if len(dados_alinhados) < self.config['janela_correlacao_dias']:
                logger.warning("Dados insuficientes para janela de correlação")
                return pd.Series(dtype=float)

            # Calcular correlação rolling
            janela = self.config['janela_correlacao_dias']
            correlacao = dados_alinhados['IBOV'].rolling(window=janela).corr(dados_alinhados['DOL'])

            logger.info(f"Correlação Ibov-Dólar calculada: média {correlacao.mean():.3f}")

            return correlacao.dropna()

        except Exception as e:
            logger.error(f"Erro no cálculo de correlação Ibov-Dólar: {e}")
            return pd.Series(dtype=float)

    def analisar_commodities(self, dados_commodities: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """
        Analisa impacto de commodities no mercado.

        Args:
            dados_commodities: Dict com dados das commodities

        Returns:
            Dict com análise de impacto das commodities
        """
        try:
            analise_resultado = {
                'commodities_analisadas': list(dados_commodities.keys()),
                'impacto_individual': {},
                'correlacao_media': {},
                'regime_mercado': 'NEUTRO'
            }

            # Analisar cada commodity
            for nome_commodity, dados in dados_commodities.items():
                if dados.empty:
                    analise_resultado['impacto_individual'][nome_commodity] = {
                        'disponivel': False,
                        'correlacao_ibov': 0,
                        'volatilidade': 0,
                        'tendencia': 'N/A'
                    }
                    continue

                # Calcular métricas da commodity
                retornos = dados['Close'].pct_change().dropna()
                volatilidade = retornos.std() * np.sqrt(252)  # Anualizada

                # Tendência (usando média móvel)
                if len(dados) >= 20:
                    sma_20 = dados['Close'].rolling(20).mean()
                    tendencia = 'ALTA' if dados['Close'].iloc[-1] > sma_20.iloc[-1] else 'BAIXA'
                else:
                    tendencia = 'INSUFICIENTE'

                analise_resultado['impacto_individual'][nome_commodity] = {
                    'disponivel': True,
                    'volatilidade': volatilidade,
                    'tendencia': tendencia,
                    'preco_atual': dados['Close'].iloc[-1] if not dados.empty else 0,
                    'periodos_analisados': len(dados)
                }

            # Determinar regime de mercado baseado em commodities
            tendencias_altas = sum(1 for info in analise_resultado['impacto_individual'].values()
                                 if info.get('tendencia') == 'ALTA')

            if tendencias_altas >= len(analise_resultado['commodities_analisadas']) * 0.7:
                analise_resultado['regime_mercado'] = 'BULL_COMMODITIES'
            elif tendencias_altas <= len(analise_resultado['commodities_analisadas']) * 0.3:
                analise_resultado['regime_mercado'] = 'BEAR_COMMODITIES'

            logger.info(f"Análise de commodities concluída: {analise_resultado['regime_mercado']}")

            return analise_resultado

        except Exception as e:
            logger.error(f"Erro na análise de commodities: {e}")
            return {
                'commodities_analisadas': list(dados_commodities.keys()),
                'erro': str(e),
                'regime_mercado': 'ERRO'
            }

    def detectar_regime_correlacao(self, correlacoes: pd.DataFrame) -> str:
        """
        Detecta regime atual de correlação.

        Args:
            correlacoes: DataFrame com séries de correlação

        Returns:
            str: Regime detectado ('ALTA', 'BAIXA', 'NEUTRA')
        """
        try:
            if correlacoes.empty:
                return 'INSUFICIENTE'

            # Usar correlação Ibov-Dólar como principal indicador
            if 'ibov_dolar' in correlacoes.columns:
                correlacao_atual = correlacoes['ibov_dolar'].iloc[-1] if not correlacoes['ibov_dolar'].empty else 0
                correlacao_media = correlacoes['ibov_dolar'].mean()

                threshold_alta = self.config['threshold_correlacao_alta']

                if correlacao_atual > threshold_alta and correlacao_media > threshold_alta * 0.8:
                    return 'ALTA_CORRELACAO'
                elif correlacao_atual < -threshold_alta * 0.5 and correlacao_media < -threshold_alta * 0.3:
                    return 'BAIXA_CORRELACAO'
                else:
                    return 'CORRELACAO_NEUTRA'
            else:
                return 'DADOS_INSUFICIENTES'

        except Exception as e:
            logger.error(f"Erro na detecção de regime: {e}")
            return 'ERRO'

    def _calcular_pontuacao_correlacao(self, correlacao_ibov_dolar: pd.Series,
                                     analise_commodities: Dict[str, Any],
                                     regime: str) -> float:
        """
        Calcula pontuação de correlação para o framework.

        Args:
            correlacao_ibov_dolar: Série de correlação Ibov-Dólar
            analise_commodities: Análise de commodities
            regime: Regime de correlação detectado

        Returns:
            float: Pontuação de 0-100
        """
        try:
            pontuacao = 50.0  # Pontuação base neutra

            # Ajuste baseado na correlação Ibov-Dólar
            if not correlacao_ibov_dolar.empty:
                correlacao_media = abs(correlacao_ibov_dolar.mean())

                if correlacao_media > self.config['threshold_correlacao_alta']:
                    pontuacao += 20  # Correlação alta aumenta pontuação
                elif correlacao_media < 0.3:
                    pontuacao -= 15  # Correlação baixa diminui pontuação

            # Ajuste baseado no regime de commodities
            regime_commodities = analise_commodities.get('regime_mercado', 'NEUTRO')

            if regime_commodities == 'BULL_COMMODITIES':
                pontuacao += 15  # Mercado de commodities em alta é positivo
            elif regime_commodities == 'BEAR_COMMODITIES':
                pontuacao -= 10  # Mercado de commodities em baixa é negativo

            # Ajuste baseado no regime de correlação
            if regime == 'ALTA_CORRELACAO':
                pontuacao += 10  # Alta correlação aumenta previsibilidade
            elif regime == 'BAIXA_CORRELACAO':
                pontuacao -= 5   # Baixa correlação diminui previsibilidade

            # Garantir limites
            pontuacao = max(0, min(100, pontuacao))

            return pontuacao

        except Exception as e:
            logger.error(f"Erro no cálculo de pontuação: {e}")
            return 50.0  # Retornar pontuação neutra em caso de erro

    def _validar_dados_entrada(self, dados_multi_ativo: Dict[str, pd.DataFrame]) -> bool:
        """
        Valida se os dados de entrada são suficientes.

        Args:
            dados_multi_ativo: Dados dos ativos

        Returns:
            bool: True se dados válidos
        """
        if not dados_multi_ativo:
            return False

        # Verificar se pelo menos IBOV ou WIN estão presentes
        ativos_principais = ['IBOV', 'WIN']
        tem_principal = any(ativo in dados_multi_ativo for ativo in ativos_principais)

        if not tem_principal:
            logger.warning("Nenhum ativo principal (IBOV/WIN) encontrado nos dados")
            return False

        # Verificar se há dados suficientes
        for nome_ativo, dados in dados_multi_ativo.items():
            if not isinstance(dados, pd.DataFrame) or dados.empty:
                logger.warning(f"Dados inválidos para ativo {nome_ativo}")
                continue

            if len(dados) < self.config['janela_correlacao_dias']:
                logger.warning(f"Dados insuficientes para {nome_ativo}: {len(dados)} períodos < {self.config['janela_correlacao_dias']}")

        return True

    def _criar_resultado_erro(self, mensagem_erro: str) -> ResultadoModulo:
        """
        Cria resultado de erro padronizado.

        Args:
            mensagem_erro: Mensagem de erro

        Returns:
            ResultadoModulo: Resultado com erro
        """
        return ResultadoModulo(
            timestamp=datetime.now(),
            status='ERROR',
            dados_analisados={'erro': mensagem_erro},
            metricas={},
            confianca=0.0,
            metadados={
                'modulo': 'correlation_analysis',
                'erro': mensagem_erro,
                'timestamp': datetime.now()
            }
        )