"""
CLI para executar backtesting de estratégias de trading.

Uso:
  python src/cli_backtest.py executar --estrategia cruzamento_medias --periodo 2024
  python src/cli_backtest.py executar --estrategia cruzamento_medias --inicio 2020-01-01 --fim 2023-12-31
  python src/cli_backtest.py listar-estrategias
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Garantir que possamos importar módulos do projeto
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.backtest.motor_backtest import (
    BacktestEngine,
    EstrategiaCruzamentoMedias,
    EstrategiaRSI,
    EstrategiaBollinger,
    EstrategiaMACD,
)
from src.backtest.estrategias_avancadas import (
    EstrategiaEnsemble,
    EstrategiaMultiIndicador,
)


def cmd_executar_backtest(args: argparse.Namespace) -> None:
    """Executa backtest de uma estratégia."""

    # Criar estratégia
    if args.estrategia == 'cruzamento_medias':
        estrategia = EstrategiaCruzamentoMedias(
            periodo_curto=args.ma_curta,
            periodo_longo=args.ma_longa
        )
    elif args.estrategia == 'rsi':
        estrategia = EstrategiaRSI(
            periodo_rsi=args.rsi_periodo,
            nivel_sobrecompra=args.rsi_sobrecompra,
            nivel_sobrevenda=args.rsi_sobrevenda
        )
    elif args.estrategia == 'bollinger':
        estrategia = EstrategiaBollinger(
            periodo=args.bb_periodo,
            num_desvios=args.bb_desvios
        )
    elif args.estrategia == 'macd':
        estrategia = EstrategiaMACD(
            rapida=args.macd_rapida,
            lenta=args.macd_lenta,
            sinal=args.macd_sinal
        )
    elif args.estrategia == 'ensemble':
        estrategia = EstrategiaEnsemble(
            usar_ma=not args.ensemble_sem_ma,
            usar_rsi=not args.ensemble_sem_rsi,
            usar_bollinger=not args.ensemble_sem_bollinger,
            usar_macd=not args.ensemble_sem_macd,
            peso_ma=args.ensemble_peso_ma,
            peso_rsi=args.ensemble_peso_rsi,
            peso_bollinger=args.ensemble_peso_bollinger,
            peso_macd=args.ensemble_peso_macd,
            limiar_consenso=args.ensemble_limiar
        )
    elif args.estrategia == 'ensemble_optimized':
        # Preset otimizado: limiar 0.55 com pesos ajustados (grid 2024)
        estrategia = EstrategiaEnsemble(
            peso_ma=1.1,
            peso_rsi=1.0,
            peso_bollinger=0.8,
            peso_macd=0.6,
            limiar_consenso=0.55
        )
    elif args.estrategia == 'multi_indicador':
        estrategia = EstrategiaMultiIndicador(
            periodo_ma_curta=args.mi_ma_curta,
            periodo_ma_longa=args.mi_ma_longa,
            periodo_rsi=args.mi_rsi_periodo,
            rsi_sobrecompra=args.mi_rsi_sobrecompra,
            rsi_sobrevenda=args.mi_rsi_sobrevenda,
        )
    else:
        print(f"❌ Estratégia '{args.estrategia}' não reconhecida.")
        print("Use: python src/cli_backtest.py listar-estrategias")
        return

    # Determinar período
    if args.periodo:
        # Período predefinido por ano
        data_inicio = f"{args.periodo}-01-01"
        data_fim = f"{args.periodo}-12-31"
    else:
        data_inicio = args.inicio
        data_fim = args.fim

    # Executar backtest
    engine = BacktestEngine()
    resultado = engine.executar_backtest(
        estrategia=estrategia,
        instrumento=args.instrumento,
        data_inicio=data_inicio,
        data_fim=data_fim,
        salvar_recomendacoes=not args.dry_run
    )

    if args.dry_run:
        print(f"\n💡 Modo DRY RUN: Nenhuma recomendação foi salva no banco.")


def cmd_listar_estrategias(args: argparse.Namespace) -> None:
    """Lista estratégias disponíveis."""
    print("\nESTRATEGIAS DISPONIVEIS:")
    print("=" * 80)

    print("\n1. cruzamento_medias")
    print("   Descrição: Cruzamento de médias móveis simples")
    print("   Parâmetros:")
    print("     --ma-curta: Período da média móvel curta (padrão: 9)")
    print("     --ma-longa: Período da média móvel longa (padrão: 21)")
    print("   Sinais:")
    print("     - COMPRA: Quando MA curta cruza acima da MA longa")
    print("     - VENDA: Quando MA curta cruza abaixo da MA longa")
    print("   Confirmação: RSI (evita sobrecompra/sobrevenda)")

    print("\n2. rsi")
    print("   Descrição: Índice de Força Relativa - sobrecompra/sobrevenda")
    print("   Parâmetros:")
    print("     --rsi-periodo: Período do RSI (padrão: 14)")
    print("     --rsi-sobrecompra: Nível de sobrecompra (padrão: 70)")
    print("     --rsi-sobrevenda: Nível de sobrevenda (padrão: 30)")
    print("   Sinais:")
    print("     - COMPRA: RSI sai de sobrevenda (cruza acima de 30)")
    print("     - VENDA: RSI sai de sobrecompra (cruza abaixo de 70)")
    print("   Confirmação: ATR para stops")

    print("\n3. bollinger")
    print("   Descrição: Bandas de Bollinger - reversão à média")
    print("   Parâmetros:")
    print("     --bb-periodo: Período das bandas (padrão: 20)")
    print("     --bb-desvios: Número de desvios padrão (padrão: 2.0)")
    print("   Sinais:")
    print("     - COMPRA: Preço toca banda inferior (+ RSI < 40)")
    print("     - VENDA: Preço toca banda superior (+ RSI > 60)")
    print("   Objetivo: Retorno à banda média")

    print("\n4. macd")
    print("   Descrição: MACD - convergência/divergência de médias")
    print("   Parâmetros:")
    print("     --macd-rapida: Período da EMA rápida (padrão: 12)")
    print("     --macd-lenta: Período da EMA lenta (padrão: 26)")
    print("     --macd-sinal: Período da linha de sinal (padrão: 9)")
    print("   Sinais:")
    print("     - COMPRA: MACD cruza acima da linha de sinal")
    print("     - VENDA: MACD cruza abaixo da linha de sinal")
    print("   Confirmação: Histograma (força do sinal)")

    print("\n5. ensemble")
    print("   Descrição: Combinação ponderada de MA/RSI/Bollinger/MACD com consenso")
    print("   Parâmetros:")
    print("     --ensemble-sem-ma/--ensemble-sem-rsi/--ensemble-sem-bollinger/--ensemble-sem-macd: Excluir componentes")
    print("     --ensemble-peso-ma/--ensemble-peso-rsi/--ensemble-peso-bollinger/--ensemble-peso-macd: Pesos (0-1)")
    print("     --ensemble-limiar: Limiar de consenso (padrão: 0.6)")
    print("   Sinais:")
    print("     - COMPRA/VENDA quando consenso ponderado ≥ limiar")

    print("\n6. ensemble_optimized")
    print("   Descrição: Ensemble com parâmetros otimizados via grid search em 2024")
    print("   Parâmetros: fixos (wMA=1.1, wRSI=1.0, wBB=0.8, wMACD=0.6, consenso=55%)")
    print("   Performance (2024): Expectativa +60.5 pts/op | Taxa acerto 53.8% | PnL +2360 pts")
    print("   Uso: Sem parâmetros adicionais (preset completo)")

    print("\n7. multi_indicador")
    print("   Descrição: Sinais somente quando MA e RSI confirmam em conjunto")
    print("   Parâmetros:")
    print("     --mi-ma-curta/--mi-ma-longa: Períodos das MMs (padrão: 9/21)")
    print("     --mi-rsi-periodo: Período do RSI (padrão: 14)")
    print("     --mi-rsi-sobrecompra/--mi-rsi-sobrevenda: Níveis (padrão: 70/30)")
    print("   Sinais:")
    print("     - COMPRA: Cruzamento de alta + RSI não sobrecomprado + preço próximo da média BB")
    print("     - VENDA: Cruzamento de baixa + RSI não sobrevendido + preço próximo da média BB")

    print("\n" + "=" * 80)
    print("Exemplos de uso:")
    print("   python src/cli_backtest.py executar --estrategia cruzamento_medias --periodo 2024")
    print("   python src/cli_backtest.py executar --estrategia rsi --periodo 2024 --rsi-periodo 14")
    print("   python src/cli_backtest.py executar --estrategia bollinger --inicio 2023-01-01 --fim 2023-12-31")
    print("   python src/cli_backtest.py executar --estrategia macd --periodo 2024 --macd-rapida 12 --macd-lenta 26")
    print("   python src/cli_backtest.py executar --estrategia ensemble_optimized --periodo 2024")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description='CLI para backtesting de estratégias de trading',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = p.add_subparsers(dest='cmd')

    # Comando: executar
    p_exec = sub.add_parser('executar', help='Executar backtest de uma estratégia')
    p_exec.add_argument(
        '--estrategia',
        type=str,
        default='cruzamento_medias',
        choices=['cruzamento_medias', 'rsi', 'bollinger', 'macd', 'ensemble', 'ensemble_optimized', 'multi_indicador'],
        help='Nome da estratégia a testar (padrão: cruzamento_medias)'
    )
    p_exec.add_argument(
        '--instrumento',
        type=str,
        default='WIN',
        help='Instrumento a analisar (padrão: WIN)'
    )
    p_exec.add_argument(
        '--periodo',
        type=str,
        help='Ano para backtest (ex: 2024). Alternativa a --inicio/--fim'
    )
    p_exec.add_argument(
        '--inicio',
        type=str,
        help='Data de início (YYYY-MM-DD). Usar com --fim'
    )
    p_exec.add_argument(
        '--fim',
        type=str,
        help='Data de fim (YYYY-MM-DD). Usar com --inicio'
    )
    p_exec.add_argument(
        '--ma-curta',
        type=int,
        default=9,
        help='Período da média móvel curta (padrão: 9)'
    )
    p_exec.add_argument(
        '--ma-longa',
        type=int,
        default=21,
        help='Período da média móvel longa (padrão: 21)'
    )

    # Parâmetros para estratégia RSI
    p_exec.add_argument(
        '--rsi-periodo',
        type=int,
        default=14,
        help='Período do RSI (padrão: 14)'
    )
    p_exec.add_argument(
        '--rsi-sobrecompra',
        type=float,
        default=70,
        help='Nível de sobrecompra do RSI (padrão: 70)'
    )
    p_exec.add_argument(
        '--rsi-sobrevenda',
        type=float,
        default=30,
        help='Nível de sobrevenda do RSI (padrão: 30)'
    )

    # Parâmetros para estratégia Bollinger
    p_exec.add_argument(
        '--bb-periodo',
        type=int,
        default=20,
        help='Período das Bandas de Bollinger (padrão: 20)'
    )
    p_exec.add_argument(
        '--bb-desvios',
        type=float,
        default=2.0,
        help='Número de desvios padrão (padrão: 2.0)'
    )

    # Parâmetros para estratégia MACD
    p_exec.add_argument(
        '--macd-rapida',
        type=int,
        default=12,
        help='Período da EMA rápida do MACD (padrão: 12)'
    )
    p_exec.add_argument(
        '--macd-lenta',
        type=int,
        default=26,
        help='Período da EMA lenta do MACD (padrão: 26)'
    )
    p_exec.add_argument(
        '--macd-sinal',
        type=int,
        default=9,
        help='Período da linha de sinal do MACD (padrão: 9)'
    )

    # Parâmetros para estratégia ENSEMBLE
    p_exec.add_argument('--ensemble-sem-ma', action='store_true', help='Não incluir componente MA no ensemble')
    p_exec.add_argument('--ensemble-sem-rsi', action='store_true', help='Não incluir componente RSI no ensemble')
    p_exec.add_argument('--ensemble-sem-bollinger', action='store_true', help='Não incluir componente Bollinger no ensemble')
    p_exec.add_argument('--ensemble-sem-macd', action='store_true', help='Não incluir componente MACD no ensemble')
    p_exec.add_argument('--ensemble-peso-ma', type=float, default=1.0, help='Peso do componente MA (padrão: 1.0)')
    p_exec.add_argument('--ensemble-peso-rsi', type=float, default=1.0, help='Peso do componente RSI (padrão: 1.0)')
    p_exec.add_argument('--ensemble-peso-bollinger', type=float, default=0.8, help='Peso do componente Bollinger (padrão: 0.8)')
    p_exec.add_argument('--ensemble-peso-macd', type=float, default=0.7, help='Peso do componente MACD (padrão: 0.7)')
    p_exec.add_argument('--ensemble-limiar', type=float, default=0.6, help='Limiar de consenso (padrão: 0.6)')

    # Parâmetros para estratégia MULTI-INDICADOR
    p_exec.add_argument('--mi-ma-curta', type=int, default=9, help='Período da média móvel curta (padrão: 9)')
    p_exec.add_argument('--mi-ma-longa', type=int, default=21, help='Período da média móvel longa (padrão: 21)')
    p_exec.add_argument('--mi-rsi-periodo', type=int, default=14, help='Período do RSI (padrão: 14)')
    p_exec.add_argument('--mi-rsi-sobrecompra', type=float, default=70, help='Nível de sobrecompra do RSI (padrão: 70)')
    p_exec.add_argument('--mi-rsi-sobrevenda', type=float, default=30, help='Nível de sobrevenda do RSI (padrão: 30)')

    p_exec.add_argument(
        '--dry-run',
        action='store_true',
        help='Não salvar recomendações no banco (apenas simular)'
    )
    p_exec.set_defaults(func=cmd_executar_backtest)

    # Comando: listar-estrategias
    p_list = sub.add_parser('listar-estrategias', help='Listar estratégias disponíveis')
    p_list.set_defaults(func=cmd_listar_estrategias)

    return p


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if not hasattr(args, 'func'):
        parser.print_help()
        return

    # Validações
    if args.cmd == 'executar':
        if not args.periodo and (not args.inicio or not args.fim):
            print("❌ Erro: Especifique --periodo OU --inicio/--fim")
            parser.print_help()
            return

        if args.periodo and (args.inicio or args.fim):
            print("❌ Erro: Use --periodo OU --inicio/--fim, não ambos")
            parser.print_help()
            return

    args.func(args)


if __name__ == '__main__':
    main()
