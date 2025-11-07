# Interfaces e Classes Base para o Framework Assimétrico
# Define contratos e estruturas comuns para todos os módulos

"""
INTERFACES DO FRAMEWORK ASSIMÉTRICO

Este módulo define as interfaces e classes base que todos os módulos
do framework devem implementar. Garante consistência e padronização.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Protocol
from dataclasses import dataclass
from datetime import datetime
import pandas as pd


class ModuloFramework(Protocol):
    """Protocolo que todos os módulos devem implementar"""

    def analisar(self, dados: Any) -> Dict[str, Any]:
        """
        Método principal de análise do módulo.

        Args:
            dados: Dados de entrada específicos do módulo

        Returns:
            Dict com resultados da análise
        """
        ...

    def validar_configuracao(self) -> bool:
        """
        Valida se a configuração do módulo é adequada.

        Returns:
            bool: True se configuração válida
        """
        ...

    def obter_metricas(self) -> Dict[str, Any]:
        """
        Retorna métricas de performance do módulo.

        Returns:
            Dict com métricas do módulo
        """
        ...


@dataclass
class ResultadoModulo:
    """Estrutura padrão para resultados de módulos"""
    timestamp: datetime
    status: str  # 'SUCCESS', 'PARTIAL', 'ERROR'
    dados_analisados: Dict[str, Any]
    metricas: Dict[str, Any]
    confianca: float  # 0-100
    metadados: Dict[str, Any]


class ModuloBase(ABC):
    """Classe base abstrata para todos os módulos"""

    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa módulo com configuração.

        Args:
            config: Configuração específica do módulo
        """
        self.config = config
        self.nome = self.__class__.__name__
        self._validar_configuracao_base()

    def _validar_configuracao_base(self):
        """Validação básica de configuração comum a todos os módulos"""
        required_keys = ['ativos_principais', 'janela_analise_dias']
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Configuração obrigatória faltando: {key}")

    @abstractmethod
    def analisar(self, dados: Any) -> ResultadoModulo:
        """Método principal de análise - deve ser implementado por cada módulo"""
        pass

    def validar_configuracao(self) -> bool:
        """Validação específica do módulo"""
        try:
            self._validar_configuracao_especifica()
            return True
        except Exception:
            return False

    @abstractmethod
    def _validar_configuracao_especifica(self):
        """Validação específica de cada módulo"""
        pass

    def obter_metricas(self) -> Dict[str, Any]:
        """Métricas padrão do módulo"""
        return {
            'nome_modulo': self.nome,
            'configuracao_valida': self.validar_configuracao(),
            'timestamp': datetime.now().isoformat()
        }


# Interfaces específicas para cada módulo

class ModuloPatternRecognitionInterface(ModuloBase):
    """Interface para módulo de reconhecimento de padrões"""

    @abstractmethod
    def analisar_padroes_tecnicos(self, dados_ohlcv: pd.DataFrame) -> Dict[str, Any]:
        """Analisa padrões técnicos no dados OHLCV"""
        pass

    @abstractmethod
    def calcular_indicadores(self, dados_ohlcv: pd.DataFrame) -> pd.DataFrame:
        """Calcula indicadores técnicos (RSI, médias, momentum)"""
        pass

    @abstractmethod
    def identificar_setups(self, indicadores: pd.DataFrame) -> List[Dict[str, Any]]:
        """Identifica setups técnicos baseados nos indicadores"""
        pass


class ModuloMacroConfluenceInterface(ModuloBase):
    """Interface para módulo de confluência macroeconômica"""

    @abstractmethod
    def analisar_selic(self, dados_selic: pd.Series) -> Dict[str, Any]:
        """Analisa impacto da taxa Selic"""
        pass

    @abstractmethod
    def analisar_cambio(self, dados_cambio: pd.DataFrame) -> Dict[str, Any]:
        """Analisa impacto do câmbio"""
        pass

    @abstractmethod
    def analisar_fluxo(self, dados_fluxo: pd.DataFrame) -> Dict[str, Any]:
        """Analisa fluxo cambial"""
        pass

    @abstractmethod
    def calcular_confluencia_macro(self, analises: Dict[str, Any]) -> float:
        """Calcula grau de confluência macroeconômica"""
        pass


