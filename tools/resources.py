"""
Educational resources and cheat sheets for algorithmic trading.
"""

def get_algo_cheat_sheet() -> str:
    """
    Returns a cheat sheet of common algorithmic trading concepts and formulas.
    """
    return """
# 📈 Algorithmic Trading Cheat Sheet

## Key Metrics
- **Sharpe Ratio**: (Rp - Rf) / σp
  - *Measure of risk-adjusted return. >1 is good, >2 is excellent.*
- **Sortino Ratio**: (Rp - Rf) / σd
  - *Like Sharpe, but only penalizes downside volatility.*
- **Maximum Drawdown (MDD)**: (Trough Value - Peak Value) / Peak Value
  - *Worst possible loss from a peak to a trough.*
- **CAGR**: (Ending Value / Beginning Value)^(1/n) - 1
  - *Compound Annual Growth Rate.*

## Common Strategies
1. **Mean Reversion**: Betting that prices will revert to the mean (e.g., Bollinger Bands, RSI).
2. **Momentum/Trend Following**: Betting that trends will continue (e.g., Moving Average Crossover, MACD).
3. **Statistical Arbitrage**: Exploiting pricing inefficiencies between correlated assets (e.g., Pairs Trading).
4. **Sentiment Analysis**: Using news/social media sentiment to predict moves (e.g., FinBERT).

## Risk Management Rules
- **Position Sizing**: Never risk more than 1-2% of capital on a single trade.
- **Stop Loss**: Always have an exit plan for losing trades.
- **Diversification**: Don't put all eggs in one basket (check correlations).
- **Kelly Criterion**: f* = (bp - q) / b
  - *Optimal bet size (use fractional Kelly for safety).*
"""

def get_classic_papers() -> str:
    """
    Returns a list of must-read academic papers in quantitative finance.
    """
    return """
# 📚 Classic Quantitative Finance Papers

## Foundations
1. **"Portfolio Selection"** by Harry Markowitz (1952)
   - *Introduced Modern Portfolio Theory (MPT) and the efficient frontier.*
2. **"Capital Asset Prices: A Theory of Market Equilibrium"** by William Sharpe (1964)
   - *Introduced the CAPM model and Beta.*
3. **"The Pricing of Options and Corporate Liabilities"** by Black & Scholes (1973)
   - *The foundation of options pricing.*

## Statistical Arbitrage & Alpha
4. **"Statistical Arbitrage in the U.S. Equities Market"** by Avellaneda & Lee (2008)
   - *A rigorous framework for pairs trading and mean reversion.*
5. **"101 Formulaic Alphas"** by Kakushadze (2016)
   - *A treasure trove of alpha factors for quantitative trading.*

## Machine Learning in Finance
6. **"Deep Learning for Limit Order Books"** by Zhang et al. (2019)
   - *Applying CNNs/LSTMs to high-frequency data.*
7. **"Financial Sentiment Analysis with Pre-trained Language Models"** (FinBERT)
   - *Using BERT for financial text classification.*
"""

def get_risk_checklist() -> str:
    """
    Returns a pre-flight checklist for risk management before deploying strategies.
    """
    return """
# ✅ Pre-Flight Risk Checklist

## 1. Strategy Validation
- [ ] **Backtest Period**: Does it cover different market regimes (bull, bear, sideways)?
- [ ] **Overfitting**: Did you optimize parameters too much? (Look for parameter stability).
- [ ] **Out-of-Sample**: Did it perform well on data it hasn't seen before?
- [ ] **Transaction Costs**: Did you include slippage and commissions?

## 2. Portfolio Health
- [ ] **Exposure**: Is leverage within safe limits (< 2x)?
- [ ] **Concentration**: Is any single position > 10% of equity?
- [ ] **Correlation**: Are all assets highly correlated? (e.g., all Tech stocks).
- [ ] **Liquidity**: Can you exit positions easily without moving the price?

## 3. System & Infrastructure
- [ ] **Data Quality**: Is your data clean and adjusted for splits/dividends?
- [ ] **Execution**: Is the order execution logic robust (retries, error handling)?
- [ ] **Fail-safes**: Is there a "Kill Switch" to stop trading if losses exceed X%?
- [ ] **Logging**: Is every action logged for audit?
"""
