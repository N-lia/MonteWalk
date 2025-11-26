import gradio as gr
import logging
import sys
from typing import List, Callable
from dotenv import load_dotenv

load_dotenv()

from config import LOG_FILE
from tools.market_data import get_price, get_fundamentals, get_orderbook
from tools.execution import place_order, cancel_order, get_positions, flatten, get_order_history
from tools.risk_engine import portfolio_risk, var, max_drawdown, monte_carlo_simulation
from tools.backtesting import run_backtest, walk_forward_analysis
from tools.feature_engineering import compute_indicators, rolling_stats, get_technical_summary
from tools.portfolio_optimizer import mean_variance_optimize, risk_parity
from tools.logger import setup_logging, log_action
from tools.news_intelligence import get_news, analyze_sentiment, get_symbol_sentiment, get_latest_news_for_watchlist
from tools.watchlist import add_to_watchlist, remove_from_watchlist, get_watchlist_data, _load_watchlist
from tools.crypto_data import get_crypto_price, get_crypto_market_data, get_trending_crypto, search_crypto
from tools.alpaca_broker import get_broker


setup_logging()
logger = logging.getLogger(__name__)

# --- Local Tools ---

def health_check() -> str:
    """Returns the health status of the MonteWalk server."""
    return "MonteWalk Server is running and healthy."

def get_account_info() -> str:
    """
    Get detailed Alpaca account information including equity, buying power, and day trade status.
    """
    try:
        broker = get_broker()
        account = broker.get_account()
        
        return f"""
=== ALPACA ACCOUNT INFO ===
Cash: ${account['cash']:,.2f}
Equity: ${account['equity']:,.2f}
Buying Power: ${account['buying_power']:,.2f}
Portfolio Value: ${account['portfolio_value']:,.2f}
Pattern Day Trader: {account['pattern_day_trader']}
Day Trade Count: {account['daytrade_count']}
"""
    except Exception as e:
        return f"ERROR: Failed to get account info - {str(e)}"

def get_portfolio_summary() -> str:
    """
    Returns a live summary of the portfolio from Alpaca (Cash, Positions, Equity).
    """
    try:
        broker = get_broker()
        account = broker.get_account()
        positions = broker.get_all_positions()
        
        summary = [
            "=== PORTFOLIO SUMMARY (Alpaca Paper Trading) ===",
            f"Cash: ${account['cash']:,.2f}",
            f"Equity: ${account['equity']:,.2f}",
            f"Buying Power: ${account['buying_power']:,.2f}",
            f"Positions: {len(positions)}",
            "--- Holdings ---"
        ]
        
        for symbol, details in positions.items():
            qty = details['qty']
            price = details['current_price']
            pl = details['unrealized_pl']
            pl_pct = details['unrealized_plpc'] * 100
            summary.append(
                f"{symbol}: {qty} shares @ ${price:.2f} "
                f"(P/L: ${pl:,.2f} / {pl_pct:+.2f}%)"
            )
            
        if not positions:
            summary.append("(No open positions)")
            
        return "\n".join(summary)
    except Exception as e:
        return f"ERROR: Failed to get portfolio - {str(e)}\n\nMake sure your Alpaca credentials are set in .env file."

def get_watchlist_resource() -> str:
    """
    Returns a live view of the watchlist with current prices.
    """
    data = get_watchlist_data()
    if not data:
        return "Watchlist is empty. Use add_to_watchlist() to track symbols."
        
    summary = ["=== MARKET WATCHLIST ==="]
    for symbol, info in data.items():
        if "error" in info:
            summary.append(f"{symbol}: ERROR - {info['error']}")
        else:
            price = info.get('price', 0.0)
            summary.append(f"{symbol}: ${price:,.2f}")
            
    return "\n".join(summary)

def get_news_resource() -> str:
    """
    Returns the latest news headlines for the watchlist.
    """
    return get_latest_news_for_watchlist()

def get_crypto_resource() -> str:
    """
    Returns the top trending cryptocurrencies.
    """
    return get_trending_crypto()

# --- Prompts (Converted to Tools) ---

