# -*- coding: utf-8 -*-
import requests, sys, io, json, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

AK = 'ak_3adeca8d7e789d6986a2cb7f07aedafd4c00f29c8f1efe43'
H = {'Authorization': 'Bearer ' + AK, 'Content-Type': 'application/json', 'User-Agent': 'yaqeen_manadger/1.0'}
BASE = 'https://dealwork.ai/api/v1'
AID = 'e983e701-ea5b-45e1-899b-ffa5e76ec24b'

print('=== 1. BID STATUS ===')
r = requests.get(f'{BASE}/bids/mine?per_page=20', headers=H, timeout=15)
if r.status_code == 200:
    bids = r.json().get('data', [])
    if bids:
        for b in bids:
            print(f'  Job: {b.get("jobId","?")}')
            print(f'  Amount: ${b.get("proposedAmount","?")}')
            print(f'  Status: {b.get("status","?")}')
            print(f'  Created: {b.get("createdAt","?")}')
            print(f'  Full: {json.dumps(b, indent=2)}')
    else:
        print('  No bids found')

print('\n=== 2. CONTRACTS ===')
for role in ['worker', 'buyer']:
    r = requests.get(f'{BASE}/contracts?role={role}&per_page=20', headers=H, timeout=15)
    if r.status_code == 200:
        data = r.json().get('data', [])
        print(f'  {role}: {len(data)} contracts')
        if data:
            for c in data:
                print(f'    {json.dumps(c, indent=2)}')
    else:
        print(f'  {role} error: {r.status_code}')

print('\n=== 3. INCOMING ORDERS / REQUESTS ===')
r = requests.get(f'{BASE}/listings/requests/pending', headers=H, timeout=15)
if r.status_code == 200:
    data = r.json().get('data', [])
    print(f'  Pending requests: {len(data)}')
    if data:
        for d in data:
            print(f'    {json.dumps(d, indent=2)}')
else:
    print(f'  Error: {r.status_code}')

print('\n=== 4. MY LISTINGS ===')
r = requests.get(f'{BASE}/listings/mine', headers=H, timeout=15)
if r.status_code == 200:
    listings = r.json().get('data', [])
    print(f'  Listings: {len(listings)}')
    for l in listings:
        print(f'  - {l.get("title","?")} (${l.get("fixedPrice","?")}) [ID: {l.get("id","?")[:12]}]')
else:
    print(f'  Error: {r.status_code}')

print('\n=== 5. WALLET ===')
r = requests.get(f'{BASE}/wallet/balance', headers=H, timeout=15)
if r.status_code == 200:
    print(f'  {json.dumps(r.json(), indent=2)}')
else:
    print(f'  Error: {r.status_code}')

print('\n=== 6. NEW JOBS AVAILABLE ===')
r = requests.get(f'{BASE}/jobs?per_page=20&sort=newest', headers=H, timeout=15)
if r.status_code == 200:
    jobs = r.json().get('data', [])
    print(f'  Open jobs: {len(jobs)}')
    for j in jobs:
        jid = j.get('id','?')[:12]
        t = (j.get('title') or '?')[:60]
        bmin = j.get('budgetMin') or '?'
        bmax = j.get('budgetMax') or '?'
        print(f'  [{jid}] ${bmin}-${bmax} | {t}')
else:
    print(f'  Error: {r.status_code}')

print('\n=== 7. AGENT PROFILE ===')
r = requests.get(f'{BASE}/agents/{AID}', headers=H, timeout=15)
if r.status_code == 200:
    d = r.json().get('data', r.json())
    for k in ['displayName','trustTierLevel','trustScore','totalEarned','walletBalance','activeContractCount','skillVersion','moltbookKarma','isSuspended','reviewStats']:
        val = d.get(k, '?')
        print(f'  {k}: {val}')

print('\n=== 8. MOLTBOOK CHECK ===')
MK = 'moltbook_sk_b7NcmWpHjoProzNe1IgzkcFhALp0j4x1'
MH = {'Authorization': 'Bearer ' + MK, 'User-Agent': 'yaqeen_manadger/1.0'}
MBASE = 'https://www.moltbook.com/api/v1'
r = requests.get(f'{MBASE}/agents/me', headers=MH, timeout=15)
if r.status_code == 200:
    me = r.json().get('agent', r.json())
    print(f'  Karma: {me.get("karma")}')
    print(f'  Posts: {me.get("posts_count")}')
    print(f'  Comments: {me.get("comments_count")}')
    # Check notifications
    r2 = requests.get(f'{MBASE}/notifications?limit=10', headers=MH, timeout=15)
    if r2.status_code == 200:
        notifs = r2.json().get('notifications', r2.json())
        print(f'  Notifications: {json.dumps(notifs, indent=2)[:500]}')
    else:
        print(f'  Notifs error: {r2.status_code}')
