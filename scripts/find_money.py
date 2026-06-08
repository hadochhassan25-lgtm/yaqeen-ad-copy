"""Find real Python issues we can solve for money"""
import urllib.request, json

GH_TOKEN = os.environ.get('GITHUB_TOKEN', '')
headers = {
    'Accept': 'application/vnd.github.v3+json',
    'Authorization': 'token ' + GH_TOKEN,
    'User-Agent': 'yaqeen-bot'
}

def req(url):
    r = urllib.request.Request(url, headers=headers)
    return json.loads(urllib.request.urlopen(r, timeout=15).read())

queries = [
    'label:sponsor+state:open+language:python&sort=created&per_page=5',
    'help+wanted+bounty+state:open+language:python&sort=created&per_page=5',
    'good+first+issue+bounty+state:open+language:python&sort=updated&per_page=5',
    'python+bounty+funded+state:open&sort=created&per_page=5',
]

for q in queries:
    try:
        data = req('https://api.github.com/search/issues?q=' + q)
        items = data.get('items', [])
        for item in items[:3]:
            repo = item['repository_url'].split('/')[-1]
            print('[' + repo + '] ' + item['title'][:70])
            print('  ' + item['html_url'])
            labels = [l['name'] for l in item['labels']]
            print('  Labels: ' + str(labels[:4]))
            print()
    except Exception as e:
        print('ERROR: ' + str(e))

print('=== SOLUTION ===')
print('The ONLY real money path right now:')
print('1. PR #16 - $3k pending review (waiting)')
print('2. Telegram bot @yaqeen_manadger_bot - LIVE, needs users')
print('3. Ghostwriter service - ready, needs a client')
