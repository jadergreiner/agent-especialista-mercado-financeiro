#!/usr/bin/env python3
"""
Playbook de Execução do Test Plan AG-008
Orquestra backup, masking, deploy staging e execução E2E para validação de rollout controlado.

Origin: TASK-16 - Implementar playbook Test Plan AG-008
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, cwd=None):
    """Executa comando e retorna sucesso."""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    base_dir = Path(__file__).parent.parent
    print("Iniciando Test Plan AG-008...")

    # 1. Backup
    print("Passo 1: Executando backup...")
    success, out, err = run_command("python scripts/backup_db.py", cwd=base_dir)
    if not success:
        print(f"Falha no backup: {err}")
        return False

    # 2. Masking
    print("Passo 2: Aplicando masking...")
    success, out, err = run_command("python scripts/mask_sqlite.py", cwd=base_dir)
    if not success:
        print(f"Falha no masking: {err}")
        return False

    # 3. Deploy staging
    print("Passo 3: Fazendo deploy em staging...")
    success, out, err = run_command("docker-compose -f docker-compose.staging.yml up -d", cwd=base_dir)
    if not success:
        print(f"Falha no deploy: {err}")
        return False

    # 4. Executar E2E
    print("Passo 4: Executando testes E2E...")
    success, out, err = run_command("npx playwright test", cwd=base_dir)
    if not success:
        print(f"Falha nos E2E: {err}")
        return False

    # 5. Relatório
    print("Passo 5: Gerando relatório...")
    with open(base_dir / "reports" / "test_plan_ag008_report.md", "w") as f:
        f.write("# Relatório Test Plan AG-008\n\n")
        f.write("✅ Backup executado\n")
        f.write("✅ Masking aplicado\n")
        f.write("✅ Staging deployado\n")
        f.write("✅ E2E executados\n")
        f.write("\n**Status: SUCESSO**\n")

    print("Test Plan AG-008 concluído com sucesso!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)