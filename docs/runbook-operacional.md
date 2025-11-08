# Runbook Operacional

## Deploy

1. Build images: docker-compose build
2. Deploy: docker-compose up -d
3. Health check: curl http://localhost:8000/health

## Rollback

1. docker-compose down
2. Restore backup: python scripts/backup_db.py restore
3. Deploy versão anterior

## Monitoramento

- Logs: docker-compose logs
- Métricas: http://localhost:9090 (Prometheus)
- Dashboards: http://localhost:3000 (Grafana)

Origin: TASK-35 - Criar runbook operacional