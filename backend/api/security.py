"""
# Origin: AG-001 - Skeleton RBAC e controles (branch feature/AG-rbac-audit-masking)

Este módulo fornece um skeleton mínimo de RBAC para o MVP. Ele usa headers HTTP
simulados (`X-User` e `X-Roles`) para autenticação em modo de desenvolvimento.
Em ambientes reais, substitua por autenticação segura (OAuth2 / JWT) e integração
com o provedor de identidade.
"""
from fastapi import APIRouter, Header, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

router = APIRouter()


class Role(str, Enum):
    admin = "admin"
    presidente = "presidente"
    auditor = "auditor"


class User(BaseModel):
    username: str
    roles: List[Role]


def get_current_user(x_user: Optional[str] = Header(None), x_roles: Optional[str] = Header(None)) -> User:
    """Mock de autenticação para desenvolvimento.

    - `X-User`: nome do usuário
    - `X-Roles`: roles separadas por vírgula (ex.: "admin,presidente")
    """
    if not x_user:
        raise HTTPException(status_code=401, detail="Usuário não autenticado (X-User header ausente)")
    roles: List[Role] = []
    if x_roles:
        for r in [i.strip() for i in x_roles.split(",") if i.strip()]:
            try:
                roles.append(Role(r))
            except ValueError:
                # ignora roles desconhecidas no mock
                pass
    return User(username=x_user, roles=roles)


def require_role(role: Role):
    """Dependency generator que valida se o usuário possui a role requerida."""

    def dep(user: User = Depends(get_current_user)):
        if role not in user.roles:
            raise HTTPException(status_code=403, detail="Acesso negado: role insuficiente")
        return user

    return dep


@router.get("/api/v1/controls/me")
def whoami(user: User = Depends(get_current_user)):
    """Retorna informação básica do usuário a partir dos headers (mock)."""
    return {"username": user.username, "roles": [r.value for r in user.roles]}


@router.get("/api/v1/controls/admin-health")
def admin_health(user: User = Depends(require_role(Role.admin))):
    """Endpoint protegido que exige role `admin` (exemplo de RBAC)."""
    return {"status": "ok", "user": user.username, "roles": [r.value for r in user.roles]}
