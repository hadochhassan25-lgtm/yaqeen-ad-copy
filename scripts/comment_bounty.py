#!/usr/bin/env python3
"""Comment on the AGI bounty issue to claim it"""
import sys, os, io
import requests

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

TOKEN = os.environ.get('GITHUB_TOKEN', '')
HEADERS = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}

def api(url, method="GET", data=None):
    r = requests.request(method, url, headers=HEADERS, json=data)
    status = r.status_code
    if status >= 400:
        print(f"{method} {url}: HTTP {status} - {r.text[:200]}")
        return None
    return r.json() if r.text else {"status": status}

# Comment /attempt on the issue
print("[1] Commenting /attempt on issue #5...")
result = api(
    "https://api.github.com/repos/aLexzzz430/Cognitive-OS/issues/5/comments",
    "POST",
    {"body": "/attempt\n\nStarting work on AGI architecture research collection."}
)
if result:
    print(f"  Comment posted: {result.get('id', 'OK')}")

# Comment /claim with PR link
print("[2] Commenting /claim on issue #5...")
result = api(
    "https://api.github.com/repos/aLexzzz430/Cognitive-OS/issues/5/comments",
    "POST",
    {"body": "/claim\n\nPR submitted: https://github.com/aLexzzz430/Cognitive-OS/pull/16"}
)
if result:
    print(f"  Comment posted: {result.get('id', 'OK')}")

print("\nDone! Bounty claimed.")
