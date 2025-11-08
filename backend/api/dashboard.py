# Origin: FEAT-001 - MVP Dashboard Público
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any
import random
from datetime import datetime, timedelta

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
    from .audit import router as audit_router
except Exception:
    from backend.api.audit import router as audit_router

app.include_router(audit_router)

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
        total_pnl_percent = (total_pnl / (total_portfolio_value - total_pnl)) * 100 if total_portfolio_value != total_pnl else 0

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

        return DashboardSummary(
            total_portfolio_value=round(total_portfolio_value, 2),
            total_pnl=round(total_pnl, 2),
            total_pnl_percent=round(total_pnl_percent, 2),
            positions=positions,
            pnl_history=pnl_history,
            last_updated=datetime.now().isoformat()
        )
    except Exception as e:
        print(f"Erro na API: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando servidor...")
    uvicorn.run(app, host="127.0.0.1", port=8002)