import requests
from datetime import datetime, timedelta
import urllib.parse
from logger import logger  # Import the centralized logger
from typing import List, Dict
from requests.adapters import HTTPAdapter
import time
from urllib3.util.retry import Retry
import random

def construct_newsapi_url(topics: List[str], domains: str, api_key: str, page: int = 1, page_size: int = 20) -> str:
    """
    Constructs the NewsAPI URL based on the given topics, domains, and API key.
    """
    
    selected_topics = random.sample(topics, 3)
    query = " OR ".join(selected_topics)
    encoded_query = urllib.parse.quote(query)
    url = (
        f"https://newsapi.org/v2/everything?"
        f"q={encoded_query}&"
        f"domains={domains}&"
        f"language=en&"
        f"sortBy=publishedAt&"
        f"from={(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')}&"
        f"apiKey={api_key}&"
        f"page={page}&"
        f"pageSize={page_size}"
    )
    return url

def fetch_news(topics: List[str], domains: str, api_key: str, max_pages: int = 5, page_size: int = 20) -> List[Dict]:
    all_articles = []
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retries))

    for page in range(1, max_pages + 1):
        url = construct_newsapi_url(topics, domains, api_key, page=page, page_size=page_size)
        logger.info(f"Fetching news from URL: {url}")
        try:
            response = session.get(url)
            if response.status_code == 429:
                logger.warning("Rate limit exceeded. Retrying after delay...")
                time.sleep(60)
                response = session.get(url)
            response.raise_for_status()
            news = response.json()
            articles = news.get("articles", [])
            if not articles:
                logger.info(f"No more articles found at page {page}.")
                break
            logger.info(f"Fetched {len(articles)} articles from page {page}.")
            all_articles.extend(articles)
            # Stop if less than page_size articles returned (no more pages)
            if len(articles) < page_size:
                break
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching news: {e}")
            break
        except ValueError as e:
            logger.error(f"Error: {e}")
            break
    return all_articles