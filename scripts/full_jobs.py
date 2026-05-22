# -*- coding: utf-8 -*-
import requests, sys, io, json, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

AK = 'ak_3adeca8d7e789d6986a2cb7f07aedafd4c00f29c8f1efe43'
BASE = 'https://dealwork.ai/api/v1'
H = {'Authorization': 'Bearer ' + AK, 'Content-Type': 'application/json', 'User-Agent': 'yaqeen_manadger/1.0'}

# Get all jobs with FULL IDs
r = requests.get(f'{BASE}/jobs?per_page=50', headers=H, timeout=15)
if r.status_code == 200:
    jobs = r.json().get('data', [])
    print(f'Total jobs: {len(jobs)}')
    for j in jobs:
        jid = j.get('id', 'FULL-MISSING')
        t = (j.get('title') or '?')[:50]
        bmin = j.get('budgetMin') or '?'
        bmax = j.get('budgetMax') or '?'
        cat = j.get('category', '?')
        mode = j.get('jobMode', '?')
        print(f'\n  ID: {jid}')
        print(f'  Title: {t}')
        print(f'  Budget: ${bmin} - ${bmax} | {cat} | {mode}')
        
        # Get full job details to find buyer and criteria
        rd = requests.get(f'{BASE}/jobs/{jid}', headers=H, timeout=15)
        if rd.status_code == 200:
            jd = rd.json().get('data', rd.json())
            desc = (jd.get('description') or '')[:200]
            print(f'  Description: {desc}')
            criteria = jd.get('acceptanceCriteria', [])
            if criteria:
                print(f'  Criteria: {len(criteria)} items')
            bids_count = jd.get('bidsCount', jd.get('bid_count', '?')) 
            print(f'  Bids: {bids_count}')
            status = jd.get('status', '?')
            print(f'  Status: {status}')
            
            # If it's an open task, claim it
            if mode == 'open' and status == 'open':
                print(f'  *** OPEN TASK - READY TO CLAIM! ***')
        else:
            print(f'  Detail error: {rd.status_code}')
        time.sleep(0.3)
else:
    print(f'Error: {r.status_code}')

# Check if we can find the salmon burgers job by searching
print('\n\n========== SEARCH FOR SALMON ==========')
r = requests.get(f'{BASE}/jobs?search=salmon&per_page=10', headers=H, timeout=15)
if r.status_code == 200:
    jobs = r.json().get('data', [])
    print(f'Found: {len(jobs)}')
    for j in jobs:
        print(json.dumps(j, indent=2)[:300])
else:
    print(f'Error: {r.status_code}')
