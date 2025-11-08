# Sistema de Detecção de Oportunidades Assimétricas
# Framework Quantitativo Avançado - Fase 1
# Arquitetura: Pattern Recognition → Macro Confluence → Correlation → Event Mapping → Risk-Reward → Timing

"""
FRAMEWORK DE DETECÇÃO ASSIMÉTRICA

Este módulo implementa um sistema completo de detecção de oportunidades assimétricas
no mercado brasileiro através da fusão de análise técnica e macroeconômica.

Arquitetura 6-etapas:
1. Pattern Recognition: Identificação de padrões técnicos (RSI, médias, momentum)
2. Macro Confluence: Análise de convergência macro (Selic, câmbio, fluxo)
3. Correlation Analysis: Análise de correlação multi-ativo (Ibovespa vs dólar/commodities)
4. Event Mapping: Mapeamento de eventos econômicos e pontuação de risco
5. Risk-Reward Calculation: Cálculo de assimetria e pontuação de oportunidade
6. Timing Optimization: Otimização de timing de entrada/saída

Objetivos:
- Win Rate ≥70% em setups identificados historicamente
- Risk-Reward Ratio > 2.0 para oportunidades
- Tempo de processamento < 5 segundos
- False positives < 30%
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class SetupAssimetrico:
    """Representa um setup de oportunidade assimétrica identificado"""
    timestamp: datetime
    ativo: str
    direcao: str  # 'LONG' ou 'SHORT'
    pontuacao_assimetria: float  # 0-100
    risk_reward_ratio: float
    confianca: float  # 0-100
    componentes: Dict[str, Any]  # Detalhes de cada módulo
    validade: datetime  # Até quando o setup é válido

@dataclass
class ResultadoAnalise:
    """Resultado completo da análise assimétrica"""
    timestamp: datetime
    setups_identificados: List[SetupAssimetrico]
    tempo_processamento: float
    status: str  # 'SUCCESS', 'PARTIAL', 'ERROR'
    metadados: Dict[str, Any]

class FrameworkAssimetrico:
    """
    Framework principal para detecção de oportunidades assimétricas.
    Coordena os 6 módulos do processo de análise.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Inicializa o framework com configuração customizada.

        Args:
            config: Dicionário com configurações do framework
        """
        self.config = config or self._configuracao_padrao()
        self.modulos = {}
        self._inicializar_modulos()

        logger.info("Framework de Detecção Assimétrica inicializado")
        logger.info(f"Configuração: {self.config}")

    def _configuracao_padrao(self) -> Dict[str, Any]:
        """Retorna configuração padrão do framework"""
        return {
            'ativos_principais': ['WIN', 'IBOV', 'DOL'],
            'janela_analise_dias': 90,
            'threshold_assimetria': 60,  # Pontuação mínima para considerar oportunidade
            'max_setups_por_analise': 3,
            'timeout_processamento': 30,  # segundos
            'cache_resultados': True,
            'validade_setup_horas': 24
        }

    def _inicializar_modulos(self):
        """Inicializa todos os módulos do framework"""
        try:
            # Importar módulos disponíveis (implementados)
            modulos_disponiveis = {}

            # Pattern Recognition - Implementado
            try:
                from .modulo_pattern_recognition import ModuloPatternRecognition
                modulos_disponiveis['pattern_recognition'] = ModuloPatternRecognition(self.config)
                logger.info("Módulo Pattern Recognition carregado")
            except ImportError as e:
                logger.warning(f"Módulo Pattern Recognition não disponível: {e}")

            # Macro Confluence - Implementado
            try:
                from .modulo_macro_confluence import ModuloMacroConfluence
                modulos_disponiveis['macro_confluence'] = ModuloMacroConfluence(self.config)
                logger.info("Módulo Macro Confluence carregado")
            except ImportError as e:
                logger.warning(f"Módulo Macro Confluence não disponível: {e}")

            # Correlation Analysis - Implementado
            try:
                from .modulo_correlation_analysis import ModuloCorrelationAnalysis
                modulos_disponiveis['correlation_analysis'] = ModuloCorrelationAnalysis(self.config)
                logger.info("Módulo Correlation Analysis carregado")
            except ImportError as e:
                logger.warning(f"Módulo Correlation Analysis não disponível: {e}")

            # Event Mapping - Implementado
            try:
                from .modulo_event_mapping import ModuloEventMapping
                modulos_disponiveis['event_mapping'] = ModuloEventMapping(self.config)
                logger.info("Módulo Event Mapping carregado")
            except ImportError as e:
                logger.warning(f"Módulo Event Mapping não disponível: {e}")

            # Risk-Reward - Implementado
            try:
                from .modulo_risk_reward import ModuloRiskReward
                modulos_disponiveis['risk_reward'] = ModuloRiskReward(self.config)
                logger.info("Módulo Risk-Reward carregado")
            except ImportError as e:
                logger.warning(f"Módulo Risk-Reward não disponível: {e}")

            # Timing Optimization - Implementado
            try:
                from .modulo_timing_optimization import ModuloTimingOptimization
                modulos_disponiveis['timing_optimization'] = ModuloTimingOptimization(self.config)
                logger.info("Módulo Timing Optimization carregado")
            except ImportError as e:
                logger.warning(f"Módulo Timing Optimization não disponível: {e}")

            # Outros módulos - ainda não implementados
            modulos_nao_implementados = [
                # Todos os módulos principais já implementados
            ]

            for modulo in modulos_nao_implementados:
                try:
                    modulo_class = modulo.replace('modulo_', 'Modulo').replace('_', ' ').title().replace(' ', '')
                    exec(f"from .{modulo} import {modulo_class}")
                    exec(f"modulos_disponiveis['{modulo.replace('modulo_', '').replace('_', '_')}'] = {modulo_class}(self.config)")
                    logger.info(f"Módulo {modulo} carregado")
                except ImportError:
                    logger.debug(f"Módulo {modulo} ainda não implementado")
                except Exception as e:
                    logger.warning(f"Erro ao carregar módulo {modulo}: {e}")

            self.modulos = modulos_disponiveis

            if self.modulos:
                logger.info(f"Módulos carregados: {list(self.modulos.keys())}")
            else:
                logger.warning("Nenhum módulo disponível")

        except Exception as e:
            logger.error(f"Erro na inicialização dos módulos: {e}")
            self.modulos = {}

    def analisar_oportunidades(self,
                             dados_mercado: Dict[str, pd.DataFrame],
                             dados_macroeconomicos: Optional[Dict[str, Any]] = None,
                             calendario_eventos: Optional[pd.DataFrame] = None) -> ResultadoAnalise:
        """
        Executa análise completa de detecção de oportunidades assimétricas.

        Args:
            dados_mercado: Dados de mercado por ativo (OHLCV)
            dados_macroeconomicos: Dados macro (Selic, câmbio, fluxo)
            calendario_eventos: Calendário de eventos econômicos

        Returns:
            ResultadoAnalise: Resultado completo da análise
        """
        inicio = datetime.now()

        try:
            logger.info("Iniciando análise de oportunidades assimétricas")
            logger.info(f"Ativos analisados: {list(dados_mercado.keys())}")

            # Etapa 1: Pattern Recognition
            padroes_tecnicos = self._executar_pattern_recognition(dados_mercado)

            # Etapa 2: Macro Confluence
            confluencia_macro = self._executar_macro_confluence(dados_macroeconomicos)

            # Etapa 3: Correlation Analysis
            correlacoes = self._executar_correlation_analysis(dados_mercado)

            # Etapa 4: Event Mapping
            eventos_mapeados = self._executar_event_mapping(calendario_eventos)

            # Etapa 5: Risk-Reward Calculation
            calculos_risco = self._executar_risk_reward_calculation(
                padroes_tecnicos, confluencia_macro, correlacoes, eventos_mapeados
            )

            # Etapa 6: Timing Optimization
            setups_otimizados = self._executar_timing_optimization(calculos_risco)

            # Filtrar setups por threshold de assimetria
            setups_filtrados = [
                setup for setup in setups_otimizados
                if setup.pontuacao_assimetria >= self.config['threshold_assimetria']
            ]

            # Limitar número máximo de setups
            setups_finais = setups_filtrados[:self.config['max_setups_por_analise']]

            tempo_processamento = (datetime.now() - inicio).total_seconds()

            resultado = ResultadoAnalise(
                timestamp=datetime.now(),
                setups_identificados=setups_finais,
                tempo_processamento=tempo_processamento,
                status='SUCCESS' if setups_finais else 'PARTIAL',
                metadados={
                    'total_setups_antes_filtro': len(setups_otimizados),
                    'setups_filtrados_threshold': len(setups_filtrados),
                    'setups_finais': len(setups_finais),
                    'modulos_executados': list(self.modulos.keys()),
                    'configuracao': self.config
                }
            )

            logger.info(f"Análise concluída em {tempo_processamento:.2f}s")
            logger.info(f"Setups identificados: {len(setups_finais)}")

            return resultado

        except Exception as e:
            logger.error(f"Erro na análise: {e}")
            tempo_processamento = (datetime.now() - inicio).total_seconds()

            return ResultadoAnalise(
                timestamp=datetime.now(),
                setups_identificados=[],
                tempo_processamento=tempo_processamento,
                status='ERROR',
                metadados={'erro': str(e)}
            )

    def _executar_pattern_recognition(self, dados_mercado: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Executa análise de padrões técnicos"""
        if 'pattern_recognition' not in self.modulos:
            logger.warning("Módulo Pattern Recognition não disponível")
            return {}

        return self.modulos['pattern_recognition'].analisar(dados_mercado)

    def _executar_macro_confluence(self, dados_macroeconomicos: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Executa análise de confluência macroeconômica"""
        if 'macro_confluence' not in self.modulos:
            logger.warning("Módulo Macro Confluence não disponível")
            return {}

        return self.modulos['macro_confluence'].analisar(dados_macroeconomicos)

    def _executar_correlation_analysis(self, dados_mercado: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Executa análise de correlação multi-ativo"""
        if 'correlation_analysis' not in self.modulos:
            logger.warning("Módulo Correlation Analysis não disponível")
            return {}

        return self.modulos['correlation_analysis'].analisar(dados_mercado)

    def _executar_event_mapping(self, calendario_eventos: Optional[pd.DataFrame]) -> Dict[str, Any]:
        """Executa mapeamento de eventos econômicos"""
        if 'event_mapping' not in self.modulos:
            logger.warning("Módulo Event Mapping não disponível")
            return {}

        return self.modulos['event_mapping'].analisar(calendario_eventos)

    def _executar_risk_reward_calculation(self,
                                        padroes_tecnicos: Dict[str, Any],
                                        confluencia_macro: Dict[str, Any],
                                        correlacoes: Dict[str, Any],
                                        eventos_mapeados: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Executa cálculo de risco-recompensa"""
        if 'risk_reward' not in self.modulos:
            logger.warning("Módulo Risk-Reward não disponível")
            return []

        # Preparar dados para o módulo Risk-Reward
        # Todos os resultados são ResultadoModulo, então acessar dados_analisados
        dados_risk_reward = {
            'componentes_analise': {
                'confluencia_tecnica': padroes_tecnicos.dados_analisados.get('confluencia_geral', 50) if hasattr(padroes_tecnicos, 'dados_analisados') else 50,
                'confluencia_macro': confluencia_macro.dados_analisados.get('confluencia_geral', 50) if hasattr(confluencia_macro, 'dados_analisados') else 50,
                'confluencia_correlacao': correlacoes.dados_analisados.get('confluencia_geral', 50) if hasattr(correlacoes, 'dados_analisados') else 50,
                'impacto_eventos': eventos_mapeados.dados_analisados.get('impacto_geral', 50) if hasattr(eventos_mapeados, 'dados_analisados') else 50,
                'setups_tecnicos': padroes_tecnicos.dados_analisados.get('setups_identificados', []) if hasattr(padroes_tecnicos, 'dados_analisados') else [],
                'momentum_tecnico': padroes_tecnicos.dados_analisados.get('momentum_geral', 50) if hasattr(padroes_tecnicos, 'dados_analisados') else 50,
                'momentum_macro': confluencia_macro.dados_analisados.get('momentum_geral', 50) if hasattr(confluencia_macro, 'dados_analisados') else 50,
                'momentum_correlacao': correlacoes.dados_analisados.get('momentum_geral', 50) if hasattr(correlacoes, 'dados_analisados') else 50,
                'rsi_alinhado': padroes_tecnicos.dados_analisados.get('rsi_alinhado', False) if hasattr(padroes_tecnicos, 'dados_analisados') else False,
                'sma_alinhada': padroes_tecnicos.dados_analisados.get('sma_alinhada', False) if hasattr(padroes_tecnicos, 'dados_analisados') else False,
                'momentum_positivo': padroes_tecnicos.dados_analisados.get('momentum_positivo', False) if hasattr(padroes_tecnicos, 'dados_analisados') else False,
                'volatilidade_alta': padroes_tecnicos.dados_analisados.get('volatilidade_alta', False) if hasattr(padroes_tecnicos, 'dados_analisados') else False,
                'evento_proximo': eventos_mapeados.dados_analisados.get('evento_critico_proximo', False) if hasattr(eventos_mapeados, 'dados_analisados') else False
            }
        }

        resultado = self.modulos['risk_reward'].analisar(dados_risk_reward)

        # Retornar setups aprovados - resultado é um ResultadoModulo
        if hasattr(resultado, 'dados_analisados') and isinstance(resultado.dados_analisados, dict):
            return resultado.dados_analisados.get('setups_aprovados', [])
        else:
            logger.warning("Resultado do módulo Risk-Reward não tem estrutura esperada")
            return []

    def _executar_timing_optimization(self, calculos_risco: List[Dict[str, Any]]) -> List[SetupAssimetrico]:
        """Executa otimização de timing"""
        if 'timing_optimization' not in self.modulos:
            logger.warning("Módulo Timing Optimization não disponível")
            return []

        # Preparar dados para o módulo Timing Optimization
        dados_timing = {
            'setups_aprovados': calculos_risco,
            'dados_mercado': {}  # Dados de mercado seriam necessários para timing real
        }

        resultado = self.modulos['timing_optimization'].analisar(dados_timing)

        # Converter timings otimizados para SetupAssimetrico
        setups_otimizados = []
        if hasattr(resultado, 'dados_analisados') and 'timings_otimizados' in resultado.dados_analisados:
            for timing in resultado.dados_analisados['timings_otimizados']:
                try:
                    setup = SetupAssimetrico(
                        timestamp=timing['timestamp_entrada'],
                        ativo=timing['ativo'],
                        direcao=timing['direcao'],
                        pontuacao_assimetria=timing.get('setup_original', {}).get('pontuacao_assimetria', 70),
                        risk_reward_ratio=timing.get('setup_original', {}).get('risk_reward_ratio', 1.5),
                        confianca=timing['confianca'],
                        componentes={
                            'timing_otimizado': timing,
                            'momentum_entrada': timing['momentum_entrada'],
                            'momentum_saida': timing['momentum_saida'],
                            'liquidez_entrada': timing['liquidez_entrada'],
                            'liquidez_saida': timing['liquidez_saida'],
                            'volatilidade_ajustada': timing['volatilidade_ajustada'],
                            'score_timing': timing['score_timing']
                        },
                        validade=timing['timestamp_saida']
                    )
                    setups_otimizados.append(setup)
                except Exception as e:
                    logger.error(f"Erro ao converter timing para SetupAssimetrico: {e}")
                    continue

        return setups_otimizados

    def obter_metricas_framework(self) -> Dict[str, Any]:
        """
        Retorna métricas de performance do framework.

        Returns:
            Dict com métricas do framework
        """
        return {
            'modulos_carregados': list(self.modulos.keys()),
            'configuracao_atual': self.config,
            'status_modulos': {
                nome: 'ATIVO' if hasattr(modulo, 'analisar') else 'INATIVO'
                for nome, modulo in self.modulos.items()
            },
            'timestamp': datetime.now().isoformat()
        }

    def validar_setup(self, setup: SetupAssimetrico) -> bool:
        """
        Valida se um setup ainda é válido baseado no tempo e condições de mercado.

        Args:
            setup: Setup a ser validado

        Returns:
            bool: True se válido, False caso contrário
        """
        agora = datetime.now()

        # Verificar validade temporal
        if agora > setup.validade:
            return False

        # Verificar condições de mercado (a implementar)
        # - Volatilidade não excessiva
        # - Liquidez adequada
        # - Ausência de eventos de alto impacto

        return True

    def gerar_playbook_operacional(self,
                                  dados_mercado: Dict[str, pd.DataFrame],
                                  salvar_arquivo: bool = True) -> str:
        """
        Gera playbook operacional integrado com análise assimétrica.

        Args:
            dados_mercado: Dados de mercado para análise
            salvar_arquivo: Se deve salvar o playbook em arquivo

        Returns:
            Conteúdo do playbook gerado
        """
        try:
            # Importar gerador de playbook
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from gerador_playbook_win import GeradorPlaybookWIN

            # Executar análise rápida para contexto
            analise_rapida = self._executar_analise_rapida(dados_mercado)

            # Gerar playbook com dados de mercado coletados
            gerador = GeradorPlaybookWIN()
            playbook = gerador.gerar_playbook(salvar_arquivo=salvar_arquivo)

            # Adicionar insights da análise assimétrica
            playbook_com_insights = self._integrar_insights_playbook(playbook, analise_rapida)

            logger.info("Playbook operacional gerado com integração de análise assimétrica")
            return playbook_com_insights

        except Exception as e:
            logger.error(f"Erro ao gerar playbook operacional: {e}")
            return f"Erro na geração do playbook: {e}"

    def _executar_analise_rapida(self, dados_mercado: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Executa análise rápida para fornecer contexto ao playbook"""
        insights = {}

        try:
            # Análise técnica básica do WIN
            if 'WIN' in dados_mercado:
                win_data = dados_mercado['WIN']
                if len(win_data) >= 20:
                    # RSI
                    delta = win_data['Close'].diff()
                    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                    rs = gain / loss
                    rsi = 100 - (100 / (1 + rs))
                    insights['rsi_atual'] = rsi.iloc[-1] if not rsi.empty else 50

                    # Momentum
                    momentum = win_data['Close'].pct_change(5).iloc[-1] * 100
                    insights['momentum_5d'] = momentum

                    # Volatilidade
                    volatilidade = win_data['Close'].pct_change().std() * 100
                    insights['volatilidade_diaria'] = volatilidade

            # Correlação WIN x Dólar se disponível
            if 'WIN' in dados_mercado and 'DOL' in dados_mercado:
                correlacao = dados_mercado['WIN']['Close'].corr(dados_mercado['DOL']['Close'])
                insights['correlacao_win_dol'] = correlacao

        except Exception as e:
            logger.warning(f"Erro na análise rápida: {e}")

        return insights

    def _integrar_insights_playbook(self, playbook: str, insights: Dict[str, Any]) -> str:
        """Integra insights da análise assimétrica no playbook"""
        try:
            # Adicionar seção de insights técnicos
            secao_insights = "\n## 🤖 INSIGHTS DA ANÁLISE ASSIMÉTRICA\n\n"

            if 'rsi_atual' in insights:
                rsi = insights['rsi_atual']
                if rsi > 70:
                    status_rsi = "🔴 Sobrecomprado"
                elif rsi < 30:
                    status_rsi = "🟢 Sobrevendido"
                else:
                    status_rsi = "🟡 Neutro"
                secao_insights += f"**RSI Atual:** {rsi:.1f} - {status_rsi}\n\n"

            if 'momentum_5d' in insights:
                momentum = insights['momentum_5d']
                if momentum > 1:
                    status_momentum = "🟢 Forte alta"
                elif momentum < -1:
                    status_momentum = "🔴 Forte baixa"
                else:
                    status_momentum = "🟡 Neutro"
                secao_insights += f"**Momentum 5D:** {momentum:.2f}% - {status_momentum}\n\n"

            if 'volatilidade_diaria' in insights:
                vol = insights['volatilidade_diaria']
                if vol > 2:
                    status_vol = "🔴 Alta volatilidade"
                elif vol < 1:
                    status_vol = "🟢 Baixa volatilidade"
                else:
                    status_vol = "🟡 Volatilidade média"
                secao_insights += f"**Volatilidade Diária:** {vol:.2f}% - {status_vol}\n\n"

            if 'correlacao_win_dol' in insights:
                corr = insights['correlacao_win_dol']
                if abs(corr) > 0.7:
                    status_corr = "🔗 Forte correlação"
                elif abs(corr) > 0.3:
                    status_corr = "🔄 Correlação moderada"
                else:
                    status_corr = "⚪ Baixa correlação"
                secao_insights += f"**Correlação WIN×Dólar:** {corr:.2f} - {status_corr}\n\n"

            secao_insights += "---\n\n"

            # Inserir antes da seção de notas livres
            playbook_atualizado = playbook.replace(
                "## 📓 NOTAS LIVRES",
                secao_insights + "## 📓 NOTAS LIVRES"
            )

            return playbook_atualizado

        except Exception as e:
            logger.error(f"Erro ao integrar insights: {e}")
            return playbook


# Função principal para uso standalone
def executar_analise_assimetrica(dados_mercado: Dict[str, pd.DataFrame],
                                dados_macroeconomicos: Optional[Dict[str, Any]] = None,
                                calendario_eventos: Optional[pd.DataFrame] = None,
                                config: Optional[Dict[str, Any]] = None) -> ResultadoAnalise:
    """
    Função principal para executar análise assimétrica.

    Args:
        dados_mercado: Dados de mercado por ativo
        dados_macroeconomicos: Dados macroeconômicos
        calendario_eventos: Calendário de eventos
        config: Configuração customizada

    Returns:
        ResultadoAnalise: Resultado da análise
    """
    framework = FrameworkAssimetrico(config)
    return framework.analisar_oportunidades(dados_mercado, dados_macroeconomicos, calendario_eventos)


if __name__ == "__main__":
    # Exemplo de uso
    print("Framework de Detecção Assimétrica - Arquitetura Base")
    print("=" * 60)

    # Inicializar framework
    framework = FrameworkAssimetrico()

    # Obter métricas
    metricas = framework.obter_metricas_framework()

    print("Status do Framework:")
    for chave, valor in metricas.items():
        print(f"  {chave}: {valor}")

    print("\nFramework pronto para implementação dos módulos!")