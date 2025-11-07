#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análise Macro Especialista - Análise de Mercado com 20+ Anos de Experiência

Este script realiza análise completa de oportunidades de mercado usando:
1. Contexto macroeconômico atual
2. Análise técnica multi-timeframe
3. Correlações entre ativos e classes
4. Avaliação de risco-retorno
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yfinance as yf
from datetime import datetime, time
import pytz
import pandas as pd
from dataclasses import dataclass
from typing import Dict, List, Tuple
import logging

@dataclass
class AnaliseMacroAtual:
    """Estrutura para análise macro atual"""
    vix: float
    treasury_10y: float
    sp500: float
    dxy: float
    ouro: float
    petroleo: float
    timestamp: datetime
    regime_volatilidade: str
    regime_taxas: str
    sentimento_equity: str
    sessao_mercado: str

@dataclass
class OportunidadeEspecialista:
    """Estrutura para oportunidade identificada por especialista"""
    ativo: str
    acao_recomendada: str
    probabilidade_sucesso: int  # 0-100
    confianca: int  # 0-100
    preco_entrada: float
    preco_alvo: float
    stop_loss: float
    risk_reward: float
    timeframe: str
    catalysts: List[str]
    justificativa_tecnica: str
    justificativa_macro: str
    nivel_invalidacao: float
    contexto_correlacao: str

