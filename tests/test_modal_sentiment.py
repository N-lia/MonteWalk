import pytest
from unittest.mock import MagicMock, patch
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock yfinance to avoid import error during testing if not installed in test env
sys.modules['yfinance'] = MagicMock()

from tools.news_intelligence import analyze_sentiment

@patch('tools.news_intelligence.requests.post')
@patch('tools.news_intelligence.MODAL_ENDPOINT_URL', "https://fake-url.modal.run")
def test_modal_success(mock_post):
    """Test successful Modal sentiment analysis via Web Endpoint."""
    # Mock the response
    mock_response = MagicMock()
    mock_response.json.return_value = {'label': 'positive', 'score': 0.95}
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    result = analyze_sentiment("This is a great company.")

    assert result['classification'] == 'POSITIVE'
    assert result['polarity'] == 0.95
    assert result['model'] == 'FinBERT (Modal Public)'

@patch('tools.news_intelligence.requests.post')
def test_modal_failure(mock_post):
    """Test graceful failure when Modal fails (no TextBlob fallback)."""
    # Mock request failure
    mock_post.side_effect = Exception("Connection error")

    result = analyze_sentiment("This is a bad company.")

    # Should return error dict
    assert 'error' in result
    assert 'Connection error' in result['error']