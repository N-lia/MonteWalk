"""
Cryptocurrency Data Tools using CoinGecko API
No API key required - Free tier with generous limits
"""

from pycoingecko import CoinGeckoAPI
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

# Initialize CoinGecko client
cg = CoinGeckoAPI()

def get_crypto_price(coin_id: str, vs_currency: str = "usd") -> Dict[str, Any]:
    """
    Gets the current price of a cryptocurrency.
    
    Args:
        coin_id: CoinGecko ID (e.g., 'bitcoin', 'ethereum', 'solana')
        vs_currency: Currency to compare against (default: 'usd')
        
    Returns:
        Dictionary with price information
    """
    try:
        data = cg.get_price(
            ids=coin_id,
            vs_currencies=vs_currency,
            include_24hr_change=True,
            include_market_cap=True,
            include_24hr_vol=True
        )
        
        if not data or coin_id not in data:
            return {"error": f"Coin '{coin_id}' not found"}
            
        coin_data = data[coin_id]
        return {
            "coin": coin_id,
            "price": coin_data.get(vs_currency, 0),
            "market_cap": coin_data.get(f"{vs_currency}_market_cap", 0),
            "24h_volume": coin_data.get(f"{vs_currency}_24h_vol", 0),
            "24h_change": coin_data.get(f"{vs_currency}_24h_change", 0),
            "currency": vs_currency.upper()
        }
    except Exception as e:
        logger.error(f"CoinGecko error for {coin_id}: {e}")
        return {"error": str(e)}

def get_crypto_market_data(coin_id: str) -> str:
    """
    Gets comprehensive market data for a cryptocurrency.
    
    Args:
        coin_id: CoinGecko ID (e.g., 'bitcoin', 'ethereum')
        
    Returns:
        Formatted string with market data
    """
    try:
        data = cg.get_coin_by_id(
            id=coin_id,
            localization=False,
            tickers=False,
            market_data=True,
            community_data=False,
            developer_data=False
        )
        
        market = data.get("market_data", {})
        
        return f"""
Crypto Market Data: {data.get('name', coin_id).upper()}
Symbol: {data.get('symbol', 'N/A').upper()}
--------------------------------
Current Price: ${market.get('current_price', {}).get('usd', 0):,.2f}
Market Cap: ${market.get('market_cap', {}).get('usd', 0):,.0f}
24h Volume: ${market.get('total_volume', {}).get('usd', 0):,.0f}
--------------------------------
24h Change: {market.get('price_change_percentage_24h', 0):.2f}%
7d Change: {market.get('price_change_percentage_7d', 0):.2f}%
30d Change: {market.get('price_change_percentage_30d', 0):.2f}%
--------------------------------
All-Time High: ${market.get('ath', {}).get('usd', 0):,.2f}
ATH Date: {market.get('ath_date', {}).get('usd', 'N/A')[:10]}
All-Time Low: ${market.get('atl', {}).get('usd', 0):,.2f}
ATL Date: {market.get('atl_date', {}).get('usd', 'N/A')[:10]}
"""
    except Exception as e:
        logger.error(f"CoinGecko error for {coin_id}: {e}")
        return f"Error fetching market data for {coin_id}: {str(e)}"

def get_trending_crypto() -> str:
    """
    Gets the top trending cryptocurrencies in the last 24 hours.
    
    Returns:
        Formatted string with trending coins
    """
    try:
        data = cg.get_search_trending()
        coins = data.get('coins', [])
        
        if not coins:
            return "No trending coins data available"
            
        summary = ["=== TRENDING CRYPTOCURRENCIES (24h) ===\n"]
        
        for i, item in enumerate(coins[:10], 1):
            coin = item.get('item', {})
            summary.append(
                f"{i}. {coin.get('name')} ({coin.get('symbol', 'N/A').upper()})"
                f" - Rank #{coin.get('market_cap_rank', 'N/A')}"
            )
            
        return "\n".join(summary)
    except Exception as e:
        logger.error(f"CoinGecko error: {e}")
        return f"Error fetching trending coins: {str(e)}"

def search_crypto(query: str) -> str:
    """
    Searches for cryptocurrencies by name or symbol.
    
    Args:
        query: Search term (e.g., 'bitcoin', 'BTC', 'ethereum')
        
    Returns:
        Formatted string with search results
    """
    try:
        data = cg.search(query=query)
        coins = data.get('coins', [])
        
        if not coins:
            return f"No results found for '{query}'"
            
        summary = [f"=== SEARCH RESULTS FOR '{query}' ===\n"]
        
        for coin in coins[:10]:
            summary.append(
                f"• {coin.get('name')} ({coin.get('symbol', 'N/A').upper()})"
                f" - ID: {coin.get('id')} - Rank #{coin.get('market_cap_rank', 'N/A')}"
            )
            
        summary.append("\nUse the 'id' with get_crypto_market_data() for detailed info")
        return "\n".join(summary)
    except Exception as e:
        logger.error(f"CoinGecko search error: {e}")
        return f"Error searching for '{query}': {str(e)}"
