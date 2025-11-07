# -*- coding: utf-8 -*-
"""
Coletor de Cotações para Análise de Correlações com WIN.

Coleta cotações de ativos correlacionados ao WIN (Mini Índice Bovespa):
- Índices (Ibovespa, S&P 500, Dow, NASDAQ)
- Moedas (Dólar)
- Commodities (Petróleo, Vale proxy)
- Volatilidade (VIX)
- Ações peso-pesado (PETR4, VALE3, ITUB4, etc.)

Fonte principal: yfinance (Yahoo Finance)
Frequência recomendada: Intraday (15min) ou Diária
"""

import sqlite3
import yfinance as yf
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
from decimal import Decimal
import pandas as pd


# Configuração de caminhos
CAMINHO_DB = Path(__file__).parent.parent.parent / "data" / "recomendacoes.sqlite"


@dataclass
class CotacaoCorrelacao:
    """Estrutura de dados para cotação de ativo correlacionado."""

    simbolo: str
    nome: str
    data_hora: datetime

    # OHLC
    abertura: Decimal
    maxima: Decimal
    minima: Decimal
    fechamento: Decimal

    # Volume e metadados
    volume: int
    variacao_dia: Optional[Decimal] = None  # % do dia
    variacao_periodo: Optional[Decimal] = None  # % desde última coleta


