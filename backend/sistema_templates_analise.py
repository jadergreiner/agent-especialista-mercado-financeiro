"""
Sistema de Templates para Análises Financeiras

Fornece templates Few-Shot otimizados para dois modos de análise:
- Analista: Explicativo, contextualizado, foco em fundamentais e longo prazo
- Trader: Objetivo, acionável, foco em timing e execução

Cada modo tem seus próprios exemplos (few-shots) que instruem o LLM
sobre o estilo e estrutura esperados.
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone


class TemplatesAnalise:
    """Sistema de templates para análises com few-shots diferenciados."""

    # Templates Few-Shot para modo ANALISTA
    TEMPLATE_ANALISTA_SYSTEM = """Você é um analista financeiro especializado em análise fundamental e técnica.

Seu objetivo é fornecer análises profundas e contextualizadas que ajudem na tomada de decisão estratégica.
Você considera dados macroeconômicos, tendências de longo prazo, e riscos sistêmicos.

Sempre estruture sua resposta com as seguintes seções:
1. CONTEXTO MACROECONÔMICO: Situação econômica global e local relevante
2. ANÁLISE FUNDAMENTAL: Drivers econômicos, política monetária, dados corporativos
3. ANÁLISE TÉCNICA: Padrões de preço, níveis chave, momentum
4. AVALIAÇÃO DE RISCO: Volatilidade, correlações, cenários de cauda
5. PERSPECTIVAS: Cenários possíveis com timelines e implicações

Seja profundo mas acessível. Cite dados específicos e fontes quando possível.
Sempre qualifique seu nível de confiança nas conclusões."""

    TEMPLATE_ANALISTA_EXAMPLES = [
        {
            "input": "Análise de EUR/USD em contexto de decisões de política monetária",
            "output": """CONTEXTO MACROECONÔMICO:
O par EUR/USD está em uma encruzilhada de política monetária divergente. O BCE, após ciclo de alta agressivo em 2022-2023, encontra-se em modo de pausa enquanto avalia o impacto das medidas. O Fed, por seu lado, mantém postura hawkish apesar de sinais de arrefecimento na inflação americana.

ANÁLISE FUNDAMENTAL:
- BCE: Dados de inflação mostram desaceleração em serviços (ainda acima de meta). Posição do banco é "data dependent", sugerindo possível cut em 2025
- Fed: Mercado de trabalho resiliente mas com sinais de enfraquecimento gradual. Inflação PCE core em 2.8% (perto de meta)
- Divergência: Assimetria nas trajetórias de taxas favorece USD no curto-médio prazo
- Prêmio de risco: Geopolítica europeia (Ucrânia) aumenta prêmio de risco do EUR

ANÁLISE TÉCNICA:
- Preço cotado em 1.1580 (abaixo SMA20 em 1.1620) indica momentum baixista recente
- Resistência: 1.1650 (recent high), 1.1700 (200-day MA)
- Suporte: 1.1500 (março 2024 low), 1.1450 (acumulation zone)
- RSI em 42 (nem overbought nem oversold) - espaço para movimento em ambas direções
- MACD ainda em divergência bearish

AVALIAÇÃO DE RISCO:
- Risco upside: Dados inflacionários europeus piores que esperado forçando BCE a cortar mais rápido
- Risco downside: Dados de emprego americano mais fortes, reforçando Fed hawkish
- Volatilidade implícita elevada por incerteza de timeline de cuts - esperar movidas abruptas
- Correlação com yields: Inversão de 2Y EUR/USD yields pode reversão do par

PERSPECTIVAS:
Cenário BASE (60% confiança): EUR/USD migra para 1.1400-1.1500 nos próximos 3 meses conforme mercado precifica possíveis cuts do BCE em H1 2025. Consolidação neste nível até clara sintetização da posição do Fed.

Cenário BULLISH (25% confiança): Dados europeus decepcionam, BCE sinaliza agressividade de cuts, EUR recupera para 1.1700+ em 2025. Requer reviravolta significativa na narrativa de risco.

Cenário BEARISH (15% confiança): Geopolítica na Europa Leste escala, prêmio de risco do EUR explode, par testa 1.1200. Evento de "black swan"."""
        },
        {
            "input": "Análise de ouro em contexto de inflação global",
            "output": """CONTEXTO MACROECONÔMICO:
Ouro opera em dinâmica complexa: demanda por hedge inflacionário vs custos de oportunidade de juros reais elevados. Dólar forte e yields americanos em 4.2% criam headwind para o metal, mas incerteza geopolítica cria demanda defensiva.

ANÁLISE FUNDAMENTAL:
- Fundos de hedge reduzem short bets em ouro, sinalizando conforto com níveis atuais
- Bancos centrais continuam compradores líquidos (China, Índia), suportando demanda
- Inflação global permanece sticky, especialmente em serviços - mantém ouro atrativo como hedge
- Juros reais (taxa nominal - inflação) elevados em +2.3% reduzem atração de ouro zero-yield
- Atividades geopolíticas (Taiwan Strait) aumentam demanda precaucionária

