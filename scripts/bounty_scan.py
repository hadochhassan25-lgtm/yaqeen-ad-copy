"""Fast bounty scan - find bounties we can solve RIGHT NOW"""
import urllib.request, json, re, sys

GH_TOKEN = os.environ.get('GITHUB_TOKEN', '')
headers = {'Accept': 'application/vnd.github.v3+json', 'Authorization': f'token {GH_TOKEN}', 'User-Agent': 'yaqeen-bot'}

def req(url):
    r = urllib.request.Request(url, headers=headers)
    return json.loads(urllib.request.urlopen(r, timeout=10).read())

print("=== ORBITER (bonsai) - HONEYPOT ===")
try:
    data = req('https://api.github.com/repos/primeintellect-ai/orbiter/issues?labels=bounty&state=open&per_page=10')
    for item in data[:5]:
        labels = [l['name'] for l in item['labels']]
        print(f"  [{', '.join(labels[:3])}] {item['title'][:60]}")
        print(f"    {item['html_url']}")
except Exception as e:
    print(f"  FAIL: {e}")

print("\n=== PYTHON BOUNTIES (hacktoberfest + good-first-issue) ===")
try:
    data = req('https://api.github.com/search/issues?q=hacktoberfest+label:bounty+state:open+language:python&sort=created&per_page=5')
    for item in data.get('items', [])[:5]:
        labels = [l['name'] for l in item['labels']]
        print(f"  [{item['repository_url'].split('/')[-1]}] {item['title'][:60]}")
        print(f"    {item['html_url']} | labels: {', '.join(labels[:3])}")
except Exception as e:
    print(f"  FAIL: {e}")

print("\n=== OPIR QUICK SCAN ===")
try:
    data = req('https://api.opire.dev/api/v1/bounties?limit=20&sort=newest')
    for b in data.get('bounties', [])[:10]:
        langs = b.get('languages', [])
        amount = b.get('value', {}).get('amount', '?')
        print(f"  ${amount} | {', '.join(langs[:2])} | {b.get('title', '?')[:50]}")
except Exception as e:
    print(f"  FAIL: {e}")
    print("  (Opire API endpoint may differ)")

print("\n=== RECOMMENDED NEXT ACTIONS ===")
print("  1. Ghostwriter: send offer to 3 Moroccan companies (client-ready)")
print("  2. BountyBot: open browser -> https://bountybot.com -> filter Python")
print("  3. PR #16: check for maintainer comments daily")
print("  4. Opire: check new bounties at https://opire.dev")
