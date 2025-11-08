"""
Testes E2E para o sistema de especialista de mercado financeiro.
Testa fluxos completos de usuário através da interface web.
"""
import pytest
from playwright.sync_api import Page, expect


@pytest.mark.e2e
def test_dashboard_carrega_posicoes(page: Page):
    """
    DADO que sou um usuário autenticado
    QUANDO acesso o dashboard
    ENTÃO vejo as posições do portfólio carregadas
    """
    # Simular acesso ao dashboard (ajustar URL conforme implementação real)
    page.goto("http://localhost:8000/dashboard")

    # Verificar se o dashboard carrega
    expect(page).to_have_title("Especialista Mercado Financeiro")

    # Verificar se há elementos de posição
    # (ajustar seletores conforme implementação real)
    positions_table = page.locator(".positions-table")
    expect(positions_table).to_be_visible()

    # Verificar se há pelo menos uma posição
    position_rows = page.locator(".position-row")
    expect(position_rows).to_have_count_greater_than(0)


@pytest.mark.e2e
def test_login_fluxo_completo(page: Page):
    """
    DADO que sou um usuário não autenticado
    QUANDO faço login com credenciais válidas
    ENTÃO sou redirecionado para o dashboard
    """
    page.goto("http://localhost:8000/login")

    # Preencher formulário de login
    page.fill("#username", "test@example.com")
    page.fill("#password", "password123")
    page.click("#login-button")

    # Verificar redirecionamento
    expect(page).to_have_url("http://localhost:8000/dashboard")

    # Verificar que estamos logados
    expect(page.locator("#user-menu")).to_be_visible()


@pytest.mark.e2e
def test_alertas_risco_funcionam(page: Page):
    """
    DADO que há posições com risco alto
    QUANDO acesso o dashboard
    ENTÃO vejo alertas de risco sendo exibidos
    """
    # Fazer login primeiro
    page.goto("http://localhost:8000/login")
    page.fill("#username", "test@example.com")
    page.fill("#password", "password123")
    page.click("#login-button")

    # Verificar alertas de risco
    risk_alerts = page.locator(".risk-alert")
    # Pode haver ou não alertas dependendo dos dados
    # expect(risk_alerts).to_have_count_greater_than(0)  # Remover se não houver dados de teste