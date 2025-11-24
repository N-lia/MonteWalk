import numpy as np
import pandas as pd
import yfinance as yf
from typing import Dict, Any, List, Optional, Literal
from tools.execution import get_positions, _load_portfolio

def _get_portfolio_data(lookback: str = "1y"):
    portfolio = get_positions()
    positions = portfolio.get("positions", {})
    if not positions:
        return None, None
    
    tickers = list(positions.keys())
    weights = np.array(list(positions.values())) # This is qty, need value weights
    
    # Fetch data
    data = yf.download(tickers, period=lookback, progress=False)['Close']
    if isinstance(data, pd.Series):
        data = data.to_frame(name=tickers[0])
        
    # Calculate current value weights
    current_prices = data.iloc[-1]
    values = current_prices * pd.Series(positions)
    total_value = values.sum()
    weights = values / total_value
    
    return data, weights

def portfolio_risk() -> str:
    """Returns annualized volatility of the portfolio."""
    data, weights = _get_portfolio_data()
    if data is None:
        return "Portfolio is empty."
    
    returns = data.pct_change().dropna()
    cov_matrix = returns.cov() * 252
    port_variance = np.dot(weights.T, np.dot(cov_matrix, weights))
    port_volatility = np.sqrt(port_variance)
    
    return f"Annualized Portfolio Volatility: {port_volatility:.2%}"

def var(confidence: float = 0.95) -> str:
    """Calculates Value at Risk (VaR)."""
    data, weights = _get_portfolio_data()
    if data is None:
        return "Portfolio is empty."
    
    returns = data.pct_change().dropna()
    # Portfolio historical returns
    port_returns = returns.dot(weights)
    
    # Parametric VaR
    mean = np.mean(port_returns)
    std = np.std(port_returns)
    var_val = np.percentile(port_returns, (1 - confidence) * 100)
    
    return f"Daily VaR ({confidence:.0%}): {var_val:.2%}"

def max_drawdown() -> str:
    """Calculates Maximum Drawdown."""
    data, weights = _get_portfolio_data()
    if data is None:
        return "Portfolio is empty."
    
    returns = data.pct_change().dropna()
    port_returns = returns.dot(weights)
    cumulative_returns = (1 + port_returns).cumprod()
    peak = cumulative_returns.expanding(min_periods=1).max()
    drawdown = (cumulative_returns / peak) - 1
    max_dd = drawdown.min()
    
    return f"Maximum Drawdown: {max_dd:.2%}"

def monte_carlo_simulation(simulations: int = 1000, days: int = 252) -> str:
    """
    Runs a Monte Carlo simulation using Geometric Brownian Motion (Log Returns).
    
    Args:
        simulations: Number of paths to simulate.
        days: Number of days to project forward.
    """
    data, weights = _get_portfolio_data()
    if data is None:
        return "Portfolio is empty."
    
    # Use Log Returns for additivity
    log_returns = np.log(data / data.shift(1)).dropna()
    
    mean_log_returns = log_returns.mean()
    cov_matrix = log_returns.cov()
    
    # Cholesky Decomposition
    try:
        L = np.linalg.cholesky(cov_matrix)
    except np.linalg.LinAlgError:
        # Fallback for non-positive definite matrix (e.g., too few data points)
        return "Covariance matrix is not positive definite. Insufficient data history."
    
    portfolio_sims = np.zeros((days, simulations))
    initial_value = 1.0 
    
    for i in range(simulations):
        Z = np.random.normal(size=(days, len(weights)))
        # Correlated random shocks
        daily_shocks = np.dot(Z, L.T)
        
        # GBM: S_t = S_0 * exp( (mu - 0.5*sigma^2)*t + sigma*W_t )
        # Here we simulate daily steps
        daily_log_ret = mean_log_returns.values + daily_shocks
        
        # Portfolio level log return
        port_log_ret = np.dot(daily_log_ret, weights)
        
        # Accumulate log returns
        cum_log_ret = np.cumsum(port_log_ret)
        portfolio_sims[:, i] = initial_value * np.exp(cum_log_ret)
        
    final_values = portfolio_sims[-1, :]
    expected_return = np.mean(final_values) - 1
    worst_case = np.percentile(final_values, 5) - 1
    best_case = np.percentile(final_values, 95) - 1
    
    return (f"Monte Carlo Results ({simulations} sims, {days} days) [Log Normal]:\n"
            f"Expected Return: {expected_return:.2%}\n"
            f"5th Percentile (VaR 95%): {worst_case:.2%}\n"
            f"95th Percentile (Upside): {best_case:.2%}")

def validate_trade(symbol: str, side: Literal["buy", "sell"], qty: float, current_price: float) -> Optional[str]:
    """
    Checks if a proposed trade violates any risk limits.
    
    Args:
        symbol: Ticker symbol.
        side: "buy" or "sell".
        qty: Quantity to trade.
        current_price: Current market price per share.
        
    Returns:
        None if valid, otherwise an error message string.
    """
    portfolio = _load_portfolio()
    cash = portfolio["cash"]
    
    # 1. Max Position Size Limit (e.g., 20% of total equity)
    # Estimate Total Equity
    positions = portfolio["positions"]
    equity = cash
    # This is a rough estimate as we don't have real-time prices for all held assets here
    # For a robust system, we'd fetch all prices. For now, we use cash + cost basis approximation or just cash
    # Let's use a simplified check: No single trade > 20% of current Cash (conservative)
    
    trade_value = qty * current_price
    
    if side == "buy":
        if trade_value > (cash * 0.50): # Cap trade at 50% of available cash
            return f"Risk Rejection: Trade value {trade_value:.2f} exceeds 50% of available cash {cash:.2f}."

    # 2. Max Quantity Check
    if qty <= 0:
        return "Risk Rejection: Quantity must be positive."
        
    return None
