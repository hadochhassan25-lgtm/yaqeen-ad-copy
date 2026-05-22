# -*- coding: utf-8 -*-
import requests, sys, io, json, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

K = 'moltbook_sk_b7NcmWpHjoProzNe1IgzkcFhALp0j4x1'
H = {'Authorization': 'Bearer ' + K, 'User-Agent': 'yaqeen_manadger/1.0'}
BASE = 'https://www.moltbook.com/api/v1'

# 1. Get posts from key earning submolts
submolts = ['agentfinance', 'agenteconomy', 'crypto', 'agentcommerce', 'usdc', 'builds', 'agentskills', 'jobs']
for slug in submolts:
    r = requests.get(f'{BASE}/submolts/{slug}/posts?limit=20', headers=H, timeout=15)
    if r.status_code == 200:
        posts = r.json().get('posts', r.json())
        if isinstance(posts, list) and len(posts) > 0:
            print(f'\n=== [{slug}] {len(posts)} posts ===')
            for p in posts[:15]:
                t = (p.get('title', '') or '')[:60]
                a = p.get('author', {}).get('name', '?')
                u = p.get('upvotes', 0)
                c = p.get('comments', 0)
                pid = p.get('id', '?')[:8]
                print(f'  [{u}u/{c}c] {t} | {a} | {pid}')
        else:
            print(f'\n[{slug}]: 0 posts')
    else:
        print(f'\n[{slug}]: HTTP {r.status_code}')
    time.sleep(0.3)

# 2. Search for earning keywords
print('\n\n========== SEARCH ==========')
for kw in ['airdrop','claim free','mint token','earn usdc','passive income','make money','bounty']:
    r = requests.get(f'{BASE}/posts', params={'search': kw, 'limit': 10}, headers=H, timeout=15)
    if r.status_code == 200:
        posts = r.json().get('posts', r.json())
        if isinstance(posts, list) and len(posts) > 0:
            print(f'\n--- "{kw}": {len(posts)} posts ---')
            for p in posts[:8]:
                t = (p.get('title', '') or '')[:60]
                a = p.get('author', {}).get('name', '?')
                u = p.get('upvotes', 0)
                pid = p.get('id', '?')[:8]
                print(f'  [{u}u] {t} | {a} | {pid}')
        else:
            print(f'\n"{kw}": 0 results')
    else:
        print(f'\n"{kw}": HTTP {r.status_code}')
    time.sleep(0.3)

# 3. Check our profile stats
print('\n\n========== MY PROFILE ==========')
r = requests.get(f'{BASE}/agents/me', headers=H, timeout=15)
if r.status_code == 200:
    me = r.json().get('agent', r.json())
    print(f'ID: {me["id"]}')
    print(f'Name: {me["name"]}')
    print(f'Karma: {me["karma"]}')
    print(f'Posts: {me["posts_count"]}')
    print(f'Comments: {me["comments_count"]}')
    print(f'Followers: {me["follower_count"]}')
    print(f'Verified: {me.get("is_verified", False)}')
    print(f'Claimed: {me.get("is_claimed", False)}')
    print(f'Active: {me.get("is_active", False)}')
    print(f'Created: {me.get("created_at", "?")}')
    print(f'Active: {me.get("last_active", "?")}')

# 4. Check my posts
r = requests.get(f'{BASE}/agents/me/posts?limit=10', headers=H, timeout=15)
if r.status_code == 200:
    posts = r.json().get('posts', r.json())
    print(f'\n--- MY POSTS ({len(posts)}) ---')
    for p in posts:
        t = (p.get('title', '') or '')[:60]
        u = p.get('upvotes', 0)
        c = p.get('comments', 0)
        pid = p.get('id', '?')[:8]
        print(f'  [{u}u/{c}c] {t} | {pid}')

# 5. Check my comments
r = requests.get(f'{BASE}/agents/me/comments?limit=10', headers=H, timeout=15)
if r.status_code == 200:
    comments = r.json().get('comments', r.json())
    print(f'\n--- MY COMMENTS ({len(comments)}) ---')
    for c in comments:
        pid = c.get('post_id', '?')[:8]
        content = (c.get('content', '') or '')[:80]
        print(f'  {content} | post: {pid}')

# 6. Read specific high-value posts
high_value = {
    '65d76887-4c84-4709-9fc6-a98cc8430bff': 'dealwork.ai guide',
    'bcd19fae-6a37-4fe7-a3f1-5e41a2f93aff': 'dealwork.ai zero invest',
    'b183ef6b-b0dc-44f2-af4c-ed5503832883': 'Zero-Cost Crypto platforms',
    '3423401c-410d-466b-bb03-517771633cb6': 'AgentHired',
    '3a2c8e05-52ce-4b86-9619-edddecc21572': 'SoulMarket',
}
print('\n\n========== HIGH VALUE POSTS (FULL) ==========')
for pid, label in high_value.items():
    r = requests.get(f'{BASE}/posts/{pid}', headers=H, timeout=15)
    if r.status_code == 200:
        p = r.json().get('post', r.json())
        title = p.get('title', '?')
        content = p.get('content', '') or ''
        author = p.get('author', {}).get('name', '?')
        ups = p.get('upvotes', 0)
        print(f'\n===== [{ups}u] {label} =====')
        print(f'by {author} | {title}')
        print(content[:1200])
        print('---')
    else:
        print(f'\n{label}: HTTP {r.status_code}')
    time.sleep(0.3)
