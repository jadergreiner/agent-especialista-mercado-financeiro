# Business Case — Modernização e Resolução de Débito Técnico

**Criado:** 2025-11-07
**Owner:** Product Owner + Tech Lead

## Resumo Executivo

Este documento resume o caso de negócio para a execução do roadmap de débito técnico que transforma o projeto de um monolito SQLite para uma arquitetura modular production-ready (PostgreSQL, Redis, observability, testes E2E). O objetivo é quantificar custos, benefícios e prazos para apoiar decisões de priorização.

## Objetivos

- Reduzir tempo médio de entrega (lead time) e retrabalho.
- Aumentar a estabilidade (menos bugs em produção).
- Permitir scaling horizontal e multi-tenant no futuro.
- Melhorar onboarding e capacidade de contratar/treinar novos devs mais rapidamente.

## Premissas

- Equipe alvo: 2 engenheiros full-time dedicados ao projeto (escopo inicial).
- Custo médio por engenheiro: R$ 40.000 / mês (exemplo, validar com financeiro).
- Duração estimada do roadmap inicial: 4 meses (8 sprints).
- Custos infra iniciais: R$ 2.000 / mês (hosting, DB, Redis) — estimativa.

## Estimativa de Custos (4 meses)

- Salários (2 engenheiros x 4 meses): R$ 40.000 * 2 * 4 = R$ 320.000
- Infra e licenças: R$ 2.000 * 4 = R$ 8.000
- Contingência (10%): R$ 32.800

**Custo Total Estimado:** R$ 360.800

> Observação: ajustar valores reais com dados de RH/financeiro.

## Benefícios (estimativas)

- Redução de retrabalho/bugs: estima-se 30-50% menos horas gastas em correções após estabilização.
- Aceleração do desenvolvimento: produtividade 2x após modularização (menor tempo de entendimento e merges).
- Economia operacional: menos incidentes → menos horas de suporte.
- Risco reduzido para falhas críticas por causa da observabilidade e testes E2E.

### KPI financeiros (exemplo)

- Horas economizadas por mês após rollout: 160h (1 engenheiro full-time equivalente)
- Valor económico mensal recuperado: 160h * R$ 250/h ≈ R$ 40.000

## Cenários de ROI

1. Cenário Conservador
   - Aceleração: 1.3x
   - Horas economizadas: 80h/mês
   - Economia mensal: R$ 20.000
   - Payback: 360.800 / 20.000 ≈ 18 meses

2. Cenário Esperado
   - Aceleração: 2x
   - Horas economizadas: 160h/mês
   - Economia mensal: R$ 40.000
   - Payback: 360.800 / 40.000 ≈ 9 meses

3. Cenário Otimista
   - Aceleração: 3x
   - Horas economizadas: 240h/mês
   - Economia mensal: R$ 60.000
   - Payback: 360.800 / 60.000 ≈ 6 meses

> Nota: os valores por hora e estimativas devem ser validados com Financeiro e Product Owner.

## Riscos e Mitigações (Financeiro/Operacional)

- Risco: Estimativas de custo incorretas → Mitigação: validar com RH/Financeiro
- Risco: Menor ganho de produtividade do que o esperado → Mitigação: sprints de validação com KPIs e pivot rápido
- Risco: Endpoints críticos afetados durante refactor → Mitigação: testes de regressão e deploy canary

## KPIs e Métricas de Sucesso

- Redução de horas gastas em bugfixes (meta: -40% em 3 meses após rollout)
- Tempo médio de onboarding de novo dev (meta: de 1 semana para 2 dias)
- Cobertura de testes: meta 80% + testes E2E para fluxos críticos
- SLA/uptime: manter 99.9% durante rollout

## Próximos Passos

1. Validar premissas de custo com Financeiro.
2. Refinar estimativas por EPIC (DT-001..DT-011).
3. Agendar workshop de priorização com PO, Tech Lead e Financeiro.
4. Medir linha de base (baseline) atual para cada KPI antes do início.

---

*Documento inicial — números provisórios. Atualizar após validação com stakeholders.*
