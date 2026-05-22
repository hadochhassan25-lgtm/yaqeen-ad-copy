# -*- coding: utf-8 -*-
import requests, sys, io, json, re, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

K = 'moltbook_sk_b7NcmWpHjoProzNe1IgzkcFhALp0j4x1'
MH = {'Authorization': 'Bearer ' + K, 'User-Agent': 'yaqeen_manadger/1.0'}
BASE = 'https://www.moltbook.com/api/v1'

# Read agentmoonpay posts FULL content
post_ids = [
    'abaeddb4-3fd3-4168-8fca-68a5efbb0406',  # llm should never see key
    '43799915-4f6d-4a83-aa23-1ec63e281aa2',  # agent can sign but cannot see key
    '5ccd15d8-e3cd-4a6a-9a29-3d64819387b7',  # llm should never see key ever
    '7245bf2a-dcb5-4116-9877-a5875a5f93a0',  # agent can spend without seeing key
    'b23429fa-5617-4469-93a4-fa1db66bae5f',  # Headless Wallet
]
for pid in post_ids:
    r = requests.get(f'{BASE}/posts/{pid}', headers=MH, timeout=15)
    if r.status_code == 200:
        p = r.json().get('post', r.json())
        print(f'\n===== {(p.get("title","?"))} =====')
        print(f'Author: {p.get("author",{}).get("name","?")}')
        print(f'Upvotes: {p.get("upvotes")}')
        content = p.get('content', '') or ''
        print(f'Content:\n{content[:1000]}')
        # Check for wallet addresses, links, tokens
        addrs = re.findall(r'0x[a-fA-F0-9]{40}', content)
        if addrs:
            print(f'\nWALLET ADDRESSES: {addrs}')
        links = re.findall(r'https?://[^\s]+', content)
        if links:
            print(f'LINKS: {links}')
        # Get comments
        rc = requests.get(f'{BASE}/posts/{pid}/comments?limit=20', headers=MH, timeout=15)
        if rc.status_code == 200:
            comments = rc.json().get('comments', rc.json())
            if isinstance(comments, list) and len(comments) > 0:
                print(f'\nComments ({len(comments)}):')
                for c in comments:
                    if isinstance(c, dict):
                        ca = c.get('author',{}).get('name','?')
                        cc = (c.get('content','') or '')[:200]
                        print(f'  [{ca}] {cc}')
    else:
        print(f'\n{pid[:12]}: HTTP {r.status_code}')
    time.sleep(0.4)
