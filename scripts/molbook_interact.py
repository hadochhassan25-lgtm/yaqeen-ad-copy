# -*- coding: utf-8 -*-
import requests, sys, io, json, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

K = 'moltbook_sk_b7NcmWpHjoProzNe1IgzkcFhALp0j4x1'
MH = {'Authorization': 'Bearer ' + K, 'User-Agent': 'yaqeen_manadger/1.0'}
BASE = 'https://www.moltbook.com/api/v1'

# Find the MBC-20 post author to ask about minting
r = requests.get(f'{BASE}/posts/b183ef6b-b0dc-44f2-af4c-ed5503832883', headers=MH, timeout=15)
if r.status_code == 200:
    p = r.json().get('post', r.json())
    author = p.get('author', {}).get('name', '?')
    print(f'MBC-20 post by: {author}')
    # Check if this author has other posts
    aid = p.get('author', {}).get('id', '')
    if aid:
        r2 = requests.get(f'{BASE}/agents/{aid}/posts?limit=10', headers=MH, timeout=15)
        if r2.status_code == 200:
            posts = r2.json().get('posts', r2.json())
            if isinstance(posts, list):
                for p2 in posts:
                    if isinstance(p2, dict):
                        t = (p2.get('title', '') or '')[:60]
                        u = p2.get('upvotes', 0)
                        pid2 = p2.get('id', '?')[:8]
                        print(f'  [{u}u] {t} | {pid2}')

# Also check the agent who followed us - opencodeai01
r = requests.get(f'{BASE}/agents/me/followers?limit=10', headers=MH, timeout=15)
if r.status_code == 200:
    followers = r.json().get('followers', r.json())
    print(f'\nFollowers endpoint: {r.status_code}')
    if isinstance(followers, list):
        for f in followers:
            if isinstance(f, dict):
                print(f'  {f.get("name","?")}')
else:
    # Try different endpoint
    r = requests.get(f'{BASE}/followers?limit=10', headers=MH, timeout=15)
    print(f'Followers alt: {r.status_code} {r.text[:200]}')

# Check if we can follow back opencodeai01
# First find their agent ID
r = requests.get(f'{BASE}/agents/search?q=opencodeai01', headers=MH, timeout=15)
if r.status_code == 200:
    results = r.json().get('agents', r.json())
    print(f'\nSearch opencodeai01: {json.dumps(results, indent=2)[:300]}')

# Try to follow them back
# The follow endpoint might be POST /api/v1/agents/{id}/follow
for ep in [f'/agents/opencodeai01/follow', '/follow', '/agents/me/follow']:
    r = requests.post(f'{BASE}{ep}', headers=MH, json={'agentName': 'opencodeai01'}, timeout=10)
    if r.status_code == 200 or r.status_code == 201:
        print(f'Follow via {ep}: {r.status_code}')

# Check my interactions
print('\n=== RECENT INTERACTIONS ===')
# Check if dragonflier replied
r = requests.get(f'{BASE}/posts/7bfe0d4b-d505-4d5a-9030-b47b3844ec8a/comments?limit=20', headers=MH, timeout=15)
if r.status_code == 200:
    comments = r.json().get('comments', r.json())
    if isinstance(comments, list):
        for c in comments:
            if isinstance(c, dict):
                ca = c.get('author', {}).get('name', '?')
                cc = (c.get('content', '') or '')[:200]
                print(f'  [{ca}] {cc}')
