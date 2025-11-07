# -*- coding: utf-8 -*-
"""
CLI Analisador de FIIs - Interface para análise de fundos imobiliários.

Uso:
    python consultar_fiis.py analisar KNRI11 HGLG11 MXRF11
    python consultar_fiis.py comparar KNRI11 HGLG11 --exportar
    python consultar_fiis.py ranking KNRI11 HGLG11 MXRF11 VISC11 --top 3
    python consultar_fiis.py setor logistica
"""

import sys
import argparse
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src" / "dados"))

from analisador_fiis import AnalisadorFIIs


def cmd_analisar(args):
    """Analisa múltiplos FIIs e gera relatório completo."""

    analisador = AnalisadorFIIs()

    print(f"\n🔍 Analisando {len(args.fiis)} FIIs...\n")

    analises = analisador.analisar_portfolio(args.fiis)

    if not analises:
        print("\n❌ Nenhum FII foi analisado com sucesso.\n")
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

    # Exportar se solicitado
    if args.exportar:
        filename = f"analise_fiis_{'-'.join(args.fiis)}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"ANÁLISE DE FIIs - {', '.join(args.fiis)}\n")
            f.write("="*80 + "\n\n")
            f.write(analisador.gerar_tabela_comparativa())
            f.write("\n\n")
            f.write(analisador.gerar_relatorio_executivo())
        print(f"✅ Análise exportada para: {filename}\n")


def cmd_ranking(args):
    """Gera ranking simples sem relatório detalhado."""

    analisador = AnalisadorFIIs()

    analises = analisador.analisar_portfolio(args.fiis)

    if not analises:
        print("\n❌ Nenhum FII foi analisado com sucesso.\n")
        return

    print(f"\n{'='*80}")
    print(f"🏆 RANKING DE FIIs - TOP {min(args.top, len(analises))}")
    print(f"{'='*80}\n")

    print(f"{'#':<4} {'FII':<10} {'Tipo':<10} {'Score':>8} {'DY':>10} {'P/VP':>8} {'Recomendação':<15}")
    print("-" * 80)

    for i, fii in enumerate(analises[:args.top], 1):
        # Emoji posição
        if i == 1:
            emoji = "🥇"
        elif i == 2:
            emoji = "🥈"
        elif i == 3:
            emoji = "🥉"
        else:
            emoji = "  "

        # Emoji recomendação
        if fii.recomendacao == 'COMPRA_FORTE':
            rec_emoji = "✅"
        elif fii.recomendacao == 'COMPRA':
            rec_emoji = "⚠️ "
        elif fii.recomendacao == 'NEUTRO':
            rec_emoji = "⚪"
        else:
            rec_emoji = "❌"

        print(f"{emoji} {i:<2} {fii.codigo:<10} {fii.tipo:<10} {fii.score_final:>7}/100 " +
              f"{float(fii.dy_12m):>9.2f}% {float(fii.pvp_atual):>7.2f} " +
              f"{rec_emoji} {fii.recomendacao:<13}")

    print(f"\n{'='*80}")
    print(f"🥇 MELHOR OPORTUNIDADE: {analises[0].codigo}")
    print(f"   Tipo: {analises[0].tipo} - {analises[0].setor}")
    print(f"   Score: {analises[0].score_final}/100")
    print(f"   P/VP: {float(analises[0].pvp_atual):.2f}")
    print(f"   DY 12M: {float(analises[0].dy_12m):.2f}%")
    print(f"{'='*80}\n")


def cmd_comparar(args):
    """Compara 2-3 FIIs lado a lado (formato simplificado)."""

    if len(args.fiis) < 2:
        print("\n❌ Forneça pelo menos 2 FIIs para comparar.\n")
        return

    if len(args.fiis) > 3:
        print("\n⚠️  Comparação limitada a 3 FIIs. Usando os 3 primeiros.\n")
        args.fiis = args.fiis[:3]

    analisador = AnalisadorFIIs()
    analises = analisador.analisar_portfolio(args.fiis)

    if not analises:
        print("\n❌ Nenhum FII foi analisado com sucesso.\n")
        return

    print(f"\n{'='*80}")
    print("📊 COMPARAÇÃO DIRETA")
    print(f"{'='*80}\n")

    # Tabela simplificada
    print(analisador.gerar_tabela_comparativa())

    # Vencedor
    melhor = analises[0]
    print(f"\n🏆 VENCEDOR: {melhor.codigo} ({melhor.score_final}/100)")
    print(f"   {melhor.tipo} - {melhor.setor}")
    print(f"   P/VP: {float(melhor.pvp_atual):.2f} | DY: {float(melhor.dy_12m):.2f}%")

    if args.exportar:
        filename = f"comparacao_fiis_{'-'.join(args.fiis)}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"COMPARAÇÃO DE FIIs - {', '.join(args.fiis)}\n")
            f.write("="*80 + "\n\n")
            f.write(analisador.gerar_tabela_comparativa())
        print(f"\n✅ Comparação exportada para: {filename}\n")


