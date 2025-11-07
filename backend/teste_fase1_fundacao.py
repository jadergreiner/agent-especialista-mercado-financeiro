"""
Script de teste manual para Fase 1 — Fundação

Testa:
- Obtenção de preço atual (yfinance)
- Aplicação de disclaimers
- Validação de linguagem prescritiva
"""

import logging
import sys
from pathlib import Path

# Adicionar backend ao path
sys.path.insert(0, str(Path(__file__).parent))

from ferramentas.preco_atual import obter_preco_atual, validar_ativo_suportado
from validadores.disclaimers import (
    DISCLAIMER_PADRAO,
    aplicar_disclaimer,
    validar_linguagem_prescritiva,
    sanitizar_texto,
)
from utils.logger_analise import configurar_logger

# Configurar logging
logger = configurar_logger("teste_fase1", nivel="INFO")


def testar_preco_atual():
    """Testa obtenção de preços para ativos prioritários."""
    print("\n" + "=" * 70)
    print("TESTE 1: Obtenção de Preço Atual")
    print("=" * 70)

    ativos_teste = ["EURUSD", "XAUUSD", "USDJPY"]

    for ativo in ativos_teste:
        print(f"\n🔍 Testando: {ativo}")
        try:
            # Validar se é suportado
            if not validar_ativo_suportado(ativo):
                print(f"⚠️  Ativo {ativo} não está na lista de suportados")

            # Obter preço
            resultado = obter_preco_atual(ativo)
            print(f"✅ Preço: {resultado['preco']}")
            print(f"   Variação: {resultado['variacao_pct']:+.2f}%")
            print(f"   Timestamp: {resultado['timestamp']}")
            print(f"   Fonte: {resultado['fonte']}")

        except Exception as e:
            print(f"❌ Erro: {e}")


def testar_disclaimers():
    """Testa aplicação de disclaimers e validação de linguagem."""
    print("\n" + "=" * 70)
    print("TESTE 2: Disclaimers e Validação de Linguagem")
    print("=" * 70)

    # Teste 1: Aplicar disclaimer
    print("\n📋 Disclaimer Padrão:")
    print(DISCLAIMER_PADRAO)

    analise_mock = {
        "ativo": "EURUSD",
        "preco": 1.0850,
        "drivers": ["Fed manteve juros", "Dados de emprego fracos"],
    }

    analise_com_disclaimer = aplicar_disclaimer(analise_mock)
    print(f"\n✅ Disclaimer aplicado: {'disclaimer' in analise_com_disclaimer}")

    # Teste 2: Validar linguagem prescritiva
    print("\n🔍 Testando validação de linguagem prescritiva:")

    textos_teste = [
        ("Preço apresenta tendência de alta", True),
        ("Você deve comprar agora!", False),
        ("Recomendo vender imediatamente", False),
        ("Considere analisar os níveis técnicos", True),
        ("Isso é garantido, sem risco!", False),
    ]

    for texto, esperado_valido in textos_teste:
        is_valid, violacoes = validar_linguagem_prescritiva(texto)
        status = "✅" if is_valid == esperado_valido else "❌"
        print(f"{status} '{texto[:50]}...' - Válido: {is_valid}")
        if violacoes:
            print(f"   Violações: {violacoes}")

    # Teste 3: Sanitizar texto
    print("\n🧹 Testando sanitização:")
    texto_ruim = "Você deve comprar EURUSD agora, vou garantir lucro!"
    texto_limpo = sanitizar_texto(texto_ruim)
    print(f"Original: {texto_ruim}")
    print(f"Sanitizado: {texto_limpo}")


def main():
    """Executa todos os testes da Fase 1."""
    print("\n" + "=" * 70)
    print("🚀 TESTES FASE 1 — FUNDAÇÃO (SPRINT 0)")
    print("=" * 70)

    try:
        testar_preco_atual()
        testar_disclaimers()

        print("\n" + "=" * 70)
        print("✅ TODOS OS TESTES DA FASE 1 CONCLUÍDOS")
        print("=" * 70)

    except Exception as e:
        logger.error(f"Erro nos testes: {e}", exc_info=True)
        print("\n❌ Testes falharam!")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
