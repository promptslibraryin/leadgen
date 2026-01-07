import time
import functools
from utils.logger import logger
import yaml

def load_config():
    try:
        with open('config.yml', 'r') as f:
            return yaml.safe_load(f)
    except Exception:
        return {}

def get_max_retries():
    config = load_config()
    return config.get('scraping', {}).get('max_retries', 3)

def retry(max_attempts=None, delay=1, exceptions=(Exception,)):
    if max_attempts is None:
        max_attempts = get_max_retries()
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempts += 1
                    if attempts >= max_attempts:
                        logger.error(f"Failed after {max_attempts} attempts: {str(e)}")
                        raise
                    logger.warning(f"Attempt {attempts}/{max_attempts} failed: {str(e)}. Retrying in {delay}s...")
                    time.sleep(delay)
            return None
        return wrapper
    return decorator
