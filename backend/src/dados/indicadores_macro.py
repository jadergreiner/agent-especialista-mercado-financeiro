# -*- coding: utf-8 -*-
"""
Indicadores macroeconômicos auxiliares.

Fornece funções resilientes para obtenção de variações do DXY com
fallback baseado em composição ponderada de pares principais de FX
quando o ticker ^DXY estiver indisponível no provedor primário.

Regras principais:
- Primeiro tenta baixar ^DXY (diário) via yfinance e calcula retorno simples
  do último fechamento contra o anterior.
- Em caso de indisponibilidade/qualidade ruim, calcula um proxy usando
  pesos do índice clássico (ICE US Dollar Index) aproximados e soma
  ponderada de retornos logarítmicos dos pares:
  EURUSD (57.6%), USDJPY (13.6%), GBPUSD (11.9%), USDCAD (9.1%),
  USDSEK (4.2%), USDCHF (3.6%).
- Ajusta o sinal conforme a posição do USD no par (USD como contra-moeda →
  retorno do USD é o negativo do retorno do par; USD como base → mesmo sinal).

Retorno: (variacao_decimal, qualidade)
  variacao_decimal: Decimal entre ~[-0.1, 0.1] representando retorno simples.
  qualidade: 'ok' | 'fallback' | 'indisponivel'
"""

from __future__ import annotations

from decimal import Decimal
from typing import Tuple

import pandas as pd
import numpy as np
import yfinance as yf


def _to_decimal_safe(x) -> Decimal:
    try:
        return Decimal(str(float(x)))
    except Exception:
        return Decimal('0')


def obter_dxy_resiliente() -> Tuple[Decimal, str]:
    """Obtém variação do DXY com fallback para proxy composto.

    Retorna (variacao, qualidade), onde qualidade ∈ {'ok','fallback','indisponivel'}
    """
    # 1) Fonte primária: ^DXY diário
    try:
        dxy = yf.download(tickers='^DXY', period='7d', interval='1d', auto_adjust=False, progress=False)
        closes = pd.to_numeric(getattr(dxy, 'Close', pd.Series([])), errors='coerce')
        closes = closes.dropna()
        if len(closes) >= 2:
            c1, c0 = _to_decimal_safe(closes.iloc[-1]), _to_decimal_safe(closes.iloc[-2])
            if c0 != 0:
                return (c1 - c0) / c0, 'ok'
    except Exception:
        pass

    # 2) Fallback: proxy ponderado por pares principais
    pesos = {
        'EURUSD=X': 0.576,
        'USDJPY=X': 0.136,
        'GBPUSD=X': 0.119,
        'USDCAD=X': 0.091,
        'USDSEK=X': 0.042,
        'USDCHF=X': 0.036,
    }
    tickers = list(pesos.keys())
    try:
        df = yf.download(tickers=tickers, period='7d', interval='1d', auto_adjust=False, progress=False)
        # yfinance com múltiplos retorna MultiIndex: (campo, ticker)
        if not isinstance(df.columns, pd.MultiIndex):
            # Normaliza para MultiIndex-like
            df = pd.concat({'Close': df['Close']}, axis=1)
        clos = df['Close'] if 'Close' in df.columns.get_level_values(0) else df.iloc[:, 0]
        # Checa disponibilidade mínima
        disp = 0
        r_logs = []
        for t in tickers:
            try:
                serie = pd.to_numeric(clos[t], errors='coerce').dropna()
                if len(serie) < 2:
                    continue
                r = np.log(serie.iloc[-1] / serie.iloc[-2])
                # Ajuste de sinal: USD contra (EURUSD, GBPUSD) → negativo
                if t in ( 'EURUSD=X', 'GBPUSD=X' ):
                    r = -r
                # USD base (USDJPY, USDCAD, USDCHF, USDSEK) → positivo
                r_logs.append((r, pesos[t]))
                disp += 1
            except Exception:
                continue
        if disp >= 3 and r_logs:
            r_w = sum(r * w for r, w in r_logs)
            r_simple = np.exp(r_w) - 1.0
            return _to_decimal_safe(r_simple), 'fallback'
    except Exception:
        pass

    # 3) Indisponível
    return Decimal('0'), 'indisponivel'
