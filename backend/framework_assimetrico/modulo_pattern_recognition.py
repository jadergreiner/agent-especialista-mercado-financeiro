# Módulo Pattern Recognition
# Etapa 1 do Framework Assimétrico
# Responsável por identificar padrões técnicos nos dados de mercado

"""
MÓDULO PATTERN RECOGNITION

Este módulo implementa a primeira etapa do framework de detecção assimétrica:
identificação de padrões técnicos através de indicadores como RSI, médias móveis
e momentum.

Indicadores analisados:
- RSI (Relative Strength Index)
- SMA (Simple Moving Average) 20 e 50 períodos
- Momentum 10 períodos

Objetivos:
- Identificar condições técnicas favoráveis
- Calcular indicadores com validação
- Detectar setups técnicos básicos
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Imports para execução direta (quando não usado como módulo)
try:
    from .interfaces import (
        ModuloPatternRecognitionInterface,
        ResultadoModulo,
        CONFIG_PADRAO_PATTERN_RECOGNITION
    )
except ImportError:
    # Para execução direta do arquivo
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

    from interfaces import (
        ModuloPatternRecognitionInterface,
        ResultadoModulo,
        CONFIG_PADRAO_PATTERN_RECOGNITION
    )

logger = logging.getLogger(__name__)


class ModuloPatternRecognition(ModuloPatternRecognitionInterface):
    """
    Módulo responsável por reconhecimento de padrões técnicos.
    Implementa análise de RSI, médias móveis e momentum.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Inicializa o módulo Pattern Recognition.

        Args:
            config: Configuração específica do módulo
        """
        config_completo = {**CONFIG_PADRAO_PATTERN_RECOGNITION, **(config or {})}
        super().__init__(config_completo)

        logger.info("Módulo Pattern Recognition inicializado")
        logger.info(f"Indicadores: {self.config['indicadores']}")

    def _validar_configuracao_especifica(self):
        """Validação específica do módulo Pattern Recognition"""
        required_indicators = ['RSI', 'SMA_20', 'SMA_50', 'MOMENTUM']
        configured_indicators = self.config.get('indicadores', [])

        for indicator in required_indicators:
            if indicator not in configured_indicators:
                raise ValueError(f"Indicador obrigatório não configurado: {indicator}")

        # Validar parâmetros dos indicadores
        if not (5 <= self.config.get('rsi_periodo', 14) <= 30):
            raise ValueError("Período RSI deve estar entre 5 e 30")

        if not (10 <= self.config.get('momentum_periodo', 10) <= 50):
            raise ValueError("Período momentum deve estar entre 10 e 50")

    def analisar(self, dados: Dict[str, pd.DataFrame]) -> ResultadoModulo:
        """
        Executa análise completa de padrões técnicos.

        Args:
            dados: Dict com dados OHLCV por ativo

        Returns:
            ResultadoModulo: Resultado da análise
        """
        inicio = datetime.now()

        try:
            logger.info("Iniciando análise de padrões técnicos")
            logger.info(f"Ativos analisados: {list(dados.keys())}")

            resultados_ativos = {}
            setups_identificados = []

            for ativo, df_ohlcv in dados.items():
                logger.info(f"Analisando padrões para {ativo}")

                # Calcular indicadores técnicos
                indicadores = self.calcular_indicadores(df_ohlcv)

                # Identificar setups técnicos
                setups_ativo = self.identificar_setups(indicadores)

                # Analisar padrões específicos
                analise_padroes = self.analisar_padroes_tecnicos(df_ohlcv)

                resultados_ativos[ativo] = {
                    'indicadores': indicadores,
                    'setups': setups_ativo,
                    'analise_padroes': analise_padroes,
                    'pontos_dados': len(df_ohlcv)
                }

                setups_identificados.extend([
                    {**setup, 'ativo': ativo} for setup in setups_ativo
                ])

            # Calcular confiança geral
            confianca = self._calcular_confianca_analise(resultados_ativos)

            # Métricas da análise
            metricas = {
                'ativos_analisados': len(resultados_ativos),
                'total_setups': len(setups_identificados),
                'indicadores_calculados': self.config['indicadores'],
                'periodo_analisado_dias': self.config['janela_analise_dias']
            }

            resultado = ResultadoModulo(
                timestamp=datetime.now(),
                status='SUCCESS',
                dados_analisados=resultados_ativos,
                metricas=metricas,
                confianca=confianca,
                metadados={
                    'tempo_processamento': (datetime.now() - inicio).total_seconds(),
                    'setups_por_ativo': {
                        ativo: len(dados['setups'])
                        for ativo, dados in resultados_ativos.items()
                    }
                }
            )

            logger.info(f"Análise Pattern Recognition concluída: {len(setups_identificados)} setups identificados")
            return resultado

        except Exception as e:
            logger.error(f"Erro na análise Pattern Recognition: {e}")
            return ResultadoModulo(
                timestamp=datetime.now(),
                status='ERROR',
                dados_analisados={},
                metricas={},
                confianca=0.0,
                metadados={'erro': str(e)}
            )

    def calcular_indicadores(self, dados_ohlcv: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula indicadores técnicos no dataframe OHLCV.

        Args:
            dados_ohlcv: DataFrame com colunas OHLCV

        Returns:
            DataFrame com indicadores calculados
        """
        df = dados_ohlcv.copy()

        # RSI (Relative Strength Index)
        if 'RSI' in self.config['indicadores']:
            df['RSI'] = self._calcular_rsi(df['Close'], self.config['rsi_periodo'])

        # Simple Moving Averages
        if 'SMA_20' in self.config['indicadores']:
            df['SMA_20'] = df['Close'].rolling(window=20).mean()

        if 'SMA_50' in self.config['indicadores']:
            df['SMA_50'] = df['Close'].rolling(window=50).mean()

        # Momentum
        if 'MOMENTUM' in self.config['indicadores']:
            df['MOMENTUM'] = self._calcular_momentum(df['Close'], self.config['momentum_periodo'])

        # Remover NaN resultantes dos cálculos
        df = df.dropna()

        return df

    def _calcular_rsi(self, precos: pd.Series, periodo: int = 14) -> pd.Series:
        """
        Calcula RSI (Relative Strength Index).

        Args:
            precos: Série de preços de fechamento
            periodo: Período para cálculo do RSI

        Returns:
            Série com valores de RSI
        """
        delta = precos.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=periodo).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=periodo).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    def _calcular_momentum(self, precos: pd.Series, periodo: int = 10) -> pd.Series:
        """
        Calcula momentum (variação percentual).

        Args:
            precos: Série de preços
            periodo: Período para cálculo do momentum

        Returns:
            Série com valores de momentum
        """
        return ((precos - precos.shift(periodo)) / precos.shift(periodo)) * 100

    def identificar_setups(self, indicadores: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Identifica setups técnicos baseados nos indicadores calculados.

        Args:
            indicadores: DataFrame com indicadores calculados

        Returns:
            Lista de setups identificados
        """
        setups = []

        if len(indicadores) < 50:  # Mínimo de dados para análise
            return setups

        # Setup 1: RSI Oversold + Momentum positivo
        if 'RSI' in indicadores.columns and 'MOMENTUM' in indicadores.columns:
            condicao_rsi = indicadores['RSI'] < self.config['rsi_oversold']
            condicao_momentum = indicadores['MOMENTUM'] > 0

            setups_rsi = indicadores[condicao_rsi & condicao_momentum]

            for idx, row in setups_rsi.iterrows():
                setups.append({
                    'tipo': 'RSI_OVERSOLD_MOMENTUM_UP',
                    'timestamp': idx,
                    'direcao': 'LONG',
                    'forca': (self.config['rsi_oversold'] - row['RSI']) / self.config['rsi_oversold'],
                    'indicadores': {
                        'rsi': row['RSI'],
                        'momentum': row['MOMENTUM']
                    }
                })

        # Setup 2: RSI Overbought + Momentum negativo
        if 'RSI' in indicadores.columns and 'MOMENTUM' in indicadores.columns:
            condicao_rsi = indicadores['RSI'] > self.config['rsi_overbought']
            condicao_momentum = indicadores['MOMENTUM'] < 0

            setups_rsi = indicadores[condicao_rsi & condicao_momentum]

            for idx, row in setups_rsi.iterrows():
                setups.append({
                    'tipo': 'RSI_OVERBOUGHT_MOMENTUM_DOWN',
                    'timestamp': idx,
                    'direcao': 'SHORT',
                    'forca': (row['RSI'] - self.config['rsi_overbought']) / (100 - self.config['rsi_overbought']),
                    'indicadores': {
                        'rsi': row['RSI'],
                        'momentum': row['MOMENTUM']
                    }
                })

        # Setup 3: Cruzamento de médias (Golden Cross)
        if 'SMA_20' in indicadores.columns and 'SMA_50' in indicadores.columns:
            sma_20_prev = indicadores['SMA_20'].shift(1)
            sma_50_prev = indicadores['SMA_50'].shift(1)

            # Golden Cross: SMA_20 cruza acima da SMA_50
            golden_cross = (indicadores['SMA_20'] > indicadores['SMA_50']) & \
                          (sma_20_prev <= sma_50_prev)

            setups_golden = indicadores[golden_cross]

            for idx, row in setups_golden.iterrows():
                setups.append({
                    'tipo': 'GOLDEN_CROSS',
                    'timestamp': idx,
                    'direcao': 'LONG',
                    'forca': 0.8,  # Força alta para cross de médias
                    'indicadores': {
                        'sma_20': row['SMA_20'],
                        'sma_50': row['SMA_50'],
                        'diferenca': row['SMA_20'] - row['SMA_50']
                    }
                })

        # Setup 4: Death Cross (cruzamento bearish)
        if 'SMA_20' in indicadores.columns and 'SMA_50' in indicadores.columns:
            # Death Cross: SMA_20 cruza abaixo da SMA_50
            death_cross = (indicadores['SMA_20'] < indicadores['SMA_50']) & \
                         (sma_20_prev >= sma_50_prev)

            setups_death = indicadores[death_cross]

            for idx, row in setups_death.iterrows():
                setups.append({
                    'tipo': 'DEATH_CROSS',
                    'timestamp': idx,
                    'direcao': 'SHORT',
                    'forca': 0.8,  # Força alta para cross de médias
                    'indicadores': {
                        'sma_20': row['SMA_20'],
                        'sma_50': row['SMA_50'],
                        'diferenca': abs(row['SMA_20'] - row['SMA_50'])
                    }
                })

        logger.info(f"Setups identificados: {len(setups)}")
        return setups

    def analisar_padroes_tecnicos(self, dados_ohlcv: pd.DataFrame) -> Dict[str, Any]:
        """
        Analisa padrões técnicos específicos no dados.

        Args:
            dados_ohlcv: DataFrame com dados OHLCV

        Returns:
            Dict com análise de padrões
        """
        analise = {
            'tendencia_geral': self._analisar_tendencia(dados_ohlcv),
            'volatilidade': self._analisar_volatilidade(dados_ohlcv),
            'forca_momentum': self._analisar_forca_momentum(dados_ohlcv),
            'nivel_suporte_resistencia': self._identificar_suporte_resistencia(dados_ohlcv)
        }

        return analise

    def _analisar_tendencia(self, dados: pd.DataFrame) -> str:
        """Analisa tendência geral do ativo"""
        if len(dados) < 20:
            return "INSUFICIENTE_DADOS"

        preco_atual = dados['Close'].iloc[-1]
        preco_20_periodos = dados['Close'].iloc[-20]

        variacao = (preco_atual - preco_20_periodos) / preco_20_periodos

        if variacao > 0.05:  # +5%
            return "ALTA_FORTE"
        elif variacao > 0.02:  # +2%
            return "ALTA_MODERADA"
        elif variacao < -0.05:  # -5%
            return "BAIXA_FORTE"
        elif variacao < -0.02:  # -2%
            return "BAIXA_MODERADA"
        else:
            return "LATERAL"

    def _analisar_volatilidade(self, dados: pd.DataFrame) -> Dict[str, Any]:
        """Analisa volatilidade do ativo"""
        retornos = dados['Close'].pct_change().dropna()

        volatilidade_diaria = retornos.std()
        volatilidade_anualizada = volatilidade_diaria * np.sqrt(252)  # Dias úteis

        # Classificar volatilidade
        if volatilidade_anualizada > 0.40:  # >40% aa
            classificacao = "MUITO_ALTA"
        elif volatilidade_anualizada > 0.30:  # >30% aa
            classificacao = "ALTA"
        elif volatilidade_anualizada > 0.20:  # >20% aa
            classificacao = "MODERADA"
        elif volatilidade_anualizada > 0.10:  # >10% aa
            classificacao = "BAIXA"
        else:
            classificacao = "MUITO_BAIXA"

        return {
            'volatilidade_diaria': volatilidade_diaria,
            'volatilidade_anualizada': volatilidade_anualizada,
            'classificacao': classificacao,
            'range_tipico': dados['High'].iloc[-20:].max() - dados['Low'].iloc[-20:].min()
        }

    def _analisar_forca_momentum(self, dados: pd.DataFrame) -> float:
        """Analisa força do momentum atual"""
        if len(dados) < 20:
            return 0.0

        # Calcular momentum composto
        momentum_curto = self._calcular_momentum(dados['Close'], 5).iloc[-1]
        momentum_medio = self._calcular_momentum(dados['Close'], 20).iloc[-1]

        # Ponderação: 60% curto prazo, 40% médio prazo
        forca_momentum = (momentum_curto * 0.6) + (momentum_medio * 0.4)

        # Normalizar para escala 0-100
        forca_normalizada = max(0, min(100, 50 + (forca_momentum * 10)))

        return forca_normalizada

    def _identificar_suporte_resistencia(self, dados: pd.DataFrame,
                                       janela: int = 20) -> Dict[str, Any]:
        """Identifica níveis de suporte e resistência"""
        if len(dados) < janela:
            return {'suporte': None, 'resistencia': None}

        recentes = dados.tail(janela)

        suporte = recentes['Low'].min()
        resistencia = recentes['High'].max()

        return {
            'suporte': suporte,
            'resistencia': resistencia,
            'distancia_suporte': (dados['Close'].iloc[-1] - suporte) / dados['Close'].iloc[-1],
            'distancia_resistencia': (resistencia - dados['Close'].iloc[-1]) / dados['Close'].iloc[-1]
        }

    def _calcular_confianca_analise(self, resultados_ativos: Dict[str, Any]) -> float:
        """Calcula confiança geral da análise"""
        if not resultados_ativos:
            return 0.0

        confiancas = []

        for ativo, dados in resultados_ativos.items():
            # Confiança baseada na quantidade de dados
            confianca_dados = min(100, len(dados.get('indicadores', [])) * 2)

            # Confiança baseada na qualidade dos indicadores
            indicadores = dados.get('indicadores', pd.DataFrame())
            if not indicadores.empty:
                # Verificar se indicadores estão bem calculados (não NaN)
                indicadores_validos = indicadores.dropna().shape[0]
                confianca_indicadores = (indicadores_validos / len(indicadores)) * 100
            else:
                confianca_indicadores = 0

            # Confiança baseada em setups identificados
            num_setups = len(dados.get('setups', []))
            confianca_setups = min(100, num_setups * 10)  # Até 10 setups = 100% confiança

            # Média ponderada
            confianca_ativo = (confianca_dados * 0.3) + \
                            (confianca_indicadores * 0.4) + \
                            (confianca_setups * 0.3)

            confiancas.append(confianca_ativo)

        return sum(confiancas) / len(confiancas) if confiancas else 0.0


# Função de teste do módulo
def testar_modulo_pattern_recognition():
    """Função para testar o módulo com dados de exemplo"""
    print("Testando Módulo Pattern Recognition")
    print("=" * 50)

    # Criar dados de exemplo
    datas = pd.date_range('2024-01-01', periods=100, freq='D')
    np.random.seed(42)

    # Simular preços OHLCV
    preco_base = 100
    precos = []
    for i in range(100):
        variacao = np.random.normal(0, 0.02)  # 2% volatilidade diária
        preco_base *= (1 + variacao)
        precos.append(preco_base)

    dados_exemplo = pd.DataFrame({
        'Open': precos,
        'High': [p * (1 + abs(np.random.normal(0, 0.01))) for p in precos],
        'Low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in precos],
        'Close': precos,
        'Volume': [1000000 + np.random.normal(0, 100000) for _ in range(100)]
    }, index=datas)

    # Inicializar módulo
    config_teste = {
        'ativos_principais': ['WIN'],
        'janela_analise_dias': 90,
        'indicadores': ['RSI', 'SMA_20', 'SMA_50', 'MOMENTUM'],
        'rsi_periodo': 14,
        'rsi_oversold': 30,
        'rsi_overbought': 70,
        'momentum_periodo': 10
    }
    modulo = ModuloPatternRecognition(config_teste)

    # Executar análise
    resultado = modulo.analisar({'WIN': dados_exemplo})

    print(f"Status: {resultado.status}")
    print(f"Confiança: {resultado.confianca:.1f}%")
    print(f"Tempo processamento: {resultado.metadados['tempo_processamento']:.2f}s")

    if resultado.status == 'SUCCESS':
        dados_win = resultado.dados_analisados['WIN']
        print(f"Setups identificados: {len(dados_win['setups'])}")
        print(f"Pontos de dados analisados: {dados_win['pontos_dados']}")

        # Mostrar primeiros setups
        for i, setup in enumerate(dados_win['setups'][:3]):
            print(f"Setup {i+1}: {setup['tipo']} - {setup['direcao']} (Força: {setup['forca']:.2f})")

    print("\nTeste concluído!")


if __name__ == "__main__":
    testar_modulo_pattern_recognition()