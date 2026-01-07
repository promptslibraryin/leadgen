import time
import urllib.parse
from playwright.sync_api import sync_playwright
from utils.logger import logger
from utils.proxies import get_random_user_agent

def scrape_google_maps(keyword, city, limit=50):
    logger.info(f"Starting Google Maps scraper for '{keyword}' in '{city}'")
    results = []
    
    with sync_playwright() as p:
        try:
            # Browser Launch (Headless=True server ke liye)
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=get_random_user_agent(),
                viewport={'width': 1920, 'height': 1080},
                locale='en-US' # Language English fix karein
            )
            page = context.new_page()
            
            # --- FIX 1: Correct URL Construction ---
            # Pehle wala URL galat tha, ye standard format hai:
            query = urllib.parse.quote_plus(f"{keyword} {city}")
            maps_url = f"https://www.google.com/maps/search/{query}/"
            
            logger.info(f"Navigating to: {maps_url}")
            
            # --- FIX 2: Wait Logic Change ---
            # 'networkidle' Google Maps par fail hota hai. 
            # Hum 'domcontentloaded' use karenge jo fast aur safe hai.
            page.goto(maps_url, timeout=60000, wait_until="domcontentloaded")
            
            # --- FIX 3: Cookie/Consent Popup Handling ---
            try:
                # Agar Google "Accept Cookies" mangta hai to click karo
                if page.locator('button[aria-label="Accept all"]').count() > 0:
                    page.click('button[aria-label="Accept all"]')
                    time.sleep(2)
            except:
                pass

            # --- FIX 4: Wait for Sidebar Results ---
            try:
                # Sidebar load hone ka wait (Maximum 15 seconds)
                page.wait_for_selector('div[role="feed"]', state="visible", timeout=15000)
                logger.info("Search results loaded.")
            except Exception as e:
                logger.error(f"Results list not found. Page title: {page.title()}")
                # Error dekhne ke liye screenshot lein
                page.screenshot(path="debug_maps_failed.png")
                browser.close()
                return []

            # --- Scrolling Logic ---
            scrollable_div = page.locator('div[role="feed"]')
            
            logger.info("Scrolling to load more results...")
            for i in range(5): 
                # Javascript se scroll karein
                scrollable_div.evaluate("el => el.scrollTop = el.scrollHeight")
                time.sleep(2) # Data load hone ka wait
            
            # --- Link Extraction ---
            # Maps ke links '/maps/place/' pattern mein hote hain
            links = page.locator('a[href*="/maps/place/"]').all()
            
            place_urls = []
            for link in links:
                url = link.get_attribute('href')
                if url:
                    clean_url = url.split('?')[0]
                    if clean_url not in place_urls:
                        place_urls.append(clean_url)
                        if len(place_urls) >= limit:
                            break
            
            logger.info(f"Found {len(place_urls)} places. Extracting details...")

            # --- Data Extraction Loop ---
            for idx, url in enumerate(place_urls):
                try:
                    # Individual Listing Page
                    page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    time.sleep(1) # Rendering wait
                    
                    data = {
                        'name': None,
                        'phone': None,
                        'website': None,
                        'address': None,
                        'source': 'Google Maps'
                    }

                    # Name (H1 tag usually contains the name)
                    if page.locator('h1').count() > 0:
                        data['name'] = page.locator('h1').first.inner_text()

                    # Phone (Button with data-item-id phone)
                    phone_btn = page.locator('button[data-item-id*="phone:tel:"]')
                    if phone_btn.count() > 0:
                        data['phone'] = phone_btn.first.get_attribute('data-item-id').replace('phone:tel:', '')

                    # Website (Button with data-item-id authority)
                    web_btn = page.locator('a[data-item-id="authority"]')
                    if web_btn.count() > 0:
                        data['website'] = web_btn.first.get_attribute('href')
                    
                    # Address (Button with data-item-id address)
                    addr_btn = page.locator('button[data-item-id="address"]')
                    if addr_btn.count() > 0:
                        data['address'] = addr_btn.first.get_attribute('aria-label').replace('Address: ', '')

                    if data['name']:
                        print(f"-> Found: {data['name']}")
                        results.append(data)
                
                except Exception as e:
                    print(f"Skipping a place due to error: {e}")
                    continue

            browser.close()
            
        except Exception as e:
            logger.error(f"Critical Error in Maps Scraper: {str(e)}")
            
    return results