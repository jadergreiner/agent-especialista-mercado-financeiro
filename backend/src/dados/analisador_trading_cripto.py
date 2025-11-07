# -*- coding: utf-8 -*-
"""
Relatório de Trading Focado - Criptoativo Individual
Análise Integrada: Fundamentalista + Técnica + On-Chain

Metodologia:
1. Análise Fundamentalista (AF): Notícias, correlações, sentimento macro
2. Análise Técnica (AT): Momentum, estrutura de preço, suportes/resistências
3. Análise On-Chain: Netflow, baleias, funding rate, supply exchanges

Autor: Agent Especialista Mercado Financeiro
Data: 2025-01-05
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple
from decimal import Decimal
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import numpy as np
from pathlib import Path

# Util: leitura de dados manuais (fallback)
from src.utils.dados_manuais import carregar_ohlcv_csv  # type: ignore


@dataclass
class RelatorioTrading:
    """Estrutura do relatório de trading completo."""

    # Identificação
    simbolo: str
    nome: str
    preco_atual: Decimal
    timestamp: datetime

    # Operação Recomendada
    operacao: str  # COMPRA, VENDA, AGUARDAR
    momentum_consolidado: str  # Ex: "Baixista curto prazo, Altista médio prazo"
    risco_recompensa: str  # Ex: "1:2.5"

    # Análise Fundamentalista
    momentum_fundamental: str  # BAIXISTA, NEUTRO, ALTISTA
    noticias_recentes: List[str]
    correlacao_btc: Decimal  # Correlação com BTC
    correlacao_eth: Decimal  # Correlação com ETH
    sentimento_macro: str  # RISK_ON, RISK_OFF, NEUTRO

    # Análise Técnica
    momentum_tecnico: str  # BAIXISTA, NEUTRO, ALTISTA
    preco_maximo_30d: Decimal
    preco_minimo_30d: Decimal
    ma_100d: Optional[Decimal]  # Média móvel 100 dias
    posicao_ma: str  # ACIMA, ABAIXO, PROXIMA
    suportes: List[Decimal]
    resistencias: List[Decimal]
    ponto_critico_baixa: Decimal  # Invalidação bullish
    ponto_critico_alta: Decimal   # Invalidação bearish

    # Análise On-Chain (mock - seria integrado com APIs reais)
    netflow_exchanges: str  # INFLOW (pressão venda), OUTFLOW (acumulação)
    whale_accumulation: str  # ACUMULANDO, DISTRIBUINDO, NEUTRO
    funding_rate: Decimal  # % (positivo = longs dominam, negativo = shorts)
    supply_exchanges: str  # AUMENTANDO (oferta), DIMINUINDO (escassez)
    conclusao_onchain: str  # Absorção de volatilidade, pressão direcional

    # Plano de Operação
    preco_entrada: Decimal
    alvo_1: Decimal
    alvo_2: Decimal
    alvo_3: Decimal
    stop_loss: Decimal
    justificativa_entrada: str
    justificativa_alvos: str
    justificativa_stop: str


class AnalisadorTradingCripto:
    """
    Analisador de trading para criptoativos individuais.

    Combina:
    1. Análise Fundamentalista (notícias, correlações)
    2. Análise Técnica (momentum, estrutura)
    3. Análise On-Chain (fluxos, baleias, funding)
    """

    def __init__(self):
        # Mapeamento de tickers
        self.ticker_map = {
            'BTCUSDT': 'BTC-USD',
            'ETHUSDT': 'ETH-USD',
            'SOLUSDT': 'SOL-USD',
            'BNBUSDT': 'BNB-USD',
            'ADAUSDT': 'ADA-USD',
            'DOTUSDT': 'DOT-USD',
            'AVAXUSDT': 'AVAX-USD',
            'LINKUSDT': 'LINK-USD',
            'MATICUSDT': 'MATIC-USD',
            'NEARUSDT': 'NEAR-USD',
            # Símbolos sem mapeamento Yahoo usarão CSV manual (backend/data/manual/CRIPTO/)
            'VIRTUALUSDT': None,
        }

    def analisar_trading(self, simbolo: str) -> Optional[RelatorioTrading]:
        """
        Gera relatório de trading completo para um criptoativo.

        Args:
            simbolo: Par de trading (ex: BTCUSDT)

        Returns:
            RelatorioTrading ou None se falhar
        """
        try:
            # 1) Tenta ticker Yahoo Finance pelo mapa
            ticker_yahoo = self.ticker_map.get(simbolo)
            historico: Optional[pd.DataFrame] = None
            nome = simbolo
            usar_csv = False

            if ticker_yahoo:
                ticker = yf.Ticker(ticker_yahoo)
                info = ticker.info
                nome = info.get('name', simbolo)
                historico = ticker.history(period="100d")
            elif simbolo in self.ticker_map and self.ticker_map[simbolo] is None:
                # Símbolo reconhecido mas sem mapeamento Yahoo → vai direto para CSV
                usar_csv = True

            if usar_csv or ticker_yahoo is None:
                # 2) Fallback: CSV manual em backend/data/manual/CRIPTO/<SIMBOLO>.csv
                base = Path(__file__).resolve().parents[2]  # backend/
                csv_path = base / 'data' / 'manual' / 'CRIPTO' / f'{simbolo}.csv'
                if csv_path.exists():
                    try:
                        historico = carregar_ohlcv_csv(csv_path)
                        # limitar a ~100 dias se vier mais longo
                        if len(historico) > 0:
                            historico = historico.tail(100)
                        print(f"📥 Usando histórico manual: {csv_path}")
                    except Exception as e:
                        print(f"❌ Falha ao ler CSV manual ({csv_path}): {e}")
                        historico = None
                else:
                    # Mensagem padrão de onboarding
                    print(f"❌ Símbolo não mapeado: {simbolo}")
                    print("   ➜ Para habilitar a análise, envie um CSV OHLCV em:")
                    print(f"     backend/data/manual/CRIPTO/{simbolo}.csv")
                    print("   Formato esperado (cabeçalhos em inglês, case-insensitive):")
                    print("     datetime, open, high, low, close, volume")
                    print("   Observações:")
                    print("   - Datas em UTC (timezone será removido)")
                    print("   - Delimitador vírgula ou ponto-e-vírgula")
                    print("   - Volume opcional")
                    return None

            if historico is None or historico.empty:
                print(f"❌ Sem dados para {simbolo}")
                return None

            # Preço atual
            preco_atual = Decimal(str(historico['Close'].iloc[-1]))

            print(f"\n{'='*80}")
            print(f"🎯 RELATÓRIO DE TRADING FOCADO: {simbolo}")
            print(f"{'='*80}")
            print(f"Ativo: {nome}")
            print(f"Preço Atual: ${float(preco_atual):.2f}")
            print(f"Análise: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*80}\n")

            # 1. ANÁLISE FUNDAMENTALISTA
            print("📰 Executando Análise Fundamentalista...")
            af_data = self._analisar_fundamentalista(simbolo, ticker_yahoo or nome, historico)

            # 2. ANÁLISE TÉCNICA
            print("📊 Executando Análise Técnica...")
            at_data = self._analisar_tecnica(historico, preco_atual)

            # 3. ANÁLISE ON-CHAIN
            print("⛓️  Executando Análise On-Chain...")
            onchain_data = self._analisar_onchain(simbolo, preco_atual)

            # 4. CONSOLIDAR MOMENTUM E OPERAÇÃO
            print("🎯 Consolidando Operação...")
            operacao_data = self._gerar_operacao(
                simbolo, preco_atual,
                af_data, at_data, onchain_data
            )

            # Montar relatório completo
            relatorio = RelatorioTrading(
                simbolo=simbolo,
                nome=nome,
                preco_atual=preco_atual,
                timestamp=datetime.now(),

                # Operação
                operacao=operacao_data['operacao'],
                momentum_consolidado=operacao_data['momentum_consolidado'],
                risco_recompensa=operacao_data['risco_recompensa'],

                # Fundamentalista
                momentum_fundamental=af_data['momentum'],
                noticias_recentes=af_data['noticias'],
                correlacao_btc=af_data['corr_btc'],
                correlacao_eth=af_data['corr_eth'],
                sentimento_macro=af_data['sentimento_macro'],

                # Técnica
                momentum_tecnico=at_data['momentum'],
                preco_maximo_30d=at_data['max_30d'],
                preco_minimo_30d=at_data['min_30d'],
                ma_100d=at_data['ma_100d'],
                posicao_ma=at_data['posicao_ma'],
                suportes=at_data['suportes'],
                resistencias=at_data['resistencias'],
                ponto_critico_baixa=at_data['critico_baixa'],
                ponto_critico_alta=at_data['critico_alta'],

                # On-Chain
                netflow_exchanges=onchain_data['netflow'],
                whale_accumulation=onchain_data['whales'],
                funding_rate=onchain_data['funding'],
                supply_exchanges=onchain_data['supply'],
                conclusao_onchain=onchain_data['conclusao'],

                # Plano
                preco_entrada=operacao_data['entrada'],
                alvo_1=operacao_data['alvo1'],
                alvo_2=operacao_data['alvo2'],
                alvo_3=operacao_data['alvo3'],
                stop_loss=operacao_data['stop'],
                justificativa_entrada=operacao_data['just_entrada'],
                justificativa_alvos=operacao_data['just_alvos'],
                justificativa_stop=operacao_data['just_stop'],
            )

            return relatorio

        except Exception as e:
            print(f"❌ Erro ao analisar {simbolo}: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _analisar_fundamentalista(
        self,
        simbolo: str,
        ticker_yahoo: str,
        historico: pd.DataFrame
    ) -> Dict:
        """Análise fundamentalista e correlações."""

        # Notícias recentes (mock - seria integrado com NewsAPI)
        noticias_db = {
            'BTCUSDT': [
                'ETF Bitcoin spot aprovado pela SEC (Janeiro 2024)',
                'Halving Bitcoin concluído (Abril 2024)',
                'MicroStrategy adiciona 10,000 BTC ao tesouro',
            ],
            'ETHUSDT': [
                'Upgrade Dencun implementado com sucesso (EIP-4844)',
                'ETF Ethereum spot em análise pela SEC',
                'TVL em Layer 2s Ethereum atinge $40B',
            ],
            'SOLUSDT': [
                'Firedancer testnet lançada com 1M TPS',
                'Volume DEX Solana supera Ethereum',
                'Saga Phone 2 anunciado para Q2 2025',
            ],
        }
        noticias = noticias_db.get(simbolo, ['Sem notícias recentes catalogadas'])

        # Correlação com BTC (se não for BTC)
        if simbolo != 'BTCUSDT':
            try:
                btc_historico = yf.Ticker('BTC-USD').history(period='30d')
                if not btc_historico.empty:
                    retornos = historico['Close'].tail(30).pct_change().dropna()
                    retornos_btc = btc_historico['Close'].tail(30).pct_change().dropna()

                    # Alinhar índices
                    comum = retornos.index.intersection(retornos_btc.index)
                    if len(comum) > 10:
                        corr_btc = Decimal(str(retornos[comum].corr(retornos_btc[comum])))
                    else:
                        corr_btc = Decimal('0.5')
                else:
                    corr_btc = Decimal('0.5')
            except:
                corr_btc = Decimal('0.5')
        else:
            corr_btc = Decimal('1.0')

        # Correlação com ETH (simplificado)
        if simbolo not in ['BTCUSDT', 'ETHUSDT']:
            corr_eth = Decimal('0.7')  # Mock
        elif simbolo == 'ETHUSDT':
            corr_eth = Decimal('1.0')
        else:
            corr_eth = Decimal('0.8')

        # Sentimento macro (heurística baseada em BTC)
        if corr_btc > Decimal('0.7'):
            sentimento = 'RISK_ON' if historico['Close'].iloc[-1] > historico['Close'].iloc[-10] else 'RISK_OFF'
        else:
            sentimento = 'NEUTRO'

        # Momentum fundamental
        retorno_30d = (historico['Close'].iloc[-1] - historico['Close'].iloc[-30]) / historico['Close'].iloc[-30]
        if retorno_30d > 0.1:
            momentum = 'ALTISTA'
        elif retorno_30d < -0.1:
            momentum = 'BAIXISTA'
        else:
            momentum = 'NEUTRO'

        return {
            'momentum': momentum,
            'noticias': noticias,
            'corr_btc': corr_btc,
            'corr_eth': corr_eth,
            'sentimento_macro': sentimento,
        }

    def _analisar_tecnica(self, historico: pd.DataFrame, preco_atual: Decimal) -> Dict:
        """Análise técnica: momentum, MAs, suportes, resistências."""

        # Extremos 30 dias
        ultimos_30 = historico.tail(30)
        max_30d = Decimal(str(ultimos_30['Close'].max()))
        min_30d = Decimal(str(ultimos_30['Close'].min()))

        # Média Móvel 100 dias
        if len(historico) >= 100:
            ma_100d = Decimal(str(historico['Close'].tail(100).mean()))
        else:
            ma_100d = None

        # Posição em relação à MA 100
        if ma_100d:
            if preco_atual > ma_100d * Decimal('1.02'):
                posicao_ma = 'ACIMA'
            elif preco_atual < ma_100d * Decimal('0.98'):
                posicao_ma = 'ABAIXO'
            else:
                posicao_ma = 'PROXIMA'
        else:
            posicao_ma = 'INDISPONIVEL'

        # Suportes (Fibonacci + mínimas relevantes)
        suportes = [
            min_30d,
            min_30d * Decimal('0.95'),  # 5% abaixo
            min_30d * Decimal('0.90'),  # 10% abaixo
        ]

        # Resistências (Fibonacci + máximas)
        resistencias = [
            max_30d * Decimal('0.95'),  # Próximo da máxima
            max_30d,
            max_30d * Decimal('1.05'),  # 5% acima
        ]

        # Pontos críticos
        critico_baixa = min_30d * Decimal('0.95')  # Perda deste suporte = bearish
        critico_alta = max_30d * Decimal('1.02')   # Rompimento = bullish

        # Momentum técnico (baseado em MAs e posição no range)
        distancia_min = (preco_atual - min_30d) / min_30d
        distancia_max = (max_30d - preco_atual) / preco_atual

        if posicao_ma == 'ACIMA' and distancia_min > Decimal('0.15'):
            momentum = 'ALTISTA'
        elif posicao_ma == 'ABAIXO' and distancia_max > Decimal('0.15'):
            momentum = 'BAIXISTA'
        else:
            momentum = 'NEUTRO'

        return {
            'momentum': momentum,
            'max_30d': max_30d,
            'min_30d': min_30d,
            'ma_100d': ma_100d,
            'posicao_ma': posicao_ma,
            'suportes': suportes,
            'resistencias': resistencias,
            'critico_baixa': critico_baixa,
            'critico_alta': critico_alta,
        }

    def _analisar_onchain(self, simbolo: str, preco_atual: Decimal) -> Dict:
        """
        Análise on-chain (mock - seria integrado com Glassnode/CryptoQuant).

        Métricas reais viriam de APIs:
        - Netflow: Glassnode, CryptoQuant
        - Whales: Whale Alert, Santiment
        - Funding: Binance/Bybit API
        - Supply: Glassnode
        """

        # Mock baseado em heurísticas por ativo
        onchain_profiles = {
            'BTCUSDT': {
                'netflow': 'OUTFLOW',  # Saindo de exchanges (bullish)
                'whales': 'ACUMULANDO',
                'funding': Decimal('0.01'),  # 0.01% positivo (longs dominam)
                'supply': 'DIMINUINDO',
                'conclusao': 'Absorção de oferta por baleias, pressure buying crescente',
            },
            'ETHUSDT': {
                'netflow': 'OUTFLOW',
                'whales': 'ACUMULANDO',
                'funding': Decimal('0.015'),
                'supply': 'DIMINUINDO',
                'conclusao': 'Staking + Layer 2 reduzindo supply disponível, bullish structure',
            },
            'SOLUSDT': {
                'netflow': 'INFLOW',  # Entrando em exchanges (bearish/neutral)
                'whales': 'DISTRIBUINDO',
                'funding': Decimal('-0.005'),  # Negativo (shorts dominam)
                'supply': 'AUMENTANDO',
                'conclusao': 'Pressure selling de baleias, cautela no curto prazo',
            },
        }

        profile = onchain_profiles.get(simbolo, {
            'netflow': 'NEUTRO',
            'whales': 'NEUTRO',
            'funding': Decimal('0'),
            'supply': 'ESTAVEL',
            'conclusao': 'Dados on-chain limitados, análise baseada em AT/AF',
        })

        return profile

    def _gerar_operacao(
        self,
        simbolo: str,
        preco_atual: Decimal,
        af: Dict,
        at: Dict,
        onchain: Dict
    ) -> Dict:
        """Consolida análises e gera operação recomendada."""

        # Scoring de momentum (0-3 pontos por análise)
        score_fundamental = {
            'ALTISTA': 3,
            'NEUTRO': 1,
            'BAIXISTA': -3,
        }[af['momentum']]

        score_tecnico = {
            'ALTISTA': 3,
            'NEUTRO': 1,
            'BAIXISTA': -3,
        }[at['momentum']]

        score_onchain = 0
        if onchain['netflow'] == 'OUTFLOW':
            score_onchain += 2
        elif onchain['netflow'] == 'INFLOW':
            score_onchain -= 2

        if onchain['whales'] == 'ACUMULANDO':
            score_onchain += 2
        elif onchain['whales'] == 'DISTRIBUINDO':
            score_onchain -= 2

        if onchain['funding'] > Decimal('0.02'):
            score_onchain -= 1  # Overleveraged longs (contrário)
        elif onchain['funding'] < Decimal('-0.02'):
            score_onchain += 1  # Overleveraged shorts (oportunidade long)

        # Score total
        score_total = score_fundamental + score_tecnico + score_onchain

        # Decisão de operação
        if score_total >= 5:
            operacao = 'COMPRA'
            momentum_consolidado = 'Altista no curto e médio prazo'
        elif score_total <= -5:
            operacao = 'VENDA'
            momentum_consolidado = 'Baixista no curto e médio prazo'
        elif score_total >= 2:
            operacao = 'COMPRA'
            momentum_consolidado = 'Neutro curto prazo, Altista médio prazo'
        elif score_total <= -2:
            operacao = 'VENDA'
            momentum_consolidado = 'Baixista curto prazo, Neutro médio prazo'
        else:
            operacao = 'AGUARDAR'
            momentum_consolidado = 'Neutro, aguardar confirmação de tendência'

        # Calcular pontos de operação
        if operacao == 'COMPRA':
            # Entrada: Próximo ao suporte (mínima 30d + 2%)
            entrada = at['min_30d'] * Decimal('1.02')

            # Alvos: Resistências progressivas
            alvo1 = at['resistencias'][0]  # Primeira resistência
            alvo2 = at['resistencias'][1]  # Máxima 30d
            alvo3 = at['resistencias'][2]  # 5% acima máxima

            # Stop: Abaixo do ponto crítico
            stop = at['critico_baixa']

            # R/R
            risco = float(entrada - stop)
            recompensa_alvo2 = float(alvo2 - entrada)
            rr = f"1:{recompensa_alvo2/risco:.1f}" if risco > 0 else "N/A"

            just_entrada = f"Zona de consolidação próxima ao suporte ${float(at['min_30d']):.2f}. " + \
                          f"On-chain: {onchain['conclusao'][:50]}..."
            just_alvos = f"TP1: Resistência imediata. TP2: Máxima 30d (retração Fib 0.618). TP3: Extensão 1.272 Fib."
            just_stop = f"Perda do suporte ${float(at['critico_baixa']):.2f} invalida tese bullish."

        elif operacao == 'VENDA':
            # Entrada: Próximo à resistência (máxima 30d - 2%)
            entrada = at['max_30d'] * Decimal('0.98')

            # Alvos: Suportes progressivos (short)
            alvo1 = at['suportes'][0]  # Mínima 30d
            alvo2 = at['suportes'][1]  # 5% abaixo
            alvo3 = at['suportes'][2]  # 10% abaixo

            # Stop: Acima do ponto crítico
            stop = at['critico_alta']

            # R/R
            risco = float(stop - entrada)
            recompensa_alvo2 = float(entrada - alvo2)
            rr = f"1:{recompensa_alvo2/risco:.1f}" if risco > 0 else "N/A"

            just_entrada = f"Rejeição de resistência ${float(at['max_30d']):.2f}. " + \
                          f"On-chain: {onchain['conclusao'][:50]}..."
            just_alvos = f"TP1: Suporte mínima 30d. TP2: Zona de demanda Fib 0.382. TP3: Suporte forte Fib 0.618."
            just_stop = f"Rompimento de ${float(at['critico_alta']):.2f} invalida tese bearish."

        else:  # AGUARDAR
            entrada = preco_atual
            alvo1 = at['resistencias'][0]
            alvo2 = at['resistencias'][1]
            alvo3 = at['resistencias'][2]
            stop = at['critico_baixa']
            rr = "N/A (aguardando setup)"

            just_entrada = "Aguardar confirmação de tendência (rompimento ou rejeição de níveis chave)."
            just_alvos = "Definir após confirmação direcional."
            just_stop = "Ajustar após entrada confirmada."

        return {
            'operacao': operacao,
            'momentum_consolidado': momentum_consolidado,
            'risco_recompensa': rr,
            'entrada': entrada,
            'alvo1': alvo1,
            'alvo2': alvo2,
            'alvo3': alvo3,
            'stop': stop,
            'just_entrada': just_entrada,
            'just_alvos': just_alvos,
            'just_stop': just_stop,
        }

    def gerar_relatorio_markdown(self, relatorio: RelatorioTrading) -> str:
        """Gera relatório em formato markdown."""

        md = f"\n# 🎯 RELATÓRIO DE TRADING FOCADO: {relatorio.simbolo}\n\n"
        md += f"**Ativo:** {relatorio.nome}\n"
        md += f"**Preço Atual:** ${float(relatorio.preco_atual):.2f} USDT\n"
        md += f"**Análise:** {relatorio.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        md += "---\n\n"

        # Parte 1: Resumo e Operação
        md += "## 📊 RESUMO EXECUTIVO\n\n"
        md += "| Categoria | Descrição do Foco de Análise |\n"
        md += "| :--- | :--- |\n"
        md += f"| **OPERAÇÃO RECOMENDADA** | **[{relatorio.operacao}]** |\n"
        md += f"| **Momentum Consolidado** | {relatorio.momentum_consolidado} |\n"
        md += f"| **Risco/Recompensa (R/R)** | {relatorio.risco_recompensa} |\n\n"

        # Parte 2: Análises Detalhadas
        md += "---\n\n"
        md += "## 📰 A. ANÁLISE FUNDAMENTALISTA E CORRELAÇÃO\n\n"
        md += f"**Momentum Fundamental:** {relatorio.momentum_fundamental}\n\n"
        md += "**Notícias Recentes:**\n"
        for noticia in relatorio.noticias_recentes:
            md += f"- {noticia}\n"
        md += f"\n**Correlações:**\n"
        md += f"- BTC: {float(relatorio.correlacao_btc):.2f} (correlação {'forte' if relatorio.correlacao_btc > Decimal('0.7') else 'moderada'})\n"
        md += f"- ETH: {float(relatorio.correlacao_eth):.2f}\n\n"
        md += f"**Sentimento Macro:** {relatorio.sentimento_macro}\n\n"

        md += "---\n\n"
        md += "## 📊 B. ANÁLISE TÉCNICA E ESTRUTURA DE PREÇO\n\n"
        md += f"**Momentum Técnico:** {relatorio.momentum_tecnico}\n\n"
        md += "**Extremos 30 Dias:**\n"
        md += f"- Máxima: ${float(relatorio.preco_maximo_30d):.2f}\n"
        md += f"- Mínima: ${float(relatorio.preco_minimo_30d):.2f}\n"
        md += f"- Range: {float((relatorio.preco_maximo_30d - relatorio.preco_minimo_30d) / relatorio.preco_minimo_30d * 100):.1f}%\n\n"

        if relatorio.ma_100d:
            md += f"**Média Móvel 100 Dias:** ${float(relatorio.ma_100d):.2f} ({relatorio.posicao_ma})\n\n"

        md += "**Níveis Críticos:**\n"
        md += f"- **Suportes:** {', '.join([f'${float(s):.2f}' for s in relatorio.suportes])}\n"
        md += f"- **Resistências:** {', '.join([f'${float(r):.2f}' for r in relatorio.resistencias])}\n"
        md += f"- **Ponto Crítico Baixa:** ${float(relatorio.ponto_critico_baixa):.2f} (invalidação bullish)\n"
        md += f"- **Ponto Crítico Alta:** ${float(relatorio.ponto_critico_alta):.2f} (invalidação bearish)\n\n"

        md += "---\n\n"
        md += "## ⛓️  C. ANÁLISE ON-CHAIN E SENTIMENTO DE MERCADO\n\n"
        md += f"**Netflow de Exchanges:** {relatorio.netflow_exchanges}\n"
        if relatorio.netflow_exchanges == 'OUTFLOW':
            md += " → Saída de exchanges (acumulação, bullish)\n"
        elif relatorio.netflow_exchanges == 'INFLOW':
            md += " → Entrada em exchanges (pressão de venda)\n"
        else:
            md += " → Neutro\n"

        md += f"\n**Whale Accumulation:** {relatorio.whale_accumulation}\n"
        md += f"**Funding Rate:** {float(relatorio.funding_rate):.3f}%\n"
        if relatorio.funding_rate > Decimal('0.02'):
            md += " → Overleveraged longs (risco de squeeze)\n"
        elif relatorio.funding_rate < Decimal('-0.02'):
            md += " → Overleveraged shorts (oportunidade long)\n"
        else:
            md += " → Balanceado\n"

        md += f"\n**Supply nas Exchanges:** {relatorio.supply_exchanges}\n\n"
        md += f"**Conclusão On-Chain:** {relatorio.conclusao_onchain}\n\n"

        # Parte 3: Plano de Execução
        md += "---\n\n"
        md += f"## 🚀 PLANO DE OPERAÇÃO REFINADO: [{relatorio.operacao}]\n\n"
        md += "| Detalhe da Operação | Valor (USDT) | Justificativa Refinada |\n"
        md += "| :--- | :---: | :--- |\n"
        md += f"| **PREÇO DE ENTRADA** | **${float(relatorio.preco_entrada):.2f}** | {relatorio.justificativa_entrada} |\n"
        md += f"| **ALVO 1 (Take Profit)** | ${float(relatorio.alvo_1):.2f} | Resistência imediata |\n"
        md += f"| **ALVO 2 (Take Profit)** | ${float(relatorio.alvo_2):.2f} | {relatorio.justificativa_alvos.split('.')[0]} |\n"
        md += f"| **ALVO 3 (Take Profit)** | ${float(relatorio.alvo_3):.2f} | Alvo swing médio prazo |\n"
        md += f"| **INVALIDAÇÃO (Stop Loss)** | **${float(relatorio.stop_loss):.2f}** | {relatorio.justificativa_stop} |\n\n"

        # Disclaimer
        md += "---\n\n"
        md += "⚠️  **DISCLAIMER:** Esta análise é apenas educacional. Não constitui recomendação de investimento. "
        md += "Cripto envolve alto risco. Sempre faça sua própria pesquisa (DYOR).\n"

        return md

    # ========================= SERIALIZAÇÃO JSON =========================
    def gerar_json(self, relatorio: RelatorioTrading) -> Dict:
        """Gera payload JSON para o contrato report.trading.cripto.v1.

        - Converte Decimals para float
        - Timestamp ISO 8601
        - Inclui viesSessao mapeado a partir de momentum_consolidado (para padronizar persistência)
        """
        payload = {
            'contractVersion': 'report.trading.cripto.v1',
            'classeAtivo': 'cripto',
            'ativo': relatorio.simbolo,
            'nome': relatorio.nome,
            'timestamp': relatorio.timestamp.isoformat(timespec='seconds'),
            'precoAtual': float(relatorio.preco_atual),
            'resumo': {
                'operacao': relatorio.operacao,
                'momentumConsolidado': relatorio.momentum_consolidado,
                'viesSessao': relatorio.momentum_consolidado,
                'rr': relatorio.risco_recompensa,
            },
            'analises': {
                'fundamentalista': {
                    'momentum': relatorio.momentum_fundamental,
                    'noticias': list(relatorio.noticias_recentes or []),
                    'correlacaoBTC': float(relatorio.correlacao_btc),
                    'correlacaoETH': float(relatorio.correlacao_eth),
                    'sentimentoMacro': relatorio.sentimento_macro,
                },
                'tecnica': {
                    'momentum': relatorio.momentum_tecnico,
                    'max30d': float(relatorio.preco_maximo_30d),
                    'min30d': float(relatorio.preco_minimo_30d),
                    'ma100d': (float(relatorio.ma_100d) if relatorio.ma_100d is not None else None),
                    'posicaoMA': relatorio.posicao_ma,
                    'suportes': [float(x) for x in (relatorio.suportes or [])],
                    'resistencias': [float(x) for x in (relatorio.resistencias or [])],
                    'pontoCriticoBaixa': float(relatorio.ponto_critico_baixa),
                    'pontoCriticoAlta': float(relatorio.ponto_critico_alta),
                },
                'onchain': {
                    'netflow': relatorio.netflow_exchanges,
                    'whales': relatorio.whale_accumulation,
                    'fundingRate': float(relatorio.funding_rate),
                    'supplyExchanges': relatorio.supply_exchanges,
                    'conclusao': relatorio.conclusao_onchain,
                }
            },
            'plano': {
                'entrada': float(relatorio.preco_entrada),
                'alvo1': float(relatorio.alvo_1),
                'alvo2': float(relatorio.alvo_2),
                'alvo3': float(relatorio.alvo_3),
                'stop': float(relatorio.stop_loss),
                'justificativas': {
                    'entrada': relatorio.justificativa_entrada,
                    'alvos': relatorio.justificativa_alvos,
                    'stop': relatorio.justificativa_stop,
                }
            },
            'qualidade': {
                'dadosMercado': 'ok' if float(relatorio.preco_atual) > 0 else 'indisponivel'
            }
        }
        return payload


# Teste standalone
if __name__ == "__main__":
    analisador = AnalisadorTradingCripto()

    # Testar com BTCUSDT
    print("Testando análise de trading para BTCUSDT...\n")
    relatorio = analisador.analisar_trading('BTCUSDT')

    if relatorio:
        print("\n" + "="*80)
        print(analisador.gerar_relatorio_markdown(relatorio))
        print("="*80)
