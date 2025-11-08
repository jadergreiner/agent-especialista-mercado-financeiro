#!/usr/bin/env python3
"""
Revisão de Logs para PII
Audita logs existentes para garantir que PII não está gravada.

Origin: TASK-37 - Revisão logs PII
"""

import os
import re
from pathlib import Path

LOG_DIR = Path(__file__).parent.parent / "logs"
PII_PATTERNS = [
    r'\b\d{3}\.\d{3}\.\d{3}-\d{2}\b',  # CPF
    r'\b\d{2}\s\d{4,5}-\d{4}\b',  # Telefone
    r'\S+@\S+\.\S+',  # Email
]

def scan_file(filepath):
    violations = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                for pattern in PII_PATTERNS:
                    if re.search(pattern, line):
                        violations.append((line_num, line.strip()))
    except Exception as e:
        print(f"Erro ao ler {filepath}: {e}")
    return violations

def main():
    if not LOG_DIR.exists():
        print("Diretório de logs não encontrado.")
        return

    total_violations = 0
    for file in LOG_DIR.glob("*.log"):
        violations = scan_file(file)
        if violations:
            print(f"Arquivo: {file}")
            for line_num, line in violations:
                print(f"  Linha {line_num}: {line}")
            total_violations += len(violations)

    if total_violations == 0:
        print("✅ Nenhum PII encontrado nos logs.")
    else:
        print(f"❌ {total_violations} violações de PII encontradas.")

if __name__ == "__main__":
    main()