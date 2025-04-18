from logger import logger  # Import the centralized logger
from typing import Optional, List

MAX_TWEET_LENGTH = 280
LINK_LENGTH = 23  # Twitter/X t.co shortener
HASHTAGS = "#PositiveIndiaAI"
EXTRA = len("\n🔗 \n")  # newline, emoji, and space

def post_thread_with_link(client, summary: str, url: str) -> Optional[int]:
    """
    Posts a summary and URL to Twitter as a thread if necessary.

    Args:
        client: Tweepy client instance.
        summary: The summary to post.
        url: The URL to include in the first tweet.

    Returns:
        The ID of the last tweet in the thread, or None if an error occurs.
    """
    logger.info("Posting to Twitter...")
    logger.info(f"Summary: {summary}")
    logger.info(f"URL: {url}")

    allowed_summary_length = MAX_TWEET_LENGTH - LINK_LENGTH - len(HASHTAGS) - EXTRA
    if len(summary) > allowed_summary_length:
        truncated_summary = summary[:allowed_summary_length - 3].rsplit(' ', 1)[0] + "..."
    else:
        truncated_summary = summary

    first_tweet_text = f"{truncated_summary}\n🔗 {url}\n{HASHTAGS}"
    logger.info(f"Length of first tweet: {len(first_tweet_text)}")

    # Post the first tweet
    try:
        tweet = client.create_tweet(text=first_tweet_text)
        tweet_id = tweet.data["id"]
        logger.info(f"First tweet posted successfully. Tweet ID: {tweet_id}")
    except Exception as e:
        logger.error(f"Error posting the first tweet: {e}")
        return None

    # Prepare the remaining summary for the thread
    remaining_summary = summary[len(truncated_summary):].strip()
    if remaining_summary:
        # Split the remaining summary into chunks of 280 characters, ensuring no word is split
        split_summary = []
        while remaining_summary:
            if len(remaining_summary) <= MAX_TWEET_LENGTH:
                split_summary.append(remaining_summary)
                break
            else:
                chunk = remaining_summary[:MAX_TWEET_LENGTH]
                chunk = chunk.rsplit(' ', 1)[0]  # Ensure truncation happens at a word boundary
                split_summary.append(chunk)
                remaining_summary = remaining_summary[len(chunk):].strip()

        logger.debug(f"Split summary into chunks: {split_summary}")

        # Post the remaining tweets
        for part in split_summary:
            try:
                tweet = client.create_tweet(text=part, in_reply_to_tweet_id=tweet_id)
                tweet_id = tweet.data["id"]
                logger.info(f"Tweet posted successfully in thread. Tweet ID: {tweet_id}")
            except Exception as e:
                logger.error(f"Error posting a tweet in the thread: {e}")
                return None

    logger.info("Successfully posted the thread.")
    return tweet_id

