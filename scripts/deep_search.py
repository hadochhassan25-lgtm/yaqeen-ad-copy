# -*- coding: utf-8 -*-
import requests, sys, io, json, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ===== PART 1: Moltbook - deep search for offers and crypto keys =====
print('='*60)
print('PART 1: MOLTBOOK SEARCH')
print('='*60)

K = 'moltbook_sk_b7NcmWpHjoProzNe1IgzkcFhALp0j4x1'
H = {'Authorization': 'Bearer ' + K, 'User-Agent': 'yaqeen_manadger/1.0'}
BASE = 'https://www.moltbook.com/api/v1'

# Search keywords for opportunities
keywords = [
    'airdrop','claim','free token','mint','CLAW','$JOBS','$USDC','earn crypto',
    'referral','bonus','reward','giveaway','faucet','wallet','private key',
    'seed phrase','deploy','contract','liquidity','pool','stake','yield',
    'bounty','bug bounty','paid task','job offer','hiring','freelance',
    'commission','partnership','collaboration'
]

found_posts = {}
for kw in keywords:
    r = requests.get(f'{BASE}/posts', params={'search': kw, 'limit': 10}, headers=H, timeout=15)
    if r.status_code == 200:
        posts = r.json().get('posts', r.json())
        if isinstance(posts, list) and len(posts) > 0:
            for p in posts:
                pid = p.get('id', '')
                if pid and pid not in found_posts:
                    found_posts[pid] = p
    time.sleep(0.25)

# Print posts we haven't seen before, sorted by upvotes
print(f'\nFound {len(found_posts)} unique posts from keyword search')
# Sort by upvotes
sorted_posts = sorted(found_posts.values(), key=lambda p: -(p.get('upvotes', 0) or 0))

for p in sorted_posts[:30]:
    pid = p.get('id', '?')[:12]
    t = (p.get('title', '') or '')[:70]
    a = p.get('author', {}).get('name', '?')
    u = p.get('upvotes', 0) or 0
    c = p.get('comments', 0) or 0
    print(f'[{u}u/{c}c] {t} | {a} | {pid}')

# Fetch full content of most promising new posts
print('\n\n===== FULL CONTENT OF TOP POSTS =====')
# Read specific high-potential posts we haven't read yet
promising_ids = [pid for pid, p in list(found_posts.items())[:5]]
for pid in promising_ids:
    r = requests.get(f'{BASE}/posts/{pid}', headers=H, timeout=15)
    if r.status_code == 200:
        p = r.json().get('post', r.json())
        t = p.get('title', '?')
        content = (p.get('content', '') or '')[:800]
        au = p.get('author', {}).get('name', '?')
        ups = p.get('upvotes', 0)
        print(f'\n=== [{ups}u] {t} | {au} ===')
        print(content)
        print('---')
    time.sleep(0.3)

# Search comments of high-upvote posts for hidden opportunities
print('\n\n===== COMMENTS ON TOP POSTS =====')
# Get top posts in the feed for comments
r = requests.get(f'{BASE}/posts?limit=10', headers=H, timeout=15)
if r.status_code == 200:
    posts = r.json().get('posts', r.json())
    if isinstance(posts, list):
        for p in posts[:5]:
            pid = p.get('id', '')
            if pid:
                rc = requests.get(f'{BASE}/posts/{pid}/comments?limit=20', headers=H, timeout=15)
                if rc.status_code == 200:
                    comments = rc.json().get('comments', rc.json())
                    if isinstance(comments, list) and len(comments) > 0:
                        t = (p.get('title', '') or '')[:50]
                        print(f'\n--- {t} ({len(comments)} comments) ---')
                        for c in comments[:8]:
                            if isinstance(c, dict):
                                ca = c.get('author', {}).get('name', '?')
                                cc = (c.get('content', '') or '')[:150]
                                print(f'  [{ca}] {cc}')
                time.sleep(0.3)
