"""
YAQEEN Worker Daemon — autonomous Dealwork agent
Runs 24/7, checks for new jobs, auto-bids, monitors listing
"""
import requests, json, time, os, sys, io, random
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = Path(__file__).resolve().parent.parent
MEMORY = BASE / 'memory'
LOG = MEMORY / 'worker_daemon.log'
STATE = MEMORY / 'worker_state.json'
MEMORY.mkdir(parents=True, exist_ok=True)

API_KEY = os.environ.get('DEALWORK_KEY') or "ak_92388ca0b2368b9978c3620df011b8477290fffaee4b42fb"
H = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
API = "https://dealwork.ai/api/v1"
LISTING_ID = "f93fd81b-210e-4f53-8626-d6d62a81e18f"
BIDDED_JOBS_FILE = MEMORY / 'bidded_jobs.json'
PUBLIC_URL_FILE = MEMORY / 'public_url.txt'

# Skills we can bid on
OUR_SKILLS = ['writing', 'coding', 'development', 'marketing', 'content-media', 'data', 'writing_research']
KEYWORDS = ['seo', 'translation', 'api', 'python', 'flask', 'content', 'copy', 'documentation',
            'arabic', 'french', 'english', 'react', 'dashboard', 'automation', 'script']

def log(msg):
    t = time.strftime('%Y-%m-%d %H:%M:%S')
    line = f'[{t}] {msg}'
    print(line, flush=True)
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(line + '\n')

def load_bidded():
    if BIDDED_JOBS_FILE.exists():
        return set(json.loads(BIDDED_JOBS_FILE.read_text()))
    return set()

def save_bidded(ids):
    BIDDED_JOBS_FILE.write_text(json.dumps(list(ids)))

def get_public_url():
    if PUBLIC_URL_FILE.exists():
        return PUBLIC_URL_FILE.read_text().strip()
    return None

def check_bids():
    try:
        r = requests.get(f'{API}/bids/mine', headers=H, timeout=15)
        if r.status_code == 200:
            bids = r.json().get('data', [])
            for b in bids:
                amt = b.get('proposedAmount', '?')
                stat = b.get('status', '?')
                title = b.get('job', {}).get('title', '?')[:50]
                log(f'Bid ${amt} | {stat} | {title}')
            return bids
    except Exception as e:
        log(f'check_bids error: {e}')
    return []

def check_contracts():
    try:
        for role in ['worker', 'buyer']:
            r = requests.get(f'{API}/contracts?role={role}&per_page=20', headers=H, timeout=15)
            if r.status_code == 200:
                data = r.json().get('data', [])
                for c in data:
                    log(f'Contract {role}: {c.get("state")} ${c.get("amount")} | {c.get("job",{}).get("title","?")[:40]}')
    except Exception as e:
        log(f'check_contracts error: {e}')

def check_listing_requests():
    try:
        r = requests.get(f'{API}/listings/requests/pending', headers=H, timeout=15)
        if r.status_code == 200:
            count = len(r.json().get('data', []))
            if count > 0:
                log(f'{count} pending listing requests!')
                return count
    except:
        pass
    return 0

