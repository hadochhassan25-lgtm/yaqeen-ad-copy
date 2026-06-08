import json

raw_path = r'C:\Users\manadger\.local\share\opencode\tool-output\tool_e775e02ef0012ZUPITJicLkm7p'
with open(raw_path, 'r', encoding='utf-8') as f:
    data = json.loads(f.read())

sep = '=' * 100
print(sep)
header = f"{'REWARD':>10} | {'LANG':>20} | {'CLAIMERS':>8} | {'TRYING':>6} | REPO / TITLE"
print(header)
print(sep)

for i, b in enumerate(data):
    pp = b.get('pendingPrice', {})
    if pp and isinstance(pp, dict) and 'value' in pp:
        cents = pp['value']
        reward = cents / 100
    else:
        reward = 0

    langs = b.get('programmingLanguages', [])
    if not langs:
        langs = b.get('languages', [])
    lang_str = ','.join(langs[:3]) if langs else '?'

    claimers = len(b.get('claimerUsers', []))
    trying = len(b.get('tryingUsers', []))
    url = b.get('url', '')
    repo = url.replace('https://github.com/', '').split('/issues')[0] if 'github.com' in url else '?'
    title = b.get('title', '')[:70]

    if claimers <= 3 or reward > 500:
        flag = '🟢' if claimers == 0 else '🟡' if claimers <= 2 else '  '
        reward_str = f"${reward:>7.0f}" if reward else '     ?'
        print(f"{flag} {reward_str} | {lang_str:>20} | {claimers:>8} | {trying:>6} | {repo}")
        print(f"    {' '*36} | {title}")
