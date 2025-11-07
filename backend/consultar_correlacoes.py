# -*- coding: utf-8 -*-
"""
CLI para consultar cotações de ativos correlacionados ao WIN.

Comandos disponíveis:
- listar: Mostra ativos configurados
- coletar: Executa coleta de cotações
- ultimas: Mostra últimas cotações
- variacao: Mostra variação dos ativos em período
- matriz: Calcula e exibe matriz de correlação
"""

import sys
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import argparse

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from dados.coletor_correlacoes import ColetorCorrelacoes


CAMINHO_DB = Path(__file__).parent / "data" / "recomendacoes.sqlite"


def cmd_listar(args):
    """Lista ativos configurados para coleta."""

    conn = sqlite3.connect(CAMINHO_DB)
    cur = conn.cursor()

    # Filtro de prioridade
    if args.prioridade and args.prioridade != 'todas':
        cur.execute("""
            SELECT simbolo, nome, categoria, prioridade, correlacao_esperada,
                   tipo_correlacao, total_coletas, ultima_coleta
            FROM ativos_correlacao_config
            WHERE ativo = 1 AND prioridade = ?
            ORDER BY prioridade, categoria, simbolo
        """, (args.prioridade,))
    else:
        cur.execute("""
            SELECT simbolo, nome, categoria, prioridade, correlacao_esperada,
                   tipo_correlacao, total_coletas, ultima_coleta
            FROM ativos_correlacao_config
            WHERE ativo = 1
            ORDER BY
                CASE prioridade
                    WHEN 'alta' THEN 1
                    WHEN 'media' THEN 2
                    WHEN 'baixa' THEN 3
                END,
                categoria, simbolo
        """)

    ativos = cur.fetchall()
    conn.close()

    if not ativos:
        print("\n⚠️  Nenhum ativo configurado")
        print("   Execute: consultar_correlacoes.py coletar --inicializar")
        return

    print(f"\n{'='*100}")
    print(f"ATIVOS CONFIGURADOS PARA CORRELAÇÃO COM WIN")
    print(f"{'='*100}\n")

    prioridade_atual = None

    for simbolo, nome, categoria, prioridade, corr, tipo, total, ultima in ativos:
        # Cabeçalho de prioridade
        if prioridade != prioridade_atual:
            prioridade_atual = prioridade
            emoji = {'alta': '🔴', 'media': '🟡', 'baixa': '🟢'}
            print(f"\n{emoji.get(prioridade, '⚪')} PRIORIDADE {prioridade.upper()}")
            print("-" * 100)

        # Formato de correlação
        corr_str = f"{corr:+.2f}".rjust(6)
        tipo_emoji = "📈" if tipo == "direto" else "📉"

        # Status de coleta
        if ultima:
            ultima_dt = datetime.fromisoformat(ultima)
            diff = datetime.now() - ultima_dt

            if diff.total_seconds() < 3600:  # < 1h
                status = f"✅ {int(diff.total_seconds() / 60)}min atrás"
            elif diff.total_seconds() < 86400:  # < 24h
                status = f"✅ {int(diff.total_seconds() / 3600)}h atrás"
            else:
                status = f"⚠️  {diff.days} dias atrás"
        else:
            status = "❌ Nunca coletado"

        print(f"{simbolo:12} {nome:25} {categoria:12} {tipo_emoji} {corr_str}  " +
              f"Coletas: {total:4}  {status}")

    print(f"\n{'='*100}\n")


def cmd_coletar(args):
    """Executa coleta de cotações."""

    coletor = ColetorCorrelacoes()

    # Inicializar configuração se solicitado
    if args.inicializar:
        print("\n" + "="*80)
        print("INICIALIZANDO CONFIGURAÇÃO DE ATIVOS")
        print("="*80)
        coletor.inicializar_ativos(incluir_prioridade_baixa=args.incluir_baixa)

    # Executar coleta
    coletor.coletar_todos_ativos(
        prioridade=args.prioridade,
        periodo=args.periodo,
        intervalo=args.intervalo
    )


