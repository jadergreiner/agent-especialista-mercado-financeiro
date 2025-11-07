"""
Ferramenta: Obtenção de Preço Atual

Retorna preço em tempo real (ou o mais recente disponível) de ativos financeiros
usando Yahoo Finance como fonte primária.
"""

import logging
from datetime import datetime
from typing import Dict, Optional

import yfinance as yf

logger = logging.getLogger(__name__)


# Mapeamento de tickers internos para símbolos Yahoo Finance
MAPA_TICKERS = {
    "EURUSD": "EURUSD=X",
    "USDJPY": "USDJPY=X",
    "GBPJPY": "GBPJPY=X",
    "AUDNZD": "AUDNZD=X",
    "XAUUSD": "GC=F",  # Gold Futures
    "WINFUT": "^BVSP",  # Ibovespa como proxy para WinFut
}


def obter_preco_atual(ativo: str, incluir_historico: bool = False) -> Dict:
    """
    Obtém preço atual e variação de um ativo financeiro.

    Args:
        ativo: Símbolo do ativo (ex: "EURUSD", "XAUUSD")
        incluir_historico: Se True, inclui últimos 5 preços de fechamento

    Returns:
        dict: {
            "ativo": str,
            "preco": float,
            "variacao_pct": float,
            "timestamp": str (ISO 8601),
            "fonte": str,
            "historico": Optional[list]  # Se incluir_historico=True
        }

    Raises:
        ValueError: Se ativo desconhecido ou dados indisponíveis
    """
    logger.info(f"Obtendo preço atual para: {ativo}")

    # Normalizar ticker
    ticker_normalizado = ativo.upper()
    ticker_yf = MAPA_TICKERS.get(ticker_normalizado, ticker_normalizado)

    try:
        # Baixar dados do Yahoo Finance
        ticker_obj = yf.Ticker(ticker_yf)
        info = ticker_obj.info

        # Tentar obter preço atual de múltiplas fontes no objeto info
        preco_atual = (
            info.get("regularMarketPrice")
            or info.get("currentPrice")
            or info.get("previousClose")
        )

        if preco_atual is None:
            # Fallback: pegar último fechamento do histórico
            hist = ticker_obj.history(period="5d")
            if hist.empty:
                raise ValueError(f"Sem dados disponíveis para {ativo}")
            preco_atual = float(hist["Close"].iloc[-1])
            preco_anterior = float(hist["Close"].iloc[-2]) if len(hist) > 1 else preco_atual
        else:
            preco_anterior = info.get("previousClose", preco_atual)

        # Calcular variação percentual
        variacao_pct = ((preco_atual - preco_anterior) / preco_anterior) * 100 if preco_anterior else 0.0

        resultado = {
            "ativo": ticker_normalizado,
            "preco": round(float(preco_atual), 4),
            "variacao_pct": round(float(variacao_pct), 2),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "fonte": "Yahoo Finance",
        }

        # Incluir histórico se solicitado
        if incluir_historico:
            hist = ticker_obj.history(period="5d")
            resultado["historico"] = [
                {
                    "data": str(date.date()),
                    "fechamento": round(float(close), 4)
                }
                for date, close in zip(hist.index, hist["Close"])
            ][-5:]  # Últimos 5 dias

        logger.info(f"Preço obtido: {resultado['ativo']} = {resultado['preco']} ({resultado['variacao_pct']:+.2f}%)")
        return resultado

    except Exception as e:
        logger.error(f"Erro ao obter preço para {ativo}: {e}")
        raise ValueError(f"Não foi possível obter preço para {ativo}. Verifique se o ticker é válido.") from e


def validar_ativo_suportado(ativo: str) -> bool:
    """
    Valida se um ativo é suportado pela ferramenta.

    Args:
        ativo: Símbolo do ativo

    Returns:
        bool: True se suportado, False caso contrário
    """
    return ativo.upper() in MAPA_TICKERS or ativo.isupper()
