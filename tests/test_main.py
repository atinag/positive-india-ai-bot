import os
os.environ["NEWS_API_KEY"] = "mock-news-api-key"
os.environ["NEWSDATA_API_KEY"] = "mock-newsdata-api-key"
os.environ["OPENAI_API_KEY"] = "mock-openai-api-key"
os.environ["TWITTER_CONSUMER_KEY"] = "mock-twitter-consumer-key"
os.environ["TWITTER_CONSUMER_SECRET"] = "mock-twitter-consumer-secret"
os.environ["TWITTER_ACCESS_TOKEN"] = "mock-twitter-access-token"
os.environ["TWITTER_ACCESS_SECRET"] = "mock-twitter-access-secret"
os.environ["TWITTER_BEARER_TOKEN"] = "mock-twitter-bearer-token"
os.environ["AZURE_STORAGE_CONNECTION_STRING"] = "mock-azure-storage-connection-string"
os.environ["AZURE_OPENAI_ENDPOINT"] = "https://azureopenaipoistiveindiabotinstance.openai.azure.com/"

import unittest
from unittest.mock import patch, MagicMock
from main import main

@patch.dict("os.environ", {
    "NEWS_API_KEY": "mock-news-api-key",
    "NEWSDATA_API_KEY": "mock-newsdata-api-key",
    "OPENAI_API_KEY": "mock-openai-api-key",
    "TWITTER_CONSUMER_KEY": "mock-twitter-consumer-key",
    "TWITTER_CONSUMER_SECRET": "mock-twitter-consumer-secret",
    "TWITTER_ACCESS_TOKEN": "mock-twitter-access-token",
    "TWITTER_ACCESS_SECRET": "mock-twitter-access-secret",
    "TWITTER_BEARER_TOKEN": "mock-twitter-bearer-token",
    "AZURE_STORAGE_CONNECTION_STRING": "mock-azure-storage-connection-string"
})
class TestMain(unittest.TestCase):

    @patch("main.logger")
    @patch("main.initialize_posted_tweets")
    @patch("main.fetch_newsapi")
    @patch("main.fetch_newsdata")
    @patch("main.filter_positive_articles")
    @patch("main.is_duplicate")
    @patch("main.process_top_article")
    @patch("main.save_posted_tweet")
    def test_duplicate_article(self, mock_save_posted_tweet, mock_process_top_article, mock_is_duplicate, mock_filter_positive_articles, mock_fetch_newsdata, mock_fetch_newsapi, mock_initialize_posted_tweets, mock_logger):
        mock_fetch_newsapi.return_value = [{"title": "Sample Article"}]
        mock_fetch_newsdata.return_value = []
        mock_filter_positive_articles.return_value = [(0.9, {"title": "Sample Article"})]
        mock_is_duplicate.return_value = True
        main()
        mock_logger.warning.assert_any_call("Duplicate article detected: Sample Article. Trying next article.")
        mock_process_top_article.assert_not_called()
        mock_save_posted_tweet.assert_not_called()

    @patch("main.logger")
    @patch("main.initialize_posted_tweets")
    @patch("main.fetch_newsapi")
    @patch("main.fetch_newsdata")
    @patch("main.filter_positive_articles")
    @patch("main.is_duplicate")
    @patch("main.process_top_article")
    @patch("main.save_posted_tweet")
    def test_successful_processing(self, mock_save_posted_tweet, mock_process_top_article, mock_is_duplicate, mock_filter_positive_articles, mock_fetch_newsdata, mock_fetch_newsapi, mock_initialize_posted_tweets, mock_logger):
        mock_fetch_newsapi.return_value = [{"title": "Positive Article"}]
        mock_fetch_newsdata.return_value = []
        mock_filter_positive_articles.return_value = [(0.95, {"title": "Positive Article"})]
        mock_is_duplicate.return_value = False
        main()
        mock_process_top_article.assert_called_once()
        mock_save_posted_tweet.assert_called_once_with("Positive Article")
        mock_logger.debug.assert_any_call("Top article title: Positive Article")

    @patch("main.logger")
    @patch("main.initialize_posted_tweets")
    @patch("main.fetch_newsapi")
    @patch("main.fetch_newsdata")
    @patch("main.filter_positive_articles")
    def test_no_positive_articles(self, mock_filter_positive_articles, mock_fetch_newsdata, mock_fetch_newsapi, mock_initialize_posted_tweets, mock_logger):
        mock_fetch_newsapi.return_value = [{"title": "Neutral Article"}]
        mock_fetch_newsdata.return_value = []
        mock_filter_positive_articles.return_value = []
        main()
        mock_logger.warning.assert_any_call("No overwhelmingly positive and relevant articles found.")

    @patch("main.logger")
    @patch("main.initialize_posted_tweets")
    @patch("main.fetch_newsapi")
    @patch("main.fetch_newsdata")
    def test_fetch_news_exception(self, mock_fetch_newsdata, mock_fetch_newsapi, mock_initialize_posted_tweets, mock_logger):
        mock_fetch_newsapi.side_effect = Exception("Error fetching news")
        mock_fetch_newsdata.return_value = []
        main()
        mock_logger.error.assert_any_call("An unexpected error occurred: Error fetching news", exc_info=True)

    @patch("main.logger")
    @patch("main.initialize_posted_tweets")
    @patch("main.fetch_newsapi")
    @patch("main.fetch_newsdata")
    @patch("main.filter_positive_articles")
    @patch("main.is_duplicate")
    @patch("main.process_top_article")
    @patch("main.save_posted_tweet")
    def test_process_top_article_exception(self, mock_save_posted_tweet, mock_process_top_article, mock_is_duplicate, mock_filter_positive_articles, mock_fetch_newsdata, mock_fetch_newsapi, mock_initialize_posted_tweets, mock_logger):
        mock_fetch_newsapi.return_value = [{"title": "Positive Article"}]
        mock_fetch_newsdata.return_value = []
        mock_filter_positive_articles.return_value = [(0.95, {"title": "Positive Article"})]
        mock_is_duplicate.return_value = False
        mock_process_top_article.side_effect = Exception("Processing error")
        main()
        mock_logger.error.assert_any_call("Error during article processing: Processing error", exc_info=True)
        mock_save_posted_tweet.assert_not_called()

    @patch("main.logger")
    @patch("main.initialize_posted_tweets")
    @patch("main.fetch_newsapi")
    @patch("main.fetch_newsdata")
    @patch("main.filter_positive_articles")
    @patch("main.is_duplicate")
    @patch("main.process_top_article")
    @patch("main.save_posted_tweet")
    def test_save_posted_tweet_exception(self, mock_save_posted_tweet, mock_process_top_article, mock_is_duplicate, mock_filter_positive_articles, mock_fetch_newsdata, mock_fetch_newsapi, mock_initialize_posted_tweets, mock_logger):
        mock_fetch_newsapi.return_value = [{"title": "Positive Article"}]
        mock_fetch_newsdata.return_value = []
        mock_filter_positive_articles.return_value = [(0.95, {"title": "Positive Article"})]
        mock_is_duplicate.return_value = False
        mock_save_posted_tweet.side_effect = Exception("Save error")
        main()
        mock_logger.error.assert_any_call("Error saving posted tweet: Save error", exc_info=True)

if __name__ == "__main__":
    unittest.main()