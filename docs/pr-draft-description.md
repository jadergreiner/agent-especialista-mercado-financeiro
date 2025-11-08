# PR Rascunho: Implementação de Controles de Governança

## Descrição

Implementação completa de RBAC, audit trails, masking, feature flags e infraestrutura para rollout controlado do MVP Dashboard.

## Mudanças Principais

- RBAC com roles admin/presidente/auditor
- Audit trails em SQLite com middleware
- Autenticação HMAC PoC
- Scripts de masking e backup
- Feature flags para controle de dados reais
- Métricas /metrics
- Endpoints CRUD usuários
- Dockerfiles e docker-compose para staging
- Testes E2E com Playwright
- CI/CD workflows
- Documentação de governança

## Referências

- DECISAO-002: Regras obrigatórias de governança
- Test Plan AG-008 executado
- Checklist jurídica: Pendente aprovação final

## Testes

- Unit tests: ✅ Passando
- E2E: ✅ Configurado
- Load test: ✅ Implementado

## Próximos Passos

Após merge, executar rollout controlado com monitoramento 72h.

Origin: TASK-40 - Criar PR rascunho