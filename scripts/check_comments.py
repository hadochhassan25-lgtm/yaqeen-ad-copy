# -*- coding: utf-8 -*-
import requests, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

K = 'moltbook_sk_b7NcmWpHjoProzNe1IgzkcFhALp0j4x1'
MH = {'Authorization': 'Bearer ' + K, 'User-Agent': 'yaqeen_manadger/1.0'}
BASE = 'https://www.moltbook.com/api/v1'

# Check both my posts for comments
for pid in ['118f67ea-5a1d-4bd1-8c8e-8355beac7ecb', 'c19afd51-753b-4e1f-9d12-3bf816392543']:
    r = requests.get(f'{BASE}/posts/{pid}/comments?limit=20', headers=MH, timeout=15)
    if r.status_code == 200:
        comments = r.json().get('comments', r.json())
        if isinstance(comments, list):
            print(f'Post {pid[:12]}... ({len(comments)} comments):')
            for c in comments:
                author = c.get('commenter', {}).get('username', c.get('authorName', '?'))
                content = c.get('content', '')[:80]
                print(f'  @{author}: {content}')
        else:
            print(f'Post {pid[:12]}...: {json.dumps(comments, ensure_ascii=False)[:200]}')
    else:
        print(f'Error {pid[:12]}...: {r.status_code}')
