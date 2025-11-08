# Plano de Migração Audit para Postgres

## Motivação

SQLite adequado para PoC, mas Postgres necessário para escala e backups robustos.

## Passos

1. Instalar psycopg2-binary
2. Criar migrations com Alembic
3. Migrar dados existentes
4. Atualizar código para usar Postgres
5. Testar migração

## Benefícios

- Concorrência melhor
- Backups automáticos
- Escalabilidade

Origin: TASK-28 - Migrar audit Postgres