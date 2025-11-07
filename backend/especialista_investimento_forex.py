#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ESPECIALISTA DE INVESTIMENTO INTERNACIONAL - FOREX
Análise especializada de oportunidades em Forex com horizonte dias/semanas

Formato Estruturado:
[INICIO] Dados econômicos atuais
[DURANTE] Correlação do ativo com outros ativos
[DURANTE] Notícias e eventos que impactam
[FIM] Parecer sobre oportunidade (APROVAR/DESCARTAR + níveis preço)
[QUANDO] Identificar outra oportunidade via correlação e RECOMENDAR
"""

import json
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging
import requests
import warnings

try:
    from .carregador_dados_historicos import CarregadorDadosHistoricos
except ImportError:
    try:
        from carregador_dados_historicos import CarregadorDadosHistoricos
    except ImportError:
        # Fallback sem carregador avançado
        CarregadorDadosHistoricos = None

warnings.filterwarnings('ignore')

class EspecialistaInvestimentoForex:
    """Especialista em análise de oportunidades Forex"""

    def __init__(self):
        self.logger = self._configurar_logger()
        self.carregador = CarregadorDadosHistoricos() if CarregadorDadosHistoricos else None

        # Pares Forex principais para análise
        self.pares_forex_principais = [
            'EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'USDCAD=X', 'USDCHF=X',
            'AUDUSD=X', 'NZDUSD=X', 'USDMXN=X', 'USDZAR=X', 'USDBRL=X'
        ]

        # Ativos de correlação (índices, commodities, bonds)
        self.ativos_correlacao = [
            '^GSPC', '^IXIC', '^VIX', 'GC=F', 'CL=F', '^TNX', 'DX-Y.NYB'
        ]

        # Calendário econômico (principais eventos)
        self.eventos_economicos = [
            'FOMC', 'ECB', 'BoE', 'BoJ', 'NFP', 'GDP', 'CPI', 'PPI'
        ]

    def _configurar_logger(self) -> logging.Logger:
        """Configura logger para o especialista"""
        logger = logging.getLogger('EspecialistaForex')
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def analisar_oportunidade_forex(self, simbolo: str, horizonte: str = 'dias') -> Dict:
        """
        Análise completa de oportunidade Forex seguindo formato estruturado

        Args:
            simbolo: Par Forex (ex: 'EURUSD=X')
            horizonte: 'dias' ou 'semanas'

        Returns:
            Dict com análise estruturada
        """
        self.logger.info(f"🔍 INICIANDO ANÁLISE ESPECIALISTA: {simbolo}")

        analise = {
            'simbolo': simbolo,
            'horizonte': horizonte,
            'timestamp_analise': datetime.now().isoformat(),
            'INICIO': {},
            'DURANTE': {},
            'FIM': {},
            'QUANDO': {},
            'status': 'em_andamento'
        }

        try:
            # [INICIO] - Dados econômicos atuais
            self.logger.info("📊 [INICIO] Coletando dados econômicos atuais...")
            analise['INICIO'] = self._coletar_dados_economicos_atuais()

            # [DURANTE] - Correlação com outros ativos
            self.logger.info("📈 [DURANTE] Analisando correlações...")
            analise['DURANTE']['correlacoes'] = self._analisar_correlacoes_ativo(simbolo)

            # [DURANTE] - Notícias e eventos que impactam
            self.logger.info("📰 [DURANTE] Coletando notícias e eventos...")
            analise['DURANTE']['noticias_eventos'] = self._coletar_noticias_eventos(simbolo)

            # [FIM] - Parecer sobre oportunidade
            self.logger.info("🎯 [FIM] Elaborando parecer sobre oportunidade...")
            analise['FIM'] = self._elaborar_parecer_oportunidade(simbolo, analise, horizonte)

            # [QUANDO] - Identificar outra oportunidade via correlação
            self.logger.info("🔄 [QUANDO] Identificando oportunidades correlacionadas...")
            analise['QUANDO'] = self._identificar_oportunidade_correlacionada(simbolo, analise)

            analise['status'] = 'concluido_com_sucesso'
            self.logger.info("✅ ANÁLISE ESPECIALISTA CONCLUÍDA")

        except Exception as e:
            self.logger.error(f"❌ ERRO na análise: {str(e)}")
            analise['status'] = 'erro'
            analise['erro'] = str(e)

        return analise

    def _coletar_dados_economicos_atuais(self) -> Dict:
        """[INICIO] Coleta dados econômicos atuais"""
        dados = {}

        try:
            # Indicadores principais
            indicadores = {
                'VIX': '^VIX',
                'DXY': 'DX-Y.NYB',
                'Treasury_10Y': '^TNX',
                'S&P_500': '^GSPC',
                'Ouro': 'GC=F',
                'WTI': 'CL=F'
            }

            for nome, ticker in indicadores.items():
                try:
                    ativo = yf.Ticker(ticker)
                    hist = ativo.history(period='2d')

                    if not hist.empty:
                        atual = float(hist['Close'].iloc[-1])
                        anterior = float(hist['Close'].iloc[-2]) if len(hist) > 1 else atual
                        variacao = ((atual / anterior) - 1) * 100

                        dados[nome] = {
                            'valor': round(atual, 2),
                            'variacao_pct': round(variacao, 2),
                            'status': 'alta' if variacao > 0 else 'baixa'
                        }
                except Exception as e:
                    self.logger.warning(f"Erro ao coletar {nome}: {str(e)}")
                    dados[nome] = {'erro': str(e)}

            # Taxas de juros (se disponíveis via API)
            dados['taxas_juros'] = self._coletar_taxas_juros()

        except Exception as e:
            self.logger.error(f"Erro geral na coleta de dados econômicos: {str(e)}")
            dados['erro_geral'] = str(e)

        return dados

    def _coletar_taxas_juros(self) -> Dict:
        """Coleta taxas de juros de bancos centrais"""
        taxas = {}

        # Taxas hardcoded (em produção, usar API real)
        taxas_referencia = {
            'FED': 4.50,  # FOMC
            'ECB': 3.75,  # BCE
            'BoE': 4.75,  # Banco da Inglaterra
            'BoJ': -0.10, # Banco do Japão
            'BRL': 10.75  # Brasil
        }

        for banco, taxa in taxas_referencia.items():
            taxas[banco] = {
                'taxa': taxa,
                'status': 'expansionista' if taxa < 2.0 else 'contracionista'
            }

        return taxas

    def _analisar_correlacoes_ativo(self, simbolo: str) -> Dict:
        """[DURANTE] Analisa correlação do ativo com outros ativos"""
        correlacoes = {}

        try:
            # Períodos de análise
            periodos = {'30d': 30, '90d': 90, '180d': 180}

            for periodo_nome, dias in periodos.items():
                correlacoes[periodo_nome] = {}

                # Coletar dados do ativo principal
                try:
                    ativo_principal = yf.Ticker(simbolo)
                    hist_principal = ativo_principal.history(period=f'{dias}d')

                    if hist_principal.empty:
                        continue

                    retornos_principal = hist_principal['Close'].pct_change().dropna()

                    # Analisar correlação com outros pares Forex
                    for par in self.pares_forex_principais:
                        if par == simbolo:
                            continue

                        try:
                            ativo_comp = yf.Ticker(par)
                            hist_comp = ativo_comp.history(period=f'{dias}d')

                            if not hist_comp.empty:
                                retornos_comp = hist_comp['Close'].pct_change().dropna()

                                # Alinhar datas
                                dados_alinhados = pd.concat([retornos_principal, retornos_comp], axis=1, join='inner')
                                dados_alinhados.columns = ['principal', 'comparado']

                                if len(dados_alinhados) > 10:
                                    correlacao = dados_alinhados.corr().iloc[0, 1]
                                    correlacoes[periodo_nome][par] = round(correlacao, 3)

                        except Exception as e:
                            self.logger.debug(f"Erro correlação {par}: {str(e)}")

                    # Correlação com ativos globais
                    for ativo_global in self.ativos_correlacao:
                        try:
                            ativo_comp = yf.Ticker(ativo_global)
                            hist_comp = ativo_comp.history(period=f'{dias}d')

                            if not hist_comp.empty:
                                retornos_comp = hist_comp['Close'].pct_change().dropna()

                                dados_alinhados = pd.concat([retornos_principal, retornos_comp], axis=1, join='inner')
                                dados_alinhados.columns = ['principal', 'comparado']

                                if len(dados_alinhados) > 10:
                                    correlacao = dados_alinhados.corr().iloc[0, 1]
                                    correlacoes[periodo_nome][ativo_global] = round(correlacao, 3)

                        except Exception as e:
                            self.logger.debug(f"Erro correlação {ativo_global}: {str(e)}")

                except Exception as e:
                    self.logger.warning(f"Erro análise período {periodo_nome}: {str(e)}")

        except Exception as e:
            self.logger.error(f"Erro geral na análise de correlações: {str(e)}")
            correlacoes['erro'] = str(e)

        return correlacoes

    def _coletar_noticias_eventos(self, simbolo: str) -> Dict:
        """[DURANTE] Coleta notícias e eventos que impactam o ativo"""
        noticias_eventos = {
            'noticias_recentes': [],
            'eventos_economicos': [],
            'sentimento_mercado': {}
        }

        try:
            # Extrair moedas do par Forex
            moedas = self._extrair_moedas_par(simbolo)

            # Buscar notícias relacionadas às moedas
            for moeda in moedas:
                try:
                    # Simulação de busca de notícias (em produção, usar API real)
                    noticias_mock = self._buscar_noticias_moedas(moeda)
                    noticias_eventos['noticias_recentes'].extend(noticias_mock)
                except Exception as e:
                    self.logger.debug(f"Erro notícias {moeda}: {str(e)}")

            # Eventos econômicos próximos
            noticias_eventos['eventos_economicos'] = self._calendario_economico_proximo()

            # Análise de sentimento
            noticias_eventos['sentimento_mercado'] = self._analisar_sentimento_mercado(simbolo)

        except Exception as e:
            self.logger.error(f"Erro na coleta de notícias/eventos: {str(e)}")
            noticias_eventos['erro'] = str(e)

        return noticias_eventos

    def _extrair_moedas_par(self, simbolo: str) -> List[str]:
        """Extrai moedas de um par Forex"""
        # Remover sufixo =X se existir
        par = simbolo.replace('=X', '')

        if len(par) == 6:  # Pares padrão (EURUSD)
            moeda1 = par[:3]
            moeda2 = par[3:]
            return [moeda1, moeda2]
        elif len(par) == 7:  # Pares com uma letra extra
            moeda1 = par[:3]
            moeda2 = par[3:]
            return [moeda1, moeda2]

        return []

    def _buscar_noticias_moedas(self, moeda: str) -> List[Dict]:
        """Busca notícias relacionadas a uma moeda (simulado)"""
        # Em produção, implementar busca real de notícias
        noticias_mock = [
            {
                'titulo': f'Desenvolvimentos econômicos em {moeda}',
                'fonte': 'Reuters',
                'data': datetime.now().isoformat(),
                'impacto': 'neutro',
                'resumo': f'Notícias econômicas recentes sobre {moeda}'
            }
        ]

        return noticias_mock

    def _calendario_economico_proximo(self) -> List[Dict]:
        """Retorna calendário econômico dos próximos dias"""
        eventos = []

        # Eventos mock (em produção, usar API real de calendário econômico)
        eventos_base = [
            {
                'evento': 'FOMC Minutes',
                'data': (datetime.now() + timedelta(days=2)).isoformat(),
                'impacto': 'alto',
                'pais': 'EUA'
            },
            {
                'evento': 'ECB Press Conference',
                'data': (datetime.now() + timedelta(days=5)).isoformat(),
                'impacto': 'alto',
                'pais': 'Europa'
            }
        ]

        return eventos_base

    def _analisar_sentimento_mercado(self, simbolo: str) -> Dict:
        """Analisa sentimento do mercado para o ativo"""
        # Análise simplificada de sentimento
        sentimento = {
            'geral': 'neutro',
            'score': 0.0,
            'fonte': 'análise_técnica'
        }

        # Em produção, implementar análise real de sentimento
        return sentimento

    def _elaborar_parecer_oportunidade(self, simbolo: str, analise: Dict, horizonte: str) -> Dict:
        """[FIM] Elabora parecer sobre a oportunidade"""
        parecer = {
            'decisao': 'DESCARTAR',
            'niveis_entrada': {},
            'take_profit': {},
            'stop_loss': {},
            'justificativa': [],
            'risco_retorno': {},
            'probabilidade_sucesso': 0.0
        }

        try:
            # Análise técnica básica
            dados_tecnicos = self._analisar_dados_tecnicos(simbolo)

            # Avaliação de condições de mercado
            condicoes_mercado = self._avaliar_condicoes_mercado(analise)

            # Cálculo de níveis de preço
            niveis_preco = self._calcular_niveis_preco(simbolo, horizonte)

            # Decisão baseada em múltiplos fatores
            score_total = self._calcular_score_oportunidade(dados_tecnicos, condicoes_mercado)

            # Tomada de decisão
            if score_total >= 7.0:
                parecer['decisao'] = 'APROVAR'
                parecer['probabilidade_sucesso'] = min(score_total / 10.0, 0.85)
            elif score_total >= 5.0:
                parecer['decisao'] = 'OBSERVAR'
                parecer['probabilidade_sucesso'] = score_total / 10.0
            else:
                parecer['decisao'] = 'DESCARTAR'
                parecer['probabilidade_sucesso'] = max(score_total / 10.0, 0.15)

            # Níveis de preço
            parecer['niveis_entrada'] = niveis_preco.get('entrada', {})
            parecer['take_profit'] = niveis_preco.get('take_profit', {})
            parecer['stop_loss'] = niveis_preco.get('stop_loss', {})

            # Justificativa
            parecer['justificativa'] = self._gerar_justificativa(score_total, dados_tecnicos, condicoes_mercado)

            # Risco/Retorno
            parecer['risco_retorno'] = self._calcular_risco_retorno(niveis_preco)

        except Exception as e:
            self.logger.error(f"Erro no parecer: {str(e)}")
            parecer['erro'] = str(e)

        return parecer

    def _analisar_dados_tecnicos(self, simbolo: str) -> Dict:
        """Análise técnica básica do ativo"""
        analise = {}

        try:
            ativo = yf.Ticker(simbolo)
            hist = ativo.history(period='6mo')

            if not hist.empty:
                # Tendência
                sma_50 = hist['Close'].rolling(50).mean().iloc[-1]
                sma_200 = hist['Close'].rolling(200).mean().iloc[-1]
                preco_atual = hist['Close'].iloc[-1]

                analise['tendencia'] = 'alta' if sma_50 > sma_200 else 'baixa'
                analise['distancia_sma50'] = ((preco_atual / sma_50) - 1) * 100

                # RSI
                delta = hist['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                analise['rsi'] = rsi.iloc[-1] if not rsi.empty else 50

                # Volatilidade
                retornos = hist['Close'].pct_change().dropna()
                analise['volatilidade'] = retornos.std() * np.sqrt(252)  # Anualizada

        except Exception as e:
            self.logger.error(f"Erro análise técnica: {str(e)}")
            analise['erro'] = str(e)

        return analise

    def _avaliar_condicoes_mercado(self, analise: Dict) -> Dict:
        """Avalia condições gerais do mercado"""
        condicoes = {
            'vix': 'neutro',
            'dxy': 'neutro',
            'volatilidade': 'normal',
            'score': 5.0
        }

        try:
            dados_economicos = analise.get('INICIO', {})

            # Avaliar VIX
            vix = dados_economicos.get('VIX', {})
            if vix.get('valor', 20) > 25:
                condicoes['vix'] = 'alto'
                condicoes['score'] -= 1
            elif vix.get('valor', 20) < 15:
                condicoes['vix'] = 'baixo'
                condicoes['score'] += 1

            # Avaliar DXY
            dxy = dados_economicos.get('DXY', {})
            if dxy.get('variacao_pct', 0) > 1:
                condicoes['dxy'] = 'forte'
            elif dxy.get('variacao_pct', 0) < -1:
                condicoes['dxy'] = 'fraco'

        except Exception as e:
            self.logger.error(f"Erro avaliação condições: {str(e)}")

        return condicoes

    def _calcular_niveis_preco(self, simbolo: str, horizonte: str) -> Dict:
        """Calcula níveis de entrada, TP e SL"""
        niveis = {
            'entrada': {},
            'take_profit': {},
            'stop_loss': {}
        }

        try:
            ativo = yf.Ticker(simbolo)
            hist = ativo.history(period='6mo')

            if not hist.empty:
                preco_atual = hist['Close'].iloc[-1]
                volatilidade = hist['Close'].pct_change().std()

                # Ajustar multiplicadores baseado no horizonte
                if horizonte == 'dias':
                    mult_tp = 2.0
                    mult_sl = 1.0
                else:  # semanas
                    mult_tp = 3.0
                    mult_sl = 1.5

                # Níveis de entrada (breakout)
                niveis['entrada']['conservador'] = round(preco_atual * 0.98, 4)
                niveis['entrada']['agressivo'] = round(preco_atual * 0.95, 4)

                # Take Profit
                alvo_tp = preco_atual * (1 + volatilidade * mult_tp)
                niveis['take_profit']['primario'] = round(alvo_tp, 4)
                niveis['take_profit']['secundario'] = round(alvo_tp * 1.2, 4)

                # Stop Loss
                alvo_sl = preco_atual * (1 - volatilidade * mult_sl)
                niveis['stop_loss']['conservador'] = round(alvo_sl, 4)
                niveis['stop_loss']['agressivo'] = round(alvo_sl * 0.95, 4)

        except Exception as e:
            self.logger.error(f"Erro cálculo níveis: {str(e)}")

        return niveis

    def _calcular_score_oportunidade(self, dados_tecnicos: Dict, condicoes_mercado: Dict) -> float:
        """Calcula score geral da oportunidade"""
        score = 5.0  # Score base neutro

        try:
            # Análise técnica (40% do score)
            if dados_tecnicos.get('tendencia') == 'alta':
                score += 1.5
            elif dados_tecnicos.get('tendencia') == 'baixa':
                score -= 1.5

            rsi = dados_tecnicos.get('rsi', 50)
            if 30 < rsi < 70:
                score += 1.0
            elif rsi < 30 or rsi > 70:
                score -= 1.0

            # Condições de mercado (30% do score)
            score += (condicoes_mercado.get('score', 5.0) - 5.0) * 0.6

            # Volatilidade (20% do score)
            volatilidade = dados_tecnicos.get('volatilidade', 0.2)
            if 0.1 < volatilidade < 0.3:
                score += 1.0
            elif volatilidade > 0.4:
                score -= 1.0

            # Limitar score entre 0 e 10
            score = max(0, min(10, score))

        except Exception as e:
            self.logger.error(f"Erro cálculo score: {str(e)}")

        return score

    def _gerar_justificativa(self, score: float, dados_tecnicos: Dict, condicoes_mercado: Dict) -> List[str]:
        """Gera justificativa detalhada da decisão"""
        justificativa = []

        try:
            if score >= 7.0:
                justificativa.append("✅ Oportunidade favorável com múltiplos fatores positivos")
            elif score >= 5.0:
                justificativa.append("⚠️ Oportunidade neutra, aguardar confirmação")
            else:
                justificativa.append("❌ Condições desfavoráveis, evitar entrada")

            # Detalhes técnicos
            tendencia = dados_tecnicos.get('tendencia', 'indefinida')
            justificativa.append(f"Tendência técnica: {tendencia}")

            rsi = dados_tecnicos.get('rsi', 50)
            if rsi < 30:
                justificativa.append("RSI indica sobrevenda (possível reversão)")
            elif rsi > 70:
                justificativa.append("RSI indica sobrecompra (possível correção)")

            # Condições de mercado
            vix_status = condicoes_mercado.get('vix', 'neutro')
            justificativa.append(f"Volatilidade mercado: {vix_status}")

        except Exception as e:
            justificativa.append(f"Erro na geração de justificativa: {str(e)}")

        return justificativa

    def _calcular_risco_retorno(self, niveis_preco: Dict) -> Dict:
        """Calcula métricas de risco/retorno"""
        risco_retorno = {
            'reward_risk_ratio': 0.0,
            'potencial_ganho_pct': 0.0,
            'risco_perda_pct': 0.0
        }

        try:
            entrada = niveis_preco.get('entrada', {}).get('conservador', 0)
            tp = niveis_preco.get('take_profit', {}).get('primario', 0)
            sl = niveis_preco.get('stop_loss', {}).get('conservador', 0)

            if entrada > 0 and tp > entrada and sl < entrada:
                ganho_potencial = ((tp / entrada) - 1) * 100
                perda_potencial = ((entrada / sl) - 1) * 100

                risco_retorno['potencial_ganho_pct'] = round(ganho_potencial, 2)
                risco_retorno['risco_perda_pct'] = round(perda_potencial, 2)
                risco_retorno['reward_risk_ratio'] = round(ganho_potencial / perda_potencial, 2)

        except Exception as e:
            self.logger.error(f"Erro cálculo risco/retorno: {str(e)}")

        return risco_retorno

    def _identificar_oportunidade_correlacionada(self, simbolo: str, analise: Dict) -> Dict:
        """[QUANDO] Identifica outra oportunidade via correlação"""
        recomendacao = {
            'ativo_recomendado': None,
            'correlacao': 0.0,
            'justificativa': '',
            'niveis_sugeridos': {}
        }

        try:
            correlacoes = analise.get('DURANTE', {}).get('correlacoes', {})

            # Procurar correlação forte no período de 90 dias
            corr_90d = correlacoes.get('90d', {})

            melhor_correlacao = 0.0
            ativo_melhor = None

            for ativo, corr in corr_90d.items():
                if abs(corr) > abs(melhor_correlacao) and ativo != simbolo:
                    melhor_correlacao = corr
                    ativo_melhor = ativo

            if ativo_melhor and abs(melhor_correlacao) > 0.6:
                recomendacao['ativo_recomendado'] = ativo_melhor
                recomendacao['correlacao'] = round(melhor_correlacao, 3)

                # Justificativa baseada na correlação
                if melhor_correlacao > 0.7:
                    recomendacao['justificativa'] = f"Correlação muito forte positiva ({melhor_correlacao}). Movimento similar esperado."
                elif melhor_correlacao < -0.7:
                    recomendacao['justificativa'] = f"Correlação forte negativa ({melhor_correlacao}). Oportunidade de diversificação."

                # Calcular níveis para o ativo recomendado
                recomendacao['niveis_sugeridos'] = self._calcular_niveis_preco(ativo_melhor, 'dias')

        except Exception as e:
            self.logger.error(f"Erro identificação oportunidade correlacionada: {str(e)}")

        return recomendacao

    def gerar_relatorio_formatado(self, analise: Dict) -> str:
        """Gera relatório formatado da análise"""
        if analise.get('status') != 'concluido_com_sucesso':
            return f"❌ Análise não concluída: {analise.get('erro', 'Erro desconhecido')}"

        simbolo = analise.get('simbolo', 'N/A')

        relatorio = f"""