class ModuloCorrelationAnalysisInterface(ModuloBase):
    """Interface para módulo de análise de correlação"""

    @abstractmethod
    def calcular_correlacao_ibov_dolar(self, dados_ibov: pd.DataFrame,
                                     dados_dolar: pd.DataFrame) -> pd.Series:
        """Calcula correlação rolling Ibovespa vs Dólar"""
        pass

    @abstractmethod
    def analisar_commodities(self, dados_commodities: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Analisa impacto de commodities no mercado"""
        pass

    @abstractmethod
    def detectar_regime_correlacao(self, correlacoes: pd.DataFrame) -> str:
        """Detecta regime atual de correlação (alta, baixa, neutra)"""
        pass


class ModuloEventMappingInterface(ModuloBase):
    """Interface para módulo de mapeamento de eventos"""

    @abstractmethod
    def carregar_calendario_eventos(self) -> pd.DataFrame:
        """Carrega calendário de eventos econômicos"""
        pass

    @abstractmethod
    def pontuar_risco_evento(self, evento: Dict[str, Any]) -> float:
        """Atribui pontuação de risco a um evento (0-100)"""
        pass

    @abstractmethod
    def analisar_impacto_historico(self, evento: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa impacto histórico do evento no mercado"""
        pass

    @abstractmethod
    def prever_volatilidade(self, eventos_proximos: List[Dict[str, Any]]) -> float:
        """Prevê volatilidade esperada baseada em eventos próximos"""
        pass


class ModuloRiskRewardInterface(ModuloBase):
    """Interface para módulo de cálculo risco-recompensa"""

    @abstractmethod
    def calcular_risk_reward_ratio(self, setup: Dict[str, Any]) -> float:
        """Calcula ratio risco-recompensa para um setup"""
        pass

    @abstractmethod
    def pontuar_assimetria(self, componentes: Dict[str, Any]) -> float:
        """Calcula pontuação de assimetria (0-100) baseada em todos os componentes"""
        pass

    @abstractmethod
    def validar_probabilidade_historica(self, setup: Dict[str, Any]) -> float:
        """Valida probabilidade histórica de sucesso do setup"""
        pass


class ModuloTimingOptimizationInterface(ModuloBase):
    """Interface para módulo de otimização de timing"""

    @abstractmethod
    def identificar_janelas_otimas(self, setup: Dict[str, Any]) -> List[datetime]:
        """Identifica janelas ótimas de entrada/saída"""
        pass

    @abstractmethod
    def calcular_momentum_intraday(self, dados_intraday: pd.DataFrame) -> pd.Series:
        """Calcula momentum intraday para timing preciso"""
        pass

    @abstractmethod
    def otimizar_liquidez(self, setup: Dict[str, Any]) -> Dict[str, Any]:
        """Otimiza timing baseado em liquidez e slippage"""
        pass


# Funções utilitárias comuns

def validar_dados_mercado(dados: Dict[str, pd.DataFrame]) -> bool:
    """
    Valida se os dados de mercado têm formato adequado.

    Args:
        dados: Dict com dados OHLCV por ativo

    Returns:
        bool: True se dados válidos
    """
    required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']

    for ativo, df in dados.items():
        if not isinstance(df, pd.DataFrame):
            return False

        if not all(col in df.columns for col in required_columns):
            return False

        if df.empty:
            return False

    return True


def calcular_confianca_analise(resultados_modulos: Dict[str, ResultadoModulo]) -> float:
    """
    Calcula confiança geral da análise baseada nos resultados dos módulos.

    Args:
        resultados_modulos: Resultados de todos os módulos

    Returns:
        float: Confiança geral (0-100)
    """
    if not resultados_modulos:
        return 0.0

    confiancas = [resultado.confianca for resultado in resultados_modulos.values()
                 if hasattr(resultado, 'confianca')]

    if not confiancas:
        return 50.0  # Confiança neutra se não há dados

    return sum(confiancas) / len(confiancas)


def log_resultado_modulo(modulo_nome: str, resultado: ResultadoModulo):
    """
    Log padronizado para resultados de módulos.

    Args:
        modulo_nome: Nome do módulo
        resultado: Resultado da análise
    """
    import logging
    logger = logging.getLogger(__name__)

    logger.info(f"Módulo {modulo_nome}: {resultado.status}")
    logger.info(f"  Confiança: {resultado.confianca:.1f}%")
    logger.info(f"  Timestamp: {resultado.timestamp}")
    logger.info(f"  Métricas: {resultado.metricas}")


# Configurações padrão para cada módulo

CONFIG_PADRAO_PATTERN_RECOGNITION = {
    'indicadores': ['RSI', 'SMA_20', 'SMA_50', 'MOMENTUM'],
    'rsi_periodo': 14,
    'rsi_overbought': 70,
    'rsi_oversold': 30,
    'momentum_periodo': 10
}

CONFIG_PADRAO_MACRO_CONFLUENCE = {
    'peso_selic': 0.4,
    'peso_cambio': 0.4,
    'peso_fluxo': 0.2,
    'janela_analise_meses': 6,
    'indicadores_macro': ['SELIC', 'CAMBIO', 'FLUXO_CAPITAIS']
}

CONFIG_PADRAO_CORRELATION_ANALYSIS = {
    'janela_correlacao_dias': 30,
    'commodities_analisadas': ['PETR4', 'VALE3', 'SOJA', 'MINERIO'],
    'threshold_correlacao_alta': 0.7
}

CONFIG_PADRAO_EVENT_MAPPING = {
    'fonte_calendario': 'BCB',
    'paises_analisados': ['BR', 'US', 'EU'],
    'janela_impacto_dias': 3,
    'peso_evento_critico': 90
}

CONFIG_PADRAO_RISK_REWARD = {
    'stop_loss_padrao': 0.02,  # 2%
    'target_profit_minimo': 0.04,  # 4%
    'peso_probabilidade': 0.5,
    'peso_risk_reward': 0.3,
    'peso_confluencia': 0.2
}

CONFIG_PADRAO_TIMING_OPTIMIZATION = {
    'janelas_analise_horas': [9, 10, 11, 14, 15, 16],  # Horas do pregão
    'min_liquidez_volume': 1000000,  # Volume mínimo
    'max_slippage_permitido': 0.005  # 0.5%
}