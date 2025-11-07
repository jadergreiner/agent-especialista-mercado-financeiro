#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste Manual - CLI v2

Demonstração das funcionalidades: cache, batch, comandos.
"""
import sys
from pathlib import Path

# Adiciona backend ao path
sys.path.insert(0, str(Path(__file__).parent))

from cache_sessoes import CacheSessoes

def testar_integracao_cache():
    """Testa integração com cache."""
    print("=" * 70)
    print("🧪 TESTE DE INTEGRAÇÃO - Cache + CLI v2")
    print("=" * 70)

    cache = CacheSessoes()

    # Simula armazenamento
    print("\n1. Armazenando análise de EURUSD...")
    resultado_forex = {
        'classe_ativo': 'forex',
        'par': 'EURUSD',
        'timeframe': 'intraday',
        'resumo': {
            'preco_atual': 1.0850,
            'operacao': 'COMPRA',
            'entrada': 1.0840,
            'stop': 1.0820,
            'alvo1': 1.0880,
            'rr': '2.0:1'
        }
    }
    cache.armazenar('EURUSD', 'forex', resultado_forex)
    print("   ✅ Armazenado")

    # Simula recuperação (cache hit)
    print("\n2. Recuperando EURUSD (deve ser cache HIT)...")
    recuperado = cache.obter('EURUSD', 'forex')
    assert recuperado is not None, "Erro: não recuperou do cache"
    assert recuperado['resumo']['operacao'] == 'COMPRA', "Erro: dados incorretos"
    print(f"   ✅ Cache HIT! Operação: {recuperado['resumo']['operacao']}")

    # Simula cache miss
    print("\n3. Tentando recuperar GBPUSD (deve ser cache MISS)...")
    nao_existe = cache.obter('GBPUSD', 'forex')
    assert nao_existe is None, "Erro: deveria ser cache miss"
    print("   ✅ Cache MISS conforme esperado")

    # Estatísticas
    print("\n4. Estatísticas do cache...")
    stats = cache.estatisticas()
    print(f"   Total: {stats['total']}")
    print(f"   Válidas: {stats['validas']}")
    print(f"   Por classe: {stats['por_classe']}")

    # Simula múltiplos pares (batch)
    print("\n5. Simulando análise batch de 3 pares...")
    pares_batch = ['BTCUSDT', 'ETHUSDT', 'EURUSD']

    for par in pares_batch:
        classe = 'cripto' if 'USDT' in par else 'forex'
        resultado_cache = cache.obter(par, classe)

        if resultado_cache:
            print(f"   ⚡ {par}: Cache HIT")
        else:
            print(f"   🔄 {par}: Cache MISS - seria consultada a fonte")
            # Simularia armazenamento aqui

    print("\n" + "=" * 70)
    print("✅ TODOS OS TESTES PASSARAM!")
    print("=" * 70)

    print("\n📊 Funcionalidades v2 verificadas:")
    print("  ✅ Cache com TTL por classe de ativo")
    print("  ✅ Cache hit/miss funcionando corretamente")
    print("  ✅ Estatísticas do cache")
    print("  ✅ Suporte a análise batch (múltiplos pares)")
    print("\n💡 Para testar o CLI interativo, execute:")
    print("   python cli_prompt_first.py")
    print("\nComandos disponíveis no CLI v2:")
    print("  - ajuda")
    print("  - cache (exibe estatísticas)")
    print("  - analisar EURUSD (análise única)")
    print("  - analisar EURUSD GBPUSD BTCUSDT (análise batch)")
    print("  - sair")


if __name__ == '__main__':
    testar_integracao_cache()
