#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste Integrado da API de Persistência
Demonstra funcionalidades do sistema via chamadas HTTP
"""

import requests
import json
from datetime import datetime

def testar_api_persistencia():
    """Testar endpoints da API de persistência"""

    base_url = "http://127.0.0.1:5001"

    print("🧪 Testando API de Persistência...")

    # 1. Health Check
    print("\n1️⃣ Health Check:")
    try:
        response = requests.get(f"{base_url}/api/health")
        print(f"   Status: {response.status_code}")
        print(f"   Resposta: {response.json()}")
    except Exception as e:
        print(f"   Erro: {e}")

    # 2. Listar tipos de dados
    print("\n2️⃣ Tipos de dados disponíveis:")
    try:
        response = requests.get(f"{base_url}/api/tipos-dado")
        if response.status_code == 200:
            tipos = response.json()['tipos_dados']
            for tipo in tipos:
                print(f"   📁 {tipo['valor']} ({tipo['nome']})")
    except Exception as e:
        print(f"   Erro: {e}")

    # 3. Salvar dados de teste
    print("\n3️⃣ Salvando dados de teste:")

    dados_teste = [
        {
            "dados": {
                "ativo": "AAPL",
                "preco": 175.50,
                "volume": 2500000,
                "timestamp": datetime.now().isoformat()
            },
            "tipo_dado": "preco_ativo",
            "tags": ["acao", "nasdaq", "tech", "apple"],
            "metadados": {"fonte": "yahoo_finance", "teste_api": True}
        },
        {
            "dados": {
                "indicador": "VIX",
                "valor": 22.1,
                "nivel": "moderado",
                "timestamp": datetime.now().isoformat()
            },
            "tipo_dado": "indicador_macro",
            "tags": ["volatilidade", "medo", "mercado"],
            "metadados": {"fonte": "cboe", "teste_api": True}
        },
        {
            "dados": {
                "ativo": "TSLA",
                "acao_recomendada": "COMPRA",
                "probabilidade_sucesso": 78,
                "confianca": 85,
                "risk_reward": 2.8,
                "preco_entrada": 245.30,
                "preco_alvo": 285.00,
                "stop_loss": 225.00,
                "catalysts": ["earnings", "delivery_numbers", "fsd_beta"]
            },
            "tipo_dado": "oportunidade",
            "tags": ["ev", "crescimento", "inovacao", "tesla"],
            "metadados": {"analista": "sistema_ia", "teste_api": True}
        }
    ]

    ids_salvos = []
    for i, dados in enumerate(dados_teste):
        try:
            response = requests.post(f"{base_url}/api/dados", json=dados)
            if response.status_code == 201:
                result = response.json()
                id_versao = result['id_versao']
                ids_salvos.append(id_versao)
                print(f"   ✅ Salvo #{i+1}: {id_versao}")
            else:
                print(f"   ❌ Erro #{i+1}: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"   ❌ Erro #{i+1}: {e}")

    # 4. Carregar dados salvos
    print(f"\n4️⃣ Carregando {len(ids_salvos)} registros salvos:")
    for i, id_versao in enumerate(ids_salvos):
        try:
            response = requests.get(f"{base_url}/api/dados/{id_versao}")
            if response.status_code == 200:
                dados = response.json()
                print(f"   ✅ Carregado #{i+1}: {id_versao[:20]}...")
            else:
                print(f"   ❌ Erro #{i+1}: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Erro #{i+1}: {e}")

    # 5. Buscar dados por critérios
    print(f"\n5️⃣ Testando buscas:")

    # Busca por tipo
    try:
        response = requests.get(f"{base_url}/api/buscar?tipo_dado=preco_ativo")
        if response.status_code == 200:
            result = response.json()
            print(f"   📊 Preços de ativos: {result['total']} encontrados")
    except Exception as e:
        print(f"   ❌ Erro busca por tipo: {e}")

    # Busca por tags
    try:
        response = requests.get(f"{base_url}/api/buscar?tags=tech&tags=nasdaq")
        if response.status_code == 200:
            result = response.json()
            print(f"   🏷️  Tags tech+nasdaq: {result['total']} encontrados")
    except Exception as e:
        print(f"   ❌ Erro busca por tags: {e}")

    # 6. Estatísticas do sistema
    print(f"\n6️⃣ Estatísticas do sistema:")
    try:
        response = requests.get(f"{base_url}/api/estatisticas")
        if response.status_code == 200:
            stats = response.json()['estatisticas']

            versoes = stats['versoes']
            print(f"   📋 Versões: {versoes['total']} total, {versoes['ativas']} ativas")

            cache = stats['cache']
            print(f"   💾 Cache: {cache['hit_rate']:.1f}% hit rate, {cache['itens_memoria']} em memória")

            armazenamento = stats['armazenamento']
            print(f"   💿 Armazenamento: {armazenamento['total_mb']:.2f} MB total")

            print(f"   📁 Por tipo de dado:")
            for tipo, info in stats['por_tipo'].items():
                print(f"      {tipo}: {info['count']} itens, compressão {info['compressao_pct']:.1f}%")

    except Exception as e:
        print(f"   ❌ Erro obtendo estatísticas: {e}")

    # 7. Testar arquivamento (simulado)
    print(f"\n7️⃣ Testando arquivamento:")
    try:
        payload = {"dias_limite": 0}  # Arquivar tudo para teste
        response = requests.post(f"{base_url}/api/arquivar", json=payload)
        if response.status_code == 200:
            result = response.json()['resultado_arquivamento']
            print(f"   📦 Arquivamento: {result.get('candidatos', 0)} candidatos, {result.get('arquivados', 0)} processados")
        else:
            print(f"   ❌ Erro arquivamento: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro arquivamento: {e}")

    print(f"\n✅ Teste da API de Persistência concluído!")
    print(f"🌐 Documentação completa em: http://127.0.0.1:5001/api/docs")

if __name__ == "__main__":
    testar_api_persistencia()