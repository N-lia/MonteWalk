"""
MonteWalk - Institutional-Grade Quantitative Finance Tools for AI Agents

This module implements a dual-mode Gradio 6 application that serves as both:
1. A standalone web UI for testing trading tools
2. An MCP (Model Context Protocol) server for AI assistant integration

ARCHITECTURE:
- 25 trading tools across 9 categories (market data, execution, risk, etc.)
- 4 live resources (portfolio, watchlist, news, crypto)
- 6 pre-built agentic workflow prompts
- Multi-source data aggregation (Yahoo Finance, Alpaca, CoinGecko, NewsAPI)
- FinBERT sentiment analysis via Modal serverless GPU

UI NAVIGATION:
- Landing Page: Hero section with feature showcase
- UI Dashboard: Portfolio/watchlist/crypto/news panels + toolbox + settings
- MCP Client Setup: Configuration instructions for Claude Desktop, VSCode, etc.

MCP INTEGRATION:
Launch with `demo.launch(mcp_server=True)` to enable MCP protocol.
AI assistants can then access all tools via stdio or HTTP connection.

USAGE:
    # Gradio UI + MCP Server
    uv run app.py
    
    # Pure MCP Server (for Claude Desktop)
    uv run server.py

Built for the MCP 1st Birthday Hackathon.
Repository: https://github.com/N-lia/MonteWalk
"""

import gradio as gr
import logging
import sys
from typing import Callable
import inspect

from dotenv import load_dotenv
load_dotenv()

# Local imports (tool implementations)
from config import LOG_FILE
from theme import ProfessionalTheme
from tools.market_data import get_price, get_fundamentals, get_orderbook
from tools.execution import (
    place_order,
    cancel_order,
    get_positions,
    flatten,
    get_order_history,
)
from tools.risk_engine import (
    portfolio_risk,
    var,
    max_drawdown,
    monte_carlo_simulation,
)
from tools.backtesting import run_backtest, walk_forward_analysis
from tools.feature_engineering import (
    compute_indicators,
    rolling_stats,
    get_technical_summary,
)
from tools.portfolio_optimizer import mean_variance_optimize, risk_parity
from tools.logger import setup_logging, log_action
from tools.news_intelligence import (
    get_news,
    analyze_sentiment,
    get_symbol_sentiment,
    get_latest_news_for_watchlist,
)
from tools.watchlist import (
    add_to_watchlist,
    remove_from_watchlist,
    get_watchlist_data,
    _load_watchlist,
)
from tools.crypto_data import (
    get_crypto_price,
    get_crypto_market_data,
    get_trending_crypto,
    search_crypto,
)
from tools.unusual_scanner import scan_unusual_activity
from tools.alpaca_broker import get_broker
from tools.resources import (
    get_algo_cheat_sheet,
    get_classic_papers,
    get_risk_checklist,
)

setup_logging()
logger = logging.getLogger(__name__)

# ----------------------------------------------------------------------
# Helper tools used on the landing page
# ----------------------------------------------------------------------
def health_check() -> str:
    return "MonteWalk Server is running and healthy."

def get_account_info() -> str:
    try:
        broker = get_broker()
        account = broker.get_account()
        return f"""
=== ALPACA ACCOUNT INFO ===
Cash: ${account['cash']:,.2f}
Equity: ${account['equity']:,.2f}
Buying Power: ${account['buying_power']:,.2f}
Portfolio Value: ${account['portfolio_value']:,.2f}
Pattern Day Trader: {account['pattern_day_trader']}
Day Trade Count: {account['daytrade_count']}
"""
    except Exception as e:
        return f"ERROR: Failed to get account info - {str(e)}"

def get_portfolio_summary() -> str:
    try:
        broker = get_broker()
        account = broker.get_account()
        positions = broker.get_all_positions()
        summary = [
            "=== PORTFOLIO SUMMARY (Alpaca Paper Trading) ===",
            f"Cash: ${account['cash']:,.2f}",
            f"Equity: ${account['equity']:,.2f}",
            f"Buying Power: ${account['buying_power']:,.2f}",
            f"Positions: {len(positions)}",
            "--- Holdings ---",
        ]
        for symbol, details in positions.items():
            qty = details["qty"]
            price = details["current_price"]
            pl = details["unrealized_pl"]
            pl_pct = details["unrealized_plpc"] * 100
            summary.append(
                f"{symbol}: {qty} shares @ ${price:.2f} (P/L: ${pl:,.2f} / {pl_pct:+.2f}%)"
            )
        if not positions:
            summary.append("(No open positions)")
        return "\n".join(summary)
    except Exception as e:
        return f"ERROR: Failed to get portfolio - {str(e)}"

