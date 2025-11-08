"""
# Origin: AG-013 - Endpoint CRUD mínimo de usuários

Fornece operações básicas de gestão de usuários (armazenamento SQLite leve para staging).
As operações são protegidas pela role `admin`.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import os
import json
from backend.api.security import require_role, Role

router = APIRouter()

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'users.sqlite')


def _get_conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            roles TEXT
        )
        """
    )
    conn.commit()
    conn.close()


class UserIn(BaseModel):
    username: str
    roles: List[str]


class UserOut(BaseModel):
    username: str
    roles: List[str]


@router.post('/api/v1/users', response_model=UserOut)
def create_user(payload: UserIn, _=Depends(require_role(Role.admin))):
    init_db()
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM users WHERE username = ?", (payload.username,))
    if cur.fetchone():
        conn.close()
        raise HTTPException(status_code=409, detail='Usuário já existe')
    cur.execute("INSERT INTO users (username, roles) VALUES (?, ?)", (payload.username, json.dumps(payload.roles)))
    conn.commit()
    conn.close()
    return {'username': payload.username, 'roles': payload.roles}


@router.get('/api/v1/users', response_model=List[UserOut])
def list_users(_=Depends(require_role(Role.admin))):
    init_db()
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT username, roles FROM users")
    rows = cur.fetchall()
    conn.close()
    return [{'username': r['username'], 'roles': json.loads(r['roles'])} for r in rows]


@router.get('/api/v1/users/{username}', response_model=UserOut)
def get_user(username: str, _=Depends(require_role(Role.admin))):
    init_db()
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT username, roles FROM users WHERE username = ?", (username,))
    r = cur.fetchone()
    conn.close()
    if not r:
        raise HTTPException(status_code=404, detail='Usuário não encontrado')
    return {'username': r['username'], 'roles': json.loads(r['roles'])}


@router.put('/api/v1/users/{username}', response_model=UserOut)
def update_user(username: str, payload: UserIn, _=Depends(require_role(Role.admin))):
    if username != payload.username:
        raise HTTPException(status_code=400, detail='username mismatch')
    init_db()
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE users SET roles = ? WHERE username = ?", (json.dumps(payload.roles), username))
    if cur.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail='Usuário não encontrado')
    conn.commit()
    conn.close()
    return {'username': payload.username, 'roles': payload.roles}


@router.delete('/api/v1/users/{username}')
def delete_user(username: str, _=Depends(require_role(Role.admin))):
    init_db()
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE username = ?", (username,))
    if cur.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail='Usuário não encontrado')
    conn.commit()
    conn.close()
    return {'status': 'deleted', 'username': username}
