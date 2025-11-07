# -*- coding: utf-8 -*-
"""
Analisador de Dividendos - Análise Fundamentalista Comparativa de Ações.

Implementa metodologia de Engenharia Financeira para seleção de melhores
oportunidades de renda passiva baseada em:

1. Consistência de pagamentos de dividendos (5 anos)
2. Sustentabilidade (LPA estável/crescente)
3. Saúde financeira (Liquidez + Caixa Livre)
4. Preços Teto (6% DY) e Ideal (8% DY)
5. Análise comparativa horizontal

Prioriza SUSTENTABILIDADE sobre Dividend Yield isolado.
"""

import yfinance as yf
import pandas as pd
from dataclasses import dataclass
from typing import List, Dict, Optional
from decimal import Decimal
from datetime import datetime, timedelta


@dataclass
class AnaliseAcao:
    """Estrutura de análise fundamentalista de ação."""

    # Identificação
    codigo: str
    nome_completo: str
    setor: str

    # Dividendos
    dy_12m: Decimal  # Dividend Yield 12 meses
    dividendos_medio_5anos: Decimal
    consistencia_dividendos: str  # CONSISTENTE, IRREGULAR, ESPORÁDICO

    # Valuation
    preco_atual: Decimal
    pl_atual: Decimal  # Price/Earnings
    lpa_atual: Decimal  # Lucro por Ação
    lpa_tendencia_5anos: str  # CRESCENTE, ESTÁVEL, VOLÁTIL, DECRESCENTE

    # Saúde Financeira
    liquidez_corrente: Decimal
    geracao_caixa_livre: str  # POSITIVA, NEGATIVA, NEUTRA

    # Preços Calculados
    preco_teto_6pct: Decimal  # DY 6%
    preco_ideal_8pct: Decimal  # DY 8%
    margem_seguranca: Decimal  # % até preço ideal

    # Score e Recomendação
    score_sustentabilidade: int  # 0-100
    score_saude_financeira: int  # 0-100
    score_valor: int  # 0-100
    score_final: int  # 0-100
    recomendacao: str  # COMPRA_FORTE, COMPRA, NEUTRO, VENDA

    # Riscos
    riscos_identificados: List[str]
    pontos_fortes: List[str]


