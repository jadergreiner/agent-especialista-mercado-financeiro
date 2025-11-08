#!/usr/bin/env python3
"""Coletor básico de métricas de governança (GitHub PRs)

Origin: DT-014 - Esqueleto de scripts de coleta de métricas

Uso:
  - Defina a variável de ambiente GITHUB_TOKEN com um token com escopo `repo` (ou public_repo)
  - python scripts/collect_metrics/github_metrics.py --owner jadergreiner --repo agent-especialista-mercado-financeiro

Saída:
  - Gera um JSON resumido com métricas (stdout / arquivo)
"""
import os
import sys
import argparse
import requests
import datetime
import json

GITHUB_API = "https://api.github.com"


def gh_headers():
    token = os.environ.get("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    return headers


def fetch_prs(owner: str, repo: str, state: str = "all", since_days: int = 30):
    """Busca PRs nos últimos `since_days` dias (paginado, básico)."""
    prs = []
    per_page = 100
    page = 1
    since = (datetime.datetime.utcnow() - datetime.timedelta(days=since_days)).isoformat() + "Z"
    while True:
        url = f"{GITHUB_API}/repos/{owner}/{repo}/pulls"
        params = {"state": state, "per_page": per_page, "page": page}
        resp = requests.get(url, headers=gh_headers(), params=params)
        resp.raise_for_status()
        data = resp.json()
        if not data:
            break
        for pr in data:
            # filtra por data de criação/atualização
            updated_at = pr.get("updated_at") or pr.get("created_at")
            if updated_at and updated_at >= since:
                prs.append(pr)
        if len(data) < per_page:
            break
        page += 1
    return prs


def count_prs_referencing_decision(prs, decision_key="DECISAO-002"):
    """Conta PRs cujo título ou corpo referencia a decisão."""
    count = 0
    hits = []
    for pr in prs:
        text = (pr.get("title", "") + "\n" + (pr.get("body") or "")).upper()
        if decision_key.upper() in text:
            count += 1
            hits.append(pr.get("number"))
    return count, hits


def count_prs_using_template(prs, template_marker="Checklist de Conformidade"):
    """Heurística simples: verifica se o corpo contém a marcação do template."""
    count = 0
    hits = []
    for pr in prs:
        body = (pr.get("body") or "").lower()
        if template_marker.lower() in body:
            count += 1
            hits.append(pr.get("number"))
    return count, hits


def build_report(owner, repo, prs, decision_key="DECISAO-002", template_marker="Checklist de Conformidade"):
    total = len(prs)
    decision_count, decision_hits = count_prs_referencing_decision(prs, decision_key)
    template_count, template_hits = count_prs_using_template(prs, template_marker)

    report = {
        "repository": f"{owner}/{repo}",
        "period_days": 30,
        "total_prs": total,
        "decision_key": decision_key,
        "decision_count": decision_count,
        "decision_pr_numbers": decision_hits,
        "template_marker": template_marker,
        "template_count": template_count,
        "template_pr_numbers": template_hits,
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
    }
    return report


def main():
    parser = argparse.ArgumentParser(description="Coletor de métricas de governança (GitHub PRs)")
    parser.add_argument("--owner", required=True)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--since-days", type=int, default=30)
    parser.add_argument("--decision", default="DECISAO-002")
    parser.add_argument("--template-marker", default="Checklist de Conformidade")
    parser.add_argument("--out", default="-", help="Arquivo de saída (JSON), use - para stdout")
    args = parser.parse_args()

    prs = fetch_prs(args.owner, args.repo, since_days=args.since_days)
    report = build_report(args.owner, args.repo, prs, args.decision, args.template_marker)

    if args.out == "-":
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump(report, fh, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
