import pandas as pd
from datetime import datetime
import os
from utils.logger import logger

def export_leads(leads, keyword, city):
    if not leads:
        logger.warning("No leads to export")
        return None, None
    
    os.makedirs('outputs', exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    keyword_safe = keyword.replace(' ', '_').replace('/', '_')
    city_safe = city.replace(' ', '_').replace('/', '_')
    
    base_filename = f"leads_{keyword_safe}_{city_safe}_{timestamp}"
    csv_path = os.path.join('outputs', f"{base_filename}.csv")
    excel_path = os.path.join('outputs', f"{base_filename}.xlsx")
    
    df = pd.DataFrame(leads)
    
    column_order = ['name', 'phone', 'website', 'address', 'instagram', 'maps_url', 'source']
    existing_columns = [col for col in column_order if col in df.columns]
    df = df[existing_columns]
    
    try:
        df.to_csv(csv_path, index=False, encoding='utf-8')
        logger.info(f"CSV exported to: {csv_path}")
    except Exception as e:
        logger.error(f"Error exporting CSV: {str(e)}")
        csv_path = None
    
    try:
        df.to_excel(excel_path, index=False, engine='openpyxl')
        logger.info(f"Excel exported to: {excel_path}")
    except Exception as e:
        logger.error(f"Error exporting Excel: {str(e)}")
        excel_path = None
    
    logger.info(f"Total leads exported: {len(leads)}")
    
    return csv_path, excel_path
