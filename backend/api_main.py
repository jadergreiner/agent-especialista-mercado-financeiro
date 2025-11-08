"""
API REST para o Especialista de Mercado Financeiro.
Documentação automática gerada pelo FastAPI/OpenAPI.
"""
from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from decimal import Decimal


app = FastAPI(
    title="Especialista Mercado Financeiro API",
    description="API para análise e gestão de portfólio de investimentos",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# Modelos Pydantic
class UserBase(BaseModel):
    """Modelo base para usuário."""
    email: str = Field(..., description="Email do usuário", example="user@example.com")
    full_name: Optional[str] = Field(None, description="Nome completo", example="João Silva")


class UserCreate(UserBase):
    """Modelo para criação de usuário."""
    password: str = Field(..., description="Senha do usuário", min_length=8)


class User(UserBase):
    """Modelo completo de usuário."""
    id: int
    is_active: bool = True
    created_at: datetime
    updated_at: datetime


class PositionBase(BaseModel):
    """Modelo base para posição."""
    ticker: str = Field(..., description="Código do ativo", example="PETR4")
    quantity: Decimal = Field(..., description="Quantidade de ativos", gt=0)
    avg_price: Decimal = Field(..., description="Preço médio de entrada", gt=0)


class Position(PositionBase):
    """Modelo completo de posição."""
    id: int
    user_id: int
    current_price: Optional[Decimal] = None
    market_value: Optional[Decimal] = None
    unrealized_pnl: Optional[Decimal] = None
    created_at: datetime
    updated_at: datetime


class RiskAlert(BaseModel):
    """Modelo para alertas de risco."""
    id: int
    user_id: int
    position_id: Optional[int] = None
    alert_type: str = Field(..., description="Tipo do alerta", example="high_risk")
    message: str = Field(..., description="Mensagem do alerta")
    severity: str = Field(..., description="Severidade", example="high")
    is_read: bool = False
    created_at: datetime


# Dependências
def get_current_user() -> int:
    """
    Dependência para obter usuário atual.

    Returns:
        ID do usuário autenticado

    Raises:
        HTTPException: Quando usuário não autenticado
    """
    # Placeholder - implementar autenticação JWT real
    return 1


# Endpoints
@app.get("/")
async def root():
    """
    Endpoint raiz da API.

    Returns:
        Mensagem de boas-vindas
    """
    return {"message": "Especialista Mercado Financeiro API", "version": "1.0.0"}


@app.get("/api/v1/portfolio/positions", response_model=List[Position])
async def get_positions(
    user_id: int = Depends(get_current_user),
    limit: int = 50,
    offset: int = 0
):
    """
    Retorna todas as posições abertas do portfólio do usuário.

    Args:
        user_id: ID do usuário autenticado (via JWT)
        limit: Número máximo de posições a retornar (padrão: 50)
        offset: Número de posições a pular (para paginação)

    Returns:
        Lista de posições com:
        - ticker (str): Código do ativo (ex: "PETR4")
        - quantity (Decimal): Quantidade de contratos
        - avg_price (Decimal): Preço médio de entrada
        - current_price (Decimal): Preço atual
        - market_value (Decimal): Valor de mercado
        - unrealized_pnl (Decimal): P&L não realizado
        - created_at: Data de criação
        - updated_at: Data de atualização

    Raises:
        401: Usuário não autenticado
        403: Usuário sem permissão para acessar posições
    """
    # Placeholder - implementar lógica real
    return []


@app.get("/api/v1/portfolio/positions/{position_id}", response_model=Position)
async def get_position(
    position_id: int,
    user_id: int = Depends(get_current_user)
):
    """
    Retorna uma posição específica do portfólio.

    Args:
        position_id: ID da posição
        user_id: ID do usuário autenticado

    Returns:
        Detalhes da posição

    Raises:
        401: Usuário não autenticado
        403: Usuário sem permissão
        404: Posição não encontrada
    """
    # Placeholder
    raise HTTPException(status_code=404, detail="Position not found")


@app.post("/api/v1/portfolio/positions", response_model=Position)
async def create_position(
    position: PositionBase,
    user_id: int = Depends(get_current_user)
):
    """
    Cria uma nova posição no portfólio.

    Args:
        position: Dados da posição a criar
        user_id: ID do usuário autenticado

    Returns:
        Posição criada

    Raises:
        401: Usuário não autenticado
        400: Dados inválidos
    """
    # Placeholder
    return Position(
        id=1,
        user_id=user_id,
        **position.dict(),
        current_price=None,
        market_value=None,
        unrealized_pnl=None,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )


@app.get("/api/v1/risk/alerts", response_model=List[RiskAlert])
async def get_risk_alerts(
    user_id: int = Depends(get_current_user),
    unread_only: bool = False
):
    """
    Retorna alertas de risco do usuário.

    Args:
        user_id: ID do usuário autenticado
        unread_only: Retornar apenas alertas não lidos

    Returns:
        Lista de alertas de risco

    Raises:
        401: Usuário não autenticado
    """
    # Placeholder
    return []


@app.put("/api/v1/risk/alerts/{alert_id}/read")
async def mark_alert_read(
    alert_id: int,
    user_id: int = Depends(get_current_user)
):
    """
    Marca um alerta como lido.

    Args:
        alert_id: ID do alerta
        user_id: ID do usuário autenticado

    Raises:
        401: Usuário não autenticado
        404: Alerta não encontrado
    """
    # Placeholder
    return {"message": "Alert marked as read"}


# Health check
@app.get("/health")
async def health_check():
    """
    Endpoint de health check.

    Returns:
        Status da aplicação
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": "1.0.0"
    }