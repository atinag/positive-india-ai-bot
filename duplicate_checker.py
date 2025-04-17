import json
import os
from logger import logger
from sentence_transformers import SentenceTransformer, util
from blob_storage import download_blob, upload_blob
from config import POSTED_TWEETS_FILE, BLOB_NAME  # Import from config.py

SIMILARITY_THRESHOLD = 0.9  # Threshold for semantic similarity

# Load the semantic similarity model
model = SentenceTransformer('all-MiniLM-L6-v2')


def load_posted_tweets():
    """
    Loads the list of previously posted tweets from Azure Blob Storage.
    """
    try:
        # Download the blob to the local file
        download_blob(BLOB_NAME, POSTED_TWEETS_FILE)

        # Load the local file
        if os.path.exists(POSTED_TWEETS_FILE):
            with open(POSTED_TWEETS_FILE, "r") as file:
                try:
                    posted_tweets = json.load(file)  # Attempt to parse JSON
                    logger.info(f"Loaded posted tweets: {posted_tweets}")
                    return posted_tweets
                except json.JSONDecodeError:
                    logger.warning(f"File '{POSTED_TWEETS_FILE}' is empty or contains invalid JSON. Returning an empty list.")
                    return []  # Return an empty list if JSON is invalid
    except Exception as e:
        logger.error(f"Error loading posted tweets: {e}")

    return []  # Return an empty list if any error occurs


def save_posted_tweet(tweet_text):
    """
    Saves a new tweet to the list of posted tweets and uploads it to Azure Blob Storage.
    """
    try:
        # Load existing tweets
        posted_tweets = load_posted_tweets()

        # Add the new tweet
        posted_tweets.append(tweet_text)

        # Save to the local file
        with open(POSTED_TWEETS_FILE, "w") as file:
            json.dump(posted_tweets, file)

        # Upload the updated file to Azure Blob Storage
        upload_blob(POSTED_TWEETS_FILE, BLOB_NAME)
    except Exception as e:
        logger.error(f"Error saving posted tweet: {e}")


def is_duplicate(new_tweet):
    """
    Checks if a tweet is a duplicate based on exact match or semantic similarity.

    Args:
        new_tweet: The tweet text to check.

    Returns:
        True if the tweet is a duplicate, False otherwise.
    """
    posted_tweets = load_posted_tweets()

    # Exact match check
    if new_tweet in posted_tweets:
        logger.info("Tweet is an exact duplicate.")
        return True

    # Semantic similarity check
    if posted_tweets:
        embeddings1 = model.encode([new_tweet], convert_to_tensor=True)
        embeddings2 = model.encode(posted_tweets, convert_to_tensor=True)
        cosine_scores = util.cos_sim(embeddings1, embeddings2)

        if any(score > SIMILARITY_THRESHOLD for score in cosine_scores[0]):
            logger.info("Tweet is a semantic duplicate.")
            return True

    return False