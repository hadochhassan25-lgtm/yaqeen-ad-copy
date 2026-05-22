import requests, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = 'https://www.moltbook.com/api/v1'
KEY = 'moltbook_sk_b7NcmWpHjoProzNe1IgzkcFhALp0j4x1'
H = {'Authorization': f'Bearer {KEY}', 'User-Agent': 'yaqeen_manadger/1.0'}

# Critical posts to deep dive
posts = {
    '0b3a80c9-4d5e-46e0-9288-f0557ab4ab8a': 'ERC-8004 + x402',
    '58759fda-1389-436b-9a8d-4ddea77954e8': 'coinbase agentic.market',
    'af7214a1-edbe-474b-a72d-f31b6f29bec7': '24k USDC wallet',
    '7736c960-68d5-4d39-aa5f-f8744e543fcc': '24k marketplace',
    '160ccded-2a17-4c78-a1d2-307f250bd346': 'AiFinPay',
}

for pid, label in posts.items():
    r = requests.get(f'{BASE}/posts/{pid}', headers=H, timeout=15)
    if r.status_code == 200:
        p = r.json().get('post', r.json())
        title = p.get('title','')
        content = p.get('content','')
        author = p.get('author',{}).get('name','?')
        ups = p.get('upvotes',0)
        print(f'\n{"="*60}')
        print(f'[{ups}↑] {title}')
        print(f'Author: {author} | Label: {label}')
        print(f'{"="*60}')
        print(content[:800])
        print(f'\nLink: https://www.moltbook.com/p/{pid}')
    else:
        print(f'[ERROR] {pid}: {r.status_code}')
