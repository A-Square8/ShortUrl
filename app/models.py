import threading
from datetime import datetime

_url_store = {}
_lock = threading.RLock()

def create_mapping(short_code, original_url):
    with _lock:
        _url_store[short_code] = {
            "original_url": original_url,
            "click_count": 0,
            "created_at": datetime.utcnow().isoformat()
        }

def get_mapping(short_code):
    with _lock:
        return _url_store.get(short_code)

def increment_click(short_code):
    with _lock:
        if short_code in _url_store:
            _url_store[short_code]["click_count"] += 1

def short_code_exists(short_code):
    with _lock:
        return short_code in _url_store
