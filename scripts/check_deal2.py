# -*- coding: utf-8 -*-
import requests, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

AK = 'ak_2ed3929ca7ac469cde1f8d920cd0f5e8c3bdb098f5e4ef8b'
DW = 'https://dealwork.ai/api/v1'
H = {'Authorization': 'Bearer ' + AK, 'Content-Type': 'application/json', 'User-Agent': 'yaqeen_manadger/1.0'}

# Check bid status
r = requests.get(DW + '/bids/mine?per_page=5', headers=H, timeout=15)
if r.status_code == 200:
    bids = r.json().get('data', [])
    for b in bids:
        print('Bid: $' + str(b.get('proposedAmount', '?')) + ' | ' + str(b.get('status', '?')) + ' | ' + str(b.get('job', {}).get('title', '?')))
else:
    print('GET /bids/mine: ' + str(r.status_code))

# Check profile
r = requests.get(DW + '/profile', headers=H, timeout=15)
if r.status_code == 200:
    p = r.json()
    if isinstance(p, dict):
        wallet = p.get('wallet', {})
        print('Balance: ' + str(wallet.get('balance', '?')))
        print('Trust tier: ' + str(p.get('trustTier', '?')))
else:
    print('GET /profile: ' + str(r.status_code))

# Check my listings
r = requests.get(DW + '/listings/me', headers=H, timeout=15)
if r.status_code == 200:
    listings = r.json().get('data', [])
    print('Active listings: ' + str(len(listings)))
    for L in listings:
        print('  ' + str(L.get('title', '?')) + ' | $' + str(L.get('price', '?')) + ' | orders: ' + str(L.get('ordersCount', 0)))
else:
    print('GET /listings/me: ' + str(r.status_code))

# Look for new jobs
r = requests.get(DW + '/jobs?per_page=10&sort=latest', headers=H, timeout=15)
if r.status_code == 200:
    jobs = r.json().get('data', [])
    print('New jobs: ' + str(len(jobs)))
    for j in jobs[:5]:
        budget = j.get('budget', {})
        max_budget = budget.get('max', '?') if isinstance(budget, dict) else '?'
        print('  ' + str(j.get('title', '?')) + ' | $' + str(max_budget) + ' | bids: ' + str(j.get('bidsCount', 0)))
else:
    print('GET /jobs: ' + str(r.status_code))
