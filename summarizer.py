def summarize_news(client, model, title, url):
    
    
    
    prompt = f"Summarize this positive news headline about India:\n\n{title}\n\nSummary:"
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes positive news about India for social media."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100
        )
        summary = response.choices[0].message.content.strip()
        return summary, url
    except Exception as e:
        print(f"Error summarizing news with OpenAI: {e}")
        return None, url