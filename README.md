---
title: MonteWalk
emoji: 🏔️
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 6.0.0
app_file: app.py
pinned: true
tags:
  - building-mcp-track-enterprise
  - building-mcp-track-consumer
  - MODAL.com
---

# 🏔️ MonteWalk

> **Institutional-grade quantitative trading tools for AI agents**  
> Built for the [MCP 1st Birthday Hackathon](https://huggingface.co/spaces/launch/mcp-1st-bday) 🎉

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)
[![Gradio 6](https://img.shields.io/badge/Gradio-6.0-orange.svg)](https://gradio.app)

**📊 MCP Server Stats:**  
🛠️ **25+ Tools** | 📡 **4 Resources** | 🎯 **6 Agentic Prompts**


---

## 🎯 The Problem

Retail traders face an **overwhelming flood** of market data, news, and analysis tools—but lack the institutional-grade infrastructure to make sense of it all:

- **Data Overload**: Thousands of stocks, crypto assets, news sources—impossible to monitor manually
- **Risk Blindness**: No access to professional risk metrics (VaR, drawdown, Monte Carlo)
- **Execution Friction**: Scattered tools across multiple platforms, no unified workflow
- **AI Disconnect**: Existing AI assistants can't access real-time market data or execute trades

What if your AI assistant could be your **quantitative analyst, risk manager, and trading desk**—all in one?

---

## ✨ The Solution

**MonteWalk** is a **Model Context Protocol (MCP) server** that transforms AI assistants like Claude into institutional-grade trading terminals. It provides:

### 🔌 **MCP Integration**
Connect to Claude Desktop, VSCode, or any MCP-compatible client to give your AI:
- Real-time market data (stocks, crypto, news)
- Portfolio management and execution
- Risk analytics and backtesting
- Intelligent workflows and automation

### 🎨 **Beautiful Gradio 6 Interface**
Test all tools through a polished, professional UI featuring:
- **Live Dashboard**: Portfolio, watchlist, crypto trends, news feed
- **Interactive Toolbox**: Direct access to 25+ trading tools
- **MCP Client Setup**: Copy-paste configuration for instant connection
- **Dark Theme**: Sleek glassmorphism design with smooth animations

### 🧠 **Agentic Workflows**
Pre-built prompts that guide AI through complex multi-step analyses:
- **Morning Briefing**: Portfolio review, market scan, risk check
- **Gamma Hunt**: Find unusual market activity and deep-dive top picks
- **Ticker Analysis**: Comprehensive research (fundamentals, technicals, sentiment)
- **Portfolio Rebalancing**: Optimize weights using modern portfolio theory

---

## 🚀 Key Features

### 📊 **Market Intelligence**
- **Multi-source Data**: Yahoo Finance, Alpaca, CoinGecko—all cached for speed
- **Crypto Support**: Live prices, trending coins, comprehensive market data
- **News Aggregation**: yfinance → NewsAPI → GNews fallback pipeline
- **Sentiment Analysis**: FinBERT-powered financial sentiment scoring (via Modal)
- **Unusual Activity Scanner**: Detect big movers, volume spikes, reversal candidates

### 📈 **Advanced Visualizations**
- **Candlestick Charts**: Professional OHLC charts with volume bars
- **Interactive Charts**: Line, bar, histogram, scatter, heatmap support
- **Dark Theme**: Charts styled to match UI with custom color palette
- **Base64 Encoding**: Charts returned as embeddable images for AI consumption
- **Integrated with Tools**: `get_price(visualize=True)`, `monte_carlo_simulation(visualize=True)`, etc.

### ⚡ **Paper Trading Engine**
- **$100K Virtual Capital**: Risk-free strategy testing on Alpaca Paper Trading
- **Smart Execution**: Simulated slippage and transaction costs
- **Pre-trade Risk Checks**: Prevents portfolio concentration >50%
- **Position Management**: Instant portfolio view and one-click flatten

### 🛡️ **Institutional Risk Analytics**
- **Value at Risk (VaR)**: Historical simulation at any confidence level
- **Monte Carlo Forecasting**: GBM-based portfolio path simulations
- **Volatility Metrics**: Annualized portfolio standard deviation
- **Drawdown Analysis**: Track maximum peak-to-trough decline

### 🔬 **Professional Backtesting**
- **Walk-Forward Analysis**: Out-of-sample validation to prevent overfitting
- **Strategy Lab**: Test MA crossovers, custom indicators, any logic
- **Transaction Costs**: Realistic modeling with slippage and fees

### 📈 **Technical Analysis Suite**
- **Smart Signals**: Automated Buy/Sell/Neutral recommendations
- **20+ Indicators**: RSI, MACD, Bollinger Bands, SMAs, and more
- **Portfolio Optimization**: Mean-variance, risk parity algorithms

### 🎯 **Intelligent Watchlist**
- **Auto-sync**: Detects owned stocks not in watchlist and prompts addition
- **Live Prices**: Real-time updates for tracked symbols
- **News Feed**: Aggregated headlines for all watched assets

---

## 🎨 UI/UX Showcase

MonteWalk features a **professionally designed Gradio 6 interface** optimized for traders:

### Landing Page
- **Hero Section**: Clear value proposition with feature cards
- **Glassmorphism Design**: Modern dark theme with subtle transparency
- **Smooth Navigation**: Instant page transitions with scroll-to-top

### Dashboard
- **4-Panel Layout**: Portfolio, Watchlist, Crypto, News—all in one view
- **One-Click Refresh**: Update all data sources simultaneously
- **Responsive Design**: Works seamlessly on desktop and tablet

### Toolbox
- **Organized by Category**: 9 tool groups with collapsible accordions
- **Dynamic Forms**: Auto-generated from function signatures
- **Clear Results**: Formatted outputs with syntax highlighting

### Settings
- **API Configuration**: Secure credential management with password fields
- **Instant Feedback**: Clear success/error messages
- **Restart Prompt**: Guides users on applying changes

---

## 🔧 Technical Implementation

### Built with Gradio 6
- **Native MCP Support**: `demo.launch(mcp_server=True)` enables seamless integration
- **Custom Theming**: Professional dark palette using `gr.themes.Base`
- **Advanced CSS**: Glassmorphism effects, custom animations, responsive grid
- **Navigation State**: Visibility control for multi-page SPA experience

### MCP Architecture
- **25+ Tools**: Comprehensive trading toolkit spanning 9 categories
- **4 Resources**: Live portfolio, watchlist, news, crypto feeds
- **6 Prompts**: Guided workflows for complex multi-step analyses
- **Error Resilience**: Automatic fallbacks and graceful degradation

### Data Pipeline
- **Caching Strategy**: 5-minute TTL on market data requests
- **Multi-source Fallback**: yfinance → NewsAPI → GNews → CoinGecko
- **FinBERT Sentiment**: Serverless GPU inference via Modal endpoint
- **Local Storage**: JSON-based portfolio and watchlist persistence

### Visualization System
- **Matplotlib + Seaborn**: Professional charts with dark theme
- **6 Chart Types**: Candlestick, line, bar, histogram, scatter, heatmap
- **mplfinance Integration**: Specialized candlestick rendering with volume
- **Base64 Images**: Charts encoded for AI/web consumption
- **Tool-Integrated**: Optional `visualize` parameter in key functions

### Market Scanner
- **3 Scan Types**: Big movers, volume spikes, reversal candidates
- **Real-time Data**: Powered by Alpaca market data API
- **Smart Filtering**: Configurable thresholds and limits
- **Visualization Support**: Bar charts for scan results

### Security & Safety
- **Paper Trading Only**: Zero real money risk
- **Environment Variables**: API keys never committed to code
- **Position Limits**: Hard-coded risk checks on every trade
- **Audit Logging**: Complete action trail with timestamps

---

## 🌍 Real-World Impact

MonteWalk democratizes **institutional-grade quantitative finance** for retail traders and developers:

### For Individual Traders
- **Learn by Doing**: Practice strategies with $100K virtual capital
- **Risk Education**: Understand VaR, drawdown, volatility in real-time
- **Time Savings**: Automate research with AI-powered workflows
- **Better Decisions**: Combine fundamentals, technicals, and sentiment

### For Developers
- **MCP Template**: Reference implementation for financial tool servers
- **Gradio Best Practices**: Professional UI patterns with Gradio 6
- **API Integration**: Multi-source data aggregation examples
- **Testing Framework**: Safe paper trading environment for strategy validation

### For AI Assistants
- **Context Enhancement**: Give Claude/GPT financial superpowers
- **Agentic Workflows**: Enable complex multi-step trading strategies
- **Real-time Data**: Connect LLMs to live market information
- **Tool Orchestration**: Demonstrate MCP's composability potential

### Potential Extensions
- **Live Trading**: Production Alpaca integration (easy switch from paper)
- **Advanced Strategies**: Options, futures, arbitrage implementations
- **Social Trading**: Share and clone successful agent workflows
- **Educational Platform**: Interactive finance courses powered by AI

---

## 🎥 Demo Video

> **Coming Soon**: Full walkthrough of MonteWalk's features, MCP integration, and agentic workflows.

---

## 🚀 Quick Start

### Option 1: Try on Hugging Face Spaces (Recommended)

**Click the Gradio UI above** to:
1. Explore the dashboard and toolbox
2. View MCP client setup instructions
3. Test tools directly in your browser

### Option 2: Run Locally

#### Prerequisites
- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (optional, recommended)
- [Alpaca Paper Trading Account](https://alpaca.markets) (free)
- [NewsAPI Key](https://newsapi.org) (optional, 100 free requests/day)

#### Installation
```bash
git clone https://github.com/N-lia/MonteWalk.git
cd MonteWalk
# Option 1: Using uv (recommended) - handles venv creation and dependency install
uv sync
# Option 2: Using pip
# python3 -m venv .venv
# source .venv/bin/activate  # Windows: .venv\Scripts\activate
# pip install -r requirements.txt
```

#### Configuration
```bash
cp .env.example .env
# Edit .env with your API keys:
# ALPACA_API_KEY=your_key
# ALPACA_SECRET_KEY=your_secret
# NEWSAPI_KEY=your_key (optional)
```

#### Run
```bash
# Gradio UI + MCP Server
uv run app.py

# Or pure MCP Server (for Claude Desktop)
uv run server.py
```

### Option 3: Connect to Claude Desktop

**1. Add to `claude_desktop_config.json`:**

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
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

**2. Restart Claude Desktop**

**3. Start using MonteWalk:**
- "What's my portfolio risk?"
- "Analyze AAPL technicals and sentiment"
- "Backtest a 10/50 MA crossover on MSFT"
- "Run morning briefing"

---

## 📚 Documentation

- **[API Reference](API_REFERENCE.md)**: Complete tool documentation with examples
- **[.env.example](.env.example)**: Configuration template

---

## 🏗️ Architecture

```
MonteWalk/
├── app.py              # Gradio 6 UI + MCP server
├── server.py           # Pure MCP server (stdio)
├── theme.py            # Custom Gradio theme
├── config.py           # Environment config
├── tools/              # 25 trading tools
│   ├── market_data.py
│   ├── execution.py
│   ├── risk_engine.py
│   ├── backtesting.py
│   ├── feature_engineering.py
│   ├── portfolio_optimizer.py
│   ├── news_intelligence.py
│   ├── watchlist.py
│   ├── crypto_data.py
│   └── ...
├── resources/          # Educational materials
└── data/               # Local storage (gitignored)
```

### Tech Stack
- **Frontend**: Gradio 6.0, Custom CSS, Google Fonts
- **MCP**: FastMCP, stdio/HTTP protocols
- **Data**: yfinance, Alpaca SDK, CoinGecko, NewsAPI
- **Analysis**: NumPy, SciPy, Pandas, pandas_ta
- **Sentiment**: FinBERT (Modal serverless GPU)
- **Deployment**: Hugging Face Spaces, Python 3.12

---

## 🎓 Learn More

- **Model Context Protocol**: [modelcontextprotocol.io](https://modelcontextprotocol.io/)
- **Gradio 6 Docs**: [gradio.app/docs](https://www.gradio.app/docs)
- **Alpaca Paper Trading**: [alpaca.markets/docs/trading/paper-trading](https://alpaca.markets/docs/trading/paper-trading/)

---

## 🙏 Acknowledgments

Built for the **MCP 1st Birthday Hackathon** by [N-lia](https://github.com/N-lia).

Special thanks to:
- **Anthropic** for the Model Context Protocol specification
- **Gradio** for the amazing UI framework and MCP support
- **Alpaca** for free paper trading infrastructure
- **Modal** for serverless GPU inference

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🔗 Links

- **GitHub**: [github.com/N-lia/MonteWalk](https://github.com/N-lia/MonteWalk)
- **Hugging Face Space**: [huggingface.co/spaces/N-lia/MonteWalk](https://huggingface.co/spaces/N-lia/MonteWalk)
- **MCP 1st Birthday**: [huggingface.co/spaces/launch/mcp-1st-bday](https://huggingface.co/spaces/launch/mcp-1st-bday)

---

**Made with ❤️ for the trading community**
