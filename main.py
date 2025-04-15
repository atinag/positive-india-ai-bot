import openai
import requests
import tweepy
import json
import os
from openai import AzureOpenAI


# Azure OpenAI configuration
# openai.api_type = "azure"
# openai.api_base = "https://azureopenaipoistiveindiabotinstance.openai.azure.com/"
# openai.api_version = "2024-12-01-preview"
# openai.api_key = os.getenv("OPENAI_API_KEY")


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

# Set up tweepy client
auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret, access_token, access_token_secret)
api = tweepy.API(auth)

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
    # response = openai.ChatCompletion.create(
    #     engine="gpt-35-turbo",
    #     messages=[
    #         {"role": "system", "content": "You are an assistant that summarizes positive news from India."},
    #         {"role": "user", "content": prompt}
    #     ],
    #     temperature=0.7,
    #     max_tokens=100,
    # )
    # return response["choices"][0]["message"]["content"].strip()
    response = client.chat.completions.create(
        model=AZURE_DEPLOYMENT_NAME,  # This should be your deployment name
        messages=[
            {"role": "system", "content": "You are an assistant that summarizes positive news from India."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=100,
    )
    return response.choices[0].message.content.strip()



# Function to post the summary to Twitter
def post_to_twitter(summary):
    api.update_status(summary)

# Main function
def main():
    positive_news = get_positive_news()
    summarized_news = summarize_news(positive_news)
    post_to_twitter(summarized_news)

if __name__ == "__main__":
    main()
