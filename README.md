# ArXiv and Engineering News Discord Bot

This Discord bot combines two main features:
1. Fetching and posting the latest ArXiv AI research papers
2. Fetching and posting the latest news articles related to data engineering, prompt engineering, and AI

## Features

### ArXiv Bot
- Scrapes the latest AI research papers from ArXiv
- Formats paper information with clickable links
- Sends paper information to a Discord channel using a webhook
- Ensures complete article information in each message chunk

### Engineering News Bot
- Fetches news articles from NewsAPI
- Filters articles by specified sources (Forbes, TechRadar, WebProNews)
- Sends the latest 5 articles to a Discord channel using a webhook
- Runs asynchronously for improved performance

## Prerequisites

- Python 3.11+
- A NewsAPI key (get one at [https://newsapi.org/](https://newsapi.org/))
- A Discord webhook URL

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/your-username/arxiv-engineering-news-discord-bot.git
   cd arxiv-engineering-news-discord-bot
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root and add your API keys:
   ```
   BASE_URL=https://arxiv.org/list/cs.AI/recent
   DISCORD_WEBHOOK_URL=your_discord_webhook_url_here
   NEWS_API_KEY=your_newsapi_key_here
   ```

## Usage

Run the script with:

```
python main.py
```

The script will:
1. Fetch the latest ArXiv AI research papers, format them, and send them to the specified Discord channel.
2. Fetch the latest engineering news articles, print them to the console, and send them to the specified Discord channel.

## Customization

### ArXiv Bot
- To change the number of results fetched, modify the `url` variable in the `scrape_and_send` function.
- To adjust the formatting of paper information, modify the `format_paper_info` function.

### Engineering News Bot
- To change the news sources, modify the `ALLOWED_SOURCES` list in the script.
- To adjust the time range for fetching news, modify the `seven_days_ago` variable in the `fetch_engineering_news` function.
- To change the number of articles sent to Discord, modify the slice in the `send_discord_message` function (`articles[:5]`).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [ArXiv](https://arxiv.org/) for providing access to research papers
- [NewsAPI](https://newsapi.org/) for providing the news data
- [Discord](https://discord.com/) for the webhook functionality