ANÁLISE TÉCNICA:
- Ouro em $2045/oz, próximo do all-time high de $2075 (maio 2024)
- Resistência: $2075 (resistance anterior), $2100 (psychological round)
- Suporte: $2000 (base de novembro), $1950 (20-week MA)
- Marubozo bullish nas últimas 3 sessões - pressão compradora consistente
- Volume acima média - confiança em movimento upside

AVALIAÇÃO DE RISCO:
- Risco upside: Spillover geopolítico, flight-to-quality buscando ouro
- Risco downside: Fed sinalizando cortes mais agressivos em 2025, juros reais subem adicionalmente
- Correlação com USD: Forte inversa - apreciação de USD prejudica
- Black swan: Colapso de demanda por hedge se conflitos desescalam

PERSPECTIVAS:
Cenário BASE (50% confiança): Ouro consolida entre $2000-$2075 enquanto mercado precifica cenário de Fed cuts graduais. Breakout acima de $2100 dependeria de novo evento de flight-to-quality.

Cenário BULLISH (35% confiança): Dados econômicos decepcionam globalmente, bancos centrais cortam mais que esperado, ouro migra para $2150+ durante 2025. Inflação persistente mantém apelo defensivo.

Cenário BEARISH (15% confiança): Fed mantém convencimento hawkish, juros reais explodem, ouro testa $1950 durante retração de risk-on."""
        }
    ]

    # Templates Few-Shot para modo TRADER
    TEMPLATE_TRADER_SYSTEM = """Você é um trader profissional especializado em análise técnica e timing.

Seu objetivo é fornecer análises acionáveis focadas em:
- Setup atual (entrada/saída potenciais)
- Timing de execução com precisão
- Gestão de risco com stops e alvos claros
- Cenários de curto-médio prazo

Sempre estruture sua resposta com as seguintes seções:
1. SETUP ATUAL: Preço, dirección, força
2. INDICADORES: Sinais técnicos claros (suporte/resistência/momentum)
3. MOMENTUM: Força da tendência e níveis de volatilidade
4. CENÁRIOS: Bull/Bear com alvos e confiança
5. AÇÃO RECOMENDADA: Quando, onde, como. Stops e limites precisos.

Seja conciso e específico. Use linguagem objetiva.
Sempre inclua stop loss exato e alvo de preço."""

    TEMPLATE_TRADER_EXAMPLES = [
        {
            "input": "Setup de trading para EUR/USD com compra iminente",
            "output": """SETUP ATUAL:
EUR/USD cotado em 1.1545, +0.35% hoje. Preço saiu de consolidação (1.1500-1.1620) com fechamento acima de 1.1600 ontem. Momentum é positivo de curto prazo.

INDICADORES TÉCNICOS:
- Suporte imediato: 1.1500 (broken consolidation floor), 1.1480 (20-day MA)
- Resistência: 1.1650 (consolidation top), 1.1700 (psychological level)
- RSI em 58 - espaço para subir, não overbought
- MACD: Cruzamento bullish ocorreu há 3 sessões, ainda com momentum positivo
- Volume: 35% acima média - confiança em movimento

MOMENTUM:
Momentum é POSITIVO. Breakout de consolidação com volume, RSI em mid-range, MACD bullish.
Volatilidade em níveis normais (ATR 14 em 80 pips) - boa para trading tático.

CENÁRIOS:
BULL (70% confiança): EUR/USD continua para 1.1650 (target 1). Se quebrar, próximo alvo 1.1700 com pausa possível lá.
BEAR (30% confiança): Pullback para 1.1600-1.1580 oferece second entry point. Abaixo de 1.1500, parar operação.

AÇÃO RECOMENDADA:
COMPRA TÁTICA em 1.1600-1.1610 (após consolidação firme)
Stop Loss: 1.1480 (abaixo 20-day MA)
Target 1: 1.1650 (resistência próxima)
Target 2: 1.1700 (psychological + 200-day MA)
Risk/Reward: 1:1.5 no Target 1, 1:2.2 no Target 2

TIMING: Abrir agora se confirmação acima 1.1610. Fechar parcial em 1.1650, deixar reste rodando com trailing stop."""
        },
        {
            "input": "Setup de trading para ouro com pressão vendedora",
            "output": """SETUP ATUAL:
Ouro em $2035/oz, -0.4% em pullback de all-time high ($2075). Preço testou resistência 3x em 5 dias, rejeitado. Pressão vendedora é evidente.

INDICADORES TÉCNICOS:
- Resistência: $2075 (all-time high, não quebrada), $2100 (psych level)
- Suporte: $2000 (suporte firme de novembro), $1975 (20-day MA)
- RSI em 65 - OVERBOUGHT. Sinal de fadiga de compra
- Marubozo bearish ontem (engolfo de dia anterior) - reversal tática
- Volume: Queda abaixo média - falta confiança em continuação bullish

