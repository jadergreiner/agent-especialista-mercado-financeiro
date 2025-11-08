"""
Coletor de Dados do Mini Índice Brasileiro (WIN)

Este módulo é responsável por coletar dados históricos do WIN (Mini Índice)
através de APIs de dados financeiros.

Autor: Sistema Especialista de Mercado Financeiro
Data: 2025
"""

import pandas as pd
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Optional, Tuple

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WinDataCollector:
    """
    Coletor de dados históricos do Mini Índice Brasileiro (WIN).

    O WIN é o contrato futuro do Ibovespa com vencimento mais próximo.
    Utiliza dados do Yahoo Finance como fonte primária.
    """

    # Símbolos possíveis do WIN no Yahoo Finance
    WIN_SYMBOLS = [
        'WINZ25.SA',  # WIN Dezembro 2025
        'WINM25.SA',  # WIN Março 2025
        'WINF25.SA',  # WIN Abril 2025
        'WINJ25.SA',  # WIN Maio 2025
        'WINQ25.SA',  # WIN Junho 2025
        'WINV25.SA',  # WIN Outubro 2025
        '^BVSP'       # Ibovespa como proxy quando WIN não disponível
    ]

    def __init__(self):
        """Inicializa o coletor de dados."""
        self.current_symbol = None

    def get_win_data(self,
                    start_date: str = None,
                    end_date: str = None,
                    interval: str = '1d') -> pd.DataFrame:
        """
        Coleta dados históricos do WIN.

        Args:
            start_date: Data inicial (YYYY-MM-DD). Default: 30 anos atrás
            end_date: Data final (YYYY-MM-DD). Default: hoje
            interval: Intervalo dos dados ('1d', '1h', '30m', etc.)

        Returns:
            DataFrame com dados OHLCV do WIN
        """
        # Definir datas padrão - 30 anos de dados históricos
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=30*365)).strftime('%Y-%m-%d')  # 30 anos

        logger.info(f"Coletando dados WIN de {start_date} até {end_date} (30 anos de histórico)")

        # Tentar diferentes símbolos do WIN
        for symbol in self.WIN_SYMBOLS:
            try:
                logger.info(f"Tentando coletar dados do símbolo: {symbol}")
                data = yf.download(symbol, start=start_date, end=end_date, interval=interval)

                if not data.empty and len(data) > 100:  # Verificar se tem dados suficientes
                    self.current_symbol = symbol
                    logger.info(f"Dados coletados com sucesso do símbolo: {symbol}")
                    logger.info(f"Total de registros: {len(data)}")

                    # Limpar e formatar dados
                    data = self._clean_data(data)
                    return data

            except Exception as e:
                logger.warning(f"Erro ao coletar dados do símbolo {symbol}: {str(e)}")
                continue

        # Se nenhum símbolo funcionou, tentar dados alternativos
        logger.warning("Nenhum símbolo WIN funcionou. Tentando dados alternativos...")
        return self._get_alternative_data(start_date, end_date, interval)

    def _clean_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Limpa e formata os dados coletados.

        Args:
            data: DataFrame bruto dos dados

        Returns:
            DataFrame limpo e formatado
        """
        # Remover linhas com valores NaN
        data = data.dropna()

        # Lidar com MultiIndex columns (formato novo do yfinance)
        if isinstance(data.columns, pd.MultiIndex):
            # Pegar apenas o primeiro nível do ticker
            data.columns = data.columns.get_level_values(0)

        # Garantir que temos as colunas necessárias
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        if not all(col in data.columns for col in required_columns):
            logger.error(f"Colunas disponíveis: {data.columns.tolist()}")
            logger.error(f"Colunas necessárias: {required_columns}")
            raise ValueError("Dados não contêm todas as colunas necessárias")

        # Se não tem Adj Close, criar baseado no Close
        if 'Adj Close' not in data.columns:
            data['Adj Close'] = data['Close']

        # Resetar índice para ter Date como coluna
        data = data.reset_index()

        # Garantir que Date é datetime
        if 'Date' in data.columns:
            data['Date'] = pd.to_datetime(data['Date'])
            data = data.set_index('Date')

        # Arredondar valores para 2 casas decimais (exceto Volume)
        numeric_columns = ['Open', 'High', 'Low', 'Close', 'Adj Close']
        data[numeric_columns] = data[numeric_columns].round(2)

        # Garantir que Volume é inteiro
        data['Volume'] = data['Volume'].astype(int)

        return data

    def _get_alternative_data(self, start_date: str, end_date: str, interval: str) -> pd.DataFrame:
        """
        Obtém dados alternativos quando WIN não está disponível.

        Args:
            start_date: Data inicial
            end_date: Data final
            interval: Intervalo

        Returns:
            DataFrame com dados alternativos
        """
        logger.info("Usando Ibovespa como proxy para WIN")

        try:
            # Usar Ibovespa como proxy
            data = yf.download('^BVSP', start=start_date, end=end_date, interval=interval)
            data = self._clean_data(data)

            # Ajustar preços para escala do WIN (dividir por 1000)
            price_columns = ['Open', 'High', 'Low', 'Close', 'Adj Close']
            data[price_columns] = data[price_columns] / 1000
            data[price_columns] = data[price_columns].round(2)

            logger.warning("ATENÇÃO: Usando Ibovespa como proxy. Valores divididos por 1000 para aproximar escala WIN.")
            return data

        except Exception as e:
            logger.error(f"Erro ao obter dados alternativos: {str(e)}")
            raise ValueError("Não foi possível obter dados do WIN ou Ibovespa")

    def get_latest_win_price(self) -> Optional[float]:
        """
        Obtém o preço mais recente do WIN.

        Returns:
            Preço de fechamento mais recente ou None se erro
        """
        try:
            # Pegar apenas o último dia
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')

            data = self.get_win_data(start_date, end_date)
            if not data.empty:
                return float(data['Close'].iloc[-1])

        except Exception as e:
            logger.error(f"Erro ao obter preço atual do WIN: {str(e)}")

        return None

    def validate_data_quality(self, data: pd.DataFrame) -> dict:
        """
        Valida a qualidade dos dados coletados.

        Args:
            data: DataFrame com dados

        Returns:
            Dicionário com métricas de qualidade
        """
        quality_metrics = {
            'total_records': len(data),
            'missing_values': data.isnull().sum().sum(),
            'duplicate_dates': data.index.duplicated().sum(),
            'negative_prices': (data[['Open', 'High', 'Low', 'Close']] < 0).sum().sum(),
            'zero_volume': (data['Volume'] == 0).sum(),
            'date_range': {
                'start': data.index.min().strftime('%Y-%m-%d') if not data.empty else None,
                'end': data.index.max().strftime('%Y-%m-%d') if not data.empty else None
            },
            'price_range': {
                'min': float(data['Low'].min()) if not data.empty else None,
                'max': float(data['High'].max()) if not data.empty else None
            }
        }

        return quality_metrics

def main():
    """Função principal para teste do coletor."""
    collector = WinDataCollector()

    # Coletar dados dos últimos 2 anos
    print("Coletando dados WIN...")
    data = collector.get_win_data()

    if not data.empty:
        print(f"Dados coletados: {len(data)} registros")
        print(f"Período: {data.index.min()} até {data.index.max()}")
        print(f"Preço atual: R$ {data['Close'].iloc[-1]:.2f}")

        # Validar qualidade
        quality = collector.validate_data_quality(data)
        print(f"Qualidade dos dados: {quality}")

        # Salvar dados
        output_file = "data/win_historical_data.csv"
        data.to_csv(output_file)
        print(f"Dados salvos em: {output_file}")

    else:
        print("Erro: Não foi possível coletar dados do WIN")

if __name__ == "__main__":
    main()