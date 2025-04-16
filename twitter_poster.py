from logger import logger  # Import the centralized logger
from typing import Optional, List

MAX_TWEET_LENGTH = 280
HASHTAGS = "#PositiveIndia #IndiaDevelopment #GoodNewsIndia"

def construct_first_tweet(summary: str, url: str) -> str:
    """
    Constructs the first tweet with hashtags and URL.
    Truncates the summary if it exceeds the character limit.
    """
    first_tweet_text = f"{summary}\n🔗 {url}\n{HASHTAGS}"
    if len(first_tweet_text) > MAX_TWEET_LENGTH:
        # Adjust truncation to account for hashtags and URL
        truncated_summary = summary[:MAX_TWEET_LENGTH - len(HASHTAGS) - len(url) - 5]
        truncated_summary = truncated_summary.rsplit(' ', 1)[0]  # Ensure truncation happens at a word boundary
        first_tweet_text = f"{truncated_summary}...\n🔗 {url}\n{HASHTAGS}"
    logger.debug(f"Constructed first tweet: {first_tweet_text}")
    return first_tweet_text

def split_summary_into_chunks(summary: str) -> List[str]:
    """
    Splits the remaining summary into chunks of 280 characters, ensuring no word is split.
    """
    chunks = []
    while summary:
        if len(summary) <= MAX_TWEET_LENGTH:
            chunks.append(summary)
            break
        else:
            chunk = summary[:MAX_TWEET_LENGTH]
            chunk = chunk.rsplit(' ', 1)[0]  # Ensure truncation happens at a word boundary
            chunks.append(chunk)
            summary = summary[len(chunk):].strip()
    logger.debug(f"Split summary into chunks: {chunks}")
    return chunks

def post_to_twitter(client, summary: str, url: str) -> Optional[int]:
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

    # Construct the first tweet
    first_tweet_text = construct_first_tweet(summary, url)
    logger.info(f"First tweet length: {len(first_tweet_text)}")

    # Post the first tweet
    try:
        tweet = client.create_tweet(text=first_tweet_text)
        tweet_id = tweet.data["id"]
        logger.info(f"First tweet posted successfully. Tweet ID: {tweet_id}")
    except Exception as e:
        logger.error(f"Error posting the first tweet: {e}")
        return None

    # Calculate the remaining summary
    # Exclude only the part of the summary that was included in the first tweet
    remaining_summary = summary[len(summary) - len(first_tweet_text) + len(url) + len(HASHTAGS) + 5:].strip()
    logger.debug(f"Remaining summary after first tweet: {remaining_summary}")

    # Post the remaining tweets as a thread
    if remaining_summary:
        chunks = split_summary_into_chunks(remaining_summary)
        logger.debug(f"Chunks to be posted in thread: {chunks}")
        for chunk in chunks:
            try:
                tweet = client.create_tweet(text=chunk, in_reply_to_tweet_id=tweet_id)
                tweet_id = tweet.data["id"]
                logger.info(f"Tweet posted successfully in thread. Tweet ID: {tweet_id}")
            except Exception as e:
                logger.error(f"Error posting a tweet in the thread: {e}")
                return None

    logger.info("Successfully posted the thread.")
    return tweet_id

