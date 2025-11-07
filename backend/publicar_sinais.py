# -*- coding: utf-8 -*-
"""
CLI - Publicar sinais a partir de relatórios JSON

Exemplos:
  python publicar_sinais.py forex .\relatorios_intraday\EURUSD_20251106_010000.json
  python publicar_sinais.py cripto .\relatorios_trading\BTCUSDT_20251106_010000.json

Saída: eventos gravados em backend/bus/*.json (com status de validação)
"""
import sys
import argparse
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / 'src'
sys.path.insert(0, str(SRC))

from sinais.emissor import signals_from_forex_report, signals_from_cripto_report, escrever_eventos
from schemas.validador import validar_contra_schema


def main():
    ap = argparse.ArgumentParser(description='Publicar sinais a partir de relatórios JSON (forex/cripto)')
    ap.add_argument('classe', choices=['forex', 'cripto'], help='Classe de ativo do relatório')
    ap.add_argument('arquivo', help='Caminho do JSON do relatório')
    args = ap.parse_args()

    rel_path = Path(args.arquivo)
    if not rel_path.exists():
        print(f"❌ Arquivo não encontrado: {rel_path}")
        return

    import json
    payload = json.loads(rel_path.read_text(encoding='utf-8'))

    # Gerar eventos
    if args.classe == 'forex':
        eventos = signals_from_forex_report(payload)
    else:
        eventos = signals_from_cripto_report(payload)

    # Validar cada evento e escrever no bus
    bus_dir = ROOT / 'bus'
    caminhos = escrever_eventos(eventos, bus_dir)

    print(f"✅ {len(eventos)} evento(s) publicados em: {bus_dir}")
    for c in caminhos:
        print(f"  - {c}")


if __name__ == '__main__':
    main()
