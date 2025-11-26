# MonteWalk 🚀

**Institutional-grade quantitative finance tools for AI agents.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)

MonteWalk is an **MCP server** that gives AI assistants (like Claude) access to professional trading tools: real-time market data, paper trading, risk analysis, and portfolio optimization.

---

## ✨ Key Features

*   **📊 Market Intelligence**: Aggregates data from Yahoo Finance, Alpaca, and CoinGecko.
*   **💰 Paper Trading**: Real execution via Alpaca ($100k virtual account).
*   **⚠️ Risk Management**: Monte Carlo simulations, VaR, and volatility metrics.
*   **📈 Backtesting**: Test strategies with walk-forward analysis.
*   **🗞️ News & Sentiment**: Multi-source news aggregation with NLP sentiment scoring.
*   **🤖 Intelligent Watchlist**: Auto-syncs with your portfolio via AI prompts.

---

## 🚀 Quick Start

### 1. Prerequisites
*   Python 3.12+
*   [Alpaca Account](https://alpaca.markets) (Free Paper Trading)
*   [NewsAPI Key](https://newsapi.org) (Optional)

### 2. Installation
```bash
git clone https://github.com/N-lia/MonteWalk.git
cd MonteWalk
python3 -m venv .venv
source .venv/bin/activate
pip install mcp yfinance pandas numpy scipy pandas_ta textblob gnews newsapi-python pycoingecko alpaca-py
python -m textblob.download_corpora
```

### 3. Configuration
Create a `.env` file:
```bash
cp .env.example .env
```
Edit `.env` with your keys:
```ini
ALPACA_API_KEY=your_key
ALPACA_SECRET_KEY=your_secret
NEWSAPI_KEY=your_key  # Optional
```

### 4. Run Server

**For Hugging Face Deployment** (Gradio UI + MCP):
```bash
uv run app.py
```

**For Local Claude Desktop** (stdio-based MCP):
```bash
uv run server.py
```

---

## 🔌 Connect to Claude Desktop

**Local Connection (Recommended)**:

Add to your `claude_desktop_config.json`:

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

> **Note**: Replace `/absolute/path/to/MonteWalk` with your actual path.

**Alternative (Streamable HTTP via Gradio)**: If using `app.py`, configure with URL:
```json
{
  "mcpServers": {
    "montewalk": {
      "url": "http://localhost:7860/gradio_api/mcp/"
    }
  }
}
```
> ⚠️ **Note**: You must start `app.py` BEFORE launching Claude Desktop for this to work.

---

## 📚 Usage

**Just ask Claude:**

*   "What's my portfolio risk?"
*   "Analyze TSLA technicals and sentiment."
*   "Backtest a 10/50 MA crossover on Apple."
*   "Buy 10 shares of MSFT."
*   "Run morning briefing." (Auto-syncs watchlist!)

See [API_REFERENCE.md](API_REFERENCE.md) for full tool documentation.

---

## 🛠️ Architecture

*   **Core**: FastMCP server
*   **Data**: yfinance, Alpaca, CoinGecko, NewsAPI
*   **Analysis**: NumPy, SciPy, Pandas, TextBlob
*   **Security**: Paper trading only, local data storage

---

## 📄 License

MIT License. Built for the **MCP 1st Birthday Hackathon**.
