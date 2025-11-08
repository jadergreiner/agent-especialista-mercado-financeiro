"""
# Origin: AG-004 - Implementacao inicial de Audit Trails (skeleton)

Módulo de auditoria leve usando sqlite3 para armazenar eventos de auditoria em staging.
Projeto: gravar eventos com timestamp UTC, username, endpoint, method, status, request_id, ip e resumo.
"""
from fastapi import APIRouter, Depends, Query
from typing import Optional, List, Dict, Any
from datetime import datetime
import sqlite3
import os
from backend.api.security import require_role, Role

router = APIRouter()

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "audit.sqlite")


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
        CREATE TABLE IF NOT EXISTS audit_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            username TEXT,
            endpoint TEXT,
            method TEXT,
            status INTEGER,
            request_id TEXT,
            ip TEXT,
            summary TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def save_event(timestamp: str, username: str, endpoint: str, method: str, status: int, request_id: str, ip: Optional[str], summary: Optional[str]):
    init_db()
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO audit_events (timestamp, username, endpoint, method, status, request_id, ip, summary) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (timestamp, username, endpoint, method, status, request_id, ip, summary),
    )
    conn.commit()
    conn.close()


@router.get("/api/v1/audit/events")
def list_events(limit: int = Query(50, ge=1, le=1000), offset: int = 0, username: Optional[str] = None, endpoint: Optional[str] = None, start: Optional[str] = None, end: Optional[str] = None, _=Depends(require_role(Role.auditor))):
    """Retorna eventos de auditoria. Protegido pela role `auditor` (ou `admin` se adaptado).

    Filtros: username, endpoint, start e end datetimes (ISO).
    """
    init_db()
    conn = _get_conn()
    cur = conn.cursor()
    query = "SELECT * FROM audit_events WHERE 1=1"
    params: List[Any] = []
    if username:
        query += " AND username = ?"
        params.append(username)
    if endpoint:
        query += " AND endpoint = ?"
        params.append(endpoint)
    if start:
        query += " AND timestamp >= ?"
        params.append(start)
    if end:
        query += " AND timestamp <= ?"
        params.append(end)
    query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    results: List[Dict[str, Any]] = []
    for r in rows:
        results.append({k: r[k] for k in r.keys()})
    return {"count": len(results), "events": results}
