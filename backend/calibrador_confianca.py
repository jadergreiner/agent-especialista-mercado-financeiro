"""
Sistema de Calibração Automática de Confiança

Implementa algoritmo inteligente para ajustar confiança dos cenários baseado em:
- Divergências entre análise técnica e fundamental
- Qualidade e frescor dos dados
- Volatilidade do mercado
- Consistência dos sinais

Reduz confiança inflada e fornece recomendações mais realistas.
"""

import logging
from typing import Dict, Optional, Any, Tuple
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CalibradorConfianca:
    """
    Calibrador automático de confiança para cenários de análise.
    """

    def __init__(self):
        """Inicializa o calibrador com parâmetros padrão."""
        # Pesos para diferentes fatores de calibração
        self.pesos = {
            'divergencia_tecnico_fundamental': 0.4,
            'qualidade_dados': 0.3,
            'volatilidade': 0.2,
            'consistencia_sinais': 0.1
        }

        # Limites de confiança
        self.limites = {
            'max_confianca': 85,
            'min_confianca': 15,
            'confianca_base_bull': 50,
            'confianca_base_bear': 50
        }

        logger.info("Calibrador de confiança inicializado")

    def calibrar_confianca(
        self,
        dados_preco: Dict,
        dados_indicadores: Optional[Dict],
        dados_noticias: Optional[Dict]
    ) -> Dict[str, Any]:
        """
        Calcula confiança calibrada para cenários Bull e Bear.

        Args:
            dados_preco: Dados de preço atuais
            dados_indicadores: Indicadores técnicos (SMA, RSI)
            dados_noticias: Dados de notícias e sentimento

        Returns:
            dict: Confiança calibrada com justificativas
        """
        logger.info("Iniciando calibração de confiança")

        # Confianças base (ponto de partida neutro)
        confianca_bull = self.limites['confianca_base_bull']
        confianca_bear = self.limites['confianca_base_bear']

        # Fatores de ajuste
        ajustes = {
            'divergencia': self._calcular_divergencia_tecnico_fundamental(dados_indicadores, dados_noticias),
            'qualidade': self._calcular_qualidade_dados(dados_preco, dados_indicadores, dados_noticias),
            'volatilidade': self._calcular_ajuste_volatilidade(dados_preco),
            'consistencia': self._calcular_consistencia_sinais(dados_indicadores, dados_noticias)
        }

        # Aplicar ajustes ponderados
        ajuste_total_bull = 0
        ajuste_total_bear = 0

        for fator, (ajuste_bull, ajuste_bear) in ajustes.items():
            # Mapear nomes dos fatores para chaves dos pesos
            chave_peso = {
                'divergencia': 'divergencia_tecnico_fundamental',
                'qualidade': 'qualidade_dados',
                'volatilidade': 'volatilidade',
                'consistencia': 'consistencia_sinais'
            }.get(fator, fator)

            peso = self.pesos[chave_peso]
            ajuste_total_bull += ajuste_bull * peso
            ajuste_total_bear += ajuste_bear * peso

            logger.debug(f"Fator {fator}: Bull {ajuste_bull:+.1f}, Bear {ajuste_bear:+.1f} (peso {peso})")

        # Aplicar ajustes às confianças base
        confianca_bull = max(self.limites['min_confianca'],
                           min(self.limites['max_confianca'],
                               confianca_bull + ajuste_total_bull))

        confianca_bear = max(self.limites['min_confianca'],
                           min(self.limites['max_confianca'],
                               confianca_bear + ajuste_total_bear))

        # Normalizar para soma = 100%
        total = confianca_bull + confianca_bear
        if total > 0:
            confianca_bull = round((confianca_bull / total) * 100, 1)
            confianca_bear = round((confianca_bear / total) * 100, 1)

        resultado = {
            'confianca_bull': confianca_bull,
            'confianca_bear': confianca_bear,
            'ajustes_aplicados': ajustes,
            'justificativas': self._gerar_justificativas(ajustes),
            'nivel_risco': self._determinar_nivel_risco(confianca_bull, confianca_bear)
        }

        logger.info(f"Confiança calibrada: Bull {confianca_bull}%, Bear {confianca_bear}%")
        return resultado

    def _calcular_divergencia_tecnico_fundamental(
        self,
        dados_indicadores: Optional[Dict],
        dados_noticias: Optional[Dict]
    ) -> Tuple[float, float]:
        """
        Calcula ajustes baseados em divergências entre técnico e fundamental.

        Returns:
            tuple: (ajuste_bull, ajuste_bear) em pontos percentuais
        """
        ajuste_bull = 0
        ajuste_bear = 0

        # Análise técnica
        sinal_tecnico = "NEUTRO"
        if dados_indicadores and 'indicadores' in dados_indicadores:
            sma_sinal = dados_indicadores['indicadores']['sma']['sinal']
            rsi_sinal = dados_indicadores['indicadores']['rsi']['sinal']

            # Lógica de combinação SMA + RSI
            if sma_sinal == 'ACIMA_SMA' and rsi_sinal in ['NEUTRO', 'ALTISTA']:
                sinal_tecnico = "ALTISTA"
            elif sma_sinal == 'ABAIXO_SMA' and rsi_sinal in ['NEUTRO', 'BAIXISTA']:
                sinal_tecnico = "BAIXISTA"
            elif rsi_sinal == 'SOBREVENDIDO':
                sinal_tecnico = "ALTISTA"  # Possível reversão
            elif rsi_sinal == 'SOBRECOMPRADO':
                sinal_tecnico = "BAIXISTA"  # Possível reversão

        # Análise fundamental (notícias)
        sinal_fundamental = "NEUTRO"
        if dados_noticias and 'resumo_geral' in dados_noticias:
            sentimento = dados_noticias['resumo_geral'].get('sentimento_geral', 'NEUTRO')
            impacto = dados_noticias['resumo_geral'].get('impacto_geral', 'MÉDIO')

            if sentimento == 'POSITIVO' and impacto == 'ALTO':
                sinal_fundamental = "ALTISTA"
            elif sentimento == 'NEGATIVO' and impacto == 'ALTO':
                sinal_fundamental = "BAIXISTA"

        # Detectar divergências
        if sinal_tecnico == "ALTISTA" and sinal_fundamental == "BAIXISTA":
            # Divergência: técnico bullish, fundamental bearish
            ajuste_bull -= 15  # Reduz confiança bull
            ajuste_bear += 10  # Aumenta confiança bear
            logger.debug("Divergência detectada: Técnico ALTISTA vs Fundamental BAIXISTA")

        elif sinal_tecnico == "BAIXISTA" and sinal_fundamental == "ALTISTA":
            # Divergência: técnico bearish, fundamental bullish
            ajuste_bull += 10  # Aumenta confiança bull
            ajuste_bear -= 15  # Reduz confiança bear
            logger.debug("Divergência detectada: Técnico BAIXISTA vs Fundamental ALTISTA")

        elif sinal_tecnico == sinal_fundamental and sinal_tecnico != "NEUTRO":
            # Confirmação: sinais alinhados
            if sinal_tecnico == "ALTISTA":
                ajuste_bull += 8
                ajuste_bear -= 5
            else:  # BAIXISTA
                ajuste_bull -= 5
                ajuste_bear += 8
            logger.debug(f"Confirmação detectada: Sinais {sinal_tecnico} alinhados")

        return ajuste_bull, ajuste_bear

    def _calcular_qualidade_dados(
        self,
        dados_preco: Dict,
        dados_indicadores: Optional[Dict],
        dados_noticias: Optional[Dict]
    ) -> Tuple[float, float]:
        """
        Calcula ajustes baseados na qualidade e frescor dos dados.

        Returns:
            tuple: (ajuste_bull, ajuste_bear) em pontos percentuais
        """
        ajuste_bull = 0
        ajuste_bear = 0

        # Verificar frescor dos dados de preço
        frescor_preco = dados_preco.get('frescor', 'desconhecido')
        if frescor_preco == 'atual':
            ajuste_bull += 2
            ajuste_bear += 2
        elif frescor_preco == 'atrasado':
            ajuste_bull -= 3
            ajuste_bear -= 3

        # Verificar disponibilidade de indicadores
        if not dados_indicadores:
            ajuste_bull -= 5
            ajuste_bear -= 5
            logger.debug("Indicadores técnicos não disponíveis - reduzindo confiança")
        else:
            # Verificar se indicadores são recentes
            timestamp_indicadores = dados_indicadores.get('timestamp')
            if timestamp_indicadores:
                try:
                    dt_indicadores = datetime.fromisoformat(timestamp_indicadores.replace('Z', '+00:00'))
                    idade_dados = datetime.now(dt_indicadores.tzinfo) - dt_indicadores
                    if idade_dados > timedelta(hours=1):
                        ajuste_bull -= 2
                        ajuste_bear -= 2
                        logger.debug("Indicadores com mais de 1 hora - reduzindo confiança")
                except:
                    pass

        # Verificar disponibilidade de notícias
        if not dados_noticias or not dados_noticias.get('noticias'):
            ajuste_bull -= 3
            ajuste_bear -= 3
            logger.debug("Notícias não disponíveis - reduzindo confiança")
        else:
            # Verificar se há notícias recentes (últimas 24h)
            noticias_recentes = 0
            for noticia in dados_noticias['noticias'][:5]:  # Top 5 notícias
                try:
                    dt_noticia = datetime.fromisoformat(noticia.get('timestamp', ''))
                    idade_noticia = datetime.now(dt_noticia.tzinfo) - dt_noticia
                    if idade_noticia < timedelta(hours=24):
                        noticias_recentes += 1
                except:
                    continue

            if noticias_recentes == 0:
                ajuste_bull -= 4
                ajuste_bear -= 4
                logger.debug("Nenhuma notícia recente (24h) - reduzindo confiança")

        return ajuste_bull, ajuste_bear

    def _calcular_ajuste_volatilidade(self, dados_preco: Dict) -> Tuple[float, float]:
        """
        Calcula ajustes baseados na volatilidade do mercado.

        Returns:
            tuple: (ajuste_bull, ajuste_bear) em pontos percentuais
        """
        ajuste_bull = 0
        ajuste_bear = 0

        # Estimar volatilidade baseada na variação percentual
        variacao_pct = abs(dados_preco.get('variacao_pct', 0))

        if variacao_pct > 2.0:  # Alta volatilidade
            # Em alta volatilidade, reduzir confiança geral
            ajuste_bull -= 8
            ajuste_bear -= 8
            logger.debug(f"Alta volatilidade detectada ({variacao_pct:.2f}%) - reduzindo confiança geral")

        elif variacao_pct > 1.0:  # Volatilidade média
            ajuste_bull -= 4
            ajuste_bear -= 4
            logger.debug(f"Volatilidade média detectada ({variacao_pct:.2f}%) - reduzindo confiança moderadamente")

        else:  # Baixa volatilidade
            # Em baixa volatilidade, manter confiança
            logger.debug(f"Baixa volatilidade detectada ({variacao_pct:.2f}%) - mantendo confiança")

        return ajuste_bull, ajuste_bear

    def _calcular_consistencia_sinais(
        self,
        dados_indicadores: Optional[Dict],
        dados_noticias: Optional[Dict]
    ) -> Tuple[float, float]:
        """
        Calcula ajustes baseados na consistência dos sinais.

        Returns:
            tuple: (ajuste_bull, ajuste_bear) em pontos percentuais
        """
        ajuste_bull = 0
        ajuste_bear = 0

        sinais = []

        # Coletar sinais de indicadores
        if dados_indicadores and 'indicadores' in dados_indicadores:
            sma_sinal = dados_indicadores['indicadores']['sma']['sinal']
            rsi_sinal = dados_indicadores['indicadores']['rsi']['sinal']

            if sma_sinal == 'ACIMA_SMA':
                sinais.append('BULL')
            elif sma_sinal == 'ABAIXO_SMA':
                sinais.append('BEAR')

            if rsi_sinal == 'ALTISTA':
                sinais.append('BULL')
            elif rsi_sinal == 'BAIXISTA':
                sinais.append('BEAR')

        # Coletar sinais de notícias
        if dados_noticias and 'resumo_geral' in dados_noticias:
            sentimento = dados_noticias['resumo_geral'].get('sentimento_geral')
            impacto = dados_noticias['resumo_geral'].get('impacto_geral')

            if sentimento == 'POSITIVO' and impacto == 'ALTO':
                sinais.append('BULL')
            elif sentimento == 'NEGATIVO' and impacto == 'ALTO':
                sinais.append('BEAR')

        # Calcular consistência
        if sinais:
            bull_sinais = sinais.count('BULL')
            bear_sinais = sinais.count('BEAR')
            total_sinais = len(sinais)

            # Consistência = maior concentração de sinais em uma direção
            consistencia_bull = bull_sinais / total_sinais
            consistencia_bear = bear_sinais / total_sinais

            # Bonus por consistência
            if consistencia_bull > 0.7:  # >70% sinais bullish
                ajuste_bull += 5
                logger.debug(f"Alta consistência bullish ({consistencia_bull:.1%})")

            if consistencia_bear > 0.7:  # >70% sinais bearish
                ajuste_bear += 5
                logger.debug(f"Alta consistência bearish ({consistencia_bear:.1%})")

        return ajuste_bull, ajuste_bear

    def _gerar_justificativas(self, ajustes: Dict) -> str:
        """
        Gera justificativas textuais para os ajustes aplicados.
        """
        justificativas = []

        divergencia = ajustes.get('divergencia', (0, 0))
        if abs(divergencia[0]) > 5 or abs(divergencia[1]) > 5:
            justificativas.append("Divergências entre análise técnica e fundamental detectadas")

        qualidade = ajustes.get('qualidade', (0, 0))
        if qualidade[0] < -5 or qualidade[1] < -5:
            justificativas.append("Qualidade ou frescor dos dados reduzindo confiança")

        volatilidade = ajustes.get('volatilidade', (0, 0))
        if volatilidade[0] < -5 or volatilidade[1] < -5:
            justificativas.append("Alta volatilidade do mercado impactando confiança")

        consistencia = ajustes.get('consistencia', (0, 0))
        if consistencia[0] > 3 or consistencia[1] > 3:
            justificativas.append("Sinais consistentes reforçando confiança")

        if not justificativas:
            justificativas.append("Confiança baseada em dados disponíveis")

        return "; ".join(justificativas)

    def _determinar_nivel_risco(self, confianca_bull: float, confianca_bear: float) -> str:
        """
        Determina o nível de risco baseado nas confianças.
        """
        diff = abs(confianca_bull - confianca_bear)

        if diff < 20:
            return "ALTO"  # Cenários muito equilibrados = alta incerteza
        elif diff < 40:
            return "MÉDIO"  # Moderada diferença
        else:
            return "BAIXO"  # Forte viés direcional