from flask import Flask, request, render_template, send_file
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import logging
import os

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, format=' %(levelname)s - %(message)s')

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
            logging.info(f"Visiting: {url}")
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
                logging.warning(f"Failed to retrieve {url}: HTTP {response.status_code}")
        except requests.RequestException as e:
            logging.error(f"Error accessing {url}: {e}")
        
        time.sleep(1)  # Be polite and avoid overwhelming the server
    
    logging.info(f"Found {len(links)} links.")
    return links


def check_links(links):
    """Check each link for HTTP errors and return lists of accessible and broken links."""
    accessible_links = []
    broken_links = []
    server_errors = []

    for link in links:
        try:
            response = requests.get(link)
            if response.status_code >= 500:
                server_errors.append(f"Server Error {response.status_code} at {link}")
            elif response.status_code >= 400:
                broken_links.append(f"Client Error {response.status_code} at {link}")
            else:
                accessible_links.append(link)
        except requests.RequestException as e:
            broken_links.append(f"Error accessing {link}: {e}")
    
    if server_errors:
        logging.error(f"Found {len(server_errors)} server errors.")
        for error in server_errors:
            logging.error(error)
    
    return accessible_links, broken_links, server_errors


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check-links', methods=['POST'])
def check_links_route():
    url = request.form['url']
    links = get_all_links(url)
    accessible_links, broken_links, server_errors = check_links(links)
    
    write_to_file('accessible_links.txt', accessible_links)
    write_to_file('broken_links.txt', broken_links)
    write_to_file('server_errors.txt', server_errors)
    
    accessible_count = len(accessible_links)
    broken_count = len(broken_links)
    server_error_count = len(server_errors)
    
    return render_template('results.html',
                           accessible_count=accessible_count,
                           broken_count=broken_count,
                           server_error_count=server_error_count)


@app.route('/download/<filename>')
def download_file(filename):
    if os.path.exists(filename):
        return send_file(filename, as_attachment=True)
    else:
        logging.error(f"File not found: {filename}")
        return "File not found", 404


def write_to_file(filename, links):
    """Write links to a text file."""
    with open(filename, 'w') as file:
        for link in links:
            file.write(f"{link}\n")


if __name__ == '__main__':
    if not os.path.exists('templates'):
        os.makedirs('templates')
    app.run(debug=True)
