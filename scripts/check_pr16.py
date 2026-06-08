import urllib.request, json, os

token = os.environ.get('GITHUB_TOKEN', '')
headers = {
    'Authorization': 'token ' + token,
    'Accept': 'application/vnd.github.v3+json',
    'User-Agent': 'hadochhassan25-lgtm'
}

# Check PR #16 status
r = urllib.request.Request(
    'https://api.github.com/repos/aLexzzz430/Cognitive-OS/pulls/16',
    headers=headers
)
resp = urllib.request.urlopen(r, timeout=15)
data = json.loads(resp.read())
print('PR #16 Status:')
for k in ['state','draft','mergeable','commits','comments','review_comments','created_at','updated_at']:
    print(f'  {k}: {data.get(k)}')
print('  URL:', data['html_url'])

# Check the comments
r2 = urllib.request.Request(
    'https://api.github.com/repos/aLexzzz430/Cognitive-OS/issues/16/comments',
    headers=headers
)
resp2 = urllib.request.urlopen(r2, timeout=15)
comments = json.loads(resp2.read())
print(f'\nComments ({len(comments)}):')
for c in comments:
    print(f'  [{c["user"]["login"]}] {c["body"][:300]}')
    print()
