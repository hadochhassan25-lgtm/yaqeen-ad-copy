import requests
r = requests.get('https://api.github.com/search/code?q=InsufficientAllowance+repo:cowprotocol/services', headers={'Accept': 'application/vnd.github.v3+json'}, timeout=15)
if r.status_code == 200:
    for item in r.json().get('items', []):
        print(f"{item['path']}:{item['name']}")
        print(f"  URL: {item['html_url']}")
else:
    print('Status:', r.status_code, r.text[:500])
