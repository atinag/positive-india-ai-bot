from config import NEWS_API_KEY, OPENAI_API_KEY, TOPICS, DOMAINS
from news_fetcher import fetch_news
from sentiment_analysis import analyze_sentiment_with_textblob_and_filter
from summarizer import summarize_news
from twitter_poster import post_to_twitter
from openai import AzureOpenAI
import tweepy
import os


# Azure OpenAI configuration
openai_client = AzureOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    api_version="2023-12-01-preview",
    azure_endpoint="https://azureopenaipoistiveindiabotinstance.openai.azure.com/",
)
AZURE_DEPLOYMENT_NAME = "gpt-35-turbo"  


# Twitter API credentials
consumer_key = os.getenv("TWITTER_CONSUMER_KEY")
consumer_secret = os.getenv("TWITTER_CONSUMER_SECRET")
access_token = os.getenv("TWITTER_ACCESS_TOKEN")
access_token_secret = os.getenv("TWITTER_ACCESS_SECRET")
twitter_bearer_token = os.getenv("TWITTER_BEARER_TOKEN")

# Set up tweepy client
tweepy_client = tweepy.Client(
    bearer_token=twitter_bearer_token,
    consumer_key = consumer_key, consumer_secret = consumer_secret,
    access_token=access_token, access_token_secret=access_token_secret)


def main():
    articles = fetch_news(TOPICS, DOMAINS, NEWS_API_KEY)
    positive_articles = []
    for article in articles:
        text = f"{article.get('title', '')} {article.get('description', '')}"
        sentiment,relevance_score = analyze_sentiment_with_textblob_and_filter(text)
        
        if sentiment > 0.1 and relevance_score > 0:  # Adjust threshold as needed
                positive_articles.append((sentiment+relevance_score, article))

    if not positive_articles:
        raise ValueError("No overwhelmingly positive articles found.")


    # Pick the highest sentiment article
    top_article = sorted(positive_articles, reverse=True)[0][1]
    title = top_article.get("title", "No Title Available")
    url = top_article.get("url", "")
    description = top_article.get("description", "No Description Available")

    summary, url = summarize_news(openai_client, "gpt-35-turbo", title, url)
    post_to_twitter(tweepy_client, summary, url)
    
if __name__ == "__main__":
    main()



