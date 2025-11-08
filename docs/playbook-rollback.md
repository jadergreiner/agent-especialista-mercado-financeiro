# Playbook de Rollback e Recovery

## Cenário de Rollback

Quando deploy falha ou causa incidentes.

## Steps de Rollback

1. Parar containers atuais
2. Restaurar backup DB
3. Deploy versão anterior
4. Validar funcionamento
5. Notificar stakeholders

## Recovery

- Usar scripts/backup_db.py para restore
- Monitorar por 24h pós-rollback

Origin: TASK-30 - Criar playbook rollback