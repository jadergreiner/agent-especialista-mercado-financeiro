# Política de Masking (rascunho)

Origin: AG-005 - Implementação inicial de masking

> Rascunho técnico. Esta política deve ser validada e aprovada pelo time de Segurança e pelo PO antes de promoção para ambientes com dados reais.

## Resumo

Este documento descreve a política mínima para mascaramento (masking) de dados sensíveis (PII) em ambientes não produtivos e em endpoints de API que expõem informações de usuários ou clientes. O objetivo é reduzir o risco de exposição de PII em staging, testes e dumps/exports.

## Escopo

- Aplicável a: staging, ambientes locais com dados reais, dumps/exports e endpoints administrativos.
- Não aplicar masking no banco de produção em operações normais onde dados completos são necessários; nesses casos usar controles de acesso (RBAC), logs com retenção adequada e processos de governança.

## Definições

- **PII**: Personally Identifiable Information — exemplos: nome, email, CPF/SSN, telefone, documentos.
- **Masking**: transformação que oculta PII (irreversível ou parcialmente reversível conforme política), reduzindo risco de exposição.

## Regras básicas (mínimo)

1. Endpoints públicos ou de staging devem retornar PII mascarado por padrão.
2. Campos sensíveis iniciais (heurística): `name`, `email`, `cpf`, `ssn`, `document`, `phone`, `telefone`.
3. Exportações administrativas (CSV/JSON) só podem ser realizadas por usuários com role `admin`; todas as exportações devem ficar registradas em audit trail.
4. Scripts de preparação de staging (ex.: `scripts/mask_sqlite.py`) devem ser usados para gerar cópias mascaradas antes de carregar em staging.

## Processo recomendado

1. Gerar backup do DB real (criptografado) e armazenar em local seguro.
2. Executar `scripts/mask_sqlite.py` ou pipeline equivalente para criar dataset mascarado.
3. Validar amostras e executar testes E2E em staging.
4. Registrar no audit trail cada execução do processo de masking e cada exportação de dados.

## Testes e QA

- Cobrir com testes unitários e E2E que verifiquem que os campos sensíveis são mascarados.
- Incluir casos de borda: valores nulos, variações de nomes de campo, listas aninhadas e respostas em streaming.

## Responsabilidades

- **Devs Backend**: implementar e manter a biblioteca de masking e os scripts de staging.
- **Time de Segurança**: validar taxa de exposição, definir catálogo final de campos sensíveis e aprovar procedimentos.
- **Product Owner / Compliance**: aprovar política e fluxo de promoção para staging/produção.

## Implementação técnica

- **Ferramenta**: script `scripts/mask_sqlite.py` e middleware de masking em `backend/api/masking.py`.
- **Execução**: aplicar masking em cópias de DB e em respostas JSON de ambientes não produtivos; preferir catálogo configurável por endpoint para produção.
- **Reversibilidade**: masking deve ser irreversível por design quando tratar-se de dados sensíveis, salvo exceções executadas por processos aprovados e auditados.

## Exemplos

### Antes do masking

```json
{
  "email": "presidente@empresa.com",
  "nome": "João Silva",
  "cpf": "123.456.789-00",
  "telefone": "(11) 99999-9999"
}
```

### Após masking (exemplo)

```json
{
  "email": "userABC@empresa.com",
  "nome": "Nome Mascarado",
  "cpf": "XXX.XXX.XXX-XX",
  "telefone": "(21) 88888-8888"
}
```

## Evolução (próximos passos)

1. Transformar heurística em catálogo configurável por endpoint e versão controlada.
2. Integrar masking no pipeline CI/CD de staging e criar métricas de cobertura (Prometheus) e alertas.
3. Incluir checklist no template de PR para mudanças que exponham dados (ver `.github/PULL_REQUEST_TEMPLATE.md`).

## Referências

- DECISAO-002 — aplicar caso a política exija mudanças arquiteturais ou escolha de modelos IA.
- `scripts/mask_sqlite.py` — utilitário no repositório para gerar cópias mascaradas.

---

Data: 2025-11-08

Autor: equipe de engenharia (rascunho automático)

Origin: TASK-15 - Documentar políticas de masking
