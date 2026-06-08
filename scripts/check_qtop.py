import json

raw_path = r'C:\Users\manadger\.local\share\opencode\tool-output\tool_e775e02ef0012ZUPITJicLkm7p'
with open(raw_path, 'r', encoding='utf-8') as f:
    data = json.loads(f.read())

# Find qtop bounty
for i, b in enumerate(data):
    if 'qtop' in b.get('url', ''):
        print(f"ID: {b.get('id')}")
        print(f"Title: {b.get('title')}")
        print(f"URL: {b.get('url')}")
        pp = b.get('pendingPrice', {})
        if pp:
            print(f"Reward: ${pp.get('value', 0)/100:.0f}")
        print(f"Claimers: {b.get('claimerUsers', [])}")
        print(f"Trying: {len(b.get('tryingUsers', []))}")
        if b.get('tryingUsers'):
            for u in b['tryingUsers']:
                print(f"  - {u.get('username')}")
        print()
