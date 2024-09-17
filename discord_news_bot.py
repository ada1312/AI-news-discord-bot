import requests
from bs4 import BeautifulSoup
import time
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BASE_URL = os.getenv('BASE_URL')
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

def get_arxiv_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except requests.RequestException as e:
        logging.error(f"Error fetching URL {url}: {e}")
        return None

def extract_paper_info(dt, dd):
    paper = {}
    
    # Extract arXiv ID and links
    abstract_link = dt.find('a', {'title': 'Abstract'})
    if abstract_link:
        paper['id'] = abstract_link.text.strip()
        paper['abstract_link'] = f"https://arxiv.org{abstract_link['href']}"
    
    pdf_link = dt.find('a', {'title': 'Download PDF'})
    paper['pdf_link'] = f"https://arxiv.org{pdf_link['href']}" if pdf_link else ''
    
    # Extract title and authors
    title_div = dd.find('div', {'class': 'list-title'})
    paper['title'] = title_div.text.replace('Title:', '').strip() if title_div else ''
    
    authors_div = dd.find('div', {'class': 'list-authors'})
    paper['authors'] = authors_div.text.replace('Authors:', '').strip() if authors_div else ''
    
    return paper

def extract_papers(soup):
    papers = []
    if soup is None:
        return papers
    
    articles_dl = soup.find('dl', id='articles')
    if not articles_dl:
        logging.error("Could not find the articles section")
        return papers

    for element in articles_dl.children:
        if element.name == 'dt':
            dd = element.find_next_sibling('dd')
            if dd:
                paper = extract_paper_info(element, dd)
                papers.append(paper)
    
    return papers

def get_next_page_link(soup):
    paging_div = soup.find('div', class_='paging')
    if paging_div:
        next_link = paging_div.find('a', string='next')
        if next_link:
            return f"https://arxiv.org{next_link['href']}"
    return None

def send_discord_webhook(paper):
    message = {
        "content": "**New Research Paper**",
        "embeds": [{
            "title": paper['title'],
            "description": f"Authors: {paper['authors']}",
            "url": paper['abstract_link'],
            "color": 5814783,  # A nice blue color
            "fields": [
                {
                    "name": "Abstract",
                    "value": f"[View Abstract]({paper['abstract_link']})"
                },
                {
                    "name": "PDF",
                    "value": f"[Download PDF]({paper['pdf_link']})"
                }
            ]
        }]
    }
    
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=message)
        response.raise_for_status()
        logging.info(f"Successfully sent message for paper: {paper['title']}")
    except requests.RequestException as e:
        logging.error(f"Error sending Discord webhook: {e}")

def scrape_and_send():
    url = f"{BASE_URL}?show=100"  # Start with showing 100 results
    
    while url:
        logging.info(f"Fetching page: {url}")
        soup = get_arxiv_data(url)
        if soup is None:
            break
        
        papers = extract_papers(soup)
        for paper in papers:
            send_discord_webhook(paper)
            time.sleep(1)  # To avoid hitting Discord rate limits
        
        url = get_next_page_link(soup)
        if url:
            time.sleep(3)  # Be nice to the arXiv server

    logging.info("Finished scraping and sending papers")

if __name__ == "__main__":
    scrape_and_send()