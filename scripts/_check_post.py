import requests, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

KEY = 'moltbook_sk_b7NcmWpHjoProzNe1IgzkcFhALp0j4x1'
H = {'Authorization': 'Bearer ' + KEY, 'User-Agent': 'yaqeen_manadger/1.0'}

r = requests.get('https://www.moltbook.com/api/v1/posts/403b2f4b-56da-4fe5-919d-00c812d1ecec', headers=H, timeout=15)
if r.status_code == 200:
    d = r.json()
    p = d.get('post', d)
    title = p.get('title', '')
    ver = p.get('verification_status', 'verified')
    ups = p.get('upvotes', 0)
    print('Title: ' + title)
    print('Verification: ' + ver)
    print('Upvotes: ' + str(ups))
    print('Link: https://www.moltbook.com/p/403b2f4b-56da-4fe5-919d-00c812d1ecec')
else:
    print('Error: ' + str(r.status_code) + ' ' + r.text[:200])
