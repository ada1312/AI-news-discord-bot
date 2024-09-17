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
import math
import random
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Download necessary NLTK data
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

# Load environment variables
load_dotenv()

# Get API keys from environment variables
NEWS_API_KEY = os.getenv('NEWS_API_KEY')
DISCORD_WEBHOOK_URL = "os.getenv('DISCORD_WEBHOOK_URL')"

# Specify the news sources and keywords we want
ALLOWED_SOURCES = ['Forbes', 'TechCrunch', 'Wired', 'MIT Technology Review', 'VentureBeat']
KEYWORDS = ['AI', 'artificial intelligence', 'machine learning', 'deep learning', 'neural networks', 'prompt engineering']

async def fetch_ai_news():
    seven_days_ago = (datetime.now() - timedelta(7)).strftime('%Y-%m-%d')
    
    url = f'https://newsapi.org/v2/everything?q=({" OR ".join(KEYWORDS)})&language=en&from={seven_days_ago}&sortBy=relevancy&apiKey={NEWS_API_KEY}'
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                if 'articles' in data:
                    filtered_articles = [
                        article for article in data['articles']
                        if article['source']['name'] in ALLOWED_SOURCES and
                        any(keyword.lower() in article['title'].lower() for keyword in KEYWORDS)
                    ]
                    return filtered_articles
                else:
                    logging.error(f"Unexpected API response structure: {data}")
                    return None
            else:
                logging.error(f"Error fetching news: {response.status}")
                logging.error(f"Response content: {await response.text()}")
                return None

def summarize_text(text, num_sentences=2):
    sentences = sent_tokenize(text)
    words = [word.lower() for sentence in sentences for word in sentence.split() if word.lower() not in stopwords.words('english')]
    freq_dist = FreqDist(words)
    sentence_scores = {sentence: sum(freq_dist[word.lower()] for word in sentence.split() if word.lower() not in stopwords.words('english')) for sentence in sentences}
    summary_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:num_sentences]
    summary = ' '.join(summary_sentences)
    return summary

def calculate_reading_time(content):
    clean_content = ''.join(char for char in content if char not in '<>')
    word_count = len(clean_content.split())
    reading_time_minutes = math.ceil(word_count / 200)
    
    if reading_time_minutes < 1:
        return "< 1 min"
    elif reading_time_minutes == 1:
        return "1 min"
    else:
        return f"{reading_time_minutes} mins"

def get_news_emoji(title):
    keywords = {
        "research": "🔬", "breakthrough": "💡", "robot": "🤖", "language": "🗣️",
        "vision": "👁️", "ethics": "🤔", "business": "💼", "health": "🏥",
        "data": "📊", "cloud": "☁️", "security": "🔒", "innovation": "🚀",
        "startup": "🌱", "investment": "💰", "education": "🎓", "future": "🔮"
    }
    for keyword, emoji in keywords.items():
        if keyword in title.lower():
            return emoji
    return "🧠"  # Default AI-related emoji

async def send_discord_message(articles):
    if not articles:
        return

    async with aiohttp.ClientSession() as session:
        webhook = discord.Webhook.from_url(DISCORD_WEBHOOK_URL, session=session)

        header_emoji = random.choice(["🤖", "🧠", "💡", "🚀", "🔬", "💻", "🌐", "📊"])
        main_embed = discord.Embed(
            title=f"{header_emoji} AI News Roundup {header_emoji}",
            description=f"📅 {datetime.now().strftime('%B %d, %Y')}\n\n🔥 **Top AI Stories:**",
            color=discord.Color.from_rgb(75, 0, 130),  # Deep purple color
            timestamp=datetime.utcnow()
        )
        main_embed.set_footer(text="Powered by NewsAPI | Updated daily", icon_url="https://newsapi.org/images/n-logo-border.png")

        await webhook.send(embed=main_embed)

        for index, article in enumerate(articles[:5], start=1):
            summary = summarize_text(article['content'])
            reading_time = calculate_reading_time(article['content'])
            news_emoji = get_news_emoji(article['title'])
            
            article_embed = discord.Embed(
                title=f"{news_emoji} {article['title']}",
                url=article['url'],
                description=f"{summary[:150]}...",
                color=discord.Color.from_rgb(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            )
            article_embed.add_field(name="Source", value=article['source']['name'], inline=True)
            article_embed.add_field(name="Reading Time", value=f"⏱️ {reading_time}", inline=True)
            
            if article.get('urlToImage'):
                article_embed.set_thumbnail(url=article['urlToImage'])

            await webhook.send(embed=article_embed)

        hashtags = "#AINews #ArtificialIntelligence #MachineLearning #TechInnovation"
        footer_embed = discord.Embed(
            description=f"{hashtags}\n\n💬 Want to discuss these stories? Join our AI community chat!\n🔔 Stay tuned for more AI updates!",
            color=discord.Color.from_rgb(75, 0, 130)
        )
        await webhook.send(embed=footer_embed)

async def main():
    if not NEWS_API_KEY or not DISCORD_WEBHOOK_URL:
        logging.error("Error: NEWS_API_KEY or DISCORD_WEBHOOK_URL is not set in the environment variables.")
        return

    news_articles = await fetch_ai_news()
    
    if news_articles:
        logging.info(f"Found {len(news_articles)} articles on AI from specified sources.")
        await send_discord_message(news_articles)
        logging.info("Message sent to Discord.")
    else:
        logging.warning("No news articles found or error occurred.")

if __name__ == "__main__":
    asyncio.run(main())