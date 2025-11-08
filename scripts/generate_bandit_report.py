import json
from pathlib import Path
p = Path('.reports/bandit_full.json')
obj = json.loads(p.read_text())
metrics = obj.get('metrics',{})
errors = obj.get('errors',[])
results = obj.get('results',[])
medium = [r for r in results if r.get('issue_severity')=='MEDIUM']
low = [r for r in results if r.get('issue_severity')=='LOW']
md = []
md.append('# Relatório Bandit (Medium & Low)\n')
md.append(f'Gerado em: {obj.get("generated_at")}\n')
md.append('## Sumário\n')
totals = metrics.get('_totals',{})
md.append(f'- Linha total: {totals.get("loc")}')
md.append(f'- High: {totals.get("SEVERITY.HIGH")}')
md.append(f'- Medium: {totals.get("SEVERITY.MEDIUM")}')
md.append(f'- Low: {totals.get("SEVERITY.LOW")}')
md.append('')
md.append('## Arquivos pulados por erro de parse\n')
if errors:
    for e in errors:
        md.append(f'- {e.get("filename")}: {e.get("reason")}')
else:
    md.append('- None')
md.append('')
md.append('## Findings de Severidade MÉDIA (detalhado)\n')
if medium:
    for r in medium:
        md.append(f'### {r.get("test_id")} — {r.get("test_name")}')
        md.append(f'- Arquivo: `{r.get("filename")}`')
        md.append(f'- Linha: {r.get("line_number")}, Severidade: {r.get("issue_severity")}, Confiança: {r.get("issue_confidence")}')
        text = r.get('issue_text','').replace('\n',' ')
        md.append(f'- Texto: {text}')
        md.append(f'- Mais: {r.get("more_info")}')
        code = r.get('code','').strip()
        if code:
            md.append('```python')
            md.append(code)
            md.append('```')
        md.append('')
else:
    md.append('- Nenhum finding de severidade média encontrado')
md.append('')
md.append('## Exemplos de Findings de Severidade BAIXA (primeiros 40)\n')
for r in low[:40]:
    md.append(f'- `{r.get("test_id")}` {r.get("test_name")} — `{r.get("filename")}`:{r.get("line_number")} — {r.get("issue_text")}')
md.append('')
md.append('## Observações e Recomendações\n')
md.append('- High findings foram mitigados na branch atual; este relatório foca Medium/Low para triagem posterior.')
md.append('- Arquivos pulados devem ser revisados manualmente por possível código inválido ou plugin incompatível.')
md.append('- Recomendo priorizar Mediums listados acima e abrir tasks para os Low recorrentes ou em módulos críticos.')

out = '\n'.join(md)
Path('docs/gestao-agil/BANDIT_MEDIUM_LOW_REPORT.md').write_text(out)
print('WROTE docs/gestao-agil/BANDIT_MEDIUM_LOW_REPORT.md')
