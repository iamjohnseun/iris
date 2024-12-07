import requests
from bs4 import BeautifulSoup

def fetch_website_content(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Failed to fetch the website content: {response.status_code}")

def parse_website_content(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    return ' '.join([p.text for p in soup.find_all('p')])

# USAGE

# url = 'https://example.com'
# html_content = fetch_website_content(url)
# parsed_content = parse_website_content(html_content)
# print(parsed_content)
