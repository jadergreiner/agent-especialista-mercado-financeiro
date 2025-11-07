# Módulo Macro Confluence
# Etapa 2 do Framework Assimétrico
# Responsável por analisar convergência macroeconômica

"""
MÓDULO MACRO CONFLUENCE

Este módulo implementa a segunda etapa do framework de detecção assimétrica:
análise de convergência entre indicadores macroeconômicos e condições de mercado.

Indicadores Macro Analisados:
- Taxa Selic (Banco Central)
- Taxa de Câmbio (USD/BRL)
- Fluxo de Capitais (investimento estrangeiro)
- Balança Comercial
- Inflação (IPCA/IGP-M)

Objetivos:
- Identificar convergência favorável entre macro e técnico
- Avaliar impacto de política monetária
- Detectar fluxos de capitais positivos
- Calcular pontuação de confluência macro (0-100)
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Imports para execução direta (quando não usado como módulo)
try:
    from .interfaces import (
        ModuloMacroConfluenceInterface,
        ResultadoModulo,
        CONFIG_PADRAO_MACRO_CONFLUENCE
    )
except ImportError:
    # Para execução direta do arquivo
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

    from interfaces import (
        ModuloMacroConfluenceInterface,
        ResultadoModulo,
        CONFIG_PADRAO_MACRO_CONFLUENCE
    )

logger = logging.getLogger(__name__)


class ModuloMacroConfluence(ModuloMacroConfluenceInterface):
    """
    Módulo responsável por análise de confluência macroeconômica.
    Avalia convergência entre Selic, câmbio, fluxo de capitais e condições técnicas.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Inicializa o módulo Macro Confluence.

        Args:
            config: Configuração específica do módulo
        """
        config_completo = {**CONFIG_PADRAO_MACRO_CONFLUENCE, **(config or {})}
        super().__init__(config_completo)

        logger.info("Módulo Macro Confluence inicializado")

    def _validar_configuracao_especifica(self):
        """Validação específica do módulo Macro Confluence"""
        required_indicators = ['SELIC', 'CAMBIO', 'FLUXO_CAPITAIS']
        configured_indicators = self.config.get('indicadores_macro', [])

        for indicator in required_indicators:
            if indicator not in configured_indicators:
                raise ValueError(f"Indicador macro obrigatório não configurado: {indicator}")

        # Validar parâmetros de análise
        if not (0.1 <= self.config.get('peso_selic', 0.3) <= 1.0):
            raise ValueError("Peso Selic deve estar entre 0.1 e 1.0")

        if not (0.1 <= self.config.get('peso_cambio', 0.3) <= 1.0):
            raise ValueError("Peso câmbio deve estar entre 0.1 e 1.0")

        if not (0.1 <= self.config.get('peso_fluxo', 0.4) <= 1.0):
            raise ValueError("Peso fluxo deve estar entre 0.1 e 1.0")

    def analisar(self, dados_macroeconomicos: Dict[str, Any]) -> ResultadoModulo:
        """
        Executa análise completa de confluência macroeconômica.

        Args:
            dados_macroeconomicos: Dict com dados macro (Selic, câmbio, fluxo, etc.)

        Returns:
            ResultadoModulo: Resultado da análise
        """
        inicio = datetime.now()

        try:
            logger.info("Iniciando análise de confluência macroeconômica")

            # Validar dados de entrada
            dados_validos = self._validar_dados_macroeconomicos(dados_macroeconomicos)
            if not dados_validos:
                return ResultadoModulo(
                    timestamp=datetime.now(),
                    status='ERROR',
                    dados_analisados={},
                    metricas={},
                    confianca=0.0,
                    metadados={'erro': 'Dados macroeconômicos insuficientes ou inválidos'}
                )

            # Análise individual de cada indicador
            analise_selic = self._analisar_selic(dados_macroeconomicos)
            analise_cambio = self._analisar_cambio(dados_macroeconomicos)
            analise_fluxo = self._analisar_fluxo_capitais(dados_macroeconomicos)

            # Cálculo de confluência geral
            pontuacao_confluencia = self._calcular_confluencia_geral(
                analise_selic, analise_cambio, analise_fluxo
            )

            # Análise de impacto no mercado
            impacto_mercado = self._analisar_impacto_mercado(
                analise_selic, analise_cambio, analise_fluxo, pontuacao_confluencia
            )

            # Calcular confiança da análise
            confianca = self._calcular_confianca_analise(
                analise_selic, analise_cambio, analise_fluxo
            )

            # Resultados consolidados
            resultados_analise = {
                'analise_selic': analise_selic,
                'analise_cambio': analise_cambio,
                'analise_fluxo': analise_fluxo,
                'pontuacao_confluencia': pontuacao_confluencia,
                'impacto_mercado': impacto_mercado,
                'periodo_analisado': self.config['janela_analise_dias']
            }

            # Métricas da análise
            metricas = {
                'indicadores_analisados': len(self.config['indicadores_macro']),
                'confluencia_geral': pontuacao_confluencia,
                'tendencia_macro': impacto_mercado['tendencia_geral'],
                'forca_confluencia': impacto_mercado['forca_sinal'],
                'dados_processados': len(dados_macroeconomicos) if dados_macroeconomicos else 0
            }

            resultado = ResultadoModulo(
                timestamp=datetime.now(),
                status='SUCCESS',
                dados_analisados=resultados_analise,
                metricas=metricas,
                confianca=confianca,
                metadados={
                    'tempo_processamento': (datetime.now() - inicio).total_seconds(),
                    'fonte_dados': 'dados_fornecidos',
                    'indicadores_macro': self.config['indicadores_macro']
                }
            )

            logger.info(f"Análise Macro Confluence concluída: Confluência {pontuacao_confluencia:.1f}%")
            return resultado

        except Exception as e:
            logger.error(f"Erro na análise Macro Confluence: {e}")
            return ResultadoModulo(
                timestamp=datetime.now(),
                status='ERROR',
                dados_analisados={},
                metricas={},
                confianca=0.0,
                metadados={'erro': str(e)}
            )

    def _validar_dados_macroeconomicos(self, dados: Dict[str, Any]) -> bool:
        """Valida se os dados macroeconômicos são suficientes para análise"""
        if not dados:
            return False

        # Verificar presença dos indicadores obrigatórios
        indicadores_obrigatorios = ['selic', 'cambio', 'fluxo_capitais']
        for indicador in indicadores_obrigatorios:
            if indicador not in dados:
                logger.warning(f"Indicador obrigatório ausente: {indicador}")
                return False

        # Verificar se há dados suficientes (mínimo 30 dias)
        for indicador, valores in dados.items():
            if isinstance(valores, (list, pd.Series)) and len(valores) < 30:
                logger.warning(f"Dados insuficientes para {indicador}: {len(valores)} pontos")
                return False

        return True

    def analisar_selic(self, dados_selic: pd.Series) -> Dict[str, Any]:
        """Analisa impacto da taxa Selic"""
        return self._analisar_selic({'selic': dados_selic})

    def analisar_cambio(self, dados_cambio: pd.DataFrame) -> Dict[str, Any]:
        """Analisa impacto do câmbio"""
        return self._analisar_cambio({'cambio': dados_cambio})

    def analisar_fluxo(self, dados_fluxo: pd.DataFrame) -> Dict[str, Any]:
        """Analisa fluxo cambial"""
        return self._analisar_fluxo_capitais({'fluxo_capitais': dados_fluxo})

    def calcular_confluencia_macro(self, analises: Dict[str, Any]) -> float:
        """Calcula grau de confluência macroeconômica"""
        # Adaptar formato dos dados para o método interno
        analise_selic = analises.get('selic', {})
        analise_cambio = analises.get('cambio', {})
        analise_fluxo = analises.get('fluxo', {})

        return self._calcular_confluencia_geral(analise_selic, analise_cambio, analise_fluxo)
        """Valida se os dados macroeconômicos são suficientes para análise"""
        if not dados:
            return False

        # Verificar presença dos indicadores obrigatórios
        indicadores_obrigatorios = ['selic', 'cambio', 'fluxo_capitais']
        for indicador in indicadores_obrigatorios:
            if indicador not in dados:
                logger.warning(f"Indicador obrigatório ausente: {indicador}")
                return False

        # Verificar se há dados suficientes (mínimo 30 dias)
        for indicador, valores in dados.items():
            if isinstance(valores, (list, pd.Series)) and len(valores) < 30:
                logger.warning(f"Dados insuficientes para {indicador}: {len(valores)} pontos")
                return False

        return True

    def _analisar_selic(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa taxa Selic e sua tendência"""
        selic_dados = dados.get('selic', [])

        if isinstance(selic_dados, list):
            selic_series = pd.Series(selic_dados)
        elif isinstance(selic_dados, pd.Series):
            selic_series = selic_dados
        else:
            return {'erro': 'Formato de dados Selic inválido'}

        # Remover valores NaN
        selic_series = selic_series.dropna()

        if len(selic_series) < 10:
            return {'erro': 'Dados Selic insuficientes'}

        # Análise da Selic atual
        selic_atual = selic_series.iloc[-1]
        selic_anterior = selic_series.iloc[-2] if len(selic_series) > 1 else selic_atual

        # Tendência da Selic (comparação com média histórica)
        media_historica = selic_series.mean()
        desvio_padrao = selic_series.std()

        # Classificação da Selic
        if selic_atual < media_historica - desvio_padrao:
            classificacao = "BAIXA_HISTORICA"
            pontuacao = 80  # Favorável para ativos de risco
        elif selic_atual < media_historica:
            classificacao = "MODERADA_BAIXA"
            pontuacao = 60
        elif selic_atual < media_historica + desvio_padrao:
            classificacao = "MODERADA_ALTA"
            pontuacao = 40
        else:
            classificacao = "ALTA_HISTORICA"
            pontuacao = 20  # Desfavorável para ativos de risco

        # Tendência recente (últimos 5 dias)
        if len(selic_series) >= 5:
            tendencia_recente = selic_series.iloc[-5:].mean()
            if tendencia_recente < selic_atual:
                tendencia = "CRESCENTE"
                ajuste_pontuacao = -10  # Selic crescendo = pior para mercado
            elif tendencia_recente > selic_atual:
                tendencia = "DECRESCENTE"
                ajuste_pontuacao = +10  # Selic caindo = melhor para mercado
            else:
                tendencia = "ESTAVEL"
                ajuste_pontuacao = 0
        else:
            tendencia = "INSUFICIENTE"
            ajuste_pontuacao = 0

        pontuacao_final = max(0, min(100, pontuacao + ajuste_pontuacao))

        return {
            'selic_atual': selic_atual,
            'selic_anterior': selic_anterior,
            'media_historica': media_historica,
            'desvio_padrao': desvio_padrao,
            'classificacao': classificacao,
            'tendencia_recente': tendencia,
            'pontuacao': pontuacao_final,
            'favoravel_mercado': pontuacao_final >= 50
        }

    def _analisar_cambio(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa taxa de câmbio USD/BRL"""
        cambio_dados = dados.get('cambio', [])

        if isinstance(cambio_dados, list):
            cambio_series = pd.Series(cambio_dados)
        elif isinstance(cambio_dados, pd.Series):
            cambio_series = cambio_dados
        else:
            return {'erro': 'Formato de dados câmbio inválido'}

        cambio_series = cambio_series.dropna()

        if len(cambio_series) < 10:
            return {'erro': 'Dados câmbio insuficientes'}

        # Análise do câmbio atual
        cambio_atual = cambio_series.iloc[-1]
        cambio_anterior = cambio_series.iloc[-2] if len(cambio_series) > 1 else cambio_atual

        # Estatísticas históricas
        media_historica = cambio_series.mean()
        minimo_historico = cambio_series.min()
        maximo_historico = cambio_series.max()

        # Volatilidade do câmbio
        volatilidade = cambio_series.pct_change().std() * np.sqrt(252)  # Anualizada

        # Classificação do câmbio
        # Para o real brasileiro, câmbio alto (reais por dólar) é negativo
        # Câmbio baixo é positivo (dólar mais barato = exportações favorecidas)
        if cambio_atual < media_historica * 0.9:  # 10% abaixo da média
            classificacao = "DESVALORIZADO"
            pontuacao = 80  # Muito favorável para exportações
        elif cambio_atual < media_historica:
            classificacao = "MODERADAMENTE_DESVALORIZADO"
            pontuacao = 60
        elif cambio_atual < media_historica * 1.1:  # 10% acima da média
            classificacao = "MODERADAMENTE_VALORIZADO"
            pontuacao = 40
        else:
            classificacao = "VALORIZADO"
            pontuacao = 20  # Desfavorável para exportações

        # Tendência recente
        if len(cambio_series) >= 5:
            cambio_5d_atras = cambio_series.iloc[-5]
            variacao_5d = (cambio_atual - cambio_5d_atras) / cambio_5d_atras * 100

            if variacao_5d < -2:  # Câmbio caindo > 2%
                tendencia = "DEPRECIACAO_FORTE"
                ajuste_pontuacao = +15  # Depreciação favorável
            elif variacao_5d < 0:
                tendencia = "DEPRECIACAO_LEVE"
                ajuste_pontuacao = +5
            elif variacao_5d > 2:  # Câmbio subindo > 2%
                tendencia = "APRECIACAO_FORTE"
                ajuste_pontuacao = -15  # Apreciação desfavorável
            elif variacao_5d > 0:
                tendencia = "APRECIACAO_LEVE"
                ajuste_pontuacao = -5
            else:
                tendencia = "ESTAVEL"
                ajuste_pontuacao = 0
        else:
            tendencia = "INSUFICIENTE"
            ajuste_pontuacao = 0

        pontuacao_final = max(0, min(100, pontuacao + ajuste_pontuacao))

        return {
            'cambio_atual': cambio_atual,
            'cambio_anterior': cambio_anterior,
            'media_historica': media_historica,
            'minimo_historico': minimo_historico,
            'maximo_historico': maximo_historico,
            'volatilidade_anualizada': volatilidade,
            'classificacao': classificacao,
            'tendencia_recente': tendencia,
            'variacao_5d_percentual': variacao_5d if 'variacao_5d' in locals() else 0,
            'pontuacao': pontuacao_final,
            'favoravel_mercado': pontuacao_final >= 50
        }

    def _analisar_fluxo_capitais(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa fluxo de capitais estrangeiros"""
        fluxo_dados = dados.get('fluxo_capitais', [])

        if isinstance(fluxo_dados, list):
            fluxo_series = pd.Series(fluxo_dados)
        elif isinstance(fluxo_dados, pd.Series):
            fluxo_series = fluxo_dados
        else:
            return {'erro': 'Formato de dados fluxo inválido'}

        fluxo_series = fluxo_series.dropna()

        if len(fluxo_series) < 10:
            return {'erro': 'Dados fluxo insuficientes'}

        # Análise do fluxo atual
        fluxo_atual = fluxo_series.iloc[-1]

        # Estatísticas históricas
        media_historica = fluxo_series.mean()
        mediana_historica = fluxo_series.median()

        # Fluxo positivo = entrada de capitais (favorável)
        # Fluxo negativo = saída de capitais (desfavorável)

        # Classificação do fluxo
        if fluxo_atual > media_historica * 1.5:  # 50% acima da média
            classificacao = "ENTRADA_FORTE"
            pontuacao = 90  # Muito favorável
        elif fluxo_atual > media_historica:
            classificacao = "ENTRADA_MODERADA"
            pontuacao = 70
        elif fluxo_atual > media_historica * 0.5:  # 50% da média
            classificacao = "ENTRADA_FRACA"
            pontuacao = 50
        elif fluxo_atual > 0:
            classificacao = "NEUTRO_POSITIVO"
            pontuacao = 40
        elif fluxo_atual > media_historica * -0.5:  # -50% da média
            classificacao = "SAIDA_FRACA"
            pontuacao = 30
        elif fluxo_atual > media_historica * -1.5:  # -150% da média
            classificacao = "SAIDA_MODERADA"
            pontuacao = 20
        else:
            classificacao = "SAIDA_FORTE"
            pontuacao = 10  # Muito desfavorável

        # Tendência do fluxo (últimos 10 dias)
        if len(fluxo_series) >= 10:
            fluxo_10d = fluxo_series.iloc[-10:]
            tendencia_10d = fluxo_10d.mean()

            if tendencia_10d > media_historica * 1.2:
                tendencia = "ENTRADA_ACELERADA"
                ajuste_pontuacao = +10
            elif tendencia_10d > media_historica:
                tendencia = "ENTRADA_ESTAVEL"
                ajuste_pontuacao = +5
            elif tendencia_10d > media_historica * 0.8:
                tendencia = "NEUTRO"
                ajuste_pontuacao = 0
            elif tendencia_10d > media_historica * 0.5:
                tendencia = "SAIDA_LEVE"
                ajuste_pontuacao = -5
            else:
                tendencia = "SAIDA_ACELERADA"
                ajuste_pontuacao = -10
        else:
            tendencia = "INSUFICIENTE"
            ajuste_pontuacao = 0

        pontuacao_final = max(0, min(100, pontuacao + ajuste_pontuacao))

        return {
            'fluxo_atual': fluxo_atual,
            'media_historica': media_historica,
            'mediana_historica': mediana_historica,
            'classificacao': classificacao,
            'tendencia_10d': tendencia,
            'pontuacao': pontuacao_final,
            'favoravel_mercado': pontuacao_final >= 50
        }

    def _calcular_confluencia_geral(self, selic: Dict, cambio: Dict, fluxo: Dict) -> float:
        """Calcula pontuação geral de confluência macroeconômica"""
        # Verificar se há erros nas análises
        if 'erro' in selic or 'erro' in cambio or 'erro' in fluxo:
            return 0.0

        # Pesos configuráveis
        peso_selic = self.config['peso_selic']
        peso_cambio = self.config['peso_cambio']
        peso_fluxo = self.config['peso_fluxo']

        # Normalizar pesos
        total_pesos = peso_selic + peso_cambio + peso_fluxo
        peso_selic_norm = peso_selic / total_pesos
        peso_cambio_norm = peso_cambio / total_pesos
        peso_fluxo_norm = peso_fluxo / total_pesos

        # Calcular pontuação ponderada
        pontuacao_selic = selic.get('pontuacao', 50)
        pontuacao_cambio = cambio.get('pontuacao', 50)
        pontuacao_fluxo = fluxo.get('pontuacao', 50)

        confluencia_geral = (
            pontuacao_selic * peso_selic_norm +
            pontuacao_cambio * peso_cambio_norm +
            pontuacao_fluxo * peso_fluxo_norm
        )

        return round(confluencia_geral, 1)

    def _analisar_impacto_mercado(self, selic: Dict, cambio: Dict, fluxo: Dict,
                                 confluencia: float) -> Dict[str, Any]:
        """Analisa impacto da confluência macro no mercado brasileiro"""

        # Verificar se há erros
        if 'erro' in selic or 'erro' in cambio or 'erro' in fluxo:
            return {
                'tendencia_geral': 'ERRO_ANALISE',
                'forca_sinal': 0,
                'impacto_esperado': 'INDEFINIDO'
            }

        # Lógica de impacto no mercado
        # Confluência alta (>70) = ambiente favorável para risco
        # Confluência baixa (<30) = ambiente desfavorável para risco

        if confluencia >= 70:
            tendencia_geral = "ALTAMENTE_FAVORAVEL"
            forca_sinal = 90
            impacto_esperado = "ALTA_PROVAVEL"
        elif confluencia >= 60:
            tendencia_geral = "FAVORAVEL"
            forca_sinal = 70
            impacto_esperado = "ALTA_POSSIVEL"
        elif confluencia >= 40:
            tendencia_geral = "NEUTRO"
            forca_sinal = 50
            impacto_esperado = "LATERAL"
        elif confluencia >= 30:
            tendencia_geral = "DESFAVORAVEL"
            forca_sinal = 30
            impacto_esperado = "BAIXA_POSSIVEL"
        else:
            tendencia_geral = "ALTAMENTE_DESFAVORAVEL"
            forca_sinal = 10
            impacto_esperado = "BAIXA_PROVAVEL"

        # Análise específica por indicador
        analises_individuais = {
            'selic': {
                'impacto': 'POSITIVO' if selic.get('favoravel_mercado', False) else 'NEGATIVO',
                'contribuicao': selic.get('pontuacao', 50) - 50  # Desvio da média
            },
            'cambio': {
                'impacto': 'POSITIVO' if cambio.get('favoravel_mercado', False) else 'NEGATIVO',
                'contribuicao': cambio.get('pontuacao', 50) - 50
            },
            'fluxo_capitais': {
                'impacto': 'POSITIVO' if fluxo.get('favoravel_mercado', False) else 'NEGATIVO',
                'contribuicao': fluxo.get('pontuacao', 50) - 50
            }
        }

        return {
            'tendencia_geral': tendencia_geral,
            'forca_sinal': forca_sinal,
            'impacto_esperado': impacto_esperado,
            'analises_individuais': analises_individuais,
            'confluencia_total': confluencia
        }

    def _calcular_confianca_analise(self, selic: Dict, cambio: Dict, fluxo: Dict) -> float:
        """Calcula confiança geral da análise macro"""

        # Verificar qualidade dos dados
        confianca_dados = 0
        indicadores_validos = 0

        for indicador in [selic, cambio, fluxo]:
            if 'erro' not in indicador:
                indicadores_validos += 1

        if indicadores_validos == 3:
            confianca_dados = 100
        elif indicadores_validos == 2:
            confianca_dados = 70
        elif indicadores_validos == 1:
            confianca_dados = 40
        else:
            confianca_dados = 0

        # Confiança baseada na consistência dos indicadores
        pontuacoes = []
        for indicador in [selic, cambio, fluxo]:
            if 'pontuacao' in indicador:
                pontuacoes.append(indicador['pontuacao'])

        if len(pontuacoes) >= 2:
            # Verificar se há grande divergência entre indicadores
            desvio_padrao = np.std(pontuacoes)
            if desvio_padrao > 30:  # Divergência alta
                confianca_consistencia = 60
            elif desvio_padrao > 20:  # Divergência moderada
                confianca_consistencia = 80
            else:  # Boa consistência
                confianca_consistencia = 100
        else:
            confianca_consistencia = 50

        # Média ponderada
        confianca_final = (confianca_dados * 0.6) + (confianca_consistencia * 0.4)

        return round(confianca_final, 1)


# Função de teste do módulo
def testar_modulo_macro_confluence():
    """Função para testar o módulo com dados de exemplo"""
    print("Testando Módulo Macro Confluence")
    print("=" * 50)

    # Criar dados macroeconômicos simulados
    np.random.seed(42)

    # Dados Selic (últimos 60 dias)
    selic_base = 10.75  # Selic atual aproximada
    selic_dados = []
    for i in range(60):
        # Selic com tendência de queda gradual
        tendencia = -0.01 * i  # Queda de 0.01% por dia
        volatilidade = np.random.normal(0, 0.02)
        selic = selic_base + tendencia + volatilidade
        selic_dados.append(max(2.0, selic))  # Selic não pode ser negativa

    # Dados câmbio USD/BRL (últimos 60 dias)
    cambio_base = 5.20  # Câmbio aproximado
    cambio_dados = []
    for i in range(60):
        # Câmbio com apreciação gradual (dólar ficando mais barato)
        tendencia = -0.005 * i
        volatilidade = np.random.normal(0, 0.03)
        cambio = cambio_base + tendencia + volatilidade
        cambio_dados.append(max(3.0, cambio))

    # Dados fluxo de capitais (últimos 60 dias, em milhões USD)
    fluxo_base = 500  # Fluxo positivo base
    fluxo_dados = []
    for i in range(60):
        # Fluxo com tendência positiva
        tendencia = 2 * i  # Entrada crescente
        volatilidade = np.random.normal(0, 50)
        fluxo = fluxo_base + tendencia + volatilidade
        fluxo_dados.append(fluxo)

    dados_macroeconomicos = {
        'selic': selic_dados,
        'cambio': cambio_dados,
        'fluxo_capitais': fluxo_dados
    }

    # Inicializar módulo
    config = {
        'ativos_principais': ['WIN'],
        'janela_analise_dias': 90,
        'indicadores_macro': ['SELIC', 'CAMBIO', 'FLUXO_CAPITAIS'],
        'peso_selic': 0.3,
        'peso_cambio': 0.3,
        'peso_fluxo': 0.4
    }

    modulo = ModuloMacroConfluence(config)

    # Executar análise
    resultado = modulo.analisar(dados_macroeconomicos)

    print(f"Status: {resultado.status}")
    print(f"Confiança: {resultado.confianca:.1f}%")

    if 'tempo_processamento' in resultado.metadados:
        print(f"Tempo processamento: {resultado.metadados['tempo_processamento']:.2f}s")
    else:
        print("Tempo processamento: N/A")

    if resultado.status == 'SUCCESS':
        dados = resultado.dados_analisados

        print(f"Pontuação Confluência Geral: {dados['pontuacao_confluencia']:.1f}%")
        print(f"Tendência Macro: {dados['impacto_mercado']['tendencia_geral']}")
        print(f"Força do Sinal: {dados['impacto_mercado']['forca_sinal']}%")
        print(f"Impacto Esperado: {dados['impacto_mercado']['impacto_esperado']}")

        # Detalhes por indicador
        print("\n--- ANÁLISE POR INDICADOR ---")
        print(f"Selic: {dados['analise_selic']['selic_atual']:.2f}% - {dados['analise_selic']['classificacao']} (Pontuação: {dados['analise_selic']['pontuacao']})")
        print(f"Câmbio: R$ {dados['analise_cambio']['cambio_atual']:.2f} - {dados['analise_cambio']['classificacao']} (Pontuação: {dados['analise_cambio']['pontuacao']})")
        print(f"Fluxo: ${dados['analise_fluxo']['fluxo_atual']:,.0f}M - {dados['analise_fluxo']['classificacao']} (Pontuação: {dados['analise_fluxo']['pontuacao']})")

    print("\nTeste concluído!")


if __name__ == "__main__":
    testar_modulo_macro_confluence()