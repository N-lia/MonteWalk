import sys
import os
sys.path.append(os.getcwd())

from tools.market_data import get_price
from tools.execution import place_order, get_positions
from tools.risk_engine import portfolio_risk
from tools.backtesting import run_backtest

def test_tools():
    print("Testing Market Data...")
    # AAPL price (should work if internet is up, otherwise might fail gracefully)
    try:
        price = get_price("AAPL", period="1d")
        print(f"Price Data Length: {len(price)}")
    except Exception as e:
        print(f"Market Data failed (expected if no internet): {e}")

    print("Testing Execution...")
    print(place_order("AAPL", "buy", 10))
    print(get_positions())

    print("Testing Risk Engine...")
    print(portfolio_risk())

    print("Testing Backtest...")
    # Short backtest
    print(run_backtest("AAPL", 10, 20, "2023-01-01", "2023-02-01"))

if __name__ == "__main__":
    test_tools()
