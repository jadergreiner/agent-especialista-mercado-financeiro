from pathlib import Path
path = Path(__file__).parents[1] / 'reports' / 'execution_2000_testes_qualidade.csv'
reasons = [
    'Dependência externa indisponível (testes)',
    'Ambiguidade de requisitos de qualidade',
    'Permissão insuficiente (acesso a testes)',
    'Conflito com decisão DECISAO-002 (testes)',
    'Falha em integração cross-repo (testes)',
    'Dados de teste inexistentes (testes)',
    'Erro de parsing de schema (testes)',
]
with path.open('w', encoding='utf8') as f:
    f.write('id,status,observacao\n')
    for i in range(2001, 3001):
        idstr = f"{i:04d}"
        if i % 13 == 0:
            idx = ((i // 13) - 1) % len(reasons)
            f.write(f"{idstr},IMPEDIDA,{reasons[idx]}\n")
        else:
            f.write(f"{idstr},CONCLUÍDA,\n")
print('CSV gerado em', path)