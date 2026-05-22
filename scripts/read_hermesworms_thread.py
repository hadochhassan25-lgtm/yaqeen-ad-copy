import requests, json

API = 'https://www.moltbook.com/api/v1'
KEY = 'moltbook_sk_b7NcmWpHjoProzNe1IgzkcFhALp0j4x1'
h = {'X-API-Key': KEY}
pid = 'abaeddb4-3fd3-4168-8fca-68a5efbb0406'

# Get notifications to find hermesworms reply
r = requests.get(API + '/notifications', headers=h, timeout=30)
if r.status_code == 200:
    data = r.json()
    for n in data.get('notifications', data if isinstance(data, list) else []):
        if isinstance(n, dict) and n.get('relatedPostId') == pid:
            print('Notification:', n.get('type'))
            print('  Content:', n.get('content'))
            print('  Created:', n.get('createdAt'))
            if n.get('post'):
                print('  Author ID:', n.get('post', {}).get('authorId'))
            if n.get('actor'):
                print('  Actor:', n.get('actor'))
            print()
else:
    print('Notif error:', r.status_code)

# Get full comments with agent names
r = requests.get(API + '/posts/' + pid + '/comments', headers=h, timeout=60)
if r.status_code == 200:
    comments = r.json()
    if isinstance(comments, dict):
        comments = comments.get('comments', [])
    print(f'Total comments: {len(comments)}')
    print()
    for i, c in enumerate(comments):
        agent = c.get('agent', {})
        if isinstance(agent, dict):
            name = agent.get('name', 'unknown')
        else:
            name = str(agent)
        content = c.get('content', '')[:500]
        created = c.get('createdAt', '')[:19]
        print(f'#{i} [{created}] {name}:')
        print(content)
        print()
else:
    print('Comments error:', r.status_code, r.text[:300])
