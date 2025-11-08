#!/usr/bin/env python3
"""
Script para enriquecer o CSV de findings Medium do Bandit com colunas de priorização.
Adiciona: esforço_estimado, impacto, sugestao_owner.
"""

import csv
from pathlib import Path

def estimar_priorizacao(test_id: str, arquivo: str) -> dict:
    """Estima esforço, impacto e owner baseado no test_id e arquivo."""
    base = {
        'esforco_estimado': 'médio',
        'impacto': 'médio',
        'sugestao_owner': 'backend team' if 'backend' in arquivo else 'scripts team'
    }

    if test_id == 'B608':  # SQL injection
        base.update({'esforco_estimado': 'alto', 'impacto': 'alto'})
    elif test_id == 'B301':  # Pickle unsafe
        base.update({'esforco_estimado': 'médio', 'impacto': 'alto'})
    elif test_id == 'B102':  # Exec
        base.update({'esforco_estimado': 'alto', 'impacto': 'alto'})
    elif test_id == 'B104':  # Bind all interfaces
        base.update({'esforco_estimado': 'baixo', 'impacto': 'médio'})
    elif test_id == 'B113':  # Requests without timeout
        base.update({'esforco_estimado': 'baixo', 'impacto': 'médio'})

    return base

def main():
    input_path = Path('.reports/bandit_medium_findings.csv')
    output_path = Path('.reports/bandit_medium_priorizado.csv')

    with open(input_path, 'r', encoding='utf-8') as f_in, \
         open(output_path, 'w', newline='', encoding='utf-8') as f_out:

        reader = csv.DictReader(f_in)
        fieldnames = reader.fieldnames + ['esforco_estimado', 'impacto', 'sugestao_owner']
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            priorizacao = estimar_priorizacao(row['test_id'], row['arquivo'])
            row.update(priorizacao)
            writer.writerow(row)

    print(f"CSV priorizado gerado: {output_path}")

if __name__ == '__main__':
    main()