"""
Ferramentas de Notícias Resumidas

Módulo responsável por buscar e resumir notícias relacionadas a ativos financeiros.
Atualmente implementado como placeholder com dados mockados estruturados.
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
import random

from utils.logger_analise import obter_logger

logger = obter_logger(__name__)


def buscar_noticias_resumidas(
    ativo: str,
    limite_noticias: int = 5,
    dias_atras: int = 7
) -> Dict[str, Any]:
    """
    Busca notícias resumidas relacionadas a um ativo financeiro.

    Args:
        ativo: Símbolo do ativo (ex: "EURUSD", "PETR4.SA")
        limite_noticias: Número máximo de notícias a retornar (padrão: 5)
        dias_atras: Dias para buscar notícias (padrão: 7)

    Returns:
        dict: Notícias resumidas com metadados
    """
    logger.info(f"Buscando notícias resumidas para {ativo} (últimos {dias_atras} dias)")

    try:
        # PLACEHOLDER: Implementação mockada
        # TODO: Integrar com APIs reais de notícias (NewsAPI, Alpha Vantage News, etc.)

        noticias_mockadas = _gerar_noticias_mockadas(ativo, limite_noticias, dias_atras)

        resultado = {
            "ativo": ativo,
            "timestamp_busca": datetime.now(timezone.utc).isoformat(),
            "parametros_busca": {
                "limite_noticias": limite_noticias,
                "dias_atras": dias_atras
            },
            "noticias": noticias_mockadas,
            "resumo_geral": _gerar_resumo_geral(noticias_mockadas),
            "fonte": "PLACEHOLDER - Integração futura com APIs de notícias",
            "status": "MOCK_DATA"
        }

        logger.info(f"Encontradas {len(noticias_mockadas)} notícias mockadas para {ativo}")
        return resultado

    except Exception as e:
        logger.error(f"Erro ao buscar notícias para {ativo}: {e}")
        raise


def _gerar_noticias_mockadas(ativo: str, quantidade: int, dias_atras: int) -> List[Dict[str, Any]]:
    """
    Gera notícias mockadas estruturadas para desenvolvimento e testes.
    """
    noticias_base = {
        "EURUSD": [
            {
                "titulo": "Fed sinaliza pausa no ciclo de aperto monetário",
                "resumo": "Presidente do Fed indica possível pausa nas próximas reuniões, impactando expectativas de juros.",
                "sentimento": "POSITIVO",
                "impacto": "ALTO",
                "fonte": "Reuters"
            },
            {
                "titulo": "Inflação da zona do euro surpreende negativamente",
                "resumo": "Dados de inflação acima do esperado podem pressionar BCE a manter política restritiva.",
                "sentimento": "NEGATIVO",
                "impacto": "MÉDIO",
                "fonte": "Bloomberg"
            },
            {
                "titulo": "Dados de emprego EUA mostram resiliência econômica",
                "resumo": "Mercado de trabalho forte pode dar suporte a manutenção de juros elevados por mais tempo.",
                "sentimento": "NEUTRO",
                "impacto": "ALTO",
                "fonte": "CNBC"
            }
        ],
        "XAUUSD": [
            {
                "titulo": "Banco Central chinês aumenta compras de ouro",
                "resumo": "China aumenta reservas de ouro em meio a tensões comerciais, apoiando preços da commodity.",
                "sentimento": "POSITIVO",
                "impacto": "ALTO",
                "fonte": "Kitco News"
            },
            {
                "titulo": "Dólar forte pressiona ouro para mínimas",
                "resumo": "Valorização do dólar reduz atratividade do ouro como ativo alternativo.",
                "sentimento": "NEGATIVO",
                "impacto": "MÉDIO",
                "fonte": "MarketWatch"
            }
        ],
        "PETR4.SA": [
            {
                "titulo": "Petrobras anuncia descoberta de petróleo no pré-sal",
                "resumo": "Nova descoberta pode adicionar reservas significativas à companhia.",
                "sentimento": "POSITIVO",
                "impacto": "ALTO",
                "fonte": "Valor Econômico"
            },
            {
                "titulo": "Preços do petróleo caem com preocupações de demanda",
                "resumo": "Queda nos preços do barril pode impactar margens da Petrobras.",
                "sentimento": "NEGATIVO",
                "impacto": "MÉDIO",
                "fonte": "Reuters"
            }
        ]
    }

    # Obter notícias base para o ativo ou usar genéricas
    noticias_possiveis = noticias_base.get(ativo, [
        {
            "titulo": f"Desenvolvimento econômico impacta {ativo}",
            "resumo": f"Notícia econômica relevante para o ativo {ativo} com impacto no mercado.",
            "sentimento": "NEUTRO",
            "impacto": "MÉDIO",
            "fonte": "Market News"
        }
    ])

    # Selecionar notícias aleatoriamente
    noticias_selecionadas = random.sample(
        noticias_possiveis,
        min(quantidade, len(noticias_possiveis))
    )

    # Adicionar timestamps e metadados
    noticias_completas = []
    base_timestamp = datetime.now(timezone.utc)

    for i, noticia in enumerate(noticias_selecionadas):
        # Timestamp aleatório nos últimos dias_atras
        dias_aleatorios = random.randint(0, dias_atras - 1)
        horas_aleatorias = random.randint(0, 23)
        timestamp_noticia = base_timestamp - timedelta(days=dias_aleatorios, hours=horas_aleatorias)

        noticia_completa = {
            **noticia,
            "timestamp": timestamp_noticia.isoformat(),
            "url": f"https://news.example.com/{ativo.lower()}/noticia-{i+1}",
            "relevancia_score": round(random.uniform(0.6, 0.95), 2)
        }
        noticias_completas.append(noticia_completa)

    # Ordenar por timestamp (mais recentes primeiro)
    noticias_completas.sort(key=lambda x: x["timestamp"], reverse=True)

    return noticias_completas


def _gerar_resumo_geral(noticias: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Gera resumo geral das notícias baseado no sentimento e impacto.
    """
    if not noticias:
        return {
            "sentimento_geral": "NEUTRO",
            "impacto_geral": "BAIXO",
            "resumo": "Nenhuma notícia relevante encontrada."
        }

    # Contar sentimentos
    sentimentos = {}
    impactos = {}

    for noticia in noticias:
        sentimento = noticia["sentimento"]
        impacto = noticia["impacto"]

        sentimentos[sentimento] = sentimentos.get(sentimento, 0) + 1
        impactos[impacto] = impactos.get(impacto, 0) + 1

    # Determinar sentimento geral
    sentimento_dominante = max(sentimentos, key=sentimentos.get)

    # Determinar impacto geral
    if impactos.get("ALTO", 0) > 0:
        impacto_geral = "ALTO"
    elif impactos.get("MÉDIO", 0) >= 2:
        impacto_geral = "MÉDIO"
    else:
        impacto_geral = "BAIXO"

    # Gerar resumo textual
    total_noticias = len(noticias)
    resumo_texto = f"Análise de {total_noticias} notícia(s). Sentimento predominantemente {sentimento_dominante.lower()} com impacto {impacto_geral.lower()} no ativo."

    return {
        "sentimento_geral": sentimento_dominante,
        "impacto_geral": impacto_geral,
        "resumo": resumo_texto,
        "estatisticas": {
            "total_noticias": total_noticias,
            "sentimentos": sentimentos,
            "impactos": impactos
        }
    }


def obter_noticias_para_analise(ativo: str) -> Dict[str, Any]:
    """
    Função de conveniência que retorna notícias formatadas para análise.
    Útil para integração com orquestrador de análise.
    """
    return buscar_noticias_resumidas(ativo)