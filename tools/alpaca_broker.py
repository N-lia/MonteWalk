"""
Alpaca Paper Trading Broker Integration
Provides a clean interface to Alpaca's paper trading API for MonteWalk.
"""

from typing import Dict, Any, List, Optional, Literal
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import (
    MarketOrderRequest, 
    LimitOrderRequest,
    GetOrdersRequest
)
from alpaca.trading.enums import OrderSide, TimeInForce, QueryOrderStatus, OrderClass
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from config import ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_PAPER_TRADING
import logging
import os

logger = logging.getLogger(__name__)


class AlpacaBroker:
    """
    Wrapper for Alpaca paper trading API.
    Handles all broker interactions for MonteWalk.
    """
    
    def __init__(self):
        """Initialize Alpaca trading and data clients."""
        if not ALPACA_API_KEY or not ALPACA_SECRET_KEY:
            logger.error("Alpaca API credentials missing in environment variables.")
            raise ValueError("Alpaca API credentials not found in environment variables.")
        
        try:
            self.trading_client = TradingClient(
                ALPACA_API_KEY, 
                ALPACA_SECRET_KEY, 
                paper=ALPACA_PAPER_TRADING
            )
            account = self.trading_client.get_account()
            logger.info(f"Alpaca Broker initialized. Account Status: {account.status}, Buying Power: ${account.buying_power}")
        except Exception as e:
            logger.critical(f"Failed to connect to Alpaca API: {e}")
            raise ConnectionError(f"Failed to connect to Alpaca: {e}")

        self.data_client = StockHistoricalDataClient(
            ALPACA_API_KEY, 
            ALPACA_SECRET_KEY
        )
        logger.info("Alpaca broker initialized (Paper Trading Mode)")
    
    def get_account(self) -> Dict[str, Any]:
        """
        Retrieve account information.
        
        Returns:
            Dict with keys: cash, equity, buying_power, portfolio_value
        """
        try:
            account = self.trading_client.get_account()
            return {
                "cash": float(account.cash),
                "equity": float(account.equity),
                "buying_power": float(account.buying_power),
                "portfolio_value": float(account.portfolio_value),
                "pattern_day_trader": account.pattern_day_trader,
                "daytrade_count": account.daytrade_count
            }
        except Exception as e:
            logger.error(f"Failed to get account: {e}")
            raise
    
    def get_all_positions(self) -> Dict[str, Any]:
        """
        Retrieve all open positions.
        
        Returns:
            Dict mapping symbol -> position details
        """
        try:
            positions = self.trading_client.get_all_positions()
            result = {}
            for pos in positions:
                result[pos.symbol] = {
                    "qty": float(pos.qty),
                    "avg_entry_price": float(pos.avg_entry_price),
                    "current_price": float(pos.current_price),
                    "market_value": float(pos.market_value),
                    "unrealized_pl": float(pos.unrealized_pl),
                    "unrealized_plpc": float(pos.unrealized_plpc),
                    "side": pos.side
                }
            return result
        except Exception as e:
            logger.error(f"Failed to get positions: {e}")
            raise
    
    def get_position(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific position by symbol.
        
        Args:
            symbol: Ticker symbol
            
        Returns:
            Position details or None if no position exists
        """
        try:
            pos = self.trading_client.get_open_position(symbol)
            return {
                "qty": float(pos.qty),
                "avg_entry_price": float(pos.avg_entry_price),
                "current_price": float(pos.current_price),
                "market_value": float(pos.market_value),
                "unrealized_pl": float(pos.unrealized_pl),
                "unrealized_plpc": float(pos.unrealized_plpc),
                "side": pos.side
            }
        except Exception as e:
            logger.debug(f"No position for {symbol}: {e}")
            return None
    
    def submit_market_order(
        self, 
        symbol: str, 
        side: Literal["buy", "sell"], 
        qty: float
    ) -> Dict[str, Any]:
        """
        Submit a market order.
        
        Args:
            symbol: Ticker symbol
            side: "buy" or "sell"
            qty: Quantity
            
        Returns:
            Order confirmation dict
        """
        try:
            order_side = OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL
            
            request = MarketOrderRequest(
                symbol=symbol.upper(),
                qty=qty,
                side=order_side,
                time_in_force=TimeInForce.DAY
            )
            
            order = self.trading_client.submit_order(request)
            
            logger.info(f"Market order submitted: {side.upper()} {qty} {symbol}")
            
            return {
                "order_id": str(order.id),
                "symbol": order.symbol,
                "qty": float(order.qty),
                "side": order.side.value,
                "type": order.type.value,
                "status": order.status.value,
                "submitted_at": str(order.submitted_at)
            }
        except Exception as e:
            logger.error(f"Market order failed: {e}")
            raise
    
    def submit_limit_order(
        self, 
        symbol: str, 
        side: Literal["buy", "sell"], 
        qty: float,
        limit_price: float
    ) -> Dict[str, Any]:
        """
        Submit a limit order.
        
        Args:
            symbol: Ticker symbol
            side: "buy" or "sell"
            qty: Quantity
            limit_price: Limit price
            
        Returns:
            Order confirmation dict
        """
        try:
            order_side = OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL
            
            request = LimitOrderRequest(
                symbol=symbol.upper(),
                qty=qty,
                side=order_side,
                time_in_force=TimeInForce.DAY,
                limit_price=limit_price
            )
            
            order = self.trading_client.submit_order(request)
            
            logger.info(f"Limit order submitted: {side.upper()} {qty} {symbol} @ {limit_price}")
            
            return {
                "order_id": str(order.id),
                "symbol": order.symbol,
                "qty": float(order.qty),
                "side": order.side.value,
                "type": order.type.value,
                "limit_price": float(order.limit_price) if order.limit_price else None,
                "status": order.status.value,
                "submitted_at": str(order.submitted_at)
            }
        except Exception as e:
            logger.error(f"Limit order failed: {e}")
            raise
    
    def get_orders(self, status: str = "all") -> List[Dict[str, Any]]:
        """
        Retrieve order history.
        
        Args:
            status: "all", "open", "closed"
            
        Returns:
            List of order dicts
        """
        try:
            status_map = {
                "all": QueryOrderStatus.ALL,
                "open": QueryOrderStatus.OPEN,
                "closed": QueryOrderStatus.CLOSED
            }
            
            request = GetOrdersRequest(
                status=status_map.get(status.lower(), QueryOrderStatus.ALL)
            )
            
            orders = self.trading_client.get_orders(request)
            
            result = []
            for order in orders:
                result.append({
                    "order_id": str(order.id),
                    "symbol": order.symbol,
                    "qty": float(order.qty),
                    "side": order.side.value,
                    "type": order.type.value,
                    "status": order.status.value,
                    "filled_qty": float(order.filled_qty) if order.filled_qty else 0,
                    "filled_avg_price": float(order.filled_avg_price) if order.filled_avg_price else None,
                    "submitted_at": str(order.submitted_at)
                })
            
            return result
        except Exception as e:
            logger.error(f"Failed to get orders: {e}")
            raise
    
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel a pending order.
        
        Args:
            order_id: Order ID to cancel
            
        Returns:
            True if successful
        """
        try:
            self.trading_client.cancel_order_by_id(order_id)
            logger.info(f"Order {order_id} cancelled")
            return True
        except Exception as e:
            logger.error(f"Failed to cancel order {order_id}: {e}")
            raise
    
    def close_all_positions(self) -> Dict[str, Any]:
        """
        Close all open positions (emergency flatten).
        
        Returns:
            Dict with closed position count and details
        """
        try:
            closed = self.trading_client.close_all_positions(cancel_orders=True)
            logger.info(f"Closed {len(closed)} positions")
            
            return {
                "closed_count": len(closed),
                "positions_closed": [
                    {
                        "symbol": pos.symbol,
                        "qty": float(pos.qty) if pos.qty else 0,
                        "status": pos.status.value
                    }
                    for pos in closed
                ]
            }
        except Exception as e:
            logger.error(f"Failed to close all positions: {e}")
            raise
    
    def close_position(self, symbol: str) -> Dict[str, Any]:
        """
        Close a specific position.
        
        Args:
            symbol: Ticker symbol
            
        Returns:
            Order details
        """
        try:
            order = self.trading_client.close_position(symbol)
            logger.info(f"Closed position: {symbol}")
            
            return {
                "order_id": str(order.id),
                "symbol": order.symbol,
                "qty": float(order.qty),
                "side": order.side.value,
                "status": order.status.value
            }
        except Exception as e:
            logger.error(f"Failed to close position {symbol}: {e}")
            raise


# Singleton instance
_broker = None

def get_broker() -> AlpacaBroker:
    """Get or create the Alpaca broker singleton."""
    global _broker
    if _broker is None:
        _broker = AlpacaBroker()
    return _broker
