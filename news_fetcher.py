import requests
from datetime import datetime, timedelta
import urllib.parse
import logging
from typing import List, Dict
from requests.adapters import HTTPAdapter
import time
from urllib3.util.retry import Retry

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def construct_newsapi_url(topics: List[str], domains: str, api_key: str) -> str:
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
    url = construct_newsapi_url(topics, domains, api_key)
    logging.info(f"Fetching news from URL: {url}")
    
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retries))
    
    try:
        response = session.get(url)
        if response.status_code == 429:  # Too Many Requests
            logging.warning("Rate limit exceeded. Retrying after delay...")
            time.sleep(60)  # Wait for 1 minute before retrying
            response = session.get(url)
        response.raise_for_status()
        news = response.json()
        articles = news.get("articles", [])
        if not articles:
            logging.warning("No articles found for the given query.")
            raise ValueError("No articles found.")
        return articles
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching news: {e}")
        return []
    except ValueError as e:
        logging.error(f"Error: {e}")
        return []