def cmd_ultimas(args):
    """Mostra últimas cotações coletadas."""

    conn = sqlite3.connect(CAMINHO_DB)
    cur = conn.cursor()

    # Buscar última cotação de cada ativo
    query = """
        SELECT c.simbolo, c.nome, c.categoria, c.fechamento,
               c.variacao_dia, c.data_hora, cfg.prioridade
        FROM cotacoes_correlacoes c
        INNER JOIN ativos_correlacao_config cfg ON c.simbolo = cfg.simbolo
        WHERE c.data_hora = (
            SELECT MAX(data_hora) FROM cotacoes_correlacoes c2
            WHERE c2.simbolo = c.simbolo
        )
    """

    # Filtro de prioridade
    if args.prioridade and args.prioridade != 'todas':
        query += " AND cfg.prioridade = ?"
        cur.execute(query + " ORDER BY cfg.prioridade, c.simbolo", (args.prioridade,))
    else:
        cur.execute(query + """
            ORDER BY
                CASE cfg.prioridade
                    WHEN 'alta' THEN 1
                    WHEN 'media' THEN 2
                    WHEN 'baixa' THEN 3
                END,
                c.simbolo
        """)

    cotacoes = cur.fetchall()
    conn.close()

    if not cotacoes:
        print("\n⚠️  Nenhuma cotação encontrada")
        print("   Execute: consultar_correlacoes.py coletar")
        return

    print(f"\n{'='*100}")
    print(f"ÚLTIMAS COTAÇÕES COLETADAS")
    print(f"{'='*100}\n")

    prioridade_atual = None

    for simbolo, nome, categoria, fechamento, variacao, data_hora, prioridade in cotacoes:
        # Cabeçalho de prioridade
        if prioridade != prioridade_atual:
            prioridade_atual = prioridade
            emoji = {'alta': '🔴', 'media': '🟡', 'baixa': '🟢'}
            print(f"\n{emoji.get(prioridade, '⚪')} PRIORIDADE {prioridade.upper()}")
            print("-" * 100)

        # Formato de variação
        if variacao is not None:
            variacao_str = f"{variacao:+6.2f}%"
            emoji_var = "📈" if variacao > 0 else "📉" if variacao < 0 else "➡️"
        else:
            variacao_str = "   N/A"
            emoji_var = "➡️"

        # Formato de data
        data_dt = datetime.fromisoformat(data_hora)
        data_str = data_dt.strftime("%d/%m %H:%M")

        print(f"{simbolo:12} {nome:25} {categoria:12} {fechamento:12.2f}  " +
              f"{emoji_var} {variacao_str}  {data_str}")

    print(f"\n{'='*100}\n")


