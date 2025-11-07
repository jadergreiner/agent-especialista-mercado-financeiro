# -*- coding: utf-8 -*-
"""
Analisador de Carteira de Criptoativos - Análise Integrada AF + AT + Modelagem
Horizonte: 2 anos (24-36 meses)

Metodologia:
- FUNDAMENTOS (40%): Utility, governança, tokenomics
- ANÁLISE TÉCNICA (30%): Volatilidade, suportes, resistências
- PROJEÇÃO CMP (30%): Capitalização de mercado potencial

Autor: Agent Especialista Mercado Financeiro
Data: 2025-01-05
"""

from dataclasses import dataclass
from typing import List, Optional, Dict
from decimal import Decimal
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import numpy as np


@dataclass
class AnaliseCripto:
    """Estrutura de dados para análise de criptoativo."""

    # Identificação
    simbolo: str
    nome: str
    categoria: str  # Blue Chip, Layer1/Layer2, AI/Gaming/Modular

    # Fundamentos (Tese de Investimento)
    tese_fundacao: str  # Utility, governança, tokenomics
    utility_score: int  # 0-100
    adocao_score: int  # 0-100

    # Preços e Market Cap
    preco_atual: Decimal
    market_cap_atual: Decimal  # USD
    preco_minimo_30d: Decimal
    preco_maximo_30d: Decimal
    volatilidade_30d: Decimal  # %

    # Análise Técnica
    ponto_critico: Decimal  # Invalidação da tese
    preco_ideal_compra: Decimal  # Zona de demanda/suporte forte
    preco_teto_acumulo: Decimal  # Resistência chave
    distancia_minima: Decimal  # % do preço atual vs mínima 30d
    distancia_maxima: Decimal  # % do preço atual vs máxima 30d

    # Projeção (2 anos)
    market_cap_projetado: Decimal  # USD (cenário conservador)
    preco_projetado: Decimal  # USD
    multiplo_retorno: Decimal  # CMP_alvo / MC_atual

    # Scores
    score_fundamentos: int  # 0-100
    score_tecnico: int  # 0-100
    score_projecao: int  # 0-100
    score_final: int  # 0-100

    # Decisão
    peso_sugerido: Decimal  # % na carteira (0-100)
    justificativa_retorno: str
    riscos: List[str]
    catalistas: List[str]


