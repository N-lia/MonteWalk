"""
News Intelligence & Sentiment Analysis Tools
Uses yfinance for news headlines and TextBlob for sentiment scoring.
"""

import yfinance as yf
from textblob import TextBlob
from gnews import GNews
from typing import List, Dict, Any
import logging
from typing import List, Dict, Any
import logging
from tools.watchlist import _load_watchlist
from newsapi import NewsApiClient
from config import NEWSAPI_KEY

logger = logging.getLogger(__name__)

def get_news(symbol: str, max_items: int = 10) -> str:
    """
    Retrieves recent news headlines for a given symbol.
    
    Args:
        symbol: Ticker symbol.
        max_items: Maximum number of news items to return.
    
    Returns:
        JSON string of news articles with titles and publishers.
    """
    try:
        ticker = yf.Ticker(symbol)
        news = ticker.news
        
        if not news:
            # Try NewsAPI first if available
            if NEWSAPI_KEY:
                logger.info(f"yfinance news empty for {symbol}, trying NewsAPI")
                newsapi_results = get_newsapi_articles(symbol, max_items)
                if newsapi_results:
                    import json
                    return json.dumps(newsapi_results, indent=2)
            
            # Fallback to Google News
            logger.info(f"Trying GNews fallback for {symbol}")
            gnews_results = get_google_news(symbol, max_items)
            if gnews_results:
                import json
                return json.dumps(gnews_results, indent=2)
            
            logger.warning(f"No news found for {symbol} from any source")
            return f"No news found for {symbol}"
        
        # Limit results
        news = news[:max_items]
        
        # Extract relevant fields (handle nested yfinance structure)
        results = []
        for item in news:
            # yfinance returns nested structure with 'content' key
            content = item.get("content", item)  # fallback to item if no content key
            title = content.get("title", "")
            
            # Publisher info is in 'provider' dict
            provider = content.get("provider", {})
            publisher = provider.get("displayName", "") if isinstance(provider, dict) else item.get("publisher", "")
            
            link = content.get("canonicalUrl", {}).get("url", "")
            if not link:
                link = item.get("link", "")
            
            results.append({
                "title": title,
                "publisher": publisher,
                "link": link,
            })
        
        logger.info(f"Fetched {len(results)} news items for {symbol} from yfinance")
        import json
        return json.dumps(results, indent=2)
        
    except Exception as e:
        logger.error(f"Error fetching news for {symbol}: {e}", exc_info=True)
        return f"Error fetching news for {symbol}: {str(e)}"


def get_google_news(symbol: str, max_items: int = 5) -> List[Dict]:
    """
    Fetches news from Google News via GNews library.
    """
    try:
        google_news = GNews(max_results=max_items)
        # Search for the symbol
        results = google_news.get_news(symbol)
        
        cleaned = []
        for item in results:
            cleaned.append({
                "title": item.get("title", ""),
                "publisher": item.get("publisher", {}).get("title", "Unknown"),
                "link": item.get("url", ""),
                "published": item.get("published date", "")
            })
        return cleaned
    except Exception as e:
        logger.error(f"GNews error for {symbol}: {e}")
        return []


def get_newsapi_articles(symbol: str, max_items: int = 5) -> List[Dict]:
    """
    Fetches news from NewsAPI.org using the company name or symbol.
    """
    if not NEWSAPI_KEY:
        logger.warning("NewsAPI key not configured")
        return []
        
    try:
        newsapi = NewsApiClient(api_key=NEWSAPI_KEY)
        
        # Search for the symbol (NewsAPI works better with company names, but symbols can work)
        # We'll search in business category for relevance
        response = newsapi.get_everything(
            q=symbol,
            language='en',
            sort_by='publishedAt',
            page_size=max_items
        )
        
        articles = response.get('articles', [])
        cleaned = []
        for article in articles:
            cleaned.append({
                "title": article.get("title", ""),
                "publisher": article.get("source", {}).get("name", "Unknown"),
                "link": article.get("url", ""),
                "published": article.get("publishedAt", ""),
                "description": article.get("description", "")
            })
        return cleaned
    except Exception as e:
        logger.error(f"NewsAPI error for {symbol}: {e}")
        return []


def analyze_sentiment(text: str) -> Dict[str, Any]:
    """
    Analyzes the sentiment of a given text using TextBlob.
    
    Args:
        text: Text to analyze (e.g., news headline, article).
    
    Returns:
        Dictionary with polarity, subjectivity, and classification.
    """
    try:
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity  # -1 (negative) to 1 (positive)
        subjectivity = blob.sentiment.subjectivity  # 0 (objective) to 1 (subjective)
        
        # Classify
        if polarity > 0.2:
            classification = "POSITIVE"
        elif polarity < -0.2:
            classification = "NEGATIVE"
        else:
            classification = "NEUTRAL"
        
        return {
            "text": text[:100] + "..." if len(text) > 100 else text,
            "polarity": round(polarity, 3),
            "subjectivity": round(subjectivity, 3),
            "classification": classification
        }
        
    except Exception as e:
        return {"error": f"Error analyzing sentiment: {str(e)}"}


def get_symbol_sentiment(symbol: str) -> str:
    """
    Fetches recent news for a symbol and calculates aggregate sentiment.
    
    Args:
        symbol: Ticker symbol.
    
    Returns:
        Aggregate sentiment analysis of recent news.
    """
    try:
        ticker = yf.Ticker(symbol)
        news = ticker.news[:10]  # Last 10 articles
        
        if not news:
            return f"No news found for {symbol}"
        
        sentiments = []
        for item in news:
            title = item.get("title", "")
            if title:
                blob = TextBlob(title)
                sentiments.append(blob.sentiment.polarity)
        
        if not sentiments:
            return f"No valid news titles for {symbol}"
        
        avg_polarity = sum(sentiments) / len(sentiments)
        
        if avg_polarity > 0.1:
            classification = "BULLISH"
        elif avg_polarity < -0.1:
            classification = "BEARISH"
        else:
            classification = "NEUTRAL"
        
        return (f"Sentiment Analysis for {symbol} ({len(sentiments)} articles):\n"
                f"Average Polarity: {avg_polarity:.3f}\n"
                f"Market Sentiment: {classification}")
        
    except Exception as e:
        return f"Error analyzing sentiment for {symbol}: {str(e)}"

def get_latest_news_for_watchlist() -> str:
    """
    Aggregates the top news headline for each symbol in the watchlist.
    Falls back to GNews if yfinance returns no results.
    """
    watchlist = _load_watchlist()
    if not watchlist:
        return "Watchlist is empty."
        
    summary = ["=== LATEST NEWS (Watchlist) ==="]
    
    for symbol in watchlist:
        try:
            # Try yfinance first
            ticker = yf.Ticker(symbol)
            news = ticker.news
            
            # If yfinance empty, try GNews
            if not news:
                gnews_results = get_google_news(symbol, max_items=1)
                if gnews_results:
                    top_item = gnews_results[0]
                    title = top_item.get("title", "No Title")
                    publisher = top_item.get("publisher", "Unknown")
                    summary.append(f"[{symbol}] {title} ({publisher})")
                else:
                    summary.append(f"[{symbol}] No recent news.")
            else:
                top_item = news[0]
                title = top_item.get("title", "No Title")
                publisher = top_item.get("publisher", "Unknown")
                summary.append(f"[{symbol}] {title} ({publisher})")
        except Exception as e:
            logger.error(f"Error fetching news for {symbol}: {e}")
            summary.append(f"[{symbol}] Error fetching news.")
            
    return "\n".join(summary)
