import time
import functools
import yfinance as yf
import pandas as pd
import pandas as pd
from typing import Dict, Any, Optional, List, Literal

def retry(times=3, delay=1):
    """Decorator to retry functions on failure."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(times):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if i == times - 1:
                        return f"Error after {times} retries: {str(e)}"
                    time.sleep(delay)
        return wrapper
    return decorator

@retry(times=3, delay=2)
def get_price(
    symbol: str, 
    interval: Literal["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"] = "1d", 
    period: Literal["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"] = "1y"
) -> List[Dict[str, Any]]:
    """
    Retrieves historical price data (OHLCV) for a given symbol.
    
    Args:
        symbol: The ticker symbol (e.g., 'AAPL', 'BTC-USD').
        interval: Data interval. Valid values: "1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo".
        period: Data period to download. Valid values: "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max".
        
    Returns:
        List of dictionaries containing OHLCV data.
    """
    ticker = yf.Ticker(symbol)
    # auto_adjust=True is important for total returns analysis
    df = ticker.history(period=period, interval=interval, auto_adjust=True)
    
    if df.empty:
        raise ValueError(f"No data found for {symbol}. Check symbol or API status.")
    
    # Data Quality Check
    if df.isnull().values.any():
        # Fill small gaps, drop large ones
        df = df.fillna(method='ffill').fillna(method='bfill')
    
    # Reset index to make Date a column
    df.reset_index(inplace=True)
    # Convert Timestamp to string for JSON serialization
    df['Date'] = df['Date'].astype(str)
    return df.to_dict(orient="records")

def get_fundamentals(symbol: str) -> Dict[str, Any]:
    """
    Retrieves core financial and fundamental data.
    
    Args:
        symbol: The ticker symbol.
        
    Returns:
        Dictionary containing fundamental data.
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        # Filter for key metrics to avoid overwhelming context
        key_metrics = [
            "marketCap", "forwardPE", "trailingPE", "pegRatio", 
            "priceToBook", "profitMargins", "revenueGrowth", 
            "returnOnEquity", "totalDebt", "totalCash", "sector", "industry"
        ]
        return {k: info.get(k) for k in key_metrics if k in info}
    except Exception as e:
        return {"error": f"Error fetching fundamentals for {symbol}: {str(e)}"}

def get_orderbook(symbol: str) -> str:
    """
    Fetches the current order book. 
    NOTE: yfinance does not provide Level 2 data. This is a placeholder to demonstrate tool registration.
    
    Args:
        symbol: The ticker symbol.
        
    Returns:
        Message indicating unavailability.
    """
    return f"Order book data (Level 2) is not available via free API for {symbol}."
