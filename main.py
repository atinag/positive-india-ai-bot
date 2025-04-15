import openai
import requests
import tweepy
import json
import os
from openai import AzureOpenAI
import random
from datetime import datetime, timedelta
from textblob import TextBlob




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

# List of enriched queries to focus on India's growth stories
topics = [
    "India economic growth",
    "India infrastructure development",
    "Indian startups",
    "Make in India success",
    "India exports",
    "India renewable energy",
    "Digital India initiative",
    "Indian innovation",
    "Indian space technology",
    "India manufacturing boom"
]

# Trusted domains
domains = ",".join([
    "thehindu.com", "livemint.com", "business-standard.com",
    "timesofindia.indiatimes.com", "hindustantimes.com", "ndtv.com",
    "indianexpress.com", "economictimes.indiatimes.com", "financialexpress.com",
    "yourstory.com", "inc42.com", "indiatoday.in", "theprint.in", "scroll.in",
    "downtoearth.org.in", "india.mongabay.com"
])


# Function to fetch positive news about India
def get_positive_news():
    
    query = " OR ".join(topics)
    
    print(f"Using query: {query}")

    # url = f"https://newsapi.org/v2/everything?q=india development&apiKey={NEWS_API_KEY}"

    url = (
        f"https://newsapi.org/v2/everything?"
        f"q={query}"
        f"&language=en"
        f"&sortBy=publishedAt"
        f"&from={(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')}"
        f"&apiKey={NEWS_API_KEY}"
    )

    print(f"NewsAPI Request URL: {url}")

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        news = response.json()
        articles = news.get("articles", [])
    
        if not articles:
            raise ValueError("No articles found for the given query.")
        

        # Apply sentiment analysis and filter
        positive_articles = []
        for article in articles:
            
            text = f"{article.get('title', '')} {article.get('description', '')}"
            
            sentiment = TextBlob(text).sentiment.polarity
            print(f"Article: {text}")
            print(f"Sentiment: {sentiment}")
            if sentiment > 0.3:  # Adjust threshold as needed
                positive_articles.append((sentiment, article))

        if not positive_articles:
            raise ValueError("No overwhelmingly positive articles found.")

        
        # Pick the highest sentiment article
        top_article = sorted(positive_articles, reverse=True)[0][1]
        title = top_article.get("title", "No Title Available")
        url = top_article.get("url", "")
        description = top_article.get("description", "No Description Available")
        
        print(f"Title: {title}")
        print(f"URL: {url}")
        print(f"Description: {description}")

        return title, url
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching news: {e}")
        return None, None
    
    except ValueError as e:
        print(f"Error: {e}")
        return None, None


# Function to summarize the news using OpenAI
def summarize_news(title,url):
    
    summaries = []
    prompt = f"Summarize this positive news headline about India:\n\n{title}\n\nSummary:"
    response = client.chat.completions.create(
            model=AZURE_DEPLOYMENT_NAME,  # This should be your deployment name
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes positive news about India for social media."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100
        )
    
    summary = response.choices[0].message.content.strip()
    return summary,url
    

# Function to post the summary to Twitter
def post_to_twitter(summary):
   
    print(f"Summary is:\n{summary}")
    print(f"Type of summary: {type(summary)}")

    if len(summary) > 280:
        summary = summary[:277] + "..."
    # Now tweet
    response = tweepyclient.create_tweet(text=summary)


def post_thread(summary):
    
    print(f"Summary is:\n{summary}")
    
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
        response = tweepyclient.create_tweet(text=text_with_tags, in_reply_to_tweet_id=reply_to_id)
        tweet_ids.append(response.data['id'])
        reply_to_id = response.data['id']

    return tweet_ids



def post_threadwithlink(summary,url):

    hashtags = "#PositiveIndia #IndiaDevelopment #GoodNewsIndia"

    print(f"Summary is:\n{summary}")
    print(f"URL is:\n{url}")

    # Add hashtags and URL only to the first tweet
    first_tweet_text = f"{summary}\n🔗 {url}\n{hashtags}"
    print(f"Length of first tweet is:\n{len(first_tweet_text)}")

    # Check if the first tweet exceeds Twitter's character limit
    if len(first_tweet_text) > 280:
        # Trim the summary to fit within the limit, ensuring no word is split
        truncated_summary = summary[:280 - len(hashtags) - len(url) - 5]
        truncated_summary = truncated_summary.rsplit(' ', 1)[0]  # Ensure truncation happens at a word boundary
        first_tweet_text = f"{truncated_summary}...\n🔗 {url}\n{hashtags}"
    else:
        truncated_summary = summary  # No truncation needed

    # Post the first tweet
    tweet = tweepyclient.create_tweet(text=first_tweet_text)
    tweet_id = tweet.data["id"]

    # Prepare the remaining summary for the thread
    remaining_summary = summary[len(truncated_summary):].strip()
    if remaining_summary:
        # Split the remaining summary into chunks of 280 characters, ensuring no word is split
        split_summary = []
        while remaining_summary:
            if len(remaining_summary) <= 280:
                split_summary.append(remaining_summary)
                break
            else:
                chunk = remaining_summary[:280]
                chunk = chunk.rsplit(' ', 1)[0]  # Ensure truncation happens at a word boundary
                split_summary.append(chunk)
                remaining_summary = remaining_summary[len(chunk):].strip()

        # Post the remaining tweets
        for part in split_summary:
            tweet = tweepyclient.create_tweet(text=part, in_reply_to_tweet_id=tweet_id)
            tweet_id = tweet.data["id"]

    return tweet_id


# Main function
def main():
    
    title,url = get_positive_news()
    summary,url = summarize_news(title,url)
    post_threadwithlink(summary,url)

if __name__ == "__main__":
    main()
