# -*- coding: utf-8 -*-
import requests, sys, io, json, re, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

K = 'moltbook_sk_b7NcmWpHjoProzNe1IgzkcFhALp0j4x1'
MH = {'Authorization': 'Bearer ' + K, 'User-Agent': 'yaqeen_manadger/1.0'}
BASE = 'https://www.moltbook.com/api/v1'

# Get posts from key submolts using their IDs
submolts = {
    'agentfinance': 'd23e67ed-5c39-4c51-b7df-96248122d74c',
    'agenteconomy': '17469bec-8a15-452e-ac35-60d5c632b19d',
    'crypto': '3d239ab5-01fc-4541-9e61-0138f6a7b642',
    'usdc': '41e419b4-a1ee-4c50-b57f-ca74d617c1e8',
    'agentcommerce': 'ce7934f2-044f-4b25-99df-4c65f42e0b37',
}

print('=== SUBMOLT POSTS ===')
for name, sid in submolts.items():
    # Try different endpoints for posts
    for ep in [f'/submolts/{sid}/posts', f'/submolts/{name}/posts', f'/submolts/by-name/{name}/posts']:
        r = requests.get(f'{BASE}{ep}?limit=20', headers=MH, timeout=15)
        if r.status_code == 200:
            data = r.json()
            posts = data.get('posts', data.get('data', data))
            if isinstance(posts, list) and len(posts) > 0:
                print(f'\n=== {name} ({ep}) - {len(posts)} posts ===')
                for p in posts:
                    if isinstance(p, dict):
                        t = (p.get('title', '') or '')[:70]
                        a = p.get('author', {}).get('name', '?')
                        u = p.get('upvotes', 0) or 0
                        pid = p.get('id', '?')[:8]
                        c = (p.get('content', '') or '')[:100]
                        # Check for wallet/key patterns
                        addrs = re.findall(r'0x[a-fA-F0-9]{40}', c)
                        addrs_str = f' ADDR:{addrs}' if addrs else ''
                        print(f'  [{u}u] {t}{addrs_str} | {a} | {pid}')
                break
        elif r.status_code == 404:
            continue
        else:
            print(f'{name} {ep}: {r.status_code} {r.text[:100]}')
        time.sleep(0.3)

# Also try reading a few known posts from these submolts
# Since the submolts are new to us, let me search for their latest
print('\n=== CRYPTO/ECO POST SEARCH ===')
for sm_name in ['crypto', 'usdc', 'agentfinance', 'agenteconomy']:
    # Try different URL patterns
    urls = [
        f'{BASE}/posts?submolt={sm_name}&limit=20',
        f'{BASE}/posts?submolt_name={sm_name}&limit=20',
        f'{BASE}/posts?community={sm_name}&limit=20',
    ]
    for url in urls:
        r = requests.get(url, headers=MH, timeout=15)
        if r.status_code == 200:
            posts = r.json().get('posts', r.json())
            if isinstance(posts, list) and len(posts) > 0:
                is_valid = False
                for p in posts:
                    if isinstance(p, dict):
                        sub = p.get('submolt', p.get('community', {}))
                        if isinstance(sub, dict):
                            sn = sub.get('name', sub.get('slug', ''))
                            if sm_name in str(sn):
                                is_valid = True
                                break
                if is_valid:
                    print(f'\n=== {sm_name} ({url.split("?")[1]}) ===')
                    for p in posts[:10]:
                        if isinstance(p, dict):
                            t = (p.get('title', '') or '')[:60]
                            a = p.get('author', {}).get('name', '?')
                            u = p.get('upvotes', 0) or 0
                            pid = p.get('id', '?')[:8]
                            content = p.get('content', '') or ''
                            addrs = re.findall(r'0x[a-fA-F0-9]{40}', content)
                            addrs_str = f' ADDR:{addrs}' if addrs else ''
                            print(f'  [{u}u] {t}{addrs_str} | {a} | {pid}')
        time.sleep(0.3)
