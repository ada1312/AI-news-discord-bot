import requests
from bs4 import BeautifulSoup
import time
import logging
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BASE_URL = os.getenv('BASE_URL')
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

MAX_MESSAGE_LENGTH = 2000

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
    
    # Extract arXiv ID and generate links
    abstract_link = dt.find('a', {'title': 'Abstract'})
    if abstract_link:
        paper['id'] = abstract_link.text.strip().replace('arXiv:', '')
        paper['abstract_link'] = f"https://arxiv.org/abs/{paper['id']}"
        paper['pdf_link'] = f"https://arxiv.org/pdf/{paper['id']}.pdf"
        paper['html_link'] = f"https://arxiv.org/html/{paper['id']}v1"
        paper['other_formats_link'] = f"https://arxiv.org/format/{paper['id']}"
    
    # Extract title
    title_div = dd.find('div', {'class': 'list-title'})
    paper['title'] = title_div.text.replace('Title:', '').strip() if title_div else ''
    
    # Extract subjects
    subjects_div = dd.find('div', {'class': 'list-subjects'})
    paper['subjects'] = subjects_div.text.replace('Subjects:', '').strip() if subjects_div else ''
    
    return paper

def extract_papers(soup):
    papers = []
    if soup is None:
        return papers
    
    articles_dl = soup.find('dl')
    if not articles_dl:
        logging.error("Could not find the articles section")
        return papers

    current_date = ""
    for element in articles_dl.children:
        if element.name == 'h3':
            current_date = element.text.split('(')[0].strip()
            logging.info(f"Processing papers for date: {current_date}")
        elif element.name == 'dt':
            dd = element.find_next_sibling('dd')
            if dd:
                paper = extract_paper_info(element, dd)
                paper['date'] = current_date
                papers.append(paper)
    
    return papers

def get_next_page_link(soup):
    paging_div = soup.find('div', class_='pagination')
    if paging_div:
        next_link = paging_div.find('a', class_='pagination-next')
        if next_link:
            return f"https://arxiv.org{next_link['href']}"
    return None

def format_paper_info(paper):
    links = (
        f"[abstract](<{paper['abstract_link']}>) | "
        f"[pdf](<{paper['pdf_link']}>) | "
        f"[html](<{paper['html_link']}>) | "
        f"[other](<{paper['other_formats_link']}>)"
    )
    return (
        f"📄 **{paper['title']}**\n"
        f"🆔 `{paper['id']}`\n"
        f"🔗 {links}\n"
        f"📚 {paper['subjects']}\n\n"
    )

def send_discord_webhook(papers):
    header = f"# New ArXiv AI Research Papers\n*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
    current_message = header

    for paper in papers:
        paper_info = format_paper_info(paper)
        if len(current_message) + len(paper_info) > MAX_MESSAGE_LENGTH:
            # Send the current message before it exceeds the limit
            send_chunk(current_message)
            current_message = paper_info
        else:
            current_message += paper_info

    # Send any remaining message
    if current_message:
        send_chunk(current_message)

def send_chunk(chunk):
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json={"content": chunk})
        response.raise_for_status()
        logging.info(f"Successfully sent message chunk. Character count: {len(chunk)}")
    except requests.RequestException as e:
        logging.error(f"Error sending Discord webhook: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logging.error(f"Response status code: {e.response.status_code}")
            logging.error(f"Response content: {e.response.text}")
    
    time.sleep(2)  # To avoid hitting Discord rate limits

def scrape_and_send():
    url = f"{BASE_URL}?show=2000"  # Start with showing 2000 results
    all_papers = []
    
    while url:
        logging.info(f"Fetching page: {url}")
        soup = get_arxiv_data(url)
        if soup is None:
            break
        
        papers = extract_papers(soup)
        all_papers.extend(papers)
        logging.info(f"Extracted {len(papers)} papers from current page")
        
        url = get_next_page_link(soup)
        if url:
            time.sleep(3)  # Be nice to the server

    send_discord_webhook(all_papers)
    logging.info(f"Scraped and sent {len(all_papers)} papers in total")

if __name__ == "__main__":
    scrape_and_send()
    