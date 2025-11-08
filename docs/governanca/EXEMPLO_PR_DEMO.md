# Exemplo de PR — Alteração em área sensível

**Título:** Atualizar integração de modelos IA e conformidade com DECISAO-002

**Descrição curta:** Este PR altera o código que integra modelos IA e adiciona métricas de observabilidade.

**Referência de Decisão:** DECISAO-002

**Checklist de conformidade:**
- [x] Referência a DECISAO(s) incluída
- [x] Plano mínimo de testes adicionado
- [x] Métricas / SLOs documentados
- [ ] Nota de Exceção anexada (não aplicável)

**Arquivos alterados:**
- `backend/models_integration.py` (integração de modelo)
- `docs/observability/metrics.md` (novas métricas)

**Como testar:**
1. Rodar suíte de testes unitários: `pytest tests/unit -q`
2. Validar endpoint `/health` e verificar métricas em Prometheus (staging)

**Aprovadores necessários:** Tech Lead, PO, Diretor Financeiro (se houver custo)
