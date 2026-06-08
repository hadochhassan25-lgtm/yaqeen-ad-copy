"""Scrape Opire homepage for visible bounties"""
import urllib.request, re, json

r = urllib.request.urlopen(urllib.request.Request(
    'https://opire.dev/home',
    headers={'User-Agent': 'Mozilla/5.0'}
), timeout=10)
html = r.read().decode('utf-8', errors='replace')

# Find GitHub issue links
links = re.findall(r'https://github\.com/[^/"\'\\]+/[^/"\'\\]+/issues/\d+', html)
print(f'GitHub issues found: {len(links)}')
for l in links:
    print(f'  {l}')

# Find amounts near issue patterns
amounts = re.findall(r'\$([0-9,]+\.?[0-9]*)', html)
print(f'\nAmounts found: {amounts[:15]}')

# Pair amounts with nearby text
lines = html.split('\n')
print(f'\nHTML lines: {len(lines)}')
for i, line in enumerate(lines):
    if '$' in line and any(lang in line for lang in ['Python','TypeScript','Rust','C++','JavaScript']):
        clean = re.sub(r'<[^>]+>', ' ', line).strip()
        if clean:
            print(f'L{i}: {clean[:150]}')
    if 'github.com' in line and 'issues' in line:
        clean = re.sub(r'<[^>]+>', ' ', line).strip()
        print(f'L{i}: {clean[:200]}')
