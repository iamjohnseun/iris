import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def create_session():
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def fetch_website_content(url, visited=None, max_depth=3, delay=1):
    if visited is None:
        visited = set()
    texts = []
    queue = [(url, 0)]
    hostname = urlparse(url).netloc
    session = create_session()

    while queue:
        current_url, depth = queue.pop(0)
        if current_url in visited or depth > max_depth:
            continue
        visited.add(current_url)
        
        try:
            response = session.get(current_url, timeout=(5, 15))
            if response.status_code == 200:
                html_content = response.text
                texts.append(parse_website_content(html_content))

                if depth < max_depth:
                    soup = BeautifulSoup(html_content, 'html.parser')
                    for link in soup.find_all('a', href=True):
                        abs_link = urljoin(current_url, link['href'])
                        if urlparse(abs_link).netloc == hostname and abs_link not in visited:
                            queue.append((abs_link, depth + 1))
        except requests.exceptions.RequestException:
            continue
            
    return ' '.join(texts) if texts else ""

def parse_website_content(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    for script in soup(["script", "style"]):
        script.extract()
    return ' '.join([p.get_text(strip=True) for p in soup.find_all('p')])

# USAGE
# url = 'https://example.com'
# all_text = fetch_website_content(url)
# print(all_text)
