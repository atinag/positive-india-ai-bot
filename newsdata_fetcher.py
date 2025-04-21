import requests
import urllib.parse
from logger import logger
from typing import List, Dict
from requests.adapters import HTTPAdapter
import time
from urllib3.util.retry import Retry
import random
from datetime import datetime, timedelta

NEWSDATA_ENDPOINT = "https://newsdata.io/api/1/news"

def construct_newsdata_url(
    topics: List[str],
    api_key: str,
    country: str = "in",
    language: str = "en",
    next_page: str = None,
    from_date: str = None
) -> str:
    selected_topics = random.sample(topics, min(3, len(topics)))
    query = " OR ".join(selected_topics)
    encoded_query = urllib.parse.quote(query)
    url = (
        f"{NEWSDATA_ENDPOINT}?"
        f"apikey={api_key}&"
        f"q={encoded_query}&"
        f"country={country}&"
        f"language={language}"
    )
    if from_date:
        url += f"&from_date={from_date}"
    if next_page:
        url += f"&page={next_page}"
    return url

def fetch_news(
    topics: List[str],
    api_key: str,
    country: str = "in",
    language: str = "en",
    max_pages: int = 5,
    days: int = 7
) -> List[Dict]:
    all_articles = []
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retries))

    from_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    next_page = None
    for _ in range(max_pages):
        url = construct_newsdata_url(topics, api_key, country, language, next_page, from_date)
        logger.info(f"Fetching news from newsdata.io URL: {url}")
        try:
            response = session.get(url)
            if response.status_code == 429:
                logger.warning("newsdata.io rate limit hit. Sleeping for 60 seconds...")
                time.sleep(60)
                response = session.get(url)
            response.raise_for_status()
            news = response.json()
            articles = news.get("results", [])
            if not articles:
                logger.info("No more articles found.")
                break
            logger.info(f"Fetched {len(articles)} articles.")
            for art in articles:
                all_articles.append({
                    "title": art.get("title"),
                    "description": art.get("description"),
                    "url": art.get("link"),
                    "publishedAt": art.get("pubDate"),
                    "source": {"name": art.get("source_id", "")}
                })
            next_page = news.get("nextPage")
            if not next_page:
                break
        except requests.RequestException as e:
            logger.error(f"Error fetching newsdata.io: {e}")
            break
        except ValueError as e:
            logger.error(f"Error: {e}")
            break
    return all_articles