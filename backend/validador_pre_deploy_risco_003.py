#!/usr/bin/env python3
"""
Script de Validação Pré-Deploy — US-QUALIDADE-007

Valida que não há confiança hardcoded em "60%" ou "Confiança Média"
no código antes de deploy da feature US-RISCO-003.

Detecta regressões simples que poderiam quebrar Radical Transparency.
"""

import re
import sys
from pathlib import Path


def validar_confianca_hardcoded():
    """
    Procura por patterns perigosos de confiança hardcoded.

    Retorna:
    - Lista de (arquivo, linha, padrão encontrado)
    """
    backend_path = Path('/repo/projetos/agent-especialista-mercado-financeiro/backend')

    patterns_perigosos = [
        (r'["\']60["\'].*[Cc]onfiança', "Confiança 60% encontrada"),
        (r'[Cc]onfiança.*["\']60["\']', "Confiança 60% encontrada (inverso)"),
        (r'[Cc]onfiança\s*[Mm]édia', "String 'Confiança Média' encontrada"),
        (r'⭐⭐⭐\s*60', "Display 3 estrelas com 60% encontrado"),
        (r'[Cc]onfiança["\']?\s*:\s*60', "JSON/dict com confiança: 60 encontrado"),
    ]

    # Arquivos a ignorar (validadores, testes, arquivos antigos)
    arquivos_ignorar = [
        'validador_pre_deploy_risco_003.py',
        'teste_',
        'monitor_forex.py',
    ]

    achados = []

    for arquivo_py in backend_path.glob('*.py'):
        # Pular arquivos ignorados
        if any(ignorar in arquivo_py.name for ignorar in arquivos_ignorar):
            continue

        try:
            with open(arquivo_py, 'r', encoding='utf-8') as f:
                linhas = f.readlines()

            for num_linha, linha in enumerate(linhas, 1):
                # Pular comentários, docstrings e strings literais de teste
                if linha.strip().startswith('#') or linha.strip().startswith('"""') or linha.strip().startswith("'''"):
                    continue

                for pattern, descricao in patterns_perigosos:
                    if re.search(pattern, linha, re.IGNORECASE):
                        achados.append((arquivo_py.name, num_linha, descricao, linha.strip()))
        except Exception as e:
            print(f"⚠️  Erro lendo {arquivo_py.name}: {e}")

    return achados


def validar_sistema_transparency():
    """
    Valida que o sistema_transparency_radical.py está integrado corretamente.

    Retorna:
    - boolean: True se tudo OK, False se há problemas
    """
    backend_path = Path('/repo/projetos/agent-especialista-mercado-financeiro/backend')

    # Verificar se arquivo existe
    arquivo_transparency = backend_path / 'sistema_transparency_radical.py'
    if not arquivo_transparency.exists():
        return False, "Arquivo sistema_transparency_radical.py não encontrado"

    # Verificar integração no orquestrador
    arquivo_orquestrador = backend_path / 'orquestrador_analise.py'
    if not arquivo_orquestrador.exists():
        return False, "Arquivo orquestrador_analise.py não encontrado"

    with open(arquivo_orquestrador, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Validar imports
    if 'from sistema_transparency_radical import' not in conteudo:
        return False, "Import de sistema_transparency_radical não encontrado em orquestrador"

    if 'obter_sistema_transparency_radical()' not in conteudo:
        return False, "Chamada a obter_sistema_transparency_radical() não encontrada"

    if 'validar_qualidade_pre_analise' not in conteudo:
        return False, "Validação de qualidade não integrada no orquestrador"

    if 'fallback_gracioso_api_falha' not in conteudo:
        return False, "Fallback gracioso não integrado no orquestrador"

    return True, "Sistema de transparência integrado corretamente"


def gerar_relatorio():
    """Gera relatório completo de validação."""
    print("\n" + "="*80)
    print("🔍 VALIDAÇÃO PRÉ-DEPLOY — US-QUALIDADE-007")
    print("="*80)

    # Validação 1: Confiança hardcoded
    print("\n📋 VALIDAÇÃO 1: Procurando confiança hardcoded (60%)")
    print("-"*80)

    achados = validar_confianca_hardcoded()

    if achados:
        print(f"\n❌ ENCONTRADOS {len(achados)} PROBLEMAS:")
        for arquivo, num_linha, descricao, linha in achados:
            print(f"  📄 {arquivo}:{num_linha}")
            print(f"     ⚠️  {descricao}")
            print(f"     📝 {linha[:70]}...")
        print("\n🚨 DEPLOY BLOQUEADO: Remova confiança hardcoded antes de continuar!")
        return False
    else:
        print("✅ Nenhuma confiança hardcoded (60%) encontrada")

    # Validação 2: Integração do sistema
    print("\n📋 VALIDAÇÃO 2: Integração do Sistema de Transparência")
    print("-"*80)

    integrado, mensagem = validar_sistema_transparency()

    if integrado:
        print(f"✅ {mensagem}")
    else:
        print(f"❌ {mensagem}")
        print("🚨 DEPLOY BLOQUEADO: Integração incompleta!")
        return False

    # Validação 3: Arquivos críticos
    print("\n📋 VALIDAÇÃO 3: Arquivos Críticos")
    print("-"*80)

    backend_path = Path('/repo/projetos/agent-especialista-mercado-financeiro/backend')
    arquivos_criticos = [
        'sistema_transparency_radical.py',
        'orquestrador_analise.py',
        'teste_sistema_transparency_radical.py',
    ]

    todos_presentes = True
    for arquivo in arquivos_criticos:
        caminho = backend_path / arquivo
        if caminho.exists():
            tamanho = caminho.stat().st_size
            print(f"✅ {arquivo:40} ({tamanho:,} bytes)")
        else:
            print(f"❌ {arquivo:40} NÃO ENCONTRADO")
            todos_presentes = False

    if not todos_presentes:
        print("🚨 DEPLOY BLOQUEADO: Arquivos críticos faltando!")
        return False

    # Resultado final
    print("\n" + "="*80)
    print("✅ VALIDAÇÃO PRÉ-DEPLOY PASSOU")
    print("="*80)
    print("\n✨ A feature US-RISCO-003 está pronta para deploy!")
    print("\nPróximos passos:")
    print("1. Executar testes unitários: pytest backend/teste_sistema_transparency_radical.py")
    print("2. Testar com dados reais: python backend/orquestrador_analise.py EURUSD")
    print("3. Validar saída HTML com avisos críticos visíveis")
    print("4. Fazer commit e criar Pull Request para code review")

    return True


def main():
    """Executa validação pré-deploy."""
    sucesso = gerar_relatorio()
    sys.exit(0 if sucesso else 1)


if __name__ == "__main__":
    main()
