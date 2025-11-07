# -*- coding: utf-8 -*-
"""
Módulo para processamento de Boletins Diários da B3.

Este módulo gerencia a coleta, parsing e armazenamento de dados dos boletins
diários da B3, incluindo:
- Ajuste diário de contratos futuros (WIN, WDO, etc.)
- Volume negociado e número de negócios
- Posições em aberto (Open Interest)
- Preços de abertura, máxima, mínima e fechamento
- Spread bid/ask e profundidade de mercado
- Participação por tipo de investidor (quando disponível)
"""

import os
import sqlite3
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from decimal import Decimal


# Caminho base para armazenamento de boletins
DIRETORIO_BASE = Path(__file__).parent.parent.parent / "data" / "boletins_b3"
DIRETORIO_RAW = DIRETORIO_BASE / "raw"
DIRETORIO_PROCESSED = DIRETORIO_BASE / "processed"
CAMINHO_DB = Path(__file__).parent.parent.parent / "data" / "recomendacoes.sqlite"


@dataclass
class DadosBoletimDiario:
    """Estrutura de dados para informações do boletim diário."""

    data_pregao: date
    simbolo: str  # WIN, WDO, DOL, IND, etc.
    vencimento: date

    # Preços
    abertura: Decimal
    maxima: Decimal
    minima: Decimal
    fechamento: Decimal
    ajuste_diario: Decimal
    variacao_pontos: Decimal
    variacao_percentual: Decimal

    # Volume e liquidez
    volume_contratos: int
    volume_financeiro: Decimal
    numero_negocios: int
    contratos_abertos: int  # Open Interest

    # Microestrutura (quando disponível)
    spread_bid_ask: Optional[Decimal] = None
    melhor_bid: Optional[Decimal] = None
    melhor_ask: Optional[Decimal] = None
    profundidade_bid: Optional[int] = None
    profundidade_ask: Optional[int] = None

    # Participação (quando disponível - similar ao COT)
    posicao_pessoa_fisica: Optional[int] = None
    posicao_investidor_institucional: Optional[int] = None
    posicao_investidor_estrangeiro: Optional[int] = None
    posicao_investidor_nao_residente: Optional[int] = None


