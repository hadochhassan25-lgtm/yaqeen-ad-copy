#!/usr/bin/env python3
"""Ping PR #16 via GitHub API"""
import requests, os

token = ''
env_path = r'C:\Users\manadger\Desktop\moltbook-app\.env'
for line in open(env_path).read().split('\n'):
    line = line.strip()
    if line.startswith('GITHUB_TOKEN='):
        token = line.split('=', 1)[1].strip()
        break

headers = {'Authorization': f'Bearer {token}', 'Accept': 'application/vnd.github.v3+json'}

r = requests.get('https://api.github.com/repos/aLexzzz430/Cognitive-OS/pulls/16', headers=headers)
pr = r.json()
print(f'Title: {pr.get("title")}')
print(f'State: {pr.get("state")}')
print(f'Merged: {pr.get("merged")}')
print(f'Comments: {pr.get("comments")}')
print(f'Updated: {pr.get("updated_at")}')

if not pr.get('merged') and pr.get('state') == 'open':
    comment_body = 'Hi @aLexzzz430, just checking in on this PR. All 12 models across 6 families have been submitted and tested. Is there anything else needed before merging?'
    r2 = requests.post(
        f'https://api.github.com/repos/aLexzzz430/Cognitive-OS/issues/16/comments',
        headers=headers,
        json={'body': comment_body}
    )
    if r2.status_code == 201:
        print(f'Ping comment added! ID: {r2.json().get("id")}')
    else:
        print(f'Failed to comment: HTTP {r2.status_code} - {r2.text[:200]}')
else:
    print('PR already merged or closed')
