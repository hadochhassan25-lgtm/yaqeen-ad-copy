#!/usr/bin/env python3
"""
YAQEEN Toku Worker Daemon — autonomous Toku.agency agent
Runs 24/7, checks for new jobs, auto-bids
"""
import requests, json, time, os, sys, io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = Path(__file__).resolve().parent.parent
MEMORY = BASE / 'memory'
LOG = MEMORY / 'toku_daemon.log'
STATE = MEMORY / 'toku_state.json'
MEMORY.mkdir(parents=True, exist_ok=True)

API_KEY = os.environ.get('TOKU_API_KEY') or 'cmprtqqf40004le044eo6gprv'
H = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
API = "https://www.toku.agency/api"
BIDDED_FILE = MEMORY / 'toku_bidded.json'
AGENT_NAME = "YAQEEN"
AGENT_ID = "cmprtqqf40003le04i097xvf8"

RELEVANT_KEYWORDS = [
    'ad', 'copy', 'copywriting', 'seo', 'translation', 'content', 'writing',
    'research', 'blog', 'article', 'documentation', 'marketing', 'social media',
    'python', 'api', 'automation', 'script', 'bot', 'web', 'landing page',
    'data entry', 'excel', 'scraping', 'integration', 'webhook', 'arabic',
    'french', 'english', 'translate', 'newsletter', 'email', 'analytics'
]

def log(msg):
    t = time.strftime('%Y-%m-%d %H:%M:%S')
    line = f'[{t}] {msg}'
    print(line, flush=True)
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(line + '\n')

def load_bidded():
    if BIDDED_FILE.exists():
        return set(json.loads(BIDDED_FILE.read_text()))
    return set()

def save_bidded(ids):
    BIDDED_FILE.write_text(json.dumps(list(ids)))

def check_profile():
    try:
        r = requests.get(f'{API}/agents/me', headers=H, timeout=15)
        if r.status_code == 200:
            d = r.json().get('agent', {})
            log(f'Profile: {d.get("name")} | Rating: {d.get("rating",0)} | Jobs: {d.get("jobsCompleted",0)}')
            return d
    except Exception as e:
        log(f'profile error: {e}')
    return None

def check_wallet():
    try:
        r = requests.get(f'{API}/agents/wallet', headers=H, timeout=15)
        if r.status_code == 200:
            w = r.json()
            cents = w.get('balanceCents', 0)
            log(f'Wallet: ${cents/100:.2f}')
            return cents
    except Exception as e:
        log(f'wallet error: {e}')
    return 0

def scan_and_bid():
    try:
        bidded = load_bidded()
        r = requests.get(f'{API}/agents/jobs?limit=50', headers=H, timeout=15)
        if r.status_code != 200:
            log(f'Jobs API error: {r.status_code} {r.text[:100]}')
            return
        jobs = r.json().get('jobPosts', [])
        if not jobs:
            log('No open jobs on Toku')
            return
        log(f'{len(jobs)} open jobs found')
        new_bids = 0
        for j in jobs:
            jid = j.get('id', '')
            if jid in bidded:
                continue
            title = (j.get('title') or '').lower()
            desc = ((j.get('description') or '') + ' ' + ' '.join(j.get('tags', []))).lower()
            text = title + ' ' + desc
            matched = any(kw in text for kw in RELEVANT_KEYWORDS)
            if not matched:
                continue
            budget = j.get('budgetCents', 500)
            bid_cents = min(max(budget, 500), 1500)
            msg = f"I can deliver this. I specialize in AI-powered content, automation, and multilingual services (EN/AR/FR). Fast turnaround. API demo: https://yaqeen-ad-copy.vercel.app/health"
            try:
                resp = requests.post(f'{API}/agents/jobs/{jid}/bids', headers=H,
                    json={'priceCents': bid_cents, 'message': msg}, timeout=15)
                bidded.add(jid)
                save_bidded(bidded)
                if resp.status_code in (200, 201):
                    log(f'BID ${bid_cents/100:.2f} on {title[:40]} ✅')
                    new_bids += 1
                else:
                    err = resp.text[:80]
                    log(f'BID ${bid_cents/100:.2f} on {title[:40]} ❌ {err}')
            except Exception as e:
                log(f'BID error on {title[:40]}: {e}')
            time.sleep(3)
        if new_bids > 0:
            log(f'{new_bids} new bids submitted')
    except Exception as e:
        log(f'scan_and_bid error: {e}')

def check_bids():
    try:
        r = requests.get(f'{API}/agents/notifications?limit=20', headers=H, timeout=15)
        if r.status_code == 200:
            notifs = r.json().get('notifications', [])
            for n in notifs:
                if n.get('type') in ('bid_accepted', 'bid_rejected'):
                    log(f'Bid {n["type"]}: {n["title"][:60]}')
    except Exception as e:
        log(f'notifications error: {e}')

def save_state(data):
    STATE.write_text(json.dumps(data, indent=2))

def load_state():
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {'cycle': 0, 'total_bids': 0}

def main():
    log('YAQEEN Toku Daemon started')
    log(f'Agent: {AGENT_NAME} ({AGENT_ID})')
    profile = check_profile()
    check_wallet()
    cycle = 0
    while True:
        cycle += 1
        log(f'--- Cycle {cycle} ---')
        check_bids()
        scan_and_bid()
        save_state({'cycle': cycle, 'last_check': time.strftime('%Y-%m-%d %H:%M:%S')})
        for _ in range(900):
            time.sleep(1)

if __name__ == '__main__':
    main()
