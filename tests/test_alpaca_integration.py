#!/usr/bin/env python3
"""
Alpaca Integration Test Suite
Tests all major Alpaca broker functionality.
"""

import sys
import os
sys.path.append(os.getcwd())

from tools.alpaca_broker import get_broker
from tools.execution import get_positions, place_order, cancel_order, flatten, get_order_history
import time


def test_connection():
    """Test 1: Broker connection"""
    print("\n=== TEST 1: Broker Connection ===")
    try:
        broker = get_broker()
        account = broker.get_account()
        print(f"✅ Connected! Cash: ${account['cash']:,.2f}")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


def test_get_positions():
    """Test 2: Get positions"""
    print("\n=== TEST 2: Get Positions ===")
    try:
        portfolio = get_positions()
        print(f"✅ Portfolio retrieved")
        print(f"   Cash: ${portfolio['cash']:,.2f}")
        print(f"   Positions: {len(portfolio['positions'])}")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


def test_market_order():
    """Test 3: Place market order"""
    print("\n=== TEST 3: Place Market Order ===")
    try:
        # Place a small order
        result = place_order("AAPL", "buy", 1, "market")
        print(f"✅ Order placed: {result}")
        
        # Wait for order to fill
        time.sleep(2)
        
        # Verify position exists
        portfolio = get_positions()
        if "AAPL" in portfolio['positions']:
            print(f"✅ Position confirmed: AAPL {portfolio['positions']['AAPL']} shares")
            return True
        else:
            print("⚠️  Order placed but position not yet filled")
            return False
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


def test_order_history():
    """Test 4: Get order history"""
    print("\n=== TEST 4: Order History ===")
    try:
        history = get_order_history("all")
        print(f"✅ Order history retrieved")
        print(history[:200] + "..." if len(history) > 200 else history)
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


def test_flatten():
    """Test 5: Flatten all positions"""
    print("\n=== TEST 5: Flatten Positions ===")
    try:
        result = flatten()
        print(f"✅ Flatten executed: {result}")
        
        # Wait for orders to fill
        time.sleep(2)
        
        # Verify no positions
        portfolio = get_positions()
        if len(portfolio['positions']) == 0:
            print("✅ All positions closed")
            return True
        else:
            print(f"⚠️  Still have {len(portfolio['positions'])} positions")
            return False
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("ALPACA INTEGRATION TEST SUITE")
    print("=" * 60)
    
    tests = [
        test_connection,
        test_get_positions,
        test_market_order,
        test_order_history,
        test_flatten
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"❌ Test raised exception: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✨ ALL TESTS PASSED! ✨")
        print("\nYour Alpaca integration is fully functional!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        print("Check the errors above for details")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
