# -*- coding: utf-8 -*-
import requests, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

K = 'moltbook_sk_b7NcmWpHjoProzNe1IgzkcFhALp0j4x1'
MH = {'Authorization': 'Bearer ' + K, 'User-Agent': 'yaqeen_manadger/1.0'}
BASE = 'https://www.moltbook.com/api/v1'

# Get my agent profile
r = requests.get(f'{BASE}/agents/me', headers=MH, timeout=15)
if r.status_code == 200:
    me = r.json().get('agent', r.json())
    print('Karma: ' + str(me.get('karma', '?')))
    print('Posts: ' + str(me.get('postsCount', me.get('posts_count', '?'))))
    print('Comments: ' + str(me.get('commentsCount', me.get('comments_count', '?'))))
    print('Followers: ' + str(me.get('followerCount', me.get('follower_count', '?'))))
    agent_id = me.get('id', '')
    if agent_id:
        # Get my posts
        r2 = requests.get(f'{BASE}/posts?authorId={agent_id}&limit=5', headers=MH, timeout=15)
        if r2.status_code == 200:
            posts = r2.json().get('posts', r2.json().get('data', []))
            if posts and len(posts) > 0:
                newest = posts[0]
                print('Last post ID: ' + str(newest.get('id', '?')))
                print('Last post time: ' + str(newest.get('createdAt', '?')))
else:
    print('Error: ' + str(r.status_code) + ' ' + r.text[:200])
