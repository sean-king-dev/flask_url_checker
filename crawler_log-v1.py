import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format=' %(levelname)s - %(message)s')

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
            logging.info(f"Visiting: {url}")  # Debug: Print URL being visited
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
                logging.warning(f"Failed to retrieve {url}: HTTP {response.status_code}")  # Debug: HTTP Error
        except requests.RequestException as e:
            logging.error(f"Error accessing {url}: {e}")
        
        # Be polite and avoid overwhelming the server
        time.sleep(1)
    
    logging.info(f"Found {len(links)} links.")  # Debug: Print number of links found
    return links

def check_links(links):
    """Check each link for HTTP errors and return lists of accessible and broken links."""
    accessible_links = []
    broken_links = []
    server_errors = []  # List specifically for 500-series errors

    for link in links:
        try:
            response = requests.get(link)
            if response.status_code >= 500:
                # Specifically handle 500-series server errors
                server_errors.append(f"Server Error {response.status_code} at {link}")
            elif response.status_code >= 400:
                # Handle 400-series client errors
                broken_links.append(f"Client Error {response.status_code} at {link}")
            else:
                # Consider links with status code less than 400 as accessible
                accessible_links.append(link)
        except requests.RequestException as e:
            # Handle exceptions related to network issues or invalid requests
            broken_links.append(f"Error accessing {link}: {e}")
    
    # Log the number of server errors for debugging
    if server_errors:
        logging.error(f"Found {len(server_errors)} server errors.")
        for error in server_errors:
            logging.error(error)
    
    return accessible_links, broken_links, server_errors

def write_to_file(filename, links):
    """Write links to a text file."""
    with open(filename, 'w') as file:
        for link in links:
            file.write(f"{link}\n")

if __name__ == '__main__':
    links = get_all_links(BASE_URL)
    if links:
        accessible_links, broken_links, server_errors = check_links(links)
        
        # Write accessible links to file
        write_to_file('accessible_links.txt', accessible_links)
        
        # Write broken links to file
        write_to_file('broken_links.txt', broken_links)
        
        # Write server errors to file
        write_to_file('server_errors.txt', server_errors)
        
        logging.info(f"Accessible links written to 'accessible_links.txt'")
        logging.info(f"Broken links written to 'broken_links.txt'")
        logging.info(f"Server errors written to 'server_errors.txt'")
    else:
        logging.info("No links found.")
