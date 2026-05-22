# -*- coding: utf-8 -*-
import requests, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Query Templ Community details
r = requests.post('https://subgraph.templ.fun', json={
    'query': '''{
      Templ(where: { slug: { _eq: "community" } }, limit: 1) {
        id address name slug memberCount token baseEntryFee entryFee tokenSymbol chainId governance treasury
      }
      Member(where: { templAddress: { _eq: "0x20f39B8b577Fc2dD27f38CD27CBcb1F3c5f09c37" } }, limit: 20) {
        address memberId
      }
      Proposal(where: { templAddress: { _eq: "0x20f39B8b577Fc2dD27f38CD27CBcb1F3c5f09c37" } }, limit: 10) {
        id proposalId proposer description forVotes againstVotes executed votingEndsAt
      }
    }'''
}, timeout=15)
if r.status_code == 200:
    data = r.json().get('data', {})
    templ = data.get('Templ', [{}])[0]
    print('=== TEMPL COMMUNITY ===')
    print(f'Name: {templ.get("name")}')
    print(f'Slug: {templ.get("slug")}')
    print(f'Members: {templ.get("memberCount")}')
    print(f'Entry fee: {templ.get("entryFee")} {templ.get("tokenSymbol","?")}')
    print(f'Token: {templ.get("token")}')
    print(f'Governance: {templ.get("governance")}')
    print(f'Treasury: {templ.get("treasury")}')
    
    print('\n=== MEMBERS ===')
    for m in data.get('Member', []):
        print(f'  #{m["memberId"]}: {m["address"][:18]}...')
    
    print('\n=== PROPOSALS ===')
    for p in data.get('Proposal', []):
        print(f'  #{p["proposalId"]}: {p["description"][:60]} | For:{p["forVotes"]} Against:{p["againstVotes"]} | Executed:{p.get("executed")}')
else:
    print(f'Error: {r.status_code}')