class GerenciadorBoletimB3:
    """Gerencia coleta, parsing e armazenamento de boletins B3."""

    def __init__(self, caminho_db: Optional[Path] = None):
        """
        Inicializa o gerenciador.

        Args:
            caminho_db: Caminho para o banco SQLite. Se None, usa o padrão.
        """
        self.caminho_db = caminho_db or CAMINHO_DB
        self._garantir_estrutura_diretorios()
        self._criar_tabelas()

    def _garantir_estrutura_diretorios(self):
        """Garante que os diretórios necessários existem."""
        DIRETORIO_RAW.mkdir(parents=True, exist_ok=True)
        DIRETORIO_PROCESSED.mkdir(parents=True, exist_ok=True)

    def _criar_tabelas(self):
        """Cria tabelas necessárias no banco de dados."""
        conn = sqlite3.connect(self.caminho_db)
        cur = conn.cursor()

        # Tabela principal de boletins diários
        cur.execute("""
            CREATE TABLE IF NOT EXISTS boletins_diarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_pregao DATE NOT NULL,
                simbolo TEXT NOT NULL,
                vencimento DATE NOT NULL,

                -- Preços
                abertura REAL NOT NULL,
                maxima REAL NOT NULL,
                minima REAL NOT NULL,
                fechamento REAL NOT NULL,
                ajuste_diario REAL NOT NULL,
                variacao_pontos REAL NOT NULL,
                variacao_percentual REAL NOT NULL,

                -- Volume e liquidez
                volume_contratos INTEGER NOT NULL,
                volume_financeiro REAL NOT NULL,
                numero_negocios INTEGER NOT NULL,
                contratos_abertos INTEGER NOT NULL,

                -- Microestrutura
                spread_bid_ask REAL,
                melhor_bid REAL,
                melhor_ask REAL,
                profundidade_bid INTEGER,
                profundidade_ask INTEGER,

                -- Participação por tipo de investidor
                posicao_pessoa_fisica INTEGER,
                posicao_investidor_institucional INTEGER,
                posicao_investidor_estrangeiro INTEGER,
                posicao_investidor_nao_residente INTEGER,

                -- Metadados
                data_importacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                arquivo_origem TEXT,

                -- Índice único para evitar duplicatas
                UNIQUE(data_pregao, simbolo, vencimento)
            )
        """)

        # Índices para consultas rápidas
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_boletins_data_simbolo
            ON boletins_diarios(data_pregao, simbolo)
        """)

        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_boletins_simbolo_vencimento
            ON boletins_diarios(simbolo, vencimento)
        """)

        # Tabela de métricas derivadas (calculadas a partir dos boletins)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS metricas_microestrutura (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_pregao DATE NOT NULL,
                simbolo TEXT NOT NULL,

                -- Métricas de liquidez
                volume_relativo REAL,  -- volume hoje / média 20 dias
                liquidez_score REAL,   -- combinação volume + spread + depth

                -- Métricas de sentiment
                sentiment_cot REAL,    -- posições long - short (normalizado)
                fluxo_estrangeiro REAL,  -- variação posição estrangeiro

                -- Métricas de rollover
                dias_ate_vencimento INTEGER,
                percentual_volume_proximo_vencimento REAL,
                risco_rollover REAL,  -- indica proximidade de necessidade de rolar

                -- Timestamp
                data_calculo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                UNIQUE(data_pregao, simbolo)
            )
        """)

        conn.commit()
        conn.close()
        print(f"✅ Tabelas de boletins criadas/verificadas em: {self.caminho_db}")

    def salvar_boletim(self, dados: DadosBoletimDiario, arquivo_origem: str = None) -> bool:
        """
        Salva dados de boletim no banco.

        Args:
            dados: Estrutura com dados do boletim
            arquivo_origem: Nome do arquivo de origem (opcional)

        Returns:
            True se salvou com sucesso, False se já existia
        """
        conn = sqlite3.connect(self.caminho_db)
        cur = conn.cursor()

        try:
            cur.execute("""
                INSERT INTO boletins_diarios (
                    data_pregao, simbolo, vencimento,
                    abertura, maxima, minima, fechamento,
                    ajuste_diario, variacao_pontos, variacao_percentual,
                    volume_contratos, volume_financeiro, numero_negocios, contratos_abertos,
                    spread_bid_ask, melhor_bid, melhor_ask, profundidade_bid, profundidade_ask,
                    posicao_pessoa_fisica, posicao_investidor_institucional,
                    posicao_investidor_estrangeiro, posicao_investidor_nao_residente,
                    arquivo_origem
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                dados.data_pregao.isoformat(),
                dados.simbolo,
                dados.vencimento.isoformat(),
                float(dados.abertura),
                float(dados.maxima),
                float(dados.minima),
                float(dados.fechamento),
                float(dados.ajuste_diario),
                float(dados.variacao_pontos),
                float(dados.variacao_percentual),
                dados.volume_contratos,
                float(dados.volume_financeiro),
                dados.numero_negocios,
                dados.contratos_abertos,
                float(dados.spread_bid_ask) if dados.spread_bid_ask else None,
                float(dados.melhor_bid) if dados.melhor_bid else None,
                float(dados.melhor_ask) if dados.melhor_ask else None,
                dados.profundidade_bid,
                dados.profundidade_ask,
                dados.posicao_pessoa_fisica,
                dados.posicao_investidor_institucional,
                dados.posicao_investidor_estrangeiro,
                dados.posicao_investidor_nao_residente,
                arquivo_origem
            ))
            conn.commit()
            print(f"✅ Boletim salvo: {dados.simbolo} {dados.data_pregao}")
            return True

        except sqlite3.IntegrityError:
            print(f"ℹ️  Boletim já existe: {dados.simbolo} {dados.data_pregao}")
            return False

        finally:
            conn.close()

    def obter_boletins(
        self,
        simbolo: str,
        data_inicio: date,
        data_fim: date
    ) -> List[Dict]:
        """
        Obtém boletins de um período.

        Args:
            simbolo: Símbolo do ativo (WIN, WDO, etc.)
            data_inicio: Data inicial
            data_fim: Data final

        Returns:
            Lista de dicionários com dados dos boletins
        """
        conn = sqlite3.connect(self.caminho_db)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute("""
            SELECT * FROM boletins_diarios
            WHERE simbolo = ? AND data_pregao BETWEEN ? AND ?
            ORDER BY data_pregao
        """, (simbolo, data_inicio.isoformat(), data_fim.isoformat()))

        resultados = [dict(row) for row in cur.fetchall()]
        conn.close()

        return resultados

    def calcular_metricas_microestrutura(self, simbolo: str, data_pregao: date) -> Dict:
        """
        Calcula métricas derivadas de microestrutura de mercado.

        Args:
            simbolo: Símbolo do ativo
            data_pregao: Data do pregão

        Returns:
            Dicionário com métricas calculadas
        """
        conn = sqlite3.connect(self.caminho_db)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        # Volume relativo (hoje vs média 20 dias)
        cur.execute("""
            WITH dados_hoje AS (
                SELECT volume_contratos
                FROM boletins_diarios
                WHERE simbolo = ? AND data_pregao = ?
            ),
            media_20d AS (
                SELECT AVG(volume_contratos) as media_vol
                FROM boletins_diarios
                WHERE simbolo = ?
                  AND data_pregao < ?
                  AND data_pregao >= date(?, '-20 days')
            )
            SELECT
                dados_hoje.volume_contratos * 1.0 / NULLIF(media_20d.media_vol, 0) as volume_relativo
            FROM dados_hoje, media_20d
        """, (simbolo, data_pregao.isoformat(), simbolo,
              data_pregao.isoformat(), data_pregao.isoformat()))

        resultado = cur.fetchone()
        volume_relativo = resultado['volume_relativo'] if resultado else None

        # TODO: Implementar demais métricas (sentiment COT, risco rollover, etc.)

        metricas = {
            'volume_relativo': volume_relativo,
            'liquidez_score': None,  # A implementar
            'sentiment_cot': None,   # A implementar
            'fluxo_estrangeiro': None,  # A implementar
            'risco_rollover': None   # A implementar
        }

        conn.close()
        return metricas

    def importar_arquivo_boletim(self, caminho_arquivo: Path) -> int:
        """
        Importa dados de um arquivo de boletim.

        Args:
            caminho_arquivo: Caminho para o arquivo (TXT, CSV ou PDF)

        Returns:
            Número de registros importados
        """
        # TODO: Implementar parsing específico por formato
        # Formatos suportados:
        # - Arquivo texto posicional da B3 (formato padrão de séries históricas)
        # - CSV exportado do site da B3
        # - PDF do boletim diário (com extração via pdfplumber/tabula)

        raise NotImplementedError(
            "Parser de arquivos será implementado com base no formato específico usado. "
            "Forneça um exemplo de arquivo para desenvolvimento do parser adequado."
        )

    def obter_caminho_boletim(self, data_pregao: date, tipo: str = 'raw') -> Path:
        """
        Retorna caminho padronizado para arquivo de boletim.

        Args:
            data_pregao: Data do pregão
            tipo: 'raw' ou 'processed'

        Returns:
            Path para o arquivo
        """
        diretorio = DIRETORIO_RAW if tipo == 'raw' else DIRETORIO_PROCESSED
        ano_mes = data_pregao.strftime('%Y-%m')
        nome_arquivo = f"boletim_b3_{data_pregao.isoformat()}.txt"

        # Organiza por ano-mês para facilitar navegação
        subdir = diretorio / ano_mes
        subdir.mkdir(parents=True, exist_ok=True)

        return subdir / nome_arquivo


