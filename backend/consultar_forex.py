# -*- coding: utf-8 -*-
"""
CLI para Análise Forex - Analisador de Oportunidades em Forex.

Uso:
    python consultar_forex.py analisar GBPNZD --operacao COMPRA
    python consultar_forex.py carry-trades --top 10
    python consultar_forex.py taxas
"""

import sys
import argparse
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src" / "dados"))

from analisador_forex import AnalisadorForex
from forex_fundamentals import ColetorForexFundamentals


def cmd_analisar(args):
    """Analisa um par Forex específico."""

    analisador = AnalisadorForex()

    print(f"\n🔍 Analisando {args.par.upper()} - {args.operacao}")

    analise = analisador.analisar_par(args.par, args.operacao)

    print(analisador.gerar_relatorio_formatado(analise))


def cmd_carry_trades(args):
    """Lista melhores carry trades disponíveis."""

    coletor = ColetorForexFundamentals()

    print(f"\n{'='*80}")
    print(f"TOP {args.top} CARRY TRADES - OPORTUNIDADES")
    print(f"{'='*80}\n")

    # Coletar e calcular
    taxas = coletor.coletar_taxas_mock()
    coletor.salvar_taxas(taxas)
    carry_trades = coletor.calcular_carry_trades()

    print(f"{'#':<4} {'Par':<12} {'Diferencial':>12} {'Atratividade':>14} {'Tipo':<25}")
    print("-" * 80)

    for i, carry in enumerate(carry_trades[:args.top], 1):
        emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
        print(f"{emoji} {i:<2} {carry['par']:<12} {carry['diferencial']:>11.2f}%  " +
              f"{carry['atratividade']:>12.2f}  {carry['tipo']:<25}")

    print(f"\n{'='*80}\n")


def cmd_taxas(args):
    """Mostra taxas atuais dos bancos centrais."""

    coletor = ColetorForexFundamentals()

    print(f"\n{'='*80}")
    print("TAXAS DE JUROS DOS BANCOS CENTRAIS")
    print(f"{'='*80}\n")

    taxas = coletor.coletar_taxas_mock()
    coletor.salvar_taxas(taxas)

    print(f"{'Moeda':<6} {'BC':<6} {'Taxa':>8} {'Guidance':<12} {'Próxima Reunião'}")
    print("-" * 80)

    for taxa in taxas:
        guidance_emoji = {
            'hawkish': '🦅',
            'dovish': '🕊️',
            'neutro': '⚖️'
        }
        emoji = guidance_emoji.get(taxa.forward_guidance, '⚪')

        proxima = taxa.proxima_reuniao.strftime("%d/%m/%Y") if taxa.proxima_reuniao else "N/A"

        print(f"{taxa.moeda:<6} {taxa.banco_central:<6} {float(taxa.taxa_atual):>7.2f}%  " +
              f"{emoji} {taxa.forward_guidance:<10} {proxima}")

    print(f"\n{'='*80}\n")


def cmd_comparar(args):
    """Compara múltiplos pares lado a lado."""

    analisador = AnalisadorForex()

    print(f"\n{'='*80}")
    print(f"COMPARAÇÃO DE PARES FOREX")
    print(f"{'='*80}\n")

    analises = []

    for par in args.pares:
        try:
            analise = analisador.analisar_par(par, args.operacao)
            analises.append(analise)
        except Exception as e:
            print(f"⚠️  Erro ao analisar {par}: {str(e)}")

    if not analises:
        print("Nenhuma análise válida.")
        return

    # Tabela comparativa
    print(f"\n{'Par':<12} {'Carry':>8} {'Confiança':>12} {'R:R':>8} {'Recomendação':<20}")
    print("-" * 80)

    for analise in sorted(analises, key=lambda x: x.confianca, reverse=True):
        emoji_rec = "✅" if analise.confianca >= 70 else "⚠️ " if analise.confianca >= 50 else "❌"

        print(f"{analise.par:<12} {float(analise.diferencial_juros):>7.2f}%  " +
              f"{analise.confianca:>10}%  {analise.risco_recompensa:>7.2f}  " +
              f"{emoji_rec} {analise.recomendacao:<18}")

    # Melhor oportunidade é a primeira da lista (já ordenada por confiança)
    melhor = analises[0]

    print(f"\n{'='*80}")
    print(f"MELHOR OPORTUNIDADE: {melhor.par} - {melhor.recomendacao}")
    print(f"Confiança: {melhor.confianca}% | Carry: {float(melhor.diferencial_juros):.2f}%")
    print(f"{'='*80}\n")

    print(analisador.gerar_relatorio_formatado(melhor))


def main():
    """Função principal do CLI."""

    parser = argparse.ArgumentParser(
        description='Análise Forex - Oportunidades de Trading em Moedas',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='comando', help='Comando a executar')

    # Comando: analisar
    parser_analisar = subparsers.add_parser('analisar', help='Analisa par Forex específico')
    parser_analisar.add_argument('par', help='Par Forex (ex: GBPNZD, EURUSD)')
    parser_analisar.add_argument(
        '--operacao',
        choices=['COMPRA', 'VENDA'],
        default='COMPRA',
        help='Tipo de operação'
    )

    # Comando: carry-trades
    parser_carry = subparsers.add_parser('carry-trades', help='Lista melhores carry trades')
    parser_carry.add_argument(
        '--top',
        type=int,
        default=10,
        help='Número de carry trades a exibir'
    )

    # Comando: taxas
    parser_taxas = subparsers.add_parser('taxas', help='Mostra taxas dos bancos centrais')

    # Comando: comparar
    parser_comparar = subparsers.add_parser('comparar', help='Compara múltiplos pares')
    parser_comparar.add_argument(
        'pares',
        nargs='+',
        help='Lista de pares para comparar (ex: EURUSD GBPUSD USDJPY)'
    )
    parser_comparar.add_argument(
        '--operacao',
        choices=['COMPRA', 'VENDA'],
        default='COMPRA',
        help='Tipo de operação'
    )

    args = parser.parse_args()

    if not args.comando:
        parser.print_help()
        return

    # Executar comando
    if args.comando == 'analisar':
        cmd_analisar(args)
    elif args.comando == 'carry-trades':
        cmd_carry_trades(args)
    elif args.comando == 'taxas':
        cmd_taxas(args)
    elif args.comando == 'comparar':
        cmd_comparar(args)


if __name__ == "__main__":
    main()