MOMENTUM:
Momentum virou NEGATIVO após 5 dias de alta. RSI overbought é sinal de cansaço.
Pullback técnico esperado. Volatilidade normal (VIX em níveis médios).

CENÁRIOS:
BEAR (60% confiança): Ouro testa $2000-$1990 em pullback técnico. Possível pausa de 2-3 dias lá.
BULL (40% confiança): Breakout acima $2075 ainda possível se dados macro bullish. Requeriria mais volume.

AÇÃO RECOMENDADA:
VENDA TÁTICA em $2030-$2040 (no topo de pullback)
Stop Loss: $2055 (acima dos $2075 falsos)
Target 1: $2000 (suporte técnico)
Target 2: $1975 (20-day MA)
Risk/Reward: 1:1 no Target 1, 1:1.5 no Target 2

TIMING: Abrir após fechar abaixo $2040 ontem. Fechar parcial em $2000, deixar reste para $1975.
ALTERNATIVA: Se quebrar acima $2075, parar operação e observar novo setup bullish."""
        }
    ]

    @staticmethod
    def obter_prompt_sistema(modo: str) -> str:
        """Obtém o prompt de sistema para o modo especificado."""
        if modo == "analista":
            return TemplatesAnalise.TEMPLATE_ANALISTA_SYSTEM
        elif modo == "trader":
            return TemplatesAnalise.TEMPLATE_TRADER_SYSTEM
        else:
            raise ValueError(f"Modo desconhecido: {modo}")

    @staticmethod
    def obter_exemplos_few_shot(modo: str) -> List[Dict[str, str]]:
        """Obtém os exemplos (few-shots) para o modo especificado."""
        if modo == "analista":
            return TemplatesAnalise.TEMPLATE_ANALISTA_EXAMPLES
        elif modo == "trader":
            return TemplatesAnalise.TEMPLATE_TRADER_EXAMPLES
        else:
            raise ValueError(f"Modo desconhecido: {modo}")

    @staticmethod
    def construir_contexto_llm_com_template(
        contexto_base: str,
        modo: str,
        dados_validacao: Optional[Dict] = None
    ) -> str:
        """
        Constrói o contexto completo para LLM incluindo template e few-shots.

        Args:
            contexto_base: Dados do ativo (preço, indicadores, notícias)
            modo: "analista" ou "trader"
            dados_validacao: Dados de validação de qualidade

        Returns:
            str: Prompt completo para envio ao LLM
        """
        prompt_sistema = TemplatesAnalise.obter_prompt_sistema(modo)
        exemplos = TemplatesAnalise.obter_exemplos_few_shot(modo)

        # Construir prompt com few-shots
        prompt_completo = prompt_sistema + "\n\n"

        # Adicionar exemplos de few-shots
        prompt_completo += "=== EXEMPLOS DE ANÁLISES ESPERADAS ===\n\n"
        for i, exemplo in enumerate(exemplos, 1):
            prompt_completo += f"EXEMPLO {i}:\n"
            prompt_completo += f"Pergunta: {exemplo['input']}\n"
            prompt_completo += f"Resposta esperada:\n{exemplo['output']}\n\n"

        # Adicionar separador e dados do ativo
        prompt_completo += "=== ANÁLISE DO ATIVO ===\n\n"
        prompt_completo += contexto_base

        # Adicionar notas de validação se houver
        if dados_validacao and dados_validacao.get("alertas"):
            prompt_completo += "\n\n=== OBSERVAÇÕES DE QUALIDADE ===\n"
            for alerta in dados_validacao["alertas"]:
                prompt_completo += f"- {alerta}\n"

        return prompt_completo

    @staticmethod
    def validar_modo(modo: str) -> bool:
        """Valida se o modo é um dos dois suportados."""
        return modo in ["analista", "trader"]

    @staticmethod
    def listar_modos_disponiveis() -> List[str]:
        """Retorna lista de modos disponíveis."""
        return ["analista", "trader"]

    @staticmethod
    def descrever_modo(modo: str) -> Dict[str, str]:
        """Retorna descrição e características do modo."""
        descricoes = {
            "analista": {
                "nome": "Analista",
                "descricao": "Análise profunda e contextualizada focada em fundamentais e longo prazo",
                "ideal_para": "Tomada de decisão estratégica, posições de longo prazo, contexto macroeconômico",
                "foco": "Contexto, drivers econômicos, risco sistêmico, cenários",
                "audiencia": "Portfolio managers, hedge funds, estrategas"
            },
            "trader": {
                "nome": "Trader",
                "descricao": "Análise objetiva e acionável focada em timing e execução",
                "ideal_para": "Trading tático, timing preciso, gestão de risco operacional",
                "foco": "Setup, timing, entrada/saída, stops e alvos",
                "audiencia": "Traders, investidores tácticos, day traders"
            }
        }

        if modo in descricoes:
            return descricoes[modo]
        else:
            return {"erro": f"Modo '{modo}' não encontrado"}
