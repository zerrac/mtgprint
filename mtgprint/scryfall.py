import threading
import time
import requests
from requests.adapters import HTTPAdapter, Retry

class Throttle:

    def __init__(self, delay: float = 0.05):
        self.delay = delay
        self.lock = threading.Lock()
        self.time = 0

    def __enter__(self):
        with self.lock:
            if self.time + self.delay > time.time():
                time.sleep(self.time + self.delay - time.time())
            self.time = time.time()
        return self


    def __exit__(self,exc_type, exc_val, exc_tb):
        pass

rate_limiter = Throttle()
SCRYFALL_URL="https://api.scryfall.com"

http = requests.Session()
retries = Retry(total=5,
                status_forcelist=[ 429, 500, 502, 503, 504])

http.mount('http://', HTTPAdapter(max_retries=retries))
http.mount('https://', HTTPAdapter(max_retries=retries))


def named(card_name: str):
        payload = {
            'exact': card_name,       
        }
        with rate_limiter:
            re = http.get(SCRYFALL_URL+"/cards/named",params=payload)
        
        re.raise_for_status()
            
        return re.json()

def get_card_by_id(id):
    with rate_limiter:
        re  = http.get(SCRYFALL_URL+"/cards/%s" % id)
    re.raise_for_status()
    return re.json()
    
def get_tokens(card):
    token_ids=list()
    if 'all_parts' in card:
        for part in card['all_parts']:
            if part['component'] == 'token':
                token_ids.append(part['id'])
    return token_ids