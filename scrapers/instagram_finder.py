import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, unquote
from utils.logger import logger
from utils.proxies import get_random_user_agent
from utils.retryer import retry
import time

def find_instagram(business_name, website=None):
    logger.info(f"Finding Instagram for: {business_name}")
    
    if website:
        instagram_url = extract_instagram_from_website(website)
        if instagram_url:
            return instagram_url
    
    instagram_url = search_google_for_instagram(business_name)
    return instagram_url

@retry()
def fetch_website_content(website):
    if not website.startswith('http'):
        website = 'https://' + website
    
    headers = {'User-Agent': get_random_user_agent()}
    return requests.get(website, headers=headers, timeout=10, allow_redirects=True)

def extract_instagram_from_website(website):
    try:
        response = fetch_website_content(website)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            instagram_links = soup.find_all('a', href=re.compile(r'instagram\.com/[^/]+/?$'))
            
            for link in instagram_links:
                href = link.get('href')
                if href and 'instagram.com/' in href:
                    instagram_url = clean_instagram_url(href)
                    if instagram_url:
                        logger.info(f"Found Instagram from website: {instagram_url}")
                        return instagram_url
            
            text_content = response.text
            instagram_match = re.search(r'instagram\.com/([a-zA-Z0-9._]+)/?', text_content)
            if instagram_match:
                username = instagram_match.group(1)
                if username not in ['share', 'p', 'reel', 'tv', 'explore', 'accounts']:
                    instagram_url = f"https://www.instagram.com/{username}/"
                    logger.info(f"Found Instagram in content: {instagram_url}")
                    return instagram_url
    
    except Exception as e:
        logger.error(f"Error extracting Instagram from website: {str(e)}")
    
    return None

@retry()
def fetch_google_search(search_url):
    headers = {'User-Agent': get_random_user_agent()}
    return requests.get(search_url, headers=headers, timeout=10)

def search_google_for_instagram(business_name):
    try:
        search_query = f"{business_name} Instagram".replace(' ', '+')
        search_url = f"https://www.google.com/search?q={search_query}"
        
        response = fetch_google_search(search_url)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            all_links = soup.find_all('a', href=True)
            
            for link in all_links:
                href = link.get('href')
                
                if '/url?q=' in href:
                    match = re.search(r'/url\?q=([^&]+)', href)
                    if match:
                        url = unquote(match.group(1))
                        if 'instagram.com/' in url:
                            instagram_url = clean_instagram_url(url)
                            if instagram_url:
                                logger.info(f"Found Instagram via Google: {instagram_url}")
                                return instagram_url
                
                elif 'instagram.com/' in href:
                    instagram_url = clean_instagram_url(href)
                    if instagram_url:
                        logger.info(f"Found Instagram via Google: {instagram_url}")
                        return instagram_url
        
        time.sleep(0.5)
    
    except Exception as e:
        logger.error(f"Error searching Google for Instagram: {str(e)}")
    
    return None

def clean_instagram_url(url):
    try:
        if 'instagram.com/' not in url:
            return None
        
        match = re.search(r'instagram\.com/([a-zA-Z0-9._]+)/?', url)
        if match:
            username = match.group(1)
            
            if username in ['p', 'reel', 'tv', 'explore', 'accounts', 'share']:
                return None
            
            return f"https://www.instagram.com/{username}/"
    
    except Exception:
        pass
    
    return None