def get_watchlist_resource() -> str:
    data = get_watchlist_data()
    if not data:
        return "Watchlist is empty. Use add_to_watchlist() to track symbols."
    summary = ["=== MARKET WATCHLIST ==="]
    for symbol, info in data.items():
        if "error" in info:
            summary.append(f"{symbol}: ERROR - {info['error']}")
        else:
            price = info.get("price", 0.0)
            summary.append(f"{symbol}: ${price:,.2f}")
    return "\n".join(summary)

def get_news_resource() -> str:
    return get_latest_news_for_watchlist()

def get_crypto_resource() -> str:
    return get_trending_crypto()

# ----------------------------------------------------------------------
# Prompt‑style tools (converted to functions)
# ----------------------------------------------------------------------
def morning_briefing() -> str:
    portfolio = get_positions()
    owned_symbols = list(portfolio.get("positions", {}).keys())
    watchlist = _load_watchlist()
    owned_but_not_watched = [s for s in owned_symbols if s not in watchlist]
    return f"""
Please generate a Morning Trading Briefing.

STEP 0: SYNC WATCHLIST (Auto‑maintenance)
{f"⚠️ Detected {len(owned_but_not_watched)} owned symbols not in watchlist: {owned_but_not_watched}" if owned_but_not_watched else "✅ Watchlist is synced with portfolio"}

CONTEXT:
1. Portfolio cash ${portfolio.get('cash',0):,.2f}, equity ${portfolio.get('equity',0):,.2f}
   Positions: {owned_symbols}
2. Watchlist: {watchlist}

BRIEFING STEPS:
- Review held positions, watchlist moves, top headlines, sentiment, risk checks, and give recommendations.
"""

def analyze_ticker(symbol: str) -> str:
    return f"""
Please perform a comprehensive analysis on {symbol}.
Steps: price trends, fundamentals, recent news, sentiment (FinBERT), technical indicators (RSI, MACD).
Output an executive summary with buy/sell/hold recommendation.
"""

def risk_analysis() -> str:
    portfolio = get_positions()
    positions = portfolio.get("positions", {})
    return f"""
Perform a risk analysis on the portfolio:
{dict(positions)}
Include volatility, VaR (95%), max drawdown, Monte Carlo forecast and sector concentration.
"""

def backtest_strategy(symbol: str, fast_ma: int = 10, slow_ma: int = 50) -> str:
    return f"""
Backtest a moving‑average crossover on {symbol} (fast={fast_ma}, slow={slow_ma}).
Run historical test (2020‑01‑01 → 2023‑12‑31) and walk‑forward validation.
Report viability, weaknesses and suggested parameter tweaks.
"""

def crypto_market_update() -> str:
    return """
Generate a Crypto Market Update using trending coins, BTC/ETH analysis and price levels.
"""

def portfolio_rebalance(target_symbols: str) -> str:
    """Portfolio rebalancing workflow prompt."""
    return f"""
🔄 **PORTFOLIO REBALANCE WORKFLOW**

Target Symbols: {target_symbols}

1. get_positions() - Review current holdings
2. mean_variance_optimize(tickers="{target_symbols}", lookback="1y") - Calculate optimal weights
3. For each symbol that needs rebalancing:
   - get_price(symbol, period="1mo", visualize=True) - Check recent trends
   - get_symbol_sentiment(symbol) - Validate timing
4. Execute trades via place_order() with calculated quantities
5. Log reasoning with log_action()
"""

def morning_gamma_hunt() -> str:
    """Morning workflow to find and analyze unusual market activity."""
    return """
🔥 **MORNING GAMMA HUNT WORKFLOW**

Find unusual activity and deep dive into the best opportunities.

**Step 1: Scan the Market**
- scan_unusual_activity("big_movers", limit=15, visualize=True)
- scan_unusual_activity("volume_spikes", limit=10, visualize=False)

**Step 2: Pick Top 3 Tickers**
Choose the 3 most interesting from the scans based on:
- Price change magnitude
- Volume conviction (volume_ratio > 2.0)
- Sector/industry relevance

**Step 3: Deep Dive Each Ticker**
For each of the 3 selected tickers:
1. get_price(symbol, period="1mo", interval="1d", visualize=True) - Check 30-day trend
2. get_symbol_sentiment(symbol) - News sentiment analysis
3. get_technical_summary(symbol) - RSI, MACD signals
4. get_fundamentals(symbol) - Quick fundamental check

**Step 4: Rank by Conviction**
Create a ranked list with:
- Symbol
- Entry thesis (why interesting)
- Key catalysts (news, technicals)
- Risk factors
- Conviction score (1-10)

**Output Format:**
Present as a concise markdown table with actionable insights.
"""