def exemplo_uso():
    """Exemplo de como usar o módulo."""

    # Inicializar gerenciador
    gerenciador = GerenciadorBoletimB3()

    # Exemplo de dados de boletim (normalmente viriam do parsing de arquivo)
    dados_exemplo = DadosBoletimDiario(
        data_pregao=date(2024, 11, 5),
        simbolo="WIN",
        vencimento=date(2024, 12, 27),
        abertura=Decimal("128500"),
        maxima=Decimal("129200"),
        minima=Decimal("128100"),
        fechamento=Decimal("128950"),
        ajuste_diario=Decimal("128950"),
        variacao_pontos=Decimal("450"),
        variacao_percentual=Decimal("0.35"),
        volume_contratos=285000,
        volume_financeiro=Decimal("3675000000"),
        numero_negocios=125000,
        contratos_abertos=520000,
        spread_bid_ask=Decimal("5"),
        melhor_bid=Decimal("128945"),
        melhor_ask=Decimal("128950")
    )

    # Salvar no banco
    gerenciador.salvar_boletim(dados_exemplo, arquivo_origem="exemplo_manual")

    # Consultar dados
    boletins = gerenciador.obter_boletins(
        simbolo="WIN",
        data_inicio=date(2024, 11, 1),
        data_fim=date(2024, 11, 5)
    )

    print(f"\n📊 Boletins encontrados: {len(boletins)}")
    for b in boletins:
        print(f"  {b['data_pregao']}: Vol={b['volume_contratos']}, OI={b['contratos_abertos']}")

    # Calcular métricas
    metricas = gerenciador.calcular_metricas_microestrutura("WIN", date(2024, 11, 5))
    print(f"\n📈 Métricas calculadas: {metricas}")

    # Mostrar caminho padrão para salvar boletim
    caminho = gerenciador.obter_caminho_boletim(date(2024, 11, 5))
    print(f"\n💾 Caminho sugerido para boletim: {caminho}")


if __name__ == "__main__":
    exemplo_uso()
