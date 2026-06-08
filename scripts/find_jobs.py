"""Find more jobs on dealwork and bid"""
import urllib.request, json, os, time
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.environ.get('DEALWORK_API_KEY', '')
headers = {'Authorization': 'Bearer ' + API_KEY, 'Content-Type': 'application/json', 'User-Agent': 'yaqeen-bot'}

def req(url, data=None, method='GET'):
    body = json.dumps(data).encode() if data else None
    r = urllib.request.Request(url, data=body, headers=headers, method=method)
    return json.loads(urllib.request.urlopen(r, timeout=15).read())

# Get all jobs across categories
print('=== ALL AVAILABLE JOBS ===')
for page in [1, 2]:
    jobs = req(f'https://dealwork.ai/api/v1/jobs?per_page=20&sort=newest&page={page}')
    print(f"\n--- Page {page} ({len(jobs.get('data',[]))} jobs) ---")
    for j in jobs.get('data', []):
        desc = (j.get('description','') or '')[:80].replace('\n',' ')
        tags = j.get('tags', [])
        print(f"[{j['status']}] [{j['category']}] {j['title']}")
        print(f"  ${j.get('budgetMin','?')} - ${j.get('budgetMax','?')} | {j.get('eligibleWorkerTypes','?')} | {j.get('jobMode','?')}")
        print(f"  Tags: {tags[:4]}")
        print(f"  ID: {j['id']}")
        print()

print('=== JOBS I CAN DO RIGHT NOW ===')
# Filter for ai_only or any + Python/research/writing categories
jobs = req('https://dealwork.ai/api/v1/jobs?per_page=50&sort=newest')
count = 0
for j in jobs.get('data', []):
    wt = j.get('eligibleWorkerTypes', 'any')
    cat = j.get('category', '')
    title = j.get('title', '')
    desc = j.get('description', '') or ''
    if wt in ['ai_only', 'any'] and j['status'] in ['bidding', 'open']:
        # Check if it matches our skills
        keywords = ['python', 'script', 'code', 'research', 'write', 'content', 'linkedin', 'post', 'data', 'analysis']
        if any(k in (title + desc).lower() for k in keywords):
            count += 1
            print(f"{count}. [{cat}] {title}")
            print(f"   ${j.get('budgetMin','?')} - ${j.get('budgetMax','?')} | Workers: {wt}")
            print(f"   ID: {j['id']}")
            print()

if count == 0:
    print("No immediately matching jobs found")
    # Just show all open/bidding jobs
    print("\nAll open/bidding jobs:")
    for j in jobs.get('data', []):
        if j['status'] in ['bidding', 'open']:
            print(f"[{j['category']}] {j['title'][:50]} | ${j.get('budgetMin','?')}-${j.get('budgetMax','?')} | {j.get('eligibleWorkerTypes','?')}")
            print(f"  ID: {j['id']}")
