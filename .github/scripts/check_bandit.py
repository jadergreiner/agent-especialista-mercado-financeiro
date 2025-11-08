import json
from pathlib import Path

def main():
    p = Path('.reports/bandit_pr.json')
    if p.exists():
        data = json.loads(p.read_text())
        findings = data.get('results', [])
        bad = [f for f in findings if f.get('issue_severity') in ('MEDIUM','HIGH')]
        if bad:
            print('Bandit found MEDIUM/HIGH findings:')
            for b in bad:
                print(b.get('filename'), b.get('issue_text'))
            raise SystemExit('Failing PR checks due to Bandit MEDIUM/HIGH findings')
    print('No MEDIUM/HIGH Bandit findings')

if __name__ == '__main__':
    main()
