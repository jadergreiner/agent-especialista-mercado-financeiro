# -*- coding: utf-8 -*-
"""
Analisador de Fundos Imobiliários (FIIs) - B3
Análise fundamentalista priorizando qualidade dos ativos e sustentabilidade.

Metodologia:
- QUALIDADE (40%): Vacância, rating, diversificação
- VALUATION (35%): P/VP, desconto/prêmio, preço vs teto
- RENDIMENTO (25%): DY, consistência, sustentabilidade

Autor: Agent Especialista Mercado Financeiro
Data: 2025-01-05
"""

from dataclasses import dataclass
from typing import List, Optional, Dict
from decimal import Decimal
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd


@dataclass
class AnaliseFII:
    """Estrutura de dados para análise de FII."""

    # Identificação
    codigo: str
    nome_completo: str
    tipo: str  # Tijolo, Papel, FOF
    setor: str  # Logístico, Lajes, Shoppings, CRI, Híbrido, etc

    # Rendimentos
    dy_12m: Decimal  # Dividend Yield 12 meses (%)
    rendimento_medio_12m: Decimal  # R$ por cota
    consistencia_rendimentos: str  # CONSISTENTE, IRREGULAR, VOLÁTIL

    # Valuation
    preco_atual: Decimal
    pvp_atual: Decimal  # Preço / Valor Patrimonial
    vp_cota: Decimal  # Valor Patrimonial por cota
    preco_teto_80centavos: Decimal  # Preço teto para renda de R$ 0.80/mês
    margem_desconto: Decimal  # % desconto vs VP (negativo = prêmio)

    # Qualidade dos Ativos
    vacancia_fisica: Optional[Decimal]  # % (para Tijolo)
    vacancia_financeira: Optional[Decimal]  # % (para Tijolo)
    indexador_principal: str  # IPCA, IGP-M, CDI, PREFIXADO, N/A
    diversificacao: str  # ALTA, MÉDIA, BAIXA

    # Liquidez
    liquidez_diaria_media: Decimal  # R$ volume médio

    # Scores
    score_qualidade: int  # 0-100
    score_valuation: int  # 0-100
    score_rendimento: int  # 0-100
    score_final: int  # 0-100

    # Decisão
    recomendacao: str  # COMPRA_FORTE, COMPRA, NEUTRO, VENDA
    riscos_identificados: List[str]
    pontos_fortes: List[str]


