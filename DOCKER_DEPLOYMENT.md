# Docker Deployment for Hugging Face Spaces

This guide explains how to deploy MonteWalk to Hugging Face Spaces using Docker.

## Quick Deployment

### 1. Create New Space
1. Go to [Hugging Face Spaces](https://huggingface.co/new-space)
2. Fill in:
   - **Space name**: `MonteWalk`
   - **License**: `MIT`
   - **Space SDK**: `Docker`
   - **Visibility**: `Public`

### 2. Clone and Push
```bash
# Clone your new Space
git clone https://huggingface.co/spaces/YOUR_USERNAME/MonteWalk
cd MonteWalk

# Copy MonteWalk files
cp -r /path/to/MonteWalk/* .

# Add, commit, and push
git add .
git commit -m "Initial deployment"
git push
```

### 3. Configure Secrets
In your Space settings, add these secrets:
- `ALPACA_API_KEY`: Your Alpaca paper trading key
- `ALPACA_SECRET_KEY`: Your Alpaca secret
- `NEWSAPI_KEY`: Your NewsAPI key (optional)
- `MODAL_ENDPOINT_URL`: Your Modal FinBERT endpoint

## Files Included

- **Dockerfile**: Container configuration
- **requirements.txt**: Python dependencies
- **app.py**: Main Gradio application
- **README.md**: Documentation (appears on Space page)

## Docker Build

The Dockerfile:
- Uses Python 3.12 slim image
- Installs dependencies from requirements.txt
- Exposes port 7860 (Gradio default)
- Runs `python app.py`

## Local Docker Testing

```bash
# Build image
docker build -t montewalk .

# Run container
docker run -p 7860:7860 \
  -e ALPACA_API_KEY=your_key \
  -e ALPACA_SECRET_KEY=your_secret \
  -e NEWSAPI_KEY=your_key \
  -e MODAL_ENDPOINT_URL=your_url \
  montewalk
```

Access at `http://localhost:7860`

## Troubleshooting

### Build Fails
- Check requirements.txt syntax
- Verify Python version compatibility

### Runtime Errors
- Ensure all secrets are set in Space settings
- Check logs in Space → "Logs" tab

### MCP Not Working
- Verify `demo.launch(mcp_server=True)` in app.py
- Check Gradio version >= 6.0.1

## Environment Variables

The app reads these from HF Spaces secrets:
- `ALPACA_API_KEY` (required)
- `ALPACA_SECRET_KEY` (required)
- `NEWSAPI_KEY` (optional, falls back to GNews)
- `MODAL_ENDPOINT_URL` (for sentiment analysis)

## Next Steps

1. Deploy to HF Spaces
2. Test the UI at your Space URL
3. Record demo video
4. Share on social media using templates in `SOCIAL_POST_TEMPLATE.md`
