from flask import Flask, request, render_template, send_file
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os

app = Flask(__name__)

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
        except requests.RequestException:
            continue
    
    return links

def check_links(links):
    """Check each link for HTTP errors and return lists of accessible and broken links."""
    accessible_links = []
    broken_links = []

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check-links', methods=['POST'])
def check_links_route():
    url = request.form['url']
    links = get_all_links(url)
    accessible_links, broken_links = check_links(links)
    
    # Save results to files
    with open('accessible_links.txt', 'w') as file:
        for link in accessible_links:
            file.write(f"{link}\n")

    with open('broken_links.txt', 'w') as file:
        for link in broken_links:
            file.write(f"{link}\n")

    return render_template('results.html')

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    if not os.path.exists('templates'):
        os.makedirs('templates')
    app.run(debug=True)
