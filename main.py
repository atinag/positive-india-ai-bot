import openai
import requests
import tweepy
import json
import os
from openai import AzureOpenAI


# Azure OpenAI configuration

client = AzureOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    api_version="2023-12-01-preview",
    azure_endpoint="https://azureopenaipoistiveindiabotinstance.openai.azure.com/",
)
AZURE_DEPLOYMENT_NAME = "gpt-35-turbo"  


# API Keys from GitHub Secrets
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# Twitter API credentials
consumer_key = os.getenv("TWITTER_CONSUMER_KEY")
consumer_secret = os.getenv("TWITTER_CONSUMER_SECRET")
access_token = os.getenv("TWITTER_ACCESS_TOKEN")
access_token_secret = os.getenv("TWITTER_ACCESS_SECRET")
twitter_bearer_token = os.getenv("TWITTER_BEARER_TOKEN")


# Set up tweepy client
tweepyclient = tweepy.Client(
    bearer_token=twitter_bearer_token,
    consumer_key = consumer_key, consumer_secret = consumer_secret,
    access_token=access_token, access_token_secret=access_token_secret)


# Function to fetch positive news about India
def get_positive_news():
    url = f"https://newsapi.org/v2/everything?q=india development&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    news = response.json()
    articles = news['articles'][:5]  # Get the top 5 articles
    headlines = "\n".join([article['title'] for article in articles])
    return headlines

# Function to summarize the news using OpenAI
def summarize_news(news):
    prompt = f"Summarize the following positive news about India:\n\n{news}\n\nSummary:"
    
    response = client.chat.completions.create(
        model=AZURE_DEPLOYMENT_NAME,  # This should be your deployment name
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes positive news about India for social media."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=500,
    )
    return response.choices[0].message.content.strip()



# Function to post the summary to Twitter
def post_to_twitter(summary):
   
    print(f"Summary is:\n{summary}")
    print(f"Type of summary: {type(summary)}")

    if len(summary) > 280:
        summary = summary[:277] + "..."
    # Now tweet
    response = tweepyclient.create_tweet(text=summary)


def post_thread(summary):
    # Split summary by newlines assuming each is a tweet-length paragraph
    tweets = summary.split('\n')
    hashtags = " \ud83c\uddee\ud83c\uddf3\u2728 #PositiveIndia #IndiaRising"
    tweet_ids = []
    reply_to_id = None

    for tweet in tweets:
        text = tweet.strip()
        if not text:
            continue
        text_with_tags = (text + hashtags) if len(text) + len(hashtags) < 280 else text
        response = client.create_tweet(text=text_with_tags, in_reply_to_tweet_id=reply_to_id)
        tweet_ids.append(response.data['id'])
        reply_to_id = response.data['id']

    return tweet_ids



# Main function
def main():
    positive_news = get_positive_news()
    summarized_news = summarize_news(positive_news)
    # post_to_twitter(summarized_news)
    post_thread(summarized_news)

if __name__ == "__main__":
    main()
