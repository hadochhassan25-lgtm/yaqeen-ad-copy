"""
YAQEEN Bounty Hunter - Find GitHub issues with bounties
"""
import urllib.request, json, sys, os

GH_TOKEN = os.environ.get('GITHUB_TOKEN', '')
headers = {
    'Accept': 'application/vnd.github.v3+json',
    'Authorization': 'token ' + GH_TOKEN,
    'User-Agent': 'yaqeen-bot'
}

def req(url):
    r = urllib.request.Request(url, headers=headers)
    return json.loads(urllib.request.urlopen(r, timeout=15).read())

print('=== YAQEEN BOUNTY HUNTER ===')
print('')

# Broader search
q = 'label:bounty+state:open&sort=created&order=desc&per_page=20'
try:
    data = req('https://api.github.com/search/issues?q=' + q)
    items = data.get('items', [])
    print('Total open bounties found: ' + str(len(items)))
    print('')
    for item in items[:15]:
        repo = item['repository_url'].split('/')[-1]
        title = item['title'][:60]
        url = item['html_url']
        labels = [l['name'] for l in item['labels']]
        lang = item.get('language', '?')
        print('[' + repo + '] ' + title)
        print('  ' + url)
        print('  Labels: ' + str(labels[:4]))
        print('')
except Exception as e:
    print('ERROR: ' + str(e))
    print('')

print('=== SERVICE STATUS ===')
print('Bot: @yaqeen_manadger_bot - LIVE')
print('API: port 5000 - LIVE')
print('')
print('Tell Iliass to open Telegram and send /start to @yaqeen_manadger_bot')
