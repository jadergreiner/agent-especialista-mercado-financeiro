#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste Smoke - CLI v2 com Cache e Batch

Testa funcionalidades principais do CLI v2.
"""
import subprocess
import sys
from pathlib import Path

def testar_cli_v2():
    """Testa CLI v2 via subprocess."""
    print("🧪 Testando CLI v2 (Cache + Batch)...")
    print("=" * 70)

    # Comandos de teste
    comandos = [
        "ajuda",
        "cache",
        "sair"
    ]

    entrada = "\n".join(comandos)

    try:
        resultado = subprocess.run(
            [sys.executable, "cli_prompt_first.py"],
            input=entrada,
            capture_output=True,
            text=True,
            timeout=10,
            cwd=Path(__file__).parent
        )

        print("✅ SAÍDA DO CLI:")
        print(resultado.stdout)

        if resultado.stderr:
            print("\n⚠️  ERROS:")
            print(resultado.stderr)

        # Verificações básicas
        assert "Prompt-First v2" in resultado.stdout, "Banner v2 não encontrado"
        assert "ESTATÍSTICAS DO CACHE" in resultado.stdout, "Comando cache não funcionou"
        assert "Encerrando sessão" in resultado.stdout, "Saída não funcionou"

        print("\n✅ Todos os testes básicos passaram!")

    except subprocess.TimeoutExpired:
        print("❌ Timeout - CLI não respondeu em 10s")
    except AssertionError as e:
        print(f"❌ Teste falhou: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")


if __name__ == '__main__':
    testar_cli_v2()