def cmd_variacao(args):
    """Mostra variação dos ativos em período específico."""

    # Calcular data inicial
    data_fim = datetime.now()
    data_inicio = data_fim - timedelta(days=args.dias)

    conn = sqlite3.connect(CAMINHO_DB)
    cur = conn.cursor()

    # Buscar primeira e última cotação de cada ativo no período
    cur.execute("""
        SELECT
            c.simbolo,
            c.nome,
            (SELECT fechamento FROM cotacoes_correlacoes
             WHERE simbolo = c.simbolo AND data_hora >= ?
             ORDER BY data_hora ASC LIMIT 1) as preco_inicial,
            (SELECT fechamento FROM cotacoes_correlacoes
             WHERE simbolo = c.simbolo AND data_hora >= ?
             ORDER BY data_hora DESC LIMIT 1) as preco_final,
            cfg.prioridade
        FROM cotacoes_correlacoes c
        INNER JOIN ativos_correlacao_config cfg ON c.simbolo = cfg.simbolo
        WHERE c.data_hora >= ?
        GROUP BY c.simbolo, c.nome, cfg.prioridade
        ORDER BY
            CASE cfg.prioridade
                WHEN 'alta' THEN 1
                WHEN 'media' THEN 2
                WHEN 'baixa' THEN 3
            END,
            c.simbolo
    """, (data_inicio.isoformat(), data_inicio.isoformat(), data_inicio.isoformat()))

    resultados = cur.fetchall()
    conn.close()

    if not resultados:
        print(f"\n⚠️  Nenhum dado encontrado para os últimos {args.dias} dias")
        return

    print(f"\n{'='*100}")
    print(f"VARIAÇÃO DOS ATIVOS - Últimos {args.dias} dias")
    print(f"{'='*100}\n")

    prioridade_atual = None

    for simbolo, nome, preco_ini, preco_fim, prioridade in resultados:
        # Cabeçalho de prioridade
        if prioridade != prioridade_atual:
            prioridade_atual = prioridade
            emoji = {'alta': '🔴', 'media': '🟡', 'baixa': '🟢'}
            print(f"\n{emoji.get(prioridade, '⚪')} PRIORIDADE {prioridade.upper()}")
            print("-" * 100)

        if preco_ini and preco_fim:
            variacao = ((preco_fim - preco_ini) / preco_ini) * 100
            variacao_str = f"{variacao:+6.2f}%"
            emoji_var = "📈" if variacao > 0 else "📉" if variacao < 0 else "➡️"

            print(f"{simbolo:12} {nome:25} {preco_ini:12.2f} → {preco_fim:12.2f}  " +
                  f"{emoji_var} {variacao_str}")
        else:
            print(f"{simbolo:12} {nome:25} - Dados insuficientes")

    print(f"\n{'='*100}\n")


def cmd_matriz(args):
    """Calcula e exibe matriz de correlação entre ativos."""

    import numpy as np
    import pandas as pd

    # Calcular data inicial
    data_fim = datetime.now()
    data_inicio = data_fim - timedelta(days=args.dias)

    conn = sqlite3.connect(CAMINHO_DB)

    # Buscar dados para cálculo de correlação
    query = """
        SELECT simbolo, data_hora, fechamento
        FROM cotacoes_correlacoes
        WHERE data_hora >= ?
        ORDER BY simbolo, data_hora
    """

    df = pd.read_sql_query(query, conn, params=(data_inicio.isoformat(),))
    conn.close()

    if df.empty:
        print(f"\n⚠️  Nenhum dado encontrado para os últimos {args.dias} dias")
        return

    # Pivotar para criar série temporal por ativo
    pivot = df.pivot(index='data_hora', columns='simbolo', values='fechamento')

    # Calcular retornos percentuais
    returns = pivot.pct_change().dropna()

    if returns.empty:
        print("\n⚠️  Dados insuficientes para calcular correlações")
        return

    # Calcular matriz de correlação
    corr_matrix = returns.corr()

    # Exibir matriz
    print(f"\n{'='*100}")
    print(f"MATRIZ DE CORRELAÇÃO - Últimos {args.dias} dias")
    print(f"{'='*100}\n")

    # Formatar para exibição
    print("Ativo".ljust(12), end='')
    for col in corr_matrix.columns:
        print(f"{col[:8]:>8}", end='')
    print()
    print("-" * 100)

    for idx in corr_matrix.index:
        print(f"{idx[:12]:12}", end='')
        for col in corr_matrix.columns:
            valor = corr_matrix.loc[idx, col]

            # Colorização por intensidade
            if abs(valor) > 0.8:
                emoji = "🔴" if valor > 0 else "🔵"
            elif abs(valor) > 0.5:
                emoji = "🟠" if valor > 0 else "🟦"
            else:
                emoji = "⚪"

            if idx == col:
                print(f"   -    ", end='')
            else:
                print(f"{emoji}{valor:+.2f}  ", end='')
        print()

    print(f"\n{'='*100}")
    print("Legenda: 🔴 Forte positiva (>0.8) | 🟠 Moderada positiva (>0.5)")
    print("         🔵 Forte negativa (<-0.8) | 🟦 Moderada negativa (<-0.5) | ⚪ Fraca")
    print(f"{'='*100}\n")

    # Salvar matriz no banco
    if args.salvar:
        conn = sqlite3.connect(CAMINHO_DB)
        cur = conn.cursor()

        salvos = 0
        for idx in corr_matrix.index:
            for col in corr_matrix.columns:
                if idx < col:  # Evitar duplicatas (A-B = B-A)
                    valor = corr_matrix.loc[idx, col]

                    try:
                        cur.execute("""
                            INSERT INTO matriz_correlacao (simbolo1, simbolo2, periodo_dias, correlacao)
                            VALUES (?, ?, ?, ?)
                        """, (idx, col, args.dias, float(valor)))
                        salvos += 1
                    except sqlite3.IntegrityError:
                        # Já existe para hoje, atualizar
                        cur.execute("""
                            UPDATE matriz_correlacao
                            SET correlacao = ?, data_calculo = CURRENT_TIMESTAMP
                            WHERE simbolo1 = ? AND simbolo2 = ? AND periodo_dias = ?
                              AND date(data_calculo) = date('now')
                        """, (float(valor), idx, col, args.dias))

        conn.commit()
        conn.close()

        print(f"✅ Matriz salva no banco: {salvos} correlações registradas\n")


