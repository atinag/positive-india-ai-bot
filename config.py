import os

# API Keys
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY")  # Add this line
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TWITTER_CONSUMER_KEY = os.getenv("TWITTER_CONSUMER_KEY")
TWITTER_CONSUMER_SECRET = os.getenv("TWITTER_CONSUMER_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

# Azure Blob Storage configuration
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER_NAME = "containerpositive-india-bot"
POSTED_TWEETS_FILE = "posted_tweets.json"  # Local file to store posted tweets
BLOB_NAME = "posted_tweets.json"  # Blob name in Azure Blob Storage

# OpenAI Configuration
AZURE_DEPLOYMENT_NAME = "gpt-35-turbo"

# Thresholds
SENTIMENT_THRESHOLD = 0.5
RELEVANCE_THRESHOLD = 0.5

# Topics and Domains
TOPICS = [
    "India growth story",
    "India economic growth",
    "India rising",
    "India development",
    "India innovation",
    "India startup",
    "India infrastructure",
    "India economy",
    "India science technology",
    "India renewable energy",
    "India manufacturing",
    "India healthcare",
    "India education reform",
    "India digital transformation",
    "India green energy",
    "India space exploration",
    "India clean tech",
    "India AI research"
]
DOMAINS = ",".join([
    "thehindu.com", "business-standard.com",
    "timesofindia.indiatimes.com", "hindustantimes.com", "ndtv.com",
    "indianexpress.com", "economictimes.indiatimes.com", "financialexpress.com",
    "yourstory.com", "indiatoday.in", "theprint.in", "scroll.in"
])
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Add any other config variables as needed