from config import NEWS_API_KEY, TOPICS, DOMAINS, SENTIMENT_THRESHOLD, RELEVANCE_THRESHOLD, AZURE_DEPLOYMENT_NAME
from clients import openai_client, tweepy_client
from news_fetcher import fetch_news
from workflow import filter_positive_articles, process_top_article
from logger import logger  # Import the centralized logger

def main():
    try:
        logger.info("Fetching news articles...")
        articles = fetch_news(TOPICS, DOMAINS, NEWS_API_KEY)
        if not articles:
            logger.warning("No articles fetched from NewsAPI.")
            return

        logger.info("Filtering positive articles...")
        positive_articles = filter_positive_articles(
            articles, openai_client, AZURE_DEPLOYMENT_NAME, SENTIMENT_THRESHOLD, RELEVANCE_THRESHOLD
        )

        if positive_articles:
            logger.info("Processing the top article...")
            process_top_article(positive_articles, openai_client, tweepy_client, AZURE_DEPLOYMENT_NAME)
        else:
            logger.warning("No overwhelmingly positive and relevant articles found.")

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()



