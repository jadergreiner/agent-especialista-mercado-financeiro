"""Expor métricas em formato textual simples compatível com Prometheus (regex)."""
from fastapi import APIRouter
from backend.api.audit import get_metrics_text

router = APIRouter()


@router.get('/metrics')
def metrics():
    return get_metrics_text()
