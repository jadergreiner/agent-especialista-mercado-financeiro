# -*- coding: utf-8 -*-
"""
Calendário macroeconômico (abstração de provedores + cache local).

Objetivo: fornecer uma interface simples para obter eventos do dia
por par/moedas, com sinalização de qualidade da fonte.

Implementação atual:
- Tenta carregar cache local em backend/data/calendario/hoje.json
  com estrutura: { "YYYY-MM-DD": { "USD": ["CPI"...], "EUR": ["PMI"...] } }
- Se não existir ou estiver vazio, retorna eventos mock herdados
  e qualidade='mock'.

Futuro:
- Providers reais (ForexFactory/Investing) com backoff, rate-limit, e
  refresh de cache.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Tuple


def _pasta_backend() -> Path:
    # este arquivo: backend/src/dados/calendario_macro.py → parents[2] = backend/
    return Path(__file__).resolve().parents[2]


def _carregar_cache(chave: str) -> Tuple[dict, str]:
    """Carrega cache do dia a partir de dois caminhos possíveis:
    - hoje.json (dinâmico)
    - YYYY-MM-DD.json (datado)

    Retorna (conteudo, qualidade_hint), onde qualidade_hint='ok' quando arquivo
    existe e está dentro do TTL, caso contrário ''.
    """
    base = _pasta_backend() / 'data' / 'calendario'
    ttl_horas = 24
    candidatos = [
        base / 'hoje.json',
        base / f'{chave}.json',
    ]
    agora = datetime.utcnow()
    for caminho in candidatos:
        try:
            if not caminho.exists():
                continue
            mtime = datetime.utcfromtimestamp(caminho.stat().st_mtime)
            if (agora - mtime) > timedelta(hours=ttl_horas):
                # expirado
                continue
            with open(caminho, 'r', encoding='utf-8') as f:
                return json.load(f), 'ok'
        except Exception:
            continue
    return {}, ''


def eventos_do_dia(par: str, data: datetime | None = None) -> Tuple[List[str], str]:
    """
    Retorna (eventos, qualidade).
    qualidade: 'ok' quando veio do cache/real; 'mock' quando heurística.
    """
    par = (par or '').upper().strip()
    base, contra = par[:3], par[3:6]
    data = data or datetime.utcnow()
    chave = data.strftime('%Y-%m-%d')

    cache, qualidade_hint = _carregar_cache(chave)
    try:
        dia = cache.get(chave, {})
        ev = []
        for moeda in (base, contra):
            itens = dia.get(moeda, [])
            for e in itens:
                if isinstance(e, str):
                    ev.append(f"{moeda}: {e}")
        if ev:
            return ev, (qualidade_hint or 'ok')
    except Exception:
        pass

    # Mock/heurística (mesma usada anteriormente)
    criticos = {
        'USD': ['Discurso do Presidente do Fed', 'Pedidos Iniciais de Seguro-Desemprego'],
        'EUR': ['Discurso BCE', 'PMI Zona do Euro'],
        'GBP': ['BoE Minutes', 'PMI Manufactura UK'],
        'JPY': ['BoJ Outlook', 'Dados de Salários'],
        'CHF': ['SNB Statement', 'CPI Suíça'],
        'CAD': ['Dados de Emprego Canadá', 'Balança Comercial'],
        'AUD': ['RBA Statement', 'Dados de Varejo'],
        'NZD': ['RBNZ Rate Statement', 'Inflação trimestral'],
    }
    eventos = []
    for m in (base, contra):
        if m in criticos:
            eventos.append(f"{m}: {criticos[m][0]}")
    if not eventos:
        eventos = ['Sem eventos críticos mapeados (mock)']
    return eventos, 'mock'
