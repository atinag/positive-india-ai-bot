# positive-india-ai-bot

An AI-powered bot that fetches, filters, summarizes, and posts **positive and inspiring news stories about India's growth** directly to X (formerly Twitter). Built as a hobby project to promote optimism and celebrate India's progress in tech, economy, infrastructure, policy, and beyond.

---

## 🌟 What It Does

1. **Fetches news** using NewsAPI about India based on curated keywords and topics.
2. **Analyzes each article** using OpenAI's GPT model to determine:
   - Sentiment (Is it overwhelmingly positive?)
   - Relevance (Does it align with India's growth story?)
3. **Performs semantic deduplication** to avoid reposting similar stories using OpenAI Embeddings.
4. **Summarizes the best article** in a tweet-friendly format.
5. **Auto-posts** it to X using Tweepy.
6. **Runs twice a day** via GitHub Actions.

---

## 🛠️ Tech Stack

- 📰 [NewsAPI](https://newsapi.org/) – for fetching the latest headlines
- 🧠 [OpenAI GPT-3.5 + Embeddings](https://platform.openai.com/) – for sentiment, relevance, summarization & deduplication
- 🐦 [Tweepy](https://docs.tweepy.org/) – for posting to X (Twitter)
- ⚙️ [GitHub Actions](https://github.com/features/actions) – for scheduled automation

---

## 📌 Features

- Modular architecture (`main.py`, `news_fetcher.py`, `sentiment_analysis.py`, etc.)
- Smart scoring of articles using both **sentiment** and **relevance**
- Avoids duplicate or near-duplicate posts using semantic similarity
- Summarizes articles into concise, tweet-ready messages
- Easily extensible for Telegram, email, or multilingual support

---

## 💡 Why I Built This

There's a lot of noise in the media today. While India is making tremendous strides across multiple domains, such positive developments are often buried. This bot aims to:
- Curate the good stuff
- Bring optimism to timelines
- Amplify India's success stories

---

## 📈 Future Enhancements

- Support for multi-tweet threads with richer context
- Integration with Telegram/WhatsApp alerts
- Regional language summaries
- Image generation for visual posts
- Public dashboard or newsletter

---

## 🤝 Contributing

This project is open for learning, tinkering, and collaborating. Feel free to fork, suggest features, or raise issues!

---

## 📣 Follow the Bot on X

📍 [@PositiveIndiaAI](https://x.com/PositiveIndiaAI)

---

## 📄 License

MIT License – free to use, adapt, and share.
