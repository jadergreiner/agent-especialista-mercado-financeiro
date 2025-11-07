# -*- coding: utf-8 -*-
"""
CLI - Consultar Trading Cripto Individual
Relatório de trading focado para criptoativos

Comandos:
  analisar <PAR>       - Análise completa AF+AT+On-Chain
  monitorar <PARES>    - Monitorar múltiplos pares
  oportunidades        - Buscar melhores setups de entrada

Exemplos:
  python consultar_trading_cripto.py analisar BTCUSDT
  python consultar_trading_cripto.py monitorar BTCUSDT ETHUSDT SOLUSDT
  python consultar_trading_cripto.py oportunidades

Autor: Agent Especialista Mercado Financeiro
Data: 2025-01-05
"""

import sys
import argparse
from pathlib import Path
from typing import List

# Adicionar backend ao path
backend_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(backend_path))

from dados.analisador_trading_cripto import AnalisadorTradingCripto, RelatorioTrading
from schemas.validador import validar_contra_schema
from persistencia.sqlite_repo import inicializar as db_inicializar, salvar_relatorio_intraday


def comando_analisar(par: str):
    """Análise completa de trading para um par."""
    # Garantir DB pronto
    db_inicializar()
    analisador = AnalisadorTradingCripto()

    print(f"\n{'='*80}")
    print(f"🎯 ANÁLISE DE TRADING: {par}")
    print(f"{'='*80}\n")

    relatorio = analisador.analisar_trading(par)

    if relatorio:
        print(analisador.gerar_relatorio_markdown(relatorio))

        # Salvar em arquivo
        output_dir = Path(__file__).parent / 'relatorios_trading'
        output_dir.mkdir(exist_ok=True)

        base = f"{par}_{relatorio.timestamp.strftime('%Y%m%d_%H%M%S')}"
        output_path = output_dir / f"{base}.md"

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(analisador.gerar_relatorio_markdown(relatorio))

        print(f"\n✅ Relatório salvo em: {output_path}")

        # JSON + validação
        payload = analisador.gerar_json(relatorio)
        ok, erros = validar_contra_schema(payload, 'report.trading.cripto.v1')
        json_path = output_dir / f"{base}.json"
        try:
            import json
            with open(json_path, 'w', encoding='utf-8') as jf:
                json.dump(payload, jf, ensure_ascii=False, indent=2)
            status = 'PASS' if ok else 'FAIL'
            print(f"✅ JSON salvo em: {json_path} | Validação: {status}")
            if not ok:
                for e in erros[:10]:
                    print(f"  - {e}")
        except Exception as e:
            print(f"⚠️  Falha ao salvar JSON: {e}")

        # Persistir em SQLite
        try:
            row_id = salvar_relatorio_intraday(payload)
            if row_id is not None:
                print(f"💾 Persistido em SQLite (id={row_id})")
            else:
                print("⚠️  Falha ao persistir em SQLite")
        except Exception as e:
            print(f"⚠️  Erro ao persistir em SQLite: {e}")
    else:
        print(f"\n❌ Falha ao analisar {par}")


