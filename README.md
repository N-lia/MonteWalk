# MonteWalk 🚀

**An intelligent MCP server that brings institutional-grade quantitative finance tools to conversational AI.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)

> Trade smarter, not harder. Ask questions in plain English, get institution-level analysis powered by Monte Carlo simulations, risk metrics, and real broker integration.

---

## 🎯 What is MonteWalk?

MonteWalk is a **Model Context Protocol (MCP) server** that transforms AI assistants like Claude into sophisticated quantitative trading analysts. Instead of manually calculating risk metrics or backtesting strategies in spreadsheets, you simply ask questions:

- *"What's my portfolio risk right now?"*
- *"Should I buy AAPL based on technical analysis?"*
- *"Run a Monte Carlo simulation on my holdings for the next 30 days"*
- *"Backtest a moving average crossover strategy on Tesla"*

### The Problem We Solve

**Retail traders** use basic tools (journals, price alerts) that only show you *after* you lost money.  
**Professional traders** use Bloomberg terminals ($25k/year) with real-time risk analytics.  
**MonteWalk** bridges this gap: **institutional-grade quant tools + conversational interface + $0 cost**.

---

## ✨ Key Features

### 📊 **Market Data Intelligence**
- **Multi-source aggregation**: Yahoo Finance, Alpaca, CoinGecko
- **Smart fallback chains**: Always get data, even if one API fails
- **Historical OHLCV data**: Custom intervals (1m to 1mo) and periods (1d to max)
- **Fundamentals**: P/E ratios, market cap, margins, earnings

### 💰 **Real Broker Integration**
- **Alpaca Paper Trading**: $100,000 virtual account with real market data
- **Live order execution**: Market and limit orders with full confirmation
- **Portfolio management**: Real-time positions, P/L tracking, buying power
- **Emergency controls**: One-click flatten all positions
- **Order history**: Complete audit trail of all trades

### ⚠️ **Advanced Risk Management**
- **Portfolio Volatility**: Annualized standard deviation with correlation matrix
- **Value at Risk (VaR)**: Historical simulation at configurable confidence levels
- **Maximum Drawdown**: Peak-to-trough analysis
- **Monte Carlo Simulation**: 
  - Geometric Brownian Motion with log returns
  - Cholesky decomposition for correlated assets
  - Percentile-based scenarios (5th, 50th, 95th)
  - Forecast 1-252 days ahead

### 📈 **Backtesting Engine**
- **Moving Average Crossover**: Standard momentum strategy
- **Transaction costs**: Realistic 10bps per trade
- **Walk Forward Analysis**: Rolling window optimization to prevent overfitting
- **Performance metrics**: Total return, Sharpe ratio, max drawdown

### 📉 **Technical Analysis**
- **Indicators**: RSI, MACD, Bollinger Bands, Moving Averages
- **Signal generation**: Buy/Sell/Hold recommendations with scoring
- **Rolling statistics**: Volatility, momentum, mean reversion

### 🎯 **Portfolio Optimization**
- **Mean-Variance Optimization**: Maximize Sharpe ratio using scipy
- **Risk Parity**: Inverse volatility weighting for balanced exposure
- **Rebalancing workflows**: Guided multi-step allocation strategies

### 🗞️ **News & Sentiment Analysis**
- **Multi-source news**: yfinance → NewsAPI → GNews (triple fallback)
- **NLP sentiment scoring**: TextBlob polarity and subjectivity
- **Aggregate analysis**: Symbol-level sentiment across multiple articles
- **Watchlist integration**: Latest headlines for all tracked symbols

### 🪙 **Cryptocurrency Support**
- **Real-time prices**: CoinGecko API for 10,000+ coins
- **Market data**: Volume, market cap, 24h change, ATH/ATL
- **Trending discovery**: Top coins in the last 24 hours
- **Search**: Find coins by name or symbol

