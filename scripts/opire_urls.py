import json

raw_path = r'C:\Users\manadger\.local\share\opencode\tool-output\tool_e775e02ef0012ZUPITJicLkm7p'
with open(raw_path, 'r', encoding='utf-8') as f:
    data = json.loads(f.read())

for i, b in enumerate(data):
    claimers = len(b.get('claimerUsers', []))
    if claimers > 3:
        continue
    url = b.get('url', '?')
    title = b.get('title', '?')[:60]
    pp = b.get('pendingPrice', {})
    langs = b.get('programmingLanguages', [])
    lang_str = ','.join(langs[:3]) if langs else '?'
    if pp and isinstance(pp, dict) and 'value' in pp:
        reward = "${:.0f}".format(pp['value']/100)
    else:
        reward = '?'
    print(f"{reward:>8} | {lang_str:>15} | {claimers} claimers | {url}")
    print(f"    {title}")
    print()
