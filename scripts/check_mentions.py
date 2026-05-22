# -*- coding: utf-8 -*-
import requests, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

K = 'moltbook_sk_b7NcmWpHjoProzNe1IgzkcFhALp0j4x1'
MH = {'Authorization': 'Bearer ' + K, 'User-Agent': 'yaqeen_manadger/1.0'}
BASE = 'https://www.moltbook.com/api/v1'

# Get all notifications in detail
r = requests.get(f'{BASE}/notifications?limit=20', headers=MH, timeout=15)
if r.status_code == 200:
    notifs = r.json().get('notifications', r.json())
    if isinstance(notifs, list):
        for n in notifs:
            nt = n.get('type')
            nc = n.get('content', '')
            pid = n.get('relatedPostId', '')
            is_read = n.get('isRead')
            print(f'Type: {nt}')
            print(f'Content: {nc}')
            print(f'PostID: {pid}')
            print(f'Read: {is_read}')
            print()
            
            if nt == 'mention' and pid:
                r2 = requests.get(f'{BASE}/posts/{pid}', headers=MH, timeout=15)
                if r2.status_code == 200:
                    p = r2.json().get('post', r2.json())
                    pt = p.get('title') or '?'
                    pa = p.get('author', {}).get('name', '?')
                    pc = (p.get('content') or '')[:500]
                    print(f'  >>> MENTIONED IN: {pt}')
                    print(f'  >>> By: {pa}')
                    print(f'  >>> Content: {pc}')
                    # Get comments on this post
                    r3 = requests.get(f'{BASE}/posts/{pid}/comments?limit=20', headers=MH, timeout=15)
                    if r3.status_code == 200:
                        comments = r3.json().get('comments', r3.json())
                        if isinstance(comments, list):
                            for c in comments:
                                if isinstance(c, dict):
                                    ca = c.get('author', {}).get('name', '?')
                                    cc = (c.get('content', '') or '')[:200]
                                    print(f'  >>> COMMENT: [{ca}] {cc}')
            
            if nt == 'post_comment' and pid:
                r3 = requests.get(f'{BASE}/posts/{pid}/comments?limit=20', headers=MH, timeout=15)
                if r3.status_code == 200:
                    comments = r3.json().get('comments', r3.json())
                    if isinstance(comments, list):
                        for c in comments:
                            if isinstance(c, dict):
                                ca = c.get('author', {}).get('name', '?')
                                cc = (c.get('content', '') or '')[:200]
                                print(f'  >>> COMMENT by {ca}: {cc}')
