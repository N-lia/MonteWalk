import numpy as np
import pandas as pd
import yfinance as yf
from scipy.optimize import minimize
from typing import List, Dict
import logging
import json


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Helper function for fetching price data, mimicking yfinance output structure
# This function is assumed to exist or be provided elsewhere,
# but for the purpose of making the provided code syntactically correct,
# a placeholder implementation using yfinance is provided.
def get_price(ticker: str, period: str, interval: str) -> str:
    """
    Fetches historical price data for a given ticker and returns it as a JSON string.
    This is a placeholder to satisfy the new mean_variance_optimize function's dependency.
    In a real scenario, this might be an API call or a more sophisticated data fetcher.
    """
    try:
        data = yf.download(ticker, period=period, interval=interval, progress=False)
        if data.empty:
            return json.dumps([])
        # Rename columns to match expected structure if necessary, e.g., 'Date' instead of index
        data_reset = data.reset_index()
        data_reset['Date'] = data_reset['Date'].dt.strftime('%Y-%m-%d') # Format date as string
        # Select relevant columns, e.g., 'Date', 'Close'
        # The new code expects 'Date' and 'Close' to be present.
        # If other columns are needed, adjust here.
        history_list = data_reset[['Date', 'Close']].to_dict(orient='records')
        return json.dumps(history_list)
    except Exception as e:
        logger.error(f"Error fetching data for {ticker} with yfinance: {e}")
        return json.dumps([])

def mean_variance_optimize(tickers: List[str], lookback: str = "1y") -> str:
    """
    Calculates optimal portfolio weights using Mean-Variance Optimization (Max Sharpe).
    """
    try:
        logger.info(f"Starting Mean-Variance Optimization for: {tickers}")
        
        # 1. Fetch Data
        data = {}
        for ticker in tickers:
            # Get 1 year of data
            history_json = get_price(ticker, period="1y", interval="1d")
            history = json.loads(history_json)
            
            if not history:
                logger.warning(f"Optimization skipped: No data for {ticker}")
                return f"Could not fetch data for {ticker}"
                
            df = pd.DataFrame(history)
            df['Date'] = pd.to_datetime(df['Date'])
            df.set_index('Date', inplace=True)
            data[ticker] = df['Close']
            
        prices = pd.DataFrame(data)
        returns = prices.pct_change().dropna()
        
        if returns.empty:
            logger.warning("Optimization failed: Insufficient data overlap")
            return "Insufficient data overlap for optimization."
            
        # 2. Optimization Setup
        n_assets = len(tickers)
        mean_returns = returns.mean() * 252
        cov_matrix = returns.cov() * 252
        
        # Objective: Maximize Sharpe Ratio (Minimize negative Sharpe)
        def negative_sharpe(weights):
            p_ret = np.sum(weights * mean_returns)
            p_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            # Handle potential division by zero or very small volatility
            if p_vol < 1e-6:
                return 1e10 # Return a very large number to penalize near-zero volatility
            return -p_ret / p_vol
            
        # Constraints: Sum of weights = 1
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        # Bounds: 0 <= weight <= 1 (Long only)
        bounds = tuple((0, 1) for _ in range(n_assets))
        # Initial Guess: Equal weights
        init_guess = n_assets * [1. / n_assets]
        
        # 3. Run Optimization
        result = minimize(negative_sharpe, init_guess, method='SLSQP', bounds=bounds, constraints=constraints)
        
        if not result.success:
            logger.error(f"Optimization failed: {result.message}")
            return f"Optimization failed: {result.message}"
            
        optimal_weights = result.x
        
        # 4. Format Output
        allocation = {ticker: weight for ticker, weight in zip(tickers, optimal_weights) if weight > 0.01}
        
        p_ret = np.sum(optimal_weights * mean_returns)
        p_vol = np.sqrt(np.dot(optimal_weights.T, np.dot(cov_matrix, optimal_weights)))
        sharpe = p_ret / p_vol
        
        logger.info(f"Optimization completed. Max Sharpe: {sharpe:.2f}")
        
        return (
            f"Optimal Allocation (Max Sharpe):\n"
            f"{json.dumps(allocation, indent=2)}\n\n"
            f"Expected Annual Return: {p_ret:.2%}\n"
            f"Expected Volatility: {p_vol:.2%}\n"
            f"Sharpe Ratio: {sharpe:.2f}"
        )
        
    except Exception as e:
        logger.error(f"Optimization error: {e}", exc_info=True)
        return f"Error optimizing portfolio: {str(e)}"

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
