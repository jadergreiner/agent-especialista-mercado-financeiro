# -*- coding: utf-8 -*-
"""
Dashboard (Streamlit) — Relatórios e Sinais

Funcionalidades:
- Relatórios: lista e filtro de relatórios (SQLite), visualização de payload JSON
- Sinais: leitura dos eventos em backend/bus, filtro por contrato/classe/instrumento, visualização de payload

Execução:
  streamlit run backend/app_dashboard.py
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
import sys
from typing import List, Dict, Any

import pandas as pd
import streamlit as st


ROOT = Path(__file__).parent
SRC = ROOT / 'src'
sys.path.insert(0, str(SRC))
DB_PATH = ROOT / 'data' / 'mercado.db'
BUS_DIR = ROOT / 'bus'


@st.cache_data(show_spinner=False)
def _carregar_relatorios(limit: int = 200) -> pd.DataFrame:
    if not DB_PATH.exists():
        return pd.DataFrame(columns=['id','classe_ativo','par','timestamp','operacao','vies_sessao','rr'])
    con = sqlite3.connect(str(DB_PATH))
    try:
        df = pd.read_sql_query(
            f"SELECT id, classe_ativo, par, timestamp, operacao, vies_sessao, rr FROM relatorios_intraday ORDER BY timestamp DESC LIMIT {int(limit)}",
            con
        )
        return df
    finally:
        con.close()


@st.cache_data(show_spinner=False)
def _carregar_payload(id_registro: int) -> Dict[str, Any] | None:
    if not DB_PATH.exists():
        return None
    con = sqlite3.connect(str(DB_PATH))
    try:
        cur = con.cursor()
        cur.execute("SELECT payload_json FROM relatorios_intraday WHERE id=?", (id_registro,))
        row = cur.fetchone()
        if not row:
            return None
        return json.loads(row[0])
    finally:
        con.close()


@st.cache_data(show_spinner=False)
def _carregar_eventos_bus() -> pd.DataFrame:
    BUS_DIR.mkdir(exist_ok=True)
    arquivos = sorted(BUS_DIR.glob('*.json'))
    linhas: List[Dict[str, Any]] = []
    for arq in arquivos:
        try:
            j = json.loads(arq.read_text(encoding='utf-8'))
            valido = j.get('valid')
            ev = j.get('event') or {}
            contrato = (ev.get('contractVersion') or '').strip()
            classe = ev.get('classeAtivo')
            instrumento = (ev.get('instrumento') or {}).get('id')
            ts = ev.get('timestamp')
            linhas.append({
                'arquivo': arq.name,
                'contrato': contrato,
                'classe': classe,
                'instrumento': instrumento,
                'timestamp': ts,
                'valid': bool(valido)
            })
        except Exception:
            continue
    if not linhas:
        return pd.DataFrame(columns=['arquivo','contrato','classe','instrumento','timestamp','valid'])
    return pd.DataFrame(linhas).sort_values('timestamp', ascending=False)


def pagina_relatorios():
    st.header('Relatórios (SQLite)')
    limite = st.sidebar.number_input('Limite', min_value=50, max_value=2000, value=200, step=50)
    df = _carregar_relatorios(limit=limite)
    if df.empty:
        st.info('Sem relatórios encontrados. Gere relatórios via CLIs para popular o banco.')
        return
    col1, col2 = st.columns([2,2])
    with col1:
        classe = st.selectbox('Classe', options=['(todas)'] + sorted(df['classe_ativo'].dropna().unique().tolist()))
    with col2:
        filtro_par = st.text_input('Filtro por Par/Ativo (contém)')

    df_view = df.copy()
    if classe != '(todas)':
        df_view = df_view[df_view['classe_ativo'] == classe]
    if filtro_par:
        df_view = df_view[df_view['par'].str.contains(filtro_par, case=False, na=False)]

    st.dataframe(df_view, use_container_width=True, hide_index=True)

    sel_id = st.number_input('ID do relatório para inspecionar', min_value=1, step=1)
    if st.button('Carregar payload'):
        payload = _carregar_payload(int(sel_id))
        if not payload:
            st.warning('Payload não encontrado para o ID informado.')
        else:
            st.subheader('Payload JSON')
            st.json(payload, expanded=False)


def pagina_sinais():
    st.header('Sinais (bus)')
    df = _carregar_eventos_bus()
    if df.empty:
        st.info('Sem eventos encontrados. Publique sinais a partir dos relatórios JSON.')
        return
    col_tools = st.columns([1,1,6])
    with col_tools[0]:
        if st.button('Atualizar lista'):
            try:
                _carregar_eventos_bus.clear()
            except Exception:
                pass
            df = _carregar_eventos_bus()
    with col_tools[1]:
        if st.button('Revalidar tudo'):
            qtd_ok, qtd_fail = 0, 0
            try:
                from schemas.validador import validar_contra_schema
                for arq in (BUS_DIR.glob('*.json')):
                    try:
                        j = json.loads(arq.read_text(encoding='utf-8'))
                        ev = j.get('event') or {}
                        contrato = ev.get('contractVersion') or ''
                        ok, erros = validar_contra_schema(ev, contrato)
                        j['valid'] = ok
                        j['errors'] = erros
                        arq.write_text(json.dumps(j, ensure_ascii=False, indent=2), encoding='utf-8')
                        if ok:
                            qtd_ok += 1
                        else:
                            qtd_fail += 1
                    except Exception:
                        qtd_fail += 1
                # refresh
                try:
                    _carregar_eventos_bus.clear()
                except Exception:
                    pass
                df = _carregar_eventos_bus()
                st.success(f"Revalidação concluída: PASS={qtd_ok}, FAIL={qtd_fail}")
            except Exception as e:
                st.warning(f"Falha ao revalidar: {e}")

    col1, col2, col3 = st.columns([2,2,2])
    with col1:
        contrato = st.selectbox('Contrato', options=['(todos)'] + sorted(df['contrato'].dropna().unique().tolist()))
    with col2:
        classe = st.selectbox('Classe', options=['(todas)'] + sorted(df['classe'].dropna().unique().tolist()))
    with col3:
        instrumento = st.text_input('Instrumento (contém)')
    only_invalid = st.checkbox('Mostrar apenas inválidos (FAIL)')

    df_view = df.copy()
    if contrato != '(todos)':
        df_view = df_view[df_view['contrato'] == contrato]
    if classe != '(todas)':
        df_view = df_view[df_view['classe'] == classe]
    if instrumento:
        df_view = df_view[df_view['instrumento'].fillna('').str.contains(instrumento, case=False, na=False)]
    if only_invalid:
        df_view = df_view[df_view['valid'] == False]
    # Adiciona coluna de status legível
    if not df_view.empty:
        df_view = df_view.assign(status=df_view['valid'].map(lambda v: 'PASS ✅' if bool(v) else 'FAIL ❌'))
        cols = ['arquivo','contrato','classe','instrumento','timestamp','status']
        show_cols = [c for c in cols if c in df_view.columns]
        st.dataframe(df_view[show_cols], use_container_width=True, hide_index=True)
    else:
        st.dataframe(df_view, use_container_width=True, hide_index=True)

    sel_arquivo = st.text_input('Arquivo para inspecionar (nome exato)')
    col_a, col_b = st.columns([1,1])
    with col_a:
        carregar = st.button('Carregar evento')
    with col_b:
        revalidar = st.button('Revalidar contra schema')

    if carregar or revalidar:
        caminho = BUS_DIR / sel_arquivo
        if not caminho.exists():
            st.warning('Arquivo não encontrado no bus.')
        else:
            j = json.loads(caminho.read_text(encoding='utf-8'))
            st.subheader('Evento (envelopado)')
            st.json(j, expanded=False)

            if revalidar:
                try:
                    from schemas.validador import validar_contra_schema
                    ev = j.get('event') or {}
                    contrato = ev.get('contractVersion') or ''
                    ok, erros = validar_contra_schema(ev, contrato)
                    st.success('Validação: PASS' if ok else 'Validação: FAIL')
                    if not ok and erros:
                        st.write('Erros:')
                        for e in erros[:20]:
                            st.write(f"- {e}")
                except Exception as e:
                    st.warning(f'Falha ao validar: {e}')


def main():
    st.set_page_config(page_title='Dashboard Mercado', layout='wide')
    st.sidebar.title('Navegação')
    pagina = st.sidebar.radio('Página', ['Relatórios', 'Sinais'])
    if pagina == 'Relatórios':
        pagina_relatorios()
    else:
        pagina_sinais()


if __name__ == '__main__':
    main()
