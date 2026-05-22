import requests

# Check trading SDK source
r = requests.get('https://api.github.com/repos/cowprotocol/cow-sdk/contents/packages/trading/src', headers={'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'Python'}, timeout=10)
if r.status_code == 200:
    for item in r.json():
        print(f'  {item["name"]}')
        if item['type'] == 'dir':
            r2 = requests.get(item['url'], headers={'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'Python'}, timeout=10)
            if r2.status_code == 200:
                for sub in r2.json():
                    print(f'    {sub["name"]}')
else:
    print(f'Status: {r.status_code}')
