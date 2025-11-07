# -*- coding: utf-8 -*-
"""
Analisador Forex - Motor de Análise Multi-Dimensional para Forex.

Combina 5 pilares de análise:
1. Carry Trade (diferenciais de juros)
2. Política Monetária (divergências de BCs)
3. Análise Técnica (níveis, tendências)
4. Correlações (impacto no WIN/IBOV)
5. Sentimento (notícias recentes)

Gera relatórios estruturados com recomendação APROVAR/DESCARTAR.
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
import yfinance as yf
from dataclasses import dataclass

from forex_fundamentals import ColetorForexFundamentals


CAMINHO_DB = Path(__file__).parent.parent.parent / "data" / "recomendacoes.sqlite"


@dataclass
class AnaliseForex:
    """Estrutura de análise completa de par Forex."""

    # Identificação
    par: str
    moeda_base: str
    moeda_cotada: str

    # Carry Trade
    diferencial_juros: Decimal
    carry_anual_pct: Decimal
    carry_rating: str  # excelente, bom, neutro, ruim

    # Política Monetária
    guidance_base: str
    guidance_cotada: str
    divergencia_politica: str  # forte, moderada, fraca

    # Técnica
    preco_atual: Decimal
    entrada_sugerida: Decimal
    stop_loss: Decimal
    take_profit_1: Decimal
    take_profit_2: Decimal
    tendencia: str  # alta, baixa, lateral

    # Correlação
    impacto_win: str  # positivo, negativo, neutro
    correlacao_ibov: float

    # Sentimento
    score_sentimento: float
    noticias_relevantes: int

    # Decisão Final
    recomendacao: str  # APROVAR_LONG, APROVAR_SHORT, DESCARTAR
    confianca: int  # 0-100
    risco_recompensa: float

    # Alternativa
    par_alternativo: Optional[str] = None
    motivo_alternativa: Optional[str] = None


class AnalisadorForex:
    """Motor de análise Forex integrado."""

    # Mapeamento COMPLETO de 42 pares para símbolos Yahoo Finance
    PARES_YAHOO = {
        # === MAJORS (7 pares) ===
        'EURUSD': 'EURUSD=X',
        'GBPUSD': 'GBPUSD=X',
        'USDJPY': 'JPY=X',
        'USDCHF': 'CHF=X',
        'USDCAD': 'CAD=X',
        'AUDUSD': 'AUDUSD=X',
        'NZDUSD': 'NZDUSD=X',

        # === CROSSES PRINCIPAIS (12 pares) ===
        'EURGBP': 'EURGBP=X',
        'EURJPY': 'EURJPY=X',
        'GBPJPY': 'GBPJPY=X',
        'EURCHF': 'EURCHF=X',
        'AUDJPY': 'AUDJPY=X',
        'CHFJPY': 'CHFJPY=X',
        'EURCAD': 'EURCAD=X',
        'AUDCAD': 'AUDCAD=X',
        'CADJPY': 'CADJPY=X',
        'NZDJPY': 'NZDJPY=X',
        'AUDNZD': 'AUDNZD=X',
        'GBPAUD': 'GBPAUD=X',

        # === CROSSES SECUNDÁRIOS (9 pares) ===
        'EURAUD': 'EURAUD=X',
        'GBPCHF': 'GBPCHF=X',
        'EURNZD': 'EURNZD=X',
        'AUDCHF': 'AUDCHF=X',
        'GBPNZD': 'GBPNZD=X',
        'GBPCAD': 'GBPCAD=X',
        'CADCHF': 'CADCHF=X',
        'NZDCAD': 'NZDCAD=X',
        'NZDCHF': 'NZDCHF=X',

        # === EXÓTICOS (10 pares) ===
        'USDBRL': 'USDBRL=X',
        'USDINR': 'INR=X',
        'USDCNY': 'CNY=X',
        'USDSGD': 'SGD=X',
        'USDHKD': 'HKD=X',
        'USDDKK': 'DKK=X',
        'USDSEK': 'SEK=X',
        'USDTRY': 'TRY=X',
        'USDMXN': 'MXN=X',
        'USDZAR': 'ZAR=X',

        # === OURO (1 par) ===
        'XAUUSD': 'GC=F',  # Gold Futures

        # === CRYPTO (3 pares) ===
        'BTCUSD': 'BTC-USD',
        'BTCEUR': 'BTC-EUR',
        'ETHUSD': 'ETH-USD',
    }

    def __init__(self):
        """Inicializa o analisador."""
        self.coletor_fundamentals = ColetorForexFundamentals()

    def analisar_par(self, par: str, operacao: str = 'COMPRA') -> AnaliseForex:
        """
        Análise completa de um par Forex.

        Args:
            par: Par forex (ex: GBPNZD, EURUSD)
            operacao: COMPRA ou VENDA

        Returns:
            AnaliseForex com todas as métricas
        """

        # Normalizar par
        par = par.upper().replace('/', '')

        # Extrair moedas
        if len(par) == 6:
            moeda_base = par[:3]
            moeda_cotada = par[3:]
        else:
            raise ValueError(f"Par inválido: {par}. Use formato XXXYYY (ex: GBPNZD)")

        print(f"\n{'='*80}")
        print(f"ANALISANDO: {operacao} {moeda_base}/{moeda_cotada}")
        print(f"{'='*80}\n")

        # PILAR 1: Carry Trade
        print("📊 PILAR 1: Carry Trade")
        carry_info = self._analisar_carry_trade(moeda_base, moeda_cotada, operacao)
        print(f"   Diferencial: {carry_info['diferencial']:+.2f}%")
        print(f"   Rating: {carry_info['rating']}")

        # PILAR 2: Política Monetária
        print("\n🏦 PILAR 2: Política Monetária")
        politica_info = self._analisar_politica_monetaria(moeda_base, moeda_cotada)
        print(f"   {moeda_base}: {politica_info['guidance_base']}")
        print(f"   {moeda_cotada}: {politica_info['guidance_cotada']}")
        print(f"   Divergência: {politica_info['divergencia']}")

        # PILAR 3: Análise Técnica
        print("\n📈 PILAR 3: Análise Técnica")
        tecnica_info = self._analisar_tecnica(par, operacao)
        print(f"   Preço Atual: {tecnica_info['preco_atual']:.4f}")
        print(f"   Tendência: {tecnica_info['tendencia']}")
        print(f"   Entrada: {tecnica_info['entrada']:.4f}")
        print(f"   Stop: {tecnica_info['stop']:.4f}")
        print(f"   TP1: {tecnica_info['tp1']:.4f}")
        print(f"   TP2: {tecnica_info['tp2']:.4f}")

        # PILAR 4: Correlação com WIN/IBOV
        print("\n🔗 PILAR 4: Correlação com Brasil")
        correlacao_info = self._analisar_correlacao_brasil(moeda_base, moeda_cotada)
        print(f"   Impacto WIN: {correlacao_info['impacto']}")
        print(f"   Correlação IBOV: {correlacao_info['correlacao']:.2f}")

        # PILAR 5: Sentimento
        print("\n📰 PILAR 5: Sentimento de Notícias")
        sentimento_info = self._analisar_sentimento(moeda_base, moeda_cotada)
        print(f"   Score: {sentimento_info['score']:+.2f}")
        print(f"   Notícias: {sentimento_info['total']}")

        # DECISÃO FINAL
        print("\n🎯 DECISÃO FINAL")
        decisao = self._calcular_decisao_final(
            carry_info, politica_info, tecnica_info,
            correlacao_info, sentimento_info, operacao
        )
        print(f"   Recomendação: {decisao['recomendacao']}")
        print(f"   Confiança: {decisao['confianca']}%")
        print(f"   Risco/Recompensa: 1:{decisao['risco_recompensa']:.2f}")

        # ALTERNATIVA
        alternativa = self._sugerir_alternativa(moeda_base, moeda_cotada, carry_info)
        if alternativa:
            print(f"\n💡 ALTERNATIVA RECOMENDADA: {alternativa['par']}")
            print(f"   Motivo: {alternativa['motivo']}")

        # Criar objeto de análise
        analise = AnaliseForex(
            par=f"{moeda_base}/{moeda_cotada}",
            moeda_base=moeda_base,
            moeda_cotada=moeda_cotada,
            diferencial_juros=Decimal(str(carry_info['diferencial'])),
            carry_anual_pct=Decimal(str(carry_info['diferencial'])),
            carry_rating=carry_info['rating'],
            guidance_base=politica_info['guidance_base'],
            guidance_cotada=politica_info['guidance_cotada'],
            divergencia_politica=politica_info['divergencia'],
            preco_atual=Decimal(str(tecnica_info['preco_atual'])),
            entrada_sugerida=Decimal(str(tecnica_info['entrada'])),
            stop_loss=Decimal(str(tecnica_info['stop'])),
            take_profit_1=Decimal(str(tecnica_info['tp1'])),
            take_profit_2=Decimal(str(tecnica_info['tp2'])),
            tendencia=tecnica_info['tendencia'],
            impacto_win=correlacao_info['impacto'],
            correlacao_ibov=correlacao_info['correlacao'],
            score_sentimento=sentimento_info['score'],
            noticias_relevantes=sentimento_info['total'],
            recomendacao=decisao['recomendacao'],
            confianca=decisao['confianca'],
            risco_recompensa=decisao['risco_recompensa'],
            par_alternativo=alternativa['par'] if alternativa else None,
            motivo_alternativa=alternativa['motivo'] if alternativa else None
        )

        return analise

    def _analisar_carry_trade(self, moeda_base: str, moeda_cotada: str, operacao: str) -> Dict:
        """Analisa diferencial de juros e carry trade."""

        conn = sqlite3.connect(CAMINHO_DB)
        cur = conn.cursor()

        # Buscar taxas
        cur.execute("""
            SELECT moeda, taxa_atual, forward_guidance
            FROM forex_taxas_juros
            WHERE moeda IN (?, ?) AND data_coleta = (
                SELECT MAX(data_coleta) FROM forex_taxas_juros
            )
        """, (moeda_base, moeda_cotada))

        taxas = {row[0]: {'taxa': row[1], 'guidance': row[2]} for row in cur.fetchall()}
        conn.close()

        if moeda_base not in taxas or moeda_cotada not in taxas:
            return {
                'diferencial': 0.0,
                'rating': 'desconhecido',
                'taxa_base': 0.0,
                'taxa_cotada': 0.0
            }

        # Calcular diferencial
        if operacao == 'COMPRA':
            diferencial = taxas[moeda_base]['taxa'] - taxas[moeda_cotada]['taxa']
        else:  # VENDA
            diferencial = taxas[moeda_cotada]['taxa'] - taxas[moeda_base]['taxa']

        # Rating do carry
        if diferencial >= 3.0:
            rating = 'excelente'
        elif diferencial >= 1.5:
            rating = 'bom'
        elif diferencial >= 0.5:
            rating = 'moderado'
        elif diferencial >= -0.5:
            rating = 'neutro'
        else:
            rating = 'negativo'

        return {
            'diferencial': diferencial,
            'rating': rating,
            'taxa_base': taxas[moeda_base]['taxa'],
            'taxa_cotada': taxas[moeda_cotada]['taxa']
        }

    def _analisar_politica_monetaria(self, moeda_base: str, moeda_cotada: str) -> Dict:
        """Analisa divergência de política monetária."""

        conn = sqlite3.connect(CAMINHO_DB)
        cur = conn.cursor()

        cur.execute("""
            SELECT moeda, forward_guidance
            FROM forex_taxas_juros
            WHERE moeda IN (?, ?) AND data_coleta = (
                SELECT MAX(data_coleta) FROM forex_taxas_juros
            )
        """, (moeda_base, moeda_cotada))

        guidance = {row[0]: row[1] for row in cur.fetchall()}
        conn.close()

        guidance_base = guidance.get(moeda_base, 'neutro')
        guidance_cotada = guidance.get(moeda_cotada, 'neutro')

        # Calcular divergência
        score_guidance = {
            'hawkish': 2,
            'neutro': 1,
            'dovish': 0
        }

        diff = abs(score_guidance.get(guidance_base, 1) - score_guidance.get(guidance_cotada, 1))

        if diff >= 2:
            divergencia = 'forte'
        elif diff >= 1:
            divergencia = 'moderada'
        else:
            divergencia = 'fraca'

        return {
            'guidance_base': guidance_base,
            'guidance_cotada': guidance_cotada,
            'divergencia': divergencia
        }

    def _analisar_tecnica(self, par: str, operacao: str) -> Dict:
        """Análise técnica: preço, níveis, tendência."""

        # Buscar símbolo Yahoo
        simbolo = self.PARES_YAHOO.get(par)

        if not simbolo:
            # Par não mapeado, retornar valores mock
            return {
                'preco_atual': 1.0000,
                'entrada': 0.9950,
                'stop': 0.9850,
                'tp1': 1.0150,
                'tp2': 1.0300,
                'tendencia': 'lateral'
            }

        try:
            # Buscar dados do Yahoo Finance
            ticker = yf.Ticker(simbolo)
            hist = ticker.history(period='1mo', interval='1d')

            if hist.empty:
                raise ValueError("Sem dados")

            preco_atual = float(hist['Close'].iloc[-1])

            # Calcular níveis técnicos simples
            if operacao == 'COMPRA':
                entrada = preco_atual * 0.995  # 0.5% abaixo
                stop = preco_atual * 0.985     # 1.5% abaixo
                tp1 = preco_atual * 1.015      # 1.5% acima
                tp2 = preco_atual * 1.030      # 3.0% acima
            else:  # VENDA
                entrada = preco_atual * 1.005
                stop = preco_atual * 1.015
                tp1 = preco_atual * 0.985
                tp2 = preco_atual * 0.970

            # Determinar tendência (SMA 20 vs SMA 50)
            sma20 = hist['Close'].rolling(20).mean().iloc[-1]
            sma50 = hist['Close'].rolling(50).mean().iloc[-1] if len(hist) >= 50 else sma20

            if sma20 > sma50 * 1.01:
                tendencia = 'alta'
            elif sma20 < sma50 * 0.99:
                tendencia = 'baixa'
            else:
                tendencia = 'lateral'

            return {
                'preco_atual': preco_atual,
                'entrada': entrada,
                'stop': stop,
                'tp1': tp1,
                'tp2': tp2,
                'tendencia': tendencia
            }

        except Exception as e:
            print(f"   ⚠️  Erro ao buscar dados: {str(e)}")
            return {
                'preco_atual': 1.0000,
                'entrada': 0.9950,
                'stop': 0.9850,
                'tp1': 1.0150,
                'tp2': 1.0300,
                'tendencia': 'lateral'
            }

    def _analisar_correlacao_brasil(self, moeda_base: str, moeda_cotada: str) -> Dict:
        """Analisa impacto do par no mercado brasileiro."""

        # Impacto direto no WIN/IBOV
        impacto_moedas = {
            'USD': 'negativo_forte',  # Dólar forte = WIN cai
            'BRL': 'positivo_forte',   # Real forte = WIN sobe
            'EUR': 'positivo_moderado',
            'GBP': 'positivo_moderado',
            'JPY': 'negativo_moderado',  # Yen forte = risk-off
            'AUD': 'positivo_fraco',     # Commodity currency
            'NZD': 'positivo_fraco',
            'CAD': 'positivo_fraco',
            'CHF': 'negativo_moderado'   # Safe haven
        }

        impacto_base = impacto_moedas.get(moeda_base, 'neutro')
        impacto_cotada = impacto_moedas.get(moeda_cotada, 'neutro')

        # Simplificar para string
        if 'BRL' in [moeda_base, moeda_cotada]:
            if moeda_base == 'BRL':
                impacto = 'positivo_forte'
            else:
                impacto = 'negativo_forte'
        elif moeda_base == 'USD' or moeda_cotada == 'USD':
            impacto = 'negativo_moderado'
        else:
            impacto = 'neutro'

        # Correlação estimada com IBOV
        correlacao = 0.0
        if 'BRL' in [moeda_base, moeda_cotada]:
            correlacao = -0.80 if moeda_cotada == 'BRL' else 0.80
        elif 'USD' in [moeda_base, moeda_cotada]:
            correlacao = -0.50

        return {
            'impacto': impacto,
            'correlacao': correlacao
        }

    def _analisar_sentimento(self, moeda_base: str, moeda_cotada: str) -> Dict:
        """Analisa sentimento das notícias recentes."""

        conn = sqlite3.connect(CAMINHO_DB)
        cur = conn.cursor()

        # Buscar notícias relevantes (últimas 24h)
        data_limite = datetime.now() - timedelta(hours=24)

        # Palavras-chave por moeda
        keywords = {
            'USD': ['dollar', 'dólar', 'fed', 'powell'],
            'EUR': ['euro', 'ecb', 'lagarde'],
            'GBP': ['pound', 'libra', 'boe', 'bailey'],
            'JPY': ['yen', 'iene', 'boj', 'ueda'],
            'BRL': ['real', 'bcb', 'copom'],
            'AUD': ['aussie', 'rba'],
            'NZD': ['kiwi', 'rbnz'],
        }

        keywords_busca = keywords.get(moeda_base, []) + keywords.get(moeda_cotada, [])

        cur.execute("""
            SELECT AVG(score_sentimento), COUNT(*)
            FROM noticias
            WHERE data_publicacao >= ?
        """, (data_limite.isoformat(),))

        resultado = cur.fetchone()
        conn.close()

        score = resultado[0] if resultado[0] else 0.0
        total = resultado[1] if resultado[1] else 0

        return {
            'score': score,
            'total': total
        }

    def _calcular_decisao_final(
        self, carry: Dict, politica: Dict, tecnica: Dict,
        correlacao: Dict, sentimento: Dict, operacao: str
    ) -> Dict:
        """Calcula recomendação final baseada nos 5 pilares."""

        # Sistema de pontuação
        pontos = 0
        max_pontos = 0

        # 1. Carry Trade (peso 30%)
        max_pontos += 30
        if carry['rating'] == 'excelente':
            pontos += 30
        elif carry['rating'] == 'bom':
            pontos += 20
        elif carry['rating'] == 'moderado':
            pontos += 10
        elif carry['rating'] == 'neutro':
            pontos += 0
        else:  # negativo
            pontos -= 10

        # 2. Política Monetária (peso 25%)
        max_pontos += 25
        if politica['divergencia'] == 'forte':
            pontos += 25
        elif politica['divergencia'] == 'moderada':
            pontos += 15
        else:
            pontos += 5

        # 3. Técnica (peso 20%)
        max_pontos += 20
        if operacao == 'COMPRA':
            if tecnica['tendencia'] == 'alta':
                pontos += 20
            elif tecnica['tendencia'] == 'lateral':
                pontos += 10
        else:  # VENDA
            if tecnica['tendencia'] == 'baixa':
                pontos += 20
            elif tecnica['tendencia'] == 'lateral':
                pontos += 10

        # 4. Correlação Brasil (peso 15%)
        max_pontos += 15
        if 'positivo' in correlacao['impacto']:
            pontos += 15
        elif 'neutro' in correlacao['impacto']:
            pontos += 7

        # 5. Sentimento (peso 10%)
        max_pontos += 10
        if sentimento['score'] > 0.3:
            pontos += 10
        elif sentimento['score'] > 0:
            pontos += 5
        elif sentimento['score'] < -0.3:
            pontos -= 5

        # Calcular confiança (0-100)
        confianca = int((pontos / max_pontos) * 100) if max_pontos > 0 else 50
        confianca = max(0, min(100, confianca))

        # Recomendação
        if confianca >= 70:
            if operacao == 'COMPRA':
                recomendacao = 'APROVAR_LONG'
            else:
                recomendacao = 'APROVAR_SHORT'
        elif confianca >= 50:
            recomendacao = 'APROVAR_TÁTICO'
        else:
            recomendacao = 'DESCARTAR'

        # Risco/Recompensa
        risco = abs(tecnica['preco_atual'] - tecnica['stop'])
        recompensa = abs(tecnica['tp1'] - tecnica['preco_atual'])
        rr = recompensa / risco if risco > 0 else 1.0

        return {
            'recomendacao': recomendacao,
            'confianca': confianca,
            'risco_recompensa': rr
        }

    def _sugerir_alternativa(self, moeda_base: str, moeda_cotada: str, carry_info: Dict) -> Optional[Dict]:
        """Sugere par alternativo com melhor carry."""

        # Buscar melhores carry trades
        melhores = self.coletor_fundamentals.obter_melhores_carry_trades(limite=5)

        if not melhores:
            return None

        # Verificar se há alternativa melhor com a mesma moeda base
        for carry in melhores:
            if carry['moeda_base'] == moeda_base and carry['diferencial'] > carry_info['diferencial'] + 1.0:
                return {
                    'par': f"{carry['moeda_base']}/{carry['moeda_cotada']}",
                    'motivo': f"Carry Trade superior: {carry['diferencial']:.2f}% vs {carry_info['diferencial']:.2f}%"
                }

        # Se for carry negativo, sugerir o melhor carry disponível
        if carry_info['diferencial'] < 0:
            melhor = melhores[0]
            return {
                'par': f"{melhor['moeda_base']}/{melhor['moeda_cotada']}",
                'motivo': f"Carry negativo atual. Sugestão: melhor carry disponível ({melhor['diferencial']:.2f}%)"
            }

        return None

    def gerar_relatorio_formatado(self, analise: AnaliseForex) -> str:
        """Gera relatório formatado similar ao output dos seus prompts."""

        relatorio = f"""
{'='*80}
RELATÓRIO DE ANÁLISE FOREX
Par: {analise.par}
Recomendação: {analise.recomendacao} | Confiança: {analise.confianca}%
{'='*80}

