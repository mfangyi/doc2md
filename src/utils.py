import re
from urllib.parse import urlparse

def clean_filename(filename):
    """Cleans a string to make it a valid filename, replacing invalid characters with underscores."""
    return re.sub(r'[\\/:*?"<>| ]', '_', filename)

def generate_filename_from_url(url):
    """Generates a base filename from a URL path."""
    path = urlparse(url).path.strip('/')
    parts = [p for p in path.split('/') if p]
    return f"{parts[-2]}_{parts[-1]}" if len(parts) >= 2 else (parts[0] if parts else "untitled")

def generate_unique_filename(directory, base_filename, existing_files):
    """Generates a unique filename within a set of existing files in the directory."""
    counter = 1
    unique_filename = base_filename
    while unique_filename in existing_files:
        unique_filename = f"{base_filename}_{counter}"
        counter += 1
    existing_files.add(unique_filename)
    return unique_filename
