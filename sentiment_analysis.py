from textblob import TextBlob

def analyze_sentiment_with_textblob_and_filter(text):

    growth_keywords = ["growth", "development",  "success", "boom", "investment", "expansion",
                            "milestone", "achievement", "launched", "innovation", "breakthrough"
                            ]

    sentiment = TextBlob(text).sentiment.polarity

    # Relevance scoring
    relevance_score = sum(1 for keyword in growth_keywords if keyword.lower() in text.lower())

    print(f"Article: {text}")
    print(f"Sentiment: {sentiment}")

    return sentiment,relevance_score





def analyze_sentiment_with_openai(client, text, model):
    prompt = (
        f"Analyze the following text and determine if it is overwhelmingly positive and relevant to the 'India growth story':\n\n"
        f"Text: {text}\n\n"
        f"Answer 'Yes' if it is overwhelmingly positive and relevant, otherwise answer 'No'."
    )
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that analyzes sentiment and relevance."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10
        )
        result = response.choices[0].message.content.strip()
        return result.lower() == "yes"
    except Exception as e:
        print(f"Error analyzing sentiment with OpenAI: {e}")
        return False