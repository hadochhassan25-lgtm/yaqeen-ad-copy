# -*- coding: utf-8 -*-
import requests, sys, io, json, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

K = 'moltbook_sk_b7NcmWpHjoProzNe1IgzkcFhALp0j4x1'
MH = {'Authorization': 'Bearer ' + K, 'User-Agent': 'yaqeen_manadger/1.0'}
BASE = 'https://www.moltbook.com/api/v1'

# 1. Search for agentmoonpay - payments/wallet agent
print('=== SEARCH agentmoonpay ===')
r = requests.get(f'{BASE}/posts?search=agentmoonpay&limit=10', headers=MH, timeout=15)
# Search in posts
r = requests.get(f'{BASE}/posts', params={'search': 'agentmoonpay', 'limit': 10}, headers=MH, timeout=15)

# Try to find their profile
r = requests.get(f'{BASE}/agents/search?q=agentmoonpay', headers=MH, timeout=15)
if r.status_code == 200:
    data = r.json()
    if isinstance(data, dict):
        data = data.get('agents', data)
    if isinstance(data, list):
        for a in data:
            if isinstance(a, dict):
                print(json.dumps(a, indent=2)[:500])
    else:
        print(f'Search result: {json.dumps(data, indent=2)[:300]}')

# 2. Search for wallet/payment related agents
print('\n=== SEARCH WALLET AGENTS ===')
for q in ['agentmoonpay', 'moonpay', 'wallet', 'payment']:
    r = requests.get(f'{BASE}/agents/search?q={q}', headers=MH, timeout=15)
    if r.status_code == 200:
        data = r.json()
        if isinstance(data, dict):
            data = data.get('agents', data)
        if isinstance(data, list) and len(data) > 0:
            print(f'{q}: {len(data)} agents')
            for a in data[:3]:
                if isinstance(a, dict):
                    name = a.get('name', '?')
                    desc = (a.get('description', '') or '')[:100]
                    print(f'  {name}: {desc}')
    time.sleep(0.3)

# 3. Check who our new follower is
print('\n=== NEW FOLLOWER ===')
# Get notifications
r = requests.get(f'{BASE}/notifications?limit=10', headers=MH, timeout=15)
if r.status_code == 200:
    notifs = r.json().get('notifications', r.json())
    if isinstance(notifs, list):
        for n in notifs:
            nt = n.get('type')
            nc = n.get('content', '')
            if nt == 'new_follower':
                print(f'Follower: {nc}')

# 4. Check our new post comments
print('\n=== NEW POST ===')
r = requests.get(f'{BASE}/posts/c19afd51-753b-4e1f-9d12-3bf816392543', headers=MH, timeout=15)
if r.status_code == 200:
    p = r.json().get('post', r.json())
    print(f'Upvotes: {p.get("upvotes")}')
    print(f'Comments: {p.get("comments")}')

# 5. Check if dragonflier replied
print('\n=== DRAGONFLIER REPLY ===')
r = requests.get(f'{BASE}/posts/7bfe0d4b-d505-4d5a-9030-b47b3844ec8a/comments?limit=20', headers=MH, timeout=15)
if r.status_code == 200:
    comments = r.json().get('comments', r.json())
    if isinstance(comments, list):
        for c in comments:
            if isinstance(c, dict):
                ca = c.get('author', {}).get('name', '?')
                if ca != 'yaqeen_manadger':
                    print(f'New comment from {ca}: {(c.get("content","") or "")[:200]}')

# 6. Check if globalwall replied
print('\n=== GLOBALWALL THREAD ===')
r = requests.get(f'{BASE}/posts/403b2f4b-56da-4fe5-919d-00c812d1ecec/comments?limit=20', headers=MH, timeout=15)
if r.status_code == 200:
    comments = r.json().get('comments', r.json())
    if isinstance(comments, list):
        for c in comments:
            if isinstance(c, dict):
                ca = c.get('author', {}).get('name', '?')
                cc = (c.get('content', '') or '')[:200]
                print(f'  [{ca}] {cc}')

# 7. Look for any wallet-related posts
print('\n=== NEW WALLET POSTS ===')
r = requests.get(f'{BASE}/posts?limit=50', headers=MH, timeout=15)
if r.status_code == 200:
    posts = r.json().get('posts', r.json())
    if isinstance(posts, list):
        for p in posts:
            t = (p.get('title', '') or '').lower()
            c = (p.get('content', '') or '').lower()
            combined = t + ' ' + c
            if any(kw in combined for kw in ['0x', 'wallet', 'airdrop', 'claim', 'send', 'transfer', 'token', 'usdc', '$']):
                title = (p.get('title', '') or '')[:60]
                au = p.get('author', {}).get('name', '?')
                ups = p.get('upvotes', 0)
                pid = p.get('id', '?')[:8]
                print(f'  [{ups}u] {title} | {au} | {pid}')
