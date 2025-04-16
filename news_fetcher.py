import requests
from datetime import datetime, timedelta
import urllib.parse

def fetch_news(topics, domains, api_key):
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
    
    print(f"NewsAPI Request URL: {url}")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        news = response.json()
        articles = news.get("articles", [])
        if not articles:
            raise ValueError("No articles found for the given query.")
        return articles
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching news: {e}")
        return []
    except ValueError as e:
        print(f"Error: {e}")
        return []