def scan_and_bid():
    try:
        bidded = load_bidded()
        r = requests.get(f'{API}/jobs?per_page=50', headers=H, timeout=15)
        if r.status_code != 200:
            return
        jobs = r.json().get('data', [])
        new_bids = 0
        for j in jobs:
            jid = j.get('id', '')
            if jid in bidded:
                continue
            title = (j.get('title') or '').lower()
            cat = j.get('category', '')
            bmin = float(j.get('budgetMin') or 0)
            bmax = float(j.get('budgetMax') or 0)
            # Skip Chinese agent listings
            if any(x in title for x in ['可可', '枭', 'chinese', 'chinois', 'bilingual']):
                continue
            if any(x in title for x in ['ai agent', '24/7 ai']):
                continue
            # Match against our skills
            matched = False
            if cat in OUR_SKILLS:
                matched = True
            for kw in KEYWORDS:
                if kw in title:
                    matched = True
                    break
            if not matched:
                continue
            # Auto-bid
            amount = min(max(bmin, 15), 50)
            hours = max(1, int(amount / 8))
            proposal = f"I can deliver this. I have experience in {cat} with fast turnaround. Quality work, delivered on time."
            if len(proposal) < 50:
                proposal = proposal + " Contact me to discuss details and timeline for your project."
            try:
                resp = requests.post(f'{API}/jobs/{jid}/bids', headers=H,
                    json={'proposedAmount': str(amount), 'estimatedHours': hours, 'proposalText': proposal}, timeout=15)
                bidded.add(jid)
                save_bidded(bidded)
                if resp.status_code in (200, 201):
                    log(f'AUTO-BID ${amount} on {title[:40]} ✅')
                    new_bids += 1
                else:
                    err = resp.text[:80]
                    log(f'AUTO-BID ${amount} on {title[:40]} ❌ {err}')
            except Exception as e:
                log(f'AUTO-BID error on {title[:40]}: {e}')
            time.sleep(3)  # Rate limit
        if new_bids > 0:
            log(f'{new_bids} new bids submitted this cycle')
    except Exception as e:
        log(f'scan_and_bid error: {e}')

def update_listing_url():
    url = get_public_url()
    if not url:
        return
    try:
        listing = requests.get(f'{API}/listings/{LISTING_ID}', headers=H, timeout=15)
        if listing.status_code != 200:
            return
        desc = listing.json().get('data', {}).get('description', '')
        if url in desc:
            return  # URL already in listing
        # Update listing with new URL
        new_desc = f"""AI advertising and SEO expert. Fully automated — instant delivery via API.

TEST THE API NOW (live, no auth needed):
GET {url}/health
POST {url}/api/generate
POST {url}/api/translate
POST {url}/api/seo-report

Services:
- AD COPY ($0.50): High-converting ad copy + headlines + CTAs
- TRANSLATION ($1.00): EN-AR-FR marketing-aware translation  
- SEO REPORTS ($1.00): Technical audits with keyword analysis

Payment:
- Crypto (USDC/ETH): 0xD0366D78055b8c637c44d769D1A1371106d13552
- PayPal: https://paypal.me/lamti

Delivery: <10 seconds. Languages: English, Arabic, French
Powered by GPT-4o-mini (GitHub Models) + DeepSeek v3 backup."""
        r = requests.patch(f'{API}/listings/{LISTING_ID}', headers=H,
            json={'description': new_desc}, timeout=15)
        if r.status_code == 200:
            log(f'Listing URL updated to {url} ✅')
    except Exception as e:
        log(f'update_listing_url error: {e}')

def check_wallet():
    try:
        r = requests.get(f'{API}/wallet/balance', headers=H, timeout=15)
        if r.status_code == 200:
            w = r.json().get('data', {})
            avail = w.get('available', '0')
            locked = w.get('locked', '0')
            if float(avail) > 0:
                log(f'💰 Wallet: ${avail} available! ${locked} locked')
            return float(avail), float(locked)
    except:
        pass
    return 0, 0

def save_state(data):
    STATE.write_text(json.dumps(data, indent=2))

def load_state():
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {'cycle': 0, 'total_bids': 3, 'total_earned': 0}

def main():
    log('YAQEEN Worker Daemon started')
    log(f'API Key: {API_KEY[:20]}...')
    cycle = 0
    while True:
        cycle += 1
        log(f'--- Cycle {cycle} ---')
        bids = check_bids()
        check_contracts()
        pending = check_listing_requests()
        scan_and_bid()
        update_listing_url()
        avail, locked = check_wallet()
        save_state({
            'cycle': cycle,
            'pending_bids': len(bids),
            'pending_requests': pending,
            'wallet_available': avail,
            'wallet_locked': locked,
            'last_check': time.strftime('%Y-%m-%d %H:%M:%S')
        })
        # Check every 15 minutes
        for _ in range(900):
            time.sleep(1)

if __name__ == '__main__':
    main()
