"""
Ferramentas de Indicadores Técnicos

Módulo responsável por calcular indicadores técnicos usando pandas-ta.
Fornece funções para análise técnica de ativos financeiros.
"""

import pandas as pd
import pandas_ta as ta
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import yfinance as yf

from utils.logger_analise import obter_logger

logger = obter_logger(__name__)


def _normalizar_simbolo_yahoo(ativo: str) -> str:
    """
    Normaliza símbolo do ativo para formato compatível com Yahoo Finance.

    Args:
        ativo: Símbolo original do ativo

    Returns:
        str: Símbolo normalizado para Yahoo Finance
    """
    # Forex: EURUSD -> EURUSD=X
    if len(ativo) == 6 and ativo.isalpha() and ativo.isupper():
        # Verifica se é par de moedas (6 letras maiúsculas)
        return f"{ativo}=X"

    # Ações brasileiras: PETR4.SA -> PETR4.SA (já correto)
    # Outros ativos permanecem iguais
    return ativo


def calcular_sma_rsi(
    ativo: str,
    periodo_sma: int = 20,
    periodo_rsi: int = 14,
    periodo_historico: int = 100
) -> Dict[str, Any]:
    """
    Calcula SMA (Simple Moving Average) e RSI (Relative Strength Index) para um ativo.

    Args:
        ativo: Símbolo do ativo (ex: "EURUSD", "PETR4.SA")
        periodo_sma: Período para cálculo da média móvel simples (padrão: 20)
        periodo_rsi: Período para cálculo do RSI (padrão: 14)
        periodo_historico: Dias de histórico para análise (padrão: 100)

    Returns:
        dict: Dados dos indicadores calculados com metadados
    """
    logger.info(f"Calculando indicadores técnicos para {ativo} (SMA{periodo_sma}, RSI{periodo_rsi})")

    try:
        # Normalizar símbolo para Yahoo Finance
        simbolo_yahoo = _normalizar_simbolo_yahoo(ativo)
        logger.info(f"Símbolo normalizado: {ativo} -> {simbolo_yahoo}")

        # Baixar dados históricos
        ticker = yf.Ticker(simbolo_yahoo)
        dados = ticker.history(period=f"{periodo_historico}d", interval="1d")

        if dados.empty:
            raise ValueError(f"Não foi possível obter dados históricos para {ativo} (símbolo: {simbolo_yahoo})")

        # Calcular indicadores usando pandas-ta
        dados['SMA'] = ta.sma(dados['Close'], length=periodo_sma)
        dados['RSI'] = ta.rsi(dados['Close'], length=periodo_rsi)

        # Obter valores mais recentes
        ultimo_fechamento = dados['Close'].iloc[-1]
        sma_atual = dados['SMA'].iloc[-1]
        rsi_atual = dados['RSI'].iloc[-1]

        # Calcular sinais básicos
        sinal_sma = "ACIMA_SMA" if ultimo_fechamento > sma_atual else "ABAIXO_SMA"
        sinal_rsi = "SOBRECOMPRADO" if rsi_atual > 70 else "SOBREVENDIDO" if rsi_atual < 30 else "NEUTRO"

        # Timestamp de cálculo
        timestamp_calculo = datetime.now(timezone.utc)

        resultado = {
            "ativo": ativo,
            "timestamp_calculo": timestamp_calculo.isoformat(),
            "periodo_historico_dias": periodo_historico,
            "indicadores": {
                "sma": {
                    "periodo": periodo_sma,
                    "valor": round(float(sma_atual), 4),
                    "preco_atual": round(float(ultimo_fechamento), 4),
                    "sinal": sinal_sma,
                    "diferenca_pct": round(float(((ultimo_fechamento - sma_atual) / sma_atual) * 100), 2)
                },
                "rsi": {
                    "periodo": periodo_rsi,
                    "valor": round(float(rsi_atual), 2),
                    "sinal": sinal_rsi,
                    "interpretacao": _interpretar_rsi(rsi_atual)
                }
            },
            "dados_brutos": {
                "total_candles": len(dados),
                "periodo_analisado": {
                    "inicio": dados.index[0].isoformat(),
                    "fim": dados.index[-1].isoformat()
                }
            },
            "fonte": "Yahoo Finance + pandas-ta"
        }

        logger.info(f"Indicadores calculados com sucesso para {ativo}")
        return resultado

    except Exception as e:
        logger.error(f"Erro ao calcular indicadores para {ativo}: {e}")
        raise


def _interpretar_rsi(rsi_valor: float) -> str:
    """
    Interpreta o valor do RSI com linguagem técnica apropriada.
    """
    if rsi_valor > 70:
        return "Zona de sobrecompra - possível reversão baixista"
    elif rsi_valor < 30:
        return "Zona de sobrevenda - possível reversão altista"
    elif 45 <= rsi_valor <= 55:
        return "Zona neutra - sem sinal claro de momentum"
    elif rsi_valor > 55:
        return "Momentum altista moderado"
    else:
        return "Momentum baixista moderado"


def obter_resumo_tecnico(ativo: str) -> Dict[str, Any]:
    """
    Função de conveniência que retorna resumo técnico completo.
    Útil para integração com orquestrador de análise.
    """
    return calcular_sma_rsi(ativo)