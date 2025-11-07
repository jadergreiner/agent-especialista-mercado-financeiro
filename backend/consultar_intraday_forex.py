# -*- coding: utf-8 -*-
"""
CLI - Relatório de Trading Intraday (Forex)
Comandos:
  analisar <PAR>          - Gera relatório completo (4–8h)
  monitorar <PARES...>    - Resumo de múltiplos pares
  oportunidades           - Scan automático de 6 pares principais

Exemplos:
  python consultar_intraday_forex.py analisar EURUSD
  python consultar_intraday_forex.py monitorar EURUSD GBPJPY USDJPY
  python consultar_intraday_forex.py oportunidades
"""

import sys
import argparse
from pathlib import Path
from typing import List

ROOT = Path(__file__).parent
SRC = ROOT / 'src'
sys.path.insert(0, str(SRC))

from dados.analisador_intraday_forex import AnalisadorIntradayForex, RelatorioIntradayForex
from schemas.validador import validar_contra_schema
from persistencia.sqlite_repo import inicializar as db_inicializar, salvar_relatorio_intraday


def cmd_analisar(par: str):
    # Garantir DB pronto
    db_inicializar()
    an = AnalisadorIntradayForex()
    print(f"\n{'='*80}\n⚡️ RELATÓRIO INTRADAY FOREX: {par}\n{'='*80}\n")
    r = an.analisar_par(par)
    if not r:
        print("❌ Falha na análise")
        return
    md = an.gerar_markdown(r)
    print(md)

    # Salvar
    out_dir = ROOT / 'relatorios_intraday'
    out_dir.mkdir(exist_ok=True)
    base = f"{par}_{r.timestamp.strftime('%Y%m%d_%H%M%S')}"
    fname_md = f"{base}.md"
    with open(out_dir / fname_md, 'w', encoding='utf-8') as f:
        f.write(md)
    print(f"\n✅ Relatório salvo em: {out_dir / fname_md}")

    # JSON (contrato report.intraday.v1)
    payload = an.gerar_json(r)
    ok, erros = validar_contra_schema(payload, 'report.intraday.v1')
    fname_json = f"{base}.json"
    with open(out_dir / fname_json, 'w', encoding='utf-8') as jf:
        import json
        json.dump(payload, jf, ensure_ascii=False, indent=2)
    status = 'PASS' if ok else 'FAIL'
    print(f"✅ JSON salvo em: {out_dir / fname_json} | Validação: {status}")
    if not ok:
        for e in erros[:10]:
            print(f"  - {e}")

    # Persistir em SQLite
    try:
        row_id = salvar_relatorio_intraday(payload)
        if row_id is not None:
            print(f"💾 Persistido em SQLite (id={row_id})")
        else:
            print("⚠️  Falha ao persistir em SQLite")
    except Exception as e:
        print(f"⚠️  Erro ao persistir em SQLite: {e}")


def _print_resumo(rs: List[RelatorioIntradayForex]):
    print("\n| PAR | OP | Viés | R/R | Entrada | Stop | Alvo 1 |")
    print("|:---:|:--:|:-----|:---:|-------:|------:|-------:|")
    for r in rs:
        emoji = '🟢' if r.operacao == 'COMPRA' else ('🔴' if r.operacao == 'VENDA' else '⚪')
        print(f"| {r.par} | {emoji} {r.operacao} | {r.vies_sessao} | {r.rr_texto} | "
              f"{float(r.preco_entrada):.5f} | {float(r.stop_loss):.5f} | {float(r.alvo_1):.5f} |")


def cmd_monitorar(pares: List[str]):
    an = AnalisadorIntradayForex()
    rels = []
    for p in pares:
        print(f"🔎 Analisando {p}...")
        r = an.analisar_par(p)
        if r:
            rels.append(r)
    if not rels:
        print("❌ Nenhum par analisado com sucesso")
        return
    print(f"\n{'='*80}\n📊 RESUMO INTRADAY\n{'='*80}")
    _print_resumo(rels)


def cmd_oportunidades():
    pares = ['EURUSD','GBPUSD','USDJPY','USDCHF','AUDUSD','USDCAD']
    cmd_monitorar(pares)


def main():
    ap = argparse.ArgumentParser(description='Intraday Forex - Relatório 4–8h')
    sub = ap.add_subparsers(dest='cmd')

    a = sub.add_parser('analisar', help='Gerar relatório para um par')
    a.add_argument('par')

    m = sub.add_parser('monitorar', help='Resumo para múltiplos pares')
    m.add_argument('pares', nargs='+')

    sub.add_parser('oportunidades', help='Scan automático de pares principais')

    args = ap.parse_args()
    if not args.cmd:
        ap.print_help()
        return
    if args.cmd == 'analisar':
        cmd_analisar(args.par)
    elif args.cmd == 'monitorar':
        cmd_monitorar(args.pares)
    elif args.cmd == 'oportunidades':
        cmd_oportunidades()


if __name__ == '__main__':
    main()