def sync_watchlist() -> str:
    portfolio = get_positions()
    owned_symbols = list(portfolio.get("positions", {}).keys())
    watchlist = _load_watchlist()
    owned_but_not_watched = [s for s in owned_symbols if s not in watchlist]
    watched_but_not_owned = [s for s in watchlist if s not in owned_symbols]
    return f"""
Synchronize watchlist with portfolio.
Add missing owned symbols: {owned_but_not_watched}
Optionally remove symbols not owned: {watched_but_not_owned}
"""

# ----------------------------------------------------------------------
# Tool organization & dynamic Interface generator
# ----------------------------------------------------------------------
tools_map = {
    "Dashboard": [health_check, get_account_info, get_portfolio_summary],
    "Market Data": [get_price, get_fundamentals, get_orderbook],
    "Market Screener": [scan_unusual_activity],
    "Execution": [place_order, cancel_order, get_positions, flatten, get_order_history],
    "Risk Management": [portfolio_risk, var, max_drawdown, monte_carlo_simulation],
    "Backtesting": [run_backtest, walk_forward_analysis],
    "Technical Analysis": [compute_indicators, rolling_stats, get_technical_summary],
    "Portfolio Opt": [mean_variance_optimize, risk_parity],
    "News & Sentiment": [get_news, analyze_sentiment, get_symbol_sentiment, get_news_resource],
    "Watchlist": [add_to_watchlist, remove_from_watchlist, get_watchlist_resource, sync_watchlist],
    "Crypto": [
        get_crypto_price,
        get_crypto_market_data,
        get_trending_crypto,
        search_crypto,
        get_crypto_resource,
        crypto_market_update,
    ],
    "Prompts": [
        morning_briefing,
        morning_gamma_hunt,
        analyze_ticker,
        risk_analysis,
        backtest_strategy,
        portfolio_rebalance,
    ],
    "Resources": [get_algo_cheat_sheet, get_classic_papers, get_risk_checklist],
    "Utils": [log_action],
}

def create_interface(tool: Callable):
    """Create a simple Gradio Interface for any callable tool."""
    sig = inspect.signature(tool)
    inputs = []
    for name, param in sig.parameters.items():
        if param.annotation is int:
            inputs.append(gr.Number(label=name, precision=0))
        elif param.annotation is float:
            inputs.append(gr.Number(label=name))
        elif param.annotation is bool:
            inputs.append(gr.Checkbox(label=name))
        else:
            inputs.append(gr.Textbox(label=name))
    output = gr.Textbox(label="Result")
    return gr.Interface(fn=tool, inputs=inputs, outputs=output, flagging_mode="never")

# ----------------------------------------------------------------------
# UI helper callbacks
# ----------------------------------------------------------------------
def save_settings(alpaca_key, alpaca_secret, newsapi_key, modal_url):
    try:
        env_content = f'''NEWSAPI_KEY="{newsapi_key}"
ALPACA_API_KEY="{alpaca_key}"
ALPACA_SECRET_KEY="{alpaca_secret}"
MODAL_ENDPOINT_URL={modal_url}
'''
        with open(".env", "w") as f:
            f.write(env_content)
        return "✅ Settings saved! Restart the server to apply changes."
    except Exception as e:
        return f"❌ Error saving settings: {str(e)}"

def refresh_dashboard():
    return (
        get_portfolio_summary(),
        get_watchlist_resource(),
        get_crypto_resource(),
        get_news_resource(),
    )

# ----------------------------------------------------------------------
# Custom CSS & static HTML
# ----------------------------------------------------------------------
CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --glass-bg: rgba(15, 23, 42, 0.6);
    --glass-border: rgba(255, 255, 255, 0.05);
    --accent-glow: rgba(59, 130, 246, 0.15);
}

.gradio-container {
    background: transparent !important;
}

/* Typography & Base */
body {
    font-family: 'Inter', sans-serif;
    background-color: #020617; /* neutral-950 */
}

h1, h2, h3, h4, h5, h6 {
    font-weight: 600;
    letter-spacing: -0.01em;
}

code, .code-block {
    font-family: 'JetBrains Mono', monospace;
}

