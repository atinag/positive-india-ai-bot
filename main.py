from config import NEWS_API_KEY, TOPICS, DOMAINS, SENTIMENT_THRESHOLD, RELEVANCE_THRESHOLD, AZURE_DEPLOYMENT_NAME
from clients import openai_client, tweepy_client
from news_fetcher import fetch_news
from workflow import filter_positive_articles, process_top_article
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def main():
    try:
        # Fetch news articles
        articles = fetch_news(TOPICS, DOMAINS, NEWS_API_KEY)
        if not articles:
            logging.warning("No articles fetched from NewsAPI.")
            return

        # Filter positive articles using OpenAI
        positive_articles = filter_positive_articles(
            articles, openai_client, AZURE_DEPLOYMENT_NAME, SENTIMENT_THRESHOLD, RELEVANCE_THRESHOLD
        )

        # Process the top article
        if positive_articles:
            process_top_article(positive_articles, openai_client, tweepy_client, AZURE_DEPLOYMENT_NAME)
        else:
            logging.warning("No overwhelmingly positive and relevant articles found.")

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()



