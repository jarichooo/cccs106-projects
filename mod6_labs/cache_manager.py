import json
import os
import time

CACHE_FILE = "weather_cache.json"
CACHE_EXPIRY_MINUTES = 10  # adjust freely

def save_cache(data):
    cache = {
        "timestamp": time.time(),
        "data": data
    }
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f)


def load_cache():
    if not os.path.exists(CACHE_FILE):
        return None
    
    with open(CACHE_FILE, "r") as f:
        cache = json.load(f)

    # expiration check
    age_minutes = (time.time() - cache["timestamp"]) / 60
    if age_minutes > CACHE_EXPIRY_MINUTES:
        return None
    
    return cache


def cache_available():
    return os.path.exists(CACHE_FILE)
