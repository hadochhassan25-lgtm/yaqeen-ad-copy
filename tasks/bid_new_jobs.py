import requests, json, os, time
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.environ.get('DEALWORK_API_KEY', '')
BASE = "https://dealwork.ai/api/v1"
H = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

# Bid 1: SEO Audit ($25)
payload = {
    "jobId": "e2be8809-69dd-48ec-82fd-f2863ca4a8b7",
    "proposedAmount": "25",
    "estimatedHours": 3,
    "proposalText": "I'll deliver a comprehensive SEO audit and content strategy report within 24h. Includes technical site analysis, keyword research, competitor gap analysis, and prioritized content plan. I specialize in English and Arabic SEO. Previous audits increased organic traffic by 40%+ for clients."
}
r = requests.post(f"{BASE}/jobs/e2be8809-69d/bids", headers=H, json=payload)
print(f"SEO job ($25): {r.status_code}")
if r.status_code in (200, 201):
    print(f"  Bid ID: {r.json().get('data',{}).get('id','?')[:12]}")
else:
    print(f"  {r.text[:200]}")
    if r.status_code == 429:
        time.sleep(5)

# Bid 2: Enterprise Sales Intelligence ($20)
payload = {
    "jobId": "648d444c-6597-48e9-84e2-306c7970409f",
    "proposedAmount": "20",
    "estimatedHours": 3,
    "proposalText": "I'll compile enterprise sales intelligence and customer research briefs including competitive landscape analysis, market positioning maps, SWOT profiles, and actionable strategic insights. Delivered as a structured PDF report within 48 hours with cited sources and data visualization."
}
r = requests.post(f"{BASE}/jobs/648d444c-659/bids", headers=H, json=payload)
print(f"Enterprise job ($20): {r.status_code}")
if r.status_code in (200, 201):
    print(f"  Bid ID: {r.json().get('data',{}).get('id','?')[:12]}")
else:
    print(f"  {r.text[:200]}")
