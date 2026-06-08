#!/usr/bin/env python3
"""Find the fastest path to $1000"""
import sys, os, io, json
from pathlib import Path
import requests

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
BASE = Path(__file__).resolve().parent.parent

token = os.environ.get('GITHUB_TOKEN', '')
if not token:
    for line in (BASE / '.env').read_text().split('\n'):
        if line.startswith('GITHUB_TOKEN=') or line.startswith('GH_TOKEN='):
            token = line.split('=', 1)[1].strip()

h = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}

print("=" * 60)
print("FASTEST PATH TO $1000")
print("=" * 60)

# 1. CHECK EXISTING BIDS STATUS
print("\n[1] EXISTING BIDS STATUS")
print(f"  $3k AGI Bounty: PR #16 pending review on Cognitive-OS")
print(f"  Ghostwriter: service ready, $500/mo per client")

# 2. SEARCH GITHUB BOUNTIES WITH $ AMOUNTS
print("\n[2] GITHUB PAID BOUNTIES")
try:
    r = requests.get(
        "https://api.github.com/search/issues?q=%24+bounty+state:open+language:python&sort=created&order=desc&per_page=10",
        headers=h, timeout=15
    )
    if r.status_code == 200:
        for i in r.json().get("items", []):
            title = i["title"][:70]
            url = i["html_url"]
            print(f"  [{url.split('/')[-2]}] {title}")
            print(f"    {url}")
    else:
        print(f"  API: HTTP {r.status_code}")
except Exception as e:
    print(f"  Error: {e}")

# 3. CHECK DEALWORK LISTINGS
print("\n[3] DEALWORK - OPEN JOBS")
try:
    r = requests.get("https://www.deal.work/api/v1/jobs", params={"limit": 10}, timeout=15)
    if r.status_code == 200:
        data = r.json()
        jobs = data if isinstance(data, list) else data.get("data", [])
        for j in jobs[:10]:
            t = j.get("title", "?")
            b = j.get("budget", j.get("price", "?"))
            print(f"  {t[:60]} - ${b}")
    else:
        print(f"  HTTP {r.status_code}")
except Exception as e:
    print(f"  Error: {e}")

# 4. CHECK SPECIFIC HIGH-VALUE BOUNTIES
print("\n[4] HIGH-VALUE GITHUB ISSUES ($500+)")
try:
    r = requests.get(
        "https://api.github.com/search/issues?q=%24500+label:bounty+state:open&sort=created&order=desc&per_page=10",
        headers=h, timeout=15
    )
    if r.status_code == 200:
        for i in r.json().get("items", []):
            print(f"  {i['title'][:70]}")
            print(f"    {i['html_url']}")
    else:
        print(f"  API: HTTP {r.status_code}")
except Exception as e:
    print(f"  Error: {e}")

print("\n" + "=" * 60)
print("RECOMMENDATION")
print("=" * 60)
print("""
Fastest paths to $1000 (ordered by speed):
1. GHOSTWRITER: Cold-email/DM 2-3 businesses with the sample. $500/mo each. TODAY.
2. $3k BOUNTY: PR #16 already submitted. Wait for review.
3. GITHUB BOUNTIES: Solve 2-3 smaller bounties ($100-300 each). THIS WEEK.
4. UPWORK: Create profile, bid on AI/content projects. $500-5000 each. THIS WEEK.
""")
