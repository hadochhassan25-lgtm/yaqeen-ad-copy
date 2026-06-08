#!/usr/bin/env python3
"""Scan new GitHub repos for potential vulnerabilities"""
import requests, os, sys, json
sys.stdout.reconfigure(encoding='utf-8')

token = ''
env_path = r'C:\Users\manadger\Desktop\moltbook-app\.env'
for line in open(env_path).read().split('\n'):
    line = line.strip()
    if line.startswith('GITHUB_TOKEN='):
        token = line.split('=', 1)[1].strip()
        break

headers = {'Accept': 'application/vnd.github.v3+json'}
if token:
    headers['Authorization'] = f'Bearer {token}'

# Scan specific promising repos for vulnerability patterns
targets = [
    # High stars, AI agent frameworks
    ('modelstudioai/cli', 'Model Studio CLI'),
    ('SynapCores/synapcores-agent', 'SynapCores Agent'),
    ('felipebridge/vantyx-ai', 'Vantyx AI'),
    # Security tools we can exploit
    ('WhitzardAgent/AgentGuard', 'AgentGuard ABAC'),
    ('Jingyi-u/model_safety_eval', 'Model Safety Eval'),
    # MCP servers
    ('Aimino-Tech/opendocswork-mcp', 'OpenDocsWork MCP'),
    ('Nonanti/narwhal', 'Narwhal MCP'),
]

for owner_repo, name in targets:
    print(f'\n=== {name} ({owner_repo}) ===')
    # Get repo info
    r = requests.get(f'https://api.github.com/repos/{owner_repo}', headers=headers)
    if r.status_code != 200:
        print(f'  Repo not found: HTTP {r.status_code}')
        continue
    repo = r.json()
    print(f'  Stars: {repo.get("stargazers_count")}, Language: {repo.get("language")}, Updated: {repo.get("updated_at")}')
    
    # Get languages
    r2 = requests.get(repo['languages_url'], headers=headers)
    langs = r2.json() if r2.status_code == 200 else {}
    print(f'  Languages: {list(langs.keys())[:3]}')
    
    # Get key files via contents API (top level)
    r3 = requests.get(repo['contents_url'].replace('{+path}', ''), headers=headers)
    if r3.status_code == 200:
        files = [f['name'] for f in r3.json()]
        interesting = [f for f in files if any(k in f.lower() for k in ['exec', 'eval', 'shell', 'danger', 'unsafe', 'vuln', 'agent'])]
        if interesting:
            print(f'  Interesting files: {interesting}')
        # Check for setup.py/requirements.txt
        py_files = [f for f in files if f.endswith('.py')]
        print(f'  Python files: {len(py_files)}')
