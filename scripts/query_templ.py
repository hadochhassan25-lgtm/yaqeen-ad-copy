# -*- coding: utf-8 -*-
import requests, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Query Templ subgraph for top communities
r = requests.post('https://subgraph.templ.fun', json={
    'query': '{ Templ(limit: 15, order_by: { memberCount: desc }) { id address name slug memberCount tokenSymbol baseEntryFee entryFee chainId } }'
}, timeout=15)
if r.status_code == 200:
    data = r.json()
    templs = data.get('data', {}).get('Templ', [])
    print(f'Templ communities found: {len(templs)}')
    for t in templs:
        print(f'  {t["name"]} (/{t["slug"]}) | {t["memberCount"]} members | fee: {t.get("entryFee","?")} {t.get("tokenSymbol","?")} | {t["address"][:18]}...')
else:
    print(f'Error: {r.status_code}')
    print(r.text[:500])
