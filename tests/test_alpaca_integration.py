#!/usr/bin/env python3
"""
Alpaca Integration Test Suite (Pytest)
Tests all major Alpaca broker functionality.
"""

import sys
import os
import pytest
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.append(os.getcwd())
from tools.execution import get_positions, place_order, get_order_history, flatten

@pytest.fixture(scope="module")
def broker():
    """Fixture to get the broker instance."""
    # Mock the config values before importing anything that uses them
    with patch('tools.alpaca_broker.ALPACA_API_KEY', 'mock_api_key'), \
         patch('tools.alpaca_broker.ALPACA_SECRET_KEY', 'mock_secret_key'), \
         patch('tools.alpaca_broker.ALPACA_PAPER_TRADING', True), \
         patch('tools.alpaca_broker.TradingClient') as MockTradingClient, \
         patch('tools.alpaca_broker.StockHistoricalDataClient'):
        
        # Mock the trading client instance
        mock_trading_client = MagicMock()
        MockTradingClient.return_value = mock_trading_client
        
        # Mock account for initialization
        mock_account = MagicMock()
        mock_account.cash = 100000.00
        mock_account.equity = 100000.00
        mock_account.buying_power = 100000.00
        mock_account.portfolio_value = 100000.00
        mock_account.status = 'ACTIVE'
        mock_account.pattern_day_trader = False
        mock_account.daytrade_count = 0
        mock_trading_client.get_account.return_value = mock_account
        
        # Create a real AlpacaBroker instance with mocked dependencies
        from tools.alpaca_broker import AlpacaBroker
        broker_instance = AlpacaBroker()
        
        # Mock the methods we'll use in tests
        mock_trading_client.get_all_positions.return_value = []
        
        yield broker_instance

def test_connection(broker):
    """Test 1: Broker connection"""
    account = broker.get_account()
    print(f"Connected! Cash: ${account['cash']:,.2f}")
    # Note: get_account returns a dict, not an object
    assert 'cash' in account and account['cash'] >= 0

def test_get_positions():
    """Test 2: Get positions"""
    portfolio = get_positions()
    print(f"Portfolio retrieved. Cash: ${portfolio['cash']:,.2f}, Positions: {len(portfolio['positions'])}")
    assert 'cash' in portfolio
    assert 'positions' in portfolio

@pytest.mark.dependency()
def test_market_order_and_history():
    """Test 3 & 4: Place market order and check history"""
    # This test requires actual broker integration, so we'll mock the components
    symbol = "SPY"
    qty = 1
    side = "buy"
    order_type = "market"
    
    # Mock the broker methods that place_order depends on
    with patch('tools.execution.broker') as mock_broker, \
         patch('yfinance.Ticker') as MockTicker:
        
        # Mock yfinance price
        mock_ticker = MockTicker.return_value
        mock_ticker.fast_info.last_price = 450.00
        
        # Mock broker submit_market_order
        mock_order_dict = {
            'order_id': 'test_order_123',
            'symbol': symbol,
            'qty': qty,
            'side': 'buy',
            'type': 'market',
            'status': 'accepted',
            'submitted_at': '2024-01-01T00:00:00Z'
        }
        mock_broker.submit_market_order.return_value = mock_order_dict
        mock_broker.get_account.return_value = {
            'cash': 100000.00,
            'equity': 100000.00,
            'buying_power': 100000.00
        }
        mock_broker.get_all_positions.return_value = {
            symbol: {'qty': qty}
        }
        mock_broker.get_orders.return_value = [mock_order_dict]
        
        print(f"Placing {side} order for {qty} {symbol}...")
        result = place_order(symbol, side, qty, order_type)
        assert result is not None, "Failed to place order"
        assert result.id == 'test_order_123', f"Expected order ID test_order_123, got {result.id}"
        print(f"Order placed: {result.id}")

        # Verify position exists
        portfolio = get_positions()
        assert symbol in portfolio['positions'], f"Position for {symbol} not found after order."
        print(f"Position confirmed: {symbol} {portfolio['positions'][symbol]} shares")

        # Verify order history
        history = get_order_history("all")
        assert history, "Order history is empty."
        
        # Check if our recent order is in the history
        order_ids = [order.id for order in history]
        assert result.id in order_ids, "Placed order not found in history."
        print("Order found in history.")

@pytest.mark.dependency(depends=["test_market_order_and_history"])
def test_flatten():
    """Test 5: Flatten all positions"""
    with patch('tools.execution.broker') as mock_broker:
        mock_broker.close_all_positions.return_value = {
            'closed_count': 1,
            'positions_closed': [
                {'symbol': 'SPY', 'qty': 1, 'status': 'filled'}
            ]
        }
        mock_broker.get_account.return_value = {
            'cash': 100000.00,
            'equity': 100000.00,
            'buying_power': 100000.00
        }
        mock_broker.get_all_positions.return_value = {}
        
        print("Flattening all positions...")
        result = flatten()
        assert result is not None, "Flatten command failed."
        print(f"Flatten executed: {len(result)} orders to close positions.")

        # Verify no positions are left
        portfolio = get_positions()
        assert len(portfolio['positions']) == 0, f"Failed to flatten all positions. {len(portfolio['positions'])} still remain."
        print("All positions have been successfully closed.")