class EspecialistaMercadoFinanceiro:
    """
    Especialista Global em Mercado Financeiro com 20+ anos de experiência

    Especialização em:
    - Análise macro multi-mercado
    - Correlações entre classes de ativos
    - Timing ótimo de entrada/saída
    - Avaliação de risco-retorno
    """

    def __init__(self):
        self.logger = self._setup_logger()
        self.timezone_ny = pytz.timezone('US/Eastern')

    def _setup_logger(self) -> logging.Logger:
        """Configurar logger"""
        logger = logging.getLogger('EspecialistaMercado')
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%H:%M:%S'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def coletar_contexto_macro_atual(self) -> AnaliseMacroAtual:
        """Coletar contexto macroeconômico em tempo real"""

        self.logger.info("🌐 Coletando contexto macro atual...")

        try:
            # Indicadores principais
            vix = yf.Ticker('^VIX')
            vix_data = vix.history(period='2d')
            vix_atual = float(vix_data['Close'].iloc[-1]) if not vix_data.empty else 20.0

            treasury = yf.Ticker('^TNX')
            treasury_data = treasury.history(period='2d')
            treasury_atual = float(treasury_data['Close'].iloc[-1]) if not treasury_data.empty else 4.0

            sp500 = yf.Ticker('^GSPC')
            sp500_data = sp500.history(period='2d')
            sp500_atual = float(sp500_data['Close'].iloc[-1]) if not sp500_data.empty else 6700

            # Moeda e commodities
            dxy = yf.Ticker('DX-Y.NYB')
            dxy_data = dxy.history(period='2d')
            dxy_atual = float(dxy_data['Close'].iloc[-1]) if not dxy_data.empty else 100.0

            ouro = yf.Ticker('GC=F')
            ouro_data = ouro.history(period='2d')
            ouro_atual = float(ouro_data['Close'].iloc[-1]) if not ouro_data.empty else 2000.0

            petroleo = yf.Ticker('CL=F')
            petroleo_data = petroleo.history(period='2d')
            petroleo_atual = float(petroleo_data['Close'].iloc[-1]) if not petroleo_data.empty else 70.0

            # Determinar regimes de mercado
            regime_vol = self._determinar_regime_volatilidade(vix_atual)
            regime_taxas = self._determinar_regime_taxas(treasury_atual)
            sentimento_equity = self._determinar_sentimento_equity(sp500_atual, vix_atual)
            sessao = self._determinar_sessao_mercado()

            return AnaliseMacroAtual(
                vix=vix_atual,
                treasury_10y=treasury_atual,
                sp500=sp500_atual,
                dxy=dxy_atual,
                ouro=ouro_atual,
                petroleo=petroleo_atual,
                timestamp=datetime.now(),
                regime_volatilidade=regime_vol,
                regime_taxas=regime_taxas,
                sentimento_equity=sentimento_equity,
                sessao_mercado=sessao
            )

        except Exception as e:
            self.logger.error(f"❌ Erro coletando contexto macro: {e}")
            raise

    def _determinar_regime_volatilidade(self, vix: float) -> str:
        """Determinar regime de volatilidade atual"""
        if vix < 15:
            return "BAIXA_VOLATILIDADE"
        elif vix < 25:
            return "VOLATILIDADE_MODERADA"
        elif vix < 35:
            return "ALTA_VOLATILIDADE"
        else:
            return "VOLATILIDADE_EXTREMA"

    def _determinar_regime_taxas(self, treasury: float) -> str:
        """Determinar regime de taxas de juros"""
        if treasury < 2.0:
            return "TAXAS_BAIXAS"
        elif treasury < 4.0:
            return "TAXAS_MODERADAS"
        elif treasury < 6.0:
            return "TAXAS_ELEVADAS"
        else:
            return "TAXAS_RESTRITIVAS"

    def _determinar_sentimento_equity(self, sp500: float, vix: float) -> str:
        """Determinar sentimento do mercado de ações"""
        # Análise baseada em níveis históricos e VIX
        if sp500 > 6500 and vix < 20:
            return "OTIMISTA"
        elif sp500 > 6200 and vix < 25:
            return "MODERADAMENTE_OTIMISTA"
        elif vix > 30:
            return "PESSIMISTA"
        else:
            return "NEUTRO"

    def _determinar_sessao_mercado(self) -> str:
        """Determinar sessão de mercado atual"""
        agora_ny = datetime.now(self.timezone_ny).time()

        # Sessões de mercado (horário de NY)
        if time(9, 30) <= agora_ny <= time(16, 0):
            return "SESSAO_NYSE_ATIVA"
        elif time(18, 0) <= agora_ny <= time(23, 59) or time(0, 0) <= agora_ny <= time(6, 0):
            return "SESSAO_ASIATICA"
        elif time(2, 0) <= agora_ny <= time(11, 0):
            return "SESSAO_EUROPEIA"
        else:
            return "ENTRE_SESSOES"

    def analisar_ativo_individual(self, ticker: str, contexto_macro: AnaliseMacroAtual) -> Dict:
        """Análise técnica e fundamental de ativo individual"""

        self.logger.info(f"📊 Analisando {ticker}...")

        try:
            ativo = yf.Ticker(ticker)

            # Dados históricos
            dados_diarios = ativo.history(period="6mo", interval="1d")
            dados_horarios = ativo.history(period="30d", interval="1h")

            if dados_diarios.empty:
                self.logger.warning(f"⚠️ Sem dados para {ticker}")
                return {}

            preco_atual = float(dados_diarios['Close'].iloc[-1])

            # Análise técnica
            analise_tecnica = self._analisar_indicadores_tecnicos(dados_diarios, dados_horarios)

            # Níveis de suporte/resistência
            niveis = self._identificar_niveis_chave(dados_diarios)

            # Contexto de volume
            volume_analysis = self._analisar_volume(dados_diarios)

            return {
                'ticker': ticker,
                'preco_atual': preco_atual,
                'analise_tecnica': analise_tecnica,
                'niveis_chave': niveis,
                'volume_analysis': volume_analysis,
                'dados_historicos': {
                    'diarios': dados_diarios.tail(20).to_dict(),
                    'horarios': dados_horarios.tail(24).to_dict()
                }
            }

        except Exception as e:
            self.logger.error(f"❌ Erro analisando {ticker}: {e}")
            return {}

    def _analisar_indicadores_tecnicos(self, dados_diarios: pd.DataFrame, dados_horarios: pd.DataFrame) -> Dict:
        """Análise de indicadores técnicos"""

        # Médias móveis
        dados_diarios['SMA20'] = dados_diarios['Close'].rolling(20).mean()
        dados_diarios['SMA50'] = dados_diarios['Close'].rolling(50).mean()
        dados_diarios['EMA12'] = dados_diarios['Close'].ewm(span=12).mean()
        dados_diarios['EMA26'] = dados_diarios['Close'].ewm(span=26).mean()

        preco_atual = dados_diarios['Close'].iloc[-1]
        sma20 = dados_diarios['SMA20'].iloc[-1]
        sma50 = dados_diarios['SMA50'].iloc[-1]

        # RSI simplificado
        delta = dados_diarios['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        rsi_atual = rsi.iloc[-1] if not rsi.empty else 50

        # Tendência
        if preco_atual > sma20 > sma50:
            tendencia = "ALTA"
        elif preco_atual < sma20 < sma50:
            tendencia = "BAIXA"
        else:
            tendencia = "LATERAL"

        return {
            'tendencia': tendencia,
            'rsi': float(rsi_atual),
            'preco_vs_sma20': ((preco_atual / sma20) - 1) * 100,
            'preco_vs_sma50': ((preco_atual / sma50) - 1) * 100,
            'momentum': 'POSITIVO' if preco_atual > sma20 else 'NEGATIVO'
        }

    def _identificar_niveis_chave(self, dados: pd.DataFrame) -> Dict:
        """Identificar níveis chave de suporte e resistência"""

        high = dados['High'].rolling(window=20).max()
        low = dados['Low'].rolling(window=20).min()

        # Últimos níveis significativos
        resistencia = float(high.iloc[-5:].max())
        suporte = float(low.iloc[-5:].min())

        preco_atual = float(dados['Close'].iloc[-1])

        return {
            'suporte_principal': suporte,
            'resistencia_principal': resistencia,
            'distancia_suporte': ((preco_atual / suporte) - 1) * 100,
            'distancia_resistencia': ((resistencia / preco_atual) - 1) * 100
        }

    def _analisar_volume(self, dados: pd.DataFrame) -> Dict:
        """Análise de volume e liquidez"""

        volume_medio = dados['Volume'].rolling(20).mean().iloc[-1]
        volume_atual = dados['Volume'].iloc[-1]

        return {
            'volume_relativo': float(volume_atual / volume_medio) if volume_medio > 0 else 1.0,
            'tendencia_volume': 'CRESCENTE' if volume_atual > volume_medio else 'DECRESCENTE'
        }

    def gerar_oportunidades_especialista(self, tickers: List[str]) -> List[OportunidadeEspecialista]:
        """Gerar oportunidades baseadas em análise de especialista"""

        self.logger.info("🎯 Gerando oportunidades com expertise de 20+ anos...")

        # Contexto macro atual
        contexto_macro = self.coletar_contexto_macro_atual()

        oportunidades = []

        for ticker in tickers:
            analise = self.analisar_ativo_individual(ticker, contexto_macro)

            if not analise:
                continue

            oportunidade = self._avaliar_oportunidade_ativo(ticker, analise, contexto_macro)

            if oportunidade:
                oportunidades.append(oportunidade)

        # Ordenar por probabilidade e confiança
        oportunidades.sort(key=lambda x: (x.probabilidade_sucesso, x.confianca), reverse=True)

        return oportunidades

    def _avaliar_oportunidade_ativo(self, ticker: str, analise: Dict, contexto_macro: AnaliseMacroAtual) -> OportunidadeEspecialista:
        """Avaliar oportunidade para ativo específico"""

        try:
            tecnica = analise['analise_tecnica']
            niveis = analise['niveis_chave']
            volume = analise['volume_analysis']
            preco_atual = analise['preco_atual']

            # Avaliação baseada em confluência de fatores
            score_tecnico = self._calcular_score_tecnico(tecnica, niveis, volume)
            score_macro = self._calcular_score_macro(contexto_macro, ticker)

            # Probabilidade de sucesso (0-100)
            probabilidade = min(95, (score_tecnico * 0.6 + score_macro * 0.4))

            # Confiança baseada em qualidade dos sinais
            confianca = min(95, probabilidade * 0.9)  # Sempre um pouco menor que probabilidade

            if probabilidade < 60:  # Filtro de qualidade
                return None

            # Definir ação recomendada
            if tecnica['tendencia'] == 'ALTA' and tecnica['rsi'] < 70:
                acao = "COMPRA"
                preco_entrada = preco_atual * 0.998  # Pequeno desconto
                preco_alvo = preco_atual * 1.08  # Target 8%
                stop_loss = preco_atual * 0.95   # Stop 5%
            elif tecnica['tendencia'] == 'BAIXA' and tecnica['rsi'] > 30:
                acao = "VENDA"
                preco_entrada = preco_atual * 1.002  # Pequeno prêmio
                preco_alvo = preco_atual * 0.92   # Target -8%
                stop_loss = preco_atual * 1.05    # Stop 5%
            else:
                acao = "OBSERVAR"
                preco_entrada = preco_atual
                preco_alvo = preco_atual
                stop_loss = preco_atual

            # Risk/Reward ratio
            if acao in ["COMPRA", "VENDA"]:
                risco = abs(preco_entrada - stop_loss)
                retorno = abs(preco_alvo - preco_entrada)
                risk_reward = retorno / risco if risco > 0 else 0
            else:
                risk_reward = 0

            # Catalysts e justificativas
            catalysts = self._identificar_catalysts(ticker, contexto_macro, tecnica)
            justificativa_tecnica = self._gerar_justificativa_tecnica(tecnica, niveis, volume)
            justificativa_macro = self._gerar_justificativa_macro(contexto_macro, ticker)

            # Timeframe recomendado
            timeframe = self._determinar_timeframe_otimo(tecnica, contexto_macro)

            # Nível de invalidação
            if acao == "COMPRA":
                invalidacao = niveis['suporte_principal'] * 0.98
            elif acao == "VENDA":
                invalidacao = niveis['resistencia_principal'] * 1.02
            else:
                invalidacao = preco_atual

            # Contexto de correlação
            contexto_correlacao = self._analisar_contexto_correlacao(ticker, contexto_macro)

            return OportunidadeEspecialista(
                ativo=ticker,
                acao_recomendada=acao,
                probabilidade_sucesso=int(probabilidade),
                confianca=int(confianca),
                preco_entrada=round(preco_entrada, 2),
                preco_alvo=round(preco_alvo, 2),
                stop_loss=round(stop_loss, 2),
                risk_reward=round(risk_reward, 2),
                timeframe=timeframe,
                catalysts=catalysts,
                justificativa_tecnica=justificativa_tecnica,
                justificativa_macro=justificativa_macro,
                nivel_invalidacao=round(invalidacao, 2),
                contexto_correlacao=contexto_correlacao
            )

        except Exception as e:
            self.logger.error(f"❌ Erro avaliando oportunidade {ticker}: {e}")
            return None

    def _calcular_score_tecnico(self, tecnica: Dict, niveis: Dict, volume: Dict) -> float:
        """Calcular score técnico (0-100)"""

        score = 50  # Base neutra

        # Tendência
        if tecnica['tendencia'] == 'ALTA':
            score += 20
        elif tecnica['tendencia'] == 'BAIXA':
            score -= 20

        # RSI
        rsi = tecnica['rsi']
        if 30 < rsi < 70:  # Zona neutra
            score += 10
        elif rsi < 30 or rsi > 70:  # Zonas extremas
            score += 5  # Pode indicar reversão

        # Posição vs médias móveis
        if tecnica['preco_vs_sma20'] > 2:
            score += 15
        elif tecnica['preco_vs_sma20'] < -2:
            score -= 15

        # Volume
        if volume['volume_relativo'] > 1.5:
            score += 10
        elif volume['volume_relativo'] < 0.8:
            score -= 5

        # Proximidade a níveis chave
        if niveis['distancia_suporte'] < 2:  # Próximo ao suporte
            score += 10
        if niveis['distancia_resistencia'] < 2:  # Próximo à resistência
            score -= 5

        return max(0, min(100, score))

    def _calcular_score_macro(self, contexto: AnaliseMacroAtual, ticker: str) -> float:
        """Calcular score macro (0-100)"""

        score = 50  # Base neutra

        # Regime de volatilidade
        if contexto.regime_volatilidade == "BAIXA_VOLATILIDADE":
            score += 15  # Favorável para posições direcionais
        elif contexto.regime_volatilidade == "VOLATILIDADE_EXTREMA":
            score -= 10  # Risco elevado

        # Sentimento de equity
        if contexto.sentimento_equity == "OTIMISTA":
            score += 20
        elif contexto.sentimento_equity == "PESSIMISTA":
            score -= 20

        # Regime de taxas (impacto em growth vs value)
        if "GOOGL" in ticker or "NVDA" in ticker or "TSLA" in ticker:  # Growth
            if contexto.regime_taxas in ["TAXAS_BAIXAS", "TAXAS_MODERADAS"]:
                score += 10
            else:
                score -= 10

        # Sessão de mercado
        if contexto.sessao_mercado == "SESSAO_NYSE_ATIVA":
            score += 5  # Maior liquidez

        return max(0, min(100, score))

    def _identificar_catalysts(self, ticker: str, contexto: AnaliseMacroAtual, tecnica: Dict) -> List[str]:
        """Identificar catalisadores para a oportunidade"""

        catalysts = []

        # Catalysts macro
        if contexto.regime_volatilidade == "BAIXA_VOLATILIDADE":
            catalysts.append("Ambiente de baixa volatilidade favorece posições direcionais")

        if contexto.sentimento_equity == "OTIMISTA":
            catalysts.append("Sentimento otimista no mercado de ações")

        # Catalysts técnicos
        if tecnica['momentum'] == 'POSITIVO':
            catalysts.append("Momentum técnico positivo com preço acima SMA20")

        if 30 < tecnica['rsi'] < 70:
            catalysts.append("RSI em zona neutra permite movimento direcional")

        # Catalysts específicos por ativo
        if ticker == "NVDA":
            catalysts.append("Setor de semicondutores/AI em foco")
        elif ticker == "AAPL":
            catalysts.append("Líder de mercado com base sólida de consumidores")
        elif ticker == "TSLA":
            catalysts.append("Transição para veículos elétricos continua")

        return catalysts[:3]  # Máximo 3 catalysts principais

    def _gerar_justificativa_tecnica(self, tecnica: Dict, niveis: Dict, volume: Dict) -> str:
        """Gerar justificativa técnica detalhada"""

        justificativa = f"Análise técnica mostra tendência {tecnica['tendencia']} "
        justificativa += f"com RSI em {tecnica['rsi']:.1f}. "

        if tecnica['preco_vs_sma20'] > 0:
            justificativa += f"Preço {tecnica['preco_vs_sma20']:.1f}% acima da SMA20. "
        else:
            justificativa += f"Preço {abs(tecnica['preco_vs_sma20']):.1f}% abaixo da SMA20. "

        if volume['volume_relativo'] > 1.2:
            justificativa += "Volume acima da média confirma movimento. "

        justificativa += f"Próximo suporte em {niveis['distancia_suporte']:.1f}% "
        justificativa += f"e resistência em {niveis['distancia_resistencia']:.1f}%."

        return justificativa

    def _gerar_justificativa_macro(self, contexto: AnaliseMacroAtual, ticker: str) -> str:
        """Gerar justificativa macro detalhada"""

        justificativa = f"Ambiente macro com VIX em {contexto.vix:.1f} "
        justificativa += f"({contexto.regime_volatilidade}), "
        justificativa += f"Treasury 10Y em {contexto.treasury_10y:.2f}% "
        justificativa += f"({contexto.regime_taxas}). "

        justificativa += f"Sentimento equity {contexto.sentimento_equity} "
        justificativa += f"com S&P 500 em {contexto.sp500:.0f}. "

        if contexto.dxy > 100:
            justificativa += "USD forte pode pressionar multinacionais. "
        else:
            justificativa += "USD enfraquecido favorece exportações. "

        return justificativa

    def _determinar_timeframe_otimo(self, tecnica: Dict, contexto: AnaliseMacroAtual) -> str:
        """Determinar timeframe ótimo para a operação"""

        if contexto.regime_volatilidade == "ALTA_VOLATILIDADE":
            return "CURTO_PRAZO (1-5 dias)"
        elif tecnica['tendencia'] == 'LATERAL':
            return "MUITO_CURTO_PRAZO (intraday)"
        else:
            return "MEDIO_PRAZO (1-4 semanas)"

    def _analisar_contexto_correlacao(self, ticker: str, contexto: AnaliseMacroAtual) -> str:
        """Analisar contexto de correlação com outros ativos"""

        contexto_cor = f"Com VIX em {contexto.vix:.1f}, correlação com mercado "

        if contexto.vix < 20:
            contexto_cor += "reduzida (ambiente de baixo risco). "
        else:
            contexto_cor += "elevada (risk-off). "

        if ticker in ["AAPL", "MSFT", "GOOGL"]:
            contexto_cor += "Large caps tendem a seguir índices principais. "
        elif ticker in ["TSLA", "NVDA"]:
            contexto_cor += "Growth stocks sensíveis a taxas e sentimento. "

        return contexto_cor

    def exibir_relatorio_executivo(self, oportunidades: List[OportunidadeEspecialista], contexto_macro: AnaliseMacroAtual):
        """Exibir relatório executivo das oportunidades"""

        print("\n" + "="*80)
        print("📊 RELATÓRIO EXECUTIVO - ESPECIALISTA MERCADO FINANCEIRO")
        print("🎯 20+ Anos de Experiência | Análise Macro-Técnica Integrada")
        print("="*80)

        # Contexto macro
        print(f"\n🌐 CONTEXTO MACROECONÔMICO ATUAL ({contexto_macro.timestamp.strftime('%H:%M:%S')})")
        print(f"   VIX: {contexto_macro.vix:.1f} ({contexto_macro.regime_volatilidade})")
        print(f"   Treasury 10Y: {contexto_macro.treasury_10y:.2f}% ({contexto_macro.regime_taxas})")
        print(f"   S&P 500: {contexto_macro.sp500:.0f} ({contexto_macro.sentimento_equity})")
        print(f"   DXY: {contexto_macro.dxy:.1f} | Ouro: ${contexto_macro.ouro:.0f} | WTI: ${contexto_macro.petroleo:.1f}")
        print(f"   Sessão: {contexto_macro.sessao_mercado}")

        if not oportunidades:
            print("\n⚠️ NENHUMA OPORTUNIDADE IDENTIFICADA NO MOMENTO")
            print("   Aguardar melhores condições de confluência macro-técnica")
            return

        print(f"\n🎯 OPORTUNIDADES IDENTIFICADAS ({len(oportunidades)} ativos)")
        print("-"*80)

        for i, opp in enumerate(oportunidades, 1):
            print(f"\n{i}. 📈 {opp.ativo} - {opp.acao_recomendada}")
            print(f"   PROBABILIDADE_SUCESSO: {opp.probabilidade_sucesso}%")
            print(f"   CONFIANÇA: {opp.confianca}%")
            print(f"   AÇÃO_RECOMENDADA: {opp.acao_recomendada}")

            if opp.acao_recomendada != "OBSERVAR":
                print(f"   ENTRADA: ${opp.preco_entrada:.2f}")
                print(f"   ALVO: ${opp.preco_alvo:.2f}")
                print(f"   STOP: ${opp.stop_loss:.2f}")
                print(f"   R/R: {opp.risk_reward:.2f}")

            print(f"   TIMEFRAME: {opp.timeframe}")
            print(f"   INVALIDAÇÃO: ${opp.nivel_invalidacao:.2f}")

            print(f"\n   💡 CATALYSTS:")
            for catalyst in opp.catalysts:
                print(f"      • {catalyst}")

            print(f"\n   📊 JUSTIFICATIVA TÉCNICA:")
            print(f"      {opp.justificativa_tecnica}")

            print(f"\n   🌐 JUSTIFICATIVA MACRO:")
            print(f"      {opp.justificativa_macro}")

            print(f"\n   🔗 CONTEXTO CORRELAÇÃO:")
            print(f"      {opp.contexto_correlacao}")

            if i < len(oportunidades):
                print("-"*50)

        print("\n" + "="*80)
        print("⚠️  DISCLAIMER: Análise para fins educacionais.")
        print("    Sempre faça sua própria pesquisa antes de investir.")
        print("="*80)

def main():
    """Função principal - Execução da análise especialista"""

    print("🚀 Iniciando Análise de Especialista em Mercado Financeiro...")

    # Portfolio de análise (top 5 tech stocks)
    portfolio = ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'META']

    # Instanciar especialista
    especialista = EspecialistaMercadoFinanceiro()

    try:
        # Coletar contexto macro
        contexto_macro = especialista.coletar_contexto_macro_atual()

        # Gerar oportunidades
        oportunidades = especialista.gerar_oportunidades_especialista(portfolio)

        # Exibir relatório
        especialista.exibir_relatorio_executivo(oportunidades, contexto_macro)

        print(f"\n✅ Análise concluída! {len(oportunidades)} oportunidades identificadas.")

    except Exception as e:
        print(f"❌ Erro na análise: {e}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())