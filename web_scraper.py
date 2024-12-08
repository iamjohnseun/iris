import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse
import time
import random
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from urllib.robotparser import RobotFileParser
from config import Config
import psutil

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
    
    crawl_stats = {
        "pages_crawled": 0,
        "urls_visited": [],
        "skipped_urls": [],
        "errors": [],
        "memory_usage": [],
        "content_lengths": []
    }
    
    if not is_allowed_to_crawl(url):
        crawl_stats["errors"].append(f"Crawling not allowed for {url}")
        return {"content": "", "stats": crawl_stats}
    
    texts = []
    queue = [(url, 0)]
    hostname = urlparse(url).netloc
    session = create_session()
    pages_crawled = 0

    while queue and pages_crawled < max_pages:
        current_url, depth = queue.pop(0)
        normalized_url = normalize_url(current_url)
        
        # Check memory usage
        memory_usage = check_memory_usage()
        crawl_stats["memory_usage"].append(memory_usage)
        
        if memory_usage > 0.8:  # 80% threshold
            crawl_stats["errors"].append("Memory usage too high, stopping crawl")
            break
            
        if normalized_url in visited or depth > Config.SCRAPING_MAX_DEPTH:
            crawl_stats["skipped_urls"].append(current_url)
            continue
            
        visited.add(normalized_url)
        crawl_stats["urls_visited"].append(current_url)
        
        try:
            response = session.get(current_url, timeout=Config.REQUEST_TIMEOUT)
            response.raise_for_status()
            
            if not 'text/html' in response.headers.get('Content-Type', '').lower():
                crawl_stats["skipped_urls"].append(current_url)
                continue

            html_content = response.text
            crawl_stats["content_lengths"].append(len(html_content))
            
            page_text = parse_website_content(html_content)
            
            if page_text.strip():
                texts.append(page_text)
                pages_crawled += 1
                crawl_stats["pages_crawled"] = pages_crawled

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
            
            time.sleep(random.uniform(Config.SCRAPING_DELAY, Config.SCRAPING_DELAY_MAX))
                
        except requests.exceptions.RequestException as e:
            crawl_stats["errors"].append(f"Error crawling {current_url}: {str(e)}")
            continue
            
    return {
        "content": ' '.join(texts) if texts else "",
        "stats": crawl_stats
    }

def parse_website_content(html_content):
    soup = BeautifulSoup(html_content, 'lxml')
    
    for element in soup(['script', 'style', 'nav', 'footer', 'header']):
        element.decompose()
    
    text_chunks = []
    
    for tag in Config.CONTENT_TAGS:
        elements = soup.find_all(tag)
        for element in elements:
            text = element.get_text(strip=True)
            if text and len(text) > 20:
                text_chunks.append(text)
    
    return ' '.join(text_chunks)

# Example usage:
# url = 'https://example.com'
# all_text = fetch_website_content(url)
# print(all_text)