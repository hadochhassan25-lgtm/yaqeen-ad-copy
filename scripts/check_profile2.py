# -*- coding: utf-8 -*-
import requests, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

K = 'moltbook_sk_b7NcmWpHjoProzNe1IgzkcFhALp0j4x1'
MH = {'Authorization': 'Bearer ' + K, 'User-Agent': 'yaqeen_manadger/1.0'}
BASE = 'https://www.moltbook.com/api/v1'

TIMEOUT = 60

# Get my agent profile
r = requests.get(f'{BASE}/agents/me', headers=MH, timeout=TIMEOUT)
print('GET /agents/me: ' + str(r.status_code))
if r.status_code == 200:
    me = r.json().get('agent', r.json())
    print('Karma: ' + str(me.get('karma', '?')))
    print('Comments: ' + str(me.get('commentsCount', me.get('comments_count', '?'))))
    agent_id = me.get('id', '')
    if agent_id:
        r2 = requests.get(f'{BASE}/posts?authorId={agent_id}&limit=3', headers=MH, timeout=TIMEOUT)
        print('GET posts: ' + str(r2.status_code))
        if r2.status_code == 200:
            posts = r2.json().get('posts', r2.json().get('data', []))
            if posts and len(posts) > 0:
                newest = posts[0]
                print('Last post time: ' + str(newest.get('createdAt', '?')))
else:
    print(r.text[:200])
