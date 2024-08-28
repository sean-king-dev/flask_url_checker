import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# Base URL of your site
BASE_URL = 'https://my.kingseducation.com'

def get_all_links(base_url):
    """Crawl the site and return a list of all internal links."""
    links = set()
    to_visit = [base_url]
    visited = set()
    
    while to_visit:
        url = to_visit.pop()
        if url in visited:
            continue

        visited.add(url)
        try:
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                for anchor in soup.find_all('a', href=True):
                    href = anchor['href']
                    absolute_url = urljoin(base_url, href)
                    parsed_url = urlparse(absolute_url)
                    if parsed_url.netloc == urlparse(base_url).netloc:
                        if absolute_url not in visited:
                            to_visit.append(absolute_url)
                        links.add(absolute_url)
        except requests.RequestException as e:
            print(f"Error accessing {url}: {e}")
    
    return links

def check_links(links):
    """Check each link for HTTP errors."""
    for link in links:
        try:
            response = requests.get(link)
            if response.status_code >= 400:
                print(f"Error {response.status_code} at {link}")
        except requests.RequestException as e:
            print(f"Error accessing {link}: {e}")

if __name__ == '__main__':
    links = get_all_links(BASE_URL)
    check_links(links)
