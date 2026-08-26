import requests
import toml
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def extract_links(url, deduplicate_and_sort=True):
    """Extracts the page title and all absolute hyperlinks from the given URL.
    
    If deduplicate_and_sort is True, the links are returned as sorted unique links.
    If False, links are returned in the order of appearance, potentially with duplicates.
    """
    if not url.strip().startswith(('http://', 'https://')):
        url = 'https://' + url.strip()
    else:
        url = url.strip()
        
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract page title
    title = soup.title.string if soup.title else ""
    if not title:
        title = urlparse(url).netloc
    title = title.strip()
    
    # Extract links
    links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        full_url = urljoin(url, href)
        parsed = urlparse(full_url)
        if parsed.scheme in ('http', 'https') and parsed.netloc:
            clean_url = full_url.split('#')[0]
            if clean_url:
                links.append(clean_url)
            
    if deduplicate_and_sort:
        return title, sorted(list(set(links)))
    else:
        # Remove consecutive duplicates
        cleaned_links = []
        for link in links:
            if not cleaned_links or link != cleaned_links[-1]:
                cleaned_links.append(link)
        return title, cleaned_links

def format_toml(title, links):
    """Formats the extracted title and links into the program's TOML format."""
    header = toml.dumps({title: {}}).strip()
    if not header.startswith('['):
        # Fallback for special characters or empty title
        header = f'["{title}"]'
        
    toml_lines = [header, "urls = ["]
    for i, url in enumerate(links):
        comma = "," if i < len(links) - 1 else ""
        toml_lines.append(f'    "{url}"{comma}')
    toml_lines.append("]")
    return "\n".join(toml_lines)
