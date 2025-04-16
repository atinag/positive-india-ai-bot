from config import NEWS_API_KEY, OPENAI_API_KEY, TOPICS, DOMAINS
from news_fetcher import fetch_news
from sentiment_analysis import analyze_sentiment_with_textblob_and_filter, analyze_sentiment_with_openai
from summarizer import summarize_news
from twitter_poster import post_to_twitter
from openai import AzureOpenAI
import tweepy
import os
import logging
from typing import List, Dict, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Azure OpenAI configuration
openai_client = AzureOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    api_version="2023-12-01-preview",
    azure_endpoint="https://azureopenaipoistiveindiabotinstance.openai.azure.com/",
)
AZURE_DEPLOYMENT_NAME = "gpt-35-turbo"

# Twitter API credentials
consumer_key = os.getenv("TWITTER_CONSUMER_KEY")
consumer_secret = os.getenv("TWITTER_CONSUMER_SECRET")
access_token = os.getenv("TWITTER_ACCESS_TOKEN")
access_token_secret = os.getenv("TWITTER_ACCESS_SECRET")
twitter_bearer_token = os.getenv("TWITTER_BEARER_TOKEN")

# Set up Tweepy client
tweepy_client = tweepy.Client(
    bearer_token=twitter_bearer_token,
    consumer_key=consumer_key,
    consumer_secret=consumer_secret,
    access_token=access_token,
    access_token_secret=access_token_secret,
)

# Constants
SENTIMENT_THRESHOLD = 0.5  # At least moderately positive
RELEVANCE_THRESHOLD = 0.5  # At least moderately relevant


def filter_positive_articles(articles: List[Dict], client, model: str) -> List[Tuple[float, Dict]]:
    """
    Filters articles based on OpenAI sentiment and relevance analysis.

    Args:
        articles: List of articles fetched from NewsAPI.
        client: OpenAI client instance.
        model: The OpenAI model to use (e.g., "gpt-35-turbo").

    Returns:
        A sorted list of tuples containing the combined score and the article.
    """
    positive_articles = []
    for article in articles:
        title = article.get("title", "")
        description = article.get("description", "")
        text = f"{title} {description}"

        # Use OpenAI to analyze sentiment and relevance
        sentiment, relevance = analyze_sentiment_with_openai(client, text, model)

        # Only include articles that meet the thresholds
        if sentiment > SENTIMENT_THRESHOLD and relevance > RELEVANCE_THRESHOLD:
            combined_score = (sentiment + relevance) / 2  # Equal weights
            positive_articles.append((combined_score, article))
            logging.info(f"Article selected: {title} (Score: {combined_score})")
        else:
            logging.info(f"Article rejected: {title} (Sentiment: {sentiment}, Relevance: {relevance})")

    # Sort articles by combined score in descending order
    return sorted(positive_articles, reverse=True)


def process_top_article(positive_articles: List[Tuple[float, Dict]]) -> Optional[Dict]:
    """
    Processes the top article by summarizing and posting it to Twitter.

    Args:
        positive_articles: List of positive articles with their scores.

    Returns:
        The top article if successfully processed, otherwise None.
    """
    if not positive_articles:
        logging.warning("No overwhelmingly positive articles found.")
        return None

    # Pick the highest sentiment article
    top_article = positive_articles[0][1]
    title = top_article.get("title", "No Title Available")
    url = top_article.get("url", "")
    description = top_article.get("description", "No Description Available")

    logging.info(f"Top article selected: {title}")

    # Summarize the article
    summary, url = summarize_news(openai_client, AZURE_DEPLOYMENT_NAME, title, url)
    if not summary:
        logging.error("Failed to summarize the article.")
        return None

    # Post to Twitter
    tweet_id = post_to_twitter(tweepy_client, summary, url)
    if tweet_id:
        logging.info(f"Successfully posted to Twitter. Tweet ID: {tweet_id}")
    else:
        logging.error("Failed to post to Twitter.")

    return top_article


def main():
    try:
        # Fetch news articles
        articles = fetch_news(TOPICS, DOMAINS, NEWS_API_KEY)
        if not articles:
            logging.warning("No articles fetched from NewsAPI.")
            return

        # Filter positive articles using OpenAI
        positive_articles = filter_positive_articles(articles, openai_client, AZURE_DEPLOYMENT_NAME)

        # Process the top article
        if positive_articles:
            process_top_article(positive_articles)
        else:
            logging.warning("No overwhelmingly positive and relevant articles found.")

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()



