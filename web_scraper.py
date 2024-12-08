import gc
import requests
import time
import random
import psutil
from urllib.parse import urljoin, urlparse, urlunparse
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from urllib.robotparser import RobotFileParser
from config import Config

def check_memory_usage():
    memory = psutil.virtual_memory()
    return memory.percent / 100.0

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

def should_crawl_url(url, hostname, visited):
    parsed = urlparse(url)
    return (
        parsed.scheme in ['http', 'https'] and
        parsed.netloc == hostname and
        not url.endswith(Config.SKIP_EXTENSIONS) and
        normalize_url(url) not in visited
    )
    
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

def fetch_website_content(url, visited=None, max_pages=Config.MAX_PAGES):
    if visited is None:
        visited = set()
    
    crawl_stats = {
        "pages_crawled": 0,
        "urls_visited": [],
        "skipped_urls": [],
        "errors": [],
        "start_time": time.time(),
        "end_time": None,
        "total_content_size": 0
    }
    
    if not is_allowed_to_crawl(url):
        crawl_stats["errors"].append(f"Crawling not allowed for {url}")
        return {"content": "", "stats": crawl_stats}
    
    texts = []
    queue = [(url, 0)]
    hostname = urlparse(url).netloc
    session = create_session()

    try:
        while queue and crawl_stats["pages_crawled"] < max_pages:
            current_url, depth = queue.pop(0)
            normalized_url = normalize_url(current_url)
            
            if normalized_url in visited or depth > Config.SCRAPING_MAX_DEPTH:
                crawl_stats["skipped_urls"].append({
                    "url": current_url,
                    "reason": "Already visited or max depth reached"
                })
                continue
                
            visited.add(normalized_url)
            crawl_stats["urls_visited"].append({
                "url": current_url,
                "depth": depth,
                "timestamp": time.time()
            })
            
            try:
                response = session.get(current_url, timeout=Config.REQUEST_TIMEOUT)
                response.raise_for_status()
                
                if not 'text/html' in response.headers.get('Content-Type', '').lower():
                    crawl_stats["skipped_urls"].append({
                        "url": current_url,
                        "reason": "Not HTML content"
                    })
                    continue

                html_content = response.text
                crawl_stats["total_content_size"] += len(html_content)
                
                page_text = parse_website_content(html_content)
                
                if page_text.strip():
                    texts.append(page_text)
                    crawl_stats["pages_crawled"] += 1

                if depth < Config.SCRAPING_MAX_DEPTH:
                    soup = BeautifulSoup(html_content, 'lxml')
                    for link in soup.find_all('a', href=True):
                        abs_link = urljoin(current_url, link['href'])
                        if should_crawl_url(abs_link, hostname, visited):
                            queue.append((abs_link, depth + 1))
                            
            except requests.exceptions.RequestException as e:
                crawl_stats["errors"].append({
                    "url": current_url,
                    "error": str(e),
                    "timestamp": time.time()
                })
                
    finally:
        session.close()
        crawl_stats["end_time"] = time.time()
        crawl_stats["duration"] = crawl_stats["end_time"] - crawl_stats["start_time"]
        gc.collect()
        
    return {
        "content": ' '.join(texts) if texts else "",
        "stats": crawl_stats
    }

def parse_website_content(html_content):
    soup = BeautifulSoup(html_content, 'lxml')
    
    # Remove unwanted elements
    for element in soup(['script', 'style', 'nav', 'footer', 'header', 'meta', 'input']):
        element.decompose()
    
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