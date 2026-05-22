# -*- coding: utf-8 -*-
import requests, sys, io, json, re, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

K = 'moltbook_sk_b7NcmWpHjoProzNe1IgzkcFhALp0j4x1'
MH = {'Authorization': 'Bearer ' + K, 'User-Agent': 'yaqeen_manadger/1.0'}
BASE = 'https://www.moltbook.com/api/v1'

# Read all agentmoonpay posts (wallet key expert)
print('=== AGENTMOONPAY POSTS ===')
moonpay_posts = [
    'abaeddb4', '43799915', '5ccd15d8', '7245bf2a'
]
for pid in moonpay_posts:
    r = requests.get(f'{BASE}/posts/{pid}', headers=MH, timeout=15)
    if r.status_code == 200:
        p = r.json().get('post', r.json())
        print(f'\n--- {(p.get("title","?"))} ---')
        print(f'By: {p.get("author",{}).get("name","?")}')
        print(f'Content: {(p.get("content","") or "")[:800]}')
        print(f'Upvotes: {p.get("upvotes")}')
        # Get comments
        rc = requests.get(f'{BASE}/posts/{pid}/comments?limit=20', headers=MH, timeout=15)
        if rc.status_code == 200:
            comments = rc.json().get('comments', rc.json())
            if isinstance(comments, list):
                for c in comments:
                    if isinstance(c, dict):
                        ca = c.get('author',{}).get('name','?')
                        cc = (c.get('content','') or '')[:200]
                        print(f'  COMMENT [{ca}]: {cc}')
    time.sleep(0.3)

# Read Headless Wallet post
print('\n\n=== HEADLESS WALLET POST ===')
pid = 'b23429fa'
r = requests.get(f'{BASE}/posts/{pid}', headers=MH, timeout=15)
if r.status_code == 200:
    p = r.json().get('post', r.json())
    print(f'Title: {p.get("title")}')
    print(f'Content: {(p.get("content","") or "")[:800]}')
    rc = requests.get(f'{BASE}/posts/{pid}/comments?limit=20', headers=MH, timeout=15)
    if rc.status_code == 200:
        comments = rc.json().get('comments', rc.json())
        if isinstance(comments, list):
            for c in comments:
                if isinstance(c, dict):
                    ca = c.get('author',{}).get('name','?')
                    cc = (c.get('content','') or '')[:200]
                    print(f'  COMMENT [{ca}]: {cc}')

# Read Agent payments post (concordiumagent)
print('\n\n=== AGENT PAYMENTS POST ===')
pid = '90b1352d'
r = requests.get(f'{BASE}/posts/{pid}', headers=MH, timeout=15)
if r.status_code == 200:
    p = r.json().get('post', r.json())
    print(f'Title: {p.get("title")}')
    print(f'Content: {(p.get("content","") or "")[:800]}')

# Read DeFi posts from crypto submolt
print('\n\n=== CRYPTO POSTS ===')
crypto_pids = ['0df47a0d', 'e712cc3b', 'be769fd2']
for pid in crypto_pids:
    r = requests.get(f'{BASE}/posts/{pid}', headers=MH, timeout=15)
    if r.status_code == 200:
        p = r.json().get('post', r.json())
        print(f'\n--- {(p.get("title","?"))} ---')
        print(f'By: {p.get("author",{}).get("name","?")}')
        print(f'Content: {(p.get("content","") or "")[:500]}')
        print(f'Upvotes: {p.get("upvotes")}')
    time.sleep(0.3)

# Also check the agentmoonpay profile  
print('\n\n=== AGENTMOONPAY PROFILE ===')
# Search for their agent info
r = requests.get(f'{BASE}/agents/search?q=agentmoonpay', headers=MH, timeout=15)
if r.status_code == 200:
    print(f'Search: {r.text[:300]}')

# Check solanize (crypto agent)
print('\n\n=== SOLANIZE (CRYPTO AGENT) ===')
pid = '0df47a0d'
r = requests.get(f'{BASE}/posts/{pid}/comments?limit=20', headers=MH, timeout=15)
if r.status_code == 200:
    comments = r.json().get('comments', r.json())
    if isinstance(comments, list):
        for c in comments:
            if isinstance(c, dict):
                ca = c.get('author',{}).get('name','?')
                cc = (c.get('content','') or '')[:200]
                print(f'  [{ca}] {cc}')
