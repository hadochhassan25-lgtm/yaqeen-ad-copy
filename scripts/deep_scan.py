#!/usr/bin/env python3
"""Deep scan promising repos for vulnerabilities"""
import requests, os, sys, json
sys.stdout.reconfigure(encoding='utf-8')

token = ''
env_path = r'C:\Users\manadger\Desktop\moltbook-app\.env'
for line in open(env_path).read().split('\n'):
    line = line.strip()
    if line.startswith('GITHUB_TOKEN='):
        token = line.split('=', 1)[1].strip()
        break

headers = {'Authorization': f'Bearer {token}', 'Accept': 'application/vnd.github.v3+json'}

# Deep scan AgentGuard (most promising - 62 stars, Python, security)
repos = [
    ('WhitzardAgent/AgentGuard', 'AgentGuard'),
    ('SynapCores/synapcores-agent', 'SynapCores'),
    ('felipebridge/vantyx-ai', 'Vantyx'),
]

for owner_repo, name in repos:
    print(f'\n========== {name} ({owner_repo}) ==========')
    
    # Get the repo's file tree
    r = requests.get(f'https://api.github.com/repos/{owner_repo}/git/trees/main?recursive=1', headers=headers)
    if r.status_code != 200:
        r = requests.get(f'https://api.github.com/repos/{owner_repo}/git/trees/master?recursive=1', headers=headers)
        if r.status_code != 200:
            print(f'  Could not get tree: HTTP {r.status_code}')
            continue
    
    tree = r.json().get('tree', [])
    
    # Look for vulnerability patterns
    vuln_keywords = ['exec', 'eval', 'subprocess', 'os.system', 'pickle', 'yaml.load',
                     '__import__', 'compile(', 'request.get', 'request.post',
                     'shell=True', 'danger', 'unsafe']
    
    dang_files = []
    for item in tree:
        path = item['path']
        if item['type'] != 'blob':
            continue
        if not path.endswith('.py'):
            continue
        
        # Check filename for danger signs
        if any(k in path.lower() for k in ['exec', 'eval', 'agent', 'tool', 'action', 'command', 'sandbox']):
            dang_files.append(path)
        
        # Check file for short content that's suspicious
        if item.get('size', 0) < 50000:  # only scan reasonably sized files
            r2 = requests.get(f'https://api.github.com/repos/{owner_repo}/contents/{path}', headers=headers)
            if r2.status_code == 200:
                try:
                    import base64
                    content = base64.b64decode(r2.json().get('content', '')).decode('utf-8', errors='ignore')
                    for kw in vuln_keywords:
                        if kw in content.lower():
                            # Find the line
                            lines = content.split('\n')
                            for i, line in enumerate(lines):
                                if kw in line.lower():
                                    print(f'  [!] {path}:{i+1} - {kw} found: {line.strip()[:100]}')
                                    break
                            break
                except:
                    pass
    
    if dang_files:
        print(f'  Key files to investigate: {dang_files[:10]}')
    
    py_files = [f['path'] for f in tree if f['type'] == 'blob' and f['path'].endswith('.py')]
    print(f'  Total Python files: {len(py_files)}')
