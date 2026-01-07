#!/usr/bin/env python3

import argparse
import sys
from utils.logger import logger
from scrapers.google_maps import scrape_google_maps
from scrapers.justdial import scrape_justdial
from scrapers.instagram_finder import find_instagram
from cleaner import clean_and_merge
from exporter import export_leads

def main():
    parser = argparse.ArgumentParser(
        description='Lead Generator - Scrape business leads from Google Maps, JustDial, and Instagram',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python cli.py --keyword "IT company" --city "Mehsana"
  python cli.py --keyword "restaurant" --city "Mumbai" --limit 100
  python cli.py -k "coffee shop" -c "Delhi" -l 30
        '''
    )
    
    parser.add_argument(
        '--keyword', '-k',
        type=str,
        required=True,
        help='Business keyword to search for (e.g., "IT company", "restaurant")'
    )
    
    parser.add_argument(
        '--city', '-c',
        type=str,
        required=True,
        help='City to search in (e.g., "Mehsana", "Mumbai")'
    )
    
    parser.add_argument(
        '--limit', '-l',
        type=int,
        default=50,
        help='Maximum number of leads to scrape (default: 50)'
    )
    
    parser.add_argument(
        '--skip-instagram',
        action='store_true',
        help='Skip Instagram profile search'
    )
    
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("LEAD GENERATOR STARTED")
    logger.info("=" * 60)
    logger.info(f"Keyword: {args.keyword}")
    logger.info(f"City: {args.city}")
    logger.info(f"Limit: {args.limit}")
    logger.info("=" * 60)
    
    try:
        logger.info("\n[1/5] Scraping Google Maps...")
        google_maps_leads = scrape_google_maps(args.keyword, args.city, args.limit)
        logger.info(f"✓ Google Maps: {len(google_maps_leads)} leads found")
        
        logger.info("\n[2/5] Scraping JustDial...")
        justdial_leads = scrape_justdial(args.keyword, args.city, args.limit)
        logger.info(f"✓ JustDial: {len(justdial_leads)} leads found")
        
        logger.info("\n[3/5] Cleaning and merging leads...")
        merged_leads = clean_and_merge(google_maps_leads, justdial_leads)
        logger.info(f"✓ Total unique leads: {len(merged_leads)}")
        
        if not args.skip_instagram and merged_leads:
            logger.info("\n[4/5] Finding Instagram profiles...")
            count = 0
            for lead in merged_leads:
                try:
                    instagram = find_instagram(lead.get('name'), lead.get('website'))
                    if instagram:
                        lead['instagram'] = instagram
                        count += 1
                except Exception as e:
                    logger.error(f"Error finding Instagram for {lead.get('name')}: {str(e)}")
            logger.info(f"✓ Found {count} Instagram profiles")
        else:
            logger.info("\n[4/5] Skipping Instagram search")
            for lead in merged_leads:
                lead['instagram'] = None
        
        logger.info("\n[5/5] Exporting leads...")
        csv_path, excel_path = export_leads(merged_leads, args.keyword, args.city)
        
        logger.info("\n" + "=" * 60)
        logger.info("LEAD GENERATION COMPLETE!")
        logger.info("=" * 60)
        logger.info(f"Total leads: {len(merged_leads)}")
        if csv_path:
            logger.info(f"CSV file: {csv_path}")
        if excel_path:
            logger.info(f"Excel file: {excel_path}")
        logger.info("=" * 60)
        
        return 0
    
    except KeyboardInterrupt:
        logger.warning("\nProcess interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"\nFatal error: {str(e)}", exc_info=True)
        return 1

if __name__ == '__main__':
    sys.exit(main())