class ColetorCorrelacoes:
    """Coleta cotações de ativos correlacionados ao WIN."""

    # Definição de ativos a coletar
    ATIVOS_PRIORIDADE_ALTA = {
        '^BVSP': {
            'nome': 'Ibovespa',
            'categoria': 'indice_br',
            'correlacao': 0.99,
            'tipo': 'direto'
        },
        'USDBRL=X': {
            'nome': 'Dólar/Real',
            'categoria': 'moeda',
            'correlacao': -0.80,
            'tipo': 'inverso'
        },
        '^GSPC': {
            'nome': 'S&P 500',
            'categoria': 'indice_us',
            'correlacao': 0.70,
            'tipo': 'direto'
        },
        '^VIX': {
            'nome': 'VIX (Volatilidade)',
            'categoria': 'volatilidade',
            'correlacao': -0.50,
            'tipo': 'inverso'
        },
        'CL=F': {
            'nome': 'Petróleo WTI',
            'categoria': 'commodity',
            'correlacao': 0.50,
            'tipo': 'direto'
        },
        'VALE3.SA': {
            'nome': 'Vale ON',
            'categoria': 'acao_br',
            'correlacao': 0.85,
            'tipo': 'direto'
        },
        'PETR4.SA': {
            'nome': 'Petrobras PN',
            'categoria': 'acao_br',
            'correlacao': 0.80,
            'tipo': 'direto'
        }
    }

    ATIVOS_PRIORIDADE_MEDIA = {
        '^DJI': {'nome': 'Dow Jones', 'categoria': 'indice_us', 'correlacao': 0.65, 'tipo': 'direto'},
        '^IXIC': {'nome': 'NASDAQ', 'categoria': 'indice_us', 'correlacao': 0.60, 'tipo': 'direto'},
        'BZ=F': {'nome': 'Petróleo Brent', 'categoria': 'commodity', 'correlacao': 0.50, 'tipo': 'direto'},
        'ITUB4.SA': {'nome': 'Itaú PN', 'categoria': 'acao_br', 'correlacao': 0.75, 'tipo': 'direto'},
        'BBDC4.SA': {'nome': 'Bradesco PN', 'categoria': 'acao_br', 'correlacao': 0.70, 'tipo': 'direto'},
        'B3SA3.SA': {'nome': 'B3 ON', 'categoria': 'acao_br', 'correlacao': 0.75, 'tipo': 'direto'},
        'EWZ': {'nome': 'ETF Brasil (EWZ)', 'categoria': 'etf', 'correlacao': 0.90, 'tipo': 'direto'}
    }

    ATIVOS_PRIORIDADE_BAIXA = {
        'ZS=F': {'nome': 'Soja', 'categoria': 'commodity', 'correlacao': 0.40, 'tipo': 'direto'},
        'GC=F': {'nome': 'Ouro', 'categoria': 'commodity', 'correlacao': -0.30, 'tipo': 'inverso'},
        'BTC-USD': {'nome': 'Bitcoin', 'categoria': 'crypto', 'correlacao': 0.35, 'tipo': 'direto'},
        '^TNX': {'nome': '10Y Treasury', 'categoria': 'bonds', 'correlacao': -0.40, 'tipo': 'inverso'}
    }

    def __init__(self):
        """Inicializa o coletor."""
        self._criar_tabelas()

    def _criar_tabelas(self):
        """Cria tabelas necessárias no banco."""
        conn = sqlite3.connect(CAMINHO_DB)
        cur = conn.cursor()

        # Tabela de cotações de correlações
        cur.execute("""
            CREATE TABLE IF NOT EXISTS cotacoes_correlacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                simbolo TEXT NOT NULL,
                nome TEXT NOT NULL,
                categoria TEXT NOT NULL,

                data_hora TIMESTAMP NOT NULL,

                -- OHLC
                abertura REAL NOT NULL,
                maxima REAL NOT NULL,
                minima REAL NOT NULL,
                fechamento REAL NOT NULL,

                -- Volume
                volume INTEGER,

                -- Variações
                variacao_dia REAL,
                variacao_periodo REAL,

                -- Metadados
                data_coleta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                UNIQUE(simbolo, data_hora)
            )
        """)

        cur.execute("CREATE INDEX IF NOT EXISTS idx_cotacoes_corr_simbolo ON cotacoes_correlacoes(simbolo)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_cotacoes_corr_data ON cotacoes_correlacoes(data_hora)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_cotacoes_corr_categoria ON cotacoes_correlacoes(categoria)")

        # Tabela de configuração de ativos
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ativos_correlacao_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                simbolo TEXT UNIQUE NOT NULL,
                nome TEXT NOT NULL,
                categoria TEXT NOT NULL,
                correlacao_esperada REAL,
                tipo_correlacao TEXT,
                prioridade TEXT,
                ativo BOOLEAN DEFAULT 1,

                ultima_coleta TIMESTAMP,
                total_coletas INTEGER DEFAULT 0
            )
        """)

        # Tabela de matriz de correlação (calculada)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS matriz_correlacao (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                simbolo1 TEXT NOT NULL,
                simbolo2 TEXT NOT NULL,

                periodo_dias INTEGER NOT NULL,
                correlacao REAL NOT NULL,

                data_calculo TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cur.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_matriz_unico
            ON matriz_correlacao(simbolo1, simbolo2, periodo_dias, date(data_calculo))
        """)

        conn.commit()
        conn.close()
        print(f"✅ Tabelas de correlações criadas/verificadas em: {CAMINHO_DB}")

    def inicializar_ativos(self, incluir_prioridade_baixa: bool = False):
        """
        Inicializa configuração de ativos no banco.

        Args:
            incluir_prioridade_baixa: Se True, inclui também ativos de prioridade baixa
        """
        conn = sqlite3.connect(CAMINHO_DB)
        cur = conn.cursor()

        # Combinar ativos conforme prioridade
        ativos = {**self.ATIVOS_PRIORIDADE_ALTA, **self.ATIVOS_PRIORIDADE_MEDIA}

        if incluir_prioridade_baixa:
            ativos = {**ativos, **self.ATIVOS_PRIORIDADE_BAIXA}

        for simbolo, info in ativos.items():
            # Determinar prioridade
            if simbolo in self.ATIVOS_PRIORIDADE_ALTA:
                prioridade = 'alta'
            elif simbolo in self.ATIVOS_PRIORIDADE_MEDIA:
                prioridade = 'media'
            else:
                prioridade = 'baixa'

            try:
                cur.execute("""
                    INSERT INTO ativos_correlacao_config
                    (simbolo, nome, categoria, correlacao_esperada, tipo_correlacao, prioridade)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    simbolo,
                    info['nome'],
                    info['categoria'],
                    info['correlacao'],
                    info['tipo'],
                    prioridade
                ))
            except sqlite3.IntegrityError:
                # Já existe, apenas atualizar informações
                cur.execute("""
                    UPDATE ativos_correlacao_config
                    SET nome = ?, categoria = ?, correlacao_esperada = ?,
                        tipo_correlacao = ?, prioridade = ?
                    WHERE simbolo = ?
                """, (
                    info['nome'],
                    info['categoria'],
                    info['correlacao'],
                    info['tipo'],
                    prioridade,
                    simbolo
                ))

        conn.commit()
        conn.close()

        print(f"\n✅ Configuração de {len(ativos)} ativos inicializada/atualizada")

    def coletar_cotacao(self, simbolo: str, periodo: str = '1d', intervalo: str = '1m') -> List[CotacaoCorrelacao]:
        """
        Coleta cotações de um ativo via yfinance.

        Args:
            simbolo: Símbolo do Yahoo Finance (ex: ^BVSP, USDBRL=X)
            periodo: Período de histórico ('1d', '5d', '1mo', etc.)
            intervalo: Intervalo dos dados ('1m', '5m', '15m', '1h', '1d')

        Returns:
            Lista de cotações coletadas
        """
        try:
            # Buscar info do ativo
            conn = sqlite3.connect(CAMINHO_DB)
            cur = conn.cursor()

            cur.execute("""
                SELECT nome, categoria FROM ativos_correlacao_config
                WHERE simbolo = ?
            """, (simbolo,))

            resultado = cur.fetchone()
            if resultado:
                nome, categoria = resultado
            else:
                nome = simbolo
                categoria = 'desconhecido'

            conn.close()

            # Coletar via yfinance
            ticker = yf.Ticker(simbolo)
            df = ticker.history(period=periodo, interval=intervalo)

            if df.empty:
                print(f"⚠️  {simbolo}: Nenhum dado retornado")
                return []

            cotacoes = []

            for timestamp, row in df.iterrows():
                # Calcular variação do dia
                variacao_dia = None
                if row['Open'] > 0:
                    variacao_dia = ((row['Close'] - row['Open']) / row['Open']) * 100

                cotacao = CotacaoCorrelacao(
                    simbolo=simbolo,
                    nome=nome,
                    data_hora=timestamp.to_pydatetime(),
                    abertura=Decimal(str(row['Open'])),
                    maxima=Decimal(str(row['High'])),
                    minima=Decimal(str(row['Low'])),
                    fechamento=Decimal(str(row['Close'])),
                    volume=int(row['Volume']) if row['Volume'] > 0 else 0,
                    variacao_dia=Decimal(str(variacao_dia)) if variacao_dia else None
                )

                cotacoes.append(cotacao)

            return cotacoes

        except Exception as e:
            print(f"❌ Erro ao coletar {simbolo}: {str(e)}")
            return []

    def salvar_cotacoes(self, cotacoes: List[CotacaoCorrelacao]) -> int:
        """
        Salva cotações no banco.

        Args:
            cotacoes: Lista de cotações a salvar

        Returns:
            Número de cotações salvas
        """
        if not cotacoes:
            return 0

        conn = sqlite3.connect(CAMINHO_DB)
        cur = conn.cursor()

        salvos = 0
        duplicados = 0

        for cotacao in cotacoes:
            try:
                # Buscar categoria
                cur.execute("""
                    SELECT categoria FROM ativos_correlacao_config
                    WHERE simbolo = ?
                """, (cotacao.simbolo,))

                resultado = cur.fetchone()
                categoria = resultado[0] if resultado else 'desconhecido'

                cur.execute("""
                    INSERT INTO cotacoes_correlacoes (
                        simbolo, nome, categoria, data_hora,
                        abertura, maxima, minima, fechamento, volume,
                        variacao_dia
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    cotacao.simbolo,
                    cotacao.nome,
                    categoria,
                    cotacao.data_hora.isoformat(),
                    float(cotacao.abertura),
                    float(cotacao.maxima),
                    float(cotacao.minima),
                    float(cotacao.fechamento),
                    cotacao.volume,
                    float(cotacao.variacao_dia) if cotacao.variacao_dia else None
                ))

                salvos += 1

            except sqlite3.IntegrityError:
                duplicados += 1

        # Atualizar contadores de coleta
        if salvos > 0:
            simbolo_ref = cotacoes[0].simbolo
            cur.execute("""
                UPDATE ativos_correlacao_config
                SET ultima_coleta = CURRENT_TIMESTAMP,
                    total_coletas = total_coletas + ?
                WHERE simbolo = ?
            """, (salvos, simbolo_ref))

        conn.commit()
        conn.close()

        return salvos

    def coletar_todos_ativos(self, prioridade: str = 'alta', periodo: str = '1d', intervalo: str = '1m'):
        """
        Coleta cotações de todos os ativos configurados.

        Args:
            prioridade: 'alta', 'media', 'baixa', ou 'todas'
            periodo: Período de histórico
            intervalo: Intervalo dos dados
        """
        conn = sqlite3.connect(CAMINHO_DB)
        cur = conn.cursor()

        # Buscar ativos a coletar
        if prioridade == 'todas':
            cur.execute("""
                SELECT simbolo, nome FROM ativos_correlacao_config
                WHERE ativo = 1
                ORDER BY
                    CASE prioridade
                        WHEN 'alta' THEN 1
                        WHEN 'media' THEN 2
                        WHEN 'baixa' THEN 3
                    END
            """)
        else:
            cur.execute("""
                SELECT simbolo, nome FROM ativos_correlacao_config
                WHERE ativo = 1 AND prioridade = ?
                ORDER BY simbolo
            """, (prioridade,))

        ativos = cur.fetchall()
        conn.close()

        if not ativos:
            print(f"⚠️  Nenhum ativo encontrado para prioridade '{prioridade}'")
            print("   Execute: inicializar_ativos() primeiro")
            return

        print(f"\n{'='*80}")
        print(f"COLETANDO COTAÇÕES - Prioridade: {prioridade.upper()}")
        print(f"{'='*80}\n")

        total_salvos = 0

        for simbolo, nome in ativos:
            print(f"📊 {nome} ({simbolo})... ", end='', flush=True)

            cotacoes = self.coletar_cotacao(simbolo, periodo=periodo, intervalo=intervalo)
            salvos = self.salvar_cotacoes(cotacoes)

            total_salvos += salvos

            if salvos > 0:
                ultima = cotacoes[-1]
                variacao = f"{ultima.variacao_dia:+.2f}%" if ultima.variacao_dia else "N/A"
                print(f"{salvos} candles | Último: {ultima.fechamento:.2f} ({variacao})")
            else:
                print("sem dados")

        print(f"\n{'='*80}")
        print(f"RESUMO: {total_salvos} cotações salvas de {len(ativos)} ativos")
        print(f"{'='*80}\n")