class AnalisadorFIIs:
    """
    Analisador fundamentalista de FIIs.

    Prioriza:
    1. Qualidade dos ativos (vacância, rating, diversificação)
    2. Valuation (P/VP, desconto/prêmio)
    3. Sustentabilidade dos rendimentos
    """

    def __init__(self):
        self.analises: List[AnaliseFII] = []

    def analisar_fii(self, codigo: str) -> Optional[AnaliseFII]:
        """
        Analisa um FII completo.

        Args:
            codigo: Código do FII (ex: KNRI11)

        Returns:
            AnaliseFII ou None se falhar
        """
        try:
            # Adicionar .SA para yfinance
            ticker = yf.Ticker(f"{codigo}.SA")

            # Coletar dados
            info = ticker.info
            historico = ticker.history(period="1y")
            dividendos = ticker.dividends

            if historico.empty:
                print(f"❌ Sem dados para {codigo}")
                return None

            # Preço atual
            preco_atual = Decimal(str(historico['Close'].iloc[-1]))

            # Valor patrimonial por cota
            vp_cota = Decimal(str(info.get('bookValue', 0.0)))
            if vp_cota == 0:
                # Fallback: estimar VP pelo P/VP se disponível
                pvp = info.get('priceToBook', 1.0)
                if pvp > 0:
                    vp_cota = preco_atual / Decimal(str(pvp))
                else:
                    vp_cota = preco_atual  # Assume P/VP = 1

            # P/VP
            pvp_atual = preco_atual / vp_cota if vp_cota > 0 else Decimal('1.0')

            # Margem de desconto (negativo = prêmio)
            margem_desconto = ((vp_cota - preco_atual) / vp_cota * 100) if vp_cota > 0 else Decimal('0')

            # Dividendos 12 meses
            if not dividendos.empty:
                data_corte = pd.Timestamp(datetime.now() - timedelta(days=365))
                if dividendos.index.tz is not None:
                    data_corte = data_corte.tz_localize(dividendos.index.tz)

                dividendos_12m = dividendos[dividendos.index >= data_corte]
                rendimento_medio_12m = Decimal(str(dividendos_12m.mean())) if not dividendos_12m.empty else Decimal('0')
                total_dividendos_12m = Decimal(str(dividendos_12m.sum())) if not dividendos_12m.empty else Decimal('0')

                # DY 12M
                dy_12m = (total_dividendos_12m / preco_atual * 100) if preco_atual > 0 else Decimal('0')

                # Consistência
                num_pagamentos = len(dividendos_12m)
                if num_pagamentos >= 11:
                    consistencia = "CONSISTENTE"
                elif num_pagamentos >= 8:
                    consistencia = "IRREGULAR"
                else:
                    consistencia = "VOLÁTIL"
            else:
                rendimento_medio_12m = Decimal('0')
                dy_12m = Decimal('0')
                consistencia = "SEM_DADOS"

            # Preço Teto (para renda de R$ 0.80/mês = R$ 9.60/ano)
            # Se DY = (Renda_Anual / Preço) * 100, então Preço_Teto = Renda_Alvo / (DY_Alvo / 100)
            # Usando DY alvo de 10% anual (conservador para FII)
            renda_alvo_anual = Decimal('9.60')  # R$ 0.80/mês * 12
            dy_alvo = Decimal('10.0')  # 10% ao ano
            preco_teto = renda_alvo_anual / (dy_alvo / 100) if dy_alvo > 0 else preco_atual

            # Nome completo
            nome_completo = info.get('longName', codigo)

            # Tipo e Setor (heurística baseada no nome - pode ser melhorado)
            tipo, setor = self._identificar_tipo_setor(nome_completo, codigo)

            # Vacância (mock - yfinance não fornece, seria necessário scraping ou API específica)
            if tipo == "Tijolo":
                vacancia_fisica = Decimal('5.0')  # Mock: 5% (seria coletado de relatórios)
                vacancia_financeira = Decimal('3.0')  # Mock: 3%
            else:
                vacancia_fisica = None
                vacancia_financeira = None

            # Indexador (mock - seria extraído de relatórios)
            if tipo == "Papel":
                indexador = "IPCA+"  # Mock: maioria é IPCA+
            elif tipo == "Tijolo":
                indexador = "IGPM"  # Mock: contratos geralmente IGPM
            else:
                indexador = "MISTO"

            # Diversificação (mock - seria calculado da carteira)
            diversificacao = "MÉDIA"  # Mock

            # Liquidez diária média
            volume_medio = historico['Volume'].tail(30).mean()
            preco_medio = historico['Close'].tail(30).mean()
            liquidez_diaria = Decimal(str(volume_medio * preco_medio))

            # Calcular scores
            score_qualidade = self._calcular_score_qualidade(
                tipo, vacancia_fisica, vacancia_financeira, diversificacao, indexador
            )

            score_valuation = self._calcular_score_valuation(
                pvp_atual, margem_desconto, preco_atual, preco_teto
            )

            score_rendimento = self._calcular_score_rendimento(
                dy_12m, consistencia, rendimento_medio_12m
            )

            # Score final (Qualidade 40%, Valuation 35%, Rendimento 25%)
            score_final = int(
                score_qualidade * 0.40 +
                score_valuation * 0.35 +
                score_rendimento * 0.25
            )

            # Recomendação
            if score_final >= 80:
                recomendacao = "COMPRA_FORTE"
            elif score_final >= 65:
                recomendacao = "COMPRA"
            elif score_final >= 50:
                recomendacao = "NEUTRO"
            else:
                recomendacao = "VENDA"

            # Identificar riscos e pontos fortes
            riscos = self._identificar_riscos(
                tipo, vacancia_fisica, pvp_atual, consistencia, liquidez_diaria
            )
            pontos_fortes = self._identificar_pontos_fortes(
                tipo, vacancia_fisica, pvp_atual, dy_12m, consistencia, diversificacao
            )

            # Criar análise
            analise = AnaliseFII(
                codigo=codigo,
                nome_completo=nome_completo,
                tipo=tipo,
                setor=setor,
                dy_12m=dy_12m,
                rendimento_medio_12m=rendimento_medio_12m,
                consistencia_rendimentos=consistencia,
                preco_atual=preco_atual,
                pvp_atual=pvp_atual,
                vp_cota=vp_cota,
                preco_teto_80centavos=preco_teto,
                margem_desconto=margem_desconto,
                vacancia_fisica=vacancia_fisica,
                vacancia_financeira=vacancia_financeira,
                indexador_principal=indexador,
                diversificacao=diversificacao,
                liquidez_diaria_media=liquidez_diaria,
                score_qualidade=score_qualidade,
                score_valuation=score_valuation,
                score_rendimento=score_rendimento,
                score_final=score_final,
                recomendacao=recomendacao,
                riscos_identificados=riscos,
                pontos_fortes=pontos_fortes
            )

            return analise

        except Exception as e:
            print(f"❌ Erro ao analisar {codigo}: {e}")
            return None

    def _identificar_tipo_setor(self, nome: str, codigo: str) -> tuple:
        """Identifica tipo e setor do FII por heurística."""
        nome_upper = nome.upper()

        # Tipo
        if 'CRI' in nome_upper or 'RENDA' in nome_upper or 'PAPEL' in nome_upper:
            tipo = "Papel"
        elif 'FOF' in nome_upper or 'FUNDOS' in nome_upper:
            tipo = "FOF"
        else:
            tipo = "Tijolo"

        # Setor
        if 'LOGIS' in nome_upper or 'GALPÃO' in nome_upper or 'GALPAO' in nome_upper:
            setor = "Logístico"
        elif 'LAJE' in nome_upper or 'ESCRITÓRIO' in nome_upper or 'ESCRITORIO' in nome_upper:
            setor = "Lajes Corporativas"
        elif 'SHOP' in nome_upper:
            setor = "Shoppings"
        elif 'HOTEL' in nome_upper or 'FLAT' in nome_upper:
            setor = "Hotéis"
        elif 'CRI' in nome_upper:
            setor = "CRI"
        elif 'AGRO' in nome_upper:
            setor = "Agronegócio"
        elif 'HIBRIDO' in nome_upper or 'HÍBRIDO' in nome_upper:
            setor = "Híbrido"
        else:
            setor = "Diversos"

        return tipo, setor

    def _calcular_score_qualidade(
        self,
        tipo: str,
        vacancia_fisica: Optional[Decimal],
        vacancia_financeira: Optional[Decimal],
        diversificacao: str,
        indexador: str
    ) -> int:
        """
        Calcula score de qualidade (0-100).

        Para Tijolo: Vacância é crítica
        Para Papel: Indexador é crítico
        """
        score = 50  # Base

        if tipo == "Tijolo":
            # Vacância Física (+30/-30)
            if vacancia_fisica is not None:
                if vacancia_fisica <= 3:
                    score += 30  # Excelente
                elif vacancia_fisica <= 7:
                    score += 15  # Boa
                elif vacancia_fisica <= 12:
                    score += 5  # Aceitável
                else:
                    score -= 30  # Crítica

            # Vacância Financeira (+10/-10)
            if vacancia_financeira is not None:
                if vacancia_financeira <= 2:
                    score += 10
                elif vacancia_financeira <= 5:
                    score += 5
                else:
                    score -= 10

        elif tipo == "Papel":
            # Indexador (+30/-10)
            if 'IPCA' in indexador:
                score += 30  # Melhor proteção inflação
            elif 'CDI' in indexador or 'SELIC' in indexador:
                score += 20  # Boa proteção
            elif 'IGP' in indexador:
                score += 10  # Aceitável
            elif 'PREFIXADO' in indexador:
                score -= 10  # Risco maior

        # Diversificação (+10/-10)
        if diversificacao == "ALTA":
            score += 10
        elif diversificacao == "BAIXA":
            score -= 10

        return max(0, min(100, score))

    def _calcular_score_valuation(
        self,
        pvp: Decimal,
        margem_desconto: Decimal,
        preco_atual: Decimal,
        preco_teto: Decimal
    ) -> int:
        """
        Calcula score de valuation (0-100).

        P/VP < 0.90: Oportunidade
        P/VP 0.90-1.10: Justo
        P/VP > 1.10: Caro
        """
        score = 50  # Base

        # P/VP (+30/-30)
        if pvp < Decimal('0.85'):
            score += 30  # Grande desconto
        elif pvp < Decimal('0.95'):
            score += 20  # Bom desconto
        elif pvp <= Decimal('1.05'):
            score += 10  # Próximo ao VP
        elif pvp <= Decimal('1.15'):
            score -= 10  # Pequeno prêmio
        else:
            score -= 30  # Prêmio alto

        # Margem de desconto vs VP (+20/-20)
        if margem_desconto > 10:
            score += 20  # >10% desconto
        elif margem_desconto > 5:
            score += 10  # 5-10% desconto
        elif margem_desconto < -10:
            score -= 20  # >10% prêmio

        return max(0, min(100, score))

    def _calcular_score_rendimento(
        self,
        dy: Decimal,
        consistencia: str,
        rendimento_medio: Decimal
    ) -> int:
        """
        Calcula score de rendimento (0-100).

        DY > 10%: Excelente
        DY 8-10%: Bom
        DY 6-8%: Aceitável
        DY < 6%: Baixo
        """
        score = 50  # Base

        # DY (+30/-20)
        if dy >= 10:
            score += 30
        elif dy >= 8:
            score += 20
        elif dy >= 6:
            score += 10
        elif dy >= 4:
            score += 0
        else:
            score -= 20

        # Consistência (+20/-20)
        if consistencia == "CONSISTENTE":
            score += 20
        elif consistencia == "IRREGULAR":
            score += 5
        elif consistencia == "VOLÁTIL":
            score -= 10
        else:  # SEM_DADOS
            score -= 20

        return max(0, min(100, score))

    def _identificar_riscos(
        self,
        tipo: str,
        vacancia: Optional[Decimal],
        pvp: Decimal,
        consistencia: str,
        liquidez: Decimal
    ) -> List[str]:
        """Identifica riscos críticos."""
        riscos = []

        if tipo == "Tijolo" and vacancia and vacancia > 10:
            riscos.append(f"Vacância elevada ({float(vacancia):.1f}%)")

        if pvp > Decimal('1.15'):
            riscos.append(f"P/VP alto ({float(pvp):.2f}) - negociando com prêmio")

        if consistencia in ["VOLÁTIL", "IRREGULAR"]:
            riscos.append(f"Rendimentos {consistencia.lower()}")

        if liquidez < Decimal('100000'):
            riscos.append(f"Baixa liquidez (R$ {float(liquidez):,.0f}/dia)")

        return riscos

    def _identificar_pontos_fortes(
        self,
        tipo: str,
        vacancia: Optional[Decimal],
        pvp: Decimal,
        dy: Decimal,
        consistencia: str,
        diversificacao: str
    ) -> List[str]:
        """Identifica pontos fortes."""
        fortes = []

        if tipo == "Tijolo" and vacancia and vacancia < 5:
            fortes.append(f"Baixa vacância ({float(vacancia):.1f}%)")

        if pvp < Decimal('0.95'):
            fortes.append(f"Negociando com desconto (P/VP {float(pvp):.2f})")

        if dy >= 10:
            fortes.append(f"DY atrativo ({float(dy):.2f}%)")

        if consistencia == "CONSISTENTE":
            fortes.append("Rendimentos consistentes (11+ meses)")

        if diversificacao == "ALTA":
            fortes.append("Alta diversificação de ativos")

        return fortes

    def analisar_portfolio(self, codigos: List[str]) -> List[AnaliseFII]:
        """
        Analisa múltiplos FIIs.

        Args:
            codigos: Lista de códigos (ex: ['KNRI11', 'HGLG11'])

        Returns:
            Lista de análises ordenadas por score
        """
        print(f"\n{'='*80}")
        print("🏢 ANÁLISE COMPARATIVA DE FIIs")
        print(f"{'='*80}")
        print(f"FIIs: {', '.join(codigos)}")
        print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}\n")

        analises = []

        for codigo in codigos:
            print(f"🏢 Analisando {codigo}...", end=" ")
            analise = self.analisar_fii(codigo)

            if analise:
                analises.append(analise)
                print(f"✅ Score: {analise.score_final}")
            else:
                print(f"❌ Falhou")

        # Ordenar por score (maior primeiro)
        analises.sort(key=lambda x: x.score_final, reverse=True)

        self.analises = analises
        return analises

    def gerar_tabela_comparativa(self) -> str:
        """Gera tabela markdown horizontal (métricas × FIIs)."""
        if not self.analises:
            return "❌ Nenhuma análise disponível"

        # Cabeçalho
        tabela = "\n| Métrica | " + " | ".join([f.codigo for f in self.analises]) + " |\n"
        tabela += "| :--- | " + " | ".join(["---" for _ in self.analises]) + " |\n"

        # Linhas
        linhas = [
            ("**FII**", lambda f: f.nome_completo),
            ("**TIPO / SETOR**", lambda f: f"{f.tipo} / {f.setor}"),
            ("**DY (12M)**", lambda f: f"{float(f.dy_12m):.2f}%"),
            ("**P/VP**", lambda f: f"{float(f.pvp_atual):.2f}"),
            ("**Vacância (%)**", lambda f:
                f"Fís: {float(f.vacancia_fisica):.1f}% / Fin: {float(f.vacancia_financeira):.1f}%"
                if f.vacancia_fisica else "N/A (Papel)"),
            ("**Liquidez Diária Média**", lambda f: f"R$ {float(f.liquidez_diaria_media):,.0f}"),
            ("**Diversificação**", lambda f: f.diversificacao),
            ("**Indexador Principal**", lambda f: f.indexador_principal),
            ("**PREÇO TETO (R$ 0.80/mês)**", lambda f: f"R$ {float(f.preco_teto_80centavos):.2f}"),
            ("**SCORE FINAL**", lambda f: f"{f.score_final}/100"),
            ("**RECOMENDAÇÃO**", lambda f: f.recomendacao),
        ]

        for label, func in linhas:
            valores = " | ".join([func(f) for f in self.analises])
            tabela += f"| {label} | {valores} |\n"

        return tabela

    def gerar_relatorio_executivo(self) -> str:
        """Gera relatório executivo identificando melhor oportunidade."""
        if not self.analises:
            return "❌ Nenhuma análise disponível"

        melhor = self.analises[0]

        relatorio = "\n## 🎯 RELATÓRIO EXECUTIVO E JULGAMENTO\n\n"
        relatorio += "### Melhor Oportunidade\n"
        relatorio += f"O Fundo Imobiliário **{melhor.codigo}** ({melhor.nome_completo}) "
        relatorio += "é considerado a melhor oportunidade de investimento, "
        relatorio += "dada a relação Qualidade vs. Preço.\n\n"
        relatorio += f"**Score Final**: {melhor.score_final}/100 | **Recomendação**: {melhor.recomendacao}\n\n"

        relatorio += "### Justificativa da Escolha\n\n"

        # Qualidade
        relatorio += f"#### 🏗️ Qualidade e Risco (Score: {melhor.score_qualidade}/100)\n"
        relatorio += f"{melhor.tipo} - {melhor.setor}. "
        if melhor.tipo == "Tijolo":
            relatorio += f"Vacância física de **{float(melhor.vacancia_fisica):.1f}%** "
            relatorio += f"e financeira de **{float(melhor.vacancia_financeira):.1f}%**. "
        relatorio += f"Indexador: **{melhor.indexador_principal}**. "
        relatorio += f"Diversificação: **{melhor.diversificacao}**.\n\n"

        # Valuation
        relatorio += f"#### 💰 Valuation (Score: {melhor.score_valuation}/100)\n"
        relatorio += f"P/VP de **{float(melhor.pvp_atual):.2f}** "
        if melhor.margem_desconto > 0:
            relatorio += f"(desconto de {float(melhor.margem_desconto):.1f}% vs VP). "
        else:
            relatorio += f"(prêmio de {float(abs(melhor.margem_desconto)):.1f}% vs VP). "
        relatorio += f"Preço atual R$ {float(melhor.preco_atual):.2f} "
        relatorio += f"vs Preço Teto R$ {float(melhor.preco_teto_80centavos):.2f} "
        relatorio += f"(renda alvo R$ 0.80/mês).\n\n"

        # Rendimento
        relatorio += f"#### 📊 Sustentabilidade do Rendimento (Score: {melhor.score_rendimento}/100)\n"
        relatorio += f"DY 12M de **{float(melhor.dy_12m):.2f}%** com rendimentos **{melhor.consistencia_rendimentos}**. "
        relatorio += f"Rendimento médio mensal: R$ {float(melhor.rendimento_medio_12m):.2f}/cota.\n\n"

        # Pontos Fortes
        if melhor.pontos_fortes:
            relatorio += "#### ✅ Pontos Fortes\n"
            for ponto in melhor.pontos_fortes:
                relatorio += f"- {ponto}\n"
            relatorio += "\n"

        # Riscos
        if melhor.riscos_identificados:
            relatorio += "#### ⚠️  Riscos a Monitorar\n"
            for risco in melhor.riscos_identificados:
                relatorio += f"- {risco}\n"
            relatorio += "\n"

        # FIIs Preteridos
        if len(self.analises) > 1:
            relatorio += "### ❌ FIIs Preteridos\n\n"
            for fii in self.analises[1:]:
                motivos = []
                if fii.score_qualidade < melhor.score_qualidade:
                    motivos.append(f"qualidade inferior ({fii.score_qualidade} vs {melhor.score_qualidade})")
                if fii.score_valuation < melhor.score_valuation:
                    motivos.append(f"valuation menos atrativo")
                if fii.score_rendimento < melhor.score_rendimento:
                    motivos.append(f"rendimento menos sustentável")

                motivo_str = ", ".join(motivos) if motivos else "score inferior"
                relatorio += f"**{fii.codigo}** (Score: {fii.score_final}/100): {motivo_str}.\n"

        return relatorio


# Teste standalone
if __name__ == "__main__":
    analisador = AnalisadorFIIs()

    # Testar com FIIs conhecidos
    codigos = ['KNRI11', 'HGLG11', 'MXRF11']

    analises = analisador.analisar_portfolio(codigos)

    if analises:
        print(f"\n{'='*80}")
        print("📊 TABELA COMPARATIVA")
        print(f"{'='*80}")
        print(analisador.gerar_tabela_comparativa())

        print(f"\n{'='*80}")
        print(analisador.gerar_relatorio_executivo())
        print(f"{'='*80}\n")
