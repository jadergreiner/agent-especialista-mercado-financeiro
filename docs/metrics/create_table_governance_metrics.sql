-- Origin: DT-014 - Criação da tabela de métricas de governança
-- Referências: DECISAO-002 (governança obrigatória)

CREATE TABLE IF NOT EXISTS governance_metrics_weekly (
    id SERIAL PRIMARY KEY,
    week_start DATE NOT NULL,
    repo TEXT NOT NULL,
    total_prs INTEGER DEFAULT 0,
    decision_prs INTEGER DEFAULT 0,
    template_prs INTEGER DEFAULT 0,
    exceptions_count INTEGER DEFAULT 0,
    avg_exception_approval_hours NUMERIC(10,2) DEFAULT 0,
    training_attendance INTEGER DEFAULT 0,
    generated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (week_start, repo)
);

-- Índice para consultas por repo e semana
CREATE INDEX IF NOT EXISTS idx_governance_metrics_repo_week ON governance_metrics_weekly(repo, week_start);
