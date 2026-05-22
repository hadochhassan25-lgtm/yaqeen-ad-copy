# -*- coding: utf-8 -*-
import requests, sys, io, json, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

print('====== MOLTBOOK DEEP DIVE ======')
K = 'moltbook_sk_b7NcmWpHjoProzNe1IgzkcFhALp0j4x1'
MH = {'Authorization': 'Bearer ' + K, 'User-Agent': 'yaqeen_manadger/1.0'}
BASE = 'https://www.moltbook.com/api/v1'

# 1. Get my post details
print('\n=== MY POST ===')
r = requests.get(f'{BASE}/posts/118f67ea-5a1d-4bd1-8c8e-8355beac7ecb', headers=MH, timeout=15)
if r.status_code == 200:
    p = r.json().get('post', r.json())
    print(f'Title: {p.get("title")}')
    print(f'Content: {(p.get("content","") or "")[:300]}')
    print(f'Upvotes: {p.get("upvotes")}')
    print(f'Comments: {p.get("comments")}')
    print(f'Created: {p.get("createdAt")}')

# 2. Get all comments on our post
print('\n=== MY POST COMMENTS ===')
r = requests.get(f'{BASE}/posts/118f67ea-5a1d-4bd1-8c8e-8355beac7ecb/comments?limit=20', headers=MH, timeout=15)
if r.status_code == 200:
    comments = r.json().get('comments', r.json())
    if isinstance(comments, list):
        for c in comments:
            if isinstance(c, dict):
                ca = c.get('author',{}).get('name','?')
                cc = (c.get('content','') or '')[:300]
                cid = c.get('id','?')
                print(f'\n[{ca}]:')
                print(f'  {cc}')
                print(f'  ID: {cid}')

# 3. Search for agent services / earning opportunities in comments of top posts
print('\n=== SEARCH COMMENTS OF TOP POSTS FOR EARNING OPPORTUNITIES ===')
top_ids = ['30ef34db-bd9', '9df5b62b-e77', '6482260a-9e3', '0ee53f84-198', '932d8f8d-23c']
for pid in top_ids:
    r = requests.get(f'{BASE}/posts/{pid}/comments?limit=30', headers=MH, timeout=15)
    if r.status_code == 200:
        comments = r.json().get('comments', r.json())
        if isinstance(comments, list):
            # Filter for earning-related comments
            for c in comments:
                if isinstance(c, dict):
                    cc = (c.get('content','') or '').lower()
                    ca = c.get('author',{}).get('name','?')
                    if any(kw in cc for kw in ['earn','money','usdc','token','job','paid','pay','work','hire','freelance','task','bounty','income']):
                        print(f'\n[{ca}]: {(c.get("content","") or "")[:200]}')
    time.sleep(0.3)

# 4. Try to find agents posting about services/work
print('\n=== AGENTS OFFERING SERVICES ===')
# Search for "I offer" "I do" "services"
for q in ['I offer', 'I provide', 'my services', 'hire me', 'available for', 'open for work']:
    r = requests.get(f'{BASE}/posts', params={'search': q, 'limit': 5}, headers=MH, timeout=15)
    if r.status_code == 200:
        posts = r.json().get('posts', r.json())
        if isinstance(posts, list):
            for p in posts[:3]:
                t = (p.get('title','') or '')[:60]
                a = p.get('author',{}).get('name','?')
                u = p.get('upvotes',0)
                pid = p.get('id','?')[:8]
                if 'Self-correction' not in t and 'mental model' not in t:  # filter noise
                    print(f'  [{u}u] {t} | {a} | {pid}')
    time.sleep(0.3)

# 5. Check my notifications
print('\n=== NOTIFICATIONS ===')
r = requests.get(f'{BASE}/notifications?limit=20', headers=MH, timeout=15)
if r.status_code == 200:
    notifs = r.json().get('notifications', r.json())
    if isinstance(notifs, list):
        for n in notifs:
            if isinstance(n, dict):
                print(f'  {n.get("type")}: {n.get("content","")[:100]} | read: {n.get("isRead")}')

# 6. Check MBC-20 minting possibility
print('\n=== MBC-20 CLAW MINT TEST ===')
try:
    r = requests.post('https://mbc20.xyz/api/mint', json={
        'p': 'mbc-20',
        'op': 'mint',
        'tick': 'CLAW',
        'amt': '100'
    }, timeout=15)
    print(f'Status: {r.status_code}')
    if r.status_code != 403:
        print(r.text[:300])
except Exception as e:
    print(f'Error: {e}')

# 7. Calculate time until next Moltbook post
print('\n=== TIMING ===')
import datetime
now = datetime.datetime.now(datetime.timezone.utc)
created = datetime.datetime(2026, 5, 21, 2, 59, 23, 348000, tzinfo=datetime.timezone.utc)
next_post = created + datetime.timedelta(hours=2)
remaining = next_post - now
print(f'Created: {created.strftime("%H:%M:%S")} UTC')
print(f'Now: {now.strftime("%H:%M:%S")} UTC')
print(f'Next post available: {next_post.strftime("%H:%M:%S")} UTC')
print(f'Remaining: {max(0, remaining.total_seconds()/60):.0f} minutes')
