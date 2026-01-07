import time
import requests
from bs4 import BeautifulSoup
from utils.logger import logger
from utils.proxies import get_random_user_agent, get_random_delay
from utils.retryer import retry
import re

@retry()
def fetch_justdial_page(url):
    headers = {
        'User-Agent': get_random_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    return response.text

def scrape_justdial(keyword, city, limit=50):
    logger.info(f"Starting JustDial scraper for '{keyword}' in '{city}'")
    results = []
    
    try:
        search_query = f"{keyword} {city}".replace(' ', '+')
        justdial_url = f"https://www.justdial.com/search?query={search_query}"
        
        logger.info(f"Fetching JustDial: {justdial_url}")
        html_content = fetch_justdial_page(justdial_url)
        time.sleep(get_random_delay())
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        listings = soup.find_all(['li', 'div'], class_=re.compile(r'.*result.*|.*listing.*|.*card.*', re.I))[:limit*2]
        
        logger.info(f"Found {len(listings)} potential listings")
        
        for idx, listing in enumerate(listings[:limit]):
            try:
                lead = extract_justdial_lead(listing)
                if lead and lead.get('name'):
                    results.append(lead)
                    logger.info(f"Extracted lead {len(results)}: {lead.get('name')}")
                if len(results) >= limit:
                    break
            except Exception as e:
                logger.error(f"Error extracting listing {idx}: {str(e)}")
                continue
        
    except Exception as e:
        logger.error(f"JustDial scraper error: {str(e)}")
    
    logger.info(f"JustDial scraping complete. Found {len(results)} leads")
    return results

def extract_justdial_lead(listing):
    lead = {
        'name': None,
        'phone': None,
        'website': None,
        'address': None,
        'maps_url': None,
        'source': 'JustDial'
    }
    
    try:
        name_elem = listing.find(['h2', 'h3', 'span', 'a'], class_=re.compile(r'.*name.*|.*title.*|.*business.*', re.I))
        if name_elem:
            lead['name'] = name_elem.get_text(strip=True)
    except Exception:
        pass
    
    try:
        phone_elem = listing.find(['span', 'a', 'p'], class_=re.compile(r'.*phone.*|.*mobile.*|.*contact.*', re.I))
        if phone_elem:
            phone_text = phone_elem.get_text(strip=True)
            phone_match = re.search(r'[\d\s\-\+\(\)]{10,}', phone_text)
            if phone_match:
                lead['phone'] = phone_match.group().strip()
        
        if not lead['phone']:
            phone_link = listing.find('a', href=re.compile(r'^tel:'))
            if phone_link:
                lead['phone'] = phone_link['href'].replace('tel:', '').strip()
    except Exception:
        pass
    
    try:
        address_elem = listing.find(['span', 'p', 'div'], class_=re.compile(r'.*address.*|.*location.*', re.I))
        if address_elem:
            lead['address'] = address_elem.get_text(strip=True)
    except Exception:
        pass
    
    try:
        website_elem = listing.find('a', class_=re.compile(r'.*website.*|.*web.*', re.I))
        if website_elem and website_elem.get('href'):
            lead['website'] = website_elem['href']
    except Exception:
        pass
    
    return lead if lead.get('name') else None
