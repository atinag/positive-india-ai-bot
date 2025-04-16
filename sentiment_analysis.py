import logging
from textblob import TextBlob
from typing import Tuple

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def analyze_sentiment_with_textblob_and_filter(text):
    """
    Analyzes sentiment using TextBlob and calculates relevance based on keywords.

    Args:
        text: The text to analyze.

    Returns:
        A tuple containing the sentiment score and relevance score.
    """
    growth_keywords = [
        "growth", "development", "success", "boom", "investment", "expansion",
        "milestone", "achievement", "launched", "innovation", "breakthrough"
    ]

    sentiment = TextBlob(text).sentiment.polarity

    # Relevance scoring
    relevance_score = sum(1 for keyword in growth_keywords if keyword.lower() in text.lower())

    logging.info(f"Text: {text}")
    logging.info(f"Sentiment: {sentiment}, Relevance: {relevance_score}")

    return sentiment, relevance_score


def analyze_sentiment_with_openai(client, text: str, model: str) -> Tuple[float, float]:
    """
    Analyzes sentiment and relevance using OpenAI.

    Args:
        client: OpenAI client instance.
        text: The text to analyze.
        model: The OpenAI model to use (e.g., "gpt-35-turbo").

    Returns:
        A tuple containing the normalized sentiment score (float, 0 to 1) 
        and the normalized relevance score (float, 0 to 1).
    """
    prompt = (
        f"Analyze the following text and provide a sentiment score (between -1 and 1) "
        f"and a relevance score (integer between 0 and 10) indicating how closely this article aligns with the 'India growth story'):\n\n"
        f"Text: {text}\n\n"
        f"Respond in the format: Sentiment: <score>, Relevance: <score>"
    )
    try:
        logging.info("Sending text to OpenAI for sentiment and relevance analysis...")
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that analyzes sentiment and relevance."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=50
        )
        result = response.choices[0].message.content.strip()
        logging.info(f"OpenAI Analysis Result: {result}")

        # Parse the result
        sentiment_str, relevance_str = result.replace("Sentiment:", "").replace("Relevance:", "").split(",")
        sentiment = float(sentiment_str.strip())
        relevance = int(relevance_str.strip())

        # Normalize sentiment (-1 to 1 -> 0 to 1)
        normalized_sentiment = (sentiment + 1) / 2
        # Normalize relevance (0 to 10 -> 0 to 1)
        normalized_relevance = relevance / 10

        # Log normalized scores
        logging.info(f"Normalized Sentiment: {normalized_sentiment}, Normalized Relevance: {normalized_relevance}")

        return normalized_sentiment, normalized_relevance
    except Exception as e:
        logging.error(f"Error analyzing sentiment with OpenAI: {e}")
        return 0.0, 0.0  # Default to neutral sentiment and no relevance