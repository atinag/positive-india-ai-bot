from logger import logger  # Import the centralized logger
from typing import Optional, List
import re

MAX_TWEET_LENGTH = 280
LINK_LENGTH = 23  # Twitter/X t.co shortener
HASHTAGS = "#PositiveIndiaAI"
EXTRA = len("\n🔗 \n")  # newline, emoji, and space

def split_text_without_splitting_words_or_hashtags(text, max_length):
    """
    Splits text into a chunk of max_length, ensuring no word or hashtag is split.
    Returns (chunk, rest).
    """
    if len(text) <= max_length:
        return text, ""
    # Find the last space before max_length
    chunk = text[:max_length]
    last_space = chunk.rfind(' ')
    if (last_space == -1):
        # No space found, force split (rare case)
        return chunk, text[max_length:].lstrip()
    # Ensure we don't split a hashtag
    if '#' in chunk[last_space:]:
        # Find previous space before the hashtag
        prev_space = chunk[:last_space].rfind(' ')
        if prev_space != -1:
            last_space = prev_space
    chunk = chunk[:last_space]
    rest = text[last_space:].lstrip()
    return chunk, rest

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

    # Split the summary for the first tweet
    first_chunk, remaining_summary = split_text_without_splitting_words_or_hashtags(summary, allowed_summary_length)
    first_tweet_text = f"{first_chunk}\n{HASHTAGS}\n🔗 {url}"
    logger.info(f"Length of first tweet: {len(first_tweet_text)}")

    # Post the first tweet
    try:
        tweet = client.create_tweet(text=first_tweet_text)
        tweet_id = tweet.data["id"]
        logger.info(f"First tweet posted successfully. Tweet ID: {tweet_id}")
    except Exception as e:
        logger.error(f"Error posting the first tweet: {e}")
        return None

    # Post the remaining summary in thread, chunked by MAX_TWEET_LENGTH, no word/hashtag split
    while remaining_summary:
        # Reserve space for hashtags in each thread tweet
        allowed_length = MAX_TWEET_LENGTH - len(HASHTAGS) - 1  # 1 for newline
        chunk, remaining_summary = split_text_without_splitting_words_or_hashtags(remaining_summary, allowed_length)
        thread_tweet_text = f"{chunk}\n{HASHTAGS}"
        try:
            tweet = client.create_tweet(text=thread_tweet_text, in_reply_to_tweet_id=tweet_id)
            tweet_id = tweet.data["id"]
            logger.info(f"Tweet posted successfully in thread. Tweet ID: {tweet_id}")
        except Exception as e:
            logger.error(f"Error posting a tweet in the thread: {e}")
            return None

    logger.info("Successfully posted the thread.")
    return tweet_id

