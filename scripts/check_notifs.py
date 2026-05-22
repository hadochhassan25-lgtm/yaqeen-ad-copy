# -*- coding: utf-8 -*-
import requests, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

K = 'moltbook_sk_b7NcmWpHjoProzNe1IgzkcFhALp0j4x1'
MH = {'Authorization': 'Bearer ' + K, 'User-Agent': 'yaqeen_manadger/1.0'}
BASE = 'https://www.moltbook.com/api/v1'

r = requests.get(f'{BASE}/notifications?limit=20&unreadOnly=true', headers=MH, timeout=15)
if r.status_code == 200:
    notifs = r.json().get('notifications', r.json())
    if isinstance(notifs, list):
        print(f'Unread notifications: {len(notifs)}')
        for n in notifs:
            ntype = n.get('type', '?')
            content = n.get('content', '')
            pid = n.get('postId', '')
            cid = n.get('commentId', '')
            cname = n.get('commenterName', n.get('actorName', ''))
            print(f'  [{ntype}] {content[:100]}')
            if pid: print(f'    postId: {pid}')
            if cname: print(f'    by: {cname}')
    else:
        print(json.dumps(notifs, ensure_ascii=False)[:500])
else:
    print(f'Error: {r.status_code}')
