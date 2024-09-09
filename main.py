import os
import aiohttp
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv
import discord
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
import nltk

# Download necessary NLTK data
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

# Load environment variables
load_dotenv()

# Get API keys from environment variables
NEWS_API_KEY = os.getenv('NEWS_API_KEY')
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

# Specify the news sources we want
ALLOWED_SOURCES = ['Forbes', 'TechRadar', 'WebProNews']

async def fetch_engineering_news():
    seven_days_ago = (datetime.now() - timedelta(7)).strftime('%Y-%m-%d')
    
    url = f'https://newsapi.org/v2/everything?q=("AI" OR "artificial intelligence" OR "prompt engineering")&language=en&from={seven_days_ago}&sortBy=publishedAt&apiKey={NEWS_API_KEY}'
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                if 'articles' in data:
                    filtered_articles = [
                        article for article in data['articles']
                        if article['source']['name'] in ALLOWED_SOURCES
                    ]
                    return filtered_articles
                else:
                    print(f"Unexpected API response structure: {data}")
                    return None
            else:
                print(f"Error fetching news: {response.status}")
                print(f"Response content: {await response.text()}")
                return None

def summarize_text(text, num_sentences=3):
    sentences = sent_tokenize(text)
    words = [word.lower() for sentence in sentences for word in sentence.split() if word.lower() not in stopwords.words('english')]
    freq_dist = FreqDist(words)
    sentence_scores = {sentence: sum(freq_dist[word.lower()] for word in sentence.split() if word.lower() not in stopwords.words('english')) for sentence in sentences}
    summary_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:num_sentences]
    summary = ' '.join(summary_sentences)
    return summary

def print_articles(articles):
    if not articles:
        print("No articles found from the specified sources on AI or prompt engineering.")
        return

    for article in articles:
        print(f"\n--- Article from {article['source']['name']} ---")
        print(f"Title: {article['title']}")
        print(f"Description: {article['description']}")
        print(f"Summary: {summarize_text(article['content'])}")
        print(f"URL: {article['url']}")
        print(f"Published at: {article['publishedAt']}")
        print("-" * 50)

async def send_discord_message(articles):
    if not articles:
        return

    embed = discord.Embed(
        title="Latest AI and Prompt Engineering News",
        color=discord.Color.blue(),
        timestamp=datetime.utcnow()
    )

    for article in articles[:5]:  # Limit to 5 articles to avoid exceeding Discord's embed limits
        summary = summarize_text(article['content'])
        embed.add_field(
            name=f"{article['source']['name']}: {article['title']}",
            value=f"Summary: {summary[:200]}... [Read more]({article['url']})",
            inline=False
        )

    embed.set_footer(text="Powered by NewsAPI")

    async with aiohttp.ClientSession() as session:
        webhook = discord.Webhook.from_url(DISCORD_WEBHOOK_URL, session=session)
        await webhook.send(embed=embed)

async def main():
    if not NEWS_API_KEY or not DISCORD_WEBHOOK_URL:
        print("Error: NEWS_API_KEY or DISCORD_WEBHOOK_URL is not set in the environment variables.")
        return

    news_articles = await fetch_engineering_news()
    
    if news_articles:
        print(f"Found {len(news_articles)} articles on AI or prompt engineering from specified sources:")
        print_articles(news_articles)
        await send_discord_message(news_articles)
        print("Message sent to Discord.")
    else:
        print("No news articles found or error occurred.")

if __name__ == "__main__":
    asyncio.run(main())