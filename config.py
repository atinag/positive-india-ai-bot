import os

# API Keys
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TWITTER_CONSUMER_KEY = os.getenv("TWITTER_CONSUMER_KEY")
TWITTER_CONSUMER_SECRET = os.getenv("TWITTER_CONSUMER_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

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
    "India development"
]
DOMAINS = ",".join([
    "thehindu.com", "livemint.com", "business-standard.com",
    "timesofindia.indiatimes.com", "hindustantimes.com", "ndtv.com",
    "indianexpress.com", "economictimes.indiatimes.com", "financialexpress.com",
    "yourstory.com", "indiatoday.in", "theprint.in", "scroll.in"
])