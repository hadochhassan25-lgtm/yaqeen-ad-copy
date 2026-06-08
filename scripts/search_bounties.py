import urllib.request, json, os

token = os.environ.get('GITHUB_TOKEN', '')
headers = {
    'Authorization': 'token ' + token,
    'Accept': 'application/vnd.github.v3+json',
    'User-Agent': 'hadochhassan25-lgtm'
}

# Search for Python issues with 'bounty' or '💰' labels
queries = [
    'label:bounty+language:python+state:open',
    'label:💰+language:python+state:open',
    'bounty+in:title+language:python+state:open',
]

for q in queries:
    url = f'https://api.github.com/search/issues?q={q}&sort=updated&order=desc&per_page=10'
    r = urllib.request.Request(url, headers=headers)
    resp = urllib.request.urlopen(r, timeout=15)
    data = json.loads(resp.read())
    print(f'\n=== Query: {q} ===')
    print(f'Total: {data["total_count"]}')
    for i, item in enumerate(data['items'][:10]):
        repo = item['repository_url'].split('/')[-1]
        org = item['repository_url'].split('/')[-2]
        print(f'{i+1}. [{org}/{repo}] {item["title"]}')
        print(f'   {item["html_url"]}')
        # Check if it has a known bounty platform link
        body = item.get('body', '') or ''
        if 'bounty' in body.lower() or 'strike' in body.lower() or 'algora' in body.lower() or 'issuehunt' in body.lower():
            print(f'   *** Bounty platform mentioned in body ***')
        print()