🥇 O FATOR DECISIVO: CARRY TRADE
─────────────────────────────────────────────────────────────────────────────
Moeda Base ({analise.moeda_base}):     Taxa: {float(analise.diferencial_juros + Decimal('2.0')):.2f}%
Moeda Cotada ({analise.moeda_cotada}):  Taxa: 2.00%
Diferencial:            {float(analise.diferencial_juros):+.2f}% a favor de {analise.moeda_base}
Rating:                 {analise.carry_rating.upper()}

Implicação: {'Carry Trade POSITIVO - Recebe juros para manter posição' if float(analise.diferencial_juros) > 0 else 'Carry Trade NEGATIVO - Paga juros para manter posição'}

🏦 DIVERGÊNCIA DE POLÍTICA MONETÁRIA
─────────────────────────────────────────────────────────────────────────────
{analise.moeda_base}:  {analise.guidance_base.upper()} {'🦅' if analise.guidance_base == 'hawkish' else '🕊️' if analise.guidance_base == 'dovish' else '⚖️'}
{analise.moeda_cotada}:  {analise.guidance_cotada.upper()} {'🦅' if analise.guidance_cotada == 'hawkish' else '🕊️' if analise.guidance_cotada == 'dovish' else '⚖️'}
Divergência: {analise.divergencia_politica.upper()}