/* Utilities */
.icon-mono {
    filter: grayscale(100%) brightness(1.2);
    display: inline-block;
}

/* Landing Page */
.landing-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 80vh;
    text-align: center;
    padding: 4rem 2rem;
    position: relative;
    overflow: hidden;
}

.hero-title {
    font-size: 4rem;
    font-weight: 700;
    margin-bottom: 1rem;
    color: #f8fafc;
    letter-spacing: -0.03em;
}

.hero-subtitle {
    font-size: 1.125rem;
    color: #94a3b8;
    margin-bottom: 3rem;
    line-height: 1.6;
    max-width: 600px;
    margin-left: auto;
    margin-right: auto;
}

/* Feature Grid */
.feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1.5rem;
    width: 100%;
    max-width: 1200px;
    margin-top: 2rem;
}

.feature-card {
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
    padding: 1.5rem;
    border-radius: 12px;
    text-align: left;
    transition: transform 0.2s ease, border-color 0.2s ease;
}

.feature-card:hover {
    transform: translateY(-2px);
    border-color: rgba(255, 255, 255, 0.1);
}

.feature-icon {
    font-size: 1.25rem;
    margin-bottom: 1rem;
    color: #e2e8f0;
    opacity: 0.8;
}

.feature-title {
    font-size: 1rem;
    font-weight: 600;
    color: #f1f5f9;
    margin-bottom: 0.5rem;
}

.feature-desc {
    font-size: 0.875rem;
    color: #94a3b8;
    line-height: 1.5;
}

/* Buttons */
.primary-btn {
    font-weight: 500 !important;
    border-radius: 8px !important;
}

.secondary-btn {
    background: transparent !important;
    border: 1px solid var(--glass-border) !important;
    color: #cbd5e1 !important;
    font-weight: 500 !important;
    border-radius: 8px !important;
}

.secondary-btn:hover {
    background: rgba(255, 255, 255, 0.05) !important;
    border-color: rgba(255, 255, 255, 0.1) !important;
}

/* Setup Page */
.setup-container {
    max-width: 900px;
    margin: 0 auto;
    padding: 3rem 1.5rem;
}

.ui-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 2rem;
}

.setup-card {
    background: rgba(15, 23, 42, 0.4);
    border: 1px solid var(--glass-border);
    border-radius: 12px;
    padding: 2rem;
    margin-bottom: 1.5rem;
}

.step-number {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 20px;
    height: 20px;
    background: #334155;
    color: #f8fafc;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-right: 0.75rem;
}

.code-block {
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 6px;
    padding: 1rem;
    margin: 0.75rem 0;
    font-size: 0.85rem;
    color: #e2e8f0;
    overflow-x: auto;
}

.path-highlight {
    color: #60a5fa;
}
"""

LANDING_HTML = """
<div class="landing-container">
    <div class="hero-content">
        <div class="hero-title">MonteWalk</div>
        <div class="hero-subtitle">
            Institutional-grade quantitative finance tools for AI agents.<br>
            Real-time market data, risk analytics, and portfolio optimization via MCP.
        </div>
        
        <div class="feature-grid">
            <div class="feature-card">
                <div class="feature-icon"><span class="icon-mono">📊</span></div>
                <div class="feature-title">Market Intelligence</div>
                <div class="feature-desc">Real-time data from Alpaca, Yahoo Finance, and CoinGecko with 5-minute caching.</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon"><span class="icon-mono">⚡</span></div>
                <div class="feature-title">Execution Engine</div>
                <div class="feature-desc">Paper trading environment with $100k virtual capital for strategy testing.</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon"><span class="icon-mono">🛡️</span></div>
                <div class="feature-title">Risk Analytics</div>
                <div class="feature-desc">Institutional metrics: VaR, Monte Carlo simulations, and volatility analysis.</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon"><span class="icon-mono">🔬</span></div>
                <div class="feature-title">Backtesting</div>
                <div class="feature-desc">Professional walk-forward analysis engine for strategy validation.</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon"><span class="icon-mono">🧠</span></div>
                <div class="feature-title">Sentiment AI</div>
                <div class="feature-desc">FinBERT-powered news analysis for institutional-grade sentiment scoring.</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon"><span class="icon-mono">👁️</span></div>
                <div class="feature-title">Smart Watchlist</div>
                <div class="feature-desc">Automated portfolio synchronization and intelligent monitoring.</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon"><span class="icon-mono">📈</span></div>
                <div class="feature-title">Advanced Visualizations</div>
                <div class="feature-desc">6 chart types including candlestick, histogram, and heatmap with dark theme.</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon"><span class="icon-mono">🔍</span></div>
                <div class="feature-title">Market Scanner</div>
                <div class="feature-desc">Detect big movers, volume spikes, and reversal candidates in real-time.</div>
            </div>
        </div>
    </div>
