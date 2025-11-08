# Origin: feature/AG-rbac-audit-masking - Gerador de triagem Bandit
"""
Gera um relatório markdown (docs/gestao-agil/BANDIT_MEDIUM_LOW_REPORT.md)
e um CSV com findings de severidade MEDIUM (.reports/bandit_medium_findings.csv)
com base em .reports/bandit_full.json.

Uso: python scripts/generate_bandit_triage.py
"""
import json
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
REPORT_JSON = ROOT / '.reports' / 'bandit_full.json'
OUT_MD = ROOT / 'docs' / 'gestao-agil' / 'BANDIT_MEDIUM_LOW_REPORT.md'
OUT_CSV = ROOT / '.reports' / 'bandit_medium_findings.csv'

if not REPORT_JSON.exists():
    raise SystemExit(f"Arquivo de relatório não encontrado: {REPORT_JSON}")

with REPORT_JSON.open('r', encoding='utf-8') as f:
    data = json.load(f)

results = data.get('results', [])
errors = data.get('errors', [])
metrics = data.get('metrics', {})
_totals = data.get('metrics', {}).get('_totals', {})

# Filtrar findings por severidade
medium_findings = [r for r in results if r.get('issue_severity') == 'MEDIUM']
low_findings = [r for r in results if r.get('issue_severity') == 'LOW']

# Estatísticas rápidas
counts_by_severity = Counter([r.get('issue_severity') for r in results])
counts_by_test = Counter([r.get('test_id') for r in results if r.get('test_id')])

# Escrever Markdown resumido
OUT_MD.parent.mkdir(parents=True, exist_ok=True)
with OUT_MD.open('w', encoding='utf-8') as md:
    md.write('# Relatório Bandit - Medium/Low (triagem)\n\n')
    md.write(f'*Gerado a partir de* `.reports/bandit_full.json`\n\n')
    md.write('## Resumo Geral\n\n')
    md.write(f'- Arquivos com erro de parsing: {len(errors)}\n')
    if errors:
        md.write('- Arquivos com parse errors:\n')
        for e in errors:
            md.write(f"  - `{e.get('filename')}` — {e.get('reason')}\n")
    md.write('\n')
    md.write('## Totais (do relatório)\n\n')
    md.write(f'- Total findings MEDIUM: {len(medium_findings)}\n')
    md.write(f'- Total findings LOW: {len(low_findings)}\n')
    md.write(f"- Totais agregados (metrics._totals): SEVERITY.HIGH={_totals.get('SEVERITY.HIGH',0)}, SEVERITY.MEDIUM={_totals.get('SEVERITY.MEDIUM',0)}, SEVERITY.LOW={_totals.get('SEVERITY.LOW',0)}\n\n")

    md.write('## Principais tipos (top 10 tests)\n\n')
    for test_id, cnt in counts_by_test.most_common(10):
        md.write(f'- {test_id}: {cnt}\n')
    md.write('\n')

    md.write('## Findings MEDIUM (resumo)\n\n')
    if not medium_findings:
        md.write('Nenhum finding MEDIUM encontrado.\n')
    else:
        # agrupar por arquivo e contar
        by_file = {}
        for r in medium_findings:
            fn = r.get('filename')
            by_file.setdefault(fn, []).append(r)
        for fn, items in sorted(by_file.items(), key=lambda kv: (-len(kv[1]), kv[0])):
            md.write(f'- `{fn}` — {len(items)} findings MEDIUM\n')
            for it in items[:5]:
                ln = it.get('line_number')
                tid = it.get('test_id')
                text = it.get('issue_text', '').replace('\n',' ')
                md.write(f"  - L{ln} | {tid} | {text}\n")
            if len(items) > 5:
                md.write(f"  - ...(+{len(items)-5} mais)\n")

    md.write('\n')
    md.write('## Findings LOW (resumo)\n\n')
    md.write(f'- Total LOW: {len(low_findings)}\n')
    md.write('\n')
    md.write('---\n')
    md.write('> Nota: arquivos substituídos por stubs temporários para permitir parsing completo. Ver branch `feature/AG-rbac-audit-masking`.')

# Export CSV com MEDIUM
OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
with OUT_CSV.open('w', encoding='utf-8') as csvf:
    csvf.write('arquivo,linha,test_id,issue_text,more_info\n')
    for r in medium_findings:
        fn = r.get('filename','').replace('\\','/')
        ln = r.get('line_number','')
        tid = r.get('test_id','')
        text = r.get('issue_text','').replace('\n',' ').replace('"','""')
        more = r.get('more_info','')
        csvf.write(f'"{fn}",{ln},"{tid}","{text}","{more}"\n')

print('Relatório gerado:', OUT_MD)
print('CSV MEDIUM gerado:', OUT_CSV)
