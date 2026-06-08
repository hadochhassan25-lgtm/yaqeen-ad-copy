import urllib.request, json, os

token = os.environ.get('GITHUB_TOKEN', '')
headers = {
    'Authorization': 'token ' + token,
    'Accept': 'application/vnd.github.v3+json',
    'User-Agent': 'hadochhassan25-lgtm'
}

# Check PR #16 files
r = urllib.request.Request(
    'https://api.github.com/repos/aLexzzz430/Cognitive-OS/pulls/16/files',
    headers=headers
)
resp = urllib.request.urlopen(r, timeout=15)
files = json.loads(resp.read())
print('PR #16 has ' + str(len(files)) + ' files:')
for f in files[:30]:
    status = f['status']
    adds = f['additions']
    dels = f['deletions']
    print('  [' + status + '] +' + str(adds) + '/-' + str(dels) + ' ' + f['filename'])

total_adds = sum(f['additions'] for f in files)
total_dels = sum(f['deletions'] for f in files)
print()
print('Total: +' + str(total_adds) + '/-' + str(total_dels) + ' lines')
