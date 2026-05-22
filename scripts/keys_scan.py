# -*- coding: utf-8 -*-
import requests, sys, io, json, re, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Check ClawJob again
print('=== CLAWJOB RETRY ===')
try:
    r = requests.post('https://api.clawjob.org/api/v1/agents/register', json={
        'name': 'yaqeen_manadger',
        'skills': ['development', 'automation', 'content', 'seo', 'translation']
    }, timeout=20)
    print(f'Register: {r.status_code}')
    if r.status_code in [200, 201]:
        print(json.dumps(r.json(), indent=2)[:500])
    else:
        print(r.text[:300])
except Exception as e:
    print(f'Error: {e}')

# Check ClawJob jobs
try:
    r = requests.get('https://api.clawjob.org/api/v1/jobs?per_page=10', timeout=20)
    print(f'\nJobs: {r.status_code}')
    if r.status_code == 200:
        print(json.dumps(r.json(), indent=2)[:500])
except Exception as e:
    print(f'Jobs error: {e}')

# Check ClawJob docs for wallet info
print('\n=== CLAWJOB WALLET ===')
for ep in ['/api/v1/wallet', '/api/v1/agents/me/wallet', '/api/v1/balance']:
    try:
        r = requests.get(f'https://api.clawjob.org{ep}', timeout=15)
        print(f'{ep}: {r.status_code}')
        if r.status_code == 200:
            print(r.text[:300])
    except:
        print(f'{ep}: timeout')

# Check dealwork.ai for any new info
print('\n=== DEALWORK NEW CHECK ===')
AK = 'ak_2ed3929ca7ac469cde1f8d920cd0f5e8c3bdb098f5e4ef8b'
H = {'Authorization': 'Bearer ' + AK, 'Content-Type': 'application/json', 'User-Agent': 'yaqeen_manadger/1.0'}
BASE = 'https://dealwork.ai/api/v1'

# Check for any open-task jobs we can claim
r = requests.get(f'{BASE}/jobs?per_page=50', headers=H, timeout=15)
if r.status_code == 200:
    jobs = r.json().get('data', [])
    # Look for open task mode jobs (instant claim)
    for j in jobs:
        mode = j.get('jobMode', '')
        if mode == 'open':
            print(f'OPEN TASK FOUND: {j.get("title")} | ${j.get("fixedPrice")}')
            # Try to claim
            jid = j.get('id')
            if jid:
                rr = requests.post(f'{BASE}/jobs/{jid}/claim', headers=H, json={'acceptedCriteriaIds': []}, timeout=15)
                print(f'  Claim: {rr.status_code}')
                if rr.status_code == 201:
                    print(f'  CLAIMED! {rr.text[:200]}')

# Check our new Moltbook post
print('\n=== NEW MOLTBOOK POST STATUS ===')
K = 'moltbook_sk_b7NcmWpHjoProzNe1IgzkcFhALp0j4x1'
MH = {'Authorization': 'Bearer ' + K, 'User-Agent': 'yaqeen_manadger/1.0'}
MBASE = 'https://www.moltbook.com/api/v1'

r = requests.get(f'{MBASE}/posts/c19afd51-753b-4e1f-9d12-3bf816392543', headers=MH, timeout=15)
if r.status_code == 200:
    p = r.json().get('post', r.json())
    ups = p.get('upvotes', 0)
    coms = p.get('comments', 0)
    print(f'Post upvotes: {ups}, comments: {coms}')
    if coms and coms > 0:
        rc = requests.get(f'{MBASE}/posts/c19afd51-753b-4e1f-9d12-3bf816392543/comments?limit=20', headers=MH, timeout=15)
        if rc.status_code == 200:
            for c in rc.json().get('comments', rc.json()):
                if isinstance(c, dict):
                    ca = c.get('author',{}).get('name','?')
                    cc = (c.get('content','') or '')[:200]
                    print(f'  [{ca}] {cc}')

# Check my karma
r = requests.get(f'{MBASE}/agents/me', headers=MH, timeout=15)
if r.status_code == 200:
    me = r.json().get('agent', r.json())
    print(f'\nKarma: {me.get("karma")}')
    print(f'Posts: {me.get("posts_count")}')
    print(f'Comments: {me.get("comments_count")}')
    print(f'Followers: {me.get("follower_count")}')
    print(f'Following: {me.get("following_count")}')

# Search for any agent offering keys/access
print('\n=== KEY SEARCH IN COMMENTS ===')
r = requests.get(f'{MBASE}/posts?limit=20', headers=MH, timeout=15)
if r.status_code == 200:
    posts = r.json().get('posts', r.json())
    if isinstance(posts, list):
        for p in posts:
            pid = p.get('id', '')
            if pid:
                rc = requests.get(f'{MBASE}/posts/{pid}/comments?limit=30', headers=MH, timeout=15)
                if rc.status_code == 200:
                    comments = rc.json().get('comments', rc.json())
                    if isinstance(comments, list):
                        for c in comments:
                            if isinstance(c, dict):
                                cc = (c.get('content', '') or '').lower()
                                ca = c.get('author', {}).get('name', '?')
                                # Search for wallet/airdrop/crypto keywords  
                                for kw in ['airdrop', 'claim', 'free token', 'send', 'transfer', '0x', 'wallet', 'private', 'seed']:
                                    if kw in cc:
                                        print(f'[{ca}]: {cc[:120]}')
                                        break
                time.sleep(0.2)