def morning_briefing() -> str:
    """
    Generates a morning briefing prompt with Portfolio and Watchlist context.
    """
    portfolio = get_positions()
    owned_symbols = list(portfolio.get('positions', {}).keys())
    watchlist = _load_watchlist()
    
    # Detect sync issues
    owned_but_not_watched = [s for s in owned_symbols if s not in watchlist]
    
    # Construct a context-rich prompt
    return f"""
Please generate a Morning Trading Briefing.

STEP 0: SYNC WATCHLIST (Auto-maintenance)
{f"⚠️ Detected {len(owned_but_not_watched)} owned symbols not in watchlist: {owned_but_not_watched}" if owned_but_not_watched else "✅ Watchlist is synced with portfolio"}
- If out of sync, automatically add owned symbols to watchlist
- Use `add_to_watchlist(symbol)` for each missing symbol

CONTEXT:
1. Portfolio:
   - Cash: ${portfolio.get('cash', 0):,.2f}
   - Equity: ${portfolio.get('equity', 0):,.2f}
   - Positions: {owned_symbols}

2. Watchlist:
   - Symbols: {watchlist}

BRIEFING STEPS:
1. Review the performance of my held positions (check today's moves)
2. Check the watchlist for any significant moves or news
3. Summarize the top market news affecting these specific assets
4. Run a quick risk check: `portfolio_risk()` and `var(0.95)`
5. Suggest any risk adjustments based on my current exposure

OUTPUT FORMAT:
📊 **Portfolio Summary**: [Cash, positions with P/L]
📰 **Market News**: [Top 3 headlines affecting your holdings]
⚠️ **Risk Status**: [Volatility, VaR, any concerns]
💡 **Today's Recommendations**: [Actions to consider]
"""

def analyze_ticker(symbol: str) -> str:
    """
    Deep dive analysis prompt for a specific ticker.
    """
    return f"""
Please perform a comprehensive analysis on {symbol}.

STEPS:
1. Use `get_price` to check the trend (1y and 5d).
2. Use `get_fundamentals` to check valuation (PE, Margins).
3. Use `get_news` and `analyze_sentiment` to gauge market mood.
4. Use `compute_indicators` (RSI, MACD) for technicals.

OUTPUT:
- Executive Summary (Buy/Sell/Hold)
- Key Risks
- Technical Levels (Support/Resistance)
"""

def risk_analysis() -> str:
    """
    Comprehensive risk analysis prompt for the current portfolio.
    """
    portfolio = get_positions()
    positions = portfolio.get('positions', {})
    
    return f"""
Please perform a comprehensive risk analysis on my portfolio.

CURRENT HOLDINGS:
{dict(positions)}

ANALYSIS STEPS:
1. Use `portfolio_risk()` to calculate current volatility
2. Use `var(confidence=0.95)` to estimate potential losses
3. Use `max_drawdown()` to see historical worst-case
4. Use `monte_carlo_simulation(1000, 30)` to forecast 30-day outcomes
5. Check correlation risk (are all positions in same sector?)

OUTPUT:
- Risk Rating (Low/Medium/High)
- Specific Concerns (concentration, volatility, etc.)
- Recommended Actions (hedge, reduce exposure, etc.)
"""

def backtest_strategy(symbol: str, fast_ma: int = 10, slow_ma: int = 50) -> str:
    """
    Backtesting workflow prompt.
    """
    return f"""
Please backtest a trading strategy for {symbol}.

STRATEGY:
- Moving Average Crossover: Fast MA={fast_ma}, Slow MA={slow_ma}

STEPS:
1. Use `run_backtest("{symbol}", {fast_ma}, {slow_ma}, "2020-01-01", "2023-12-31")` for historical test
2. Use `walk_forward_analysis("{symbol}")` for out-of-sample validation
3. Compare strategy return vs Buy & Hold
4. Analyze the Sharpe ratio and max drawdown

OUTPUT:
- Is this strategy viable? (Yes/No/Maybe)
- Key weaknesses of the strategy
- Suggested parameter improvements
"""

def crypto_market_update() -> str:
    """
    Cryptocurrency market analysis prompt.
    """
    return f"""
Please generate a Crypto Market Update.

STEPS:
1. Use `get_trending_crypto()` to see what's hot
2. Use `get_crypto_market_data("bitcoin")` for BTC analysis
3. Use `get_crypto_market_data("ethereum")` for ETH analysis
4. Use `get_crypto_price()` for any other coins of interest

OUTPUT:
- Market Sentiment (Bullish/Bearish/Neutral)
- Top 3 Trending Coins with analysis
- BTC & ETH price levels and support/resistance
- Any notable price movements or news
"""

def portfolio_rebalance(target_symbols: str = "AAPL,MSFT,GOOGL") -> str:
    """
    Portfolio rebalancing workflow prompt.
    """
    symbols = [s.strip() for s in target_symbols.split(',')]
    
    return f"""
Please help me rebalance my portfolio to include: {', '.join(symbols)}

STEPS:
1. Use `get_positions()` to see current holdings
2. Use `mean_variance_optimize({symbols})` to get optimal weights
3. Use `risk_parity({symbols})` as an alternative allocation
4. Compare both strategies and explain trade-offs
5. Calculate what orders I need to place to reach optimal allocation

OUTPUT:
- Recommended allocation (with reasoning)
- Specific buy/sell orders to execute
- Expected impact on portfolio risk
- Implementation timeline (all at once or gradual?)
"""