### 🔍 **Watchlist Management**
- **Track symbols**: Add stocks and crypto to monitoring list
- **Live prices**: Auto-updating resource for all watchlist items
- **Integrated news**: Latest headlines for each symbol

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.12+**
- **Alpaca account** (free paper trading): [Sign up here](https://alpaca.markets)
- **(Optional) NewsAPI key** (free tier): [Get one here](https://newsapi.org)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/MonteWalk.git
cd MonteWalk

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install mcp yfinance pandas numpy scipy pandas_ta textblob gnews newsapi-python pycoingecko alpaca-py

# 4. Download NLP corpora for sentiment analysis
python -m textblob.download_corpora

# 5. Set up environment variables
cp .env.example .env
# Edit .env and add your Alpaca API keys
```

### Environment Configuration

Edit `.env` with your API credentials:

```bash
# Required: Alpaca Paper Trading
ALPACA_API_KEY=your_paper_key_here
ALPACA_SECRET_KEY=your_paper_secret_here

# Optional: NewsAPI (for enhanced news)
NEWSAPI_KEY=your_newsapi_key_here
```

> **Security Note**: Never commit your `.env` file! The `.gitignore` is pre-configured to exclude it.

### Running MonteWalk

```bash
# Start the MCP server
python server.py
```

The server will initialize all tools and wait for MCP client connections.

---

## 🔌 Connecting to Claude Desktop

Add MonteWalk to your Claude Desktop configuration:

**macOS/Linux**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "montewalk": {
      "command": "/absolute/path/to/MonteWalk/.venv/bin/python",
      "args": ["/absolute/path/to/MonteWalk/server.py"]
    }
  }
}
```

**Important**: Replace `/absolute/path/to/MonteWalk` with your actual installation path.

After updating the config:
1. Restart Claude Desktop
2. Look for the 🔌 MCP icon in the bottom right
3. Verify MonteWalk is connected

---

## 📚 Usage Examples

### Example 1: Portfolio Risk Analysis

```
You: What's my current portfolio risk?

Claude (using MonteWalk):
- Calls portfolio_risk()
- Calls var(confidence=0.95)
- Calls max_drawdown()
- Calls monte_carlo_simulation(1000, 30)

Response:
"Your portfolio has 18.5% annualized volatility. 
Value at Risk (95% confidence): You could lose $2,450 in a bad day.
Maximum historical drawdown: -12.3%
Monte Carlo forecast (30 days):
  - Worst case (5th percentile): -8.2%
  - Expected: +2.1%
  - Best case (95th percentile): +12.5%"
```

### Example 2: Stock Analysis

```
You: Should I buy Tesla? Analyze TSLA for me.

Claude (using MonteWalk):
- Calls get_price("TSLA", period="1y")
- Calls get_fundamentals("TSLA")
- Calls get_technical_summary("TSLA")
- Calls get_symbol_sentiment("TSLA")
- Calls get_news("TSLA", max_items=5)

Response:
"TSLA Technical Summary: SELL (Score: -2)
- Price: $242.50
- RSI: 72.3 (Overbought)
- MACD: Bearish crossover
- Below 50-day MA
News Sentiment: BEARISH (Polarity: -0.35)
Recent headlines show concerns about..."
```

### Example 3: Backtest a Strategy

```
You: Backtest a 10/50 MA crossover on Apple from 2020 to 2023

Claude (using MonteWalk):
- Calls run_backtest("AAPL", 10, 50, "2020-01-01", "2023-12-31")
- Calls walk_forward_analysis("AAPL")

Response:
"Backtest Results (AAPL 10/50 MA):
Total Return: 15.2% (vs Buy & Hold: 48.5%)
Sharpe Ratio: 0.65
Max Drawdown: -18.2%

Walk Forward Analysis shows the strategy underperformed 
in 3 of 4 test windows. Not recommended."
```

### Example 4: Execute a Trade

```
You: Buy 10 shares of Microsoft at market price

Claude (using MonteWalk):
- Calls get_price("MSFT") to check current price
- Calls validate_trade() for pre-trade risk checks
- Calls place_order("MSFT", "buy", 10, "market")

Response:
"ORDER FILLED: Bought 10 shares of MSFT at $380.25
Total cost: $3,802.50 (including $0.10 commission)
Remaining buying power: $96,197.40"
```

---

## 🛠️ Architecture

```
MonteWalk/
├── server.py                    # Main MCP server with tool/resource/prompt registration
├── config.py                    # Configuration and environment variables
│
├── tools/                       # Modular tool implementations
│   ├── market_data.py          # Yahoo Finance integration (OHLCV, fundamentals)
│   ├── execution.py            # Paper trading engine (orders, positions)
│   ├── alpaca_broker.py        # Alpaca API wrapper (real broker integration)
│   ├── risk_engine.py          # VaR, Monte Carlo, portfolio volatility
│   ├── backtesting.py          # Strategy backtesting and walk forward
│   ├── portfolio_optimizer.py  # Mean-variance, risk parity
│   ├── feature_engineering.py  # Technical indicators (RSI, MACD, BB)
│   ├── news_intelligence.py    # Multi-source news + sentiment analysis
│   ├── crypto_data.py          # CoinGecko cryptocurrency data
│   ├── watchlist.py            # Symbol tracking and monitoring
│   └── logger.py               # Audit logging
│
├── data/                        # Runtime state (gitignored)
│   ├── portfolio.json          # Current holdings and cash
│   ├── watchlist.json          # Tracked symbols
│   └── activity.log            # Trade audit trail
│
└── tests/                       # Test suite
    └── test_basic.py           # Core functionality tests
```

### Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Framework** | FastMCP | MCP server implementation |
| **Broker** | Alpaca API | Paper trading execution |
| **Market Data** | yfinance, Alpaca | OHLCV, fundamentals, real-time quotes |
| **Crypto Data** | CoinGecko | Cryptocurrency prices and trends |
| **News** | yfinance, NewsAPI, GNews | Multi-source headlines |
| **Sentiment** | TextBlob | Local NLP (no API required) |
| **Compute** | NumPy, SciPy, Pandas | Mathematical operations |
| **Technical Analysis** | pandas_ta | Indicators (RSI, MACD, etc.) |

---

## 📖 Complete Tool Reference

MonteWalk provides **25 tools**, **4 resources**, and **6 prompts**.

### Tools by Category

#### 🔹 Market Data (3 tools)
- `get_price(symbol, interval, period)` - Historical OHLCV data
- `get_fundamentals(symbol)` - P/E, market cap, margins
- `get_orderbook(symbol)` - Order book snapshot (placeholder)

#### 🔹 Execution (5 tools)
- `place_order(symbol, side, qty, order_type, limit_price)` - Execute trades
- `cancel_order(order_id)` - Cancel pending orders
- `get_positions()` - Current portfolio holdings
- `flatten()` - Close all positions immediately
- `get_order_history()` - Historical order activity
- `get_account_info()` - Alpaca account details

#### 🔹 Risk Management (4 tools)
- `portfolio_risk()` - Annualized volatility
- `var(confidence)` - Value at Risk
- `max_drawdown()` - Historical worst-case decline
- `monte_carlo_simulation(simulations, days)` - Probabilistic forecasting

#### 🔹 Backtesting (2 tools)
- `run_backtest(symbol, fast_ma, slow_ma, start_date, end_date)` - Strategy testing
- `walk_forward_analysis(symbol, train_months, test_months)` - Out-of-sample validation

#### 🔹 Technical Analysis (3 tools)
- `compute_indicators(symbol, indicators)` - RSI, MACD, Bollinger Bands
- `rolling_stats(symbol, window)` - Moving averages and volatility
- `get_technical_summary(symbol)` - Buy/Sell/Hold signal

#### 🔹 Portfolio Optimization (2 tools)
- `mean_variance_optimize(tickers)` - Max Sharpe ratio allocation
- `risk_parity(tickers)` - Equal risk contribution weights

#### 🔹 News & Sentiment (3 tools)
- `get_news(symbol, max_items)` - Headlines from multiple sources
- `analyze_sentiment(text)` - NLP polarity scoring
- `get_symbol_sentiment(symbol)` - Aggregate news sentiment

#### 🔹 Cryptocurrency (4 tools)
- `get_crypto_price(coin_id, vs_currency)` - Real-time crypto prices
- `get_crypto_market_data(coin_id)` - Comprehensive market stats
- `get_trending_crypto()` - Top 10 trending coins
- `search_crypto(query)` - Find coins by name/symbol

#### 🔹 Watchlist (2 tools)
- `add_to_watchlist(symbol)` - Track a symbol
- `remove_from_watchlist(symbol)` - Untrack a symbol

#### 🔹 Logging (1 tool)
- `log_action(action_type, details)` - Audit trail for decisions

### Resources (Auto-updating Context)

Resources provide live data to the AI without explicit tool calls:

- `portfolio://summary` - Cash, positions, P/L
- `market://watchlist` - Live prices for all tracked symbols
- `news://latest` - Latest headlines for watchlist
- `crypto://trending` - Top trending cryptocurrencies

### Prompts (Guided Workflows)

Prompts are pre-built multi-step analysis workflows:

- `morning_briefing()` - Portfolio review + news + risk assessment
- `analyze_ticker(symbol)` - Deep dive: technicals + fundamentals + sentiment
- `risk_analysis()` - Comprehensive portfolio risk report
- `backtest_strategy(symbol, fast_ma, slow_ma)` - Strategy validation
- `crypto_market_update()` - Crypto market overview
- `portfolio_rebalance(target_symbols)` - Allocation optimization

---

## 🔒 Security & Safety

### Built-in Safeguards

✅ **Paper Trading Only**: Hardcoded to Alpaca paper trading endpoint  
✅ **Environment Variables**: API keys never in source code  
✅ **Pre-Trade Risk Checks**: Validates position sizing before execution  
✅ **Audit Logging**: All trades logged to `data/activity.log`  
✅ **Data Isolation**: User data in `data/` directory (gitignored)  

### Best Practices

1. **Never commit `.env`**: Pre-configured in `.gitignore`
2. **Use paper trading first**: Test strategies before risking real money
3. **Review AI decisions**: Always verify trades before confirming
4. **Keep logs**: Monitor `data/activity.log` for audit trail
5. **Rotate API keys**: Regenerate Alpaca keys periodically

---

## 🧪 Testing

Run the test suite to verify your installation:

```bash
# Basic functionality tests
python tests/test_basic.py

# Individual component tests (optional)
python -m pytest tests/ -v
```

---

## 🐛 Troubleshooting

### Issue: "No module named 'mcp'"
**Solution**: Ensure virtual environment is activated and dependencies installed:
```bash
source .venv/bin/activate
pip install mcp yfinance pandas numpy scipy pandas_ta textblob gnews newsapi-python pycoingecko alpaca-py
```

### Issue: "Alpaca authentication failed"
**Solution**: Verify your `.env` file has correct paper trading keys:
1. Log into [alpaca.markets](https://alpaca.markets)
2. Navigate to Paper Trading dashboard
3. Regenerate API keys
4. Update `.env` with new credentials

### Issue: "Portfolio is empty" errors
**Solution**: The portfolio initializes on first trade. Either:
1. Place a test order: `place_order("AAPL", "buy", 1, "market")`
2. Or check if `data/portfolio.json` exists and is valid JSON

### Issue: "No news found for symbol"
**Solution**: 
1. Add NewsAPI key to `.env` for better coverage
2. Check symbol is valid (use `get_price(symbol)` first)
3. Try different symbol or wait (API rate limits)

---

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- [ ] Additional backtesting strategies (mean reversion, pairs trading)
- [ ] More portfolio optimization methods (Black-Litterman, HRP)
- [ ] Advanced sentiment analysis (FinBERT, social media)
- [ ] Database integration for historical tracking
- [ ] Web dashboard for visualization
- [ ] Additional broker integrations (IBKR, TD Ameritrade)

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Alpaca Markets** for free paper trading API
- **Yahoo Finance** for market data access
- **CoinGecko** for cryptocurrency data
- **Model Context Protocol** for the MCP framework
- **Anthropic** for Claude

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/MonteWalk/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/MonteWalk/discussions)

---

**Built with ❤️ for the MCP 1st Birthday Hackathon**

*Trade smarter. Risk less. Analyze more.*
