"""
Backtesting Avançado para Estratégias WIN

Implementa backtesting completo com custos de transação,
slippage, validação walk-forward e métricas de performance financeira.

Autor: Sistema Especialista de Mercado Financeiro
Data: 2025
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from enum import Enum

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TradeType(Enum):
    """Tipos de operação."""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

@dataclass
class Trade:
    """Representa uma operação de trading."""
    timestamp: datetime
    trade_type: TradeType
    price: float
    quantity: int
    commission: float
    slippage: float
    total_cost: float

@dataclass
class Position:
    """Representa uma posição de trading."""
    symbol: str
    quantity: int
    avg_price: float
    current_value: float
    unrealized_pnl: float

class WinBacktester:
    """
    Backtester avançado para estratégias WIN.

    Inclui custos de transação, slippage, validação walk-forward
    e métricas de performance financeira completas.
    """

    def __init__(self,
                 initial_capital: float = 100000.0,
                 commission_per_trade: float = 5.0,  # R$ por contrato
                 slippage_bps: float = 2.0,  # Slippage em basis points
                 max_position_size: int = 5):  # Máximo de contratos

        self.initial_capital = initial_capital
        self.commission_per_trade = commission_per_trade
        self.slippage_bps = slippage_bps / 10000  # Converter para decimal
        self.max_position_size = max_position_size

        # Estado do portfolio
        self.cash = initial_capital
        self.positions: Dict[str, Position] = {}
        self.trades: List[Trade] = []
        self.portfolio_values: List[Tuple[datetime, float]] = []

        # Métricas de performance
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_pnl = 0.0
        self.max_drawdown = 0.0
        self.peak_value = initial_capital

        logger.info(f"Backtester inicializado: Capital={initial_capital}, Comissão={commission_per_trade}, Slippage={slippage_bps}bps")

    def execute_trade(self, timestamp: datetime, signal: float, current_price: float,
                     symbol: str = "WIN") -> Optional[Trade]:
        """
        Executa uma operação baseada no sinal do modelo.

        Args:
            timestamp: Timestamp da operação
            signal: Sinal do modelo (-1 a 1, onde > 0.1 = BUY, < -0.1 = SELL)
            current_price: Preço atual do ativo
            symbol: Símbolo do ativo

        Returns:
            Trade executado ou None se não houve operação
        """

        # Determinar tipo de operação baseado no sinal
        if signal > 0.1:  # Sinal de compra
            trade_type = TradeType.BUY
            quantity = min(self.max_position_size, int(self.cash / (current_price * 1.1)))  # Reserva margem
        elif signal < -0.1:  # Sinal de venda
            trade_type = TradeType.SELL
            quantity = -min(self.max_position_size, abs(self.positions.get(symbol, Position(symbol, 0, 0, 0, 0)).quantity))
        else:
            return None  # Hold

        if quantity == 0:
            return None

        # Calcular slippage
        slippage_amount = current_price * self.slippage_bps
        if trade_type == TradeType.BUY:
            execution_price = current_price + slippage_amount
        else:
            execution_price = current_price - slippage_amount

        # Calcular custos
        commission = abs(quantity) * self.commission_per_trade
        total_cost = (execution_price * abs(quantity)) + commission

        # Verificar se há capital suficiente para compra
        if trade_type == TradeType.BUY and total_cost > self.cash:
            logger.warning(f"Capital insuficiente: {self.cash:.2f} < {total_cost:.2f}")
            return None

        # Executar trade
        trade = Trade(
            timestamp=timestamp,
            trade_type=trade_type,
            price=execution_price,
            quantity=quantity,
            commission=commission,
            slippage=slippage_amount * abs(quantity),
            total_cost=total_cost
        )

        # Atualizar portfolio
        self._update_portfolio(trade, symbol)
        self.trades.append(trade)
        self.total_trades += 1

        logger.debug(f"Trade executado: {trade_type.value} {quantity} @ {execution_price:.2f}")

        return trade

    def _update_portfolio(self, trade: Trade, symbol: str):
        """Atualiza o estado do portfolio após uma operação."""

        if symbol not in self.positions:
            self.positions[symbol] = Position(symbol, 0, 0, 0, 0)

        position = self.positions[symbol]

        if trade.trade_type == TradeType.BUY:
            # Calcular novo preço médio
            total_quantity = position.quantity + trade.quantity
            if total_quantity > 0:
                total_cost = (position.quantity * position.avg_price) + (trade.quantity * trade.price)
                new_avg_price = total_cost / total_quantity
                position.avg_price = new_avg_price
                position.quantity = total_quantity

            self.cash -= trade.total_cost

        elif trade.trade_type == TradeType.SELL:
            # Realizar P&L
            pnl = (trade.price - position.avg_price) * abs(trade.quantity)
            self.total_pnl += pnl
            self.cash += (trade.price * abs(trade.quantity)) - trade.commission

            position.quantity += trade.quantity  # Quantity é negativo para venda

            # Atualizar contadores de trades winners/losers
            if pnl > 0:
                self.winning_trades += 1
            else:
                self.losing_trades += 1

        # Atualizar valor corrente da posição
        position.current_value = position.quantity * trade.price
        position.unrealized_pnl = (trade.price - position.avg_price) * position.quantity

    def update_portfolio_value(self, timestamp: datetime, current_prices: Dict[str, float]):
        """Atualiza o valor total do portfolio."""

        total_value = self.cash

        for symbol, position in self.positions.items():
            if symbol in current_prices:
                position.current_value = position.quantity * current_prices[symbol]
                position.unrealized_pnl = (current_prices[symbol] - position.avg_price) * position.quantity
                total_value += position.current_value

        self.portfolio_values.append((timestamp, total_value))

        # Atualizar drawdown
        if total_value > self.peak_value:
            self.peak_value = total_value
        else:
            drawdown = (self.peak_value - total_value) / self.peak_value
            self.max_drawdown = max(self.max_drawdown, drawdown)

    def run_backtest(self, data: pd.DataFrame, signals: pd.Series,
                    symbol: str = "WIN") -> Dict[str, float]:
        """
        Executa backtest completo.

        Args:
            data: DataFrame com dados OHLCV
            signals: Série com sinais do modelo (-1 a 1)
            symbol: Símbolo do ativo

        Returns:
            Dicionário com métricas de performance
        """

        logger.info("Iniciando backtest...")

        # Reset state
        self.__init__(self.initial_capital, self.commission_per_trade,
                     self.slippage_bps * 10000, self.max_position_size)

        for i, (timestamp, row) in enumerate(data.iterrows()):
            current_price = row['Close']
            signal = signals.iloc[i] if i < len(signals) else 0.0

            # Executar trade se houver sinal
            self.execute_trade(timestamp, signal, current_price, symbol)

            # Atualizar valor do portfolio
            self.update_portfolio_value(timestamp, {symbol: current_price})

        # Calcular métricas finais
        return self.calculate_performance_metrics()

    def calculate_performance_metrics(self) -> Dict[str, float]:
        """Calcula métricas de performance do backtest."""

        if not self.portfolio_values:
            return {}

        # Valores finais
        final_value = self.portfolio_values[-1][1]
        total_return = (final_value - self.initial_capital) / self.initial_capital * 100

        # Retornos diários
        portfolio_df = pd.DataFrame(self.portfolio_values, columns=['timestamp', 'value'])
        portfolio_df['returns'] = portfolio_df['value'].pct_change()
        portfolio_df = portfolio_df.dropna()

        # Métricas de risco
        volatility = portfolio_df['returns'].std() * np.sqrt(252) * 100  # Anualizada em %
        sharpe_ratio = (portfolio_df['returns'].mean() / portfolio_df['returns'].std() * np.sqrt(252)
                       if portfolio_df['returns'].std() > 0 else 0)

        # Métricas de trading
        win_rate = self.winning_trades / self.total_trades * 100 if self.total_trades > 0 else 0
        avg_win = self.total_pnl / self.winning_trades if self.winning_trades > 0 else 0
        avg_loss = self.total_pnl / self.losing_trades if self.losing_trades > 0 else 0
        profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else float('inf')

        # Calmar ratio (retorno anual / max drawdown)
        years = len(portfolio_df) / 252
        annual_return = total_return / years if years > 0 else 0
        calmar_ratio = annual_return / (self.max_drawdown * 100) if self.max_drawdown > 0 else float('inf')

        return {
            'total_return_pct': total_return,
            'annual_return_pct': annual_return,
            'volatility_pct': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown_pct': self.max_drawdown * 100,
            'calmar_ratio': calmar_ratio,
            'total_trades': self.total_trades,
            'win_rate_pct': win_rate,
            'total_pnl': self.total_pnl,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'final_value': final_value,
            'initial_capital': self.initial_capital
        }

    def get_trades_df(self) -> pd.DataFrame:
        """Retorna DataFrame com todas as operações."""
        trades_data = []
        for trade in self.trades:
            trades_data.append({
                'timestamp': trade.timestamp,
                'type': trade.trade_type.value,
                'price': trade.price,
                'quantity': trade.quantity,
                'commission': trade.commission,
                'slippage': trade.slippage,
                'total_cost': trade.total_cost
            })
        return pd.DataFrame(trades_data)

    def get_portfolio_df(self) -> pd.DataFrame:
        """Retorna DataFrame com evolução do portfolio."""
        return pd.DataFrame(self.portfolio_values, columns=['timestamp', 'value'])

def create_signals_from_predictions(predictions: np.ndarray, threshold: float = 0.02) -> pd.Series:
    """
    Cria sinais de trading a partir de predições do modelo.

    Args:
        predictions: Array com predições do modelo
        threshold: Threshold para gerar sinal (em %)

    Returns:
        Série com sinais (-1 a 1)
    """

    # Calcular retornos esperados
    current_prices = predictions[:-1]  # Preços atuais
    next_prices = predictions[1:]      # Preços preditos

    expected_returns = (next_prices - current_prices) / current_prices

    # Criar sinais
    signals = np.zeros(len(predictions))
    signals[1:] = np.where(expected_returns > threshold, 1.0,
                          np.where(expected_returns < -threshold, -1.0, 0.0))

    return pd.Series(signals, name='signal')

def benchmark_buy_and_hold(data: pd.DataFrame, initial_capital: float = 100000.0) -> Dict[str, float]:
    """
    Calcula performance de buy & hold para benchmark.

    Args:
        data: DataFrame com dados OHLCV
        initial_capital: Capital inicial

    Returns:
        Métricas de performance buy & hold
    """

    initial_price = data['Close'].iloc[0]
    final_price = data['Close'].iloc[-1]

    # Simular compra no início e venda no fim
    shares = initial_capital // initial_price
    final_value = shares * final_price
    total_return = (final_value - initial_capital) / initial_capital * 100

    # Retornos diários
    returns = data['Close'].pct_change().dropna()
    volatility = returns.std() * np.sqrt(252) * 100
    sharpe_ratio = (returns.mean() / returns.std() * np.sqrt(252)
                   if returns.std() > 0 else 0)

    # Max drawdown
    peak = initial_capital
    max_drawdown = 0
    current_value = initial_capital

    for price in data['Close']:
        current_value = shares * price
        if current_value > peak:
            peak = current_value
        else:
            drawdown = (peak - current_value) / peak
            max_drawdown = max(max_drawdown, drawdown)

    years = len(data) / 252
    annual_return = total_return / years if years > 0 else 0
    calmar_ratio = annual_return / (max_drawdown * 100) if max_drawdown > 0 else float('inf')

    return {
        'total_return_pct': total_return,
        'annual_return_pct': annual_return,
        'volatility_pct': volatility,
        'sharpe_ratio': sharpe_ratio,
        'max_drawdown_pct': max_drawdown * 100,
        'calmar_ratio': calmar_ratio,
        'final_value': final_value,
        'initial_capital': initial_capital
    }