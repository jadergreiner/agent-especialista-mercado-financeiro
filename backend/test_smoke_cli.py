#!/usr/bin/env python3
"""
Smoke test - CLI Prompt-First v1
Valida comandos básicos e latência.
"""
import subprocess
import time
import json
from pathlib import Path


def teste_smoke_cli():
    """Testa comandos principais do CLI."""
    print("🧪 Iniciando smoke test do CLI Prompt-First v1...")
    print("=" * 70)

    # Comandos para testar
    comandos_teste = [
        "ajuda",
        "analisar BTCUSDT",
        "sair"
    ]

    # Prepara input
    entrada = "\n".join(comandos_teste) + "\n"

    # Executa CLI
    cli_path = Path(__file__).parent / 'cli_prompt_first.py'
    inicio = time.time()

    resultado = subprocess.run(
        ['python', str(cli_path)],
        input=entrada,
        capture_output=True,
        text=True,
        timeout=30
    )

    tempo_total = time.time() - inicio

    print(f"\n⏱️  Tempo total: {tempo_total:.2f}s")
    print("\n📤 STDOUT:")
    print(resultado.stdout)

    if resultado.stderr:
        print("\n⚠️  STDERR:")
        print(resultado.stderr)

    # Validações básicas
    saida = resultado.stdout

    checks = {
        "Banner exibido": "AGENT ESPECIALISTA" in saida,
        "Ajuda funcionou": "COMANDOS:" in saida,
        "Análise executada": "Analisando BTCUSDT" in saida or "Contrato Mínimo v1" in saida,
        "Encerramento OK": "Encerrando sessão" in saida,
        "Exit code 0": resultado.returncode == 0
    }

    print("\n✅ VALIDAÇÕES:")
    for check, passou in checks.items():
        status = "✅" if passou else "❌"
        print(f"  {status} {check}")

    # Verifica log de sessão
    log_path = Path(__file__).parent / 'logs' / 'sessoes_cli.jsonl'
    if log_path.exists():
        with open(log_path, 'r', encoding='utf-8') as f:
            ultimas = f.readlines()[-5:]  # últimas 5 linhas
            print(f"\n📋 LOG DE SESSÃO (últimas {len(ultimas)} entradas):")
            for linha in ultimas:
                entrada_log = json.loads(linha)
                print(f"  - {entrada_log['comando']}: {entrada_log['latencia_ms']}ms | sucesso={entrada_log['sucesso']}")

    sucesso_geral = all(checks.values())
    print("\n" + "=" * 70)
    if sucesso_geral:
        print("✅ SMOKE TEST: PASSOU")
    else:
        print("❌ SMOKE TEST: FALHOU")
    print("=" * 70)

    return sucesso_geral


if __name__ == '__main__':
    import sys
    sucesso = teste_smoke_cli()
    sys.exit(0 if sucesso else 1)
