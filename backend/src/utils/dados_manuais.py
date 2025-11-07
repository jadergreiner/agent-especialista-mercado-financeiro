# -*- coding: utf-8 -*-
"""
Utilitários para leitura de cotações manuais (CSV) em formato OHLCV.

Padrão suportado (case-insensitive):
  - Colunas: datetime | date[, time], open, high, low, close[, volume]
  - Delimitador: vírgula ou ponto-e-vírgula
  - Datas em UTC (recomendado); timezone será removido para índice

Saída: pandas.DataFrame com índice DateTime e colunas: Open, High, Low, Close, Volume (se disponível)
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional
import pandas as pd


def _ptbr_to_float(valor: str) -> float:
    """Converte string PT-BR para float (vírgula → ponto, remove separador de milhar)."""
    v = (valor or '').strip()
    v = v.replace('\u00A0', ' ').replace(' ', '')
    # Remover separador de milhar '.' e trocar ',' por '.'
    v = v.replace('.', '').replace(',', '.')
    v = v.replace('%', '')
    if v == '' or v == '-':
        return 0.0
    return float(v)


def carregar_ohlcv_csv(caminho: Path) -> pd.DataFrame:
    """Carrega um CSV OHLCV e normaliza para colunas padrão.

    Regras de detecção:
    - Busca cabeçalhos por nomes usuais (case-insensitive)
    - Aceita 'datetime' único, ou 'date'/'data' (+ 'time' opcional)
    - Converte números para float; suporta PT-BR (vírgula decimal)
    - Ignora linhas inválidas
    """
    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")

    # Tenta vírgula e ponto-e-vírgula (pandas detecta automaticamente)
    try:
        df = pd.read_csv(caminho, sep=None, engine='python')
    except Exception:
        df = pd.read_csv(caminho, sep=',')

    # Normalizar nomes de colunas: remover BOM, espaços e aspas
    cols = {c.lstrip('\ufeff').strip().strip('"').lower(): c for c in df.columns}

    # Determinar coluna de data/hora
    dt_col = None
    if 'datetime' in cols:
        dt_col = cols['datetime']
        dt_series = pd.to_datetime(df[dt_col], utc=True, errors='coerce')
    elif 'date' in cols and 'time' in cols:
        dt_series = pd.to_datetime(df[cols['date']] + ' ' + df[cols['time']], utc=True, errors='coerce')
    elif 'date' in cols:
        dt_series = pd.to_datetime(df[cols['date']], dayfirst=True, utc=True, errors='coerce')
    elif 'data' in cols:
        # PT-BR: Data
        dt_series = pd.to_datetime(df[cols['data']], dayfirst=True, utc=True, errors='coerce')
    else:
        raise ValueError(f"Cabeçalhos de data não encontrados. Esperado 'datetime', 'date' ou 'data'(PT-BR). Headers: {list(df.columns)}")

    # Mapear OHLCV
    def pick(*names):
        for n in names:
            if n in cols:
                return cols[n]
        return None

    open_col = pick('open', 'abertura')
    high_col = pick('high', 'max', 'maxima', 'máxima')
    low_col = pick('low', 'min', 'minima', 'mínima')
    close_col = pick('close', 'ultimo', 'último', 'close_price')
    vol_col = pick('volume', 'vol', 'vol.')

    for req, label in [(open_col, 'open'), (high_col, 'high'), (low_col, 'low'), (close_col, 'close')]:
        if req is None:
            raise ValueError(f"Coluna obrigatória ausente no CSV: {label}")

    # Converter usando função PT-BR-aware
    out = pd.DataFrame({
        'Open': df[open_col].apply(_ptbr_to_float),
        'High': df[high_col].apply(_ptbr_to_float),
        'Low': df[low_col].apply(_ptbr_to_float),
        'Close': df[close_col].apply(_ptbr_to_float),
    })
    if vol_col:
        # Volume pode ter sufixo K/M
        def parse_vol(v):
            v = str(v).strip()
            mult = 1
            if v.endswith('K') or v.endswith('k'):
                mult = 1_000
                v = v[:-1]
            elif v.endswith('M') or v.endswith('m'):
                mult = 1_000_000
                v = v[:-1]
            try:
                return _ptbr_to_float(v) * mult
            except Exception:
                return 0.0
        out['Volume'] = df[vol_col].apply(parse_vol)

    # Atribuir índice de data
    dt_idx = pd.to_datetime(dt_series)
    # Remover timezone se presente (tz_convert requer aware, se None já é naive)
    if hasattr(dt_idx, 'dt') and hasattr(dt_idx.dt, 'tz') and dt_idx.dt.tz is not None:
        dt_idx = dt_idx.dt.tz_convert(None)
    elif hasattr(dt_idx, 'tz') and dt_idx.tz is not None:
        dt_idx = dt_idx.tz_convert(None)
    out.index = dt_idx
    out = out.dropna(subset=['Open', 'High', 'Low', 'Close'])
    out = out.sort_index()
    return out
