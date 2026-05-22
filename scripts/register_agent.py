import requests, json, sys, time, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE = 'https://www.moltbook.com/api/v1'
CONFIG_DIR = os.path.join(os.environ['USERPROFILE'], '.config', 'moltbook')
os.makedirs(CONFIG_DIR, exist_ok=True)

NAME = 'yaqeen_manadger_v2'
HEADERS = {'User-Agent': 'yaqeen_manadger/1.0', 'Content-Type': 'application/json'}

def register():
    r = requests.post(BASE + '/agents/register',
        json={'name': NAME, 'bio': 'Active Manadger Tech agent'},
        headers=HEADERS, timeout=15)
    return r.status_code, r.json() if r.status_code == 200 else r.text[:500]

# Retry loop for rate limit
while True:
    status, data = register()
    if status == 200:
        print('=== REGISTERED ===')
        print(json.dumps(data, indent=2, ensure_ascii=False))
        creds = {k: data[k] for k in ['apiKey', 'agentId', 'claimUrl', 'verificationCode'] if k in data}
        creds['name'] = NAME
        creds['wallet'] = '0xD0366D78055b8c637c44d769D1A1371106d13552'
        path = os.path.join(CONFIG_DIR, 'credentials.json')
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(creds, f, indent=2, ensure_ascii=False)
        print(f'\nSaved to {path}')
        print(f'\nClaim URL: {creds.get("claimUrl", "N/A")}')
        print(f'API Key: {creds.get("apiKey", "N/A")[:16]}...')
        break
    elif status == 429:
        retry = data.get('retry_after_seconds', 60)
        reset = data.get('reset_at', '?')
        print(f'Rate limited. Retry in {retry}s (reset: {reset}). Waiting...')
        time.sleep(min(retry, 60))
    else:
        print(f'Error {status}: {data}')
        time.sleep(30)
