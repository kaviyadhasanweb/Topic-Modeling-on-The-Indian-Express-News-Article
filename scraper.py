import requests
from bs4 import BeautifulSoup
import logging

def scrape_headlines():
    """Scrape headlines from the Indian Express India section."""
    url = "https://indianexpress.com/section/india/"
    return scrape_headlines_custom(url)

def scrape_headlines_custom(url):
    """Scrape headlines from a custom URL."""
    logging.info(f"Scraping headlines from: {url}")
    
    try:
        # Add user agent to avoid being blocked
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise exception for 4XX/5XX responses
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try multiple selectors for better compatibility with different sites
        headlines = []
        
        # Look for headlines in h1, h2, h3 tags
        for tag in ['h1', 'h2', 'h3']:
            for heading in soup.find_all(tag):
                # Skip if inside footer, nav, header, sidebar elements
                if heading.find_parent(['footer', 'nav', 'header']) or heading.find_parent(class_=lambda c: c and ('footer' in c or 'nav' in c or 'header' in c or 'sidebar' in c)):
                    continue
                    
                text = heading.get_text(strip=True)
                if text and len(text) > 15:  # Filter out very short texts
                    headlines.append(text)
        
        # Look for article titles in common class names
        title_classes = ['title', 'headline', 'heading', 'article-title', 'story-title']
        for cls in title_classes:
            for elem in soup.find_all(class_=lambda c: c and cls in c.lower()):
                # Skip if inside footer, nav, header elements
                if elem.find_parent(['footer', 'nav', 'header']) or elem.find_parent(class_=lambda c: c and ('footer' in c or 'nav' in c or 'header' in c)):
                    continue
                    
                text = elem.get_text(strip=True)
                if text and len(text) > 15 and text not in headlines:
                    headlines.append(text)
        
        # If we're not getting enough headlines, try with <a> tags that might contain article links
        if len(headlines) < 5:
            for a_tag in soup.find_all('a'):
                # Skip if in navigation, footer or header
                if a_tag.find_parent(['footer', 'nav', 'header']) or a_tag.find_parent(class_=lambda c: c and ('footer' in c or 'nav' in c or 'header' in c)):
                    continue
                    
                # Only consider links that might be article links (with reasonable text length)
                text = a_tag.get_text(strip=True)
                if text and len(text) > 20 and len(text) < 150 and text not in headlines:
                    headlines.append(text)
                    
        # Process headlines to clean them
        cleaned_headlines = []
        for headline in headlines:
            # Remove specific patterns like "More in X" or "View All" that appear in navigation elements
            if any(pattern in headline for pattern in ["More in", "View All", "Read More", "Video", "Follow us"]):
                continue
                
            # Clean up any extra whitespace and newlines
            cleaned = " ".join(headline.split())
            if cleaned and len(cleaned) > 15:
                cleaned_headlines.append(cleaned)
        
        # Remove duplicates while preserving order
        unique_headlines = []
        seen = set()
        for headline in cleaned_headlines:
            if headline not in seen:
                seen.add(headline)
                unique_headlines.append(headline)
        
        logging.info(f"Found {len(unique_headlines)} unique headlines")
        return unique_headlines
        
    except Exception as e:
        logging.error(f"Error scraping headlines: {str(e)}")
        return []