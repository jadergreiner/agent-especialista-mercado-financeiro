"""
Configuração para testes E2E.
Configura ambiente de teste com banco isolado e servidor de aplicação.
"""
import pytest
import subprocess
import time
import requests
from pathlib import Path


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """
    Configura o ambiente de teste antes de todos os testes E2E.
    Inicia banco de dados de teste e servidor da aplicação.
    """
    # Aqui seria configurado o banco de teste e servidor
    # Por enquanto, apenas um placeholder
    yield
    # Cleanup após os testes


@pytest.fixture(scope="session")
def test_server():
    """
    Inicia o servidor FastAPI para testes E2E.
    """
    # Placeholder - implementar quando houver servidor FastAPI
    server_process = None

    # Exemplo de como seria:
    # server_process = subprocess.Popen([
    #     "uvicorn", "main:app",
    #     "--host", "127.0.0.1",
    #     "--port", "8000",
    #     "--reload"
    # ])

    # Aguardar servidor iniciar
    # time.sleep(2)

    yield "http://localhost:8000"

    # Terminar servidor
    # if server_process:
    #     server_process.terminate()
    #     server_process.wait()


@pytest.fixture
def authenticated_page(page, test_server):
    """
    Fixture que retorna uma página já autenticada.
    """
    page.goto(f"{test_server}/login")

    # Simular login (ajustar conforme implementação real)
    page.fill("#username", "test@example.com")
    page.fill("#password", "password123")
    page.click("#login-button")

    # Aguardar redirecionamento
    page.wait_for_url(f"{test_server}/dashboard")

    return page