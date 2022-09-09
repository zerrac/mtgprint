import threading
import time
import requests
from requests.adapters import HTTPAdapter, Retry
import os.path
import shutil
import sys

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

def get_localized_card(set, collector_number, lang):
    with rate_limiter:
        re = http.get(SCRYFALL_URL+"/cards/%s/%s/%s" %(set,collector_number, lang))
    re.raise_for_status()
    return re.json()

def search(payload, url=None):
    with rate_limiter:
        if url == None:
            re = http.get(SCRYFALL_URL+"/cards/search", params=payload)
        else:
            re = http.get(url)
    re.raise_for_status()
    data = re.json()['data']

    if re.json()['has_more']:
        data = data + search(payload, re.json()['next_page'])

    return data

def get_prints(oracleid, order = "released", direction ="desc"):
    payload = {
        'q': "oracleid:%s" % oracleid,
        'order': order,
        'dir': direction,
        'unique': 'prints'
    }
    return search(payload)

def download(url, dest):
    if not os.path.exists(dest):
        with rate_limiter:
            re = http.get(url, stream=True)
        re.raise_for_status()
        with open(dest, 'xb') as f:
            re.raw.decode_content = True
            shutil.copyfileobj(re.raw, f)
    else:
        print("Previous copy of the card found. Reusing it!")

def image_getsize(url):
    with rate_limiter:
        re =  http.head(url)
    re.raise_for_status()
    if 'Content-Length' in re.headers.keys():
        return int(re.headers['Content-Length'])
    else: 
        return 0

def get_face_url(image):
    if 'image_uris' in image:
        return image['image_uris']['png']
    elif 'card_faces' in image:
        return  image['card_faces'][0]['image_uris']['png']
    
def get_tokens(card):
    token_ids=list()
    if 'all_parts' in card:
        for part in card['all_parts']:
            if part['component'] == 'token':
                token_ids.append(part['id'])
    return token_ids