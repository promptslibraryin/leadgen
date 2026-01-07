import time
import pandas as pd
import re
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urljoin

# --- STEP 1: WEBSITE SE EMAIL NIKALNE WALA FUNCTION ---
def get_email_from_site(website_url):
    if not website_url: return "N/A"
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    paths = ["", "/contact", "/contact-us", "/about-us"]
    
    print(f"   Searching inside: {website_url} ...")
    
    try:
        for path in paths:
            full_url = urljoin(website_url, path)
            try:
                response = requests.get(full_url, headers=headers, timeout=5)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Regex for Email
                text = soup.get_text()
                emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
                
                valid_emails = [e for e in emails if not e.endswith(('png', 'jpg', 'wix.com', 'sentry.io'))]
                
                if valid_emails:
                    return valid_emails[0] # Pehla email return karo
            except:
                continue
    except:
        pass
    return "N/A"

# --- STEP 2: JUSTDIAL SCRAPER ---
def scrape_justdial():
    city = input("City Name (e.g., Mumbai): ")
    keyword = input("Business Keyword (e.g., Interior Designers): ")
    target_count = int(input("Kitni leads chahiye?: "))

    # Justdial URL Structure
    url = f"https://www.justdial.com/{city}/{keyword}"
    print(f"\n🚀 Opening Justdial: {url}")

    options = webdriver.ChromeOptions()
    # User Agent badalna zaruri hai nahi to Justdial block kar dega
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        driver.get(url)
        time.sleep(5) # Page load hone do

        data_list = []
        processed_names = []

        # Scrolling Loop
        last_height = driver.execute_script("return document.body.scrollHeight")
        
        while len(data_list) < target_count:
            # Page ko niche scroll karo
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3) # Load hone ka wait
            
            # Justdial ke cards dhundo
            # Note: Justdial classes badalta rehta hai, isliye hum generic structure dhundenge
            cards = driver.find_elements(By.CLASS_NAME, 'resultbox')
            
            if not cards:
                # Backup selector agar 'resultbox' class change ho gayi ho
                cards = driver.find_elements(By.CSS_SELECTOR, "div[data-href]")

            for card in cards:
                try:
                    # 1. Name nikalo
                    name_el = card.find_element(By.CLASS_NAME, 'resultbox_title_anchor')
                    name = name_el.text
                    
                    if name in processed_names: continue
                    processed_names.append(name)

                    # 2. Website Link nikalo (Zaruri step)
                    website_url = None
                    try:
                        # Justdial par website icon aksar alag class me hota hai
                        # Hum saare links check karenge card ke andar
                        links = card.find_elements(By.TAG_NAME, 'a')
                        for link in links:
                            href = link.get_attribute('href')
                            if href and "http" in href and "justdial" not in href:
                                website_url = href
                                break
                    except:
                        pass
                    
                    # 3. Email nikalo (Website se)
                    email = "N/A"
                    if website_url:
                        email = get_email_from_site(website_url)
                    
                    print(f"✅ Found: {name} | 🌐 {website_url} | 📧 {email}")

                    data_list.append({
                        "Business Name": name,
                        "Website": website_url,
                        "Email": email,
                        "City": city
                    })
                    
                    if len(data_list) >= target_count: break
                    
                except Exception as e:
                    continue # Skip error cards

            # Check karo agar aur scroll nahi ho raha
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                print("⚠️ End of list reached.")
                break
            last_height = new_height
            
    except Exception as e:
        print(f"Error: {e}")
        
    finally:
        # Save Data
        if data_list:
            df = pd.DataFrame(data_list)
            filename = f"Justdial_{keyword}_{city}.csv"
            df.to_csv(filename, index=False)
            print(f"\n🎉 Saved {len(df)} leads to {filename}")
        driver.quit()

if __name__ == "__main__":
    scrape_justdial()