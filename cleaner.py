import phonenumbers
from rapidfuzz import fuzz
from utils.logger import logger
import re

def normalize_phone(phone_str, default_region='IN'):
    if not phone_str:
        return None
    
    try:
        phone_str = str(phone_str).strip()
        phone_str = re.sub(r'[^\d\+]', '', phone_str)
        
        if not phone_str:
            return None
        
        parsed = phonenumbers.parse(phone_str, default_region)
        
        if phonenumbers.is_valid_number(parsed):
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except Exception as e:
        logger.debug(f"Could not normalize phone: {phone_str} - {str(e)}")
    
    return phone_str if phone_str else None

def dedupe(leads, similarity_threshold=85):
    logger.info(f"Deduplicating {len(leads)} leads...")
    
    if not leads:
        return []
    
    unique_leads = []
    seen_phones = set()
    seen_names = []
    
    for lead in leads:
        phone = lead.get('phone')
        name = lead.get('name', '').strip()
        
        if not name:
            continue
        
        is_duplicate = False
        
        if phone and phone in seen_phones:
            is_duplicate = True
        
        if not is_duplicate:
            for seen_name in seen_names:
                similarity = fuzz.ratio(name.lower(), seen_name.lower())
                if similarity >= similarity_threshold:
                    is_duplicate = True
                    break
        
        if not is_duplicate:
            unique_leads.append(lead)
            if phone:
                seen_phones.add(phone)
            seen_names.append(name)
    
    logger.info(f"Removed {len(leads) - len(unique_leads)} duplicates. {len(unique_leads)} unique leads remain")
    return unique_leads

def clean_and_merge(google_maps_leads, justdial_leads):
    logger.info("Cleaning and merging leads...")
    
    all_leads = []
    
    for lead in google_maps_leads:
        cleaned_lead = clean_lead(lead)
        if cleaned_lead:
            all_leads.append(cleaned_lead)
    
    for lead in justdial_leads:
        cleaned_lead = clean_lead(lead)
        if cleaned_lead:
            all_leads.append(cleaned_lead)
    
    logger.info(f"Total leads before deduplication: {len(all_leads)}")
    
    unique_leads = dedupe(all_leads)
    
    return unique_leads

def clean_lead(lead):
    if not lead or not lead.get('name'):
        return None
    
    cleaned = {
        'name': lead.get('name', '').strip(),
        'phone': normalize_phone(lead.get('phone')),
        'website': clean_url(lead.get('website')),
        'address': lead.get('address', '').strip() if lead.get('address') else None,
        'maps_url': clean_url(lead.get('maps_url')),
        'instagram': clean_url(lead.get('instagram')),
        'source': lead.get('source', 'Unknown')
    }
    
    if not cleaned['name']:
        return None
    
    return cleaned

def clean_url(url):
    if not url:
        return None
    
    url = str(url).strip()
    
    if not url:
        return None
    
    if not url.startswith('http'):
        url = 'https://' + url
    
    return url
