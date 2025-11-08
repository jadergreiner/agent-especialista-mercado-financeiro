"""
Ferramenta: Obtenção de Preço Atual

Retorna preço em tempo real (ou o mais recente disponível) de ativos financeiros
usando Yahoo Finance como fonte primária.
"""

import logging
from datetime import datetime, timezone, time
from typing import Dict, Optional

import yfinance as yf
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from utils.logger_analise import obter_logger

logger = obter_logger(__name__)


def _verificar_mercado_aberto(ativo: str, dt: datetime) -> str:
    """
    Verifica se o mercado está aberto para um ativo específico.

    Args:
        ativo: Símbolo do ativo
        dt: Data/hora para verificar

    Returns:
        str: "aberto", "fechado", "pre_mercado", "pos_mercado"
    """
    # Forex: 24/5 (segunda 00:00 até sexta 23:59 UTC)
    if ativo in ["EURUSD", "USDJPY", "GBPJPY", "AUDNZD"]:
        if dt.weekday() >= 5:  # Sábado=5, Domingo=6
            return "fechado"
        return "aberto"

    # Ouro (GC=F): Seg-Sex 18:00-17:00 ET (22:00-21:00 UTC)
    elif ativo == "XAUUSD":
        if dt.weekday() >= 5:
            return "fechado"
        hora_utc = dt.time()
        if time(22, 0) <= hora_utc <= time(21, 0):  # Ajuste para virada de dia
            return "aberto"
        elif time(21, 0) < hora_utc < time(22, 0):
            return "pre_mercado"
        else:
            return "fechado"

    # Ibovespa/WinFut: Seg-Sex 10:00-17:55 BRT (13:00-20:55 UTC)
    elif ativo == "WINFUT":
        if dt.weekday() >= 5:
            return "fechado"
        hora_utc = dt.time()
        if time(13, 0) <= hora_utc <= time(20, 55):
            return "aberto"
        elif time(9, 0) <= hora_utc < time(13, 0):
            return "pre_mercado"
        else:
            return "fechado"

    # Default: assumir aberto para outros ativos
    return "aberto"


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
    return _obter_preco_atual_com_retry(ativo, incluir_historico)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type((Exception,)),
    before_sleep=lambda retry_state: logger.warning(
        f"Tentativa {retry_state.attempt_number} falhou para {retry_state.args[0] if retry_state.args else 'ativo'}. "
        f"Tentando novamente em {retry_state.next_action.sleep} segundos..."
    )
)
def _obter_preco_atual_com_retry(ativo: str, incluir_historico: bool = False) -> Dict:
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

        # Obter timestamp do preço (usar regularMarketTime se disponível, senão now)
        timestamp_preco = info.get("regularMarketTime")
        if timestamp_preco:
            # Yahoo retorna timestamp em segundos
            timestamp_preco = datetime.fromtimestamp(timestamp_preco, tz=timezone.utc)
        else:
            timestamp_preco = datetime.now(timezone.utc)

        # Calcular frescor dos dados
        idade_dados = datetime.now(timezone.utc) - timestamp_preco
        frescor = "tempo_real" if idade_dados.total_seconds() < 900 else "atrasado"  # 15min = 900s

        # Verificar status do mercado
        mercado_status = _verificar_mercado_aberto(ticker_normalizado, datetime.now(timezone.utc))

        if mercado_status == "fechado":
            logger.warning(f"⚠️ Mercado fechado para {ticker_normalizado} — último preço de {timestamp_preco.strftime('%Y-%m-%d %H:%M UTC')}")

        resultado = {
            "ativo": ticker_normalizado,
            "preco": round(float(preco_atual), 4),
            "variacao_pct": round(float(variacao_pct), 2),
            "timestamp": timestamp_preco.isoformat(),
            "frescor": frescor,
            "idade_dados_minutos": round(idade_dados.total_seconds() / 60, 1),
            "mercado_status": mercado_status,
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
