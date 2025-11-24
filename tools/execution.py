import yfinance as yf
from typing import Dict, Any, Optional, Literal
from config import INITIAL_CAPITAL
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


def get_positions() -> Dict[str, Any]:
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
) -> str:
    """
    Submits a market or limit order to Alpaca paper trading.
    
    Args:
        symbol: Ticker symbol.
        side: 'buy' or 'sell'.
        qty: Quantity to trade.
        order_type: 'market' or 'limit'.
        limit_price: Required if order_type is 'limit'.
        
    Returns:
        Confirmation message or error
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
        except:
            return f"Failed to get price for {symbol}"
        
        if current_price is None:
            return f"Failed to get price for {symbol}"
        
        # Pre-Trade Risk Check
        risk_error = validate_trade(symbol, side, qty, current_price)
        if risk_error:
            return risk_error
        
        # Submit order to Alpaca
        if order_type == "market":
            order_result = broker.submit_market_order(symbol, side, qty)
            return (
                f"✅ Market Order Submitted: {side.upper()} {qty} {symbol}\n"
                f"Order ID: {order_result['order_id']}\n"
                f"Status: {order_result['status']}\n"
                f"Submitted at: {order_result['submitted_at']}"
            )
        
        elif order_type == "limit":
            if not limit_price:
                return "ERROR: Limit price required for limit orders."
            
            # Validate limit price direction
            if side == "buy" and limit_price > current_price:
                logger.warning(f"Buy limit {limit_price} is above market {current_price}")
            if side == "sell" and limit_price < current_price:
                logger.warning(f"Sell limit {limit_price} is below market {current_price}")
            
            order_result = broker.submit_limit_order(symbol, side, qty, limit_price)
            return (
                f"✅ Limit Order Submitted: {side.upper()} {qty} {symbol} @ ${limit_price:.2f}\n"
                f"Order ID: {order_result['order_id']}\n"
                f"Status: {order_result['status']}\n"
                f"Submitted at: {order_result['submitted_at']}"
            )
        else:
            return f"ERROR: Unknown order type: {order_type}"
            
    except Exception as e:
        logger.error(f"Order failed: {e}")
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
        broker.cancel_order(order_id)
        return f"✅ Order {order_id} cancelled successfully"
    except Exception as e:
        logger.error(f"Cancel order failed: {e}")
        return f"ERROR: Failed to cancel order - {str(e)}"


def flatten() -> str:
    """
    Immediately closes all open positions.
    
    Returns:
        Summary of closed positions
    """
    if broker is None:
        return "ERROR: Alpaca broker not initialized."
    
    try:
        result = broker.close_all_positions()
        
        if result['closed_count'] == 0:
            return "No positions to flatten."
        
        msg = [f"✅ Flattened {result['closed_count']} positions:"]
        for pos in result['positions_closed']:
            msg.append(f"  - {pos['symbol']}: {pos['qty']} shares ({pos['status']})")
        
        return "\n".join(msg)
    except Exception as e:
        logger.error(f"Flatten failed: {e}")
        return f"ERROR: Failed to flatten positions - {str(e)}"


def get_order_history(status: str = "all") -> str:
    """
    Get order history from Alpaca.
    
    Args:
        status: "all", "open", or "closed"
        
    Returns:
        Formatted order history
    """
    if broker is None:
        return "ERROR: Alpaca broker not initialized."
    
    try:
        orders = broker.get_orders(status)
        
        if not orders:
            return f"No {status} orders found."
        
        msg = [f"=== {status.upper()} ORDERS ({len(orders)}) ==="]
        for order in orders[:10]:  # Limit to 10 most recent
            msg.append(
                f"{order['symbol']}: {order['side'].upper()} {order['qty']} "
                f"({order['type']}, {order['status']}) - {order['submitted_at']}"
            )
        
        if len(orders) > 10:
            msg.append(f"\n... and {len(orders) - 10} more orders")
        
        return "\n".join(msg)
    except Exception as e:
        logger.error(f"Get order history failed: {e}")
        return f"ERROR: Failed to get order history - {str(e)}"
