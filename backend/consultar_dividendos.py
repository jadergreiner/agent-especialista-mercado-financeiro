# -*- coding: utf-8 -*-
"""
CLI Analisador de Dividendos - Interface para análise de ações.

Uso:
    python consultar_dividendos.py analisar TGMA3 KLBN11 GGBR4
    python consultar_dividendos.py comparar ITSA4 BBDC4 PETR4 --top 3
"""

import sys
import argparse
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src" / "dados"))

from analisador_dividendos import AnalisadorDividendos


def cmd_analisar(args):
    """Analisa múltiplas ações e gera relatório completo."""

    analisador = AnalisadorDividendos()

    print(f"\n🔍 Analisando {len(args.acoes)} ações...\n")

    analises = analisador.analisar_portfolio(args.acoes)

    if not analises:
        print("\n❌ Nenhuma ação foi analisada com sucesso.\n")
        return

    # Tabela comparativa
    print(f"\n{'='*80}")
    print("📊 TABELA COMPARATIVA")
    print(f"{'='*80}\n")

    print(analisador.gerar_tabela_comparativa())

    # Relatório executivo
    print(f"\n{'='*80}")
    print(analisador.gerar_relatorio_executivo())
    print(f"{'='*80}\n")


def cmd_ranking(args):
    """Gera ranking simples sem relatório detalhado."""

    analisador = AnalisadorDividendos()

    analises = analisador.analisar_portfolio(args.acoes)

    if not analises:
        print("\n❌ Nenhuma ação foi analisada com sucesso.\n")
        return

    print(f"\n{'='*80}")
    print(f"🏆 RANKING DE DIVIDENDOS - TOP {min(args.top, len(analises))}")
    print(f"{'='*80}\n")

    print(f"{'#':<4} {'Ação':<10} {'Score':>8} {'DY':>10} {'P/L':>8} {'Liq.':>8} {'Recomendação':<15}")
    print("-" * 80)

    for i, acao in enumerate(analises[:args.top], 1):
        # Emoji
        if i == 1:
            emoji = "🥇"
        elif i == 2:
            emoji = "🥈"
        elif i == 3:
            emoji = "🥉"
        else:
            emoji = "  "

        # Emoji recomendação
        if acao.recomendacao == 'COMPRA_FORTE':
            rec_emoji = "✅"
        elif acao.recomendacao == 'COMPRA':
            rec_emoji = "⚠️ "
        else:
            rec_emoji = "⚪"

        print(f"{emoji} {i:<2} {acao.codigo:<10} {acao.score_final:>7}/100 " +
              f"{float(acao.dy_12m):>9.2f}% {float(acao.pl_atual):>7.2f} " +
              f"{float(acao.liquidez_corrente):>7.2f} " +
              f"{rec_emoji} {acao.recomendacao:<13}")

    print(f"\n{'='*80}")
    print(f"🥇 MELHOR OPORTUNIDADE: {analises[0].codigo}")
    print(f"   Score: {analises[0].score_final}/100")
    print(f"   Preço Ideal: R$ {float(analises[0].preco_ideal_8pct):.2f}")
    print(f"   Consistência: {analises[0].consistencia_dividendos}")
    print(f"{'='*80}\n")


def cmd_setor(args):
    """Analisa ações de um setor específico."""

    # Setores pré-definidos
    setores = {
        'bancos': ['ITUB4', 'BBDC4', 'BBAS3', 'SANB11', 'BPAN4'],
        'energia': ['PETR4', 'ELET3', 'ELET6', 'TAEE11', 'CPLE6'],
        'utilities': ['SAPR4', 'SBSP3', 'CSAN3', 'TRPL4', 'CMIG4'],
        'siderurgia': ['GGBR4', 'GOAU4', 'CSNA3', 'USIM5'],
        'varejo': ['LREN3', 'PCAR3', 'MGLU3', 'ARZZ3', 'VIVA3'],
    }

    if args.setor.lower() not in setores:
        print(f"\n❌ Setor '{args.setor}' não encontrado.")
        print(f"\nSetores disponíveis: {', '.join(setores.keys())}\n")
        return

    acoes = setores[args.setor.lower()]

    analisador = AnalisadorDividendos()

    print(f"\n📊 Análise do Setor: {args.setor.upper()}")
    print(f"Ações: {', '.join(acoes)}\n")

    analises = analisador.analisar_portfolio(acoes)

    if analises:
        print("\n" + analisador.gerar_tabela_comparativa())
        print("\n" + analisador.gerar_relatorio_executivo())


def main():
    """Função principal do CLI."""

    parser = argparse.ArgumentParser(
        description='Analisador de Dividendos - Seleção de Renda Passiva',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='comando', help='Comando a executar')

    # Comando: analisar
    parser_analisar = subparsers.add_parser(
        'analisar',
        help='Análise completa com tabela e relatório'
    )
    parser_analisar.add_argument(
        'acoes',
        nargs='+',
        help='Códigos das ações (ex: TGMA3 KLBN11 GGBR4)'
    )

    # Comando: ranking
    parser_ranking = subparsers.add_parser(
        'ranking',
        help='Ranking simples sem relatório detalhado'
    )
    parser_ranking.add_argument(
        'acoes',
        nargs='+',
        help='Códigos das ações'
    )
    parser_ranking.add_argument(
        '--top',
        type=int,
        default=10,
        help='Número de ações no ranking (default: 10)'
    )

    # Comando: setor
    parser_setor = subparsers.add_parser(
        'setor',
        help='Analisa ações de um setor específico'
    )
    parser_setor.add_argument(
        'setor',
        choices=['bancos', 'energia', 'utilities', 'siderurgia', 'varejo'],
        help='Setor a analisar'
    )

    args = parser.parse_args()

    if not args.comando:
        parser.print_help()
        return

    # Executar comando
    if args.comando == 'analisar':
        cmd_analisar(args)
    elif args.comando == 'ranking':
        cmd_ranking(args)
    elif args.comando == 'setor':
        cmd_setor(args)


if __name__ == "__main__":
    main()