def cmd_setor(args):
    """Analisa FIIs de um setor específico."""

    # Setores pré-definidos
    setores = {
        'logistica': ['HGLG11', 'LOGG3', 'RLOG11', 'VILG11'],
        'lajes': ['KNIP11', 'HGRE11', 'RECT11', 'PVBI11'],
        'shoppings': ['XPML11', 'VISC11', 'HSML11', 'MALL11'],
        'papel': ['KNRI11', 'MXRF11', 'BTLG11', 'KNCR11'],
        'hibrido': ['HGBS11', 'RBRF11', 'BCFF11', 'CPTS11'],
    }

    if args.setor.lower() not in setores:
        print(f"\n❌ Setor '{args.setor}' não encontrado.")
        print(f"\nSetores disponíveis: {', '.join(setores.keys())}\n")
        return

    fiis = setores[args.setor.lower()]

    analisador = AnalisadorFIIs()

    print(f"\n📊 Análise do Setor: {args.setor.upper()}")
    print(f"FIIs: {', '.join(fiis)}\n")

    analises = analisador.analisar_portfolio(fiis)

    if analises:
        print("\n" + analisador.gerar_tabela_comparativa())
        print("\n" + analisador.gerar_relatorio_executivo())


def main():
    """Função principal do CLI."""

    parser = argparse.ArgumentParser(
        description='Analisador de FIIs - Qualidade e Sustentabilidade',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python consultar_fiis.py analisar KNRI11 HGLG11 MXRF11
  python consultar_fiis.py ranking KNRI11 HGLG11 MXRF11 VISC11 --top 3
  python consultar_fiis.py comparar KNRI11 HGLG11
  python consultar_fiis.py setor logistica
        """
    )

    subparsers = parser.add_subparsers(dest='comando', help='Comando a executar')

    # Comando: analisar
    parser_analisar = subparsers.add_parser(
        'analisar',
        help='Análise completa com tabela e relatório'
    )
    parser_analisar.add_argument(
        'fiis',
        nargs='+',
        help='Códigos dos FIIs (ex: KNRI11 HGLG11 MXRF11)'
    )
    parser_analisar.add_argument(
        '--exportar',
        action='store_true',
        help='Exportar análise para arquivo TXT'
    )

    # Comando: ranking
    parser_ranking = subparsers.add_parser(
        'ranking',
        help='Ranking simples sem relatório detalhado'
    )
    parser_ranking.add_argument(
        'fiis',
        nargs='+',
        help='Códigos dos FIIs'
    )
    parser_ranking.add_argument(
        '--top',
        type=int,
        default=10,
        help='Número de FIIs no ranking (default: 10)'
    )

    # Comando: comparar
    parser_comparar = subparsers.add_parser(
        'comparar',
        help='Compara 2-3 FIIs lado a lado'
    )
    parser_comparar.add_argument(
        'fiis',
        nargs='+',
        help='Códigos dos FIIs (2 ou 3)'
    )
    parser_comparar.add_argument(
        '--exportar',
        action='store_true',
        help='Exportar comparação para arquivo TXT'
    )

    # Comando: setor
    parser_setor = subparsers.add_parser(
        'setor',
        help='Analisa FIIs de um setor específico'
    )
    parser_setor.add_argument(
        'setor',
        choices=['logistica', 'lajes', 'shoppings', 'papel', 'hibrido'],
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
    elif args.comando == 'comparar':
        cmd_comparar(args)
    elif args.comando == 'setor':
        cmd_setor(args)


if __name__ == "__main__":
    main()