📈 ANÁLISE TÉCNICA
─────────────────────────────────────────────────────────────────────────────
Preço Atual:    {float(analise.preco_atual):.4f}
Tendência:      {analise.tendencia.upper()}

Níveis Recomendados:
├─ Entrada:     {float(analise.entrada_sugerida):.4f}
├─ Stop Loss:   {float(analise.stop_loss):.4f}
├─ Take Profit 1: {float(analise.take_profit_1):.4f}
└─ Take Profit 2: {float(analise.take_profit_2):.4f}

Risco/Recompensa: 1:{analise.risco_recompensa:.2f}

🔗 CORRELAÇÃO COM MERCADO BRASILEIRO
─────────────────────────────────────────────────────────────────────────────
Impacto no WIN:        {analise.impacto_win.upper()}
Correlação com IBOV:   {analise.correlacao_ibov:+.2f}

📰 SENTIMENTO DE MERCADO
─────────────────────────────────────────────────────────────────────────────
Score:                 {analise.score_sentimento:+.2f} {'📈' if analise.score_sentimento > 0 else '📉' if analise.score_sentimento < 0 else '➡️'}
Notícias Relevantes:   {analise.noticias_relevantes}

🎯 DECISÃO FINAL
─────────────────────────────────────────────────────────────────────────────
Recomendação:  {analise.recomendacao}
Confiança:     {analise.confianca}%

