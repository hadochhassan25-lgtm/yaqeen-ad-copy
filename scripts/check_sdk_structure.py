import requests

for branch in ['main', 'develop']:
    r = requests.get(f'https://api.github.com/repos/cowprotocol/cow-sdk/contents/packages/order-book/src?ref={branch}', headers={'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'Python'}, timeout=10)
    if r.status_code == 200:
        print(f'=== {branch} ===')
        for item in r.json():
            print(f'  {item["name"]}')
        break
    else:
        print(f'{branch}: {r.status_code}')
