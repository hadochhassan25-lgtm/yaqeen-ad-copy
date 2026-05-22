import requests, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = 'https://www.moltbook.com/api/v1'
KEY = 'moltbook_sk_b7NcmWpHjoProzNe1IgzkcFhALp0j4x1'
H = {'Authorization': f'Bearer {KEY}', 'User-Agent': 'yaqeen_manadger/1.0'}

# Search for payment/wallet systems
queries = [
    'x402 payment agent',
    'USDC Base agent wallet',
    'ClawTasks bounty earn',
    'NormieClaw sell skills earn',
]

for q in queries:
    r = requests.get(f'{BASE}/search?q={q}&type=posts&limit=5', headers=H, timeout=15)
    if r.status_code == 200:
        data = r.json()
        print(f'\n=== SEARCH: "{q}" ({data.get("count",0)} results) ===')
        for res in data.get('results', [])[:5]:
            title = res.get('title','') or '(comment)'
            ups = res.get('upvotes',0)
            pid = res['post_id']
            r2 = requests.get(f'{BASE}/posts/{pid}', headers=H, timeout=15)
            excerpt = ''
            if r2.status_code == 200:
                excerpt = r2.json().get('post',{}).get('content','')[:250]
            print(f'  [{ups}↑] {title[:90]}')
            print(f'  Link: https://www.moltbook.com/p/{pid}')
            if excerpt: print(f'  {excerpt[:200]}')
            print()

# Also search for ClawTasks specifically
r = requests.get(f'{BASE}/search?q=ClawTasks+USDC+bounty&type=posts&limit=5', headers=H, timeout=15)
if r.status_code == 200:
    print(f'\n=== SEARCH: "ClawTasks" ===')
    for res in r.json().get('results', [])[:5]:
        title = res.get('title','') or '(comment)'
        ups = res.get('upvotes',0)
        pid = res['post_id']
        print(f'  [{ups}↑] {title[:90]}')
        print(f'  Link: https://www.moltbook.com/p/{pid}')
