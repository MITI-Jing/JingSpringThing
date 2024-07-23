import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

def fetch_page(url):
    """Fetch the content of a web page."""
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to fetch {url} with status code {response.status_code}")
        return None

def parse_dates_from_html(html):
    """Parse dates from HTML content."""
    soup = BeautifulSoup(html, 'html.parser')
    dates = []

    # Example: extracting all dates in the format YYYY-MM-DD from text
    date_pattern_text = re.compile(r'\b\d{4}-\d{2}-\d{2}\b')

    for tag in soup.find_all(string=date_pattern_text):
        match = date_pattern_text.search(tag)
        if match:
            dates.append(match.group())
    
    # Example: extracting dates from meta tags
    meta_tags = soup.find_all('meta')
    for tag in meta_tags:
        if 'content' in tag.attrs:
            date_pattern_meta = re.compile(r'\d{4}-\d{2}-\d{2}')
            match = date_pattern_meta.search(tag.attrs['content'])
            if match:
                dates.append(match.group())

    return dates

def scrape_dates_from_urls(urls):
    """Scrape dates from a list of URLs and store them in a DataFrame."""
    data = []

    for url in urls:
        html = fetch_page(url)
        if html:
            dates = parse_dates_from_html(html)
            for date in dates:
                data.append({
                    'url': url,
                    'date': date
                })
        else:
            print(f"Failed to fetch {url}")
    
    return pd.DataFrame(data)

# Example usage
if __name__ == "__main__":
    urls = [
        'https://example.com/page1',
        'https://example.com/page2',
        'https://example.com/page3'
    ]

    df = scrape_dates_from_urls(urls)
    print(df)
    # Optionally, save the DataFrame to a CSV file
    df.to_csv('scraped_dates.csv', index=False)