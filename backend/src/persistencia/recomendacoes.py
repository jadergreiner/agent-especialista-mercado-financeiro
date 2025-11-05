"""
Persistência de recomendações e resultados para treinamento do agente.
Usa SQLite (sqlite3) para armazenamento local sem dependências externas.

Todas as mensagens, docstrings e nomes seguem o padrão em Português.
"""
from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from collections import defaultdict

# Caminho padrão do banco de dados (em backend/data/recomendacoes.sqlite)
PASTA_DADOS_PADRAO = Path(__file__).resolve().parents[2] / "data"
BD_PADRAO = PASTA_DADOS_PADRAO / "recomendacoes.sqlite"


@dataclass
class Recomendacao:
    """Registro de recomendação emitida pelo agente"""
    timestamp: str
    instrumento: str
    direcao: str
    preco_entrada: float
    contratos_inicio: int
    stop_loss: float
    tp1: float
    tp2: float
    tp3: float
    reforcos_json: str  # JSON com lista de reforços
    saldo_macro: int
    confianca: int
    valido_ate: str
    variacao_dia: str
    tendencia: str
    melhor_spread: str
    atr_valor: float
    relatorio_json: str  # Snapshot completo (compactado)


@dataclass
class Resultado:
    """Resultado verificado para uma recomendação"""
    id_recomendacao: int
    timestamp_validacao: str
    status: str  # 'executada', 'cancelada', 'expirada'
    acertou: Optional[bool]  # True (TP), False (STOP), None (n/a)
    preco_saida: Optional[float]
    pnl_pontos: Optional[float]
    pnl_reais: Optional[float]
    motivo_saida: Optional[str]  # 'tp1|tp2|tp3|stop|tempo|manual'
    observacoes: Optional[str]


def _conectar(caminho_bd: Optional[Path] = None) -> sqlite3.Connection:
    caminho = (caminho_bd or BD_PADRAO)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(caminho))
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn


def inicializar_banco(caminho_bd: Optional[Path] = None) -> None:
    """Cria tabelas e índices se não existirem, e aplica migrações necessárias"""
    conn = _conectar(caminho_bd)
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS recomendacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                instrumento TEXT NOT NULL,
                direcao TEXT NOT NULL,
                preco_entrada REAL NOT NULL,
                contratos_inicio INTEGER NOT NULL,
                stop_loss REAL,
                tp1 REAL,
                tp2 REAL,
                tp3 REAL,
                reforcos_json TEXT,
                saldo_macro INTEGER,
                confianca INTEGER,
                valido_ate TEXT,
                variacao_dia TEXT,
                tendencia TEXT,
                melhor_spread TEXT,
                atr_valor REAL,
                relatorio_json TEXT
            );

            CREATE TABLE IF NOT EXISTS resultados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_recomendacao INTEGER NOT NULL,
                timestamp_validacao TEXT NOT NULL,
                status TEXT NOT NULL,
                acertou INTEGER,
                preco_saida REAL,
                pnl_pontos REAL,
                pnl_reais REAL,
                motivo_saida TEXT,
                observacoes TEXT,
                FOREIGN KEY(id_recomendacao) REFERENCES recomendacoes(id)
            );

            CREATE INDEX IF NOT EXISTS idx_recom_timestamp ON recomendacoes(timestamp);
            CREATE INDEX IF NOT EXISTS idx_recom_instr ON recomendacoes(instrumento);
            CREATE INDEX IF NOT EXISTS idx_res_recom ON resultados(id_recomendacao);

            -- Tabela opcional para importação de preços diários (dados manuais)
            CREATE TABLE IF NOT EXISTS precos_diarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT NOT NULL,                -- ISO date YYYY-MM-DD (UTC)
                instrumento TEXT NOT NULL,         -- Ex: 'WIN' ou 'IBOV-FUT'
                ultimo REAL NOT NULL,
                abertura REAL NOT NULL,
                maxima REAL NOT NULL,
                minima REAL NOT NULL,
                volume INTEGER,                    -- número de contratos/negócios
                variacao_pct REAL,                 -- variação em fração (ex: 0.0003 = 0,03%)
                fonte TEXT,                        -- origem do arquivo (ex: 'investing.com')
                arquivo TEXT,                      -- nome do arquivo importado
                inserido_em TEXT NOT NULL          -- timestamp UTC de inserção
            );
            CREATE UNIQUE INDEX IF NOT EXISTS idx_precos_diarios_uniq ON precos_diarios(data, instrumento, ifnull(fonte, ''));
            """
        )
        
        # Migração: adicionar coluna atr_valor se não existir
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(recomendacoes)")
        colunas = [row[1] for row in cur.fetchall()]
        if 'atr_valor' not in colunas:
            conn.execute("ALTER TABLE recomendacoes ADD COLUMN atr_valor REAL DEFAULT 0.0")
            conn.commit()
        
        conn.commit()
    finally:
        conn.close()


def salvar_recomendacao(dados: Dict[str, Any], caminho_bd: Optional[Path] = None) -> int:
    """
    Salva recomendação emitida pelo analisador e retorna o id gerado.
    Espera dicionário retornado por AnalisadorWinDayTrading.analisar().
    """
    conn = _conectar(caminho_bd)
    try:
        rec = _converter_para_recomendacao(dados)
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO recomendacoes (
                timestamp, instrumento, direcao, preco_entrada, contratos_inicio,
                stop_loss, tp1, tp2, tp3, reforcos_json, saldo_macro, confianca,
                valido_ate, variacao_dia, tendencia, melhor_spread, atr_valor, relatorio_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                rec.timestamp,
                rec.instrumento,
                rec.direcao,
                rec.preco_entrada,
                rec.contratos_inicio,
                rec.stop_loss,
                rec.tp1,
                rec.tp2,
                rec.tp3,
                rec.reforcos_json,
                rec.saldo_macro,
                rec.confianca,
                rec.valido_ate,
                rec.variacao_dia,
                rec.tendencia,
                rec.melhor_spread,
                rec.atr_valor,
                rec.relatorio_json,
            ),
        )
        conn.commit()
        return int(cur.lastrowid)
    finally:
        conn.close()


def listar_pendentes(caminho_bd: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Lista recomendações sem resultado registrado"""
    conn = _conectar(caminho_bd)
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT r.id, r.timestamp, r.instrumento, r.direcao, r.preco_entrada,
                   r.stop_loss, r.tp1, r.tp2, r.tp3, r.confianca, r.saldo_macro,
                   r.valido_ate
            FROM recomendacoes r
            LEFT JOIN resultados x ON x.id_recomendacao = r.id
            WHERE x.id_recomendacao IS NULL
            ORDER BY r.timestamp DESC
            LIMIT 100;
            """
        )
        colunas = [d[0] for d in cur.description]
        return [dict(zip(colunas, linha)) for linha in cur.fetchall()]
    finally:
        conn.close()


def registrar_resultado(
    id_recomendacao: int,
    status: str,
    acertou: Optional[bool] = None,
    preco_saida: Optional[float] = None,
    pnl_pontos: Optional[float] = None,
    pnl_reais: Optional[float] = None,
    motivo_saida: Optional[str] = None,
    observacoes: Optional[str] = None,
    caminho_bd: Optional[Path] = None,
) -> None:
    """Registra o resultado de uma recomendação (manual ou automatizado)"""
    conn = _conectar(caminho_bd)
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO resultados (
                id_recomendacao, timestamp_validacao, status, acertou, preco_saida,
                pnl_pontos, pnl_reais, motivo_saida, observacoes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                id_recomendacao,
                datetime.utcnow().isoformat(),
                status,
                (1 if acertou is True else (0 if acertou is False else None)),
                preco_saida,
                pnl_pontos,
                pnl_reais,
                motivo_saida,
                observacoes,
            ),
        )
        conn.commit()
    finally:
        conn.close()


def calcular_metricas_basicas(
    dias: int = 30, caminho_bd: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Calcula métricas simples das recomendações validadas nos últimos N dias.
    """
    conn = _conectar(caminho_bd)
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT x.status, x.acertou, x.pnl_reais
            FROM resultados x
            WHERE x.timestamp_validacao >= datetime('now', ?)
            """,
            (f'-{dias} days',),
        )
        linhas = cur.fetchall()
        total = len(linhas)
        executadas = [l for l in linhas if l[0] == 'executada']
        canceladas = [l for l in linhas if l[0] != 'executada']
        acertos = [l for l in executadas if l[1] == 1]
        erros = [l for l in executadas if l[1] == 0]

        soma_pnl = sum((l[2] or 0.0) for l in executadas)
        pnl_pos = sum((l[2] or 0.0) for l in executadas if (l[2] or 0.0) > 0)
        pnl_neg = -sum((l[2] or 0.0) for l in executadas if (l[2] or 0.0) < 0)
        profit_factor = (pnl_pos / pnl_neg) if pnl_neg > 0 else None

        return {
            'periodo_dias': dias,
            'total_resultados': total,
            'executadas': len(executadas),
            'canceladas_ou_expiradas': len(canceladas),
            'acertos': len(acertos),
            'erros': len(erros),
            'acuracia': (len(acertos) / len(executadas)) if executadas else None,
            'pnl_total_reais': soma_pnl,
            'profit_factor': profit_factor,
        }
    finally:
        conn.close()


def calcular_metricas_detalhadas(
    dias: int = 30, caminho_bd: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Métricas detalhadas por categoria: tendência, saldo macro e horário (sessões).
    Considera todas as recomendações com resultado nos últimos N dias.
    """
    conn = _conectar(caminho_bd)
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT r.tendencia, r.saldo_macro, r.timestamp, r.instrumento, r.direcao,
                   r.melhor_spread, r.atr_valor,
                   x.status, x.acertou, x.pnl_reais
            FROM recomendacoes r
            JOIN resultados x ON x.id_recomendacao = r.id
            WHERE x.timestamp_validacao >= datetime('now', ?)
            """,
            (f'-{dias} days',),
        )
        linhas = cur.fetchall()
        # Índices: 0=tendencia,1=saldo_macro,2=timestamp,3=instrumento,4=direcao,
        #          5=melhor_spread,6=atr_valor,7=status,8=acertou,9=pnl_reais
        def add_metric(bucket: Dict[str, Dict[str, Any]], chave: str, status: str, acertou: Optional[int], pnl: Optional[float]):
            m = bucket.setdefault(chave, {
                'sinais': 0,
                'executadas': 0,
                'canceladas_ou_expiradas': 0,
                'acertos': 0,
                'erros': 0,
                'pnl_total_reais': 0.0,
                'profit_factor': None,
                '_pnl_pos': 0.0,
                '_pnl_neg': 0.0,
            })
            m['sinais'] += 1
            if status == 'executada':
                m['executadas'] += 1
                if acertou == 1:
                    m['acertos'] += 1
                elif acertou == 0:
                    m['erros'] += 1
                valor = (pnl or 0.0)
                m['pnl_total_reais'] += valor
                if valor > 0:
                    m['_pnl_pos'] += valor
                elif valor < 0:
                    m['_pnl_neg'] += -valor
            else:
                m['canceladas_ou_expiradas'] += 1

        def cat_saldo(v: int) -> str:
            if v <= -3:
                return '≤ -3'
            if -2 <= v <= -1:
                return '-2 a -1'
            if 0 <= v <= 1:
                return '0 a +1'
            if 2 <= v <= 3:
                return '+2 a +3'
            return '≥ +4'

        def cat_horario(ts: str) -> str:
            # Usa hora local do timestamp registrado
            try:
                dt = datetime.fromisoformat(ts)
            except Exception:
                return 'Indefinido'
            h = dt.hour
            if 10 <= h <= 10:
                return 'Abertura (10h)'
            if 11 <= h <= 12:
                return 'Manhã (11-12h)'
            if 13 <= h <= 14:
                return 'Meio (13-14h)'
            if 15 <= h <= 16:
                return 'Tarde (15-16h)'
            if 17 <= h <= 23:
                return 'Fechamento/After (≥17h)'
            return 'Pré-abertura (<10h)'

        def cat_volatilidade(atr: float) -> str:
            """Categoriza volatilidade baseado no ATR"""
            if atr < 1000:
                return 'Baixa (<1000)'
            if atr <= 1200:
                return 'Média (1000-1200)'
            return 'Alta (>1200)'

        buckets_tend = {}
        buckets_saldo = {}
        buckets_hora = {}
        buckets_spread = {}
        buckets_direcao = {}
        buckets_volatilidade = {}

        for linha in linhas:
            tnd, saldo, ts, _instr, dir_trade, spread, atr, st, ac, pnl = linha
            add_metric(buckets_tend, (tnd or 'Indefinido').upper(), st, ac, pnl)
            add_metric(buckets_saldo, cat_saldo(int(saldo or 0)), st, ac, pnl)
            add_metric(buckets_hora, cat_horario(ts or ''), st, ac, pnl)
            add_metric(buckets_spread, (spread or 'Indefinido').upper(), st, ac, pnl)
            add_metric(buckets_direcao, (dir_trade or 'Indefinido').upper(), st, ac, pnl)
            add_metric(buckets_volatilidade, cat_volatilidade(float(atr or 0)), st, ac, pnl)

        def finalize(bucket: Dict[str, Dict[str, Any]]):
            for k, m in bucket.items():
                if m['executadas']:
                    m['acuracia'] = m['acertos'] / m['executadas']
                else:
                    m['acuracia'] = None
                if m['_pnl_neg'] > 0:
                    m['profit_factor'] = m['_pnl_pos'] / m['_pnl_neg']
                else:
                    m['profit_factor'] = None
                # remover internos
                m.pop('_pnl_pos', None)
                m.pop('_pnl_neg', None)

        finalize(buckets_tend)
        finalize(buckets_saldo)
        finalize(buckets_hora)
        finalize(buckets_spread)
        finalize(buckets_direcao)
        finalize(buckets_volatilidade)

        return {
            'periodo_dias': dias,
            'por_tendencia': buckets_tend,
            'por_saldo_macro': buckets_saldo,
            'por_horario': buckets_hora,
            'por_spread': buckets_spread,
            'por_direcao': buckets_direcao,
            'por_volatilidade': buckets_volatilidade,
        }
    finally:
        conn.close()


def _converter_para_recomendacao(dados: Dict[str, Any]) -> Recomendacao:
    """Converte saída do analisador em objeto Recomendacao"""
    # Campos do resultado
    rel = dados['relatorio_executivo']
    plano = dados['plano_trading']

    # Direção
    direcao = plano.get('direcao', 'AGUARDAR')

    # Preços
    preco_entrada = plano['entrada_inicial']['preco'] if direcao != 'AGUARDAR' else 0.0
    stop = plano['gestao_saida']['stop_loss']['preco'] if direcao != 'AGUARDAR' else 0.0

    tps = plano['gestao_saida']['take_profit'] if direcao != 'AGUARDAR' else []
    tp1 = tps[0]['preco'] if len(tps) > 0 else 0.0
    tp2 = tps[1]['preco'] if len(tps) > 1 else 0.0
    tp3 = tps[2]['preco'] if len(tps) > 2 else 0.0

    reforcos = plano['reforcos'] if direcao != 'AGUARDAR' else []

    saldo_macro_str = rel['sintese']['saldo_macro']  # "+6 - FORTEMENTE FAVORÁVEL 🟢"
    # Extrair saldo numérico
    try:
        saldo_macro_num = int(saldo_macro_str.split(' ')[0])
    except Exception:
        saldo_macro_num = 0

    # Extrair ATR da análise técnica
    try:
        atr_valor = float(dados['analise_tecnica']['indicadores']['atr']['valor'])
    except (KeyError, TypeError, ValueError):
        atr_valor = 0.0

    rec = Recomendacao(
        timestamp= dados.get('timestamp', datetime.utcnow().isoformat()),
        instrumento= 'WIN',
        direcao= direcao,
        preco_entrada= float(preco_entrada),
        contratos_inicio= int(plano.get('entrada_inicial',{}).get('contratos', 0)) if direcao != 'AGUARDAR' else 0,
        stop_loss= float(stop),
        tp1= float(tp1),
        tp2= float(tp2),
        tp3= float(tp3),
        reforcos_json= json.dumps(reforcos, ensure_ascii=False),
        saldo_macro= int(saldo_macro_num),
        confianca= int(plano.get('confianca', 0)) if direcao != 'AGUARDAR' else 0,
        valido_ate= plano.get('valido_ate', ''),
        variacao_dia= rel.get('variacao_dia', ''),
        tendencia= rel['sintese'].get('tendencia', ''),
        melhor_spread= rel['sintese'].get('melhor_spread', ''),
        atr_valor= atr_valor,
        relatorio_json= json.dumps(dados, ensure_ascii=False),
    )
    return rec
