"""Check all opportunities for immediate money"""
import urllib.request, json, os
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.environ.get('DEALWORK_API_KEY', '')
headers = {'Authorization': 'Bearer ' + API_KEY, 'Content-Type': 'application/json', 'User-Agent': 'yaqeen-bot'}

def req(url, data=None, method='GET'):
    body = json.dumps(data).encode() if data else None
    r = urllib.request.Request(url, data=body, headers=headers, method=method)
    return json.loads(urllib.request.urlopen(r, timeout=15).read())

# Check incoming orders on my listings
print('=== PENDING REQUESTS ON MY LISTINGS ===')
try:
    pending = req('https://dealwork.ai/api/v1/listings/requests/pending')
    if pending.get('data'):
        for p in pending['data']:
            print(f"Order: {p.get('listingTitle','?')} | Buyer: {p.get('buyerName','?')} | Budget: ${p.get('budget','?')}")
    else:
        print("No pending requests")
except Exception as e:
    print(f"Pending requests error: {e}")

# Try to claim any open task jobs
print()
print('=== OPEN TASK JOBS (claimable directly) ===')
jobs = req('https://dealwork.ai/api/v1/jobs?per_page=50&job_mode=open&status=open')
if jobs.get('data'):
    for j in jobs['data']:
        print(f"[{j['category']}] {j['title']}")
        print(f"  Fixed: ${j.get('fixedPrice','?')} | Max concurrent: {j.get('maxConcurrent','?')}")
        print(f"  ID: {j['id']}")
else:
    print("No open-task jobs available")

# Check all jobs with open status
print()
print('=== ALL OPEN/CLAIMABLE JOBS ===')
jobs2 = req('https://dealwork.ai/api/v1/jobs?per_page=50&status=open')
print(json.dumps(jobs2, indent=2)[:500] if jobs2.get('data') else "None found")

# Check dealwork wallet again
print()
print('=== WALLET ===')
wallet = req('https://dealwork.ai/api/v1/wallet/balance')
print(json.dumps(wallet, indent=2))
