import requests, os
token = os.environ.get('GITHUB_TOKEN', '')
r = requests.get('https://models.inference.ai.azure.com/models',
    headers={'Authorization': f'Bearer {token}'}, timeout=15)
print(f'HTTP {r.status_code}')
if r.status_code == 200:
    data = r.json()
    if isinstance(data, list):
        for m in data:
            print(f'  {m.get("id", "?")}')
    elif isinstance(data, dict):
        for m in data.get('data', []):
            print(f'  {m.get("id", "?")}')
else:
    print(r.text[:500])
