import time
import functools
import yfinance as yf
import pandas as pd
import json
import logging
from typing import Dict, Any, Optional, List, Literal

logger = logging.getLogger(__name__)

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
    period: Literal["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"] = "1y",
    visualize: bool = False
) -> str:
    """
    Retrieves historical price data (OHLCV) for a given symbol.
    
    Args:
        symbol: The ticker symbol (e.g., 'AAPL', 'BTC-USD').
        interval: Data interval. Valid values: "1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo".
        period: Data period to download. Valid values: "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max".
        visualize: If True, returns a candlestick chart instead of raw data.
        
    Returns:
        JSON string of OHLCV data or base64-encoded candlestick chart.
    """
    try:
        ticker = yf.Ticker(symbol)
        history = ticker.history(period=period, interval=interval)
        
        if history.empty:
            logger.warning(f"No price data found for {symbol} (period={period}, interval={interval})")
            return json.dumps([])
        
        # Reset index to make Date a column
        history.reset_index(inplace=True)
        
        if visualize:
            try:
                from tools.visualizer import plot_candlestick
                # Convert to DataFrame format expected by visualizer
                df = history[['Date', 'Open', 'High', 'Low', 'Close']].copy()
                if 'Volume' in history.columns:
                    df['Volume'] = history['Volume']
                
                chart = plot_candlestick(
                    df,
                    title=f"{symbol} - {period} ({interval} interval)",
                    volume='Volume' in df.columns
                )
                return chart
            except Exception as e:
                logger.error(f"Error generating candlestick chart: {e}")
                # Fall through to return data
        
        # Convert to JSON-friendly format (list of dicts)
        # Convert timestamps to string
        history['Date'] = history['Date'].astype(str)
        
        data = history.to_dict(orient="records")
        logger.info(f"Fetched {len(data)} price records for {symbol}")
        
        return json.dumps(data, indent=2)
        
    except Exception as e:
        logger.error(f"Error fetching price data for {symbol}: {e}")
        return json.dumps([])

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
