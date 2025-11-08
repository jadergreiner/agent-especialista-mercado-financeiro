import os
import sys
import pathlib

# Ensure repo root is on sys.path for imports during tests
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.utils.masking import mask_dict


def test_mask_dict_simple():
    data = {
        "nome_presidente": "Joao Silva",
        "cpf": "123.456.789-00",
        "email": "joao@example.com",
        "saldo": 1000,
    }

    masked = mask_dict(data)
    assert masked["nome_presidente"] == "***MASKED***"
    assert masked["cpf"] == "***MASKED***"
    assert masked["email"] == "***MASKED***"
    assert masked["saldo"] == 1000


def test_mask_dict_nested():
    data = {
        "cliente": {
            "nome": "Cliente X",
            "ssn": "999-99-9999",
        },
        "token": "secrettoken",
    }
    masked = mask_dict(data)
    assert masked["cliente"]["ssn"] == "***MASKED***"
    assert masked["cliente"]["nome"] == "Cliente X"
    assert masked["token"] == "***MASKED***"
"""Testes para middleware de masking genérico.
"""
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
