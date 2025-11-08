# Origin: FEAT-001 - MVP Dashboard Público
import pytest
from playwright.sync_api import Page, expect

def test_dashboard_loads_and_shows_metrics(page: Page):
    """
    E2E: Dashboard carrega e exibe métricas principais
    """
    # Navegar para o dashboard
    page.goto("http://localhost:8501")  # Streamlit default port

    # Verificar título
    expect(page.locator("h1")).to_contain_text("Meu Home - Dashboard Executivo")

    # Verificar métricas principais
    expect(page.locator("text=Valor Total do Portfólio")).to_be_visible()
    expect(page.locator("text=P&L Total")).to_be_visible()
    expect(page.locator("text=Posições Ativas")).to_be_visible()

def test_dashboard_shows_positions_table(page: Page):
    """
    E2E: Dashboard exibe tabela de posições
    """
    page.goto("http://localhost:8501")

    # Aguardar carregamento
    page.wait_for_load_state("networkidle")

    # Verificar seção de posições
    expect(page.locator("text=Posições Atuais")).to_be_visible()

    # Verificar que há uma tabela (dataframe do Streamlit)
    # Streamlit usa classes específicas, mas vamos verificar conteúdo
    expect(page.locator("text=PETR4.SA")).to_be_visible()
    expect(page.locator("text=VALE3.SA")).to_be_visible()

def test_dashboard_shows_pnl_chart(page: Page):
    """
    E2E: Dashboard exibe gráfico de P&L
    """
    page.goto("http://localhost:8501")

    # Aguardar carregamento
    page.wait_for_load_state("networkidle")

    # Verificar seção do gráfico
    expect(page.locator("text=Evolução do P&L")).to_be_visible()

    # Verificar que há um gráfico (Plotly)
    # Plotly charts têm classes específicas
    expect(page.locator(".js-plotly-plot")).to_be_visible()