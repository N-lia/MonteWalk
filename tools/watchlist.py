import json
import yfinance as yf
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
from config import DATA_DIR

logger = logging.getLogger(__name__)

WATCHLIST_FILE = DATA_DIR / "watchlist.json"

def _load_watchlist() -> List[str]:
    if not WATCHLIST_FILE.exists():
        return []
    try:
        with open(WATCHLIST_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []

def _save_watchlist(watchlist: List[str]):
    with open(WATCHLIST_FILE, "w") as f:
        json.dump(watchlist, f, indent=4)

def add_to_watchlist(symbol: str) -> str:
    """
    Adds a symbol to the monitoring watchlist.
    """
    symbol = symbol.upper()
    watchlist = _load_watchlist()
    if symbol not in watchlist:
        watchlist.append(symbol)
        _save_watchlist(watchlist)
        logger.info(f"Added {symbol} to watchlist")
        return f"Added {symbol} to watchlist."
    return f"{symbol} is already in the watchlist."

def remove_from_watchlist(symbol: str) -> str:
    """
    Removes a symbol from the watchlist.
    """
    symbol = symbol.upper()
    watchlist = _load_watchlist()
    if symbol in watchlist:
        watchlist.remove(symbol)
        _save_watchlist(watchlist)
        logger.info(f"Removed {symbol} from watchlist")
        return f"Removed {symbol} from watchlist."
    return f"{symbol} was not in the watchlist."

def get_watchlist_data() -> Dict[str, Any]:
    """
    Fetches current data for all symbols in the watchlist.
    """
    watchlist = _load_watchlist()
    if not watchlist:
        return {}
    
    data = {}
    for symbol in watchlist:
        try:
            ticker = yf.Ticker(symbol)
            # fast_info is faster for real-time-ish data
            price = ticker.fast_info.last_price
            change = 0.0 # yfinance fast_info doesn't always have change % easily accessible without full history
            # Let's try to get a bit more if possible, but keep it fast
            data[symbol] = {
                "price": price,
                "status": "Active"
            }
        except Exception as e:
            data[symbol] = {"error": str(e)}
            
    return data
