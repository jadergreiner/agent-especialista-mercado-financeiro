#!/usr/bin/env python3
"""
ANALISADOR DE OPORTUNIDADES FOREX
Sistema especializado para análise de pares Forex do portfolio

Funcionalidades:
1. ✅ TAKE PROFIT - Identificação de níveis de saída com lucro
2. ✅ Reforço de Posição - Oportunidades de adicionar posições
3. ✅ HEDGE - Proteção contra riscos através de correlações
4. ✅ Correlação - Análise de relacionamentos entre pares
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging
import warnings

try:
    from .carregador_dados_historicos import CarregadorDadosHistoricos
    from .detector_niveis_criticos_ml import DetectorNiveisCriticosML
except ImportError:
    from carregador_dados_historicos import CarregadorDadosHistoricos
    from detector_niveis_criticos_ml import DetectorNiveisCriticosML

warnings.filterwarnings('ignore')

class AnalisadorOportunidadesForex:
    """Analisador especializado para oportunidades em pares Forex"""

    def __init__(self):
        self.logger = self._configurar_logger()
        self.carregador = CarregadorDadosHistoricos()
        self.detector = DetectorNiveisCriticosML(self.carregador)

        # Pares Forex do portfolio
        self.pares_forex = ['EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'USDCAD=X', 'USDCHF=X']

        # Mapeamento de moedas para análise de correlação
        self.moedas_base = {
            'EURUSD=X': ('EUR', 'USD'),
            'GBPUSD=X': ('GBP', 'USD'),
            'USDJPY=X': ('USD', 'JPY'),
            'USDCAD=X': ('USD', 'CAD'),
            'USDCHF=X': ('USD', 'CHF')
        }

    def _configurar_logger(self) -> logging.Logger:
        logger = logging.getLogger('AnalisadorForex')
        logger.setLevel(logging.INFO)
        return logger

    def analisar_oportunidades_forex(self) -> Dict:
        """
        Analisar oportunidades específicas para pares Forex:
        1. TAKE PROFIT - Níveis de saída com lucro
        2. Reforço de Posição - Entradas adicionais
        3. HEDGE - Proteção via correlações
        4. Correlação - Relacionamentos entre pares
        """

        self.logger.info("🔄 INICIANDO ANÁLISE DE OPORTUNIDADES FOREX")
        timestamp_inicio = datetime.now()

        resultado = {
            'timestamp_analise': timestamp_inicio.isoformat(),
            'pares_analisados': self.pares_forex,
            'oportunidades_take_profit': [],
            'oportunidades_reforco': [],
            'oportunidades_hedge': [],
            'analise_correlacao': {},
            'metricas_gerais': {},
            'status': 'em_andamento'
        }

        try:
            # 1. Análise de TAKE PROFIT
            self.logger.info("💰 ANALISANDO TAKE PROFIT - Níveis de saída")
            resultado['oportunidades_take_profit'] = self._analisar_take_profit()

            # 2. Análise de Reforço de Posição
            self.logger.info("📈 ANALISANDO REFORÇO DE POSIÇÃO")
            resultado['oportunidades_reforco'] = self._analisar_reforco_posicao()

            # 3. Análise de HEDGE
            self.logger.info("🛡️ ANALISANDO OPORTUNIDADES DE HEDGE")
            resultado['oportunidades_hedge'] = self._analisar_hedge()

            # 4. Análise de Correlação
            self.logger.info("📊 ANALISANDO CORRELAÇÕES ENTRE PARES")
            resultado['analise_correlacao'] = self._analisar_correlacoes()

            # 5. Métricas Gerais
            resultado['metricas_gerais'] = self._calcular_metricas_gerais(resultado)

            resultado['status'] = 'concluido_com_sucesso'
            self.logger.info("✅ ANÁLISE FOREX CONCLUÍDA COM SUCESSO")

        except Exception as e:
            self.logger.error(f"❌ ERRO na análise Forex: {e}")
            resultado['status'] = 'erro'
            resultado['erro'] = str(e)

        return resultado

    def _analisar_take_profit(self) -> List[Dict]:
        """Identificar níveis de TAKE PROFIT baseados em análise técnica"""
        oportunidades_tp = []

        for par in self.pares_forex:
            try:
                # Carregar dados usando método simplificado
                dados = self._carregar_dados_forex_simples(par, periodo='3mo')
                if dados.empty:
                    continue

                # Detectar níveis críticos (versão simplificada)
                niveis = self._detectar_niveis_simples(dados)

                # Análise de momentum e tendência
                dados['SMA_20'] = dados['Close'].rolling(20).mean()
                dados['SMA_50'] = dados['Close'].rolling(50).mean()

                preco_atual = dados['Close'].iloc[-1]
                sma_20 = dados['SMA_20'].iloc[-1]
                sma_50 = dados['SMA_50'].iloc[-1]

                # Lógica de TAKE PROFIT
                if preco_atual > sma_20 > sma_50:  # Tendência de alta
                    # Procurar resistência próxima
                    resistencia_proxima = None
                    for nivel in niveis.get('resistencias', []):
                        if nivel > preco_atual * 1.005:  # 0.5% acima
                            resistencia_proxima = nivel
                            break

                    if resistencia_proxima:
                        distancia = ((resistencia_proxima - preco_atual) / preco_atual) * 100
                        if distancia <= 3.0:  # Até 3% de ganho
                            oportunidades_tp.append({
                                'par': par,
                                'tipo': 'TAKE_PROFIT',
                                'direcao': 'VENDA',
                                'preco_atual': round(preco_atual, 5),
                                'nivel_tp': round(resistencia_proxima, 5),
                                'potencial_ganho_pct': round(distancia, 2),
                                'confianca': 'ALTA' if distancia <= 1.5 else 'MEDIA',
                                'justificativa': f'Resistência técnica em {resistencia_proxima:.5f} com tendência de alta confirmada'
                            })

                elif preco_atual < sma_20 < sma_50:  # Tendência de baixa
                    # Procurar suporte próximo
                    suporte_proximo = None
                    for nivel in sorted(niveis.get('suportes', []), reverse=True):
                        if nivel < preco_atual * 0.995:  # 0.5% abaixo
                            suporte_proximo = nivel
                            break

                    if suporte_proximo:
                        distancia = ((preco_atual - suporte_proximo) / preco_atual) * 100
                        if distancia <= 3.0:  # Até 3% de ganho
                            oportunidades_tp.append({
                                'par': par,
                                'tipo': 'TAKE_PROFIT',
                                'direcao': 'COMPRA',
                                'preco_atual': round(preco_atual, 5),
                                'nivel_tp': round(suporte_proximo, 5),
                                'potencial_ganho_pct': round(distancia, 2),
                                'confianca': 'ALTA' if distancia <= 1.5 else 'MEDIA',
                                'justificativa': f'Suporte técnico em {suporte_proximo:.5f} com tendência de baixa confirmada'
                            })

            except Exception as e:
                self.logger.warning(f"Erro ao analisar TAKE PROFIT para {par}: {e}")
                continue

        return oportunidades_tp

    def _analisar_reforco_posicao(self) -> List[Dict]:
        """Identificar oportunidades de reforço de posição"""
        oportunidades_reforco = []

        for par in self.pares_forex:
            try:
                # Carregar dados usando método simplificado
                dados = self._carregar_dados_forex_simples(par, periodo='3mo')
                if dados.empty:
                    continue

                # Análise de volatilidade e momentum
                dados['Returns'] = dados['Close'].pct_change()
                dados['Volatility'] = dados['Returns'].rolling(20).std() * np.sqrt(252)
                dados['RSI'] = self._calcular_rsi(dados['Close'])

                preco_atual = dados['Close'].iloc[-1]
                volatilidade = dados['Volatility'].iloc[-1]
                rsi = dados['RSI'].iloc[-1]

                # Lógica de reforço
                if rsi < 30 and volatilidade < 0.15:  # Oversold e baixa volatilidade
                    # Procurar pullback para suporte
                    suporte_proximo = self._encontrar_suporte_proximo(dados, preco_atual)

                    if suporte_proximo and abs((suporte_proximo - preco_atual) / preco_atual) < 0.02:
                        oportunidades_reforco.append({
                            'par': par,
                            'tipo': 'REFORCO_POSICAO',
                            'direcao': 'COMPRA',
                            'preco_atual': round(preco_atual, 5),
                            'nivel_entrada': round(suporte_proximo, 5),
                            'rsi_atual': round(rsi, 2),
                            'volatilidade': round(volatilidade, 4),
                            'confianca': 'ALTA',
                            'justificativa': f'RSI em {rsi:.1f} (oversold) com baixa volatilidade. Reforçar em suporte {suporte_proximo:.5f}'
                        })

                elif rsi > 70 and volatilidade < 0.15:  # Overbought e baixa volatilidade
                    # Procurar pullback para resistência
                    resistencia_proxima = self._encontrar_resistencia_proxima(dados, preco_atual)

                    if resistencia_proxima and abs((resistencia_proxima - preco_atual) / preco_atual) < 0.02:
                        oportunidades_reforco.append({
                            'par': par,
                            'tipo': 'REFORCO_POSICAO',
                            'direcao': 'VENDA',
                            'preco_atual': round(preco_atual, 5),
                            'nivel_entrada': round(resistencia_proxima, 5),
                            'rsi_atual': round(rsi, 2),
                            'volatilidade': round(volatilidade, 4),
                            'confianca': 'ALTA',
                            'justificativa': f'RSI em {rsi:.1f} (overbought) com baixa volatilidade. Reforçar em resistência {resistencia_proxima:.5f}'
                        })

            except Exception as e:
                self.logger.warning(f"Erro ao analisar reforço para {par}: {e}")
                continue

        return oportunidades_reforco

    def _analisar_hedge(self) -> List[Dict]:
        """Identificar oportunidades de hedge através de correlações"""
        oportunidades_hedge = []

        try:
            # Carregar dados de todos os pares
            dados_pares = {}
            for par in self.pares_forex:
                dados = self._carregar_dados_forex_simples(par, periodo='3mo')
                if not dados.empty:
                    dados_pares[par] = dados['Close'].pct_change().dropna()

            if len(dados_pares) >= 2:
                # Criar DataFrame de retornos
                df_retornos = pd.DataFrame(dados_pares)

                # Calcular correlação
                correlacao = df_retornos.corr()

                # Identificar pares com correlação negativa forte (bons para hedge)
                for i in range(len(correlacao.columns)):
                    for j in range(i+1, len(correlacao.columns)):
                        par1 = correlacao.columns[i]
                        par2 = correlacao.columns[j]
                        corr_valor = correlacao.iloc[i, j]

                        if corr_valor <= -0.3:  # Correlação negativa moderada/forte
                            oportunidades_hedge.append({
                                'par_principal': par1,
                                'par_hedge': par2,
                                'correlacao': round(corr_valor, 3),
                                'tipo_hedge': 'CORRELACAO_NEGATIVA',
                                'eficacia': 'ALTA' if abs(corr_valor) > 0.5 else 'MEDIA',
                                'justificativa': f'Correlação {corr_valor:.3f} permite hedge eficaz entre {par1} e {par2}'
                            })

        except Exception as e:
            self.logger.warning(f"Erro ao analisar hedge: {e}")

        return oportunidades_hedge

    def _analisar_correlacoes(self) -> Dict:
        """Análise completa de correlações entre pares Forex"""
        analise_corr = {
            'matriz_correlacao': {},
            'pares_mais_correlacionados': [],
            'pares_menos_correlacionados': [],
            'insights_correlacao': []
        }

        try:
            # Carregar dados de todos os pares
            dados_pares = {}
            for par in self.pares_forex:
                dados = self._carregar_dados_forex_simples(par, periodo='3mo')
                if not dados.empty:
                    dados_pares[par] = dados['Close']

            if len(dados_pares) >= 2:
                # Criar DataFrame e calcular correlação
                df_precos = pd.DataFrame(dados_pares)
                correlacao = df_precos.pct_change().corr()

                # Matriz de correlação
                analise_corr['matriz_correlacao'] = correlacao.round(3).to_dict()

                # Pares mais correlacionados (positiva)
                corr_flat = correlacao.where(np.triu(np.ones_like(correlacao), k=1).astype(bool))
                max_corr = corr_flat.max().max()
                max_corr_pairs = []

                for i in range(len(correlacao)):
                    for j in range(i+1, len(correlacao)):
                        if correlacao.iloc[i, j] == max_corr:
                            max_corr_pairs.append({
                                'par1': correlacao.index[i],
                                'par2': correlacao.columns[j],
                                'correlacao': round(max_corr, 3)
                            })

                analise_corr['pares_mais_correlacionados'] = max_corr_pairs

                # Pares menos correlacionados (negativa)
                min_corr = corr_flat.min().min()
                min_corr_pairs = []

                for i in range(len(correlacao)):
                    for j in range(i+1, len(correlacao)):
                        if correlacao.iloc[i, j] == min_corr:
                            min_corr_pairs.append({
                                'par1': correlacao.index[i],
                                'par2': correlacao.columns[j],
                                'correlacao': round(min_corr, 3)
                            })

                analise_corr['pares_menos_correlacionados'] = min_corr_pairs

                # Insights
                analise_corr['insights_correlacao'] = self._gerar_insights_correlacao(correlacao)

        except Exception as e:
            self.logger.warning(f"Erro na análise de correlação: {e}")

        return analise_corr

    def _calcular_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calcular RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def _encontrar_suporte_proximo(self, dados: pd.DataFrame, preco_atual: float) -> Optional[float]:
        """Encontrar suporte técnico próximo"""
        # Implementação simplificada - em produção usaria detector de níveis
        return preco_atual * 0.98  # 2% abaixo como exemplo

    def _encontrar_resistencia_proxima(self, dados: pd.DataFrame, preco_atual: float) -> Optional[float]:
        """Encontrar resistência técnica próxima"""
        # Implementação simplificada - em produção usaria detector de níveis
        return preco_atual * 1.02  # 2% acima como exemplo

    def _gerar_insights_correlacao(self, correlacao: pd.DataFrame) -> List[str]:
        """Gerar insights sobre correlações"""
        insights = []

        # Análise EURUSD vs outros
        eurusd_corr = correlacao.loc['EURUSD=X'].drop('EURUSD=X')
        max_corr_eurusd = eurusd_corr.max()
        min_corr_eurusd = eurusd_corr.min()

        insights.append(f"EURUSD mostra correlação máxima de {max_corr_eurusd:.3f} e mínima de {min_corr_eurusd:.3f}")

        # Análise de pares com USD
        pares_usd = [par for par in self.pares_forex if 'USD' in par]
        if len(pares_usd) > 1:
            corr_usd = correlacao.loc[pares_usd, pares_usd]
            media_corr_usd = corr_usd.mean().mean()
            insights.append(f"Correlação média entre pares com USD: {media_corr_usd:.3f}")

        return insights

    def _detectar_niveis_simples(self, dados: pd.DataFrame) -> Dict:
        """Detecção simplificada de suportes e resistências"""
        try:
            # Usar médias móveis como referência simples
            dados['SMA_20'] = dados['Close'].rolling(20).mean()
            dados['SMA_50'] = dados['Close'].rolling(50).mean()

            preco_atual = dados['Close'].iloc[-1]
            sma_20 = dados['SMA_20'].iloc[-1]

            # Suportes e resistências simples baseados em percentis
            suportes = [
                dados['Low'].quantile(0.25),
                dados['Low'].quantile(0.5),
                dados['Low'].quantile(0.75)
            ]

            resistencias = [
                dados['High'].quantile(0.25),
                dados['High'].quantile(0.5),
                dados['High'].quantile(0.75)
            ]

            return {
                'suportes': suportes,
                'resistencias': resistencias
            }

        except Exception as e:
            self.logger.warning(f"Erro na detecção simples de níveis: {e}")
            return {'suportes': [], 'resistencias': []}

    def _calcular_metricas_gerais(self, resultado: Dict) -> Dict:
        """Calcular métricas gerais da análise"""
        return {
            'total_oportunidades_tp': len(resultado.get('oportunidades_take_profit', [])),
            'total_oportunidades_reforco': len(resultado.get('oportunidades_reforco', [])),
            'total_oportunidades_hedge': len(resultado.get('oportunidades_hedge', [])),
            'pares_analisados': len(self.pares_forex),
            'timestamp_analise': datetime.now().isoformat()
        }

    def _carregar_dados_forex_simples(self, par: str, periodo: str = '3mo') -> pd.DataFrame:
        """Carregamento simplificado de dados Forex usando yfinance diretamente"""
        try:
            import yfinance as yf

            ticker = yf.Ticker(par)
            dados = ticker.history(period=periodo, interval='1d', auto_adjust=True)

            if dados.empty or len(dados) < 10:
                return pd.DataFrame()

            # Padronizar colunas
            dados = dados[['Open', 'High', 'Low', 'Close', 'Volume']]
            dados.index = pd.to_datetime(dados.index)

            return dados

        except Exception as e:
            self.logger.warning(f"Erro ao carregar dados simples para {par}: {e}")
            return pd.DataFrame()