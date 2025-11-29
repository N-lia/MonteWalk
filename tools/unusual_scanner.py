"""
Unusual Activity Scanner (Alpaca Data API)
Scans market for unusual trading activity using Alpaca's real-time data.
"""

import logging
from typing import List, Dict, Any, Literal, Optional
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest, StockLatestQuoteRequest
from alpaca.data.timeframe import TimeFrame
from config import ALPACA_API_KEY, ALPACA_SECRET_KEY

logger = logging.getLogger(__name__)

# Cache for market snapshot (5-minute TTL)
_CACHE = {
    "data": None,
    "timestamp": None,
    "ttl": 300  # 5 minutes in seconds
}

# S&P 500 core tickers (top 100 for speed)
SP500_CORE = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "UNH", "XOM",
    "JN", "JPM", "V", "PG", "MA", "HD", "CVX", "MRK", "ABBV", "PEP",
    "COST", "AVGO", "KO", "ADBE", "MCD", "CSCO", "ACN", "TMO", "ABT", "LIN",
    "NFLX", "NKE", "ORCL", "CRM", "DIS", "VZ", "CMCSA", "WMT", "DHR", "INTC",
    "AMD", "TXN", "QCOM", "PM", "NEE", "UNP", "RTX", "HON", "UPS", "LOW",
    "SPGI", "INTU", "CAT", "BMY", "BA", "AMGN", "SBUX", "IBM", "GE", "AMAT",
    "ELV", "DE", "GILD", "PLD", "LMT", "ADI", "ADP", "TJX", "BKNG", "MDLZ",
    "SYK", "VRTX", "ISRG", "CI", "MMC", "CB", "PGR", "ZTS", "SO", "BLK",
    "REGN", "NOW", "C", "DUK", "BSX", "SLB", "SCHW", "ETN", "MO", "GS",
    "TMUS", "EOG", "PNC", "MS", "USB", "LRCX", "HCA", "CME", "ICE", "MMM"
]

# Singleton for Alpaca data client
_data_client = None

def _get_alpaca_client() -> Optional[StockHistoricalDataClient]:
    """Get or create Alpaca data client singleton."""
    global _data_client
    
    if _data_client is None:
        try:
            if not ALPACA_API_KEY or not ALPACA_SECRET_KEY:
                logger.error("Alpaca credentials not found in environment")
                return None
            
            _data_client = StockHistoricalDataClient(ALPACA_API_KEY, ALPACA_SECRET_KEY)
            logger.info("Alpaca data client initialized for market scanner")
        except Exception as e:
            logger.error(f"Failed to initialize Alpaca data client: {e}")
            return None
    
    return _data_client


def _get_ticker_universe() -> List[str]:
    """Get universe of tickers to scan."""
    return SP500_CORE


def _is_cache_valid() -> bool:
    """Check if cached data is still valid."""
    if _CACHE["data"] is None or _CACHE["timestamp"] is None:
        return False
    
    elapsed = (datetime.now() - _CACHE["timestamp"]).total_seconds()
    return elapsed < _CACHE["ttl"]


def _fetch_ticker_data_alpaca(symbol: str) -> Optional[Dict[str, Any]]:
    """Fetch 5-day data for a single ticker using Alpaca."""
    try:
        data_client = _get_alpaca_client()
        if not data_client:
            logger.debug("Alpaca data client not available")
            return None
        
        # Get 5-day bars
        end_time = datetime.now()
        start_time = end_time - timedelta(days=7)  # Extra days for weekends
        
        request = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=TimeFrame.Day,
            start=start_time,
            end=end_time
        )
        
        bars = data_client.get_stock_bars(request)
        
        if symbol not in bars or len(bars[symbol]) < 2:
            return None
        
        # Convert to list and sort by time
        bar_list = list(bars[symbol])
        bar_list.sort(key=lambda x: x.timestamp)
        
        # Get latest and previous day
        latest = bar_list[-1]
        previous = bar_list[-2] if len(bar_list) >= 2 else latest
        
        # Calculate average volume (exclude today)
        avg_volume = sum(b.volume for b in bar_list[:-1]) / max(len(bar_list) - 1, 1)
        
        # Calculate metrics
        price_change = ((latest.close - previous.close) / previous.close) * 100
        volume_ratio = latest.volume / avg_volume if avg_volume > 0 else 0
        
        return {
            "symbol": symbol,
            "price": round(latest.close, 2),
            "change_pct": round(price_change, 2),
            "volume": int(latest.volume),
            "avg_volume": int(avg_volume),
            "volume_ratio": round(volume_ratio, 2),
            "high": round(latest.high, 2),
            "low": round(latest.low, 2),
        }
    except Exception as e:
        logger.debug(f"Error fetching {symbol} from Alpaca: {e}")
        return None


def _fetch_market_snapshot(tickers: List[str], max_workers: int = 10) -> List[Dict]:
    """Fetch current snapshot for all tickers in parallel using Alpaca."""
    
    # Check cache first
    if _is_cache_valid():
        logger.info("Using cached market snapshot")
        return _CACHE["data"]
    
    logger.info(f"Fetching market snapshot for {len(tickers)} tickers via Alpaca...")
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_ticker = {executor.submit(_fetch_ticker_data_alpaca, ticker): ticker for ticker in tickers}
        
        for future in as_completed(future_to_ticker):
            data = future.result()
            if data:
                results.append(data)
    
    # Update cache
    _CACHE["data"] = results
    _CACHE["timestamp"] = datetime.now()
    
    logger.info(f"Fetched data for {len(results)} tickers from Alpaca")
    return results


