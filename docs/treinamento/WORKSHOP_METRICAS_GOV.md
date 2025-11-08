# Workshop: Métricas de Governança e Adoção de Regras (60-90 min)

Origin: DT-014 / LA-018 - Material de treinamento

Público-alvo: Tech Lead, Engenheiros, PO, DevOps

Objetivos
- Explicar as métricas implementadas
- Demonstrar o coletor de métricas (scripts)
- Ensinar interpretação do dashboard e ações corretivas

Agenda (90 minutos sugeridos)

1. Abertura e contexto (10 min)
   - Por que regras como DECISAO-002 importam
   - Objetivos do workshop

2. Métricas e modelo de dados (15 min)
   - Revisão das métricas (PRs que referenciam decisões, uso do template, exceções, tempo de aprovação, participação)
   - Tabela `governance_metrics_weekly`

3. Demonstração prática (20 min)
   - Executar `scripts/collect_metrics/github_metrics.py`
   - Ler JSON de saída
   - Inserir no Postgres (exemplo) e atualizar dashboard

4. Hands-on (30 min)
   - Dividir em pequenos grupos (2-3 pessoas)
   - Cada grupo executa o script localmente e gera um relatório
   - Validar resultados e propor uma ação corretiva (ex: falta de adesão a template)

5. Encerramento e próximos passos (15 min)
   - Plano de ação (responsáveis e prazos)
   - Como registrar exceções no backlog (DT-014)

Materiais
- Slides com conceitos e queries (criar `docs/treinamento/slides_metricas.pdf`)
- Scripts: `scripts/collect_metrics/github_metrics.py`
- Acesso: credenciais de leitura do repositório ou executar via CI

Checklist pós-workshop
- Registrar participação (treinamento_attendance)
- Agendar revisão semanal nas reuniões do Tech Lead
- Implementar alertas no dashboard para queda de adesão
