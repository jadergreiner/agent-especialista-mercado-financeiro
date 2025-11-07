# -*- coding: utf-8 -*-
"""
Forex Fundamentals - Coleta de Dados Macroeconômicos para Análise Forex.

Coleta dados fundamentais essenciais para análise de Forex:
- Taxas de juros dos principais bancos centrais (Fed, ECB, BoE, BoJ, RBNZ, RBA, BCB)
- Próximas reuniões de política monetária
- Forward guidance (Hawkish/Dovish)
- Diferenciais de juros (Carry Trade)
- Indicadores macro (PIB, Inflação, PMI)

Fonte de Dados:
- APIs de bancos centrais (quando disponível)
- Web scraping de fontes oficiais
- Trading Economics API (opcional)
- Yahoo Finance para dados de mercado
"""

import sqlite3
import yfinance as yf
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from decimal import Decimal
import requests
from bs4 import BeautifulSoup


# Configuração de caminhos
CAMINHO_DB = Path(__file__).parent.parent.parent / "data" / "recomendacoes.sqlite"


@dataclass
class TaxaJurosBancoCentral:
    """Estrutura de dados para taxa de juros de banco central."""

    banco_central: str  # Fed, ECB, BoE, BoJ, RBNZ, RBA, BCB
    pais: str
    moeda: str  # USD, EUR, GBP, JPY, NZD, AUD, BRL

    taxa_atual: Decimal
    taxa_anterior: Optional[Decimal]

    data_decisao: datetime
    proxima_reuniao: Optional[datetime]

    forward_guidance: str  # hawkish, dovish, neutro
    expectativa_mercado: Optional[Decimal]  # Taxa esperada próxima reunião

    data_coleta: datetime = datetime.now()


@dataclass
class IndicadorMacro:
    """Estrutura de dados para indicadores macroeconômicos."""

    pais: str
    indicador: str  # PIB, Inflação, PMI, Desemprego
    valor_atual: Decimal
    valor_anterior: Optional[Decimal]

    periodo_referencia: str  # Q3 2025, Oct 2025, etc.
    unidade: str  # %, pontos, etc.

    data_coleta: datetime = datetime.now()


