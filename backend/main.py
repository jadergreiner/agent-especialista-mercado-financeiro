"""
Agent Especialista Mercado Financeiro - Ponto de Entrada do Backend
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# Origin: feature/AG-rbac-audit-masking
try:
    # Conditional import to avoid breaking environments without starlette/fastapi extras
    from backend.middleware.audit import AuditMiddleware  # type: ignore
    from backend.utils.masking import mask_dict  # type: ignore
except Exception:
    AuditMiddleware = None
    mask_dict = None

app = FastAPI(
    title="API Agent Especialista de Mercado Financeiro",
    description="Agente de IA para análise global de mercado financeiro",
    version="0.1.0"
)

# Configuração CORS para frontend Angular
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # Porta padrão do Angular
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def raiz():
    """Endpoint de verificação de saúde"""
    return {
        "status": "online",
        "servico": "Agent Especialista de Mercado Financeiro",
        "versao": "0.1.0"
    }

@app.get("/api/v1/saude")
async def verificacao_saude():
    """Verificação detalhada de saúde"""
    return {
        "status": "saudavel",
        "servicos": {
            "api": "operacional",
            "feeds_dados": "pendente",
            "motor_analise": "pendente"
        }
    }


# Register audit middleware only in development/demo
if os.environ.get("ENABLE_DEMO_AUDIT", "true").lower() in ("1", "true", "yes") and AuditMiddleware is not None:
    # use a relative path log inside the repo for demo purposes
    audit_log = os.environ.get("DEMO_AUDIT_LOG", ".logs/audit.log")
    app.add_middleware(AuditMiddleware, logfile=audit_log)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
