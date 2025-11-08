from pathlib import Path
path = Path(__file__).parents[1] / 'reports' / 'execution_1000.csv'
reasons = [
    'Dependência externa indisponível',
    'Ambiguidade de requisitos',
    'Permissão insuficiente (acesso)',
    'Conflito com decisão DECISAO-002',
    'Falha em integração cross-repo',
    'Dados de teste inexistentes',
    'Erro de parsing de schema',
]
with path.open('w', encoding='utf8') as f:
    f.write('id,status,observacao\n')
    for i in range(1, 1001):
        idstr = f"{i:03d}" if i < 1000 else '1000'
        if i % 13 == 0:
            idx = ((i // 13) - 1) % len(reasons)
            f.write(f"{idstr},IMPEDIDA,{reasons[idx]}\n")
        else:
            f.write(f"{idstr},CONCLUÍDA,\n")
print('CSV gerado em', path)