def main():
    """Função principal do CLI."""

    parser = argparse.ArgumentParser(
        description='Consulta cotações de ativos correlacionados ao WIN',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='comando', help='Comando a executar')

    # Comando: listar
    parser_listar = subparsers.add_parser('listar', help='Lista ativos configurados')
    parser_listar.add_argument(
        '--prioridade',
        choices=['alta', 'media', 'baixa', 'todas'],
        default='todas',
        help='Filtrar por prioridade'
    )

    # Comando: coletar
    parser_coletar = subparsers.add_parser('coletar', help='Coleta cotações')
    parser_coletar.add_argument(
        '--prioridade',
        choices=['alta', 'media', 'baixa', 'todas'],
        default='alta',
        help='Prioridade dos ativos a coletar'
    )
    parser_coletar.add_argument(
        '--periodo',
        default='1d',
        help='Período de histórico (1d, 5d, 1mo, etc.)'
    )
    parser_coletar.add_argument(
        '--intervalo',
        default='1h',
        help='Intervalo dos candles (1m, 5m, 15m, 1h, 1d)'
    )
    parser_coletar.add_argument(
        '--inicializar',
        action='store_true',
        help='Inicializar configuração de ativos antes de coletar'
    )
    parser_coletar.add_argument(
        '--incluir-baixa',
        action='store_true',
        help='Incluir também ativos de prioridade baixa na inicialização'
    )

    # Comando: ultimas
    parser_ultimas = subparsers.add_parser('ultimas', help='Mostra últimas cotações')
    parser_ultimas.add_argument(
        '--prioridade',
        choices=['alta', 'media', 'baixa', 'todas'],
        default='todas',
        help='Filtrar por prioridade'
    )

    # Comando: variacao
    parser_variacao = subparsers.add_parser('variacao', help='Mostra variação em período')
    parser_variacao.add_argument(
        '--dias',
        type=int,
        default=7,
        help='Número de dias a analisar'
    )

    # Comando: matriz
    parser_matriz = subparsers.add_parser('matriz', help='Calcula matriz de correlação')
    parser_matriz.add_argument(
        '--dias',
        type=int,
        default=30,
        help='Período para cálculo (dias)'
    )
    parser_matriz.add_argument(
        '--salvar',
        action='store_true',
        help='Salvar matriz no banco de dados'
    )

    args = parser.parse_args()

    if not args.comando:
        parser.print_help()
        return

    # Executar comando
    if args.comando == 'listar':
        cmd_listar(args)
    elif args.comando == 'coletar':
        cmd_coletar(args)
    elif args.comando == 'ultimas':
        cmd_ultimas(args)
    elif args.comando == 'variacao':
        cmd_variacao(args)
    elif args.comando == 'matriz':
        cmd_matriz(args)


if __name__ == "__main__":
    main()