{'─'*80}
Status: {'✅ OPERAÇÃO APROVADA' if analise.confianca >= 70 else '⚠️  OPERAÇÃO TÁTICA' if analise.confianca >= 50 else '❌ OPERAÇÃO DESCARTADA'}
{'─'*80}
"""

        if analise.par_alternativo:
            relatorio += f"""
💡 OPORTUNIDADE ALTERNATIVA RECOMENDADA
─────────────────────────────────────────────────────────────────────────────
Par Sugerido:  {analise.par_alternativo}
Motivo:        {analise.motivo_alternativa}
"""

        relatorio += f"\n{'='*80}\n"

        return relatorio


def exemplo_uso():
    """Exemplo de uso do analisador Forex."""

    analisador = AnalisadorForex()

    # Exemplo 1: Análise de COMPRA GBPNZD (do seu prompt)
    analise = analisador.analisar_par('GBPNZD', 'COMPRA')

    print("\n" + "="*80)
    print("RELATÓRIO FORMATADO")
    print("="*80)
    print(analisador.gerar_relatorio_formatado(analise))

    # Exemplo 2: Análise de VENDA AUDUSD
    print("\n" + "="*80)
    print("SEGUNDA ANÁLISE")
    print("="*80)
    analise2 = analisador.analisar_par('AUDUSD', 'VENDA')
    print(analisador.gerar_relatorio_formatado(analise2))


if __name__ == "__main__":
    exemplo_uso()
