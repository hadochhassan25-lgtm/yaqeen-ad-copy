# -*- coding: utf-8 -*-
import requests, sys, io, json, re, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

K = 'moltbook_sk_b7NcmWpHjoProzNe1IgzkcFhALp0j4x1'
MH = {'Authorization': 'Bearer ' + K, 'User-Agent': 'yaqeen_manadger/1.0'}
BASE = 'https://www.moltbook.com/api/v1'

# Try different submolt endpoints to find where wallet discussions happen
submolts_to_try = [
    'm/agentfinance', 'm/agenteconomy', 'm/crypto', 'm/usdc', 'm/agentcommerce',
    'm/finance', 'm/economics', 'm/investing', 'm/trading', 'm/markets',
]

print('=== SUBMOLT DISCOVERY ===')
for sm in submolts_to_try:
    # Try different API patterns
    for pat in [f'/submolts/by-name/{sm.replace("m/","")}', f'/m/{sm.replace("m/","")}', f'/submolts/{sm.replace("m/","")}']:
        r = requests.get(f'{BASE}{pat}', headers=MH, timeout=10)
        if r.status_code == 200:
            print(f'FOUND: {pat}')
            d = r.json().get('submolt', r.json())
            print(json.dumps(d, indent=2)[:300])
            break
    time.sleep(0.2)

# Scan posts for wallet addresses (0x...)
print('\n=== WALLET ADDRESSES IN POSTS ===')
r = requests.get(f'{BASE}/posts?limit=50', headers=MH, timeout=15)
if r.status_code == 200:
    posts = r.json().get('posts', r.json())
    if isinstance(posts, list):
        for p in posts:
            if isinstance(p, dict):
                title = p.get('title', '') or ''
                content = p.get('content', '') or ''
                combined = title + ' ' + content
                # Find 0x addresses
                addresses = re.findall(r'0x[a-fA-F0-9]{40}', combined)
                if addresses:
                    pid = p.get('id', '?')[:12]
                    au = p.get('author', {}).get('name', '?')
                    ups = p.get('upvotes', 0)
                    print(f'\n[{ups}u] {title[:60]} | {au}')
                    print(f'  Addresses: {addresses}')

# Check if there are wallet/token airdrop posts
print('\n=== AIRDROP/CLAIM POSTS ===')
r = requests.get(f'{BASE}/posts?limit=50', headers=MH, timeout=15)
if r.status_code == 200:
    posts = r.json().get('posts', r.json())
    if isinstance(posts, list):
        for p in posts:
            if isinstance(p, dict):
                title = p.get('title', '') or ''
                content = p.get('content', '') or ''
                combined = (title + ' ' + content).lower()
                if any(kw in combined for kw in ['airdrop', 'claim free', 'free token', 'free mint', 'giveaway', 'faucet']):
                    pid = p.get('id', '?')[:8]
                    au = p.get('author', {}).get('name', '?')
                    ups = p.get('upvotes', 0)
                    print(f'  [{ups}u] {title[:60]} | {au} | {pid}')

# Check the post that mentioned wallet keywords
print('\n=== POSTS WITH WALLET KEYWORDS ===')
r = requests.get(f'{BASE}/posts?limit=50', headers=MH, timeout=15)
if r.status_code == 200:
    posts = r.json().get('posts', r.json())
    if isinstance(posts, list):
        for p in posts:
            if isinstance(p, dict):
                title = p.get('title', '') or ''
                content = p.get('content', '') or ''
                combined = (title + ' ' + content).lower()
                # Only include posts that genuinely have wallet content (not agentmoonpay comments)
                if 'wallet' in combined and 'moonpay' not in combined and 'high-trust' not in combined:
                    pid = p.get('id', '?')[:8]
                    au = p.get('author', {}).get('name', '?')
                    ups = p.get('upvotes', 0)
                    score = sum(1 for kw in ['wallet','crypto','token','airdrop','claim','usdc','base','eth'] if kw in combined)
                    if score >= 2:
                        print(f'  [{ups}u] {title[:70]} | {au} | {pid}')
