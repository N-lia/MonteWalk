import sys
import os
import pytest
import json
from unittest.mock import patch

# Add project root to path
sys.path.append(os.getcwd())

from tools.market_data import get_price
from tools.execution import place_order, get_positions
from tools.risk_engine import portfolio_risk
from tools.backtesting import run_backtest


@pytest.fixture
def mock_broker():
    """Mock broker to simulate API calls without hitting actual endpoints."""
    with patch('tools.alpaca_broker.get_broker') as mock:
        yield mock

def test_get_price_success():
    """Test successful retrieval of price data."""
    # This test remains an integration test as it fetches live data.
    try:
        price_json = get_price("AAPL", period="1d")
        assert price_json is not None, "Price data should not be None"
        price_data = json.loads(price_json)
        assert len(price_data) > 0, "Price data should not be empty"
        print(f"Successfully fetched price data for AAPL. Length: {len(price_data)}")
    except Exception as e:
        pytest.fail(f"get_price failed unexpectedly: {e}")

def test_get_price_failure():
    """Test graceful failure of price data retrieval."""
    # get_price catches exceptions and returns empty JSON, not raising them
    with patch('yfinance.Ticker.history', side_effect=Exception("Network Error")):
        result = get_price("FAIL", period="1d")
        # Should return empty JSON array on error
        data = json.loads(result)
        assert data == [], "Should return empty list on error"
    print("Correctly handled failure for get_price.")

def test_place_order(mock_broker):
    """Test placing an order."""
    # This test is mocked to avoid actual trades.
    place_order("AAPL", "buy", 10)
    # Further assertions could be added if place_order returned a mockable object
    print("Simulated placing an order for AAPL.")

def test_get_positions(mock_broker):
    """Test retrieving positions."""
    # This test is mocked.
    get_positions()
    print("Simulated retrieving positions.")

def test_portfolio_risk(mock_broker):
    """Test risk engine calculation."""
    # This test is mocked.
    portfolio_risk()
    print("Simulated portfolio risk calculation.")

def test_run_backtest():
    """Test backtesting functionality."""
    # This is an integration test using actual data.
    try:
        result = run_backtest("AAPL", 10, 20, "2023-01-01", "2023-02-01")
        assert result is not None, "Backtest should return a result"
        print("Successfully ran backtest for AAPL.")
    except Exception as e:
        pytest.fail(f"run_backtest failed unexpectedly: {e}")