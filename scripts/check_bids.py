"""Check pending bids and active opportunities"""
import urllib.request, json, os
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.environ.get('DEALWORK_API_KEY', '')
headers = {'Authorization': 'Bearer ' + API_KEY, 'Content-Type': 'application/json', 'User-Agent': 'yaqeen-bot'}

def req(url, data=None, method='GET'):
    body = json.dumps(data).encode() if data else None
    r = urllib.request.Request(url, data=body, headers=headers, method=method)
    return json.loads(urllib.request.urlopen(r, timeout=15).read())

print('=== MY BIDS (detailed) ===')
bids = req('https://dealwork.ai/api/v1/bids/mine?per_page=20')
for b in bids.get('data', []):
    print(f"Job: {b.get('jobTitle','?')}")
    print(f"  Amount: ${b.get('proposedAmount','?')}")
    print(f"  Status: {b.get('status','?')}")
    print(f"  Created: {b.get('createdAt','?')}")
    if b.get('jobId'):
        print(f"  Job ID: {b['jobId']}")
    print()

print('=== JOB DETAILS ===')
# Get the research job
job = req('https://dealwork.ai/api/v1/jobs/c0ef69b8-eed1-4632-af8f-2147750341a9')
print(f"Title: {job.get('title')}")
print(f"Description: {job.get('description','')[:200]}")
print(f"Category: {job.get('category')}")
print(f"Budget: ${job.get('budgetMin','?')} - ${job.get('budgetMax','?')}")
print(f"Worker type: {job.get('eligibleWorkerTypes')}")
print(f"Status: {job.get('status')}")
print(f"Created: {job.get('createdAt')}")
print()

# Check agent heartbeat
print('=== HEARTBEAT ===')
try:
    hb = req('https://dealwork.ai/api/v1/agents/fec238ff-1150-4d72-9d1e-51c8fec8dad0/heartbeat', 
             {'skillVersion': '1.0.0'}, 'POST')
    print(json.dumps(hb, indent=2)[:500])
except Exception as e:
    print(f"Heartbeat error: {e}")
