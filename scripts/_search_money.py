import requests, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = 'https://www.moltbook.com/api/v1'
KEY = 'moltbook_sk_b7NcmWpHjoProzNe1IgzkcFhALp0j4x1'
H = {'Authorization': f'Bearer {KEY}', 'User-Agent': 'yaqeen_manadger/1.0'}

# Search for money-related topics
queries = [
    'money earning opportunities agents',
    'crypto trading profit',
    'how agents make money',
    'agent finance business',
]

for q in queries:
    r = requests.get(f'{BASE}/search?q={q}&type=posts&limit=5', headers=H, timeout=15)
    if r.status_code == 200:
        data = r.json()
        print(f'\n=== SEARCH: "{q}" ({data.get("count",0)} results) ===')
        for res in data.get('results', [])[:3]:
            title = res.get('title', '') or '(comment)'
            author = res.get('author', {}).get('name', '?')
            ups = res.get('upvotes', 0)
            sim = res.get('similarity', 0)
            pid = res['post_id']
            print(f'  [{res["type"].upper()}] {title[:80]}')
            print(f'  Author: {author} | Upvotes: {ups} | Sim: {sim}')
            print(f'  Link: https://www.moltbook.com/p/{pid}\n')
    else:
        print(f'[ERROR] {q}: {r.status_code}')

# Fetch finance submolts
for sub in ['crypto','agentfinance','trading']:
    r = requests.get(f'{BASE}/submolts/{sub}/feed?sort=hot&limit=6', headers=H, timeout=15)
    if r.status_code == 200:
        data = r.json()
        print(f'\n=== SUBMOLT: m/{sub} (hot) ===')
        for p in data.get('posts', [])[:6]:
            print(f'  [{p.get("upvotes",0)}] {p["title"][:90]}')
            print(f'  by {p["author"]["name"]} | Comments: {p.get("comment_count",0)}')
            print(f'  Link: https://www.moltbook.com/p/{p["id"]}\n')
    else:
        print(f'[ERROR] {sub}: {r.status_code}')

# Also check general feed for money posts
r = requests.get(f'{BASE}/feed?sort=hot&limit=30', headers=H, timeout=15)
if r.status_code == 200:
    print('\n=== GENERAL HOT FEED (money-related) ===')
    for p in r.json().get('posts', []):
        t = p['title'].lower()
        if any(w in t for w in ['money','crypto','token','profit','earn','finance','trade','invest','revenue','pay','buy','sell','nft','defi','rich','dollar']):
            print(f'  [{p.get("upvotes",0)}] {p["title"][:90]}')
            print(f'  by {p["author"]["name"]} in m/{p["submolt_name"]}')
            print(f'  Link: https://www.moltbook.com/p/{p["id"]}\n')
