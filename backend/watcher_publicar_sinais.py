# -*- coding: utf-8 -*-
"""
Watcher de relatórios → publicação automática de sinais no bus

Funciona para Forex e Cripto:
- Observa as pastas de relatórios JSON e, quando um novo arquivo aparece,
  emite sinais via contratos (signal.tech.v1, signal.macroflow.v1) dentro de
  backend/bus/.
- Evita duplicar processamento mantendo um pequeno estado em
  backend/data/watcher_state.json.

Uso (PowerShell):
  python .\watcher_publicar_sinais.py           # observa em tempo real
  python .\watcher_publicar_sinais.py --backfill  # processa arquivos existentes e encerra
  python .\watcher_publicar_sinais.py --reset-state  # limpa estado e reprocessa tudo

Requisitos: watchdog (opcional). Se não estiver instalado, usa polling simples.
"""
from __future__ import annotations

import json
import sys
import time
import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Set, List

ROOT = Path(__file__).parent
SRC = ROOT / 'src'
sys.path.insert(0, str(SRC))

from sinais.emissor import (
    signals_from_forex_report,
    signals_from_cripto_report,
    escrever_eventos,
)


DATA_DIR = ROOT / 'data'
STATE_FILE = DATA_DIR / 'watcher_state.json'
REL_FX = ROOT / 'relatorios_intraday'
REL_CR = ROOT / 'relatorios_trading'
BUS_DIR = ROOT / 'bus'


def _load_state() -> Dict[str, bool]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not STATE_FILE.exists():
        return {}
    try:
        return json.loads(STATE_FILE.read_text(encoding='utf-8'))
    except Exception:
        return {}


def _save_state(state: Dict[str, bool]) -> None:
    try:
        STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')
    except Exception as e:
        print(f"⚠️  Falha ao salvar estado: {e}")


def _is_report_file(p: Path) -> bool:
    return p.suffix.lower() == '.json' and p.is_file()


def _process_file(path: Path, classe: str) -> bool:
    try:
        payload = json.loads(path.read_text(encoding='utf-8'))
        if classe == 'forex':
            eventos = signals_from_forex_report(payload)
        else:
            eventos = signals_from_cripto_report(payload)
        escrever_eventos(eventos, BUS_DIR)
        print(f"✅ Publicados {len(eventos)} eventos para {classe} a partir de: {path.name}")
        return True
    except Exception as e:
        print(f"❌ Erro ao processar {path}: {e}")
        return False


def _scan_and_process(state: Dict[str, bool], limit_per_dir: int | None = None) -> int:
    processed = 0
    # Forex
    if REL_FX.exists():
        files_fx = sorted([p for p in REL_FX.glob('*.json') if _is_report_file(p)], key=lambda x: x.stat().st_mtime)
        if limit_per_dir:
            files_fx = files_fx[-limit_per_dir:]
        for p in files_fx:
            k = str(p.resolve())
            if not state.get(k):
                ok = _process_file(p, 'forex')
                if ok:
                    state[k] = True
                    processed += 1
    # Cripto
    if REL_CR.exists():
        files_cr = sorted([p for p in REL_CR.glob('*.json') if _is_report_file(p)], key=lambda x: x.stat().st_mtime)
        if limit_per_dir:
            files_cr = files_cr[-limit_per_dir:]
        for p in files_cr:
            k = str(p.resolve())
            if not state.get(k):
                ok = _process_file(p, 'cripto')
                if ok:
                    state[k] = True
                    processed += 1
    return processed


def _watch_loop_polling(state: Dict[str, bool], interval_sec: float = 2.0) -> None:
    print("👀 Watcher iniciado em modo polling...")
    try:
        while True:
            cnt = _scan_and_process(state)
            if cnt:
                _save_state(state)
            time.sleep(interval_sec)
    except KeyboardInterrupt:
        print("\n👋 Encerrando watcher...")


def main():
    ap = argparse.ArgumentParser(description='Watcher automático para publicar sinais a partir de relatórios JSON (forex/cripto).')
    ap.add_argument('--backfill', action='store_true', help='Processa arquivos existentes e encerra')
    ap.add_argument('--reset-state', action='store_true', help='Reseta o estado e reprocessa tudo')
    ap.add_argument('--limit', type=int, default=200, help='Limita backfill aos N arquivos mais recentes por pasta (padrão=200)')
    args = ap.parse_args()

    state = {} if args.reset_state else _load_state()

    if args.backfill:
        print("🔁 Backfill inicial...")
        n = _scan_and_process(state, limit_per_dir=args.limit)
        _save_state(state)
        print(f"✅ Backfill concluído. Arquivos processados: {n}")
        return

    # Modo watch (polling simples por default para evitar dependências)
    _watch_loop_polling(state)


if __name__ == '__main__':
    main()