</div>
"""

MCP_CLIENT_SETUP_HTML = """
<div class="setup-container">
    <div class="setup-header">
        <h2 style="font-size: 2.5rem; font-weight: 700; margin-bottom: 0.5rem; color: #f8fafc;">Connect Your AI Assistant</h2>
        <p style="color: #94a3b8; font-size: 1.1rem;">Enable MonteWalk tools in your favorite AI environment.</p>
    </div>

    <div class="setup-card">
        <h2 style="color: #f1f5f9; display: flex; align-items: center; gap: 1rem; font-size: 1.25rem;">
            <span class="icon-mono" style="font-size: 1.5rem;">🤖</span> Claude Desktop
        </h2>
        <p style="color: #94a3b8; margin-bottom: 1.5rem; font-size: 0.95rem;">Recommended for the best agentic experience.</p>
        
        <h3 style="color: #e2e8f0; font-size: 1rem; margin-bottom: 0.5rem;"><span class="step-number">1</span> Locate Configuration</h3>
        <p style="color: #94a3b8; font-size: 0.9rem; margin-bottom: 1rem;">
            Open your config file at:<br>
            <span style="opacity: 0.7">macOS:</span> <code>~/Library/Application Support/Claude/claude_desktop_config.json</code><br>
            <span style="opacity: 0.7">Windows:</span> <code>%APPDATA%\\Claude\\claude_desktop_config.json</code>
        </p>

        <h3 style="color: #e2e8f0; font-size: 1rem; margin-bottom: 0.5rem;"><span class="step-number">2</span> Add Server Definition</h3>
        <div class="code-block">{
  "mcpServers": {
    "montewalk": {
      "command": "<span class="path-highlight">/absolute/path/to/MonteWalk/.venv/bin/python</span>",
      "args": ["<span class="path-highlight">/absolute/path/to/MonteWalk/server.py</span>"]
    }
  }
}</div>
    </div>

    <div class="setup-card">
        <h2 style="color: #f1f5f9; display: flex; align-items: center; gap: 1rem; font-size: 1.25rem;">
            <span class="icon-mono" style="font-size: 1.5rem;">💻</span> VSCode & Cursor
        </h2>
        
        <h3 style="color: #e2e8f0; font-size: 1rem; margin-top: 1.5rem; margin-bottom: 0.5rem;"><span class="step-number">1</span> Install Extension</h3>
        <p style="color: #94a3b8; margin-bottom: 1.5rem; font-size: 0.9rem;">Search for <strong>"Model Context Protocol"</strong> in the marketplace.</p>

        <h3 style="color: #e2e8f0; font-size: 1rem; margin-bottom: 0.5rem;"><span class="step-number">2</span> Configure Settings</h3>
        <div class="code-block">"mcp.servers": {
  "montewalk": {
    "command": "<span class="path-highlight">/absolute/path/to/MonteWalk/.venv/bin/python</span>",
    "args": ["<span class="path-highlight">/absolute/path/to/MonteWalk/server.py</span>"]
  }
}</div>
    </div>