def exemplo_uso():
    """Exemplo de uso do coletor de correlações."""

    coletor = ColetorCorrelacoes()

    # 1. Inicializar ativos (primeira vez)
    print("="*80)
    print("INICIALIZANDO CONFIGURAÇÃO DE ATIVOS")
    print("="*80)
    coletor.inicializar_ativos(incluir_prioridade_baixa=False)

    # 2. Coletar ativos de prioridade alta (últimas 24h, candles de 1h)
    coletor.coletar_todos_ativos(prioridade='alta', periodo='1d', intervalo='1h')

    # 3. Consultar última cotação
    conn = sqlite3.connect(CAMINHO_DB)
    cur = conn.cursor()

    cur.execute("""
        SELECT simbolo, nome, fechamento, variacao_dia, data_hora
        FROM cotacoes_correlacoes
        WHERE data_hora = (
            SELECT MAX(data_hora) FROM cotacoes_correlacoes c2
            WHERE c2.simbolo = cotacoes_correlacoes.simbolo
        )
        ORDER BY simbolo
    """)

    print(f"\n{'='*80}")
    print("ÚLTIMAS COTAÇÕES COLETADAS")
    print(f"{'='*80}\n")

    for row in cur.fetchall():
        simbolo, nome, fechamento, variacao, data_hora = row
        variacao_str = f"{variacao:+.2f}%" if variacao else "N/A"
        print(f"{nome:20} ({simbolo:12}): {fechamento:10.2f}  {variacao_str:>8}  {data_hora}")

    conn.close()


if __name__ == "__main__":
    exemplo_uso()
