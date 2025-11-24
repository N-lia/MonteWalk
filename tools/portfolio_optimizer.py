import numpy as np
import pandas as pd
import yfinance as yf
from scipy.optimize import minimize
from typing import List, Dict

def mean_variance_optimize(tickers: List[str], lookback: str = "1y") -> str:
    """
    Calculates optimal portfolio weights using Mean-Variance Optimization (Max Sharpe).
    """
    data = yf.download(tickers, period=lookback, progress=False)['Close']
    if data.empty: return "No data."
    
    returns = data.pct_change().dropna()
    mean_returns = returns.mean()
    cov_matrix = returns.cov()
    num_assets = len(tickers)
    
    def negative_sharpe(weights):
        p_ret = np.sum(returns.mean() * weights) * 252
        p_var = np.dot(weights.T, np.dot(cov_matrix, weights))
        p_vol = np.sqrt(p_var) * np.sqrt(252)
        if p_vol < 1e-6:
            return 0.0 # Avoid division by zero
        return -p_ret / p_vol
    
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bounds = tuple((0, 1) for _ in range(num_assets))
    init_guess = num_assets * [1. / num_assets,]
    
    result = minimize(negative_sharpe, init_guess, method='SLSQP', bounds=bounds, constraints=constraints)
    
    if not result.success:
        return f"Optimization failed: {result.message}"
    
    weights = dict(zip(tickers, result.x))
    # Filter small weights
    weights = {k: float(f"{v:.4f}") for k, v in weights.items() if v > 0.01}
    
    return f"Optimal Weights (Max Sharpe): {weights}"

def risk_parity(tickers: List[str]) -> str:
    """
    Calculates weights based on Inverse Volatility (Naive Risk Parity).
    """
    data = yf.download(tickers, period="1y", progress=False)['Close']
    returns = data.pct_change().dropna()
    volatility = returns.std()
    
    inv_vol = 1 / volatility
    weights = inv_vol / inv_vol.sum()
    
    w_dict = weights.to_dict()
    w_dict = {k: float(f"{v:.4f}") for k, v in w_dict.items()}
    
    return f"Risk Parity Weights: {w_dict}"