</div>
"""

# ----------------------------------------------------------------------
# Gradio app definition
# ----------------------------------------------------------------------
with gr.Blocks(title="MonteWalk MCP Server") as demo:
    # Apply custom CSS globally
    gr.HTML(f"<style>{CUSTOM_CSS}</style>")

    # ---------- Landing page ----------
    with gr.Column(visible=True, elem_classes="landing-container") as landing_page:
        gr.HTML(LANDING_HTML)
        with gr.Row(elem_id="action-buttons"):
            with gr.Column(scale=1):
                pass
            with gr.Column(scale=2):
                with gr.Row():
                    ui_btn = gr.Button(
                        "Test via UI",
                        elem_classes="primary-btn",
                        size="lg",
                    )
                    client_btn = gr.Button(
                        "Setup MCP Client",
                        elem_classes="secondary-btn",
                        size="lg",
                    )
            with gr.Column(scale=1):
                pass

    # ---------- UI Dashboard ----------
    with gr.Column(visible=False, elem_classes="ui-container") as ui_page:
        # Top‑right back button
        with gr.Row():
            back_from_ui_btn = gr.Button("← Back to Home", size="sm", elem_classes="secondary-btn")
        gr.Markdown("# MonteWalk Trading Terminal")
        with gr.Tabs():
            # ----- Dashboard tab -----
            with gr.Tab("Dashboard"):
                with gr.Row():
                    refresh_btn = gr.Button("Refresh Data", variant="primary")
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### Portfolio")
                        portfolio_view = gr.Textbox(
                            label="Holdings",
                            value="Click 'Refresh Data' to load...",
                            lines=10,
                            interactive=False,
                        )
                    with gr.Column(scale=1):
                        gr.Markdown("### Watchlist")
                        watchlist_view = gr.Textbox(
                            label="Market Data",
                            value="Click 'Refresh Data' to load...",
                            lines=10,
                            interactive=False,
                        )
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### Crypto Trends")
                        crypto_view = gr.Textbox(
                            label="Trending Coins",
                            value="Click 'Refresh Data' to load...",
                            lines=8,
                            interactive=False,
                        )
                    with gr.Column(scale=1):
                        gr.Markdown("### News Feed")
                        news_view = gr.Textbox(
                            label="Latest Headlines",
                            value="Click 'Refresh Data' to load...",
                            lines=8,
                            interactive=False,
                        )
                refresh_btn.click(
                    fn=refresh_dashboard,
                    inputs=[],
                    outputs=[portfolio_view, watchlist_view, crypto_view, news_view],
                )
            # ----- Toolbox tab -----
            with gr.Tab("Toolbox"):
                gr.Markdown("Direct access to all MCP tools.")
                for category, tools in tools_map.items():
                    with gr.Accordion(category, open=False):
                        for tool in tools:
                            with gr.Accordion(tool.__name__, open=False):
                                create_interface(tool)
            # ----- Settings tab -----
            with gr.Tab("Settings"):
                gr.Markdown("### API Configuration")
                gr.Markdown("Update your keys below – a server restart is required for changes to take effect.")
                with gr.Row():
                    alpaca_key_input = gr.Textbox(label="Alpaca API Key", type="password", placeholder="PK...")
                    alpaca_secret_input = gr.Textbox(label="Alpaca Secret Key", type="password", placeholder="...")
                with gr.Row():
                    newsapi_input = gr.Textbox(label="NewsAPI Key", type="password", placeholder="...")
                    modal_url_input = gr.Textbox(label="Modal Endpoint URL", placeholder="https://...")
                save_btn = gr.Button("Save Settings")
                settings_output = gr.Textbox(label="Status")
                save_btn.click(
                    fn=save_settings,
                    inputs=[alpaca_key_input, alpaca_secret_input, newsapi_input, modal_url_input],
                    outputs=settings_output,
                )

    # ---------- MCP Client Setup page ----------
    with gr.Column(visible=False) as client_page:
        with gr.Row():
            back_from_client_btn = gr.Button("← Back to Home", size="sm", elem_classes="secondary-btn")
        gr.HTML(MCP_CLIENT_SETUP_HTML)

    # ---------- Navigation callbacks ----------
    def go_to_ui():
        return gr.update(visible=False), gr.update(visible=True), gr.update(visible=False)

    def go_to_client():
        return gr.update(visible=False), gr.update(visible=False), gr.update(visible=True)

    def go_home():
        return gr.update(visible=True), gr.update(visible=False), gr.update(visible=False)

    ui_btn.click(fn=go_to_ui, outputs=[landing_page, ui_page, client_page], scroll_to_output=True)
    client_btn.click(fn=go_to_client, outputs=[landing_page, ui_page, client_page], scroll_to_output=True)
    back_from_ui_btn.click(fn=go_home, outputs=[landing_page, ui_page, client_page], scroll_to_output=True)
    back_from_client_btn.click(fn=go_home, outputs=[landing_page, ui_page, client_page], scroll_to_output=True)

if __name__ == "__main__":
    import os
    
    logger.info("Starting MonteWalk Gradio MCP Server...")
    server_name = os.getenv("GRADIO_SERVER_NAME", "localhost")
    server_port = int(os.getenv("GRADIO_SERVER_PORT", "7860"))
    logger.info(f"UI URL: http://{server_name}:{server_port}")
    logger.info("MCP enabled – tools available to clients")
    
    demo.launch(
        mcp_server=True,
        footer_links=["gradio", "settings", "api"],
        theme=ProfessionalTheme(),
        server_name=server_name,
        server_port=server_port
    )