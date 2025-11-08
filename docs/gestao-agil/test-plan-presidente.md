## Test Plan: Fluxo Presidente — Cadastro de Operações (E2E + Rollback)

<!-- Origin: AG-008 - Definir Critérios de Aceitação e Test Plan -->

Versão: 2025-11-08
Responsável: Engenheiro QA + Engenheiro Backend

Objetivo
-------
Definir o Test Plan mínimo necessário para validar o fluxo crítico que permite ao Presidente cadastrar operações com dados reais em ambiente controlado. Incluir cenários E2E, critérios de aceitação e playbook de rollback.

Escopo
------
- Fluxo: Autenticação (Presidente) → Página/Endpoint de cadastro de operação → Persistência → Audit log → Visualização no dashboard
- Ambientes: Staging controlado (dados reais mascarados conforme política) e ambiente de release (para testes finais)

Requisitos pré-condição
----------------------
1. Gate "Test Plan & Acceptance Criteria" aprovado no Roadmap
2. Issue AG-008 criada e com checklist de aprovação
3. Ambiente de staging provisionado com backup e política de retention

Cenários E2E (mínimos)
----------------------
1. Autenticação com 2FA (quando habilitado)
   - Dado: Conta do Presidente provisionada em staging
   - Quando: Presidente realiza login com credenciais válidas e 2FA
   - Então: Sessão iniciada e token válido retornado; evento de login gravado no audit log

2. Cadastro de operação (happy path)
   - Dado: Presidente autenticado
   - Quando: Envia payload válido para `POST /api/v1/operations`
   - Então: Código 201 retornado; operação persistida; entrada no audit log com user_id, timestamp, action=create

3. Validação de masking/PII
   - Dado: Operação criada com PII
   - Quando: Visualizar operação em ambiente não-prod (usuário sem permissão de PII)
   - Então: Campos sensíveis devem estar mascarados conforme política (ex: cpf -> XXX.XXX.***-**) e audit trail registra acesso

4. Falha transacional e rollback
   - Dado: Simular erro na gravação (e.g., DB unavailable)
   - Quando: Cliente envia requisição de criação de operação
   - Então: Operação NÃO é persistida; resposta 503/500 apropriada; ação compensatória definida (retry/backoff) e playbook de rollback acionável

5. Reprodutibilidade e logs
   - Verificar que os logs estruturados (JSON) contêm user_id, request_id, timestamp, action e trace_id

Critérios de Aceitação (mínimos)
-------------------------------
- Todos os cenários E2E acima passam em CI para a branch de release
- Audit logs consultáveis em staging com queries básicas
- Política de masking aplicada em ambientes não-prod
- Playbook de rollback testado com restauração do estado pré-teste
- Aprovação documentada pelo PO e Tech Lead (checklist preenchido)

Playbook de Rollback (resumo)
----------------------------
1. Detectar falha (CI ou monitoramento manual)
2. Executar rota de compensação (API) se disponível
3. Restaurar backup mais recente (procedimento testado):
   - Restaurar BD de staging a partir de snapshot mais recente
   - Validar integridade e consistência
4. Registrar incidente e notificar stakeholders (Presidente/PO/TechLead)
5. Post-mortem com ações corretivas e teste de regressão

Plano de Execução e Responsabilidades
------------------------------------
- Engenheiro QA: escrever e automatizar testes Playwright/Pytest
- Engenheiro Backend: prover endpoints e mocks de falha para testes de rollback
- DevOps: disponibilizar staging com snapshots e scripts de restauração
- PO: validar critérios de aceitação e assinar checklist

Roteiro de Entrega (estimativa)
------------------------------
- 0.5 dia: Documentar Test Plan (este arquivo)
- 1 dia: Implementar E2E scripts básicos (3-5 cenários)
- 1 dia: Validar playbook de rollback em staging
- 0.5 dia: Revisão PO/Tech Lead e assinatura de checklist

Anexos/Referências
------------------
- Backlog: `docs/gestao-agil/BACKLOG_DEBITO_TECNICO.md` (ISSUE AG-008)
- Roadmap: `docs/gestao-agil/ROADMAP_DEBITO_TECNICO.md` (Gate Test Plan & Acceptance Criteria)
