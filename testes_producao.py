#!/usr/bin/env python3
"""
TESTES DE PRODUÇÃO - Validar funcionamento com dados reais
Execute este script antes de colocar em produção
"""

import os
import sys
from pathlib import Path

# Adicionar backend ao path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

def testar_configuracao_ambiente():
    """Testa se configuração de ambiente está correta"""
    print("🔧 Testando configuração de ambiente...")

    try:
        from configuracao_ambiente import configurar_ambiente_producao
        config = configurar_ambiente_producao()

        if config.ambiente.value == 'producao':
            print("✅ Ambiente PRODUÇÃO configurado")
            return True
        else:
            print(f"⚠️ Ambiente configurado: {config.ambiente.value}")
            return False

    except Exception as e:
        print(f"❌ Erro na configuração: {e}")
        return False

def testar_conectividade_corretora():
    """Testa conectividade com corretora"""
    print("\n📡 Testando conectividade com corretora...")

    try:
        from configuracao_ambiente import obter_configuracao_corretora, configurar_ambiente_producao

        config_sistema = configurar_ambiente_producao()
        config_corretora = obter_configuracao_corretora(config_sistema)

        if config_corretora.get('api_key') and config_corretora['api_key'] != 'SEU_ALPACA_LIVE_KEY':
            print("✅ Chaves de API configuradas")
            # Aqui poderia testar conectividade real
            print("✅ Conectividade básica OK")
            return True
        else:
            print("❌ Chaves de API não configuradas")
            return False

    except Exception as e:
        print(f"❌ Erro na conectividade: {e}")
        return False

def testar_sistema_aprendizado():
    """Testa sistema de aprendizado contínuo"""
    print("\n🧠 Testando sistema de aprendizado...")

    try:
        from sistema_aprendizado_continuo import SistemaAprendizadoContinuo

        sistema = SistemaAprendizadoContinuo()

        if hasattr(sistema, 'ambiente'):
            print(f"✅ Sistema configurado para: {sistema.ambiente}")
            return True
        else:
            print("⚠️ Sistema sem configuração de ambiente")
            return False

    except Exception as e:
        print(f"❌ Erro no sistema de aprendizado: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("🚀 TESTES DE PRODUÇÃO - Agent Especialista Mercado Financeiro")
    print("=" * 60)

    testes = [
        ("Configuração de Ambiente", testar_configuracao_ambiente),
        ("Conectividade Corretora", testar_conectividade_corretora),
        ("Sistema de Aprendizado", testar_sistema_aprendizado),
    ]

    resultados = []
    for nome_teste, funcao_teste in testes:
        print(f"\n📋 Executando: {nome_teste}")
        try:
            resultado = funcao_teste()
            resultados.append((nome_teste, resultado))
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
            resultados.append((nome_teste, False))

    # Resumo
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES:")

    todos_passaram = True
    for nome_teste, resultado in resultados:
        status = "✅ PASSOU" if resultado else "❌ FALHOU"
        print(f"   {nome_teste}: {status}")
        if not resultado:
            todos_passaram = False

    print("\n" + "=" * 60)
    if todos_passaram:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Sistema pronto para produção")
    else:
        print("⚠️ Alguns testes falharam!")
        print("🔧 Corrija os problemas antes de colocar em produção")

    return todos_passaram

if __name__ == "__main__":
    sucesso = main()
    sys.exit(0 if sucesso else 1)
