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
            print(f"Visiting: {url}")  # Debug: Print URL being visited
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
            else:
                print(f"Failed to retrieve {url}: HTTP {response.status_code}")  # Debug: HTTP Error
        except requests.RequestException as e:
            print(f"Error accessing {url}: {e}")
    
    print(f"Found {len(links)} links.")  # Debug: Print number of links found
    return links

def check_links(links):
    """Check each link for HTTP errors and return lists of accessible and broken links."""
    accessible_links = []
    broken_links = []
    server_errors = []  # List specifically for 500-series errors

    for link in links:
        try:
            response = requests.get(link)
            if response.status_code >= 400:
                broken_links.append(f"Error {response.status_code} at {link}")
            else:
                accessible_links.append(link)
        except requests.RequestException as e:
            broken_links.append(f"Error accessing {link}: {e}")
    
    return accessible_links, broken_links

def write_to_file(filename, links):
    """Write links to a text file."""
    with open(filename, 'w') as file:
        for link in links:
            file.write(f"{link}\n")

if __name__ == '__main__':
    links = get_all_links(BASE_URL)
    if links:
        accessible_links, broken_links = check_links(links)
        # Write accessible links to file
        write_to_file('accessible_links.txt', accessible_links)
        # Write broken links to file
        write_to_file('broken_links.txt', broken_links)
        print(f"Accessible links written to 'accessible_links.txt'")
        print(f"Broken links written to 'broken_links.txt'")
    else:
        print("No links found.")
