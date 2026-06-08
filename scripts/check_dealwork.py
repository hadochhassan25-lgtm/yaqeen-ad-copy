"""Check dealwork wallet and browse jobs"""
import urllib.request, json, os
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.environ.get('DEALWORK_API_KEY', '')
headers = {'Authorization': 'Bearer ' + API_KEY, 'Content-Type': 'application/json', 'User-Agent': 'yaqeen-bot'}

def req(url, data=None, method='GET'):
    body = json.dumps(data).encode() if data else None
    r = urllib.request.Request(url, data=body, headers=headers, method=method)
    return json.loads(urllib.request.urlopen(r, timeout=15).read())

print('=== WALLET ===')
try:
    wallet = req('https://dealwork.ai/api/v1/wallet/balance')
    print(json.dumps(wallet, indent=2))
except Exception as e:
    print(f"Wallet error: {e}")

print()
print('=== AVAILABLE JOBS (first 10) ===')
try:
    jobs = req('https://dealwork.ai/api/v1/jobs?per_page=10&sort=newest')
    for j in jobs.get('data', []):
        desc_short = j['description'][:100].replace('\n', ' ')
        print(f"[{j['category']}] {j['title']}")
        print(f"  Budget: ${j.get('budgetMin','?')} - ${j.get('budgetMax','?')} | Mode: {j.get('jobMode','?')} | Status: {j['status']}")
        print(f"  Worker type: {j.get('eligibleWorkerTypes','any')}")
        print(f"  ID: {j['id']}")
        print()
except Exception as e:
    print(f"Jobs error: {e}")

print('=== MY CONTRACTS (worker) ===')
try:
    contracts = req('https://dealwork.ai/api/v1/contracts?role=worker&per_page=10')
    for c in contracts.get('data', []):
        print(f"[{c['state']}] {c.get('job',{}).get('title','?')} | ${c.get('amount','?')}")
    if not contracts.get('data'):
        print("No worker contracts")
except Exception as e:
    print(f"Worker contracts error: {e}")

print()
print('=== MY BIDS ===')
try:
    bids = req('https://dealwork.ai/api/v1/bids/mine?per_page=10')
    for b in bids.get('data', []):
        print(f"[{b['status']}] {b.get('jobTitle','?')} | ${b.get('proposedAmount','?')}")
    if not bids.get('data'):
        print("No bids")
except Exception as e:
    print(f"Bids error: {e}")
