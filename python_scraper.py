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
from urllib.parse import urlparse

# --- EMAIL EXTRACTION FUNCTION ---
def extract_email_from_website(website_url):
    if not website_url:
        return "Not Found"
    
    try:
        # Website par jao (Timeout 5 second rakha hai taaki script slow na ho)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(website_url, headers=headers, timeout=5)
        
        # Agar website khul gayi
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            text_content = soup.get_text()
            
            # Regex se Email dhundo
            email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            emails = re.findall(email_pattern, text_content)
            
            # Common junk emails filter karo (image extensions wagarah)
            valid_emails = [email for email in emails if not email.endswith(('.png', '.jpg', '.jpeg', '.gif', 'wix.com', 'sentry.io'))]
            
            if valid_emails:
                return valid_emails[0] # Pehla valid email return karo
    except:
        pass # Agar error aaye to ignore karo
    
    return "Not Found"

# --- MAIN SCRAPER ---
def get_leads_with_emails():
    keyword = input("Business Keyword (e.g. Dentist): ")
    city = input("City Name (e.g. Mumbai): ")
    target_leads = int(input("Kitni leads chahiye?: "))
    
    search_query = f"{keyword} in {city}"
    print(f"\n🚀 Finding: '{search_query}'...")

    options = webdriver.ChromeOptions()
    options.add_argument("--lang=en-GB")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        driver.get("https://www.google.com/maps")
        time.sleep(3)

        search_box = driver.find_element(By.ID, "searchboxinput")
        search_box.send_keys(search_query)
        search_box.send_keys(Keys.ENTER)
        time.sleep(5)

        # Scrolling logic
        scrollable_div = driver.find_element(By.CSS_SELECTOR, "div[role='feed']")
        
        extracted_data = []
        previous_count = 0
        
        while len(extracted_data) < target_leads:
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
            time.sleep(2)
            
            elements = driver.find_elements(By.CSS_SELECTOR, "div[role='article']")
            if len(elements) == previous_count:
                print("⚠️ No more results found on Maps.")
                break
            previous_count = len(elements)
            
            # Naye elements ko process karo
            # (Note: Hum end se start karke piche check kar rahe hain taaki naye items process ho)
            new_items = elements[len(extracted_data):]
            
            for card in new_items:
                try:
                    text_content = card.text
                    lines = text_content.split('\n')
                    name = lines[0] # Business Name
                    
                    # 1. Phone Find karo
                    phone_pattern = r'((\+91|0)?[ -]?[6-9][0-9]{4}[ -]?[0-9]{5})'
                    phone_match = re.search(phone_pattern, text_content)
                    phone = phone_match.group(0) if phone_match else "Not Available"
                    
                    # 2. Website Link Find karo (Trick part)
                    website_url = None
                    try:
                        # Card ke andar links check karo
                        links = card.find_elements(By.TAG_NAME, "a")
                        for link in links:
                            href = link.get_attribute("href")
                            if href and "google.com" not in href: # Jo google ka link na ho, wo website hai
                                website_url = href
                                break
                    except:
                        website_url = None
                    
                    # 3. Email Hunting (Agar website mili to)
                    email = "Not Found"
                    if website_url:
                        print(f"🌍 Checking Website: {name}...")
                        email = extract_email_from_website(website_url)
                    
                    lead = {
                        "Business Name": name,
                        "Phone": phone,
                        "Email": email,
                        "Website": website_url if website_url else "N/A",
                        "City": city
                    }
                    
                    extracted_data.append(lead)
                    print(f"✅ Lead Added: {name} | 📧 {email}")

                    if len(extracted_data) >= target_leads:
                        break

                except Exception as e:
                    continue
            
            if len(extracted_data) >= target_leads:
                break

        # Save to CSV
        df = pd.DataFrame(extracted_data)
        filename = f"Leads_{keyword}_{city}_WithEmails.csv"
        df.to_csv(filename, index=False)
        print(f"\n🎉 Done! {len(df)} leads saved to {filename}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    get_leads_with_emails()