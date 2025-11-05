"""
CLI de Avaliação de Recomendações

Permite:
- Listar recomendações pendentes de validação
- Registrar resultado manual (executada/cancelada/expirada)
- Calcular métricas básicas (últimos N dias)
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

from persistencia.recomendacoes import (
    inicializar_banco,
    listar_pendentes,
    registrar_resultado,
    calcular_metricas_basicas,
)
from avaliacao.validador_automatico import validar_pendentes


def cmd_listar(args: argparse.Namespace) -> None:
    inicializar_banco()
    pendentes = listar_pendentes()
    if not pendentes:
        print("\n✅ Nenhuma recomendação pendente de validação.")
        return

    print("\n📋 Recomendações Pendentes (máx 100):\n")
    for r in pendentes:
        print(f"- id={r['id']} | {r['timestamp']} | {r['instrumento']} | {r['direcao']} | "
              f"Entrada: {r['preco_entrada']:,.2f} | Conf.: {r['confianca']}/10 | ".replace(',', '.') +
              f"Saldo: {r['saldo_macro']} | Válido até: {r['valido_ate']}")


def cmd_resultado(args: argparse.Namespace) -> None:
    inicializar_banco()
    status = args.status
    acertou = None
    if status == 'executada':
        if args.acertou is None:
            print("❌ Para 'executada', informe --acertou 1|0")
            return
        acertou = (args.acertou == 1)

    registrar_resultado(
        id_recomendacao=args.id,
        status=status,
        acertou=acertou,
        preco_saida=args.preco_saida,
        pnl_pontos=args.pnl_pontos,
        pnl_reais=args.pnl_reais,
        motivo_saida=args.motivo,
        observacoes=args.obs,
    )
    print("\n✅ Resultado registrado com sucesso.")


def cmd_metricas(args: argparse.Namespace) -> None:
    inicializar_banco()
    m = calcular_metricas_basicas(dias=args.dias)
    print("\n📈 Métricas Básicas")
    print(f"Período: {m['periodo_dias']} dias")
    print(f"Total resultados: {m['total_resultados']}")
    print(f"Executadas: {m['executadas']} | Canceladas/Expiradas: {m['canceladas_ou_expiradas']}")
    if m['executadas']:
        print(f"Acurácia: {m['acuracia']*100:.1f}%")
        if m['profit_factor'] is not None:
            print(f"Profit Factor: {m['profit_factor']:.2f}")
        print(f"PNL total (R$): {m['pnl_total_reais'] or 0.0:.2f}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="CLI de Avaliação de Recomendações")
    sub = p.add_subparsers(dest='cmd', required=True)

    p_list = sub.add_parser('listar', help='Listar recomendações pendentes')
    p_list.set_defaults(func=cmd_listar)

    p_res = sub.add_parser('resultado', help='Registrar resultado para uma recomendação')
    p_res.add_argument('--id', type=int, required=True, help='ID da recomendação')
    p_res.add_argument('--status', choices=['executada', 'cancelada', 'expirada'], required=True)
    p_res.add_argument('--acertou', type=int, choices=[0,1], help='1=acertou (TP), 0=errou (STOP)')
    p_res.add_argument('--preco-saida', dest='preco_saida', type=float)
    p_res.add_argument('--pnl-pontos', dest='pnl_pontos', type=float)
    p_res.add_argument('--pnl-reais', dest='pnl_reais', type=float)
    p_res.add_argument('--motivo', type=str, help='tp1|tp2|tp3|stop|tempo|manual')
    p_res.add_argument('--obs', type=str, help='observações livres')
    p_res.set_defaults(func=cmd_resultado)

    p_met = sub.add_parser('metricas', help='Calcular métricas básicas (últimos N dias)')
    p_met.add_argument('--dias', type=int, default=30)
    p_met.set_defaults(func=cmd_metricas)

    p_auto = sub.add_parser('auto', help='Executar validação automática das pendentes')
    def _cmd_auto(args: argparse.Namespace) -> None:
        ids = validar_pendentes()
        if ids:
            print(f"\n✅ Validação automática concluída. {len(ids)} recomendações atualizadas.")
    p_auto.set_defaults(func=_cmd_auto)

    return p


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == '__main__':
    main()
