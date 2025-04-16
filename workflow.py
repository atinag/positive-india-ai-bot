import logging
from typing import List, Dict, Tuple, Optional
from sentiment_analysis import analyze_sentiment_with_openai
from summarizer import summarize_news
from twitter_poster import post_to_twitter

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
            logging.info(f"Article selected: {title} (Score: {combined_score})")
        else:
            logging.info(f"Article rejected: {title} (Sentiment: {sentiment}, Relevance: {relevance})")

    # Sort articles by combined score in descending order
    positive_articles = sorted(positive_articles, key=lambda x: x[0], reverse=True)  # Sort by combined_score
    logging.debug(f"Positive Articles: {positive_articles}")
    return positive_articles


def process_top_article(positive_articles: List[Tuple[float, Dict]], openai_client, tweepy_client, model: str) -> Optional[Dict]:
    """
    Processes the top article by summarizing and posting it to Twitter.
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
    summary, url = summarize_news(openai_client, model, title, url)
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