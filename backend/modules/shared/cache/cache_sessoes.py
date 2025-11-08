#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cache de Sessões v2 - SQLite

Sistema de cache para resultados de análises com TTL por classe de ativo.
Reduz latência e carga nas APIs externas.
"""
import sqlite3
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any


class CacheSessoes:
    """
    Gerencia cache de resultados de análises com TTL configurável.

    Características:
    - Storage SQLite (leve, sem dependências externas)
    - TTL por classe de ativo (forex: 5min, cripto: 2min)
    - Chave composta: símbolo + classe + timeframe
    - Invalidação automática por expiração
    """

    # TTL padrão em minutos por classe de ativo
    TTL_PADRAO = {
        'forex': 5,      # Forex: 5 minutos (mercado menos volátil)
        'cripto': 2,     # Cripto: 2 minutos (alta volatilidade)
        'acao': 5,       # Ações: 5 minutos
        'commodities': 5 # Commodities: 5 minutos
    }

    def __init__(self, caminho_db: Optional[Path] = None):
        """
        Inicializa cache.

        Args:
            caminho_db: Caminho do arquivo SQLite (padrão: backend/cache/sessoes_cache.db)
        """
        if caminho_db is None:
            caminho_db = Path(__file__).parent / 'cache' / 'sessoes_cache.db'

        caminho_db.parent.mkdir(exist_ok=True)
        self.caminho_db = caminho_db
        self._criar_tabela()

    def _criar_tabela(self):
        """Cria tabela de cache se não existir."""
        with sqlite3.connect(self.caminho_db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache_analises (
                    chave TEXT PRIMARY KEY,
                    simbolo TEXT NOT NULL,
                    classe TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    resultado TEXT NOT NULL,
                    criado_em TEXT NOT NULL,
                    expira_em TEXT NOT NULL
                )
            """)
            # Índice para facilitar limpeza de expirados
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_expira_em
                ON cache_analises(expira_em)
            """)
            conn.commit()

    def _gerar_chave(self, simbolo: str, classe: str, timeframe: str = 'intraday') -> str:
        """
        Gera chave única para o cache.

        Args:
            simbolo: Símbolo do ativo (ex: BTCUSDT, EURUSD)
            classe: Classe do ativo (forex, cripto, acao, commodities)
            timeframe: Timeframe da análise (intraday, diario, semanal)

        Returns:
            Chave única: "SIMBOLO:CLASSE:TIMEFRAME"
        """
        return f"{simbolo.upper()}:{classe.lower()}:{timeframe.lower()}"

    def obter(self, simbolo: str, classe: str, timeframe: str = 'intraday') -> Optional[Dict[str, Any]]:
        """
        Obtém resultado do cache se válido.

        Args:
            simbolo: Símbolo do ativo
            classe: Classe do ativo
            timeframe: Timeframe da análise

        Returns:
            Resultado em cache ou None se expirado/inexistente
        """
        chave = self._gerar_chave(simbolo, classe, timeframe)
        agora = datetime.now(timezone.utc).isoformat()

        with sqlite3.connect(self.caminho_db) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT resultado FROM cache_analises
                WHERE chave = ? AND expira_em > ?
            """, (chave, agora))

            linha = cursor.fetchone()
            if linha:
                return json.loads(linha['resultado'])

        return None

    def armazenar(
        self,
        simbolo: str,
        classe: str,
        resultado: Dict[str, Any],
        timeframe: str = 'intraday',
        ttl_minutos: Optional[int] = None
    ):
        """
        Armazena resultado no cache.

        Args:
            simbolo: Símbolo do ativo
            classe: Classe do ativo
            resultado: Resultado da análise (dict serializable)
            timeframe: Timeframe da análise
            ttl_minutos: TTL customizado em minutos (usa padrão se None)
        """
        chave = self._gerar_chave(simbolo, classe, timeframe)
        agora = datetime.now(timezone.utc)

        # Define TTL
        if ttl_minutos is None:
            ttl_minutos = self.TTL_PADRAO.get(classe.lower(), 5)

        expira_em = agora + timedelta(minutes=ttl_minutos)

        with sqlite3.connect(self.caminho_db) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO cache_analises
                (chave, simbolo, classe, timeframe, resultado, criado_em, expira_em)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                chave,
                simbolo.upper(),
                classe.lower(),
                timeframe.lower(),
                json.dumps(resultado, ensure_ascii=False),
                agora.isoformat(),
                expira_em.isoformat()
            ))
            conn.commit()

    def limpar_expirados(self) -> int:
        """
        Remove entradas expiradas do cache.

        Returns:
            Número de entradas removidas
        """
        agora = datetime.now(timezone.utc).isoformat()

        with sqlite3.connect(self.caminho_db) as conn:
            cursor = conn.execute("""
                DELETE FROM cache_analises
                WHERE expira_em <= ?
            """, (agora,))
            conn.commit()
            return cursor.rowcount

    def invalidar(self, simbolo: str, classe: str, timeframe: str = 'intraday'):
        """
        Invalida entrada específica do cache.

        Args:
            simbolo: Símbolo do ativo
            classe: Classe do ativo
            timeframe: Timeframe da análise
        """
        chave = self._gerar_chave(simbolo, classe, timeframe)

        with sqlite3.connect(self.caminho_db) as conn:
            conn.execute("""
                DELETE FROM cache_analises
                WHERE chave = ?
            """, (chave,))
            conn.commit()

    def estatisticas(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do cache.

        Returns:
            Dict com total de entradas, válidas, expiradas, por classe
        """
        agora = datetime.now(timezone.utc).isoformat()

        with sqlite3.connect(self.caminho_db) as conn:
            conn.row_factory = sqlite3.Row

            # Total de entradas
            total = conn.execute("SELECT COUNT(*) as total FROM cache_analises").fetchone()['total']

            # Válidas (não expiradas)
            validas = conn.execute("""
                SELECT COUNT(*) as validas FROM cache_analises
                WHERE expira_em > ?
            """, (agora,)).fetchone()['validas']

            # Por classe
            por_classe = {}
            cursor = conn.execute("""
                SELECT classe, COUNT(*) as count FROM cache_analises
                WHERE expira_em > ?
                GROUP BY classe
            """, (agora,))

            for linha in cursor:
                por_classe[linha['classe']] = linha['count']

        return {
            'total': total,
            'validas': validas,
            'expiradas': total - validas,
            'por_classe': por_classe
        }


if __name__ == '__main__':
    # Teste básico
    print("🧪 Testando CacheSessoes...")

    cache = CacheSessoes()

    # Teste 1: Armazenar e recuperar
    print("\n✅ Teste 1: Armazenar e recuperar")
    resultado_teste = {
        'simbolo': 'BTCUSDT',
        'operacao': 'COMPRA',
        'preco_entrada': 45000.0,
        'stop_loss': 44500.0,
        'take_profit': 46000.0
    }
    cache.armazenar('BTCUSDT', 'cripto', resultado_teste)

    recuperado = cache.obter('BTCUSDT', 'cripto')
    assert recuperado is not None, "Erro: não recuperou do cache"
    assert recuperado['operacao'] == 'COMPRA', "Erro: dados incorretos"
    print(f"   Recuperado: {recuperado['simbolo']} - {recuperado['operacao']}")

    # Teste 2: Cache miss (símbolo diferente)
    print("\n✅ Teste 2: Cache miss (símbolo não existe)")
    resultado = cache.obter('ETHUSD', 'cripto')
    assert resultado is None, "Erro: deveria retornar None"
    print("   Retornou None conforme esperado")

    # Teste 3: Estatísticas
    print("\n✅ Teste 3: Estatísticas")
    stats = cache.estatisticas()
    print(f"   Total: {stats['total']} | Válidas: {stats['validas']} | Expiradas: {stats['expiradas']}")
    print(f"   Por classe: {stats['por_classe']}")

    # Teste 4: TTL customizado
    print("\n✅ Teste 4: TTL customizado (forex 5min)")
    cache.armazenar('EURUSD', 'forex', {'simbolo': 'EURUSD', 'operacao': 'VENDA'}, ttl_minutos=5)
    recuperado_forex = cache.obter('EURUSD', 'forex')
    assert recuperado_forex is not None, "Erro: não recuperou forex"
    print(f"   Recuperado: {recuperado_forex['simbolo']} - {recuperado_forex['operacao']}")

    # Teste 5: Invalidação manual
    print("\n✅ Teste 5: Invalidação manual")
    cache.invalidar('BTCUSDT', 'cripto')
    resultado = cache.obter('BTCUSDT', 'cripto')
    assert resultado is None, "Erro: deveria estar invalidado"
    print("   Invalidado com sucesso")

    print("\n✅ Todos os testes passaram!")
    print(f"\n📊 Estatísticas finais:")
    stats_final = cache.estatisticas()
    print(f"   Total: {stats_final['total']} | Válidas: {stats_final['validas']}")
