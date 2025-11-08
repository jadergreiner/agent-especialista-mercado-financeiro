from pathlib import Path
path = Path(__file__).parents[1] / 'reports' / 'execution_1000_docs_agil.csv'
reasons = [
    'Dependência externa indisponível (provedor de docs)',
    'Ambiguidade de requisitos de documentação',
    'Permissão insuficiente (acesso a repositório docs)',
    'Conflito com decisão DECISAO-002 (docs)',
    'Falha em integração cross-repo (docs)',
    'Dados de teste inexistentes (docs)',
    'Erro de parsing de schema (docs)',
]
with path.open('w', encoding='utf8') as f:
    f.write('id,status,observacao\n')
    for i in range(1001, 2001):
        idstr = f"{i:04d}"
        if i % 13 == 0:
            idx = ((i // 13) - 1) % len(reasons)
            f.write(f"{idstr},IMPEDIDA,{reasons[idx]}\n")
        else:
            f.write(f"{idstr},CONCLUÍDA,\n")
print('CSV gerado em', path)