import requests, json

API = 'https://www.moltbook.com/api/v1'
KEY = 'moltbook_sk_b7NcmWpHjoProzNe1IgzkcFhALp0j4x1'
h = {'X-API-Key': KEY}

# Search for hermesworms private key post
r = requests.get(f'{API}/search?q=hermesworms+private+key&type=posts', headers=h, timeout=10)
if r.status_code != 200:
    print('Search error:', r.status_code, r.text[:200])
    exit()

results = r.json().get('results', [])
if not results:
    print('No posts found for hermesworms private key')
    # Try searching by agent name
    r = requests.get(f'{API}/agents/profile?name=hermesworms', headers=h, timeout=10)
    if r.status_code == 200:
        agent = r.json().get('agent', {})
        print('hermesworms profile:', agent.get('posts_count', 0), 'posts')
        print(json.dumps(agent, indent=2)[:500])
    exit()

pid = results[0].get('id', '')
print('Found post:', pid, '-', results[0].get('title', '')[:80])

# Read post
r = requests.get(f'{API}/posts/{pid}', headers=h, timeout=10)
if r.status_code == 200:
    p = r.json().get('post', {})
    print('Content:', p.get('content', '')[:500])
    print()

# Read comments
r = requests.get(f'{API}/posts/{pid}/comments', headers=h, timeout=10)
if r.status_code == 200:
    print('=== Comments ===')
    for c in r.json().get('comments', []):
        a = c.get('agent', {}).get('name', '?')
        content = c.get('content', '')[:300]
        print(f'{a}: {content}')
        print()
