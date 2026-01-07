from flask import Flask, request, jsonify
import sys
import os

# Aapke existing modules import kar rahe hain
from scrapers.google_maps import scrape_google_maps
from scrapers.justdial import scrape_justdial
from scrapers.instagram_finder import find_instagram
from cleaner import clean_and_merge
# Note: exporter ki zaroorat nahi hai kyunki n8n data sambhal lega

app = Flask(__name__)

@app.route('/api/scrape', methods=['POST'])
def scrape_leads():
    try:
        # 1. n8n se Data lena
        data = request.json
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        keyword = data.get('keyword')
        city = data.get('city')
        limit = int(data.get('limit', 10)) # Default 10 agar n8n ne nahi bheja
        skip_instagram = data.get('skip_instagram', False)

        # Validation
        if not keyword or not city:
            return jsonify({"error": "Keyword and City are required"}), 400

        print(f"--- Processing: {keyword} in {city} (Limit: {limit}) ---")

        # 2. Google Maps Scraping
        print("Starting Google Maps...")
        google_maps_leads = scrape_google_maps(keyword, city, limit)
        
        # 3. JustDial Scraping
        print("Starting JustDial...")
        justdial_leads = scrape_justdial(keyword, city, limit)

        # 4. Cleaning & Merging (Ye aapke cleaner.py se aa raha hai)
        print("Merging Data...")
        # Agar cleaner.py upload nahi kiya to simple merge kar raha hu (Safety ke liye)
        try:
            merged_leads = clean_and_merge(google_maps_leads, justdial_leads)
        except NameError:
            # Fallback agar cleaner.py nahi hai
            merged_leads = google_maps_leads + justdial_leads

        # 5. Instagram Finder (Optional)
        if not skip_instagram and merged_leads:
            print("Finding Instagram Profiles...")
            for lead in merged_leads:
                try:
                    # Sirf tab dhundo agar website ya naam hai
                    name = lead.get('name')
                    website = lead.get('website')
                    
                    if name:
                        instagram = find_instagram(name, website)
                        lead['instagram'] = instagram # Result me add kar diya
                    else:
                        lead['instagram'] = None
                        
                except Exception as e:
                    print(f"Error finding Insta for {lead.get('name')}: {e}")
                    lead['instagram'] = None

        # 6. Final Data Return (JSON format me)
        return jsonify({
            "status": "success",
            "total_leads": len(merged_leads),
            "data": merged_leads
        })

    except Exception as e:
        print(f"ERROR: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # Server start karo
    print("Server starting on port 5000...")
    app.run(host='0.0.0.0', port=5001)