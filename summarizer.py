from logger import logger  # Import the centralized logger
import openai
import time
from typing import Optional, Tuple

def summarize_news(client, model: str, title: str, url: str, retries: int = 3, prompt_template: str = None) -> Tuple[Optional[str], str]:
    """
    Summarizes a news article using OpenAI's API.

    Args:
        client: OpenAI client instance.
        model: The OpenAI model to use (e.g., "gpt-35-turbo").
        title: The title of the news article.
        url: The URL of the news article.
        retries: Number of retries in case of API failure.
        prompt_template: Optional custom prompt template.

    Returns:
        A tuple containing the summary (or None if failed) and the URL.
    """
    if not prompt_template:
        prompt_template = "Summarize this positive news headline about India:\n\n{title}\n\nSummary:"
    prompt = prompt_template.format(title=title)

    for attempt in range(retries):
        try:
            logger.info(f"Summarizing news for title: {title}")
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes positive news about India for social media."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100
            )
            summary = response.choices[0].message.content.strip()
            logger.info(f"Generated summary: {summary}")
            return summary, url
        except openai.error.OpenAIError as e:
            logger.error(f"OpenAI API error on attempt {attempt + 1}: {e}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                return None, url
        except Exception as e:
            logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
            else:
                return None, url