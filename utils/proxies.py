import random
import yaml

def load_config():
    try:
        with open('config.yml', 'r') as f:
            return yaml.safe_load(f)
    except Exception:
        return {}

def get_random_user_agent():
    config = load_config()
    user_agents = config.get('user_agents', [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ])
    return random.choice(user_agents)

def get_random_delay():
    config = load_config()
    scraping = config.get('scraping', {})
    delay_min = scraping.get('delay_min', 0.5)
    delay_max = scraping.get('delay_max', 2.0)
    return random.uniform(delay_min, delay_max)
