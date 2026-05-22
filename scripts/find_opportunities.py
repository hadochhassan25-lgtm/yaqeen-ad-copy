# -*- coding: utf-8 -*-
import requests, sys, io, json, time, uuid
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

K = 'moltbook_sk_b7NcmWpHjoProzNe1IgzkcFhALp0j4x1'
H = {'Authorization': 'Bearer ' + K, 'User-Agent': 'yaqeen_manadger/1.0'}
BASE = 'https://www.moltbook.com/api/v1'

# Try different submolt post endpoints
submolts = ['agentfinance', 'agenteconomy', 'crypto', 'agentcommerce', 'usdc', 'builds', 'agentskills', 'jobs', 'trading', 'security', 'fomolt', 'openclaw']
for slug in submolts:
    # Try multiple endpoint patterns
    for ep in [f'/submolts/{slug}/posts', f'/m/{slug}/posts', f'/communities/{slug}/posts', f'/submolts/name/{slug}/posts']:
        try:
            r = requests.get(f'{BASE}{ep}?limit=5', headers=H, timeout=10)
            if r.status_code == 200:
                data = r.json()
                if isinstance(data, dict):
                    posts = data.get('posts', data.get('data', []))
                else:
                    posts = data
                if isinstance(posts, list) and len(posts) > 0:
                    print(f'FOUND: {ep} -> {len(posts)} posts')
                    for p in posts[:3]:
                        if isinstance(p, dict):
                            t = (p.get('title', '') or '')[:50]
                            print(f'  {t}')
                    print()
                    break
        except:
            pass

# Check dealwork.ai API
print('\n========== DEALWORK.AI ==========')
try:
    r = requests.get('https://dealwork.ai/api/v1/jobs?per_page=10', timeout=15)
    if r.status_code == 200:
        jobs = r.json().get('data', [])
        print(f'Open jobs: {len(jobs)}')
        for j in jobs[:10]:
            t = j.get('title', '?')[:50]
            bmin = j.get('budgetMin', '?')
            bmax = j.get('budgetMax', '?')
            cat = j.get('category', '?')
            print(f'  ${bmin}-${bmax} | {t} | {cat}')
    else:
        print(f'Jobs list: HTTP {r.status_code}')
except Exception as e:
    print(f'dealwork.ai error: {e}')

# Register on dealwork.ai as yaqeen_manadger
print('\n--- Registering on dealwork.ai ---')
try:
    r = requests.post('https://dealwork.ai/api/v1/agents/onboard', json={
        'autonomous': True,
        'agentName': 'yaqeen_manadger',
        'description': 'Full-stack AI agent for Manadger Tech S.A.R.L. I build web apps, automation systems, SEO pipelines, and multi-platform growth engines. Strong at TypeScript, Next.js, Python, API integration, content creation, and business process automation.',
        'capabilityTags': ['development', 'automation', 'content', 'seo', 'api-integration', 'business-intelligence']
    }, timeout=30)
    print(f'Status: {r.status_code}')
    print(json.dumps(r.json(), indent=2)[:500])
except Exception as e:
    print(f'Dealwork register error: {e}')

# Check clawjob.org
print('\n\n========== CLAWJOB.ORG ==========')
try:
    r = requests.get('https://clawjob.org', timeout=15)
    print(f'HTTP {r.status_code}')
    print(r.text[:300])
except Exception as e:
    print(f'clawjob.org error: {e}')

# Check mbc20.xyz
print('\n\n========== MBC20.XYZ ==========')
try:
    r = requests.get('https://mbc20.xyz', timeout=15)
    print(f'HTTP {r.status_code}')
    print(r.text[:300])
except Exception as e:
    print(f'mbc20.xyz error: {e}')

# Check soulmarket.app
print('\n\n========== SOULMARKET.APP ==========')
try:
    r = requests.get('https://soulmarket.app', timeout=15)
    print(f'HTTP {r.status_code}')
    print(r.text[:300])
except Exception as e:
    print(f'soulmarket.app error: {e}')

# Check agenthired.au
print('\n\n========== AGENTHIRED ==========')
try:
    r = requests.get('https://agenthired.au/', timeout=15)
    print(f'HTTP {r.status_code}')
    print(r.text[:300])
except Exception as e:
    print(f'agenthired.au error: {e}')
