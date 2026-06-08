import requests, json, os

url = 'https://api.github.com/repos/aLexzzz430/Cognitive-OS/pulls/16'
headers = {'Authorization': 'Bearer ' + os.environ.get('GITHUB_TOKEN', '')}
try:
    r = requests.get(url, headers=headers, timeout=10)
    if r.status_code == 200:
        d = r.json()
        state = "OPEN" if d['state'] == 'open' else "CLOSED"
        merged = "YES" if d.get('merged') else "NO"
        result = f"PR #{d['number']} | State: {state} | Merged: {merged}"
        result += f"\nTitle: {d['title']}"
        result += f"\nCreated: {d['created_at']}"
        result += f"\nUpdated: {d['updated_at']}"
        result += f"\nComments: {d['comments']} | Review Comments: {d['review_comments']}"
        result += f"\nChanges: +{d['additions']}/-{d['deletions']} across {d['commits']} commits"
        if d.get('merged_by'):
            result += f"\nMerged by: {d['merged_by']['login']}"
        print(result)
    else:
        print(f"HTTP {r.status_code}: {r.text[:300]}")
except Exception as e:
    print(f"Error: {e}")
