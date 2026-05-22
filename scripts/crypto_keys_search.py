# -*- coding: utf-8 -*-
import requests, sys, io, json, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ===== PART 2: Dealwork - try claiming open tasks =====
AK = 'ak_3adeca8d7e789d6986a2cb7f07aedafd4c00f29c8f1efe43'
BASE = 'https://dealwork.ai/api/v1'
H = {'Authorization': 'Bearer ' + AK, 'Content-Type': 'application/json', 'User-Agent': 'yaqeen_manadger/1.0'}

# Check for real buyer jobs (filtering out agent listings)
print('=== REAL BUYER JOBS (search for specific work needs) ===')
buyer_keywords = ['need','help','looking for','hire','i want','i need','please']
for kw in ['need help','looking for','hire','i want']:
    r = requests.get(f'{BASE}/jobs', params={'search': kw, 'per_page': 20}, headers=H, timeout=15)
    if r.status_code == 200:
        jobs = r.json().get('data', [])
        if len(jobs) > 0:
            print(f'\n--- Search "{kw}": {len(jobs)} jobs ---')
            for j in jobs:
                t = (j.get('title') or '?')[:60]
                bmin = j.get('budgetMin') or '?'
                bmax = j.get('budgetMax') or '?'
                print(f'  ${bmin}-${bmax} | {t}')
    time.sleep(0.3)

# ===== PART 3: AgentFlex - check leaderboard for earning agents =====
print('\n\n=== AGENTFLEX LEADERBOARD ===')
try:
    r = requests.get('https://agentflex.vip/api/leaderboard', timeout=15)
    print(f'Status: {r.status_code}')
    if r.status_code == 200:
        print(json.dumps(r.json(), indent=2)[:1000])
    else:
        print(r.text[:300])
except:
    pass
try:
    # Try common API endpoints
    for ep in ['/api/agents','/api/top','/agents.json','/leaderboard.json']:
        r = requests.get(f'https://agentflex.vip{ep}', timeout=15)
        print(f'{ep}: {r.status_code}')
        if r.status_code == 200:
            print(r.text[:500])
except:
    pass

# ===== PART 4: Check Moltbook agent pages for opportunities =====
print('\n\n=== MOLTBOOK AGENT DIRECT SEARCH ===')
K = 'moltbook_sk_b7NcmWpHjoProzNe1IgzkcFhALp0j4x1'
MH = {'Authorization': 'Bearer ' + K, 'User-Agent': 'yaqeen_manadger/1.0'}
MBASE = 'https://www.moltbook.com/api/v1'

# Try to get agents list
r = requests.get(f'{MBASE}/agents?per_page=50', headers=MH, timeout=15)
print(f'Agents list: {r.status_code}')
if r.status_code == 200:
    data = r.json()
    print(json.dumps(data, indent=2)[:500])

# Check if there's a wallet endpoint
r = requests.get(f'{MBASE}/wallet', headers=MH, timeout=15)
print(f'\nWallet: {r.status_code}')
if r.status_code == 200:
    print(r.text[:300])

# ===== PART 5: Check our Moltbook balance and tokens =====
print('\n\n=== MOLTBOOK MY DATA ===')
r = requests.get(f'{MBASE}/agents/me', headers=MH, timeout=15)
if r.status_code == 200:
    me = r.json().get('agent', r.json())
    print(f'Name: {me.get("name")}')
    print(f'Karma: {me.get("karma")}')
    # Check for any balance field
    for key in me:
        if any(x in key.lower() for x in ['balance','wallet','token','coin','credit','point']):
            print(f'{key}: {me[key]}')

# ===== PART 6: Check what dealwork bid status is =====
print('\n\n=== DEALWORK BID STATUS ===')
r = requests.get(f'{BASE}/bids/mine?per_page=20', headers=H, timeout=15)
if r.status_code == 200:
    bids = r.json().get('data', [])
    for b in bids:
        print(json.dumps(b, indent=2)[:400])

# ===== PART 7: Look for any public wallet addresses or airdrops on Moltbook =====
print('\n\n=== MOLTBOOK WALLET/AIRDROP POSTS ===')
# Check specific posts that might contain wallet info
# Read the Zero-Cost crypto post fully
r = requests.get(f'{MBASE}/posts/b183ef6b-b0dc-44f2-af4c-ed5503832883', headers=MH, timeout=15)
if r.status_code == 200:
    p = r.json().get('post', r.json())
    content = (p.get('content', '') or '')
    print('Zero-Cost Crypto post FULL:')
    print(content[:2000])
    print('---')
    # Check comments
    rc = requests.get(f'{MBASE}/posts/b183ef6b-b0dc-44f2-af4c-ed5503832883/comments?limit=20', headers=MH, timeout=15)
    if rc.status_code == 200:
        comments = rc.json().get('comments', rc.json())
        if isinstance(comments, list) and len(comments) > 0:
            print(f'\nComments ({len(comments)}):')
            for c in comments[:10]:
                if isinstance(c, dict):
                    ca = c.get('author',{}).get('name','?')
                    cc = (c.get('content','') or '')[:200]
                    print(f'  [{ca}] {cc}')
