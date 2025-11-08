# Origin: FEAT-001 - MVP Dashboard Público
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Agent Especialista - Meu Home",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Meu Home - Dashboard Executivo")
st.markdown("---")

# Função para buscar dados da API
def get_dashboard_data():
    try:
        response = requests.get("http://localhost:8000/api/v1/dashboard/summary", timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao conectar com a API: {e}")
        st.info("Certifique-se de que o backend está rodando: `python backend/api/dashboard.py`")
        return None

# Buscar dados
data = get_dashboard_data()

if data:
    # Métricas principais
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Valor Total do Portfólio",
            f"R$ {data['total_portfolio_value']:,.2f}",
            help="Valor atual de todas as posições"
        )

    with col2:
        pnl_color = "normal" if data['total_pnl'] >= 0 else "inverse"
        st.metric(
            "P&L Total",
            f"R$ {data['total_pnl']:,.2f}",
            f"{data['total_pnl_percent']:+.2f}%",
            delta_color=pnl_color,
            help="Lucro/Prejuízo total"
        )

    with col3:
        st.metric(
            "Posições Ativas",
            len(data['positions']),
            help="Número de ativos no portfólio"
        )

    st.markdown("---")

    # Gráfico P&L histórico
    st.subheader("📈 Evolução do P&L (30 dias)")

    pnl_df = pd.DataFrame(data['pnl_history'])
    pnl_df['date'] = pd.to_datetime(pnl_df['date'])
    pnl_df = pnl_df.sort_values('date')

    fig = px.line(
        pnl_df,
        x='date',
        y='pnl',
        title='P&L Diário',
        labels={'pnl': 'Valor (R$)', 'date': 'Data'}
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Tabela de posições
    st.subheader("📋 Posições Atuais")

    positions_df = pd.DataFrame(data['positions'])
    positions_df['pnl'] = positions_df['pnl'].apply(lambda x: f"R$ {x:,.2f}")
    positions_df['pnl_percent'] = positions_df['pnl_percent'].apply(lambda x: f"{x:+.2f}%")
    positions_df['current_price'] = positions_df['current_price'].apply(lambda x: f"R$ {x:.2f}")
    positions_df['avg_price'] = positions_df['avg_price'].apply(lambda x: f"R$ {x:.2f}")

    st.dataframe(
        positions_df[['symbol', 'quantity', 'avg_price', 'current_price', 'pnl', 'pnl_percent']],
        column_config={
            "symbol": st.column_config.TextColumn("Ativo", width="medium"),
            "quantity": st.column_config.NumberColumn("Quantidade", width="small"),
            "avg_price": st.column_config.TextColumn("Preço Médio", width="medium"),
            "current_price": st.column_config.TextColumn("Preço Atual", width="medium"),
            "pnl": st.column_config.TextColumn("P&L", width="medium"),
            "pnl_percent": st.column_config.TextColumn("% P&L", width="small"),
        },
        hide_index=True,
        use_container_width=True
    )

    # Última atualização
    st.caption(f"Última atualização: {datetime.fromisoformat(data['last_updated']).strftime('%d/%m/%Y %H:%M:%S')}")

else:
    st.warning("Não foi possível carregar os dados do dashboard.")
    st.info("Para testar localmente:")
    st.code("cd backend/api && python dashboard.py", language="bash")
    st.code("streamlit run frontend/dashboard.py", language="bash")