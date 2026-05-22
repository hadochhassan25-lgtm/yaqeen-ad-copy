#!/usr/bin/env python3
"""
YAQEEN Agent CLI — Manadger Tech S.A.R.L
Usage:
  python yaqeen_agent.py generate --business "Cafe" --audience "Professionals" --industry "Coffee"
  python yaqeen_agent.py monitor
  python yaqeen_agent.py serve
  python yaqeen_agent.py demo
"""
import sys, os, json, random, subprocess, webbrowser, time, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

WALLET = "0xD0366D78055b8c637c44d769D1A1371106d13552"
PRICE_USDC = 0.50
PRICE_ETH = 0.0005
PORT = 5000
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TEMPLATES = {
    'facebook': {
        'primary_text': [
            "Stop scrolling. {benefit} is closer than you think.",
            "Your customers are looking for {benefit}. Show them you exist.",
            "Most {audience} don't know they need {benefit}. Yet.",
            "The #1 mistake {audience} make? Ignoring {benefit}."],
        'headline': ["Discover {solution} Today", "Why {audience} Choose {solution}", "{benefit} — Made Simple"],
        'description': ["Join {count}+ {audience} who trust {solution}. See results in days.",
                        "Built for {audience}. {solution} delivers {benefit} without the headache."],
        'cta': ["Get Started Free", "Learn More", "Try It Now", "Book a Demo"]},
    'instagram': {
        'caption': ["Your {industry} game just leveled up.",
                    "POV: You found {solution} for {audience}.",
                    "Stop guessing. Start {benefit}."],
        'cta': ["Link in bio", "DM us", "Tag someone who needs this", "Swipe up"]},
    'google': {
        'headline': ["{solution}: {benefit}", "Best {solution} for {audience}", "Top-Rated {solution}"],
        'description': ["Looking for {benefit}? {solution} helps {audience} achieve results fast.",
                        "Trusted by {count}+ {audience}. Get {benefit} with {solution}."]},
    'linkedin': {
        'headline': ["How {audience} Achieve {benefit}", "Scaling {industry}? Here's Your Playbook"],
        'body': ["The #1 challenge for {audience}? {pain_point}. Here's how {solution} solves it.",
                 "Organizations using {solution} see {x}% improvement in {metric}. That's {benefit}."]}}

def rand(arr): return random.choice(arr)
def randint(a,b): return random.randint(a,b)

def generate(business, audience, industry, platform='facebook', count=3):
    benefit = f'smarter {industry.lower()} marketing'
    solution = business
    pain_point = f'ineffective {industry.lower()} advertising'
    platforms = ['facebook','instagram','google','linkedin'] if platform == 'all' else [platform]
    results = {}
    for p in platforms:
        tmpl = TEMPLATES[p]
        variants = []
        for _ in range(count):
            v = {}
            if p == 'facebook':
                v['primary_text'] = rand(tmpl['primary_text']).format(benefit=benefit,audience=audience,solution=solution,industry=industry)
                v['headline'] = rand(tmpl['headline']).format(solution=solution,audience=audience,benefit=benefit,industry=industry)
                v['description'] = rand(tmpl['description']).format(count=randint(100,5000),audience=audience,solution=solution,benefit=benefit)
                v['cta'] = rand(tmpl['cta'])
            elif p == 'instagram':
                v['caption'] = rand(tmpl['caption']).format(industry=industry,solution=solution,audience=audience,benefit=benefit)
                v['cta'] = rand(tmpl['cta'])
            elif p == 'google':
                v['headline'] = rand(tmpl['headline']).format(solution=solution,benefit=benefit,audience=audience)
                v['description'] = rand(tmpl['description']).format(benefit=benefit,solution=solution,audience=audience,count=randint(100,5000))
            elif p == 'linkedin':
                v['headline'] = rand(tmpl['headline']).format(audience=audience,benefit=benefit,solution=solution,industry=industry)
                v['body'] = rand(tmpl['body']).format(audience=audience,pain_point=pain_point,solution=solution,benefit=benefit,x=randint(20,80),metric='conversion')
            variants.append(v)
        results[p] = variants
    return results

def fmt(results, platform):
    platforms = [platform] if platform != 'all' else list(results.keys())
    out = ''
    for p in platforms:
        out += f'\n=== {p.upper()} Ad Copy ===\n'
        for i, v in enumerate(results[p], 1):
            out += f'\nVariant {i}:\n'
            for k, val in v.items():
                label = k.replace('_',' ').title()
                out += f'  {label}: {val}\n'
    return out

