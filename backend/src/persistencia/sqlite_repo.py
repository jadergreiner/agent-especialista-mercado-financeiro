# -*- coding: utf-8 -*-
"""
Persistência em SQLite para relatórios intraday

Tabela: relatorios_intraday
- id INTEGER PRIMARY KEY
- classe_ativo TEXT
- par TEXT
- timestamp TEXT (ISO 8601)
- operacao TEXT
- vies_sessao TEXT
- rr TEXT
- payload_json TEXT

Índices: idx_relatorios_intraday_par_ts (par, timestamp)
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Dict, Any, Optional


def _caminho_db() -> Path:
    base = Path(__file__).resolve().parents[2]  # backend/
    data_dir = base / 'data'
    data_dir.mkdir(exist_ok=True)
    return data_dir / 'mercado.db'


def _conectar() -> sqlite3.Connection:
    return sqlite3.connect(str(_caminho_db()))


def inicializar() -> None:
    con = _conectar()
    try:
        cur = con.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS relatorios_intraday (
                id INTEGER PRIMARY KEY,
                classe_ativo TEXT NOT NULL,
                par TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                operacao TEXT NOT NULL,
                vies_sessao TEXT NOT NULL,
                rr TEXT NOT NULL,
                payload_json TEXT NOT NULL
            );
            """
        )
        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_relatorios_intraday_par_ts
            ON relatorios_intraday(par, timestamp);
            """
        )
        # Tabela de revalidação: registra assertividade 24h depois
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS revalidacoes (
                id INTEGER PRIMARY KEY,
                relatorio_id INTEGER NOT NULL,
                classe_ativo TEXT NOT NULL,
                par TEXT NOT NULL,
                timestamp_original TEXT NOT NULL,
                timestamp_revalidacao TEXT NOT NULL,
                operacao_original TEXT NOT NULL,
                preco_entrada_original REAL,
                preco_alvo1 REAL,
                preco_stop REAL,
                preco_24h REAL NOT NULL,
                acertou INTEGER NOT NULL,
                pontos_movimento REAL,
                pct_movimento REAL,
                objetivo_atingido TEXT,
                observacoes TEXT,
                FOREIGN KEY(relatorio_id) REFERENCES relatorios_intraday(id)
            );
            """
        )
        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_revalidacoes_relatorio_id
            ON revalidacoes(relatorio_id);
            """
        )
        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_revalidacoes_par_ts
            ON revalidacoes(par, timestamp_revalidacao);
            """
        )
        con.commit()
    finally:
        con.close()


def salvar_relatorio_intraday(payload: Dict[str, Any]) -> Optional[int]:
    """Insere um payload de relatório intraday no banco.

    Retorna o id inserido ou None se falhar.
    """
    try:
        classe = payload.get('classeAtivo', 'forex')
        par = payload.get('par') or payload.get('ativo') or '-'
        ts = payload.get('timestamp', '')
        resumo = payload.get('resumo', {})
        oper = resumo.get('operacao', '-')
        vies = resumo.get('viesSessao', '-')
        rr = resumo.get('rr', 'N/A')

        con = _conectar()
        try:
            cur = con.cursor()
            cur.execute(
                """
                INSERT INTO relatorios_intraday
                (classe_ativo, par, timestamp, operacao, vies_sessao, rr, payload_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (classe, par, ts, oper, vies, rr, json.dumps(payload, ensure_ascii=False))
            )
            con.commit()
            return int(cur.lastrowid)
        finally:
            con.close()
    except Exception:
        return None


def salvar_revalidacao(
    relatorio_id: int,
    classe_ativo: str,
    par: str,
    timestamp_original: str,
    timestamp_revalidacao: str,
    operacao_original: str,
    preco_entrada_original: float,
    preco_alvo1: float,
    preco_stop: float,
    preco_24h: float,
    acertou: bool,
    pontos_movimento: Optional[float] = None,
    pct_movimento: Optional[float] = None,
    objetivo_atingido: Optional[str] = None,
    observacoes: Optional[str] = None,
) -> Optional[int]:
    """Registra revalidação de assertividade após 24h.

    Args:
        relatorio_id: ID do relatório original
        classe_ativo: forex|cripto|acoes etc
        par: EURUSD, BTCUSDT etc
        timestamp_original: ISO 8601 da análise original
        timestamp_revalidacao: ISO 8601 da revalidação (24h depois)
        operacao_original: COMPRA|VENDA|ESPERAR
        preco_entrada_original: Preço de entrada sugerido
        preco_alvo1: Take profit 1
        preco_stop: Stop loss
        preco_24h: Preço real após 24h
        acertou: True se direção correta (COMPRA→subiu, VENDA→caiu)
        pontos_movimento: Movimento em pontos/pips
        pct_movimento: Movimento percentual
        objetivo_atingido: 'TP1', 'TP2', 'STOP', 'PARCIAL', 'NENHUM'
        observacoes: Texto livre

    Returns:
        ID do registro de revalidação ou None se falhar
    """
    try:
        con = _conectar()
        try:
            cur = con.cursor()
            cur.execute(
                """
                INSERT INTO revalidacoes (
                    relatorio_id, classe_ativo, par,
                    timestamp_original, timestamp_revalidacao,
                    operacao_original, preco_entrada_original,
                    preco_alvo1, preco_stop, preco_24h,
                    acertou, pontos_movimento, pct_movimento,
                    objetivo_atingido, observacoes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    relatorio_id, classe_ativo, par,
                    timestamp_original, timestamp_revalidacao,
                    operacao_original, preco_entrada_original,
                    preco_alvo1, preco_stop, preco_24h,
                    1 if acertou else 0,
                    pontos_movimento, pct_movimento,
                    objetivo_atingido, observacoes
                )
            )
            con.commit()
            return int(cur.lastrowid)
        finally:
            con.close()
    except Exception as e:
        print(f"Erro ao salvar revalidação: {e}")
        return None


def listar_relatorios_pendentes_revalidacao(limite_horas: int = 24) -> list[Dict[str, Any]]:
    """Lista relatórios que precisam ser revalidados.

    Critérios:
    - timestamp_original + limite_horas <= agora
    - Ainda não revalidado (sem registro em revalidacoes)

    Returns:
        Lista de dicts com dados do relatório
    """
    from datetime import datetime, timedelta, timezone

    agora = datetime.now(timezone.utc)
    limite_ts = (agora - timedelta(hours=limite_horas)).isoformat()

    con = _conectar()
    try:
        cur = con.cursor()
        cur.execute(
            """
            SELECT r.id, r.classe_ativo, r.par, r.timestamp, r.operacao, r.payload_json
            FROM relatorios_intraday r
            LEFT JOIN revalidacoes rv ON r.id = rv.relatorio_id
            WHERE r.timestamp <= ?
              AND rv.id IS NULL
            ORDER BY r.timestamp ASC
            """,
            (limite_ts,)
        )
        rows = cur.fetchall()
        resultados = []
        for row in rows:
            payload = json.loads(row[5])
            resultados.append({
                'id': row[0],
                'classe_ativo': row[1],
                'par': row[2],
                'timestamp': row[3],
                'operacao': row[4],
                'payload': payload
            })
        return resultados
    finally:
        con.close()
