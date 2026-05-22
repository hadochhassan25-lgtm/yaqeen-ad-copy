import requests
import json

# The CoW Swap UI is at github.com/cowprotocol/cowswap
# Let me look at the order submission logic
r = requests.get('https://api.github.com/repos/cowprotocol/cowswap/contents/src', headers={'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'Python'}, timeout=10)
if r.status_code == 200:
    top_dirs = []
    for item in r.json():
        if item['type'] == 'dir':
            top_dirs.append(item['name'])
    print('Top dirs in cowswap:', json.dumps(top_dirs, indent=2))
    
    # Look for relevant files
    for item in r.json():
        name = item['name'].lower()
        if any(kw in name for kw in ['order', 'trade', 'swap', 'permit', 'approve', 'hook']):
            print(f'  Found: {item["name"]} ({item["type"]})')
elif r.status_code == 404:
    # Try legacy path
    r2 = requests.get('https://api.github.com/repos/cowprotocol/cowswap/contents/src/custom', headers={'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'Python'}, timeout=10)
    if r2.status_code == 200:
        print('custom dir contents:')
        for item in r2.json():
            print(f'  {item["name"]}')
    else:
        print(f'cowswap search: {r.status_code}')
        # Try searching for permit-related endpoint in services repo
        r3 = requests.get('https://raw.githubusercontent.com/cowprotocol/services/main/orderbook/openapi.yml', headers={'User-Agent': 'Python'}, timeout=10)
        if r3.status_code == 200:
            # Look for InsufficientAllowance in the file
            content = r3.text
            idx = content.find('InsufficientAllowance')
            if idx >= 0:
                print('Found InsufficientAllowance in openapi.yml:')
                print(content[max(0,idx-200):idx+500])
            else:
                print('Not found in openapi.yml')
        else:
            print(f'openapi: {r3.status_code}')
            # Try another path for the openapi
            r4 = requests.get('https://api.cow.fi/mainnet/api/v1/openapi.yaml', headers={'User-Agent': 'Python'}, timeout=10)
            print(f'v1 openapi.yaml: {r4.status_code}')
            if r4.status_code == 200:
                print(r4.text[:500])