def cmd_generate(args):
    b = args.get('--business') or input('Business name: ')
    a = args.get('--audience') or input('Target audience: ')
    i = args.get('--industry') or input('Industry: ')
    p = args.get('--platform', 'facebook')
    c = int(args.get('--count', '3'))
    results = generate(b, a, i, p, c)
    print(fmt(results, p))
    print(f'\n--- Payment ---')
    print(f'Send ${PRICE_USDC:.2f} USDC or {PRICE_ETH} ETH to:')
    print(f'  {WALLET}')
    print(f'Chain: Base (Ethereum also accepted)')

def cmd_serve(args):
    api_file = os.path.join(BASE_DIR, 'services', 'yaqeen_ad_api_deploy.py')
    client_file = os.path.join(BASE_DIR, 'services', 'yaqeen_client.html')
    print(f'[+] Starting YAQEEN API on port {PORT}...')
    proc = subprocess.Popen([sys.executable, api_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(3)
    try:
        import requests as r
        resp = r.get(f'http://localhost:{PORT}/health', timeout=5)
        print(f'[+] API running: {resp.json()}')
    except:
        print('[!] API failed to start. Try: pip install flask')
    print(f'[+] Demo page: {client_file}')
    webbrowser.open(f'file://{client_file}')
    print('[+] Press Ctrl+C to stop')
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        proc.terminate()
        print('\n[+] Stopped')

def cmd_demo(args):
    client_file = os.path.join(BASE_DIR, 'services', 'yaqeen_client.html')
    print(f'[+] Opening demo page...')
    webbrowser.open(f'file://{client_file}')
    print(f'[+] Wallet: {WALLET}')
    print(f'[+] Price: ${PRICE_USDC:.2f} USDC per request')

def cmd_openserv(args):
    """Check OpenServ idea status."""
    import requests
    key = "64ef5c33adcfda1a00abc0f921e216f429602d8f1dab8d5325b109feeb6a1865"
    h = {"x-openserv-key": key}
    r = requests.get("https://api.launch.openserv.ai/ideas/69975e64b492c646b1878c77", headers=h, timeout=15)
    d = r.json()
    print(f'Idea: {d.get("title","?")}')
    print(f'Pickups: {d.get("pickups","?")}')
    comments = d.get("comments", [])
    print(f'Comments: {len(comments)}')
    for c in comments[-5:]:
        content = c.get("content","")[:120]
        date = c.get("createdAt","")[:16]
        print(f'  [{date}] {content}')

def cmd_monitor(args):
    """Check all platforms for activity."""
    print("=== YAQEEN Monitor ===")
    print()
    # OpenServ
    try:
        import requests
        r = requests.get(
            "https://api.launch.openserv.ai/ideas/69975e64b492c646b1878c77",
            headers={"x-openserv-key": "64ef5c33adcfda1a00abc0f921e216f429602d8f1dab8d5325b109feeb6a1865"},
            timeout=10)
        d = r.json()
        cmts = d.get("comments", [])
        our_cmts = [c for c in cmts if "YAQEEN" in c.get("content","") or "yaqeen" in c.get("content","").lower()]
        print(f"[OpenServ] {len(cmts)} comments total, {len(our_cmts)} from us")
        last = cmts[-1] if cmts else None
        if last:
            print(f"  Last comment: [{last.get('createdAt','')[:16]}] {last.get('content','')[:80]}...")
    except Exception as e:
        print(f"[OpenServ] Error: {e}")

    print(f"\n[System] Ready on port {PORT}")
    print(f"[Wallet] {WALLET}")
    print(f"[Price] ${PRICE_USDC:.2f} USDC / {PRICE_ETH} ETH")
    print()
    print("Run: python yaqeen_agent.py serve    # Start API server + demo")
    print("Run: python yaqeen_agent.py demo     # Open demo page")
    print("Run: python yaqeen_agent.py generate # Create ad copy")

if __name__ == '__main__':
    args = sys.argv[1:]
    if not args:
        cmd_monitor({})
    elif args[0] == 'generate':
        params = {}
        for i in range(1, len(args)-1):
            if args[i].startswith('--'):
                params[args[i]] = args[i+1]
        cmd_generate(params)
    elif args[0] == 'serve':
        cmd_serve({})
    elif args[0] == 'demo':
        cmd_demo({})
    elif args[0] == 'monitor':
        cmd_monitor({})
    elif args[0] == 'openserv':
        cmd_openserv({})
    else:
        print(f'Usage: python {sys.argv[0]} [generate|serve|demo|monitor|openserv]')