class ColetorForexFundamentals:
    """Coleta dados fundamentais para análise Forex."""

    # Configuração de Bancos Centrais
    BANCOS_CENTRAIS = {
        'FED': {
            'nome': 'Federal Reserve',
            'pais': 'Estados Unidos',
            'moeda': 'USD',
            'simbolo_yahoo': '^IRX',  # Treasury 13 Week
            'url_oficial': 'https://www.federalreserve.gov/'
        },
        'ECB': {
            'nome': 'European Central Bank',
            'pais': 'Zona do Euro',
            'moeda': 'EUR',
            'simbolo_yahoo': 'EURUSD=X',
            'url_oficial': 'https://www.ecb.europa.eu/'
        },
        'BOE': {
            'nome': 'Bank of England',
            'pais': 'Reino Unido',
            'moeda': 'GBP',
            'simbolo_yahoo': 'GBPUSD=X',
            'url_oficial': 'https://www.bankofengland.co.uk/'
        },
        'BOJ': {
            'nome': 'Bank of Japan',
            'pais': 'Japão',
            'moeda': 'JPY',
            'simbolo_yahoo': 'JPYUSD=X',
            'url_oficial': 'https://www.boj.or.jp/en/'
        },
        'RBNZ': {
            'nome': 'Reserve Bank of New Zealand',
            'pais': 'Nova Zelândia',
            'moeda': 'NZD',
            'simbolo_yahoo': 'NZDUSD=X',
            'url_oficial': 'https://www.rbnz.govt.nz/'
        },
        'RBA': {
            'nome': 'Reserve Bank of Australia',
            'pais': 'Austrália',
            'moeda': 'AUD',
            'simbolo_yahoo': 'AUDUSD=X',
            'url_oficial': 'https://www.rba.gov.au/'
        },
        'BCB': {
            'nome': 'Banco Central do Brasil',
            'pais': 'Brasil',
            'moeda': 'BRL',
            'simbolo_yahoo': 'USDBRL=X',
            'url_oficial': 'https://www.bcb.gov.br/'
        }
    }

    # Taxas conhecidas (atualizar manualmente ou via API)
    TAXAS_ATUAIS_MOCK = {
        'FED': {'taxa': 5.50, 'guidance': 'hawkish', 'proxima': '2025-11-07'},
        'ECB': {'taxa': 3.50, 'guidance': 'dovish', 'proxima': '2025-12-12'},
        'BOE': {'taxa': 4.00, 'guidance': 'neutro', 'proxima': '2025-11-06'},
        'BOJ': {'taxa': 0.00, 'guidance': 'dovish', 'proxima': '2025-12-19'},
        'RBNZ': {'taxa': 2.50, 'guidance': 'dovish', 'proxima': '2025-11-26'},
        'RBA': {'taxa': 3.60, 'guidance': 'neutro', 'proxima': '2025-12-03'},
        'BCB': {'taxa': 11.25, 'guidance': 'hawkish', 'proxima': '2025-12-11'}
    }

    def __init__(self):
        """Inicializa o coletor."""
        self._criar_tabelas()

    def _criar_tabelas(self):
        """Cria tabelas necessárias no banco."""
        conn = sqlite3.connect(CAMINHO_DB)
        cur = conn.cursor()

        # Tabela de taxas de juros
        cur.execute("""
            CREATE TABLE IF NOT EXISTS forex_taxas_juros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                banco_central TEXT NOT NULL,
                pais TEXT NOT NULL,
                moeda TEXT NOT NULL,

                taxa_atual REAL NOT NULL,
                taxa_anterior REAL,

                data_decisao TIMESTAMP NOT NULL,
                proxima_reuniao TIMESTAMP,

                forward_guidance TEXT,
                expectativa_mercado REAL,

                data_coleta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                UNIQUE(banco_central, data_decisao)
            )
        """)

        cur.execute("CREATE INDEX IF NOT EXISTS idx_forex_taxas_bc ON forex_taxas_juros(banco_central)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_forex_taxas_moeda ON forex_taxas_juros(moeda)")

        # Tabela de indicadores macro
        cur.execute("""
            CREATE TABLE IF NOT EXISTS forex_indicadores_macro (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pais TEXT NOT NULL,
                indicador TEXT NOT NULL,

                valor_atual REAL NOT NULL,
                valor_anterior REAL,

                periodo_referencia TEXT,
                unidade TEXT,

                data_coleta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                UNIQUE(pais, indicador, periodo_referencia)
            )
        """)

        cur.execute("CREATE INDEX IF NOT EXISTS idx_forex_macro_pais ON forex_indicadores_macro(pais)")

        # Tabela de carry trade (calculado)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS forex_carry_trade (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                par_forex TEXT NOT NULL,

                moeda_base TEXT NOT NULL,
                moeda_cotada TEXT NOT NULL,

                taxa_base REAL NOT NULL,
                taxa_cotada REAL NOT NULL,
                diferencial REAL NOT NULL,

                tipo_carry TEXT,
                atratividade REAL,

                data_calculo TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cur.execute("CREATE INDEX IF NOT EXISTS idx_carry_par ON forex_carry_trade(par_forex)")
        cur.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_carry_unico
            ON forex_carry_trade(par_forex, date(data_calculo))
        """)

        conn.commit()
        conn.close()

        print(f"✅ Tabelas Forex Fundamentals criadas/verificadas em: {CAMINHO_DB}")

    def coletar_taxas_mock(self) -> List[TaxaJurosBancoCentral]:
        """
        Coleta taxas usando dados mock (temporário).

        TODO: Substituir por scraping ou API real quando disponível.
        """
        taxas_coletadas = []

        for bc_code, bc_info in self.BANCOS_CENTRAIS.items():
            mock_data = self.TAXAS_ATUAIS_MOCK.get(bc_code)

            if mock_data:
                taxa = TaxaJurosBancoCentral(
                    banco_central=bc_code,
                    pais=bc_info['pais'],
                    moeda=bc_info['moeda'],
                    taxa_atual=Decimal(str(mock_data['taxa'])),
                    taxa_anterior=None,  # TODO: buscar histórico
                    data_decisao=datetime.now() - timedelta(days=30),  # Mock
                    proxima_reuniao=datetime.fromisoformat(mock_data['proxima']),
                    forward_guidance=mock_data['guidance'],
                    expectativa_mercado=None
                )

                taxas_coletadas.append(taxa)

        return taxas_coletadas

    def salvar_taxas(self, taxas: List[TaxaJurosBancoCentral]) -> int:
        """Salva taxas no banco."""
        if not taxas:
            return 0

        conn = sqlite3.connect(CAMINHO_DB)
        cur = conn.cursor()

        salvos = 0

        for taxa in taxas:
            try:
                cur.execute("""
                    INSERT INTO forex_taxas_juros (
                        banco_central, pais, moeda,
                        taxa_atual, taxa_anterior,
                        data_decisao, proxima_reuniao,
                        forward_guidance, expectativa_mercado
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    taxa.banco_central,
                    taxa.pais,
                    taxa.moeda,
                    float(taxa.taxa_atual),
                    float(taxa.taxa_anterior) if taxa.taxa_anterior else None,
                    taxa.data_decisao.isoformat(),
                    taxa.proxima_reuniao.isoformat() if taxa.proxima_reuniao else None,
                    taxa.forward_guidance,
                    float(taxa.expectativa_mercado) if taxa.expectativa_mercado else None
                ))
                salvos += 1
            except sqlite3.IntegrityError:
                # Atualizar se já existe
                cur.execute("""
                    UPDATE forex_taxas_juros
                    SET taxa_atual = ?, forward_guidance = ?,
                        proxima_reuniao = ?, data_coleta = CURRENT_TIMESTAMP
                    WHERE banco_central = ? AND date(data_decisao) = date(?)
                """, (
                    float(taxa.taxa_atual),
                    taxa.forward_guidance,
                    taxa.proxima_reuniao.isoformat() if taxa.proxima_reuniao else None,
                    taxa.banco_central,
                    taxa.data_decisao.isoformat()
                ))

        conn.commit()
        conn.close()

        return salvos

    def calcular_carry_trades(self) -> List[Dict]:
        """
        Calcula oportunidades de carry trade baseado em diferenciais de juros.

        Returns:
            Lista de dicts com pares ordenados por atratividade
        """
        conn = sqlite3.connect(CAMINHO_DB)
        cur = conn.cursor()

        # Buscar últimas taxas de cada BC
        cur.execute("""
            SELECT banco_central, moeda, taxa_atual, forward_guidance
            FROM forex_taxas_juros
            WHERE data_coleta = (
                SELECT MAX(data_coleta) FROM forex_taxas_juros t2
                WHERE t2.banco_central = forex_taxas_juros.banco_central
            )
        """)

        taxas = {row[1]: {'taxa': row[2], 'guidance': row[3], 'bc': row[0]}
                 for row in cur.fetchall()}

        # Calcular todos os pares possíveis
        carry_trades = []
        moedas = list(taxas.keys())

        for i, moeda_base in enumerate(moedas):
            for moeda_cotada in moedas[i+1:]:
                diferencial = taxas[moeda_base]['taxa'] - taxas[moeda_cotada]['taxa']

                # Determinar direção do carry
                if abs(diferencial) >= 0.5:  # Carry significativo
                    if diferencial > 0:
                        par = f"{moeda_base}{moeda_cotada}"
                        tipo = "positivo_compra"
                        atratividade = diferencial
                    else:
                        par = f"{moeda_cotada}{moeda_base}"
                        tipo = "positivo_venda"
                        atratividade = -diferencial
                        diferencial = -diferencial

                    # Ajustar atratividade por forward guidance
                    if taxas[moeda_base]['guidance'] == 'hawkish':
                        atratividade *= 1.2
                    elif taxas[moeda_base]['guidance'] == 'dovish':
                        atratividade *= 0.8

                    carry_trades.append({
                        'par': par,
                        'moeda_base': moeda_base if diferencial > 0 else moeda_cotada,
                        'moeda_cotada': moeda_cotada if diferencial > 0 else moeda_base,
                        'taxa_base': taxas[moeda_base]['taxa'] if diferencial > 0 else taxas[moeda_cotada]['taxa'],
                        'taxa_cotada': taxas[moeda_cotada]['taxa'] if diferencial > 0 else taxas[moeda_base]['taxa'],
                        'diferencial': abs(diferencial),
                        'tipo': tipo,
                        'atratividade': atratividade
                    })

        # Ordenar por atratividade
        carry_trades.sort(key=lambda x: x['atratividade'], reverse=True)

        # Salvar no banco
        for carry in carry_trades:
            try:
                cur.execute("""
                    INSERT INTO forex_carry_trade (
                        par_forex, moeda_base, moeda_cotada,
                        taxa_base, taxa_cotada, diferencial,
                        tipo_carry, atratividade
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    carry['par'],
                    carry['moeda_base'],
                    carry['moeda_cotada'],
                    carry['taxa_base'],
                    carry['taxa_cotada'],
                    carry['diferencial'],
                    carry['tipo'],
                    carry['atratividade']
                ))
            except sqlite3.IntegrityError:
                pass  # Já existe para hoje

        conn.commit()
        conn.close()

        return carry_trades

    def obter_melhores_carry_trades(self, limite: int = 5) -> List[Dict]:
        """Retorna os melhores carry trades calculados."""
        conn = sqlite3.connect(CAMINHO_DB)
        cur = conn.cursor()

        cur.execute("""
            SELECT par_forex, moeda_base, moeda_cotada,
                   taxa_base, taxa_cotada, diferencial,
                   tipo_carry, atratividade,
                   data_calculo
            FROM forex_carry_trade
            WHERE date(data_calculo) = date('now')
            ORDER BY atratividade DESC
            LIMIT ?
        """, (limite,))

        resultados = []
        for row in cur.fetchall():
            resultados.append({
                'par': row[0],
                'moeda_base': row[1],
                'moeda_cotada': row[2],
                'taxa_base': row[3],
                'taxa_cotada': row[4],
                'diferencial': row[5],
                'tipo': row[6],
                'atratividade': row[7],
                'data': row[8]
            })

        conn.close()
        return resultados


def exemplo_uso():
    """Exemplo de uso do coletor Forex Fundamentals."""

    coletor = ColetorForexFundamentals()

    print("="*80)
    print("COLETANDO TAXAS DE JUROS DOS BANCOS CENTRAIS")
    print("="*80 + "\n")

    # 1. Coletar taxas (mock por enquanto)
    taxas = coletor.coletar_taxas_mock()
    print(f"✅ {len(taxas)} taxas coletadas\n")

    # Exibir taxas
    print("TAXAS ATUAIS:")
    print("-" * 80)
    for taxa in taxas:
        guidance_emoji = {
            'hawkish': '🦅',
            'dovish': '🕊️',
            'neutro': '⚖️'
        }
        emoji = guidance_emoji.get(taxa.forward_guidance, '⚪')

        proxima = taxa.proxima_reuniao.strftime("%d/%m/%Y") if taxa.proxima_reuniao else "N/A"

        print(f"{taxa.moeda:4} {taxa.banco_central:5} {float(taxa.taxa_atual):5.2f}%  " +
              f"{emoji} {taxa.forward_guidance:8}  Próxima: {proxima}")

    # 2. Salvar no banco
    salvos = coletor.salvar_taxas(taxas)
    print(f"\n✅ {salvos} taxas salvas no banco\n")

    # 3. Calcular carry trades
    print("="*80)
    print("CALCULANDO OPORTUNIDADES DE CARRY TRADE")
    print("="*80 + "\n")

    carry_trades = coletor.calcular_carry_trades()

    print("TOP 10 CARRY TRADES:")
    print("-" * 80)
    print(f"{'Par':<10} {'Diferencial':>12} {'Atratividade':>14} {'Tipo':<20}")
    print("-" * 80)

    for carry in carry_trades[:10]:
        print(f"{carry['par']:<10} {carry['diferencial']:>11.2f}%  " +
              f"{carry['atratividade']:>12.2f}  {carry['tipo']:<20}")

    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    exemplo_uso()
