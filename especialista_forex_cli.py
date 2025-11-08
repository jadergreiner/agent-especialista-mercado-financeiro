# -*- coding: utf-8 -*-
"""
CLI para Especialista de Investimento Internacional - Forex

Uso:
    python especialista_forex_cli.py EURUSD=X --horizonte dias
    python especialista_forex_cli.py GBPUSD=X --horizonte semanas
"""

import sys
import argparse
from pathlib import Path

# Adicionar backend ao path
sys.path.insert(0, str(Path(__file__).parent))

from backend.especialista_investimento_forex import EspecialistaInvestimentoForex


def main():
    """Função principal da CLI"""
    parser = argparse.ArgumentParser(
        description='Especialista de Investimento Internacional - Análise Forex',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python especialista_forex_cli.py EURUSD=X
  python especialista_forex_cli.py GBPUSD=X --horizonte semanas
  python especialista_forex_cli.py USDJPY=X --horizonte dias

Pares Forex suportados:
  EURUSD=X, GBPUSD=X, USDJPY=X, USDCAD=X, USDCHF=X
  AUDUSD=X, NZDUSD=X, USDMXN=X, USDZAR=X, USDBRL=X
        """
    )

    parser.add_argument(
        'simbolo',
        help='Par Forex para análise (ex: EURUSD=X)'
    )

    parser.add_argument(
        '--horizonte',
        choices=['dias', 'semanas'],
        default='dias',
        help='Horizonte da análise (padrão: dias)'
    )

    parser.add_argument(
        '--json',
        action='store_true',
        help='Saída em formato JSON em vez de relatório formatado'
    )

    args = parser.parse_args()

    # Validar par Forex
    pares_validos = [
        'EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'USDCAD=X', 'USDCHF=X',
        'AUDUSD=X', 'NZDUSD=X', 'USDMXN=X', 'USDZAR=X', 'USDBRL=X'
    ]

    if args.simbolo not in pares_validos:
        print(f"❌ Par Forex inválido: {args.simbolo}")
        print("Pares válidos:", ', '.join(pares_validos))
        return 1

    try:
        # Executar análise
        especialista = EspecialistaInvestimentoForex()

        print(f"🔍 Iniciando análise especialista para {args.simbolo}...")
        print(f"⏱️ Horizonte: {args.horizonte}")
        print("-" * 60)

        analise = especialista.analisar_oportunidade_forex(args.simbolo, args.horizonte)

        if args.json:
            # Saída JSON
            import json
            print(json.dumps(analise, indent=2, default=str, ensure_ascii=False))
        else:
            # Saída formatada
            relatorio = especialista.gerar_relatorio_formatado(analise)
            print(relatorio)

        return 0

    except KeyboardInterrupt:
        print("\n⚠️ Análise interrompida pelo usuário")
        return 1
    except Exception as e:
        print(f"❌ Erro durante análise: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())