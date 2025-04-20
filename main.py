from config import NEWS_API_KEY, TOPICS, DOMAINS, SENTIMENT_THRESHOLD, RELEVANCE_THRESHOLD, AZURE_DEPLOYMENT_NAME
from clients import openai_client, tweepy_client
from news_fetcher import fetch_news
from workflow import filter_positive_articles, process_top_article
from logger import logger  # Import the centralized logger
from duplicate_checker import is_duplicate, save_posted_tweet
from blob_storage import initialize_posted_tweets
from twitter_poster import MAX_TWEET_LENGTH, LINK_LENGTH, HASHTAGS, EXTRA  # Add this import

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
            logger.info("Looking for the first non-duplicate positive article...")
            for _, article in positive_articles:
                title = article.get("title", "No Title Available")
                try:
                    if is_duplicate(title):
                        logger.warning(f"Duplicate article detected: {title}. Trying next article.")
                        continue
                except Exception as e:
                    logger.error(f"Error during duplicate check: {e}", exc_info=True)
                    continue

                logger.info(f"Processing article: {title}")
                logger.debug(f"Top article title: {title}")

                # Calculate allowed summary length for the tweet
                allowed_summary_length = MAX_TWEET_LENGTH - LINK_LENGTH - len(HASHTAGS) - EXTRA

                # Process and post the article
                try:
                    process_top_article(
                        article,
                        openai_client,
                        tweepy_client,
                        AZURE_DEPLOYMENT_NAME,
                        allowed_summary_length
                    )
                except Exception as e:
                    logger.error(f"Error during article processing: {e}", exc_info=True)
                    continue  # Try next article if processing fails

                # Save the posted article to avoid duplicates in the future
                try:
                    save_posted_tweet(title)
                except Exception as e:
                    logger.error(f"Error saving posted tweet: {e}", exc_info=True)
                break  # Stop after posting the first non-duplicate article
            else:
                logger.warning("No non-duplicate positive articles found.")
        else:
            logger.warning("No overwhelmingly positive and relevant articles found.")

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)


if __name__ == "__main__": 
    main()



