from config import NEWS_API_KEY, TOPICS, DOMAINS, SENTIMENT_THRESHOLD, RELEVANCE_THRESHOLD, AZURE_DEPLOYMENT_NAME
from clients import openai_client, tweepy_client
from news_fetcher import fetch_news
from workflow import filter_positive_articles, process_top_article
from logger import logger  # Import the centralized logger
from duplicate_checker import is_duplicate, save_posted_tweet
from blob_storage import initialize_posted_tweets

def main():
    try:
        # Ensure the posted_tweets.json file is initialized
        initialize_posted_tweets()

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
            top_article = positive_articles[0][1]  # Get the second element of the first tuple
            title = top_article.get("title", "No Title Available")  # Safely get the title

            logger.debug(f"Top article title: {title}")

            # Check for duplicates
            try:
                if is_duplicate(title):
                    logger.warning("Duplicate article detected. Skipping posting.")
                    return
            except Exception as e:
                logger.error(f"Error during duplicate check: {e}")

            # Process and post the article
            process_top_article(top_article, openai_client, tweepy_client, AZURE_DEPLOYMENT_NAME)

            # Save the posted article to avoid duplicates in the future
            save_posted_tweet(title)
        else:
            logger.warning("No overwhelmingly positive and relevant articles found.")

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")


if __name__ == "__main__": 
    main()



