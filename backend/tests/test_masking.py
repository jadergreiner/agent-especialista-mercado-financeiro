"""Testes para middleware de masking genérico.
"""
import os
import sqlite3
from fastapi.testclient import TestClient
from backend.api.dashboard import app

client = TestClient(app)


def test_masking_applied_to_test_user():
    r = client.get("/api/v1/test/user")
    assert r.status_code == 200
    data = r.json()
    # name deve ser mascarado (ex.: 'A***')
    assert isinstance(data.get("name"), str)
    assert data["name"].endswith("***")
    # email deve conter '***@' depois do primeiro caractere
    assert "***@" in data.get("email", "")
    # cpf deve estar parcialmente mascarado
    assert data.get("cpf", "").startswith("***-***-")
    # nested.contact_email também deve ser mascarado
    nested = data.get("nested", {})
    assert "***@" in nested.get("contact_email", "")
    # telefone deve ter sufixo preservado
    assert nested.get("phone", "").startswith("(*** ) ")
