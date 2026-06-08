#!/usr/bin/env python3
"""Scan AgentGuard for vulnerability patterns"""
import requests, os, base64, sys
sys.stdout.reconfigure(encoding='utf-8')

token=''
for line in open(r'C:\Users\manadger\Desktop\moltbook-app\.env').read().split('\n'):
    if line.startswith('GITHUB_TOKEN='):
        token=line.split('=',1)[1].strip()
        break

h={'Authorization':f'Bearer {token}','Accept':'application/vnd.github.v3+json'}

# Get all py files recursively
r=requests.get('https://api.github.com/repos/WhitzardAgent/AgentGuard/git/trees/main?recursive=1', headers=h)
if r.status_code!=200:
    print(f'Tree error: {r.status_code}')
    exit()

tree=r.json().get('tree',[])
py_files=[f for f in tree if f['type']=='blob' and f['path'].endswith('.py')]
print(f'Total Python files: {len(py_files)}')

for item in py_files:
    path=item['path']
    if item['size']>50000:
        continue
    # Get content
    r2=requests.get(f'https://api.github.com/repos/WhitzardAgent/AgentGuard/contents/{path}', headers=h)
    if r2.status_code!=200:
        continue
    try:
        c=base64.b64decode(r2.json()['content']).decode('utf-8',errors='ignore')
        lines=c.split('\n')
        for i,line in enumerate(lines):
            low=line.lower()
            if any(k in low for k in ['exec(','eval(','subprocess','os.system','pickle.load','yaml.load(','shell=true','__import__','compile(','danger','unsafe']):
                print(f'  [!] {path}:L{i+1}: {line.strip()[:150]}')
    except:
        pass

print('Done scanning AgentGuard')
