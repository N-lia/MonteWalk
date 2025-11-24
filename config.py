import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Data directory for storing local state (paper trading portfolio, logs)
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# Paper Trading Settings
INITIAL_CAPITAL = 100_000.0  # $100k paper money
PORTFOLIO_FILE = DATA_DIR / "portfolio.json"

# Logging
LOG_FILE = DATA_DIR / "activity.log"

# Risk Settings
DEFAULT_LOOKBACK_PERIOD = "1y"
RISK_FREE_RATE = 0.04  # 4% for Sharpe Ratio calcs

# Backtesting Defaults
DEFAULT_BACKTEST_START = "2020-01-01"
DEFAULT_BACKTEST_END = "2023-12-31"

# API Keys (set via environment variables)
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")

# Alpaca Paper Trading Configuration
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY", "")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY", "")
ALPACA_PAPER_TRADING = True  # Safety: Always use paper trading
ALPACA_BASE_URL = "https://paper-api.alpaca.markets"
