# VSCode MCP Client Setup Guide

## Prerequisites

1. **Install VSCode** (v1.95 or later)
2. **Enable MCP in VSCode**:
   - Open VSCode settings (Ctrl+, or Cmd+,)
   - Search for `chat.mcp.gallery.enabled`
   - Enable it

## Option 1: Workspace Configuration (Recommended)

### Step 1: Create MCP Configuration File

Create `.vscode/mcp.json` in your workspace:

```json
{
  "mcpServers": {
    "QuantAgent": {
      "command": "uv",
      "args": [
        "run",
        "server.py"
      ],
      "env": {
        "NEWSAPI_KEY": "${env:NEWSAPI_KEY}"
      }
    }
  }
}
```

### Step 2: Set Environment Variables (Optional)

If you have a NewsAPI key, add it to your shell profile:

```bash
export NEWSAPI_KEY="your_key_here"
```

Then reload VSCode.

### Step 3: Start the Server

1. Open the Command Palette (Ctrl+Shift+P or Cmd+Shift+P)
2. Run: `MCP: List Servers`
3. You should see "QuantAgent" listed
4. Select it and click "Start"

## Option 2: Add Server via Command Palette

1. Open Command Palette (Ctrl+Shift+P)
2. Run: `MCP: Add Server`
3. Choose "Workspace" (or "Global" for all projects)
4. Enter configuration:
   - **Name**: `QuantAgent`
   - **Command**: `uv`
   - **Args**: `run server.py`
   - **Working Directory**: `/home/mario/MonteWalk`

## Option 3: Command Line Installation

```bash
code --add-mcp '{
  "command": "uv",
  "args": ["run", "server.py"],
  "cwd": "/home/mario/MonteWalk"
}'
```

## Verifying It Works

1. Open GitHub Copilot Chat in VSCode
2. Type: `@QuantAgent health_check`
3. You should see: "Quant Agent Server is running and healthy."

## Using the Server

Once connected, you can use the tools in Copilot Chat:

```
@QuantAgent get_crypto_price bitcoin
@QuantAgent get_technical_summary AAPL
@QuantAgent What's in my portfolio?
```

## Accessing Resources

Resources appear automatically in Copilot's context:
- `portfolio://summary` - Your current portfolio
- `market://watchlist` - Stocks you're watching
- `news://latest` - Latest news for watchlist
- `crypto://trending` - Trending cryptocurrencies

## Accessing Prompts

Use the prompts via:
```
@QuantAgent /morning_briefing
@QuantAgent /analyze_ticker TSLA
```

## Troubleshooting

### Server Not Starting?

1. Check MCP Server Logs:
   - View → Output → "MCP Server Logs"

2. Verify `uv` is in PATH:
   ```bash
   which uv
   ```

3. Test manually:
   ```bash
   cd /home/mario/MonteWalk
   uv run server.py
   ```

### Can't See Tools?

1. Restart the MCP server:
   - Command Palette → `MCP: Restart Server` → Select "QuantAgent"

2. Check server registration:
   - Command Palette → `MCP: List Servers`

## Next Steps

- Read the tool documentation in the README
- Try the prompts (`morning_briefing`, `analyze_ticker`)
- Check resources in Copilot sidebar
