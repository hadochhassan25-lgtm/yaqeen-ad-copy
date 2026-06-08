"""Find open unclaimed Opire bounties we can solve"""
import urllib.request, json

url = 'https://api.opire.dev/rewards'
r = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=10)
data = json.loads(r.read().decode())

print('=== OPEN / UNCLAIMED BOUNTIES ===')
found = 0
for item in data:
    claimers = item.get('claimerUsers', [])
    tryers = item.get('tryingUsers', [])
    if not claimers:
        found += 1
        langs = item.get('programmingLanguages', [])
        price = item.get('pendingPrice', '?')
        org = item.get('organization', '?')
        proj = item.get('project', '?')
        print(f'--- Bounty #{found} ---')
        print(f'Title: {item["title"][:80]}')
        print(f'URL: {item["url"]}')
        print(f'Price: ${price}')
        print(f'Languages: {langs}')
        print(f'Project: {org}/{proj}')
        print(f'Trying: {len(tryers)} users')
        print()

if found == 0:
    print('No open bounties found')

print(f'\nTotal bounties: {len(data)}')
print(f'Claimed: {len(data) - found}')
print(f'Open: {found}')
