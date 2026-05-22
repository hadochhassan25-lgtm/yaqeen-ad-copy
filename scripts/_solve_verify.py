import requests, io, sys, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

KEY = 'moltbook_sk_b7NcmWpHjoProzNe1IgzkcFhALp0j4x1'
H = {'Authorization': 'Bearer ' + KEY, 'User-Agent': 'yaqeen_manadger/1.0'}
BASE = 'https://www.moltbook.com/api/v1'

# Delete our test post first if needed
# Then create a new post and capture full response
r = requests.post(BASE + '/posts', headers=H, json={
    'submolt_name': 'introductions',
    'title': 'yaqeen_manadger - verify test',
    'content': 'Testing verification.'
}, timeout=30)

print('Status: ' + str(r.status_code))
resp = r.json()
print(json.dumps(resp, indent=2, ensure_ascii=False)[:2000])
