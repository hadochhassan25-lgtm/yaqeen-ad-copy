#!/usr/bin/env python3
"""Quick scan - just list key Python files in promising repos"""
import requests, os, sys
sys.stdout.reconfigure(encoding='utf-8')

token = ''
env_path = r'C:\Users\manadger\Desktop\moltbook-app\.env'
for line in open(env_path).read().split('\n'):
    line = line.strip()
    if line.startswith('GITHUB_TOKEN='):
        token = line.split('=', 1)[1].strip()
        break

headers = {'Authorization': f'Bearer {token}', 'Accept': 'application/vnd.github.v3+json'}

# Just list all Python files in AgentGuard (most promising)
print('=== AgentGuard Python files ===')
r = requests.get('https://api.github.com/repos/WhitzardAgent/AgentGuard/git/trees/main?recursive=1', headers=headers)
if r.status_code != 200:
    r = requests.get('https://api.github.com/repos/WhitzardAgent/AgentGuard/git/trees/master?recursive=1', headers=headers)

if r.status_code == 200:
    tree = r.json().get('tree', [])
    py_files = [f['path'] for f in tree if f['type'] == 'blob' and f['path'].endswith('.py')]
    # key files related to execution
    key = [f for f in py_files if any(k in f.lower() for k in ['exec', 'eval', 'agent', 'tool', 'execut', 'sandbox', 'shell', 'command', 'run', 'action', 'plugin'])]
    for f in key:
        print(f'  {f}')
    print(f'Total Python: {len(py_files)}')
    print(f'Key files: {len(key)}')
    
    # Read the most interesting ones
    for f in key[:3]:
        r2 = requests.get(f'https://api.github.com/repos/WhitzardAgent/AgentGuard/contents/{f}', headers=headers)
        if r2.status_code == 200:
            import base64
            content = base64.b64decode(r2.json().get('content', '')).decode('utf-8', errors='ignore')
            # Show first/last lines
            lines = content.split('\n')
            print(f'\n  --- {f} ({len(lines)} lines) ---')
            # Look for dangerous patterns
            for i, line in enumerate(lines):
                if any(k in line.lower() for k in ['exec(', 'eval(', 'subprocess', 'os.system', '__import__', 'pickle.load', 'yaml.load(', 'shell=true']):
                    print(f'  [!] L{i+1}: {line.strip()[:120]}')

print()

# Also check vantyx-ai
print('=== Vantyx AI Python files ===')
r = requests.get('https://api.github.com/repos/felipebridge/vantyx-ai/git/trees/main?recursive=1', headers=headers)
if r.status_code != 200:
    r = requests.get('https://api.github.com/repos/felipebridge/vantyx-ai/git/trees/master?recursive=1', headers=headers)
if r.status_code == 200:
    tree = r.json().get('tree', [])
    py_files = [f['path'] for f in tree if f['type'] == 'blob' and f['path'].endswith('.py')]
    for f in py_files:
        r2 = requests.get(f'https://api.github.com/repos/felipebridge/vantyx-ai/contents/{f}', headers=headers)
        if r2.status_code == 200:
            import base64
            content = base64.b64decode(r2.json().get('content', '')).decode('utf-8', errors='ignore')
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if any(k in line.lower() for k in ['exec(', 'eval(', 'subprocess', 'os.system', '__import__', 'pickle.load', 'yaml.load(', 'shell=true']):
                    print(f'  [!] {f}:L{i+1}: {line.strip()[:120]}')
