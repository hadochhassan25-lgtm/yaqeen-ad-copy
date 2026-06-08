"""
YAQEEN Worker Daemon — autonomous Dealwork agent
Runs 24/7, checks for new jobs, auto-bids, monitors listing
"""
import requests, json, time, os, sys, io, random
from pathlib import Path
from dotenv import load_dotenv
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = Path(__file__).resolve().parent.parent
load_dotenv(BASE / '.env')
MEMORY = BASE / 'memory'
LOG = MEMORY / 'worker_daemon.log'
STATE = MEMORY / 'worker_state.json'
MEMORY.mkdir(parents=True, exist_ok=True)

API_KEY = os.environ.get('DEALWORK_KEY') or os.environ.get('DEALWORK_API_KEY') or ""
if not API_KEY:
    print("[DAEMON] CRITICAL: DEALWORK_KEY not set in environment", flush=True)
H = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
API = "https://dealwork.ai/api/v1"
LISTING_ID = "f93fd81b-210e-4f53-8626-d6d62a81e18f"
BIDDED_JOBS_FILE = MEMORY / 'bidded_jobs.json'
BID_RESULTS_FILE = MEMORY / 'bid_results.json'
PUBLIC_URL_FILE = MEMORY / 'public_url.txt'
VERCEL_URL = "https://yaqeen-ad-copy.vercel.app"

OUR_SKILLS = ['writing', 'coding', 'development', 'marketing', 'content-media', 'data', 'writing_research', 'design', 'tech-support']

KEYWORDS = [
    'seo', 'translation', 'api', 'python', 'flask', 'content', 'copy', 'documentation',
    'arabic', 'french', 'english', 'react', 'dashboard', 'automation', 'script',
    'marketing', 'ad', 'copywriting', 'content writing', 'blog', 'article',
    'telegram bot', 'discord bot', 'scraping', 'data entry', 'web scraping',
    'landing page', 'html', 'css', 'javascript', 'node', 'flask api',
    'rest api', 'integration', 'webhook', 'crypto', 'blockchain', 'wallet',
    'chatbot', 'ai', 'gpt', 'llm', 'openai', 'claude',
    'excel', 'google sheets', 'power bi', 'data analysis',
    'virtual assistant', 'va', 'customer support', 'tech support',
    'wordpress', 'shopify', 'wix', 'web design',
    'social media', 'facebook ads', 'google ads', 'instagram',
    'proofreading', 'editing', 'transcription', 'research'
]

PROPOSAL_TEMPLATES = {
    'writing': 'I specialize in marketing copy, ad copy, SEO content, and technical documentation. I deliver clean, native-quality writing in English, Arabic, and French. Fast turnaround, revisions included.',
    'coding': 'Full-stack developer (Python, Flask, React, Node.js, APIs). I build automations, scrapers, dashboards, bots, and backends. Experience deploying on Vercel and managing cloud infra. Clean code, tested, delivered on time.',
    'development': 'Full-stack developer with strong experience in Python, Flask, React, and API development. I deliver production-ready code with documentation and tests. Fast turnaround for tight deadlines.',
    'marketing': 'Digital marketing specialist: SEO audits, ad copy (Facebook/Google/LinkedIn/IG), content strategy, and marketing automation. I help businesses get more traffic and conversions with data-driven copy.',
    'content-media': 'Content creator and writer: blog posts, social media content, ad copy, newsletters, and video scripts. I write for engagement and conversions. Native English/Arabic/French.',
    'data': 'Data analyst and automation specialist: Python, Excel, Google Sheets, Power BI, web scraping, data cleaning, and visualization. I turn raw data into actionable insights.',
    'writing_research': 'Research writer: I produce well-researched articles, reports, documentation, and technical content. Background in technical writing and academic research. Citations included.',
    'design': 'Web and graphic designer: landing pages, social media creatives, branding, and UI mockups. HTML/CSS, Figma, Canva. Fast iterations based on feedback.',
    'tech-support': 'Technical support specialist: troubleshooting, system admin, API integration, deployment, and debugging. I resolve issues fast with clear communication.'
}

