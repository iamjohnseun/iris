import gc
import requests
import time
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

def is_allowed_to_crawl(url, rp):
    try:
        return rp.can_fetch("*", url)
    except:
        return False

def should_crawl_url(url, base_domain):
    parsed = urlparse(url)
    return (
        parsed.netloc == base_domain and
        not any(ext in parsed.path.lower() for ext in Config.EXCLUDED_EXTENSIONS) and
        not any(pattern in url.lower() for pattern in Config.EXCLUDED_PATTERNS)
    )

def create_session():
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    session.headers.update({
        'User-Agent': Config.USER_AGENT,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    })
    return session

def get_urls_to_process(base_url, single_page=False):
    session = create_session()
    urls = {normalize_url(base_url)}
    
    if single_page:
        return list(urls)
        
    try:
        response = session.get(base_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        base_domain = urlparse(base_url).netloc
        
        for link in soup.find_all('a'):
            href = link.get('href')
            if href:
                full_url = urljoin(base_url, href)
                normalized_url = normalize_url(full_url)
                if urlparse(normalized_url).netloc == base_domain:
                    urls.add(normalized_url)
                    
                if check_memory_usage() > 0.9:
                    gc.collect()
                    break
                    
    except Exception as e:
        print(f"Error collecting URLs from {base_url}: {str(e)}")
        
    return list(urls)

def parse_website_content(soup):
    # Remove unwanted elements
    for element in soup.find_all(Config.EXCLUDED_ELEMENTS):
        element.decompose()

    # Remove elements with specific classes or IDs
    for element in soup.find_all(class_=Config.EXCLUDED_CLASSES):
        element.decompose()
    
    for element in soup.find_all(id=Config.EXCLUDED_IDS):
        element.decompose()

    # Extract content from specific tags
    content_tags = Config.CONTENT_TAGS
    content = []
    for tag in content_tags:
        elements = soup.find_all(tag)
        for element in elements:
            text = element.get_text(strip=True)
            if text and len(text.split()) > Config.MIN_WORDS_PER_ELEMENT:
                content.append(text)

    return ' '.join(content)


def process_batch(urls):
    session = create_session()
    results = []
    
    for url in urls:
        result = fetch_website_content(url, single_page=True)
        results.append(result)
    return results

def fetch_website_content(url, single_page=False):
    result = {
        "content": "",
        "stats": {
            "pages_scraped": 0,
            "total_words": 0,
            "scraping_time": 0,
            "memory_usage": 0
        },
        "errors": []
    }
    
    start_time = time.time()
    session = create_session()
    
    visited_urls = set()
    urls_to_visit = {normalize_url(url)}
    base_domain = urlparse(url).netloc
    
    # Initialize robots.txt parser
    rp = RobotFileParser()
    robots_url = urljoin(url, '/robots.txt')
    try:
        rp.set_url(robots_url)
        rp.read()
    except Exception as e:
        result["errors"].append(f"Failed to read robots.txt: {str(e)}")
        # Set rp to None to indicate robots.txt is not available
        rp = None
    
    while urls_to_visit and len(visited_urls) < Config.MAX_PAGES:
        current_url = urls_to_visit.pop()
        
        if current_url in visited_urls:
            continue
            
        if rp is not None and not is_allowed_to_crawl(current_url, rp):
            result["errors"].append(f"URL not allowed by robots.txt: {current_url}")
            continue
            
        try:
            response = session.get(
                current_url, 
                timeout=Config.REQUEST_TIMEOUT,
                allow_redirects=True
            )
            response.raise_for_status()
            
            if 'text/html' not in response.headers.get('Content-Type', ''):
                continue

            soup = BeautifulSoup(response.text, 'html.parser')
            content = parse_website_content(soup)
            result["content"] += content + " "
            visited_urls.add(current_url)
            result["stats"]["pages_scraped"] += 1
            
            # If single_page is True, don't collect more URLs
            if not single_page:
                for link in soup.find_all('a'):
                    href = link.get('href')
                    if href:
                        absolute_url = urljoin(current_url, href)
                        normalized_url = normalize_url(absolute_url)
                        if (should_crawl_url(normalized_url, base_domain) and 
                            normalized_url not in visited_urls):
                            urls_to_visit.add(normalized_url)
            
            # Memory management
            current_memory = check_memory_usage()
            result["stats"]["memory_usage"] = current_memory
            if current_memory >= Config.MAX_MEMORY_USAGE:
                gc.collect()
                result["errors"].append("Memory usage threshold reached")
                break
                
        except Exception as e:
            result["errors"].append(f"Error scraping {current_url}: {str(e)}")
            continue
            
        # time.sleep(random.uniform(0.1, 0.3))
        
        if single_page:
            break
    
    result["stats"]["scraping_time"] = time.time() - start_time
    result["stats"]["total_words"] = len(result["content"].split())
    result["content"] = result["content"].strip()
    
    return result

# Example usage:
# url = 'https://example.com'
# all_text = fetch_website_content(url)
# print(all_text)