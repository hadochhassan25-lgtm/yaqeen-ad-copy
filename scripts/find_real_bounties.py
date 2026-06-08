import urllib.request, json, re, os

token = os.environ.get('GITHUB_TOKEN', '')
headers = {
    'Authorization': 'token ' + token,
    'Accept': 'application/vnd.github.v3+json',
    'User-Agent': 'hadochhassan25-lgtm'
}

q = 'label:bounty+language:python+state:open&sort=updated&order=desc&per_page=100'
url = 'https://api.github.com/search/issues?q=' + q
r = urllib.request.Request(url, headers=headers)
resp = urllib.request.urlopen(r, timeout=15)
data = json.loads(resp.read())
print('Total:', data['total_count'], '\n')

real_bounties = []
for item in data['items']:
    repo_url = item['repository_url']
    org = repo_url.split('/')[-2]
    repo = repo_url.split('/')[-1]
    title = item['title']
    body = (item.get('body') or '')[:2000]
    html_url = item['html_url']
    labels = [l['name'] for l in item['labels']]
    
    # Skip known crypto/token repos
    skip_orgs = ['scottcjn', 'rustchain', 'crypt', 'token']
    if any(s in org.lower() for s in skip_orgs):
        continue
    if 'RTC' in body or 'rustchain' in body.lower():
        continue
    
    # Find dollar amounts
    amounts = re.findall(r'\$[0-9,]+', body)
    has_real_money = len(amounts) > 0
    
    if has_real_money:
        print(f'--- {org}/{repo} ---')
        print(f'Title: {title}')
        print(f'Amounts: {amounts}')
        print(f'Labels: {labels}')
        print(f'URL: {html_url}')
        print()

print('=== Summary of real-money bounties found ===')