DEFAULT_PROPOSAL = 'I can deliver this project with high quality and fast turnaround. I have strong experience in similar work and I communicate clearly. Let me know if you have questions — I\'m ready to start.'

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

def load_bid_results():
    if BID_RESULTS_FILE.exists():
        return json.loads(BID_RESULTS_FILE.read_text())
    return {'won': 0, 'lost': 0, 'pending': 0, 'total_spent': 0, 'history': []}

def save_bid_results(data):
    BID_RESULTS_FILE.write_text(json.dumps(data, indent=2))

def build_proposal(title, cat, budget):
    tmpl = PROPOSAL_TEMPLATES.get(cat, DEFAULT_PROPOSAL)
    title_short = title[:60] if len(title) > 60 else title
    if budget > 100:
        proposal = f"I have strong experience delivering {title_short}. {tmpl} I'm available to start immediately and work within your budget. Let's schedule a quick call to discuss requirements."
    elif budget > 20:
        proposal = f"I can handle {title_short}. {tmpl} Available now, fast turnaround. Happy to discuss details."
    else:
        proposal = f"I can do this. {tmpl}"
    return proposal[:500]

def scan_and_bid():
    try:
        bidded = load_bidded()
        br = load_bid_results()
        r = requests.get(f'{API}/jobs?per_page=50', headers=H, timeout=15)
        if r.status_code != 200:
            return
        jobs = r.json().get('data', [])
        if not jobs:
            log('No jobs found on Dealwork')
            return
        new_bids = 0
        for j in jobs:
            jid = j.get('id', '')
            if jid in bidded:
                continue
            title = (j.get('title') or '').lower()
            cat = j.get('category', '')
            bmin = float(j.get('budgetMin') or 0)
            bmax = float(j.get('budgetMax') or 0)
            budget_avg = (bmin + bmax) / 2
            if budget_avg == 0:
                budget_avg = 25
            if any(x in title for x in ['可可', '枭', 'chinese', 'chinois']):
                continue
            if any(x in title for x in ['ai agent', '24/7 ai']):
                continue
            matched = False
            if cat in OUR_SKILLS:
                matched = True
            for kw in KEYWORDS:
                if kw in title:
                    matched = True
                    break
            if not matched:
                continue
            amount = min(max(bmin, 15), 75)
            if budget_avg > 50:
                amount = min(budget_avg * 0.7, 75)
            hours = max(1, int(amount / 10))
            proposal = build_proposal(title, cat, budget_avg)
            try:
                resp = requests.post(f'{API}/jobs/{jid}/bids', headers=H,
                    json={'proposedAmount': str(round(amount, 2)), 'estimatedHours': hours, 'proposalText': proposal}, timeout=15)
                bidded.add(jid)
                save_bidded(bidded)
                if resp.status_code in (200, 201):
                    log(f'AUTO-BID ${round(amount,2)} on {title[:40]} ✅')
                    new_bids += 1
                    br['history'].append({'job': title[:60], 'amount': round(amount, 2), 'status': 'pending', 'time': time.strftime('%Y-%m-%d %H:%M')})
                else:
                    err = resp.text[:80]
                    log(f'AUTO-BID ${round(amount,2)} on {title[:40]} ❌ {err}')
                    br['history'].append({'job': title[:60], 'amount': round(amount, 2), 'status': 'failed', 'error': err, 'time': time.strftime('%Y-%m-%d %H:%M')})
            except Exception as e:
                log(f'AUTO-BID error on {title[:40]}: {e}')
            time.sleep(2.5)
        save_bid_results(br)
        if new_bids > 0:
            log(f'{new_bids} new bids submitted this cycle')
    except Exception as e:
        log(f'scan_and_bid error: {e}')

