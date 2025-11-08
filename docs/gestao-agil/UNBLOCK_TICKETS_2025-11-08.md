# Tickets de Desbloqueio (76) — Execução 1000 Atividades

Data: 2025-11-08
Origin: DECISAO-002

Resumo: Durante a execução autônoma de 1000 atividades, 76 atividades foram marcadas como [IMPEDIDA]. Este arquivo documenta o processo para gerar tickets individuais de desbloqueio e propõe um script que converte as linhas `IMPEDIDA` do arquivo `reports/execution_1000.csv` em entradas do backlog ou issues.

Local dos dados:
- `reports/execution_1000.csv` — CSV com colunas `id,status,observacao`.

Instruções (gerar tickets locais em lote):

1) Rodar script Python que cria um arquivo `docs/gestao-agil/UNBLOCK_LIST_2025-11-08.md` contendo as 76 linhas formatadas para colagem no backlog/issue tracker.

Exemplo de script (executar na raiz do repo):

```python
# scripts/generate_unblock_tickets.py
from pathlib import Path
p = Path('reports') / 'execution_1000.csv'
out = Path('docs/gestao-agil') / 'UNBLOCK_LIST_2025-11-08.md'
lines = p.read_text(encoding='utf8').splitlines()
with out.open('w', encoding='utf8') as f:
    f.write('# UNBLOCK LIST (2025-11-08)\n\n')
    f.write('Cada entrada abaixo corresponde a uma tarefa impedida identificada na execução em lote. Adicione owner e crie issue/ticket com SLA=48h.\n\n')
    for row in lines[1:]:
        if 'IMPEDIDA' in row:
            id,status,obs = row.split(',',2)
            f.write(f'- [ ] UNBLOCK-{id}: Tarefa impedida (ID {id}) — Motivo: {obs} — Owner: TBD — SLA: 48h\n')
print('Arquivo gerado em', out)
```

2) Executar o script:

```powershell
python scripts/generate_unblock_tickets.py
```

3) O arquivo `docs/gestao-agil/UNBLOCK_LIST_2025-11-08.md` será criado com 76 linhas no formato pronto para colagem no backlog ou criação de issues via API/GitHub CLI.

4) Opcional: integração com GitHub CLI para criar issues automaticamente (exemplo simplificado):

```powershell
# Requer GH CLI autenticado e permissões
Get-Content docs/gestao-agil/UNBLOCK_LIST_2025-11-08.md | ForEach-Object {
  if ($_ -match '^\- \[ \] UNBLOCK-(\d+):') {
    $id = $matches[1]
    $title = "UNBLOCK-$id: Tarefa impedida"
    $body = $_
    gh issue create --title $title --body $body --label blocked
  }
}
```

Observação de governança:
- Todo ticket de desbloqueio deve referenciar `Origin: DECISAO-002` se o impedimento for por conflito de decisão.
- SLA padrão: 48h; owner deve ser atribuído pelo Tech Lead ou PO.

---

Se quiser, eu executo o script agora e adiciono `docs/gestao-agil/UNBLOCK_LIST_2025-11-08.md` ao repositório e/ou crio issues via GH CLI (você precisará autorizar o uso do GH CLI neste ambiente).