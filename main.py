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
    article = news['articles'][0]  # Get only top article
    title = article['title']
    url = article['url']
    return title, url

    # headlines_with_links = []
    # for article in articles:
    #     title = article['title']
    #     link = article['url']
    #     headlines_with_links.append(f"{title}\n{link}")
   
    # return headlines_with_links
    # headlines = "\n".join([article['title'] for article in articles])
    # return headlines

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
    
    
    # prompt = f"Summarize the following positive news about India:\n\n{news}\n\nSummary:"
    
    # response = client.chat.completions.create(
    #     model=AZURE_DEPLOYMENT_NAME,  # This should be your deployment name
    #     messages=[
    #         {"role": "system", "content": "You are a helpful assistant that summarizes positive news about India for social media."},
    #         {"role": "user", "content": prompt}
    #     ],
    #     temperature=0.7,
    #     max_tokens=500,
    # )
    # return response.choices[0].message.content.strip()



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

    #summarized_news = summarize_news(positive_news)
    # combined_text = "\n\n".join(positive_news_items)
    summary,url = summarize_news(title,url)

    # post_to_twitter(summarized_news)
    # post_thread(summarized_news)
    post_threadwithlink(summary,url)

if __name__ == "__main__":
    main()
