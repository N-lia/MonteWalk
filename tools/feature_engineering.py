import pandas as pd
import pandas_ta as ta
import yfinance as yf
from typing import List
import logging

logger = logging.getLogger(__name__)

def compute_indicators(symbol: str, indicators: List[str] = ["RSI", "MACD"]) -> str:
    """
    Calculates technical indicators for a symbol.
    
    Args:
        symbol: Ticker symbol.
        indicators: List of indicators (e.g., ['RSI', 'MACD', 'BBANDS']).
    """
    df = yf.download(symbol, period="1y", progress=False)
    if df.empty:
        return f"No data for {symbol}"
    
    # Handle MultiIndex
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
        
    result = df[['Close']].copy()
    
    for ind in indicators:
        try:
            if ind.upper() == "RSI":
                result['RSI'] = ta.rsi(df['Close'])
            elif ind.upper() == "MACD":
                macd = ta.macd(df['Close'])
                result = pd.concat([result, macd], axis=1)
            elif ind.upper() == "BBANDS":
                bb = ta.bbands(df['Close'])
                result = pd.concat([result, bb], axis=1)
            # Add more as needed
        except Exception as e:
            return f"Error computing {ind}: {str(e)}"
            
    return result.tail(10).to_json(orient="index")

def rolling_stats(symbol: str, window: int = 20) -> str:
    """Computes rolling mean and volatility."""
    df = yf.download(symbol, period="1y", progress=False)
    if df.empty: return "No data"
    
    close = df['Close']
    if isinstance(close, pd.DataFrame): close = close.iloc[:, 0]
    
    stats = pd.DataFrame()
    stats['Mean'] = close.rolling(window=window).mean()
    stats['Std'] = close.rolling(window=window).std()
    
    return stats.tail(10).to_json(orient="index")

def get_technical_summary(symbol: str) -> str:
    """
    Performs a technical analysis summary (RSI, MACD, Moving Averages).
    Returns a 'Buy', 'Sell', or 'Neutral' signal based on aggregated indicators.
    """
    try:
        # Need enough data for 200 SMA
        df = yf.download(symbol, period="2y", progress=False)
        if df.empty:
            return f"No data found for {symbol}"
            
        # Handle MultiIndex if present
        # yfinance structure: columns are (Price, Ticker)
        if isinstance(df.columns, pd.MultiIndex):
            # If we have a MultiIndex, we want the 'Close' level, and then the specific ticker
            # But usually df['Close'] gives us the Close column(s).
            pass 
            
        close = df['Close']
        if isinstance(close, pd.DataFrame):
            # If multiple tickers or just weird structure, take the first column
            close = close.iloc[:, 0]
            
        # 1. RSI
        rsi = ta.rsi(close, length=14)
        if rsi is None or rsi.empty:
            return f"Not enough data to calculate RSI for {symbol}"
        current_rsi = rsi.iloc[-1]
        
        # 2. MACD
        macd = ta.macd(close)
        if macd is None or macd.empty:
            return f"Not enough data to calculate MACD for {symbol}"
        
        # MACD_12_26_9, MACDh_12_26_9 (hist), MACDs_12_26_9 (signal)
        # Column names depend on pandas_ta version/settings, but usually standard
        macd_line = macd.iloc[-1, 0] # First column is usually MACD line
        macd_signal = macd.iloc[-1, 2] # Third column is usually Signal line
        
        # 3. Moving Averages
        sma_50 = ta.sma(close, length=50)
        sma_200 = ta.sma(close, length=200)
        
        if sma_50 is None or sma_50.empty:
            return "Not enough data for SMA 50"
        if sma_200 is None or sma_200.empty:
            # Fallback if 200 SMA not available (e.g. IPO recently)
            sma_200_val = 0
            has_200 = False
        else:
            sma_200_val = sma_200.iloc[-1]
            has_200 = True
            
        sma_50_val = sma_50.iloc[-1]
        current_price = close.iloc[-1]
        
        # Scoring Logic
        score = 0
        reasons = []
        
        # RSI Logic
        if current_rsi < 30:
            score += 1
            reasons.append(f"RSI is Oversold ({current_rsi:.2f})")
        elif current_rsi > 70:
            score -= 1
            reasons.append(f"RSI is Overbought ({current_rsi:.2f})")
        else:
            reasons.append(f"RSI is Neutral ({current_rsi:.2f})")
            
        # MACD Logic
        if macd_line > macd_signal:
            score += 1
            reasons.append("MACD Bullish Crossover")
        else:
            score -= 1
            reasons.append("MACD Bearish Crossover")
            
        # Trend Logic
        if current_price > sma_50_val:
            score += 1
            reasons.append("Price above 50 SMA (Bullish Trend)")
        else:
            score -= 1
            reasons.append("Price below 50 SMA (Bearish Trend)")
            
        if has_200:
            if current_price > sma_200_val:
                score += 1
                reasons.append("Price above 200 SMA (Long-term Bullish)")
            else:
                score -= 1
                reasons.append("Price below 200 SMA (Long-term Bearish)")
        else:
            reasons.append("200 SMA not available (Insufficient history)")
            
        # Final Verdict
        if score >= 2:
            signal = "STRONG BUY"
        elif score == 1:
            signal = "BUY"
        elif score == 0:
            signal = "NEUTRAL"
        elif score == -1:
            signal = "SELL"
        else:
            signal = "STRONG SELL"
            
        return (f"Technical Summary for {symbol}:\n"
                f"Signal: {signal} (Score: {score})\n"
                f"Price: ${current_price:.2f}\n"
                f"--------------------------------\n"
                f"Analysis:\n" + "\n".join([f"- {r}" for r in reasons]))
                
    except Exception as e:
        return f"Error performing technical analysis: {str(e)}"
