import pandas as pd
import pandas_ta as ta
import yfinance as yf
import numpy as np
from typing import Dict, Any, List, Tuple

def _fetch_data(symbol: str, start: str, end: str):
    return yf.download(symbol, start=start, end=end, progress=False)

def run_backtest(symbol: str, fast_ma: int, slow_ma: int, start_date: str = "2020-01-01", end_date: str = "2023-12-31") -> str:
    """
    Backtests a Moving Average Crossover strategy.
    """
    df = _fetch_data(symbol, start_date, end_date)
    if df.empty:
        return "No data found."
    
    # Calculate Indicators
    # Handle MultiIndex columns if present (yfinance update)
    close = df['Close']
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
        
    df['Fast'] = close.rolling(window=fast_ma).mean()
    df['Slow'] = close.rolling(window=slow_ma).mean()
    
    # Signal
    df['Signal'] = 0
    df.loc[df['Fast'] > df['Slow'], 'Signal'] = 1
    df['Position'] = df['Signal'].shift(1)
    
    # Returns
    df['Returns'] = close.pct_change()
    
    # Transaction Costs (e.g., 10bps per trade)
    COST_BPS = 0.001
    trades = df['Signal'].diff().abs()
    costs = trades * COST_BPS
    
    df['Strategy'] = (df['Returns'] * df['Position']) - costs
    
    cumulative = (1 + df['Strategy']).cumprod()
    total_return = cumulative.iloc[-1] - 1
    
    std_dev = df['Strategy'].std()
    if std_dev == 0:
        sharpe = 0.0
    else:
        sharpe = df['Strategy'].mean() / std_dev * np.sqrt(252)
    
    return (f"Backtest Results ({symbol} {fast_ma}/{slow_ma}) [w/ Costs]:\n"
            f"Total Return: {total_return:.2%}\n"
            f"Sharpe Ratio: {sharpe:.2f}")

def walk_forward_analysis(symbol: str, start_date: str = "2020-01-01", end_date: str = "2023-12-31", train_months: int = 12, test_months: int = 3) -> str:
    """
    Performs Walk Forward Analysis on MA Crossover.
    Optimizes (Fast, Slow) on Train, tests on Test.
    """
    df = _fetch_data(symbol, start_date, end_date)
    if df.empty:
        return "No data found."
    
    close = df['Close']
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
        
    # Generate windows
    # Simplified: Iterate by index assuming daily data
    # 21 days/month
    train_len = train_months * 21
    test_len = test_months * 21
    step = test_len
    
    results = []
    
    # Parameter Grid
    fast_params = [10, 20, 50]
    slow_params = [50, 100, 200]
    
    current_idx = 0
    while current_idx + train_len + test_len < len(df):
        train_data = close.iloc[current_idx : current_idx + train_len]
        test_data = close.iloc[current_idx + train_len : current_idx + train_len + test_len]
        
        # Optimize on Train
        best_perf = -np.inf
        best_params = (0, 0)
        
        for f in fast_params:
            for s in slow_params:
                if f >= s: continue
                # Vectorized backtest on train
                fast_ma = train_data.rolling(window=f).mean()
                slow_ma = train_data.rolling(window=s).mean()
                signal = (fast_ma > slow_ma).astype(int).shift(1)
                ret = train_data.pct_change() * signal
                perf = ret.sum() # Simple sum of returns
                
                if perf > best_perf:
                    best_perf = perf
                    best_params = (f, s)
        
        # Test on Test Data
        f, s = best_params
        fast_ma_test = test_data.rolling(window=f).mean()
        slow_ma_test = test_data.rolling(window=s).mean()
        signal_test = (fast_ma_test > slow_ma_test).astype(int).shift(1)
        ret_test = test_data.pct_change() * signal_test
        test_perf = ret_test.sum()
        
        results.append({
            "Period": f"{test_data.index[0].date()} to {test_data.index[-1].date()}",
            "Best Params": best_params,
            "Test Return": test_perf
        })
        
        current_idx += step
        
    # Format Output
    output = ["Walk Forward Analysis Results:"]
    total_ret = 0
    for r in results:
        output.append(f"[{r['Period']}] Params: {r['Best Params']}, Return: {r['Test Return']:.2%}")
        total_ret += r['Test Return']
        
    output.append(f"Total Walk Forward Return: {total_ret:.2%}")
    return "\n".join(output)
