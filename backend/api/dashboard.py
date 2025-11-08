# Origin: FEAT-001 - MVP Dashboard Público
import logging
import json
from fastapi import FastAPI
from fastapi.responses import JSONResponse
try:
    from .masking import _mask_obj as _mask_obj_for_tests
except Exception:
    from backend.api.masking import _mask_obj as _mask_obj_for_tests
from pydantic import BaseModel
from typing import List, Dict, Any
import random
from datetime import datetime, timedelta

# Configurar logging estruturado em JSON


class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)


logger = logging.getLogger()
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)

app = FastAPI(title="Agent Especialista - Dashboard API", version="1.0.0")

# Tenta incluir rotas de controles e segurança (skeleton RBAC/middleware).
try:
    # import relativo funciona quando o pacote é importado como módulo
    from .security import router as controls_router
except Exception:
    # fallback absoluto (quando executado de maneiras diferentes)
    from backend.api.security import router as controls_router

app.include_router(controls_router)
try:
    # registrar middleware de auditoria
    from .middleware import setup_audit_middleware
except Exception:
    from backend.api.middleware import setup_audit_middleware

setup_audit_middleware(app)

try:
    from .masking import setup_masking_middleware
except Exception:
    from backend.api.masking import setup_masking_middleware

# Registrar middleware de masking (aplica mascaramento em respostas JSON)
setup_masking_middleware(app)

try:
    from .audit import router as audit_router
except Exception:
    from backend.api.audit import router as audit_router

app.include_router(audit_router)
try:
    from .flags import router as flags_router
except Exception:
    from backend.api.flags import router as flags_router

app.include_router(flags_router)
try:
    from .metrics import router as metrics_router
except Exception:
    from backend.api.metrics import router as metrics_router

app.include_router(metrics_router)
try:
    from .users import router as users_router
except Exception:
    from backend.api.users import router as users_router

app.include_router(users_router)


class Position(BaseModel):
    symbol: str
    quantity: float
    avg_price: float
    current_price: float
    pnl: float
    pnl_percent: float


class DashboardSummary(BaseModel):
    total_portfolio_value: float
    total_pnl: float
    total_pnl_percent: float
    positions: List[Position]
    pnl_history: List[Dict[str, Any]]
    last_updated: str


@app.get("/")
async def root():
    """Endpoint raiz para health check."""
    return {"status": "ok", "message": "Dashboard API is running"}


@app.get("/api/v1/dashboard/summary")
async def get_dashboard_summary() -> DashboardSummary:
    """
    Retorna resumo do dashboard com posições mock e P&L histórico.
    """
    try:
        # Dados mock para MVP
        positions = [
            Position(
                symbol="PETR4.SA",
                quantity=1000,
                avg_price=25.50,
                current_price=26.80,
                pnl=1300.00,
                pnl_percent=5.10
            ),
            Position(
                symbol="VALE3.SA",
                quantity=500,
                avg_price=60.00,
                current_price=58.50,
                pnl=-750.00,
                pnl_percent=-2.50
            ),
            Position(
                symbol="ITUB4.SA",
                quantity=200,
                avg_price=22.00,
                current_price=23.10,
                pnl=220.00,
                pnl_percent=5.00
            ),
            Position(
                symbol="BBDC4.SA",
                quantity=300,
                avg_price=15.50,
                current_price=16.20,
                pnl=210.00,
                pnl_percent=4.52
            )
        ]

        total_portfolio_value = sum(p.current_price * p.quantity for p in positions)
        total_pnl = sum(p.pnl for p in positions)
        # Calcular percentual de P&L com proteção contra divisão por zero
        if total_portfolio_value != total_pnl:
            total_pnl_percent = (total_pnl / (total_portfolio_value - total_pnl)) * 100
        else:
            total_pnl_percent = 0

        # P&L histórico mock (últimos 30 dias)
        pnl_history = []
        base_value = total_portfolio_value - total_pnl
        for i in range(30):
            date = (datetime.now() - timedelta(days=29-i)).strftime("%Y-%m-%d")
            pnl_value = base_value + random.uniform(-5000, 5000)
            pnl_history.append({
                "date": date,
                "pnl": pnl_value,
                "pnl_percent": ((pnl_value - base_value) / base_value) * 100
            })

        last_updated_str = datetime.now().isoformat()
        return DashboardSummary(
            total_portfolio_value=round(total_portfolio_value, 2),
            total_pnl=round(total_pnl, 2),
            total_pnl_percent=round(total_pnl_percent, 2),
            positions=positions,
            pnl_history=pnl_history,
            last_updated=last_updated_str,
        )
    except Exception as e:
        print(f"Erro na API: {e}")
        import traceback
        traceback.print_exc()
        raise


@app.get("/api/v1/test/user")
async def _test_user_info():
    """Rota de teste que retorna PII — usada apenas por testes automatizados para validar masking."""
    payload = {
        "name": "Alice Silva",
        "email": "alice.silva@example.com",
        "cpf": "12345678901",
        "nested": {"contact_email": "contact@example.com", "phone": "5511999998888"}
    }
    # Aplicar masking diretamente para garantir resultado previsível nos testes
    masked = _mask_obj_for_tests(payload)
    return JSONResponse(masked)


if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando servidor...")
    uvicorn.run(app, host="127.0.0.1", port=8002)
