import openai
import tweepy
from config import OPENAI_API_KEY, AZURE_DEPLOYMENT_NAME, TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET, TWITTER_BEARER_TOKEN

def get_openai_client():
    openai.api_type = "azure"
    openai.api_base = "https://azureopenaipoistiveindiabotinstance.openai.azure.com/"
    openai.api_version = "2023-12-01-preview"
    openai.api_key = OPENAI_API_KEY
    return openai

# Use this function to get the client instead of directly initializing it
openai_client = get_openai_client()

# Initialize Tweepy client
tweepy_client = tweepy.Client(
    bearer_token=TWITTER_BEARER_TOKEN,
    consumer_key=TWITTER_CONSUMER_KEY,
    consumer_secret=TWITTER_CONSUMER_SECRET,
    access_token=TWITTER_ACCESS_TOKEN,
    access_token_secret=TWITTER_ACCESS_SECRET,
)