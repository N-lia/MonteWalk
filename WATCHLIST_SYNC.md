# Intelligent Watchlist Sync - Usage Guide

## 🎯 Overview

MonteWalk now includes **AI-powered watchlist synchronization** via prompts. Instead of hardcoding sync logic, the AI agent intelligently manages your watchlist based on your trading activity.

---

## 🆕 New Prompts

### 1. `sync_watchlist()` - Manual Sync

**Purpose**: Synchronize watchlist with portfolio holdings on-demand

**When to Use**:
- After executing multiple trades
- Want to clean up watchlist
- Periodically (weekly/monthly)

**What It Does**:
1. Compares portfolio holdings vs watchlist
2. Auto-adds owned symbols to watchlist
3. Offers to remove symbols you've sold (optional)
4. Keeps research symbols (in watchlist but not owned)

**Example Usage**:

```
You: Run sync_watchlist

Claude:
"I've analyzed your portfolio and watchlist:

Portfolio Holdings: ['AAPL', 'MSFT', 'GOOGL']
Watchlist: ['AAPL', 'TSLA', 'NVDA']

Discrepancies:
- Owned but NOT in watchlist: ['MSFT', 'GOOGL']
- In watchlist but NOT owned: ['TSLA', 'NVDA']

Syncing now...
✅ Added MSFT to watchlist
✅ Added GOOGL to watchlist
🔍 Keeping TSLA and NVDA (research symbols)

Watchlist now tracking 5 symbols (3 owned, 2 research)"
```

---

### 2. Enhanced `morning_briefing()` - Auto-Sync

**Purpose**: Daily briefing with automatic watchlist maintenance

**What Changed**: Now includes **Step 0: Auto-sync** before briefing

**What It Does**:
1. Detects if any owned symbols are missing from watchlist
2. Automatically adds them
3. Proceeds with regular morning briefing

**Example Usage**:

```
You: Run morning_briefing

Claude:
"STEP 0: SYNC WATCHLIST
⚠️ Detected 1 owned symbol not in watchlist: ['AAPL']
Adding AAPL to watchlist...
✅ Watchlist synced

📊 PORTFOLIO SUMMARY
Cash: $95,000
Equity: $105,000
Positions: AAPL (10 shares, +2.3% today)

📰 MARKET NEWS
1. Apple announces new AI features (Bloomberg)
2. Tech sector rallies on Fed comments...

⚠️ RISK STATUS
Portfolio Volatility: 18.5% (annualized)
VaR (95%): $2,450 potential loss in bad day
Status: Moderate risk

💡 TODAY'S RECOMMENDATIONS
- Consider taking profits on AAPL (+2.3%)
- Watch for Fed announcement at 2pm
- Portfolio is single-stock concentrated, consider diversifying"
```

---

## 🔄 How Auto-Sync Works

### Smart Detection

The agent detects three scenarios:

#### Scenario 1: Owned but Not Watched ❌→✅
```
Portfolio: ['AAPL', 'MSFT']
Watchlist: ['AAPL']

Action: Auto-add MSFT to watchlist
Reason: You own it, you should track it
```

#### Scenario 2: Watched but Not Owned 🔍
```
Portfolio: ['AAPL']
Watchlist: ['AAPL', 'TSLA', 'NVDA']

Action: Keep TSLA and NVDA (research symbols)
Reason: You might want to buy them later
Optional: Can remove if recently sold
```

#### Scenario 3: Already Synced ✅
```
Portfolio: ['AAPL', 'MSFT']
Watchlist: ['AAPL', 'MSFT', 'TSLA']

Action: None (already in sync)
Status: ✅ Watchlist is synced with portfolio
```

---

## 💡 Usage Patterns

### Pattern 1: After Trading

```
You: Buy 10 shares of Apple at market price

Claude: 
"✅ Market Order Submitted: BUY 10 AAPL
Order ID: abc123..."

You: Sync watchlist

Claude:
"✅ Added AAPL to watchlist (now tracking owned position)
Watchlist now has 3 symbols"
```

### Pattern 2: Daily Morning Routine

```
You: Run morning_briefing

Claude:
[Automatically syncs watchlist first]
[Then provides full briefing]
```

### Pattern 3: Weekly Cleanup

```
You: Sync watchlist and clean up old symbols

Claude:
"Analyzing watchlist...
Found 3 symbols you've sold:
- TSLA (sold 5 days ago)
- NVDA (sold 2 weeks ago)
- AMD (sold 1 month ago)

Removing old positions...
✅ Watchlist cleaned
Now tracking 5 symbols (5 owned, 0 research)"
```

### Pattern 4: Research Workflow

```
You: Add TSLA and NVDA to watchlist for research

Claude: 
"✅ Added TSLA to watchlist
✅ Added NVDA to watchlist"

[Later, after buying TSLA]

You: Buy 5 shares of TSLA

Claude:
"✅ Order filled
Note: TSLA already in watchlist (no action needed)"
```

---

## 🎨 Customization Options

### Conservative Mode (Default)
- Keeps all research symbols
- Only adds owned symbols
- Never removes without asking

```
You: Sync watchlist in conservative mode

Claude:
"Keeping all watchlist symbols
Only adding missing owned positions"
```

