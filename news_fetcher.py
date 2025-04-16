import requests
from datetime import datetime, timedelta
import urllib.parse
from logger import logger  # Import the centralized logger
from typing import List, Dict
from requests.adapters import HTTPAdapter
import time
from urllib3.util.retry import Retry

def construct_newsapi_url(topics: List[str], domains: str, api_key: str) -> str:
    """
    Constructs the NewsAPI URL based on the given topics, domains, and API key.
    """
    query = " OR ".join(topics)
    encoded_query = urllib.parse.quote(query)
    url = (
        f"https://newsapi.org/v2/everything?"
        f"q={encoded_query}&"
        f"domains={domains}&"
        f"language=en&"
        f"sortBy=publishedAt&"
        f"from={(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')}&"
        f"apiKey={api_key}"
    )
    return url

def fetch_news(topics: List[str], domains: str, api_key: str) -> List[Dict]:
    """
    Fetches news articles from NewsAPI based on the given topics and domains.

    Args:
        topics: List of topics to search for.
        domains: Comma-separated list of domains to restrict the search to.
        api_key: NewsAPI API key.

    Returns:
        A list of articles (dictionaries) or an empty list if an error occurs.
    """
    url = construct_newsapi_url(topics, domains, api_key)
    logger.info(f"Fetching news from URL: {url}")
    
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retries))
    
    try:
        response = session.get(url)
        if response.status_code == 429:  # Too Many Requests
            logger.warning("Rate limit exceeded. Retrying after delay...")
            time.sleep(60)  # Wait for 1 minute before retrying
            response = session.get(url)
        response.raise_for_status()
        news = response.json()
        articles = news.get("articles", [])
        if not articles:
            logger.warning("No articles found for the given query.")
            raise ValueError("No articles found.")
        logger.info(f"Fetched {len(articles)} articles.")
        return articles
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching news: {e}")
        return []
    except ValueError as e:
        logger.error(f"Error: {e}")
        return []