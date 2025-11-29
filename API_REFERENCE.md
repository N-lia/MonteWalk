# QuantAgent API Reference

Complete reference for all tools, resources, and prompts in the QuantAgent MCP server.

---

## Table of Contents

- [Tools (25)](#tools)
  - [Market Data (3)](#market-data)
  - [Execution (4)](#execution)
  - [Risk Management (4)](#risk-management)
  - [Backtesting (2)](#backtesting)
  - [Technical Analysis (3)](#technical-analysis)
  - [Portfolio Optimization (2)](#portfolio-optimization)
  - [News & Sentiment (3)](#news--sentiment)
  - [Watchlist (2)](#watchlist)
  - [Cryptocurrency (4)](#cryptocurrency)
  - [Logging (1)](#logging)
- [Resources (4)](#resources)
- [Prompts (2)](#prompts)

---

## Tools

### Market Data

#### `get_price`

Retrieves historical price data (OHLCV) for a given symbol.

**Parameters:**
- `symbol` (str): Ticker symbol (e.g., 'AAPL', 'BTC-USD')
- `interval` (Literal): Data interval - "1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo" (default: "1d")
- `period` (Literal): Data period - "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max" (default: "1y")

**Returns:** `List[Dict[str, Any]]` - List of OHLCV data dictionaries

**Example:**
```python
get_price("AAPL", interval="1d", period="1mo")
# Returns: [{"Date": "2024-01-01", "Open": 150.0, "High": 155.0, ...}, ...]
```

---

#### `get_fundamentals`

Fetches fundamental metrics for a symbol.

**Parameters:**
- `symbol` (str): Ticker symbol

**Returns:** `Dict[str, Any]` - Dictionary with P/E ratio, market cap, margins, etc.

**Example:**
```python
get_fundamentals("AAPL")
# Returns: {"pe_ratio": 28.5, "market_cap": 2800000000000, ...}
```

---

#### `get_orderbook`

Placeholder for order book data (currently returns mock data).

**Parameters:**
- `symbol` (str): Ticker symbol

**Returns:** `str` - Order book representation

---

### Execution

#### `place_order`

Submits a market or limit order to the paper trading exchange with simulated slippage and transaction costs.

**Parameters:**
- `symbol` (str): Ticker symbol
- `side` (Literal["buy", "sell"]): Order side
- `qty` (float): Quantity to trade
- `order_type` (Literal["market", "limit"]): Order type (default: "market")
- `limit_price` (Optional[float]): Required if order_type is "limit"

**Returns:** `str` - Execution confirmation or error message

**Example:**
```python
place_order("AAPL", "buy", 10, "market")
# Returns: "ORDER FILLED: Bought 10 shares of AAPL at $150.08..."
```

**Pre-trade Risk Checks:**
- Validates trade doesn't exceed 50% of available cash
- Ensures positive quantity
- Checks symbol price availability

---

#### `cancel_order`

Cancels a pending order (currently a placeholder for paper trading).

**Parameters:**
- `order_id` (str): Order ID to cancel

**Returns:** `str` - Cancellation confirmation

---

#### `get_positions`

Returns current portfolio state (cash and positions).

**Returns:** `Dict[str, Any]` - Portfolio dictionary

**Example:**
```python
get_positions()
# Returns: {"cash": 95000.0, "positions": {"AAPL": 10, "MSFT": 5}}
```

---

#### `flatten`

Closes all open positions at market price.

**Returns:** `str` - Summary of closed positions

**Example:**
```python
flatten()
# Returns: "Sold 10 AAPL at $150.00. Sold 5 MSFT at $380.00. All positions closed."
```

---

### Risk Management

#### `portfolio_risk`

Calculates portfolio volatility (annualized standard deviation).

**Returns:** `str` - Portfolio volatility percentage

**Example:**
```python
portfolio_risk()
# Returns: "Portfolio Volatility: 18.45% (annualized)"
```

---

#### `var`

Calculates Value at Risk (VaR) using historical simulation.

**Parameters:**
- `confidence` (float): Confidence level (default: 0.95)

**Returns:** `str` - VaR estimate

**Example:**
```python
var(confidence=0.95)
# Returns: "VaR (95% confidence): $2,450 over 1 day"
```

---

#### `max_drawdown`

Calculates the maximum drawdown of the portfolio.

**Returns:** `str` - Maximum drawdown percentage

**Example:**
```python
max_drawdown()
# Returns: "Max Drawdown: -12.34%"
```

---

#### `monte_carlo_simulation`

Runs Monte Carlo simulation using Geometric Brownian Motion to forecast potential portfolio paths.

**Parameters:**
- `simulations` (int): Number of simulation paths (default: 1000)
- `days` (int): Forecast horizon in days (default: 252)

**Returns:** `str` - Simulation summary with percentiles

**Example:**
```python
monte_carlo_simulation(simulations=500, days=30)
# Returns: "Monte Carlo Simulation (500 paths, 30 days)
#           5th percentile: -$1,200
#           50th percentile: +$450
#           95th percentile: +$3,100"
```

---

### Backtesting

#### `run_backtest`

Backtests a simple Moving Average Crossover strategy with transaction costs.

**Parameters:**
- `symbol` (str): Ticker symbol
- `fast_ma` (int): Fast moving average period
- `slow_ma` (int): Slow moving average period
- `start_date` (str): Start date (default: "2020-01-01")
- `end_date` (str): End date (default: "2023-12-31")

**Returns:** `str` - Backtest results with returns and metrics

**Example:**
```python
run_backtest("AAPL", fast_ma=10, slow_ma=50, start_date="2023-01-01", end_date="2023-12-31")
# Returns: "Backtest Results: Total Return: 15.2%, Buy & Hold: 48.5%, Sharpe: 0.65"
```

---

#### `walk_forward_analysis`

Performs rolling walk-forward analysis for out-of-sample validation.

**Parameters:**
- `symbol` (str): Ticker symbol
- `start_date` (str): Start date (default: "2020-01-01")
- `end_date` (str): End date (default: "2023-12-31")
- `train_months` (int): Training window in months (default: 12)
- `test_months` (int): Testing window in months (default: 3)

**Returns:** `str` - Walk-forward results summary

**Example:**
```python
walk_forward_analysis("AAPL", train_months=12, test_months=3)
# Returns: "Walk Forward Results: Window 1: Train 12.3%, Test -2.1%..."
```

---

### Technical Analysis

#### `compute_indicators`

Calculates technical indicators (RSI, MACD, Bollinger Bands).

**Parameters:**
- `symbol` (str): Ticker symbol
- `indicators` (List[str]): List of indicators (default: ["RSI", "MACD"])

**Returns:** `str` - JSON string of indicator values

**Example:**
```python
compute_indicators("AAPL", indicators=["RSI", "MACD", "BBANDS"])
# Returns: JSON with indicator values for last 10 days
```

---

#### `rolling_stats`

Computes rolling mean and volatility.

**Parameters:**
- `symbol` (str): Ticker symbol
- `window` (int): Rolling window size (default: 20)

**Returns:** `str` - JSON string of rolling statistics

---

#### `get_technical_summary`

Performs comprehensive technical analysis and returns a clear Buy/Sell/Neutral signal.

**Parameters:**
- `symbol` (str): Ticker symbol

**Returns:** `str` - Technical summary with signal

**Example:**
```python
get_technical_summary("AAPL")
# Returns: "Technical Summary for AAPL:
#           Signal: BUY (Score: 2)
#           Price: $175.50
#           - RSI is Neutral (55.32)
#           - MACD Bullish Crossover
#           - Price above 50 SMA..."
```

**Scoring Logic:**
- RSI: Oversold (<30) = +1, Overbought (>70) = -1
- MACD: Bullish crossover = +1, Bearish = -1
- 50 SMA: Price above = +1, below = -1
- 200 SMA: Price above = +1, below = -1

**Signals:**
- Score ≥2: STRONG BUY
- Score =1: BUY
- Score =0: NEUTRAL
- Score =-1: SELL
- Score ≤-2: STRONG SELL

---

### Portfolio Optimization

#### `mean_variance_optimize`

Calculates optimal portfolio weights using Mean-Variance Optimization (maximizes Sharpe ratio).

**Parameters:**
- `tickers` (List[str]): List of ticker symbols
- `lookback` (str): Lookback period (default: "1y")

**Returns:** `str` - Optimal weights dictionary

**Example:**
```python
mean_variance_optimize(["AAPL", "MSFT", "GOOGL"])
# Returns: "Optimal Weights (Max Sharpe): {'AAPL': 0.45, 'MSFT': 0.32, 'GOOGL': 0.23}"
```

---

#### `risk_parity`

Calculates weights based on Inverse Volatility (Naive Risk Parity).

**Parameters:**
- `tickers` (List[str]): List of ticker symbols

**Returns:** `str` - Risk parity weights

**Example:**
```python
risk_parity(["AAPL", "MSFT"])
# Returns: "Risk Parity Weights: {'AAPL': 0.52, 'MSFT': 0.48}"
```

---

### News & Sentiment

#### `get_news`

Retrieves recent news headlines for a symbol (yfinance → NewsAPI → GNews fallback).

**Parameters:**
- `symbol` (str): Ticker symbol
- `max_items` (int): Maximum news items (default: 10)

**Returns:** `str` - JSON string of news articles

**Example:**
```python
get_news("AAPL", max_items=5)
# Returns: JSON array of news: [{"title": "...", "publisher": "...", "link": "..."}, ...]
```

---

#### `analyze_sentiment`

Analyzes sentiment of text using FinBERT (Modal).

**Parameters:**
- `text` (str): Text to analyze

**Returns:** `Dict[str, Any]` - Sentiment analysis with polarity and subjectivity

**Example:**
```python
analyze_sentiment("Apple announces record-breaking earnings!")
# Returns: {"text": "Apple announces...", "polarity": 0.98, "subjectivity": 0.0, "classification": "POSITIVE", "model": "FinBERT (Modal Public)"}
```

**Classification:**
- Polarity >0.2: POSITIVE
- Polarity <-0.2: NEGATIVE
- Otherwise: NEUTRAL

---

#### `get_symbol_sentiment`

Fetches news and calculates aggregate sentiment for a symbol.

**Parameters:**
- `symbol` (str): Ticker symbol

**Returns:** `str` - Sentiment summary

**Example:**
```python
get_symbol_sentiment("AAPL")
# Returns: "Sentiment Analysis for AAPL (10 articles):
#           Average Polarity: 0.35
#           Market Sentiment: BULLISH"
```

---

### Watchlist

#### `add_to_watchlist`

Adds a symbol to the monitoring watchlist.

**Parameters:**
- `symbol` (str): Ticker symbol

**Returns:** `str` - Confirmation message

**Example:**
```python
add_to_watchlist("TSLA")
# Returns: "Added TSLA to watchlist."
```

---

#### `remove_from_watchlist`

Removes a symbol from the watchlist.

**Parameters:**
- `symbol` (str): Ticker symbol

**Returns:** `str` - Confirmation message

---

### Cryptocurrency

#### `get_crypto_price`

Gets current price of a cryptocurrency using CoinGecko API.

**Parameters:**
- `coin_id` (str): CoinGecko ID (e.g., 'bitcoin', 'ethereum', 'solana')
- `vs_currency` (str): Currency to compare (default: "usd")

**Returns:** `Dict[str, Any]` - Price data

**Example:**
```python
get_crypto_price("bitcoin")
# Returns: {"coin": "bitcoin", "price": 97832.0, "market_cap": ..., "24h_change": 1.34}
```

---

#### `get_crypto_market_data`

Gets comprehensive market data for a cryptocurrency.

**Parameters:**
- `coin_id` (str): CoinGecko ID

**Returns:** `str` - Formatted market data

**Example:**
```python
get_crypto_market_data("ethereum")
# Returns: "Crypto Market Data: ETHEREUM
#           Current Price: $3,450.23
#           24h Change: +2.5%
#           All-Time High: $4,878.26..."
```

---

#### `get_trending_crypto`

Gets the top trending cryptocurrencies in the last 24 hours.

**Returns:** `str` - List of trending coins

**Example:**
```python
get_trending_crypto()
# Returns: "=== TRENDING CRYPTOCURRENCIES (24h) ===
#           1. Bitcoin (BTC) - Rank #1
#           2. Dogecoin (DOGE) - Rank #8..."
```

---

#### `search_crypto`

Searches for cryptocurrencies by name or symbol.

**Parameters:**
- `query` (str): Search term

**Returns:** `str` - Search results

**Example:**
```python
search_crypto("cardano")
# Returns: "=== SEARCH RESULTS FOR 'cardano' ===
#           • Cardano (ADA) - ID: cardano - Rank #9..."
```

---

### Logging

#### `log_action`

Logs an agent action or reasoning step for audit purposes.

**Parameters:**
- `action_type` (str): Category (e.g., 'REASONING', 'TRADE_DECISION', 'ERROR')
- `details` (str): Description of the action

**Returns:** `str` - Confirmation

**Example:**
```python
log_action("TRADE_DECISION", "Decided to buy AAPL due to positive technical signals")
# Returns: "Action logged successfully."
```

---

## Resources

Resources provide live, read-only data that is automatically available to the AI without explicit tool calls.

### `portfolio://summary`

Returns a live summary of the portfolio (cash, positions, equity).

**Format:**
```
=== PORTFOLIO SUMMARY ===
Cash: $95,000.00
Positions: 2
--- Holdings ---
AAPL: 10 shares
MSFT: 5 shares
```

---

### `market://watchlist`

Returns live prices for all symbols in the watchlist.

**Format:**
```
=== MARKET WATCHLIST ===
AAPL: $175.50
TSLA: $245.30
```

---

### `news://latest`

Returns the latest headline for each symbol in the watchlist.

**Format:**
```
=== LATEST NEWS (Watchlist) ===
[AAPL] Apple announces new AI features (Bloomberg)
[TSLA] Tesla hits production milestone (Reuters)
```

---

### `crypto://trending`

Returns the top 10 trending cryptocurrencies.

**Format:**
```
=== TRENDING CRYPTOCURRENCIES (24h) ===
1. Bitcoin (BTC) - Rank #1
2. Ethereum (ETH) - Rank #2
...
```

---

## Prompts

Prompts are pre-defined workflows that guide the AI through complex, multi-step analyses.

### `morning_briefing`

Generates a comprehensive morning trading briefing.

**Context Included:**
- Current portfolio (cash + positions)
- Watchlist symbols

**Workflow:**
1. Review performance of held positions
2. Check watchlist for significant moves
3. Summarize top market news
4. Suggest risk adjustments

**Usage:**
```
@QuantAgent /morning_briefing
```

---

### `analyze_ticker`

Performs a deep-dive analysis on a specific ticker.

**Parameters:**
- `symbol` (str): Ticker to analyze

**Workflow:**
1. Fetch price trends (1y and 5d)
2. Get fundamentals (P/E, margins)
3. Analyze news sentiment
4. Compute technical indicators

**Output:**
- Executive Summary (Buy/Sell/Hold)
- Key Risks
- Technical Levels (Support/Resistance)

**Usage:**
```
@QuantAgent /analyze_ticker TSLA
```

---

## Quick Reference Card

| Category | Tool Count | Key Tools |
|----------|------------|-----------|
| Market Data | 3 | `get_price`, `get_fundamentals` |
| Execution | 4 | `place_order`, `get_positions`, `flatten` |
| Risk | 4 | `portfolio_risk`, `var`, `monte_carlo_simulation` |
| Backtesting | 2 | `run_backtest`, `walk_forward_analysis` |
| Technical | 3 | `get_technical_summary`, `compute_indicators` |
| Portfolio Opt | 2 | `mean_variance_optimize`, `risk_parity` |
| News | 3 | `get_news`, `get_symbol_sentiment` |
| Watchlist | 2 | `add_to_watchlist`, `remove_from_watchlist` |
| Crypto | 4 | `get_crypto_price`, `get_trending_crypto` |
| Logging | 1 | `log_action` |
| **Total** | **25** | |

---

## Common Workflows

### Execute a Trade
```
1. get_price("AAPL") - Check current price
2. get_technical_summary("AAPL") - Get buy/sell signal
3. portfolio_risk() - Check current risk
4. place_order("AAPL", "buy", 10) - Execute
```

### Risk Analysis
```
1. get_positions() - See current holdings
2. portfolio_risk() - Check volatility
3. var(0.99) - Check worst-case scenario
4. monte_carlo_simulation(1000, 30) - Forecast outcomes
```

### Research a Stock
```
1. get_fundamentals("TSLA") - Check valuation
2. get_news("TSLA", 10) - Read headlines
3. get_symbol_sentiment("TSLA") - Gauge mood
4. get_technical_summary("TSLA") - Technical signal
```

---

## Error Handling

All tools implement robust error handling:
- **Market Data**: Returns error if symbol not found or API unavailable
- **Execution**: Pre-trade risk checks prevent invalid trades
- **Risk Tools**: Return "Portfolio empty" if no positions
- **News**: Automatic fallback: yfinance → NewsAPI → GNews
- **Crypto**: Graceful degradation if CoinGecko API fails

---

## Rate Limits & Quotas

| API | Free Tier Limit | Status |
|-----|----------------|--------|
| yfinance | ~2,000/hour | No key required |
| NewsAPI | 100 requests/day | Optional key |
| CoinGecko | 10-50 calls/minute | No key required |
| GNews | Unlimited (scraped) | No key required |

---

## Support & Documentation

- **Main README**: [`README.md`](file:///home/mario/MonteWalk/README.md)
- **VSCode Setup**: [`VSCODE_SETUP.md`](file:///home/mario/MonteWalk/VSCODE_SETUP.md)
- **NewsAPI Setup**: [`NEWSAPI_SETUP.md`](file:///home/mario/MonteWalk/NEWSAPI_SETUP.md)
- **Audit Report**: [`AUDIT_REPORT.md`](file:///home/mario/MonteWalk/AUDIT_REPORT.md)