def comando_monitorar(pares: List[str]):
    """Monitora múltiplos pares e gera resumo consolidado."""
    analisador = AnalisadorTradingCripto()

    print(f"\n{'='*80}")
    print(f"📊 MONITORAMENTO DE PARES DE TRADING")
    print(f"{'='*80}\n")
    print(f"Analisando {len(pares)} pares...\n")

    relatorios = []
    for par in pares:
        print(f"🔍 Analisando {par}...")
        relatorio = analisador.analisar_trading(par)
        if relatorio:
            relatorios.append(relatorio)

    if not relatorios:
        print("\n❌ Nenhum par foi analisado com sucesso")
        return

    # Tabela consolidada
    print(f"\n{'='*80}")
    print("📊 RESUMO DE OPORTUNIDADES")
    print(f"{'='*80}\n")

    print("| PAR | OPERAÇÃO | MOMENTUM | R/R | ENTRADA | STOP | ALVO 2 |")
    print("|:---:|:--------:|:--------:|:---:|--------:|-----:|-------:|")

    for r in relatorios:
        emoji_op = "🟢" if r.operacao == "COMPRA" else "🔴" if r.operacao == "VENDA" else "⚪"
        print(f"| {r.simbolo} | {emoji_op} {r.operacao} | {r.momentum_consolidado[:30]}... | "
              f"{r.risco_recompensa} | ${float(r.preco_entrada):,.2f} | "
              f"${float(r.stop_loss):,.2f} | ${float(r.alvo_2):,.2f} |")

    # Estatísticas
    compras = sum(1 for r in relatorios if r.operacao == "COMPRA")
    vendas = sum(1 for r in relatorios if r.operacao == "VENDA")
    aguardar = sum(1 for r in relatorios if r.operacao == "AGUARDAR")

    print(f"\n📈 **Operações Recomendadas:**")
    print(f"  - COMPRA: {compras}")
    print(f"  - VENDA: {vendas}")
    print(f"  - AGUARDAR: {aguardar}")

    # Melhores oportunidades
    if compras > 0:
        melhores_compras = [r for r in relatorios if r.operacao == "COMPRA"]
        melhores_compras.sort(
            key=lambda r: (
                1 if r.momentum_fundamental == "ALTISTA" else 0,
                1 if r.momentum_tecnico == "ALTISTA" else 0,
                1 if r.netflow_exchanges == "OUTFLOW" else 0,
            ),
            reverse=True
        )

        print(f"\n🎯 **Melhor Oportunidade de COMPRA:** {melhores_compras[0].simbolo}")
        print(f"   - Momentum: {melhores_compras[0].momentum_consolidado}")
        print(f"   - R/R: {melhores_compras[0].risco_recompensa}")
        print(f"   - Entrada: ${float(melhores_compras[0].preco_entrada):,.2f}")


def comando_oportunidades():
    """Busca automaticamente melhores setups em pares principais."""
    pares_principais = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'ADAUSDT']

    print(f"\n{'='*80}")
    print("🔎 BUSCA AUTOMÁTICA DE OPORTUNIDADES")
    print(f"{'='*80}\n")
    print(f"Analisando {len(pares_principais)} pares principais...\n")

    comando_monitorar(pares_principais)


def main():
    parser = argparse.ArgumentParser(
        description='CLI para análise de trading de criptoativos',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

  Analisar um par específico:
    python consultar_trading_cripto.py analisar BTCUSDT

  Monitorar múltiplos pares:
    python consultar_trading_cripto.py monitorar BTCUSDT ETHUSDT SOLUSDT

  Buscar oportunidades automaticamente:
    python consultar_trading_cripto.py oportunidades

Pares disponíveis:
  BTCUSDT, ETHUSDT, SOLUSDT, BNBUSDT, ADAUSDT, DOTUSDT,
  AVAXUSDT, LINKUSDT, MATICUSDT, NEARUSDT
        """
    )

    subparsers = parser.add_subparsers(dest='comando', help='Comando a executar')

    # Comando: analisar
    parser_analisar = subparsers.add_parser(
        'analisar',
        help='Análise completa de trading para um par'
    )
    parser_analisar.add_argument(
        'par',
        help='Par de trading (ex: BTCUSDT)'
    )

    # Comando: monitorar
    parser_monitorar = subparsers.add_parser(
        'monitorar',
        help='Monitorar múltiplos pares'
    )
    parser_monitorar.add_argument(
        'pares',
        nargs='+',
        help='Lista de pares (ex: BTCUSDT ETHUSDT)'
    )

    # Comando: oportunidades
    parser_oportunidades = subparsers.add_parser(
        'oportunidades',
        help='Buscar melhores setups automaticamente'
    )

    args = parser.parse_args()

    if not args.comando:
        parser.print_help()
        return

    try:
        if args.comando == 'analisar':
            comando_analisar(args.par)
        elif args.comando == 'monitorar':
            comando_monitorar(args.pares)
        elif args.comando == 'oportunidades':
            comando_oportunidades()
    except KeyboardInterrupt:
        print("\n\n⚠️  Operação cancelada pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