### Aggressive Cleanup
- Removes sold symbols automatically
- Keeps only owned + actively researched
- Cleans up old entries

```
You: Sync watchlist and remove all sold symbols

Claude:
"Analyzing order history...
Removing symbols sold in last 30 days..."
```

---

## 🔧 Technical Details

### Prompt Architecture

```python
@mcp.prompt()
def sync_watchlist() -> str:
    # Get current state
    portfolio = get_positions()  # From Alpaca
    watchlist = _load_watchlist()  # From local JSON
    
    # Find discrepancies
    owned_but_not_watched = [...]
    watched_but_not_owned = [...]
    
    # Return intelligent prompt for agent
    return """
    Instructions for AI agent to:
    1. Auto-add owned symbols
    2. Handle watched-but-not-owned symbols
    3. Verify sync
    """
```

### Why Prompts Instead of Code?

**❌ Hardcoded Approach**:
```python
# Auto-add after every trade (inflexible)
def place_order(symbol, ...):
    result = broker.submit_order(...)
    add_to_watchlist(symbol)  # Always adds, no intelligence
    return result
```

**✅ Prompt Approach**:
```python
# AI agent decides based on context
@mcp.prompt()
def sync_watchlist():
    # Provides context and options
    # Agent makes intelligent decisions
    # Can handle edge cases
    # User can override
```

**Benefits**:
1. **Flexibility**: Agent can adapt to user preferences
2. **Intelligence**: Understands context (research vs owned)
3. **Explainability**: Shows what it's doing and why
4. **User Control**: Can override agent decisions
5. **No Code Changes**: Behavior adjusts via conversation

---

## 📋 Best Practices

### 1. Run Sync After Trading Sessions
```
Morning: Execute trades
Evening: Run sync_watchlist to clean up
```

### 2. Include in Morning Routine
```
Daily: Run morning_briefing
(Auto-syncs as Step 0)
```

### 3. Periodic Deep Clean
```
Monthly: "Sync watchlist and remove all symbols I haven't owned in 60 days"
```

### 4. Research Symbol Management
```
Before research: "Add TSLA, NVDA, AMD to watchlist"
After buying: Sync happens automatically
After deciding not to buy: "Remove TSLA from watchlist"
```

---

## 🎯 Example Workflows

### Workflow 1: New Trader Setup

```
Day 1:
You: Buy 10 AAPL, 5 MSFT, 3 GOOGL
You: Sync watchlist
Claude: ✅ Added all 3 to watchlist

Day 2:
You: Morning briefing
Claude: [Auto-syncs] ✅ All symbols tracked
```

### Workflow 2: Active Trader

```
Monday: Buy AAPL, MSFT
Tuesday: Buy TSLA, sell AAPL
Wednesday: Run sync_watchlist
Claude: 
- Added TSLA ✅
- AAPL sold but keeping in watchlist (research)
- Tracking 4 symbols (2 owned, 2 research)
```

### Workflow 3: Research-Heavy User

```
You: Add 10 tech stocks to watchlist for research
You: [Analyzes them over the week]
You: Buy AAPL and MSFT
You: Sync watchlist

Claude:
"You own AAPL and MSFT (already in watchlist)
Still researching 8 other symbols
No sync needed ✅"
```

---

## 🚀 Quick Commands

| Command | Result |
|---------|--------|
| `sync_watchlist` | Full sync analysis |
| `morning_briefing` | Auto-sync + briefing |
| `add [symbol] to watchlist` | Manual add |
| `remove [symbol] from watchlist` | Manual remove |
| `show watchlist` | View current watchlist |
| `show positions` | View portfolio |

---

## 🔮 Future Enhancements

Planned improvements:

1. **Auto-remove sold symbols after X days**
   - Configurable threshold (7/30/60 days)
   - Smart detection of "sold permanently" vs "temporary trade"

2. **Watchlist categories**
   - "Owned", "Research", "Sold", "Archived"
   - Better organization

3. **Alpaca native watchlist integration**
   - Sync with Alpaca's cloud watchlist
   - Cross-device consistency

4. **Smart suggestions**
   - "You've researched TSLA for 30 days but haven't bought. Remove?"
   - "NVDA is trending, add to research watchlist?"

---

## ❓ FAQ

**Q: Does sync happen automatically after every trade?**  
A: No. It runs when you invoke a prompt (`sync_watchlist` or `morning_briefing`). This gives you control.

**Q: Will it remove symbols I'm researching?**  
A: No, by default it keeps all "watched but not owned" symbols. You can explicitly ask to remove them.

**Q: What if I want to track a symbol I don't own?**  
A: Perfect! Just add it manually. Sync will keep it as a "research symbol".

**Q: Can I disable auto-sync in morning briefing?**  
A: Yes, just ask: "Give me morning briefing without syncing watchlist"

**Q: Does this work with Alpaca's watchlist feature?**  
A: Not yet. Currently uses local JSON. Alpaca integration is planned.

---

## 📞 Support

If sync isn't working as expected:

1. Check portfolio: `get_positions()`
2. Check watchlist: View `data/watchlist.json`
3. Manual sync: `sync_watchlist`
4. Force rebuild: Delete `data/watchlist.json` and re-add symbols

---

**🎉 Enjoy intelligent watchlist management powered by AI!**
