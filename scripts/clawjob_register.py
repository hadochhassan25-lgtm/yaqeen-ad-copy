# -*- coding: utf-8 -*-
import requests, sys, io, json, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Part 1: ClawJob registration
print('========== CLAWJOB REGISTRATION ==========')
try:
    r = requests.post('https://api.clawjob.org/api/v1/agents/register', json={
        'name': 'yaqeen_manadger',
        'skills': ['development', 'automation', 'content', 'seo', 'translation', 'arabic', 'french']
    }, timeout=15)
    print(f'Status: {r.status_code}')
    print(json.dumps(r.json(), indent=2)[:500])
except Exception as e:
    print(f'Error: {e}')

# Part 2: ClawJob docs
print('\n========== CLAWJOB SKILL.MD ==========')
try:
    r = requests.get('https://api.clawjob.org/skill.md', timeout=15)
    print(f'Status: {r.status_code}')
    print(r.text[:2000])
except Exception as e:
    print(f'Error: {e}')

# Part 3: ClawJob jobs
print('\n========== CLAWJOB JOBS ==========')
try:
    r = requests.get('https://api.clawjob.org/api/v1/jobs?per_page=20', timeout=15)
    print(f'Status: {r.status_code}')
    print(json.dumps(r.json(), indent=2)[:2000])
except Exception as e:
    print(f'Error: {e}')

# Part 4: Dealwork seed jobs (create them)
print('\n========== DEALWORK SEED JOBS ==========')
AK = 'ak_3adeca8d7e789d6986a2cb7f07aedafd4c00f29c8f1efe43'
DH = {'Authorization': 'Bearer ' + AK, 'Content-Type': 'application/json', 'User-Agent': 'yaqeen_manadger/1.0'}
DBASE = 'https://dealwork.ai/api/v1'
r = requests.post(f'{DBASE}/jobs/seed?deadlineDays=45&minActive=5', headers=DH, timeout=15)
print(f'Status: {r.status_code}')
if r.status_code == 200:
    print(json.dumps(r.json(), indent=2)[:500])
else:
    print(r.text[:300])

# Part 5: Check incoming orders on listings
print('\n========== INCOMING REQUESTS ==========')
r = requests.get(f'{DBASE}/listings/requests/pending', headers=DH, timeout=15)
print(f'Status: {r.status_code}')
if r.status_code == 200:
    print(json.dumps(r.json(), indent=2)[:500])
else:
    print(r.text[:300])

# Part 6: Try to bid on salmon burgers job
print('\n========== SALMON BURGERS BID ==========')
# First get the full job details
r = requests.get(f'{DBASE}/jobs/cb3ca024-af8', headers=DH, timeout=15)
if r.status_code == 200:
    print('Job details:')
    print(json.dumps(r.json(), indent=2)[:800])
else:
    print(f'Job fetch error: {r.status_code}')

# Part 7: Check agentflex.vip
print('\n========== AGENTFLEX.VIP ==========')
try:
    r = requests.get('https://agentflex.vip', timeout=15)
    print(f'Status: {r.status_code}')
    print(r.text[:500])
except Exception as e:
    print(f'Error: {e}')
