# -*- coding: utf-8 -*-
import requests, sys, io, json, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Dealwork.ai credentials
AK = 'ak_3adeca8d7e789d6986a2cb7f07aedafd4c00f29c8f1efe43'
BASE = 'https://dealwork.ai/api/v1'
H = {'Authorization': 'Bearer ' + AK, 'Content-Type': 'application/json', 'User-Agent': 'yaqeen_manadger/1.0'}
AGENT_ID = 'e983e701-ea5b-45e1-899b-ffa5e76ec24b'

# Get all available jobs with full details
print('=== ALL OPEN JOBS (detailed) ===')
r = requests.get(f'{BASE}/jobs?per_page=50', headers=H, timeout=15)
if r.status_code == 200:
    jobs = r.json().get('data', [])
    print(f'Total jobs: {len(jobs)}\n')
    for j in jobs:
        jid = (j.get('id') or '?')[:12]
        t = ((j.get('title') or '') or '?')[:80]
        bmin = j.get('budgetMin', '?')
        bmax = j.get('budgetMax', '?')
        cat = j.get('category', '?')
        desc = ((j.get('description') or '') or '')[:150]
        status = j.get('status', '?')
        worker_type = j.get('eligibleWorkerTypes', '?')
        mode = j.get('jobMode', '?')
        deadline = (j.get('deadline') or '?')[:10]
        print(f'[{jid}] {status} | ${bmin}-${bmax} | {cat} | {worker_type} | {mode}')
        print(f'  {t}')
        print(f'  {desc}')
        
        # Check if open task (can claim instantly)
        if mode == 'open' and status == 'open':
            print(f'  *** OPEN TASK - CAN CLAIM INSTANTLY! ***')
        print()
else:
    print(f'Error: {r.status_code} {r.text[:200]}')

# Check wallet
print('\n=== WALLET ===')
r = requests.get(f'{BASE}/wallet/balance', headers=H, timeout=15)
if r.status_code == 200:
    print(json.dumps(r.json(), indent=2)[:300])
else:
    print(f'Error: {r.status_code} {r.text[:200]}')

# Check my contracts
print('\n=== MY CONTRACTS ===')
r = requests.get(f'{BASE}/contracts?role=worker&per_page=20', headers=H, timeout=15)
if r.status_code == 200:
    print(json.dumps(r.json(), indent=2)[:500])
else:
    print(f'Error: {r.status_code}')

# Check my bids
print('\n=== MY BIDS ===')
r = requests.get(f'{BASE}/bids/mine?per_page=20', headers=H, timeout=15)
if r.status_code == 200:
    print(json.dumps(r.json(), indent=2)[:500])
else:
    print(f'Error: {r.status_code}')

# Check agent listings
print('\n=== MY LISTINGS ===')
r = requests.get(f'{BASE}/listings/mine', headers=H, timeout=15)
if r.status_code == 200:
    print(json.dumps(r.json(), indent=2)[:300])
else:
    print(f'Error: {r.status_code}')
