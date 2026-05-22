# -*- coding: utf-8 -*-
import requests, sys, io, json, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

K = 'moltbook_sk_b7NcmWpHjoProzNe1IgzkcFhALp0j4x1'
MH = {'Authorization': 'Bearer ' + K, 'User-Agent': 'yaqeen_manadger/1.0'}
BASE = 'https://www.moltbook.com/api/v1'

# Get full post data from key submolts
print('=== AGENT FINANCE POSTS (full) ===')
r = requests.get(f'{BASE}/posts?submolt=agentfinance&limit=20', headers=MH, timeout=15)
if r.status_code == 200:
    posts = r.json().get('posts', r.json())
    if isinstance(posts, list):
        for p in posts:
            if isinstance(p, dict):
                pid = p.get('id', '')
                t = (p.get('title', '') or '')[:70]
                a = p.get('author', {}).get('name', '?')
                u = p.get('upvotes', 0) or 0
                c = (p.get('content', '') or '')[:200]
                has_addr = '0x' in c
                print(f'\n[{u}u] {t} | {a}')
                print(f'  ID: {pid}')
                print(f'  Content: {c}')
                if has_addr:
                    # Extract addresses
                    import re
                    addrs = re.findall(r'0x[a-fA-F0-9]{40}', c)
                    print(f'  WALLETS: {addrs}')

# Get crypto submolt posts
print('\n\n=== CRYPTO POSTS (full) ===')
r = requests.get(f'{BASE}/posts?submolt=crypto&limit=20', headers=MH, timeout=15)
if r.status_code == 200:
    posts = r.json().get('posts', r.json())
    if isinstance(posts, list):
        for p in posts:
            if isinstance(p, dict):
                pid = p.get('id', '')
                t = (p.get('title', '') or '')[:70]
                a = p.get('author', {}).get('name', '?')
                u = p.get('upvotes', 0) or 0
                c = (p.get('content', '') or '')[:200]
                has_addr = '0x' in c
                print(f'\n[{u}u] {t} | {a}')
                print(f'  ID: {pid}')
                print(f'  Content: {c}')
                if has_addr:
                    addrs = re.findall(r'0x[a-fA-F0-9]{40}', c)
                    print(f'  WALLETS: {addrs}')

# Get USDC posts
print('\n\n=== USDC POSTS (full) ===')
r = requests.get(f'{BASE}/posts?submolt=usdc&limit=20', headers=MH, timeout=15)
if r.status_code == 200:
    posts = r.json().get('posts', r.json())
    if isinstance(posts, list):
        for p in posts:
            if isinstance(p, dict):
                pid = p.get('id', '')
                t = (p.get('title', '') or '')[:70]
                a = p.get('author', {}).get('name', '?')
                u = p.get('upvotes', 0) or 0
                c = (p.get('content', '') or '')[:200]
                print(f'\n[{u}u] {t} | {a}')
                print(f'  ID: {pid}')
                print(f'  Content: {c}')

# Get agent economy posts
print('\n\n=== AGENT ECONOMY POSTS (full) ===')
r = requests.get(f'{BASE}/posts?submolt=agenteconomy&limit=20', headers=MH, timeout=15)
if r.status_code == 200:
    posts = r.json().get('posts', r.json())
    if isinstance(posts, list):
        for p in posts:
            if isinstance(p, dict):
                pid = p.get('id', '')
                t = (p.get('title', '') or '')[:70]
                a = p.get('author', {}).get('name', '?')
                u = p.get('upvotes', 0) or 0
                c = (p.get('content', '') or '')[:200]
                print(f'\n[{u}u] {t} | {a}')
                print(f'  ID: {pid}')
                print(f'  Content: {c}')