class AnalisadorCarteiraCripto:
    """
    Analisador integrado de carteira de criptoativos.

    Combina:
    1. Análise Fundamentalista (AF): Utility, adoção, tokenomics
    2. Análise Técnica (AT): Volatilidade, suportes, resistências
    3. Modelagem Financeira: Projeção de Market Cap potencial
    """

    def __init__(self):
        self.analises: List[AnaliseCripto] = []

        # Database de Market Cap potenciais (cenários conservadores)
        # Baseado em comparação com peers e crescimento do setor
        self.projecoes_market_cap = {
            'BTC': Decimal('2000000000000'),  # $2T (ouro digital maduro)
            'ETH': Decimal('1000000000000'),  # $1T (plataforma contratos inteligentes dominante)
            'SOL': Decimal('200000000000'),   # $200B (Ethereum killer consolidado)
            'LINK': Decimal('50000000000'),   # $50B (oráculos padrão do mercado)
            'MATIC': Decimal('30000000000'),  # $30B (Layer 2 principal Ethereum)
            'RNDR': Decimal('20000000000'),   # $20B (DePIN + AI rendering líder)
            'AAVE': Decimal('15000000000'),   # $15B (DeFi lending protocolo #1)
            'TIA': Decimal('25000000000'),    # $25B (Modular blockchain revolucionário)
            'IMX': Decimal('10000000000'),    # $10B (Gaming/NFT Layer 2 dominante)
            'KAS': Decimal('15000000000'),    # $15B (DAG + PoW inovador)
        }

        # Categorias (para diversificação)
        self.categorias = {
            'BTC': 'Blue Chip',
            'ETH': 'Blue Chip',
            'SOL': 'Layer 1',
            'LINK': 'Infraestrutura',
            'MATIC': 'Layer 2',
            'RNDR': 'AI/DePIN',
            'AAVE': 'DeFi',
            'TIA': 'Modular',
            'IMX': 'Gaming/NFT',
            'KAS': 'Layer 1 Alternativo',
        }

    def analisar_ativo(self, simbolo: str) -> Optional[AnaliseCripto]:
        """
        Analisa um criptoativo completo (AF + AT + Modelagem).

        Args:
            simbolo: Símbolo do ativo (ex: BTC, ETH, SOL)

        Returns:
            AnaliseCripto ou None se falhar
        """
        try:
            # Mapear símbolo para ticker Yahoo Finance
            ticker_map = {
                'BTC': 'BTC-USD',
                'ETH': 'ETH-USD',
                'SOL': 'SOL-USD',
                'LINK': 'LINK-USD',
                'MATIC': 'MATIC-USD',
                'RNDR': 'RNDR-USD',
                'AAVE': 'AAVE-USD',
                'TIA': 'TIA-USD',
                'IMX': 'IMX-USD',
                'KAS': 'KAS-USD',
            }

            ticker_yahoo = ticker_map.get(simbolo)
            if not ticker_yahoo:
                print(f"❌ Símbolo {simbolo} não mapeado")
                return None

            # Coletar dados
            ticker = yf.Ticker(ticker_yahoo)
            info = ticker.info
            historico = ticker.history(period="1mo")

            if historico.empty:
                print(f"❌ Sem dados para {simbolo}")
                return None

            # Preço atual
            preco_atual = Decimal(str(historico['Close'].iloc[-1]))

            # Market Cap atual
            market_cap_atual = Decimal(str(info.get('marketCap', 0)))
            if market_cap_atual == 0:
                # Fallback: estimar MC = circulating supply * preço
                print(f"⚠️  Market Cap não disponível para {simbolo}, usando estimativa")
                market_cap_atual = preco_atual * Decimal('1000000')  # Placeholder

            # Volatilidade e extremos 30 dias
            preco_minimo = Decimal(str(historico['Close'].min()))
            preco_maximo = Decimal(str(historico['Close'].max()))

            # Volatilidade (desvio padrão dos retornos diários)
            retornos = historico['Close'].pct_change().dropna()
            volatilidade = Decimal(str(retornos.std() * np.sqrt(30) * 100))  # Anualizada em %

            # Distâncias
            distancia_minima = ((preco_atual - preco_minimo) / preco_minimo * 100) if preco_minimo > 0 else Decimal('0')
            distancia_maxima = ((preco_maximo - preco_atual) / preco_atual * 100) if preco_atual > 0 else Decimal('0')

            # Nome
            nome = info.get('name', simbolo)

            # Categoria
            categoria = self.categorias.get(simbolo, 'Outros')

            # Tese de fundação (específica por ativo)
            tese = self._gerar_tese_fundacao(simbolo)

            # Scores fundamentalistas (heurística - seria aprimorada com dados on-chain)
            utility_score = self._calcular_utility_score(simbolo)
            adocao_score = self._calcular_adocao_score(simbolo, info)

            # Análise Técnica: Pontos críticos
            ponto_critico = preco_minimo * Decimal('0.90')  # 10% abaixo da mínima = invalidação
            preco_ideal = preco_minimo * Decimal('1.05')     # Próximo à mínima (zona de demanda)
            preco_teto = preco_maximo * Decimal('0.95')      # Próximo à máxima (resistência)

            # Projeção 2 anos
            mc_projetado = self.projecoes_market_cap.get(simbolo, market_cap_atual * Decimal('5'))

            # Supply (simplificado - seria coletado de API específica)
            # Para calcular preço projetado = MC_projetado / Supply_circulante
            # Aqui vamos usar uma aproximação: preço_proj = preço_atual * (MC_proj / MC_atual)
            multiplo_retorno = mc_projetado / market_cap_atual if market_cap_atual > 0 else Decimal('1')
            preco_projetado = preco_atual * multiplo_retorno

            # Calcular scores
            score_fundamentos = self._calcular_score_fundamentos(utility_score, adocao_score)
            score_tecnico = self._calcular_score_tecnico(volatilidade, distancia_minima, distancia_maxima)
            score_projecao = self._calcular_score_projecao(multiplo_retorno, categoria)

            # Score final (Fundamentos 40%, Técnico 30%, Projeção 30%)
            score_final = int(
                score_fundamentos * 0.40 +
                score_tecnico * 0.30 +
                score_projecao * 0.30
            )

            # Peso sugerido na carteira (baseado em categoria e score)
            peso_sugerido = self._calcular_peso_carteira(categoria, score_final)

            # Justificativa de retorno
            justificativa = self._gerar_justificativa_retorno(simbolo, multiplo_retorno, categoria)

            # Riscos e catalisadores
            riscos = self._identificar_riscos(simbolo, volatilidade, categoria)
            catalistas = self._identificar_catalistas(simbolo, categoria)

            # Criar análise
            analise = AnaliseCripto(
                simbolo=simbolo,
                nome=nome,
                categoria=categoria,
                tese_fundacao=tese,
                utility_score=utility_score,
                adocao_score=adocao_score,
                preco_atual=preco_atual,
                market_cap_atual=market_cap_atual,
                preco_minimo_30d=preco_minimo,
                preco_maximo_30d=preco_maximo,
                volatilidade_30d=volatilidade,
                ponto_critico=ponto_critico,
                preco_ideal_compra=preco_ideal,
                preco_teto_acumulo=preco_teto,
                distancia_minima=distancia_minima,
                distancia_maxima=distancia_maxima,
                market_cap_projetado=mc_projetado,
                preco_projetado=preco_projetado,
                multiplo_retorno=multiplo_retorno,
                score_fundamentos=score_fundamentos,
                score_tecnico=score_tecnico,
                score_projecao=score_projecao,
                score_final=score_final,
                peso_sugerido=peso_sugerido,
                justificativa_retorno=justificativa,
                riscos=riscos,
                catalistas=catalistas
            )

            return analise

        except Exception as e:
            print(f"❌ Erro ao analisar {simbolo}: {e}")
            return None

    def _gerar_tese_fundacao(self, simbolo: str) -> str:
        """Gera tese fundamentalista específica do ativo."""
        teses = {
            'BTC': 'Reserva de valor digital (ouro 2.0), escassez programática (21M), adoção institucional crescente',
            'ETH': 'Plataforma de contratos inteligentes dominante, transição PoS, base para DeFi/NFTs/RWA',
            'SOL': 'Alta throughput (65k TPS), baixas taxas, ecossistema DeFi+NFT+Gaming em expansão',
            'LINK': 'Oráculos descentralizados padrão-ouro, integração com CBDCs, tokenização RWA',
            'MATIC': 'Layer 2 Ethereum líder, soluções zkEVM, parcerias enterprise (Disney, Starbucks)',
            'RNDR': 'Rede descentralizada de renderização GPU, pivô para AI compute, DePIN promissor',
            'AAVE': 'Protocolo lending/borrowing líder ($10B+ TVL), governança ativa, GHO stablecoin',
            'TIA': 'Modular blockchain (consenso separado de execução), inovação arquitetural, rollups-as-a-service',
            'IMX': 'Layer 2 zkRollup para gaming/NFTs, zero gas fees, parcerias AAA games (Gods Unchained, Guild of Guardians)',
            'KAS': 'DAG + PoW (BlockDAG), alta escalabilidade sem sacrificar descentralização, comunidade forte',
        }
        return teses.get(simbolo, 'Tese não definida')

    def _calcular_utility_score(self, simbolo: str) -> int:
        """Calcula score de utilidade (0-100)."""
        # Heurística baseada em maturidade e casos de uso
        scores = {
            'BTC': 95,  # Store of value estabelecido
            'ETH': 95,  # Plataforma madura
            'SOL': 85,  # Ecossistema crescente
            'LINK': 90,  # Oráculos essenciais
            'MATIC': 85, # Layer 2 consolidado
            'RNDR': 80,  # DePIN emergente
            'AAVE': 90,  # DeFi blue chip
            'TIA': 75,   # Tecnologia nova mas promissora
            'IMX': 80,   # Gaming/NFT nicho forte
            'KAS': 70,   # Tecnologia inovadora mas early
        }
        return scores.get(simbolo, 50)

    def _calcular_adocao_score(self, simbolo: str, info: dict) -> int:
        """Calcula score de adoção baseado em métricas de mercado."""
        # Volume, liquidez, holders (simplificado)
        volume = info.get('volume24Hr', 0)

        if volume > 1000000000:  # >$1B
            return 90
        elif volume > 100000000:  # >$100M
            return 75
        elif volume > 10000000:  # >$10M
            return 60
        else:
            return 40

    def _calcular_score_fundamentos(self, utility: int, adocao: int) -> int:
        """Score fundamentalista (média ponderada)."""
        return int(utility * 0.6 + adocao * 0.4)

    def _calcular_score_tecnico(
        self,
        volatilidade: Decimal,
        dist_minima: Decimal,
        dist_maxima: Decimal
    ) -> int:
        """Score técnico (volatilidade + posição no range)."""
        score = 50

        # Volatilidade (menor = melhor para entrada)
        if volatilidade < 30:
            score += 20  # Baixa volatilidade
        elif volatilidade < 50:
            score += 10
        elif volatilidade > 80:
            score -= 20  # Alta volatilidade = risco

        # Posição no range 30d (mais próximo da mínima = melhor)
        if dist_minima < 10:
            score += 30  # Muito próximo da mínima
        elif dist_minima < 20:
            score += 20
        elif dist_minima > 50:
            score -= 10  # Longe da mínima (caro)

        return max(0, min(100, score))

    def _calcular_score_projecao(self, multiplo: Decimal, categoria: str) -> int:
        """Score de projeção (potencial de retorno)."""
        score = 50

        # Múltiplo de retorno
        if multiplo >= 20:
            score += 40  # 20x+ = altíssimo potencial
        elif multiplo >= 10:
            score += 30  # 10-20x = alto potencial
        elif multiplo >= 5:
            score += 20  # 5-10x = bom potencial
        elif multiplo >= 3:
            score += 10  # 3-5x = moderado
        else:
            score -= 10  # <3x = baixo para cripto

        # Categoria (ajuste de risco)
        if categoria == 'Blue Chip':
            score += 10  # Menor risco
        elif categoria in ['AI/DePIN', 'Modular']:
            score += 5   # Alto potencial narrativa

        return max(0, min(100, score))

    def _calcular_peso_carteira(self, categoria: str, score: int) -> Decimal:
        """Calcula peso sugerido na carteira (%)."""
        # Base de alocação por categoria
        pesos_base = {
            'Blue Chip': Decimal('20'),        # 20% cada (40% total)
            'Layer 1': Decimal('10'),
            'Layer 2': Decimal('8'),
            'Infraestrutura': Decimal('10'),
            'DeFi': Decimal('8'),
            'AI/DePIN': Decimal('10'),
            'Modular': Decimal('8'),
            'Gaming/NFT': Decimal('8'),
            'Layer 1 Alternativo': Decimal('8'),
        }

        peso_base = pesos_base.get(categoria, Decimal('10'))

        # Ajustar pelo score (±30%)
        if score >= 80:
            peso_ajustado = peso_base * Decimal('1.3')
        elif score >= 70:
            peso_ajustado = peso_base * Decimal('1.15')
        elif score < 60:
            peso_ajustado = peso_base * Decimal('0.7')
        else:
            peso_ajustado = peso_base

        return peso_ajustado

    def _gerar_justificativa_retorno(
        self,
        simbolo: str,
        multiplo: Decimal,
        categoria: str
    ) -> str:
        """Gera justificativa para o múltiplo de retorno projetado."""
        justificativas = {
            'BTC': f'Adoção institucional (ETFs), halving 2024, ouro digital mainstream → {float(multiplo):.1f}x realista',
            'ETH': f'Merge PoS, Layer 2 scaling, RWA tokenization, ETFs spot → {float(multiplo):.1f}x conservador',
            'SOL': f'Performance superior, ecossistema crescente, recuperação FTX superada → {float(multiplo):.1f}x factível',
            'LINK': f'Oráculos padrão, CCIP cross-chain, CBDCs, RWA tokenization → {float(multiplo):.1f}x fundamentado',
            'MATIC': f'zkEVM liderança, Polygon 2.0, parcerias enterprise → {float(multiplo):.1f}x atingível',
            'RNDR': f'AI boom, DePIN narrativa, escassez GPUs, pivô compute → {float(multiplo):.1f}x explosivo',
            'AAVE': f'DeFi líder, GHO stablecoin, real yield, governança ativa → {float(multiplo):.1f}x sólido',
            'TIA': f'Modular blockchain revolucionário, RaaS, eficiência validadores → {float(multiplo):.1f}x disruptivo',
            'IMX': f'Gaming mass adoption, AAA partnerships, zero fees → {float(multiplo):.1f}x promissor',
            'KAS': f'BlockDAG inovação, comunidade forte, PoW sustentável → {float(multiplo):.1f}x especulativo',
        }
        return justificativas.get(simbolo, f'Projeção baseada em crescimento do setor {categoria}')

    def _identificar_riscos(self, simbolo: str, volatilidade: Decimal, categoria: str) -> List[str]:
        """Identifica riscos específicos do ativo."""
        riscos = []

        if volatilidade > 60:
            riscos.append(f'Alta volatilidade ({float(volatilidade):.1f}%)')

        if categoria in ['AI/DePIN', 'Modular', 'Gaming/NFT']:
            riscos.append('Narrativa emergente (alto risco/retorno)')

        if simbolo in ['SOL']:
            riscos.append('Histórico de downtime de rede')

        if simbolo in ['KAS']:
            riscos.append('Listagens limitadas em exchanges tier-1')

        riscos.append('Risco regulatório global (SEC, MiCA)')
        riscos.append('Correlação com BTC/macroeconomia')

        return riscos[:3]  # Top 3 riscos

    def _identificar_catalistas(self, simbolo: str, categoria: str) -> List[str]:
        """Identifica catalisadores de valorização."""
        catalistas_gerais = {
            'BTC': ['Halving 2024', 'ETFs spot aprovados', 'Adoção El Salvador/países'],
            'ETH': ['EIP-4844 (Dencun)', 'Layer 2 boom', 'ETFs spot'],
            'SOL': ['Firedancer upgrade', 'Mobile (Saga)', 'DePIN liderança'],
            'LINK': ['CCIP mainnet', 'CBDCs partnerships', 'Staking v0.2'],
            'MATIC': ['Polygon 2.0 rollout', 'zkEVM adoption', 'Disney/Nike NFTs'],
            'RNDR': ['AI compute demand', 'Apple Vision Pro', 'Cloud rendering'],
            'AAVE': ['GHO expansion', 'V4 protocol', 'Real-world assets'],
            'TIA': ['Mainnet launch', 'Rollups ecosystem', 'Modular thesis'],
            'IMX': ['Gods Unchained mobile', 'AAA games Q1 2026', 'Immutable Passport'],
            'KAS': ['Binance listing', 'ASIC resistance', 'BlockDAG papers'],
        }
        return catalistas_gerais.get(simbolo, ['Crescimento do setor', 'Adoção mainstream', 'Inovação tecnológica'])

    def analisar_carteira(self, simbolos: List[str]) -> List[AnaliseCripto]:
        """
        Analisa carteira completa de criptoativos.

        Args:
            simbolos: Lista de símbolos (ex: ['BTC', 'ETH', 'SOL'])

        Returns:
            Lista de análises ordenadas por score
        """
        print(f"\n{'='*80}")
        print("🚀 ANÁLISE INTEGRADA DE CARTEIRA DE CRIPTOATIVOS")
        print(f"{'='*80}")
        print(f"Ativos: {', '.join(simbolos)}")
        print(f"Horizonte: 2 anos (24-36 meses)")
        print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}\n")

        analises = []

        for simbolo in simbolos:
            print(f"🔍 Analisando {simbolo}...", end=" ")
            analise = self.analisar_ativo(simbolo)

            if analise:
                analises.append(analise)
                print(f"✅ Score: {analise.score_final} | Múltiplo: {float(analise.multiplo_retorno):.1f}x")
            else:
                print(f"❌ Falhou")

        # Ordenar por score final
        analises.sort(key=lambda x: x.score_final, reverse=True)

        # Normalizar pesos (somar 100%)
        soma_pesos = sum(a.peso_sugerido for a in analises)
        if soma_pesos > 0:
            for analise in analises:
                analise.peso_sugerido = (analise.peso_sugerido / soma_pesos) * 100

        self.analises = analises
        return analises

    def gerar_tabela_analitica(self) -> str:
        """Gera tabela analítica horizontal completa."""
        if not self.analises:
            return "❌ Nenhuma análise disponível"

        tabela = "\n## 📊 TABELA ANALÍTICA HORIZONTAL\n\n"
        tabela += "| Ativo | Fundação da Decisão (Tese) | Volatilidade 30D: AT (Máx/Mín/Crítico) | "
        tabela += "Preço Ideal Compra | Preço Teto Acúmulo | Projeção Valorização (2 anos) |\n"
        tabela += "| :--- | :--- | :--- | :--- | :--- | :--- |\n"

        for a in self.analises:
            # Ativo
            linha = f"| **{a.simbolo}** ({a.categoria}) | "

            # Tese
            linha += f"{a.tese_fundacao[:80]}... | "

            # Volatilidade AT
            linha += f"Vol: {float(a.volatilidade_30d):.1f}% | "
            linha += f"Máx: ${float(a.preco_maximo_30d):.2f} | "
            linha += f"Mín: ${float(a.preco_minimo_30d):.2f} | "
            linha += f"Crítico: ${float(a.ponto_critico):.2f} | "

            # Preço Ideal
            linha += f"${float(a.preco_ideal_compra):.2f} (suporte forte) | "

            # Preço Teto
            linha += f"${float(a.preco_teto_acumulo):.2f} (resistência) | "

            # Projeção
            linha += f"**{float(a.multiplo_retorno):.1f}x** | "
            linha += f"CMP: ${float(a.market_cap_projetado)/1e9:.0f}B / "
            linha += f"MC atual: ${float(a.market_cap_atual)/1e9:.1f}B | "
            linha += f"R$ 100 → R$ {float(a.multiplo_retorno) * 100:.0f} |\n"

            tabela += linha

        return tabela

    def gerar_resumo_executivo(self) -> str:
        """Gera resumo executivo com projeção consolidada."""
        if not self.analises:
            return "❌ Nenhuma análise disponível"

        # Calcular retorno médio ponderado
        retorno_ponderado = sum(
            float(a.multiplo_retorno) * float(a.peso_sugerido) / 100
            for a in self.analises
        )

        resumo = "\n## 🚀 PROJEÇÃO DE POTENCIAL DE VALORIZAÇÃO E JUSTIFICATIVA\n\n"
        resumo += f"### A projeção para a carteira diversificada é de:\n\n"
        resumo += f"**Cada R$ 100 investidos podem se tornar R$ {retorno_ponderado * 100:.0f} em até 02 anos.**\n\n"

        resumo += "### Fundamentação da Projeção (Modelagem Financeira)\n\n"
        resumo += "A projeção conservadora baseia-se em múltiplos de Market Cap realistas:\n\n"

        # Agrupar por categoria
        blue_chips = [a for a in self.analises if a.categoria == 'Blue Chip']
        infra = [a for a in self.analises if a.categoria in ['Layer 1', 'Layer 2', 'Infraestrutura']]
        apostas = [a for a in self.analises if a.categoria in ['AI/DePIN', 'Modular', 'Gaming/NFT', 'Layer 1 Alternativo', 'DeFi']]

        if blue_chips:
            resumo += "**Blue Chips (BTC/ETH):** "
            resumo += "Adoção institucional (ETFs), halvings, transição para store-of-value global. "
            media_bc = sum(float(a.multiplo_retorno) for a in blue_chips) / len(blue_chips)
            resumo += f"Múltiplo médio: {media_bc:.1f}x.\n\n"

        if infra:
            resumo += "**Infraestrutura (Layer 1/Layer 2):** "
            resumo += "Scaling solutions, oráculos, interoperabilidade. Crescimento DeFi+NFT+Gaming. "
            media_infra = sum(float(a.multiplo_retorno) for a in infra) / len(infra)
            resumo += f"Múltiplo médio: {media_infra:.1f}x.\n\n"

        if apostas:
            resumo += "**Apostas de Crescimento (AI/Gaming/Modular):** "
            resumo += "Narrativas emergentes (AI compute, DePIN, modularidade, gaming mass adoption). "
            media_apostas = sum(float(a.multiplo_retorno) for a in apostas) / len(apostas)
            resumo += f"Múltiplo médio: {media_apostas:.1f}x.\n\n"

        resumo += "### 📈 Próximo Passo: Alocação de Risco e Capital\n\n"
        resumo += "| Ativo | Peso Sugerido | Justificativa |\n"
        resumo += "| :--- | :---: | :--- |\n"

        for a in self.analises:
            resumo += f"| {a.simbolo} | {float(a.peso_sugerido):.1f}% | {a.justificativa_retorno[:60]}... |\n"

        return resumo


# Teste standalone
if __name__ == "__main__":
    analisador = AnalisadorCarteiraCripto()

    # Carteira sugerida
    simbolos = ['BTC', 'ETH', 'SOL', 'LINK', 'MATIC', 'RNDR', 'AAVE', 'TIA', 'IMX', 'KAS']

    analises = analisador.analisar_carteira(simbolos)

    if analises:
        print(analisador.gerar_tabela_analitica())
        print(analisador.gerar_resumo_executivo())
