import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse
import time
import random
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from urllib.robotparser import RobotFileParser
from config import Config

def normalize_url(url):
    parsed = urlparse(url)
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))

def is_allowed_to_crawl(url):
    rp = RobotFileParser()
    rp.set_url(urljoin(url, '/robots.txt'))
    try:
        rp.read()
        return rp.can_fetch(Config.USER_AGENT, url)
    except:
        return True

def create_session():
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    session.headers.update({'User-Agent': Config.USER_AGENT})
    return session

def fetch_website_content(url, visited=None, max_pages=50):
    if visited is None:
        visited = set()
    
    if not is_allowed_to_crawl(url):
        return ""
    
    texts = []
    queue = [(url, 0)]
    hostname = urlparse(url).netloc
    session = create_session()
    pages_crawled = 0

    while queue and pages_crawled < max_pages:
        current_url, depth = queue.pop(0)
        normalized_url = normalize_url(current_url)
        
        if normalized_url in visited or depth > Config.SCRAPING_MAX_DEPTH:
            continue
            
        visited.add(normalized_url)
        
        try:
            response = session.get(current_url, timeout=Config.REQUEST_TIMEOUT)
            response.raise_for_status()
            
            if not 'text/html' in response.headers.get('Content-Type', '').lower():
                continue

            html_content = response.text
            page_text = parse_website_content(html_content)
            
            if page_text.strip():
                texts.append(page_text)
                pages_crawled += 1

            if depth < Config.SCRAPING_MAX_DEPTH:
                soup = BeautifulSoup(html_content, 'lxml')
                for link in soup.find_all('a', href=True):
                    abs_link = urljoin(current_url, link['href'])
                    parsed_link = urlparse(abs_link)
                    
                    if (parsed_link.scheme in ['http', 'https'] and
                        parsed_link.netloc == hostname and
                        not abs_link.endswith(Config.SKIP_EXTENSIONS) and
                        normalize_url(abs_link) not in visited):
                        queue.append((abs_link, depth + 1))
            
            # Random delay between requests
            # time.sleep(random.uniform(Config.SCRAPING_DELAY, Config.SCRAPING_DELAY_MAX))
                
        except requests.exceptions.RequestException:
            continue
            
    return ' '.join(texts) if texts else ""

def parse_website_content(html_content):
    soup = BeautifulSoup(html_content, 'lxml')
    
    # Remove unwanted elements
    for element in soup(['script', 'style', 'nav', 'footer', 'header']):
        element.decompose()
    
    # Extract text from configured content tags
    text_chunks = []
    
    for tag in Config.CONTENT_TAGS:
        elements = soup.find_all(tag)
        for element in elements:
            text = element.get_text(strip=True)
            if text and len(text) > 20:  # Filter out very short texts
                text_chunks.append(text)
    
    return ' '.join(text_chunks)


# Example usage:
# url = 'https://example.com'
# all_text = fetch_website_content(url)
# print(all_text)