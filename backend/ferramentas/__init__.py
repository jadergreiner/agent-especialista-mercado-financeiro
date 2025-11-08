"""
Módulo de Ferramentas para Análise de Ativos

Contém funções especializadas para:
- Obtenção de preços em tempo real
- Cálculo de indicadores técnicos
- Busca e resumo de notícias
"""

from .preco_atual import obter_preco_atual

__all__ = ["obter_preco_atual"]
