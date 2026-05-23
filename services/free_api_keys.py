"""
YAQEEN Free API Keys — Auto-refreshing keys from free-llm-api-keys GitHub repo.
Fetches README.md every 30 min, parses the key tables, rotates expired keys.
"""
import requests, re, time, threading, json
from pathlib import Path
from datetime import datetime

README_URL = 'https://raw.githubusercontent.com/alistaitsacle/free-llm-api-keys/main/README.md'
API_BASE = 'https://aiapiv2.pekpik.com/v1'
REFRESH_INTERVAL = 1800  # 30 min
CACHE_FILE = Path(__file__).resolve().parent / 'keys_cache.json'

_keys_by_model = {}
_keys_list = []
_last_refresh = 0
_lock = threading.Lock()

def fetch_keys():
    try:
        r = requests.get(README_URL, timeout=15)
        if r.status_code != 200:
            return
        text = r.text
        pattern = r'\|\s*`(sk-[A-Za-z0-9]{45,65})`\s*\|\s*([\w\.-]+)\s*\|\s*.*?\|\s*\$?(\d+)\s*\|\s*(\d+)\s*RPM\s*\|\s*(\d{4}-\d{2}-\d{2})'
        matches = re.findall(pattern, text)
        parsed = {}
        all_keys = []
        now = datetime.now()
        for key, model, budget, rpm, exp_date in matches:
            try:
                exp = datetime.strptime(exp_date, '%Y-%m-%d')
                if exp < now:
                    continue
            except:
                continue
            entry = {
                'key': key,
                'model': model,
                'budget': int(budget),
                'rpm': int(rpm),
                'expires': exp_date
            }
            if model not in parsed:
                parsed[model] = []
            parsed[model].append(entry)
            all_keys.append(entry)

        with _lock:
            _keys_by_model.clear()
            _keys_by_model.update(parsed)
            _keys_list.clear()
            _keys_list.extend(all_keys)
            global _last_refresh
            _last_refresh = time.time()

        try:
            with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump({'_ts': time.time(), 'keys': all_keys}, f, ensure_ascii=False)
        except:
            pass
    except:
        _load_cache()

def _load_cache():
    try:
        if CACHE_FILE.exists():
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                cached = json.load(f)
            if cached.get('keys'):
                parsed = {}
                for entry in cached['keys']:
                    m = entry['model']
                    if m not in parsed:
                        parsed[m] = []
                    parsed[m].append(entry)
                with _lock:
                    _keys_by_model.clear()
                    _keys_by_model.update(parsed)
                    _keys_list.clear()
                    _keys_list.extend(cached['keys'])
    except:
        pass

def get_key(model='smart-chat'):
    if time.time() - _last_refresh > REFRESH_INTERVAL:
        fetch_keys()
    with _lock:
        keys = _keys_by_model.get(model, [])
        if not keys:
            keys = _keys_by_model.get('smart-chat', [])
        if not keys:
            for m, ks in _keys_by_model.items():
                keys.extend(ks)
        if keys:
            keys.sort(key=lambda k: k.get('budget', 0), reverse=True)
            return keys[0]['key']
    return None

def get_keys_by_model(model='smart-chat'):
    if time.time() - _last_refresh > REFRESH_INTERVAL:
        fetch_keys()
    with _lock:
        return _keys_by_model.get(model, [])[:5]

def get_all_keys():
    if time.time() - _last_refresh > REFRESH_INTERVAL:
        fetch_keys()
    with _lock:
        return _keys_list[:]

def get_models():
    if time.time() - _last_refresh > REFRESH_INTERVAL:
        fetch_keys()
    with _lock:
        return {m: len(ks) for m, ks in _keys_by_model.items()}

def test_key(key, model='smart-chat'):
    try:
        from openai import OpenAI
        client = OpenAI(base_url=API_BASE, api_key=key)
        resp = client.chat.completions.create(
            model=model, messages=[{'role': 'user', 'content': 'hi'}], max_tokens=5, timeout=10
        )
        return bool(resp.choices)
    except:
        return False

def background_refresh():
    fetch_keys()
    while True:
        time.sleep(REFRESH_INTERVAL)
        fetch_keys()

def init():
    t = threading.Thread(target=background_refresh, daemon=True)
    t.start()

if __name__ == '__main__':
    fetch_keys()
    print(f'Models: {get_models()}')
    print(f'smart-chat keys: {len(get_keys_by_model("smart-chat"))}')
    k = get_key('smart-chat')
    print(f'Best smart-chat key: {k[:20]}...')
    print(f'All: {len(get_all_keys())} keys')
