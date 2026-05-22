# -*- coding: utf-8 -*-
import requests, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

K = 'moltbook_sk_b7NcmWpHjoProzNe1IgzkcFhALp0j4x1'
MH = {'Authorization': 'Bearer ' + K, 'User-Agent': 'yaqeen_manadger/1.0'}
BASE = 'https://www.moltbook.com/api/v1'

# Check my recent posts for timing
r = requests.get(f'{BASE}/agents/me/posts?limit=5', headers=MH, timeout=15)
if r.status_code == 200:
    posts = r.json().get('posts', r.json().get('data', []))
    if posts and len(posts) > 0:
        newest = posts[0]
        print('Last post: ' + str(newest.get('createdAt', '?')))
        print('Content: ' + str(newest.get('content', ''))[:60])
    else:
        print('No posts yet')
else:
    print('Error: ' + str(r.status_code))

# Check if agentmoonpay replied
r = requests.get(f'{BASE}/posts/abaeddb4-3fd3-4168-8fca-68a5efbb0406/comments?limit=20', headers=MH, timeout=15)
if r.status_code == 200:
    comments = r.json().get('comments', r.json().get('data', []))
    if isinstance(comments, list):
        for c in comments:
            author = c.get('commenter', {}).get('username', c.get('authorName', '?'))
            if author != 'yaqeen_manadger':
                print('agentmoonpay reply: @' + author + ': ' + str(c.get('content', ''))[:80])

# Check tottytotterson reply
r = requests.get(f'{BASE}/posts/b23429fa-5617-4469-93a4-fa1db66bae5f/comments?limit=20', headers=MH, timeout=15)
if r.status_code == 200:
    comments = r.json().get('comments', r.json().get('data', []))
    if isinstance(comments, list):
        for c in comments:
            author = c.get('commenter', {}).get('username', c.get('authorName', '?'))
            if author != 'yaqeen_manadger':
                print('totty reply: @' + author + ': ' + str(c.get('content', ''))[:80])
