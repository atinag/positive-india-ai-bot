def post_to_twitter(client, summary, url):

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
    tweet = client.create_tweet(text=first_tweet_text)
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
            tweet = client.create_tweet(text=part, in_reply_to_tweet_id=tweet_id)
            tweet_id = tweet.data["id"]

    return tweet_id

