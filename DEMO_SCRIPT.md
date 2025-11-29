# Demo Video Script

## Overview
**Duration**: 3-4 minutes  
**Tone**: Professional but approachable, enthusiastic  
**Format**: Screen recording with voiceover

---

## Script Outline

### Scene 1: Landing Page (20 seconds)
**Visual**: MonteWalk landing page  
**Voiceover**:
> "Meet MonteWalk—an institutional-grade quantitative trading platform built for AI agents. Retail traders struggle with data overload and lack professional risk tools. MonteWalk solves this by connecting AI assistants like Claude to real-time market data, portfolio management, and advanced analytics—all through the Model Context Protocol."

**Action**: Scroll slowly through feature cards

---

### Scene 2: Dashboard Tour (40 seconds)
**Visual**: Click "Test via UI" button, navigate to Dashboard  
**Voiceover**:
> "The Gradio 6 interface gives you a professional trading terminal in your browser. The dashboard shows your portfolio holdings, watchlist with live prices, trending cryptocurrencies, and aggregated news—all in one view."

**Action**: 
1. Show portfolio panel (point out cash, positions)
2. Highlight watchlist with prices
3. Scroll through crypto trends
4. Show news headlines
5. Click "Refresh Data" to demonstrate live updates

---

### Scene 3: Toolbox Deep Dive (50 seconds)
**Visual**: Navigate to Toolbox tab  
**Voiceover**:
> "Behind the scenes, MonteWalk provides 25 specialized tools across 9 categories. Let's test a few."

**Action**:
1. **Market Data**: Open `get_price`, enter "AAPL", period "1mo", show chart
2. **Technical Analysis**: Open `get_technical_summary`, enter "AAPL", show BUY/SELL signal with reasoning
3. **Risk Management**: Open `portfolio_risk`, show volatility calculation
4. **News & Sentiment**: Open `get_symbol_sentiment`, enter "TSLA", show FinBERT analysis

**Voiceover continues**:
> "Each tool is production-ready with error handling, multi-source fallbacks, and intelligent caching."

---

### Scene 4: MCP Integration (40 seconds)
**Visual**: Navigate to "Setup MCP Client" page  
**Voiceover**:
> "The real power comes from connecting MonteWalk to your AI assistant via MCP. Claude Desktop, VSCode, Cursor—any MCP-compatible client can access these tools."

**Action**:
1. Show Claude Desktop config snippet
2. Highlight the simple setup (2 lines of JSON)

**Visual**: Switch to Claude Desktop window (if available)  
**Voiceover**:
> "Once connected, your AI can orchestrate complex workflows—like this morning briefing that analyzes portfolio risk, scans for unusual activity, and summarizes top news."

**Action**: Type in Claude: "Run morning briefing" (show output if possible)

---

### Scene 5: Agentic Workflows (30 seconds)
**Visual**: Back to MonteWalk UI, show Prompts accordion  
**Voiceover**:
> "MonteWalk includes pre-built agentic workflows. The Morning Gamma Hunt finds unusual market activity, deep-dives the top 3 picks, and ranks them by conviction score. The Portfolio Rebalance workflow calculates optimal weights using modern portfolio theory."

**Action**: 
1. Expand Prompts accordion
2. Show `morning_gamma_hunt` prompt text
3. Show `portfolio_rebalance` prompt

---

### Scene 6: Technical Highlights (20 seconds)
**Visual**: Screen showing code editor with app.py  
**Voiceover**:
> "Built with Gradio 6's native MCP support, custom theming, and a robust data pipeline that aggregates from Yahoo Finance, Alpaca, CoinGecko, and NewsAPI—with FinBERT sentiment analysis running on Modal's serverless GPUs."

**Action**: Quick scroll through app.py structure

---

### Scene 7: Real-World Impact (15 seconds)
**Visual**: Back to landing page, scroll to "Real-World Impact" section  
**Voiceover**:
> "MonteWalk democratizes institutional-grade tools for retail traders, provides a reference implementation for financial MCP servers, and showcases the power of agentic AI in finance."

---

### Scene 8: Call to Action (15 seconds)
**Visual**: Gradio UI with clear URL visible  
**Voiceover**:
> "Try MonteWalk on Hugging Face Spaces, connect it to Claude Desktop, or run it locally. Links in the description. Built for the MCP 1st Birthday Hackathon—where AI meets quantitative finance."

**Action**: Show GitHub star button, HF Space link

---

## Recording Tips

### Technical Setup
- **Resolution**: 1080p minimum
- **Tool**: OBS Studio, Loom, or QuickTime
- **Audio**: Clear microphone, no background noise
- **Speed**: Speak at moderate pace, pause between sections

### Visual Quality
- **Hide Distractions**: Close unrelated tabs, clear desktop
- **Highlight**: Use cursor highlights or zoom for important UI elements
- **Smooth Transitions**: No jarring cuts, use fade when switching contexts

### Content Focus
- **Show, Don't Tell**: Let the UI speak for itself
- **Real Data**: Use actual API responses, not mocked data
- **Enthusiasm**: Convey genuine excitement about the project

---

## Post-Production Checklist
- [ ] Add text overlays for key features
- [ ] Include background music (low volume, non-distracting)
- [ ] Add title card with "MonteWalk - MCP 1st Birthday Hackathon"
- [ ] Include end card with links:
  - HF Space URL
  - GitHub URL
  - MCP Hackathon page
- [ ] Export in MP4 (H.264)
- [ ] Upload to YouTube (unlisted is fine)
- [ ] Embed in README