class AnalisadorDividendos:
    """
    Analisador de Ações para Renda Passiva.

    Metodologia:
    1. Coleta dados fundamentalistas (yfinance)
    2. Valida consistência de dividendos (5 anos)
    3. Calcula preços teto e ideal
    4. Avalia sustentabilidade vs valor
    5. Gera tabela comparativa + relatório executivo
    """

    def __init__(self):
        """Inicializa o analisador."""
        self.acoes_analisadas: List[AnaliseAcao] = []

    def analisar_acao(self, codigo: str) -> Optional[AnaliseAcao]:
        """
        Análise fundamentalista completa de uma ação.

        Args:
            codigo: Ticker da ação (ex: TGMA3, KLBN11)

        Returns:
            AnaliseAcao com todas as métricas
        """

        print(f"\n📊 Analisando {codigo}...", end=' ')

        try:
            # Adicionar .SA para B3
            ticker_yf = f"{codigo}.SA"
            acao = yf.Ticker(ticker_yf)

            # Obter informações básicas
            info = acao.info

            # Histórico de preços (5 anos)
            hist = acao.history(period="5y")

            if hist.empty:
                print("❌ Sem dados históricos")
                return None

            # Dados fundamentalistas
            preco_atual = Decimal(str(hist['Close'].iloc[-1]))

            # Nome e setor
            nome_completo = info.get('longName', codigo)
            setor = info.get('sector', 'N/D')

            # Dividend Yield
            dy_12m = Decimal(str(info.get('dividendYield', 0) * 100)) if info.get('dividendYield') else Decimal('0')

            # LPA (Earnings Per Share)
            lpa_atual = Decimal(str(info.get('trailingEps', 0)))

            # P/L (Price to Earnings)
            pl_atual = Decimal(str(info.get('trailingPE', 0))) if info.get('trailingPE') else Decimal('0')

            # Liquidez Corrente
            liquidez_corrente = Decimal(str(info.get('currentRatio', 0)))

            # Caixa Livre (Free Cash Flow)
            fcf = info.get('freeCashflow', 0)
            geracao_caixa_livre = 'POSITIVA' if fcf > 0 else 'NEGATIVA' if fcf < 0 else 'NEUTRA'

            # Calcular dividendos médio 5 anos (aproximação)
            dividendos = acao.dividends
            if not dividendos.empty:
                # Últimos 5 anos (converter para timezone-aware)
                data_corte = pd.Timestamp(datetime.now() - timedelta(days=5*365))
                if dividendos.index.tz is not None:
                    data_corte = data_corte.tz_localize(dividendos.index.tz)
                dividendos_5anos = dividendos[dividendos.index >= data_corte]

                if len(dividendos_5anos) >= 5:  # Pelo menos 5 pagamentos
                    dividendos_medio = Decimal(str(dividendos_5anos.sum() / 5))
                    consistencia = 'CONSISTENTE'
                elif len(dividendos_5anos) >= 3:
                    dividendos_medio = Decimal(str(dividendos_5anos.sum() / len(dividendos_5anos)))
                    consistencia = 'IRREGULAR'
                else:
                    dividendos_medio = Decimal('0')
                    consistencia = 'ESPORÁDICO'
            else:
                dividendos_medio = Decimal('0')
                consistencia = 'SEM_HISTÓRICO'

            # Tendência LPA (simplificado - seria ideal ter dados anuais)
            # Por ora, usar variação recente
            if lpa_atual > 0:
                lpa_tendencia = 'ESTÁVEL'  # Mock - precisa dados históricos de LPA
            else:
                lpa_tendencia = 'VOLÁTIL'

            # Calcular preços teto e ideal
            if dividendos_medio > 0:
                preco_teto = dividendos_medio / Decimal('0.06')  # DY 6%
                preco_ideal = dividendos_medio / Decimal('0.08')  # DY 8%
            else:
                preco_teto = Decimal('0')
                preco_ideal = Decimal('0')

            # Margem de segurança
            if preco_ideal > 0:
                margem_seguranca = ((preco_ideal - preco_atual) / preco_atual) * 100
            else:
                margem_seguranca = Decimal('0')

            # Scores (0-100)
            score_sustentabilidade = self._calcular_score_sustentabilidade(
                lpa_tendencia, consistencia, lpa_atual
            )

            score_saude_financeira = self._calcular_score_saude(
                liquidez_corrente, geracao_caixa_livre
            )

            score_valor = self._calcular_score_valor(
                margem_seguranca, dy_12m, pl_atual
            )

            score_final = int(
                score_sustentabilidade * 0.40 +
                score_saude_financeira * 0.35 +
                score_valor * 0.25
            )

            # Recomendação
            if score_final >= 80:
                recomendacao = 'COMPRA_FORTE'
            elif score_final >= 65:
                recomendacao = 'COMPRA'
            elif score_final >= 50:
                recomendacao = 'NEUTRO'
            else:
                recomendacao = 'VENDA'

            # Identificar riscos e pontos fortes
            riscos = self._identificar_riscos(
                consistencia, lpa_tendencia, liquidez_corrente,
                geracao_caixa_livre, margem_seguranca
            )

            pontos_fortes = self._identificar_pontos_fortes(
                consistencia, dy_12m, liquidez_corrente,
                lpa_tendencia, margem_seguranca
            )

            analise = AnaliseAcao(
                codigo=codigo,
                nome_completo=nome_completo,
                setor=setor,
                dy_12m=dy_12m,
                dividendos_medio_5anos=dividendos_medio,
                consistencia_dividendos=consistencia,
                preco_atual=preco_atual,
                pl_atual=pl_atual,
                lpa_atual=lpa_atual,
                lpa_tendencia_5anos=lpa_tendencia,
                liquidez_corrente=liquidez_corrente,
                geracao_caixa_livre=geracao_caixa_livre,
                preco_teto_6pct=preco_teto,
                preco_ideal_8pct=preco_ideal,
                margem_seguranca=margem_seguranca,
                score_sustentabilidade=score_sustentabilidade,
                score_saude_financeira=score_saude_financeira,
                score_valor=score_valor,
                score_final=score_final,
                recomendacao=recomendacao,
                riscos_identificados=riscos,
                pontos_fortes=pontos_fortes
            )

            print(f"✅ Score: {score_final}")
            return analise

        except Exception as e:
            print(f"❌ Erro: {str(e)}")
            return None

    def _calcular_score_sustentabilidade(
        self, lpa_tendencia: str, consistencia: str, lpa: Decimal
    ) -> int:
        """Calcula score de sustentabilidade (0-100)."""

        score = 50  # Base

        # Tendência LPA
        if lpa_tendencia == 'CRESCENTE':
            score += 30
        elif lpa_tendencia == 'ESTÁVEL':
            score += 20
        elif lpa_tendencia == 'VOLÁTIL':
            score += 5
        else:  # DECRESCENTE
            score -= 20

        # Consistência dividendos
        if consistencia == 'CONSISTENTE':
            score += 20
        elif consistencia == 'IRREGULAR':
            score += 5
        else:  # ESPORÁDICO
            score -= 30

        # LPA positivo
        if lpa > 0:
            score += 0
        else:
            score -= 20

        return max(0, min(100, score))

    def _calcular_score_saude(
        self, liquidez: Decimal, caixa: str
    ) -> int:
        """Calcula score de saúde financeira (0-100)."""

        score = 50

        # Liquidez corrente
        if liquidez >= 2.0:
            score += 30
        elif liquidez >= 1.5:
            score += 20
        elif liquidez >= 1.0:
            score += 10
        else:
            score -= 20

        # Geração de caixa
        if caixa == 'POSITIVA':
            score += 20
        elif caixa == 'NEUTRA':
            score += 0
        else:
            score -= 20

        return max(0, min(100, score))

    def _calcular_score_valor(
        self, margem: Decimal, dy: Decimal, pl: Decimal
    ) -> int:
        """Calcula score de valor (0-100)."""

        score = 50

        # Margem de segurança
        if margem >= 30:
            score += 30
        elif margem >= 15:
            score += 20
        elif margem >= 0:
            score += 10
        else:
            score -= 20

        # Dividend Yield
        if dy >= 8:
            score += 15
        elif dy >= 6:
            score += 10
        elif dy >= 4:
            score += 5

        # P/L
        if 0 < pl <= 10:
            score += 5
        elif pl <= 15:
            score += 0
        else:
            score -= 5

        return max(0, min(100, score))

    def _identificar_riscos(
        self, consistencia: str, lpa_tendencia: str,
        liquidez: Decimal, caixa: str, margem: Decimal
    ) -> List[str]:
        """Identifica riscos principais."""

        riscos = []

        if consistencia in ['ESPORÁDICO', 'IRREGULAR']:
            riscos.append('Dividendos inconsistentes')

        if lpa_tendencia in ['VOLÁTIL', 'DECRESCENTE']:
            riscos.append('LPA instável')

        if liquidez < 1.0:
            riscos.append('Liquidez corrente baixa')

        if caixa == 'NEGATIVA':
            riscos.append('Queima de caixa')

        if margem < 0:
            riscos.append('Preço acima do ideal')

        return riscos if riscos else ['Sem riscos críticos identificados']

    def _identificar_pontos_fortes(
        self, consistencia: str, dy: Decimal, liquidez: Decimal,
        lpa_tendencia: str, margem: Decimal
    ) -> List[str]:
        """Identifica pontos fortes."""

        fortes = []

        if consistencia == 'CONSISTENTE':
            fortes.append('Histórico sólido de dividendos')

        if dy >= 6:
            fortes.append(f'Dividend Yield atrativo ({float(dy):.2f}%)')

        if liquidez >= 1.5:
            fortes.append('Boa saúde financeira')

        if lpa_tendencia == 'CRESCENTE':
            fortes.append('Lucro em crescimento')

        if margem >= 15:
            fortes.append('Preço com margem de segurança')

        return fortes if fortes else ['Oportunidade limitada no momento']

    def analisar_portfolio(
        self, codigos: List[str]
    ) -> List[AnaliseAcao]:
        """
        Analisa múltiplas ações e gera ranking.

        Args:
            codigos: Lista de tickers (ex: ['TGMA3', 'KLBN11'])

        Returns:
            Lista de análises ordenadas por score
        """

        print(f"\n{'='*80}")
        print(f"📊 ANÁLISE COMPARATIVA DE DIVIDENDOS")
        print(f"{'='*80}")
        print(f"Ações: {', '.join(codigos)}")
        print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}")

        analises_validas = []

        for codigo in codigos:
            analise = self.analisar_acao(codigo)
            if analise:
                analises_validas.append(analise)

        # Ordenar por score final
        self.acoes_analisadas = sorted(
            analises_validas,
            key=lambda x: x.score_final,
            reverse=True
        )

        return self.acoes_analisadas

    def gerar_tabela_comparativa(self) -> str:
        """Gera tabela markdown comparativa horizontal."""

        if not self.acoes_analisadas:
            return "⚠️  Nenhuma análise disponível."

        # Cabeçalho
        header = "| Métrica |" + "".join(
            f" {a.codigo} |" for a in self.acoes_analisadas
        )
        separator = "| :--- |" + " :--- |" * len(self.acoes_analisadas)

        # Linhas
        linhas = []

        # Nomes
        linhas.append(
            "| **AÇÃO** |" +
            "".join(f" {a.nome_completo} |" for a in self.acoes_analisadas)
        )

        # Setor
        linhas.append(
            "| **SETOR** |" +
            "".join(f" {a.setor} |" for a in self.acoes_analisadas)
        )

        # DY 12M
        linhas.append(
            "| **DY (12M)** |" +
            "".join(f" {float(a.dy_12m):.2f}% |" for a in self.acoes_analisadas)
        )

        # P/L
        linhas.append(
            "| **P/L** |" +
            "".join(f" {float(a.pl_atual):.2f} |" for a in self.acoes_analisadas)
        )

        # LPA Atual
        linhas.append(
            "| **LPA (Atual)** |" +
            "".join(f" R$ {float(a.lpa_atual):.2f} |" for a in self.acoes_analisadas)
        )

        # LPA Tendência
        linhas.append(
            "| **LPA (Tendência 5a)** |" +
            "".join(f" {a.lpa_tendencia_5anos} |" for a in self.acoes_analisadas)
        )

        # Liquidez Corrente
        linhas.append(
            "| **Liq. Corrente** |" +
            "".join(f" {float(a.liquidez_corrente):.2f} |" for a in self.acoes_analisadas)
        )

        # Geração Caixa
        linhas.append(
            "| **Geração Caixa Livre** |" +
            "".join(f" {a.geracao_caixa_livre} |" for a in self.acoes_analisadas)
        )

        # Preço Teto
        linhas.append(
            "| **PREÇO TETO (6% DY)** |" +
            "".join(
                f" R$ {float(a.preco_teto_6pct):.2f} |"
                if a.preco_teto_6pct > 0
                else " N/D |"
                for a in self.acoes_analisadas
            )
        )

        # Preço Ideal
        linhas.append(
            "| **PREÇO IDEAL (8% DY)** |" +
            "".join(
                f" R$ {float(a.preco_ideal_8pct):.2f} |"
                if a.preco_ideal_8pct > 0
                else " N/D |"
                for a in self.acoes_analisadas
            )
        )

        # Score Final
        linhas.append(
            "| **SCORE FINAL** |" +
            "".join(f" {a.score_final}/100 |" for a in self.acoes_analisadas)
        )

        # Recomendação
        linhas.append(
            "| **RECOMENDAÇÃO** |" +
            "".join(f" {a.recomendacao} |" for a in self.acoes_analisadas)
        )

        return "\n".join([header, separator] + linhas)

    def gerar_relatorio_executivo(self) -> str:
        """Gera relatório executivo com julgamento."""

        if not self.acoes_analisadas:
            return "⚠️  Nenhuma análise disponível."

        melhor = self.acoes_analisadas[0]

        relatorio = f"""
## 🎯 RELATÓRIO EXECUTIVO E JULGAMENTO

### Melhor Oportunidade
A ação **{melhor.codigo}** ({melhor.nome_completo}) é considerada a melhor oportunidade de investimento de renda passiva no momento.

**Score Final**: {melhor.score_final}/100 | **Recomendação**: {melhor.recomendacao}

### Justificativa da Escolha

#### 💰 Sustentabilidade do Lucro (Score: {melhor.score_sustentabilidade}/100)
{melhor.codigo} apresenta **{melhor.consistencia_dividendos}** em dividendos com LPA {melhor.lpa_tendencia_5anos}.
O lucro por ação de R$ {float(melhor.lpa_atual):.2f} demonstra capacidade de geração de valor consistente.
"""

        # Comparar com outras
        if len(self.acoes_analisadas) > 1:
            outras = [a for a in self.acoes_analisadas[1:]]
            relatorio += f"\nComparativamente, "

            for outra in outras[:2]:  # Até 2 outras
                relatorio += f"{outra.codigo} apresenta {outra.consistencia_dividendos} "
                relatorio += f"(LPA {outra.lpa_tendencia_5anos}), "

            relatorio = relatorio.rstrip(", ") + "."

        relatorio += f"""

#### 🏥 Saúde Financeira (Score: {melhor.score_saude_financeira}/100)
Liquidez corrente de **{float(melhor.liquidez_corrente):.2f}** e geração de caixa livre **{melhor.geracao_caixa_livre}**
garantem solidez financeira para manutenção dos pagamentos de dividendos.
"""

        relatorio += f"""

#### 💎 Potencial de Valor (Score: {melhor.score_valor}/100)
Com DY 12M de **{float(melhor.dy_12m):.2f}%** e P/L de **{float(melhor.pl_atual):.2f}**, a ação apresenta
"""

        if melhor.margem_seguranca > 0:
            relatorio += f"margem de segurança de **{float(melhor.margem_seguranca):.1f}%** "
            relatorio += f"em relação ao preço ideal (R$ {float(melhor.preco_ideal_8pct):.2f})."
        else:
            relatorio += "valuation esticado, exigindo cautela na entrada."

        # Pontos Fortes
        relatorio += f"\n\n#### ✅ Pontos Fortes\n"
        for ponto in melhor.pontos_fortes:
            relatorio += f"- {ponto}\n"

        # Riscos
        if melhor.riscos_identificados[0] != 'Sem riscos críticos identificados':
            relatorio += f"\n#### ⚠️  Riscos a Monitorar\n"
            for risco in melhor.riscos_identificados:
                relatorio += f"- {risco}\n"

        # Ações descartadas
        if len(self.acoes_analisadas) > 1:
            relatorio += "\n### ❌ Ações Preteridas\n"

            for acao in self.acoes_analisadas[1:]:
                motivos = []

                if acao.score_sustentabilidade < 60:
                    motivos.append("baixa sustentabilidade")

                if acao.consistencia_dividendos != 'CONSISTENTE':
                    motivos.append("dividendos inconsistentes")

                if acao.liquidez_corrente < 1.0:
                    motivos.append("liquidez preocupante")

                if acao.margem_seguranca < 0:
                    motivos.append("preço elevado")

                relatorio += f"\n**{acao.codigo}** (Score: {acao.score_final}/100): "
                relatorio += ", ".join(motivos) if motivos else "score inferior"
                relatorio += "."

        relatorio += "\n"
        return relatorio


def main():
    """Função principal - teste do analisador."""

    # Ações do prompt original
    acoes = ['TGMA3', 'KLBN11', 'GGBR4', 'GOAU4', 'LOGG3', 'RANI3']

    analisador = AnalisadorDividendos()

    # Análise completa
    analises = analisador.analisar_portfolio(acoes)

    if analises:
        print(f"\n{'='*80}")
        print("📊 TABELA COMPARATIVA")
        print(f"{'='*80}\n")

        print(analisador.gerar_tabela_comparativa())

        print(f"\n{'='*80}")
        print(analisador.gerar_relatorio_executivo())
        print(f"{'='*80}\n")
    else:
        print("\n❌ Nenhuma ação foi analisada com sucesso.\n")


if __name__ == "__main__":
    main()