def screen_big_movers(min_change: float = 8.0, min_volume: int = 1_000_000, limit: int = 15) -> List[Dict]:
    """
    Find stocks with large price moves (±8%+) on significant volume.
    
    Args:
        min_change: Minimum absolute price change percentage
        min_volume: Minimum volume threshold
        limit: Maximum results to return
    
    Returns:
        List of dictionaries with ticker data
    """
    tickers = _get_ticker_universe()
    data = _fetch_market_snapshot(tickers)
    
    # Filter for big movers
    filtered = [
        d for d in data
        if abs(d['change_pct']) >= min_change and d['volume'] >= min_volume
    ]
    
    # Sort by absolute change
    filtered.sort(key=lambda x: abs(x['change_pct']), reverse=True)
    filtered = filtered[:limit]
    
    # Add summary
    for item in filtered:
        item['summary'] = f"{'+' if item['change_pct'] > 0 else ''}{item['change_pct']:.1f}% on {item['volume_ratio']:.1f}x volume"
    
    return filtered


def screen_volume_spikes(volume_ratio_min: float = 3.0, limit: int = 15) -> List[Dict]:
    """
    Find stocks with unusual volume (3x+ average).
    
    Args:
        volume_ratio_min: Minimum volume ratio (current / average)
        limit: Maximum results to return
    
    Returns:
        List of dictionaries with ticker data
    """
    tickers = _get_ticker_universe()
    data = _fetch_market_snapshot(tickers)
    
    # Filter for volume spikes
    filtered = [d for d in data if d['volume_ratio'] >= volume_ratio_min]
    
    # Sort by volume ratio
    filtered.sort(key=lambda x: x['volume_ratio'], reverse=True)
    filtered = filtered[:limit]
    
    # Add summary
    for item in filtered:
        item['summary'] = f"{item['volume_ratio']:.1f}x avg volume ({'+' if item['change_pct'] > 0 else ''}{item['change_pct']:.1f}%)"
    
    return filtered


def screen_reversal_candidates(dip_min: float = -5.0, dip_max: float = -15.0, min_volume_ratio: float = 1.5, limit: int = 15) -> List[Dict]:
    """
    Find stocks down 5-15% with elevated volume (potential bounce candidates).
    
    Args:
        dip_min: Minimum price decline (e.g., -5%)
        dip_max: Maximum price decline (e.g., -15%)
        min_volume_ratio: Minimum volume ratio to confirm interest
        limit: Maximum results to return
    
    Returns:
        List of dictionaries with ticker data
    """
    tickers = _get_ticker_universe()
    data = _fetch_market_snapshot(tickers)
    
    # Filter for dips with volume
    filtered = [
        d for d in data
        if dip_max <= d['change_pct'] <= dip_min and d['volume_ratio'] >= min_volume_ratio
    ]
    
    # Sort by volume ratio (higher volume = more conviction)
    filtered.sort(key=lambda x: x['volume_ratio'], reverse=True)
    filtered = filtered[:limit]
    
    # Add summary
    for item in filtered:
        item['summary'] = f"Down {abs(item['change_pct']):.1f}% on {item['volume_ratio']:.1f}x volume"
    
    return filtered


def scan_unusual_activity(
    criteria: Literal["big_movers", "volume_spikes", "reversal_candidates"] = "big_movers",
    limit: int = 15,
    visualize: bool = False
) -> str:
    """
    Universal market scanner for unusual trading activity using Alpaca data.
    
    Args:
        criteria: Screening template to use
        limit: Maximum results to return
        visualize: If True, returns bar chart of results
    
    Returns:
        Formatted text summary or base64-encoded chart
    """
    try:
        data_client = _get_alpaca_client()
        if not data_client:
            return "❌ Alpaca data client not initialized. Check API credentials in .env file."
        
        logger.info(f"Running unusual activity scan: {criteria}")
        
        # Run appropriate scanner
        if criteria == "big_movers":
            results = screen_big_movers(limit=limit)
            title = f"🔥 Big Movers (±8%+ on volume)"
        elif criteria == "volume_spikes":
            results = screen_volume_spikes(limit=limit)
            title = f"📊 Volume Spikes (3x+ avg volume)"
        elif criteria == "reversal_candidates":
            results = screen_reversal_candidates(limit=limit)
            title = f"🎯 Reversal Candidates (Dip + Volume)"
        else:
            return f"Unknown criteria: {criteria}"
        
        if not results:
            return f"No unusual activity found matching '{criteria}' criteria"
        
        # Format text output
        output = [f"\n=== {title} ==="]
        output.append(f"Found {len(results)} matches (via Alpaca Data API)\n")
        
        for i, item in enumerate(results, 1):
            output.append(
                f"{i}. {item['symbol']:6} ${item['price']:8.2f} | "
                f"{item['summary']}"
            )
        
        result_text = "\n".join(output)
        
        # Add visualization if requested
        if visualize and results:
            try:
                from tools.visualizer import plot_bar
                
                symbols = [r['symbol'] for r in results]
                changes = [r['change_pct'] for r in results]
                
                chart = plot_bar(
                    symbols,
                    changes,
                    title=title,
                    x_label="Symbol",
                    y_label="Price Change (%)",
                    horizontal=False
                )
                result_text += f"\n\n{chart}"
            except Exception as e:
                logger.error(f"Error generating visualization: {e}")
                result_text += f"\n(Visualization error: {str(e)})"
        
        return result_text
        
    except Exception as e:
        logger.error(f"Error in unusual activity scan: {e}", exc_info=True)
        return f"Error scanning market: {str(e)}"
