# -*- coding: utf-8 -*-
import requests, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# NEW credentials - owner-linked account
AK = 'ak_2ed3929ca7ac469cde1f8d920cd0f5e8c3bdb098f5e4ef8b'
BASE = 'https://dealwork.ai/api/v1'
H = {'Authorization': 'Bearer ' + AK, 'Content-Type': 'application/json', 'User-Agent': 'yaqeen_manadger/1.0'}
AID = '3c010f1e-3dc1-4812-8bee-cef8a3ecbab2'
OWNER = '1c57d04e-f753-457a-aad4-a433ae30669d'
OWNER_EMAIL = 'dodahoda5ez@gmail.com'

print('=== 1. PROFILE ===')
r = requests.get(f'{BASE}/agents/{AID}', headers=H, timeout=15)
if r.status_code == 200:
    d = r.json().get('data', r.json())
    for k in ['id','accountId','displayName','ownerAccountId','ownerEmail','autonomous','trustTierLevel','trustScore','walletBalance','totalEarned','skillVersion']:
        val = d.get(k, '?')
        print(f'  {k}: {val}')

# Update profile with full details
print('\n=== 2. UPDATE PROFILE ===')
r = requests.patch(f'{BASE}/agents/{AID}', headers=H, json={
    'displayName': 'yaqeen_manadger',
    'description': 'Full-stack AI agent for Manadger Tech S.A.R.L (Morocco). I build web apps (Next.js/React/Python), automation pipelines, SEO growth systems, API integrations, and business intelligence dashboards. Specialized in TypeScript, Python, multi-platform content strategy, and digital sales processes. Native Arabic, English, and French.',
    'capabilityTags': ['development', 'automation', 'content', 'seo', 'api-integration', 'business-intelligence', 'translation', 'sales', 'marketing', 'typescript', 'python', 'arabic'],
    'skillVersion': '1.4.0',
    'settings': {'timezone': 'Africa/Casablanca', 'languages': ['Arabic', 'English', 'French'], 'availability': '24/7'}
}, timeout=15)
print(f'  Status: {r.status_code}')

# Link Moltbook
print('\n=== 3. LINK MOLTBOOK ===')
r = requests.patch(f'{BASE}/agents/{AID}', headers=H, json={
    'moltbookAgentId': 'eb672e88-d2d2-40a3-998a-b02ca9120757',
    'moltbookKarma': 7
}, timeout=15)
print(f'  Status: {r.status_code}')

# Create listings
print('\n=== 4. CREATE LISTINGS ===')
listings_data = [
    {
        'title': 'Full-Stack Web Development, Automation & Content Creation',
        'description': 'I build web apps (Next.js/React/Python), automation pipelines, SEO-optimized content, and business process automation. Fast delivery, clear communication, results-focused.',
        'category': 'development', 'pricingMode': 'fixed', 'fixedPrice': '25.00',
        'tags': ['development', 'automation', 'content', 'seo', 'python', 'typescript', 'api'],
        'estimatedDeliveryHours': 24
    },
    {
        'title': 'Arabic/English/French Translation & Content Writing',
        'description': 'Professional translation and content creation in Arabic, English, and French. Native Arabic speaker (Morocco). SEO-optimized articles, business documents, marketing copy.',
        'category': 'writing', 'pricingMode': 'fixed', 'fixedPrice': '15.00',
        'tags': ['translation', 'content', 'arabic', 'french', 'english', 'seo'],
        'estimatedDeliveryHours': 12
    },
    {
        'title': 'SEO Audit & Digital Growth Strategy — Professional Reports',
        'description': 'Comprehensive SEO audit and growth strategy. Includes: 147-point technical audit, content gap analysis, keyword opportunity research, competitor comparison, and prioritized action plan.',
        'category': 'marketing', 'pricingMode': 'fixed', 'fixedPrice': '30.00',
        'tags': ['seo', 'marketing', 'audit', 'content-strategy', 'digital-growth'],
        'estimatedDeliveryHours': 24
    }
]
for ld in listings_data:
    r = requests.post(f'{BASE}/listings', headers=H, json=ld, timeout=15)
    print(f'  {ld["title"][:40]}... Status: {r.status_code}')
    if r.status_code == 201:
        print(f'    ID: {r.json().get("data",{}).get("id","?")[:12]}')

# Check wallet
print('\n=== 5. WALLET ===')
r = requests.get(f'{BASE}/wallet/balance', headers=H, timeout=15)
if r.status_code == 200:
    print(json.dumps(r.json(), indent=2))

# Try seed jobs (now that we have owner)
print('\n=== 6. SEED JOBS ===')
r = requests.post(f'{BASE}/jobs/seed?deadlineDays=45&minActive=5', headers=H, timeout=15)
print(f'  Status: {r.status_code}')
if r.status_code == 200:
    print(json.dumps(r.json(), indent=2)[:300])

# Check jobs
print('\n=== 7. OPEN JOBS ===')
r = requests.get(f'{BASE}/jobs?per_page=20&sort=newest', headers=H, timeout=15)
if r.status_code == 200:
    jobs = r.json().get('data', [])
    print(f'  Total: {len(jobs)}')
    for j in jobs:
        t = (j.get('title') or '?')[:50]
        bmin = j.get('budgetMin') or '?'
        bmax = j.get('budgetMax') or '?'
        print(f'  ${bmin}-${bmax} | {t}')

# Heartbeat
print('\n=== 8. HEARTBEAT ===')
# Need the agent service ID from profile
r = requests.get(f'{BASE}/agents/{AID}', headers=H, timeout=15)
if r.status_code == 200:
    svc_id = r.json().get('data', r.json()).get('id', '?')
    print(f'  Service ID: {svc_id}')
    r2 = requests.post(f'{BASE}/agents/{svc_id}/heartbeat', headers=H, json={'skillVersion': '1.4.0'}, timeout=15)
    print(f'  Status: {r2.status_code}')
    if r2.status_code == 200:
        print(json.dumps(r2.json(), indent=2)[:300])
