"""
Validadores: Disclaimers e Segurança

Garante conformidade e proteção contra interpretações prescritivas.
"""

import logging
import re
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


DISCLAIMER_PADRAO = """
⚠️ AVISO IMPORTANTE:
Esta análise é APENAS para fins informativos e educacionais.
NÃO constitui recomendação de investimento, consultoria financeira ou incitação à compra/venda de ativos.
Mercados financeiros envolvem risco substancial de perda de capital.
Consulte um profissional qualificado e autorizado antes de tomar decisões de investimento.
Desempenho passado não garante resultados futuros.
""".strip()


# Palavras e padrões proibidos (linguagem prescritiva)
PALAVRAS_PROIBIDAS = [
    r"\bcompre\b",
    r"\bvenda\b",
    r"\bcomprar\b",
    r"\bvender\b",
    r"\brecomend[oa]\b",
    r"\bgarant[io]\b",
    r"\bcerteza\b",
    r"\bsem risco\b",
    r"\blica[oa]?\b",  # "Lícia" ou "Lício" no contexto financeiro
    r"\bdeve comprar\b",
    r"\bdeve vender\b",
    r"\bvai subir\b",
    r"\bvai cair\b",
    r"\bentrar (agora|já)\b",
    r"\bsair (agora|já)\b",
]


def aplicar_disclaimer(analise: Dict) -> Dict:
    """
    Injeta disclaimer padrão na estrutura de análise.

    Args:
        analise: Dicionário com dados da análise

    Returns:
        dict: Análise com disclaimer adicionado
    """
    analise_com_disclaimer = analise.copy()
    analise_com_disclaimer["disclaimer"] = DISCLAIMER_PADRAO
    logger.debug("Disclaimer aplicado à análise")
    return analise_com_disclaimer


def validar_linguagem_prescritiva(texto: str) -> Tuple[bool, List[str]]:
    """
    Detecta linguagem prescritiva ou inapropriada no texto.

    Args:
        texto: Texto a ser validado

    Returns:
        tuple: (is_valid, lista_de_violacoes)
            - is_valid: False se encontrou violações
            - lista_de_violacoes: Lista de palavras/padrões detectados
    """
    texto_lower = texto.lower()
    violacoes = []

    for padrao in PALAVRAS_PROIBIDAS:
        if re.search(padrao, texto_lower, re.IGNORECASE):
            violacoes.append(padrao.replace(r"\b", "").replace("\\", ""))

    if violacoes:
        logger.warning(f"Linguagem prescritiva detectada: {violacoes}")
        return False, violacoes

    logger.debug("Validação de linguagem prescritiva: OK")
    return True, []


def sanitizar_texto(texto: str) -> str:
    """
    Remove ou substitui linguagem prescritiva detectada.

    Args:
        texto: Texto original

    Returns:
        str: Texto sanitizado
    """
    texto_sanitizado = texto

    # Substituições comuns
    substituicoes = {
        r"\bcompre\b": "considere analisar",
        r"\bvenda\b": "avalie a posição",
        r"\bcomprar\b": "analisar",
        r"\bvender\b": "avaliar",
        r"\brecomendo\b": "observo que",
        r"\brecomenda\b": "observa-se que",
        r"\bgaranto\b": "sugiro prudência",
        r"\bgarantido\b": "possível",
        r"\bcerteza\b": "probabilidade",
        r"\bsem risco\b": "com risco controlado",
        r"\bdeve comprar\b": "pode considerar analisar",
        r"\bdeve vender\b": "pode considerar avaliar",
        r"\bvai subir\b": "pode apresentar tendência de alta",
        r"\bvai cair\b": "pode apresentar tendência de baixa",
    }

    for padrao, substituto in substituicoes.items():
        texto_sanitizado = re.sub(padrao, substituto, texto_sanitizado, flags=re.IGNORECASE)

    if texto_sanitizado != texto:
        logger.info("Texto sanitizado: linguagem prescritiva removida/substituída")

    return texto_sanitizado
