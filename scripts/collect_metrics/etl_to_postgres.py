#!/usr/bin/env python3
"""ETL simples: carrega JSON gerado por github_metrics.py para Postgres

Origin: DT-014 - ETL para `governance_metrics_weekly`

Uso:
  - Definir variáveis de ambiente: PGHOST, PGPORT, PGUSER, PGPASSWORD, PGDATABASE
  - python scripts/collect_metrics/etl_to_postgres.py --in metrics_report.json

Observação: script intencionalmente simples para inicialização. Em produção, usar pool, migrations e testes.
"""
import os
import argparse
import json
import datetime
import psycopg2
from psycopg2.extras import execute_values


def parse_week_start(generated_at_iso: str) -> str:
    # Retorna a data da segunda-feira da semana do timestamp
    dt = datetime.datetime.fromisoformat(generated_at_iso.replace("Z", "+00:00"))
    # calcula offset para segunda-feira
    monday = dt - datetime.timedelta(days=dt.weekday())
    return monday.date().isoformat()


def upsert_metrics(conn, report: dict):
    week_start = parse_week_start(report["generated_at"]) if report.get("generated_at") else None
    repo = report.get("repository")
    total_prs = report.get("total_prs", 0)
    decision_prs = report.get("decision_count", 0)
    template_prs = report.get("template_count", 0)
    exceptions_count = report.get("exceptions_count", 0)
    avg_exception_approval_hours = report.get("avg_exception_approval_hours", 0)
    training_attendance = report.get("training_attendance", 0)

    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO governance_metrics_weekly(
                week_start, repo, total_prs, decision_prs, template_prs,
                exceptions_count, avg_exception_approval_hours, training_attendance, generated_at
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (week_start, repo) DO UPDATE SET
                total_prs = EXCLUDED.total_prs,
                decision_prs = EXCLUDED.decision_prs,
                template_prs = EXCLUDED.template_prs,
                exceptions_count = EXCLUDED.exceptions_count,
                avg_exception_approval_hours = EXCLUDED.avg_exception_approval_hours,
                training_attendance = EXCLUDED.training_attendance,
                generated_at = EXCLUDED.generated_at
            """,
            (
                week_start,
                repo,
                total_prs,
                decision_prs,
                template_prs,
                exceptions_count,
                avg_exception_approval_hours,
                training_attendance,
                report.get("generated_at")
            ),
        )
    conn.commit()


def main():
    parser = argparse.ArgumentParser(description="ETL: JSON -> Postgres (governance_metrics_weekly)")
    parser.add_argument("--in", dest="infile", required=True, help="Arquivo JSON gerado pelo coletor")
    args = parser.parse_args()

    infile = args.infile
    if not os.path.exists(infile):
        print(f"Arquivo não encontrado: {infile}")
        return

    with open(infile, "r", encoding="utf-8") as fh:
        report = json.load(fh)

    # Conexão Postgres via envvars
    pg = {
        "host": os.environ.get("PGHOST", "localhost"),
        "port": int(os.environ.get("PGPORT", 5432)),
        "user": os.environ.get("PGUSER", "postgres"),
        "password": os.environ.get("PGPASSWORD", ""),
        "dbname": os.environ.get("PGDATABASE", "postgres"),
    }

    dsn = f"host={pg['host']} port={pg['port']} user={pg['user']} password={pg['password']} dbname={pg['dbname']}"
    conn = psycopg2.connect(dsn)
    try:
        upsert_metrics(conn, report)
        print("ETL concluído com sucesso.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