def update_listing_url():
    url = get_public_url()
    if not url:
        url = VERCEL_URL
    try:
        listing = requests.get(f'{API}/listings/{LISTING_ID}', headers=H, timeout=15)
        if listing.status_code != 200:
            return
        desc = listing.json().get('data', {}).get('description', '')
        if VERCEL_URL in desc:
            return  # Vercel URL already in listing
        new_desc = f"""AI advertising and SEO expert. Fully automated — instant delivery via API.

TEST THE API NOW (live, no auth needed):
GET {VERCEL_URL}/health
POST {VERCEL_URL}/api/generate (body: business, audience, industry, platform, tone, language)
POST {VERCEL_URL}/api/translate
POST {VERCEL_URL}/api/seo-report

Services:
- AD COPY ($0.50): High-converting ad copy + headlines + CTAs for FB/IG/Google/LinkedIn
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
            log(f'Listing URL updated to {VERCEL_URL} ✅')
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

CRYPTO_WALLET = os.environ.get('WALLET_ADDRESS', '0xD0366D78055b8c637c44d769D1A1371106d13552')
CRYPTO_CHAIN = os.environ.get('CHAIN', 'base')
PAID_INVOICES_FILE = MEMORY / 'paid_invoices.json'

def load_paid():
    if PAID_INVOICES_FILE.exists():
        return set(json.loads(PAID_INVOICES_FILE.read_text()))
    return set()

def save_paid(ids):
    PAID_INVOICES_FILE.write_text(json.dumps(list(ids)))

def check_crypto_payments():
    try:
        sys.path.insert(0, str(BASE / 'services'))
        from payment_bridge import check_all_invoices, stop
        result = check_all_invoices()
        stop()
        paid_invoices = [inv for inv in result.get('invoices', []) if inv.get('status') == 'paid']
        already = load_paid()
        for inv in paid_invoices:
            iid = inv['id']
            if iid not in already:
                amount = inv.get('amount', '?')
                log(f'💰 PAYMENT RECEIVED: ${amount} USDC | Invoice: {iid}')
                already.add(iid)
                save_paid(already)
        bal = result.get('total', 0)
        pd = result.get('paid', 0)
        log(f'Crypto: {pd}/{bal} invoices paid | Wallet: {CRYPTO_WALLET[:16]}...')
        return result
    except Exception as e:
        log(f'check_crypto_payments error: {e}')
        return None

def save_state(data):
    STATE.write_text(json.dumps(data, indent=2))

def load_state():
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {'cycle': 0, 'total_bids': 3, 'total_earned': 0}

def main():
    log('YAQEEN Worker Daemon started')
    log(f'API Key: {API_KEY[:20]}...')
    log(f'Crypto Wallet: {CRYPTO_WALLET[:16]}... on {CRYPTO_CHAIN}')
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
        crypto = check_crypto_payments()
        br = load_bid_results()
        br['pending'] = sum(1 for h in br.get('history', []) if h.get('status') == 'pending')
        br['won'] = sum(1 for h in br.get('history', []) if h.get('status') == 'won')
        br['lost'] = sum(1 for h in br.get('history', []) if h.get('status') == 'lost')
        save_bid_results(br)
        log(f'Bid stats: {br.get("won",0)} won / {br.get("lost",0)} lost / {br.get("pending",0)} pending')
        save_state({
            'cycle': cycle,
            'pending_bids': len(bids),
            'pending_requests': pending,
            'wallet_available': avail,
            'wallet_locked': locked,
            'paid_invoices': len(load_paid()),
            'bids_won': br.get('won', 0),
            'bids_lost': br.get('lost', 0),
            'last_check': time.strftime('%Y-%m-%d %H:%M:%S')
        })
        # Check every 15 minutes
        for _ in range(900):
            time.sleep(1)

if __name__ == '__main__':
    main()
