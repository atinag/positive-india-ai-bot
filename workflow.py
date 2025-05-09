from logger import logger  # Import the centralized logger
from typing import List, Dict, Tuple, Optional
from sentiment_analysis import analyze_sentiment_with_openai
from summarizer import summarize_news
from twitter_poster import post_thread_with_link

def filter_positive_articles(articles: List[Dict], client, model: str, sentiment_threshold: float, relevance_threshold: float) -> List[Tuple[float, Dict]]:
    """
    Filters articles based on OpenAI sentiment and relevance analysis.
    """
    positive_articles = []
    for article in articles:
        title = article.get("title", "")
        description = article.get("description", "")
        text = f"{title} {description}"

        # Use OpenAI to analyze sentiment and relevance
        sentiment, relevance = analyze_sentiment_with_openai(client, text, model)

        # Only include articles that meet the thresholds
        if sentiment > sentiment_threshold and relevance > relevance_threshold:
            combined_score = (sentiment + relevance) / 2  # Equal weights
            positive_articles.append((combined_score, article))  # Ensure tuple is appended
            logger.info(f"Article selected: {title} (Score: {combined_score})")
        else:
            logger.info(f"Article rejected: {title} (Sentiment: {sentiment}, Relevance: {relevance})")

    # Sort articles by combined score in descending order
    positive_articles = sorted(positive_articles, key=lambda x: x[0], reverse=True)  # Sort by combined_score
    logger.debug(f"Positive Articles: {positive_articles}")
    return positive_articles


def process_top_article(
    article,
    openai_client,
    tweepy_client,
    deployment_name,
    allowed_summary_length  # Add this parameter
):
    """
    Processes a single article by summarizing and posting it to Twitter.
    """
    try:
        title = article.get("title", "No Title Available")
        description = article.get("description", "No Description Available")
        url = article.get("url", "")

        logger.info(f"Top article selected: {title}")

        # Summarize the article
        summary, url = summarize_news(
            openai_client,
            deployment_name,
            title,
            description,
            url,
            allowed_summary_length  # Pass it here
        )
        if not summary:
            logger.error("Failed to summarize the article.")
            return None

        # Post to Twitter
        tweet_id = post_thread_with_link(tweepy_client, summary, url)
        if tweet_id:
            logger.info(f"Successfully posted to Twitter. Tweet ID: {tweet_id}")
        else:
            logger.error("Failed to post to Twitter.")

        return article
    except KeyError as e:
        logger.error(f"KeyError while processing the article: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error while processing the article: {e}", exc_info=True)
        return None