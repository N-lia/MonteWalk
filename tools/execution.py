import yfinance as yf
from typing import Any, Optional, Literal
from tools.alpaca_broker import get_broker
import logging

logger = logging.getLogger(__name__)

# Get the Alpaca broker instance
try:
    broker = get_broker()
    logger.info("Execution module using Alpaca broker")
except Exception as e:
    logger.error(f"Failed to initialize Alpaca broker: {e}")
    broker = None


class OrderResult:
    """Simple order result wrapper for API compatibility."""
    def __init__(self, order_dict: dict[str, Any]):
        self.id = order_dict.get('order_id')
        self.order_id = order_dict.get('order_id')
        self.symbol = order_dict.get('symbol')
        self.qty = order_dict.get('qty')
        self.side = order_dict.get('side')
        self.status = order_dict.get('status')
        self.submitted_at = order_dict.get('submitted_at')
        self._dict = order_dict
    
    def __str__(self):
        return (
            f"Order {self.id}: {self.side.upper()} {self.qty} {self.symbol} "
            f"(Status: {self.status})"
        )


class Order:
    """Simple order wrapper for API compatibility."""
    def __init__(self, order_dict: dict[str, Any]):
        self.id = order_dict.get('order_id')
        self.order_id = order_dict.get('order_id')
        self.symbol = order_dict.get('symbol')
        self.qty = order_dict.get('qty')
        self.side = order_dict.get('side')
        self.type = order_dict.get('type')
        self.status = order_dict.get('status')
        self.filled_qty = order_dict.get('filled_qty', 0)
        self.filled_avg_price = order_dict.get('filled_avg_price')
        self.submitted_at = order_dict.get('submitted_at')
        self._dict = order_dict


def get_positions() -> dict[str, Any]:
    """
    Retrieves the current state of all held positions and cash balance.
    
    Returns:
        Dict with 'cash' and 'positions' keys
    """
    if broker is None:
        return {
            "error": "Alpaca broker not initialized. Check your API credentials.",
            "cash": 0,
            "positions": {}
        }
    
    try:
        account = broker.get_account()
        positions_raw = broker.get_all_positions()
        
        # Convert to simple format: {symbol: qty}
        positions = {
            symbol: details['qty'] 
            for symbol, details in positions_raw.items()
        }
        
        return {
            "cash": account['cash'],
            "equity": account['equity'],
            "buying_power": account['buying_power'],
            "positions": positions
        }
    except Exception as e:
        logger.error(f"Failed to get positions: {e}")
        return {
            "error": str(e),
            "cash": 0,
            "positions": {}
        }


def place_order(
    symbol: str, 
    side: Literal["buy", "sell"], 
    qty: float, 
    order_type: Literal["market", "limit"] = "market", 
    limit_price: Optional[float] = None
) -> OrderResult:
    """
    Submits a market or limit order to Alpaca paper trading.
    
    Args:
        symbol: Ticker symbol.
        side: 'buy' or 'sell'.
        qty: Quantity to trade.
        order_type: 'market' or 'limit'.
        limit_price: Required if order_type is 'limit'.
        
    Returns:
        OrderResult object with order details
    """
    if broker is None:
        return "ERROR: Alpaca broker not initialized. Check your API credentials in .env file."
    
    # Import here to avoid circular dependency
    from tools.risk_engine import validate_trade
    
    try:
        # Get current price for risk validation
        ticker = yf.Ticker(symbol)
        try:
            current_price = ticker.fast_info.last_price
        except Exception:
            return f"Failed to get price for {symbol}"
        
        if current_price is None:
            return f"Failed to get price for {symbol}"
        
        # Pre-Trade Risk Check
        risk_error = validate_trade(symbol, side, qty, current_price)
        if risk_error:
            logger.warning(f"Trade rejected by risk engine: {risk_error}")
            return risk_error
        
        # Submit order to Alpaca
        if order_type == "market":
            logger.info(f"Submitting MARKET order: {side.upper()} {qty} {symbol}")
            order_result = broker.submit_market_order(symbol, side, qty)
            logger.info(f"Order submitted successfully: ID={order_result['order_id']}")
            return OrderResult(order_result)
        
        elif order_type == "limit":
            if not limit_price:
                return "ERROR: Limit price required for limit orders."
            
            # Validate limit price direction
            if side == "buy" and limit_price > current_price:
                logger.warning(f"Buy limit {limit_price} is above market {current_price}")
            if side == "sell" and limit_price < current_price:
                logger.warning(f"Sell limit {limit_price} is below market {current_price}")
            
            logger.info(f"Submitting LIMIT order: {side.upper()} {qty} {symbol} @ ${limit_price}")
            order_result = broker.submit_limit_order(symbol, side, qty, limit_price)
            logger.info(f"Order submitted successfully: ID={order_result['order_id']}")
            return OrderResult(order_result)
        else:
            logger.error(f"Unknown order type requested: {order_type}")
            return f"ERROR: Unknown order type: {order_type}"
            
    except Exception as e:
        logger.error(f"Order failed: {e}", exc_info=True)
        return f"ERROR: Order failed - {str(e)}"


def cancel_order(order_id: str) -> str:
    """
    Cancels a specific open order.
    
    Args:
        order_id: The Alpaca order ID to cancel
        
    Returns:
        Confirmation message
    """
    if broker is None:
        return "ERROR: Alpaca broker not initialized."
    
    try:
        logger.info(f"Cancelling order: {order_id}")
        broker.cancel_order(order_id)
        logger.info(f"Order {order_id} cancelled successfully")
        return f"✅ Order {order_id} cancelled successfully"
    except Exception as e:
        logger.error(f"Cancel order failed: {e}", exc_info=True)
        return f"ERROR: Failed to cancel order - {str(e)}"


def flatten() -> list[dict[str, Any]]:
    """
    Immediately closes all open positions.
    
    Returns:
        list of closed position orders
    """
    if broker is None:
        logger.error("Alpaca broker not initialized.")
        return []
    
    try:
        result = broker.close_all_positions()
        return result.get('positions_closed', [])
    except Exception as e:
        logger.error(f"Flatten failed: {e}")
        return []


def get_order_history(status: str = "all") -> list[Order]:
    """
    Get order history from Alpaca.
    
    Args:
        status: "all", "open", or "closed"
        
    Returns:
        list of Order objects
    """
    if broker is None:
        logger.error("Alpaca broker not initialized.")
        return []
    
    try:
        orders = broker.get_orders(status)
        return [Order(order) for order in orders]
    except Exception as e:
        logger.error(f"Get order history failed: {e}")
        return []
