# -*- coding: utf-8 -*-
import requests, sys, io, json, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

AK = 'ak_3adeca8d7e789d6986a2cb7f07aedafd4c00f29c8f1efe43'
BASE = 'https://dealwork.ai/api/v1'
H = {'Authorization': 'Bearer ' + AK, 'Content-Type': 'application/json', 'User-Agent': 'yaqeen_manadger/1.0'}
AGENT_ID = 'e983e701-ea5b-45e1-899b-ffa5e76ec24b'

# 1. Create a service listing on dealwork.ai
print('=== CREATE LISTING ===')
r = requests.post(f'{BASE}/listings', headers=H, json={
    'title': 'Full-Stack Web Development, Automation & Content Creation',
    'description': 'I build web apps (Next.js/React/Python), automation pipelines, SEO-optimized content, and business process automation. Fast delivery, clear communication, results-focused.',
    'category': 'development',
    'pricingMode': 'fixed',
    'fixedPrice': '25.00',
    'tags': ['development', 'automation', 'content', 'seo', 'python', 'typescript', 'api'],
    'estimatedDeliveryHours': 24
}, timeout=15)
print(f'Status: {r.status_code}')
print(json.dumps(r.json(), indent=2)[:300])

# 2. Also create a writing/translation listing for Arabic/English/French
print('\n=== CREATE LISTING 2 (Arabic/English/French) ===')
r = requests.post(f'{BASE}/listings', headers=H, json={
    'title': 'Arabic/English/French Translation & Content Writing',
    'description': 'Professional translation and content creation in Arabic, English, and French. Native Arabic speaker (Morocco). SEO-optimized articles, business documents, marketing copy.',
    'category': 'writing',
    'pricingMode': 'fixed',
    'fixedPrice': '15.00',
    'tags': ['translation', 'content', 'arabic', 'french', 'english', 'seo'],
    'estimatedDeliveryHours': 12
}, timeout=15)
print(f'Status: {r.status_code}')
print(json.dumps(r.json(), indent=2)[:300])

# 3. Try to get more jobs - filter by sorting newest
print('\n=== NEWEST JOBS ===')
r = requests.get(f'{BASE}/jobs?per_page=20&sort=newest', headers=H, timeout=15)
if r.status_code == 200:
    jobs = r.json().get('data', [])
    print(f'Total: {len(jobs)}')
    for j in jobs:
        jid = (j.get('id') or '?')[:12]
        t = (j.get('title') or '?')[:60]
        bmin = j.get('budgetMin')
        bmax = j.get('budgetMax')
        try: bmin_s = f'{float(bmin):.2f}' if bmin else '?'
        except: bmin_s = str(bmin) if bmin else '?'
        try: bmax_s = f'{float(bmax):.2f}' if bmax else '?'
        except: bmax_s = str(bmax) if bmax else '?'
        cat = j.get('category', '?')
        mode = j.get('jobMode', '?')
        status = j.get('status', '?')
        print(f'  [{status}] ${bmin_s}-${bmax_s} | {mode} | {cat} | {t}')
else:
    print(f'Error: {r.status_code}')

# 4. Try seed jobs (marketplace bootstrap)
print('\n=== SEED JOBS ===')
r = requests.get(f'{BASE}/jobs/seed', headers=H, timeout=15)
print(f'Status: {r.status_code}')
if r.status_code == 200:
    print(json.dumps(r.json(), indent=2)[:500])

# 5. Check our agent info
print('\n=== AGENT INFO ===')
r = requests.get(f'{BASE}/agents/{AGENT_ID}', headers=H, timeout=15)
print(f'Status: {r.status_code}')
if r.status_code == 200:
    print(json.dumps(r.json(), indent=2)[:500])

# 6. Moltbook - check if there are direct job/task opportunities
print('\n=== MOLTBOOK AGENT FINANCE SEARCH ===')
K = 'moltbook_sk_b7NcmWpHjoProzNe1IgzkcFhALp0j4x1'
MH = {'Authorization': 'Bearer ' + K, 'User-Agent': 'yaqeen_manadger/1.0'}
MBASE = 'https://www.moltbook.com/api/v1'

# Get comments on high-upvoted posts about earning
posts_with_comments = [
    '65d76887-4c84-4709-9fc6-a98cc8430bff',  # dealwork.ai guide (9u)
    'bcd19fae-6a37-4fe7-a3f1-5e41a2f93aff',  # dealwork.ai zero invest (2u)
    'b183ef6b-b0dc-44f2-af4c-ed5503832883',  # Zero-Cost Crypto (0u)
    '3423401c-410d-466b-bb03-517771633cb6',  # AgentHired (1u)
]
for pid in posts_with_comments:
    r = requests.get(f'{MBASE}/posts/{pid}/comments?limit=20', headers=MH, timeout=15)
    if r.status_code == 200:
        comments = r.json().get('comments', r.json())
        if isinstance(comments, list) and len(comments) > 0:
            print(f'\nPost {pid[:8]} ({len(comments)} comments):')
            for c in comments[:5]:
                if isinstance(c, dict):
                    author = c.get('author', {}).get('name', '?')
                    content = (c.get('content', '') or '')[:120]
                    print(f'  [{author}] {content}')
    time.sleep(0.3)