╔══════════════════════════════════════════════════════════════╗
║           ESPECIALISTA DE INVESTIMENTO INTERNACIONAL         ║
║                    ANÁLISE FOREX - {simbolo}                     ║
╚══════════════════════════════════════════════════════════════╝

"""

        # [INICIO] - Dados econômicos atuais
        relatorio += "[INICIO] DADOS ECONÔMICOS ATUAIS\n"
        relatorio += "=" * 50 + "\n"

        dados_economicos = analise.get('INICIO', {})
        for indicador, dados in dados_economicos.items():
            if isinstance(dados, dict) and 'valor' in dados:
                valor = dados['valor']
                variacao = dados.get('variacao_pct', 0)
                status = dados.get('status', 'neutro')
                relatorio += f"📊 {indicador}: {valor} ({variacao:+.2f}%) [{status}]\n"

        # [DURANTE] - Correlações
        relatorio += "\n[DURANTE] CORRELAÇÃO COM OUTROS ATIVOS\n"
        relatorio += "=" * 50 + "\n"

        correlacoes = analise.get('DURANTE', {}).get('correlacoes', {})
        corr_90d = correlacoes.get('90d', {})

        # Top 5 correlações positivas
        positivas = sorted([(k, v) for k, v in corr_90d.items() if v > 0.3],
                          key=lambda x: x[1], reverse=True)[:5]

        if positivas:
            relatorio += "📈 Correlações Positivas (90d):\n"
            for ativo, corr in positivas:
                relatorio += f"   {ativo}: {corr:+.3f}\n"

        # Top 5 correlações negativas
        negativas = sorted([(k, v) for k, v in corr_90d.items() if v < -0.3],
                          key=lambda x: x[1])[:5]

        if negativas:
            relatorio += "\n📉 Correlações Negativas (90d):\n"
            for ativo, corr in negativas:
                relatorio += f"   {ativo}: {corr:+.3f}\n"

        # [DURANTE] - Notícias e eventos
        relatorio += "\n[DURANTE] NOTÍCIAS E EVENTOS QUE IMPACTAM\n"
        relatorio += "=" * 50 + "\n"

        noticias_eventos = analise.get('DURANTE', {}).get('noticias_eventos', {})
        eventos = noticias_eventos.get('eventos_economicos', [])

        if eventos:
            relatorio += "📅 Eventos Econômicos Próximos:\n"
            for evento in eventos[:3]:  # Top 3
                data = evento.get('data', '')[:10]
                relatorio += f"   {evento.get('evento', '')} ({data}) - Impacto: {evento.get('impacto', '')}\n"

        # [FIM] - Parecer sobre oportunidade
        relatorio += "\n[FIM] PARECER SOBRE A OPORTUNIDADE\n"
        relatorio += "=" * 50 + "\n"

        fim = analise.get('FIM', {})
        decisao = fim.get('decisao', 'DESCARTAR')
        probabilidade = fim.get('probabilidade_sucesso', 0) * 100

        if decisao == 'APROVAR':
            relatorio += f"✅ DECISÃO: {decisao} (Probabilidade: {probabilidade:.1f}%)\n"
        elif decisao == 'OBSERVAR':
            relatorio += f"⚠️ DECISÃO: {decisao} (Probabilidade: {probabilidade:.1f}%)\n"
        else:
            relatorio += f"❌ DECISÃO: {decisao} (Probabilidade: {probabilidade:.1f}%)\n"

        # Níveis de preço
        entrada = fim.get('niveis_entrada', {})
        tp = fim.get('take_profit', {})
        sl = fim.get('stop_loss', {})

        if entrada:
            relatorio += f"\n🎯 NÍVEIS DE ENTRADA:\n"
            relatorio += f"   Conservador: {entrada.get('conservador', 'N/A')}\n"
            relatorio += f"   Agressivo: {entrada.get('agressivo', 'N/A')}\n"

        if tp:
            relatorio += f"\n💰 TAKE PROFIT:\n"
            relatorio += f"   Primário: {tp.get('primario', 'N/A')}\n"
            relatorio += f"   Secundário: {tp.get('secundario', 'N/A')}\n"

        if sl:
            relatorio += f"\n🛡️ STOP LOSS:\n"
            relatorio += f"   Conservador: {sl.get('conservador', 'N/A')}\n"
            relatorio += f"   Agressivo: {sl.get('agressivo', 'N/A')}\n"

        # Justificativa
        justificativa = fim.get('justificativa', [])
        if justificativa:
            relatorio += f"\n📋 JUSTIFICATIVA:\n"
            for item in justificativa:
                relatorio += f"   • {item}\n"

        # Risco/Retorno
        risco_retorno = fim.get('risco_retorno', {})
        if risco_retorno:
            relatorio += f"\n📊 RISCO/RETORNO:\n"
            relatorio += f"   Ratio Reward/Risk: {risco_retorno.get('reward_risk_ratio', 0):.2f}\n"
            relatorio += f"   Potencial Ganho: {risco_retorno.get('potencial_ganho_pct', 0):+.1f}%\n"
            relatorio += f"   Risco Perda: {risco_retorno.get('risco_perda_pct', 0):+.1f}%\n"

        # [QUANDO] - Oportunidade correlacionada
        relatorio += "\n[QUANDO] OPORTUNIDADE CORRELACIONADA RECOMENDADA\n"
        relatorio += "=" * 50 + "\n"

        quando = analise.get('QUANDO', {})
        ativo_recomendado = quando.get('ativo_recomendado')

        if ativo_recomendado:
            correlacao = quando.get('correlacao', 0)
            justificativa_quando = quando.get('justificativa', '')

            relatorio += f"🎯 ATIVO RECOMENDADO: {ativo_recomendado}\n"
            relatorio += f"📈 Correlação: {correlacao:+.3f}\n"
            relatorio += f"💡 Justificativa: {justificativa_quando}\n"

            # Níveis sugeridos
            niveis_sugeridos = quando.get('niveis_sugeridos', {})
            entrada_sug = niveis_sugeridos.get('entrada', {})
            if entrada_sug:
                relatorio += f"\n📍 NÍVEIS SUGERIDOS PARA {ativo_recomendado}:\n"
                relatorio += f"   Entrada: {entrada_sug.get('conservador', 'N/A')}\n"
                relatorio += f"   Take Profit: {niveis_sugeridos.get('take_profit', {}).get('primario', 'N/A')}\n"
                relatorio += f"   Stop Loss: {niveis_sugeridos.get('stop_loss', {}).get('conservador', 'N/A')}\n"
        else:
            relatorio += "❌ Nenhuma oportunidade correlacionada identificada\n"

        relatorio += f"\n⏰ Análise realizada em: {analise.get('timestamp_analise', '')[:19]}\n"
        relatorio += "=" * 80 + "\n"

        return relatorio


def analisar_oportunidade_cli():
    """Função CLI para análise de oportunidade Forex"""
    import argparse

    parser = argparse.ArgumentParser(description='Especialista de Investimento Forex')
    parser.add_argument('simbolo', help='Par Forex (ex: EURUSD=X)')
    parser.add_argument('--horizonte', choices=['dias', 'semanas'],
                       default='dias', help='Horizonte da análise')

    args = parser.parse_args()

    especialista = EspecialistaInvestimentoForex()
    analise = especialista.analisar_oportunidade_forex(args.simbolo, args.horizonte)

    print(especialista.gerar_relatorio_formatado(analise))


if __name__ == "__main__":
    analisar_oportunidade_cli()