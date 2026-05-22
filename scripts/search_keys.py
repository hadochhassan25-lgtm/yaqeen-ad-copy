# -*- coding: utf-8 -*-
import requests, sys, io, json, re, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

K = 'moltbook_sk_b7NcmWpHjoProzNe1IgzkcFhALp0j4x1'
MH = {'Authorization': 'Bearer ' + K, 'User-Agent': 'yaqeen_manadger/1.0'}
BASE = 'https://www.moltbook.com/api/v1'

# 1. Try DMs / messages endpoint
print('=== MESSAGES / DMs ===')
chat_endpoints = [
    '/messages',
    '/chats',
    '/dms',
    '/conversations',
    '/inbox',
    '/agents/me/messages',
    '/agents/me/chats',
    '/agents/me/dms',
    '/agents/me/inbox',
]
for ep in chat_endpoints:
    r = requests.get(f'{BASE}{ep}?limit=20', headers=MH, timeout=10)
    if r.status_code != 404:
        print(f'{ep}: {r.status_code}')
        if r.status_code == 200:
            print(r.text[:500])
    time.sleep(0.2)

# 2. Search all posts for key patterns - scrape every available post
print('\n=== SEARCH FOR KEY PATTERNS ===')
# Scan the feed for posts about keys, wallets, tokens
for page in range(1, 4):
    r = requests.get(f'{BASE}/posts?page={page}&limit=50', headers=MH, timeout=15)
    if r.status_code == 200:
        posts = r.json().get('posts', r.json())
        if isinstance(posts, list):
            for p in posts:
                if isinstance(p, dict):
                    pid = p.get('id', '')
                    title = (p.get('title', '') or '')
                    content = (p.get('content', '') or '')
                    combined = (title + ' ' + content).lower()
                    # Search for key patterns
                    patterns = [
                        '0x[a-fA-F0-9]{40}',  # Ethereum address
                        'sk_[a-zA-Z0-9_]+',    # Secret key (like Moltbook)
                        'ak_[a-zA-Z0-9_]+',    # API key (like dealwork)
                        'private[_-]?key',
                        'seed[_-]?phrase',
                        'wallet',
                        'airdrop',
                        'claim.*token',
                        'free.*mint',
                        'api[_-]?key',
                        'bearer',
                        'authorization',
                        '0x[a-fA-F0-9]{64}',  # Private key (64 hex chars)
                        'moltbook_sk_',
                    ]
                    for pat in patterns:
                        matches = re.findall(pat, combined, re.IGNORECASE)
                        if matches:
                            au = p.get('author', {}).get('name', '?')
                            ups = p.get('upvotes', 0)
                            coms = p.get('comments', 0)
                            print(f'\n[MATCH] {pat} in post {pid[:12]}')
                            print(f'  Title: {title[:60]}')
                            print(f'  By: {au} [{ups}u/{coms}c]')
                            print(f'  Matches: {matches[:5]}')
    time.sleep(0.5)

# 3. Read comments from ALL posts for leaked keys
print('\n\n=== SCAN COMMENTS FOR KEYS ===')
# Get latest posts and scan their comments
r = requests.get(f'{BASE}/posts?limit=10', headers=MH, timeout=15)
if r.status_code == 200:
    posts = r.json().get('posts', r.json())
    if isinstance(posts, list):
        for p in posts:
            if isinstance(p, dict):
                pid = p.get('id', '')
                if pid:
                    rc = requests.get(f'{BASE}/posts/{pid}/comments?limit=50', headers=MH, timeout=15)
                    if rc.status_code == 200:
                        comments = rc.json().get('comments', rc.json())
                        if isinstance(comments, list):
                            for c in comments:
                                if isinstance(c, dict):
                                    cc = (c.get('content', '') or '')
                                    ca = c.get('author', {}).get('name', '?')
                                    # Check for key patterns in comments
                                    for pat in ['0x[a-fA-F0-9]{40}', '0x[a-fA-F0-9]{64}', 'sk_[a-zA-Z0-9_]+', 'ak_[a-zA-Z0-9_]+', 'private.key', 'seed.phrase', 'api.key', 'bearer']:
                                        matches = re.findall(pat, cc, re.IGNORECASE)
                                        if matches:
                                            print(f'\n[KEY FOUND IN COMMENT] by {ca}:')
                                            print(f'  Matched: {matches[:3]}')
                                            print(f'  Context: {cc[:150]}')
                    time.sleep(0.3)

# 4. Try to access any special agent pages or hidden features
print('\n\n=== SPECIAL ENDPOINTS ===')
special = [
    '/agents/me/keys',
    '/agents/me/tokens',
    '/agents/me/wallet',
    '/agents/me/api-keys',
    '/agents/me/credentials',
    '/keys',
    '/tokens',
    '/api-keys',
]
for ep in special:
    r = requests.get(f'{BASE}{ep}', headers=MH, timeout=10)
    if r.status_code != 404:
        print(f'{ep}: {r.status_code}')
        if r.status_code == 200:
            print(r.text[:300])
