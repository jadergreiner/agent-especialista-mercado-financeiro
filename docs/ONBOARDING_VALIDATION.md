# Validação de Onboarding Técnico — Checklist e Automação

**Criado:** 2025-11-07
**Owner:** Tech Lead

## Objetivo

Garantir que qualquer novo desenvolvedor consiga preparar ambiente local e executar suíte básica de testes em menos de 1 dia útil. Documentar passos e automatizar validações para reduzir fricção no onboarding.

## Checklist Manual (mínimo)

1. Acesso ao repositório (SSH/HTTPS) confirmado.
2. Variáveis de ambiente necessárias documentadas em `.env.example`.
3. Python recomendado: 3.11+ instalado.
4. Virtualenv/venv criado e ativado.
5. Instalar dependências: `pip install -r backend/requirements.txt`.
6. Banco local: instruções para executar container PostgreSQL com Docker Compose.
7. Rodar migrações (se aplicável).
8. Rodar testes unitários: `pytest -q` — todos devem passar.
9. Rodar um teste de integração leve (ex: `tests/integration/test_health.py`).
10. Acesso à documentação da API (OpenAPI) e validação rápida de um endpoint.

## Scripts de Validação Automática

### Script PowerShell: `scripts/validate_onboarding.ps1`

Criado script automatizado para validar setup básico. Executar em PowerShell:

```powershell
# No diretório raiz do projeto
.\scripts\validate_onboarding.ps1
```

**O que o script verifica:**

1. Versão do Python (3.11+)
2. Virtualenv ativa (recomendado)
3. Instalação de dependências via `pip`
4. Serviços Docker (Postgres, Redis) via docker-compose
5. Testes unitários com pytest
6. Endpoint de saúde (/health)

**Saídas esperadas:**

- Código de saída 0: Tudo OK
- Código de saída 1: Falha crítica (setup incompleto)

**Pré-requisitos para o script:**

- PowerShell 5.1+
- Python 3.11+ instalado
- Docker Desktop rodando
- Arquivos: `backend/requirements.txt`, `docker-compose.yml`, `backend/tests/unit/`

### Próximos passos para automação

1. Adicionar job CI que executa este script em PRs (GitHub Actions).
2. Criar versão para Linux/Mac (Bash) se necessário.
3. Integrar com ferramentas de lint (black, flake8) no script.

## Critérios de Aceite

- Tempo de setup para desenvolvedor novo: < 8 horas (meta inicial)
- Script `scripts/validate_onboarding.ps1` retorna código 0 em ambiente limpo
- Documentação `docs/ONBOARDING_VALIDATION.md` atualizada e linkada no README

## Métricas

- Tempo médio de onboarding (dias)
- Porcentagem de erros de setup detectados na primeira execução do script
- Número de chamadas ao canal de suporte por novos devs no primeiro mês

## Próximos passos

1. Implementar `scripts/validate_onboarding.ps1` e versionar.
2. Adicionar job CI que executa validação de onboarding em branch `dev` (opcional).
3. Atualizar `BACKLOG_DEBITO_TECNICO.md` para referenciar este documento e marcar DT-010 como iniciado.
