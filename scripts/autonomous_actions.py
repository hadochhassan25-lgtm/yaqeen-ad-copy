# -*- coding: utf-8 -*-
import requests, sys, io, json, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ========== DEALWORK.AI CHECK ==========
print('========== DEALWORK.AI ==========')
AK = 'ak_2ed3929ca7ac469cde1f8d920cd0f5e8c3bdb098f5e4ef8b'
H = {'Authorization': 'Bearer ' + AK, 'Content-Type': 'application/json', 'User-Agent': 'yaqeen_manadger/1.0'}
BASE = 'https://dealwork.ai/api/v1'

# 1. Bid status
print('\n=== BIDS ===')
r = requests.get(f'{BASE}/bids/mine?per_page=20', headers=H, timeout=15)
if r.status_code == 200:
    for b in r.json().get('data', []):
        amt = b.get('proposedAmount', '?')
        stat = b.get('status', '?')
        jt = b.get('job', {}).get('title', '?')
        print(f'  ${amt} | {stat} | {jt}')

# 2. Contracts
print('\n=== CONTRACTS ===')
for role in ['worker', 'buyer']:
    r = requests.get(f'{BASE}/contracts?role={role}&per_page=20', headers=H, timeout=15)
    if r.status_code == 200:
        data = r.json().get('data', [])
        if data:
            print(f'  {role}: {len(data)}')
            for c in data:
                print(f'    {c.get("state")} | ${c.get("amount")} | {c.get("job",{}).get("title","?")}')

# 3. Pending orders
print('\n=== PENDING REQUESTS ===')
r = requests.get(f'{BASE}/listings/requests/pending', headers=H, timeout=15)
if r.status_code == 200:
    d = r.json().get('data', [])
    print(f'  {len(d)} pending requests')

# 4. Check for new jobs  
print('\n=== NEW JOBS ===')
r = requests.get(f'{BASE}/jobs?per_page=50', headers=H, timeout=15)
if r.status_code == 200:
    jobs = r.json().get('data', [])
    # Filter for real buyer jobs (not agent services like Chinese/SEO)
    real_jobs = []
    for j in jobs:
        t = (j.get('title') or '').lower()
        bmin = j.get('budgetMin')
        bmax = j.get('budgetMax')
        # Skip agent listing-style jobs (Chinese characters, agent names)
        is_listing = any(x in t for x in ['可乐', 'xiao', '枭', 'chinese', 'chinois', 'bilingual'])
        if not is_listing:
            real_jobs.append(j)
    print(f'  Total: {len(jobs)}, Real buyer jobs: {len(real_jobs)}')
    for j in real_jobs:
        t = (j.get('title') or '?')[:60]
        bmin = j.get('budgetMin') or '?'
        bmax = j.get('budgetMax') or '?'
        cat = j.get('category', '?')
        jid = j.get('id','?')[:12]
        print(f'  [${bmin}-${bmax}] {cat} | {t} | {jid}')

# 5. Wallet
print('\n=== WALLET ===')
r = requests.get(f'{BASE}/wallet/balance', headers=H, timeout=15)
if r.status_code == 200:
    w = r.json().get('data', {})
    print(f'  Available: ${w.get("available")} Locked: ${w.get("locked")}')

# ========== CLAWJOB CHECK ==========
print('\n\n========== CLAWJOB ==========')
try:
    r = requests.get('https://api.clawjob.org/api/v1/jobs?per_page=10', timeout=30)
    print(f'  Jobs API: {r.status_code}')
    if r.status_code == 200:
        print(json.dumps(r.json(), indent=2)[:500])
except Exception as e:
    print(f'  API Error: {e}')
# Try registering anyway
try:
    r = requests.post('https://api.clawjob.org/api/v1/agents/register', json={
        'name': 'yaqeen_manadger',
        'skills': ['development', 'automation', 'content', 'seo', 'translation']
    }, timeout=30)
    print(f'  Register: {r.status_code}')
    if r.status_code == 200 or r.status_code == 201:
        print(json.dumps(r.json(), indent=2)[:300])
except Exception as e:
    print(f'  Register error: {e}')

# ========== UPDATE PROJECT CONTEXT ==========
print('\n\n========== SAVING CREDENTIALS ==========')
creds = {
    'dealwork_owner_linked': {
        'note': 'This is the active account linked to owner dodahoda5ez@gmail.com',
        'apiKey': 'ak_2ed3929ca7ac469cde1f8d920cd0f5e8c3bdb098f5e4ef8b',
        'hmacSecret': '2bc793f6c326a057defdaf17018c308e1a4817778f56a471def9147bede3b0c8',
        'agentAccountId': '3c010f1e-3dc1-4812-8bee-cef8a3ecbab2',
        'ownerAccountId': '1c57d04e-f753-457a-aad4-a433ae30669d',
        'ownerEmail': 'dodahoda5ez@gmail.com',
        'serviceAgentId': '94753111-ec59-4bf2-8526-52b66de09f77'
    },
    'dealwork_autonomous_old': {
        'note': 'Old autonomous account, no longer active',
        'apiKey': 'ak_3adeca8d7e789d6986a2cb7f07aedafd4c00f29c8f1efe43',
        'agentAccountId': 'e983e701-ea5b-45e1-899b-ffa5e76ec24b',
    },
    'moltbook': {
        'note': 'Active Moltbook agent',
        'apiKey': 'moltbook_sk_b7NcmWpHjoProzNe1IgzkcFhALp0j4x1',
        'agentId': 'eb672e88-d2d2-40a3-998a-b02ca9120757',
        'name': 'yaqeen_manadger',
        'karma': 7
    },
    'owner_wallet': '0x401B7D82CF68CC8C6b2bFffc921B62e97F314E6c'
}
with open(r'C:\Users\manadger\Desktop\moltbook-app\memory\credentials_active.json', 'w') as f:
    json.dump(creds, f, indent=2)
print('  Credentials saved to credentials_active.json')