def sync_watchlist() -> str:
    """
    Intelligent watchlist synchronization with portfolio holdings.
    """
    portfolio = get_positions()
    owned_symbols = list(portfolio.get('positions', {}).keys())
    watchlist = _load_watchlist()
    
    # Find discrepancies
    owned_but_not_watched = [s for s in owned_symbols if s not in watchlist]
    watched_but_not_owned = [s for s in watchlist if s not in owned_symbols]
    
    return f"""
Please synchronize my watchlist with my actual portfolio holdings.

CURRENT STATE:
1. Portfolio Holdings: {owned_symbols}
2. Watchlist: {watchlist}

DISCREPANCIES DETECTED:
- Owned but NOT in watchlist: {owned_but_not_watched if owned_but_not_watched else 'None ✅'}
- In watchlist but NOT owned: {watched_but_not_owned if watched_but_not_owned else 'None ✅'}

SYNCHRONIZATION STEPS:
1. **Auto-add owned symbols to watchlist**:
   - For each symbol in {owned_but_not_watched}:
     - Use `add_to_watchlist(symbol)` to track it
     - Confirm: "Added [symbol] to watchlist (now tracking owned position)"

2. **Handle watched-but-not-owned symbols** (your choice):
   - Option A (Conservative): Keep them (you might want to buy later)
   - Option B (Clean): Remove old symbols you've sold:
     - For each symbol in {watched_but_not_owned}:
       - Check if you recently sold it (use `get_order_history()`)
       - If sold, use `remove_from_watchlist(symbol)`
       - If never owned, keep it (research symbol)

3. **Verify sync**:
   - Confirm all owned symbols are now in watchlist
   - List any research symbols (watched but not owned)

OUTPUT FORMAT:
✅ Synchronized: [symbols added to watchlist]
🔍 Research Symbols: [symbols in watchlist but not owned]
📊 Watchlist now tracking [X] symbols ([Y] owned, [Z] research)

AUTOMATION NOTE:
Run this sync automatically:
- After any trade execution
- During morning briefing
- Before risk analysis
"""

# --- Tool Organization ---

tools_map = {
    "Dashboard": [health_check, get_account_info, get_portfolio_summary],
    "Market Data": [get_price, get_fundamentals, get_orderbook],
    "Execution": [place_order, cancel_order, get_positions, flatten, get_order_history],
    "Risk Engine": [portfolio_risk, var, max_drawdown, monte_carlo_simulation],
    "Backtesting": [run_backtest, walk_forward_analysis],
    "Feature Engineering": [compute_indicators, rolling_stats, get_technical_summary],
    "Portfolio Opt": [mean_variance_optimize, risk_parity],
    "News & Sentiment": [get_news, analyze_sentiment, get_symbol_sentiment, get_news_resource],
    "Watchlist": [add_to_watchlist, remove_from_watchlist, get_watchlist_resource, sync_watchlist],
    "Crypto": [get_crypto_price, get_crypto_market_data, get_trending_crypto, search_crypto, get_crypto_resource, crypto_market_update],
    "Prompts": [morning_briefing, analyze_ticker, risk_analysis, backtest_strategy, portfolio_rebalance],
    "Utils": [log_action]
}

import inspect

def create_interface(tool: Callable):
    """Creates a Gradio Interface for a tool by inferring inputs/outputs."""
    sig = inspect.signature(tool)
    
    inputs = []
    for name, param in sig.parameters.items():
        if param.annotation == int:
            inputs.append(gr.Number(label=name, precision=0))
        elif param.annotation == float:
            inputs.append(gr.Number(label=name))
        elif param.annotation == bool:
            inputs.append(gr.Checkbox(label=name))
        else:
            inputs.append(gr.Textbox(label=name))
    outputs = gr.Textbox(label="Result")
    
    return gr.Interface(
        fn=tool,
        inputs=inputs,
        outputs=outputs,
        flagging_mode="never"
    )

# --- Gradio App ---

with gr.Blocks(title="MonteWalk MCP Server") as demo:
    gr.Markdown("# MonteWalk MCP Server")
    gr.Markdown("This Gradio app exposes the MonteWalk trading tools as an MCP Server.")
    
    for category, tools in tools_map.items():
        with gr.Tab(category):
            for tool in tools:
                with gr.Accordion(tool.__name__, open=False):
                    create_interface(tool)

if __name__ == "__main__":
    logger.info("Starting MonteWalk Gradio MCP Server...")
    demo.launch(server_name="0.0.0.0", server_port=7860, mcp_server=True)
