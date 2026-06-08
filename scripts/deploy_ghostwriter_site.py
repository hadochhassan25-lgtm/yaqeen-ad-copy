"""Create GitHub repo with landing page to promote the bot"""
import urllib.request, json, base64, os

GH_TOKEN = os.environ.get('GITHUB_TOKEN', '')
headers = {
    'Accept': 'application/vnd.github.v3+json',
    'Authorization': 'token ' + GH_TOKEN,
    'User-Agent': 'yaqeen-bot',
    'Content-Type': 'application/json'
}

def req(url, data=None, method='GET'):
    body = json.dumps(data).encode() if data else None
    r = urllib.request.Request(url, data=body, headers=headers, method=method)
    return json.loads(urllib.request.urlopen(r, timeout=15).read())

repo_name = 'yaqeen-ghostwriter'
repo_full = f'hadochhassan25-lgtm/{repo_name}'

# Check if repo exists
try:
    repo = req(f'https://api.github.com/repos/{repo_full}')
    print(f'Repo exists: {repo["html_url"]}')
except:
    print('Creating repo...')
    data = {
        'name': repo_name,
        'description': 'AI Ghostwriter - Generate 7 LinkedIn posts in 2 minutes via Telegram',
        'homepage': f'https://hadochhassan25-lgtm.github.io/{repo_name}',
        'private': False,
        'has_pages': True,
        'auto_init': True
    }
    repo = req('https://api.github.com/user/repos', data, 'POST')
    print(f'Repo created: {repo["html_url"]}')

branch = repo.get('default_branch', 'main')

# Read landing page
with open(r'C:\Users\manadger\Desktop\moltbook-app\memory\yaqeen_landing.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Update index.html
sha = None
try:
    r = urllib.request.Request(f'https://api.github.com/repos/{repo_full}/contents/index.html', headers=headers)
    existing = json.loads(urllib.request.urlopen(r, timeout=15).read())
    sha = existing['sha']
    print('Existing index.html found, will update')
except:
    pass

b64_html = base64.b64encode(html.encode()).decode()
file_data = {
    'message': 'Deploy YAQEEN Ghostwriter landing page',
    'content': b64_html,
    'branch': branch
}
if sha:
    file_data['sha'] = sha

result = req(f'https://api.github.com/repos/{repo_full}/contents/index.html', file_data, 'PUT')
print(f'index.html: {result["content"]["html_url"]}')

# Update README
readme = '''# YAQEEN Ghostwriter

AI-powered LinkedIn ghostwriter. Generate 7 professional posts in 2 minutes.

## How it works

1. Open [@yaqeen_manadger_bot](https://t.me/yaqeen_manadger_bot) on Telegram
2. Send your name/business name and industry
3. Receive 7 LinkedIn posts in markdown
4. Pay $2 via PayPal or USDC

## Pricing

- **$2.00** per batch (7 posts)
- **$10.00** per 5-batch package (35 posts)
- **$50.00/month** for daily posting (140+ posts)

## Stack

- **Bot**: Python + python-telegram-bot
- **LLM**: GitHub Models (gpt-4o-mini)
- **Payment**: PayPal / USDC
- **API**: Flask

Built by [Manadger Tech S.A.R.L](https://github.com/hadochhassan25-lgtm)
'''

sha_readme = None
try:
    r = urllib.request.Request(f'https://api.github.com/repos/{repo_full}/contents/README.md', headers=headers)
    existing_r = json.loads(urllib.request.urlopen(r, timeout=15).read())
    sha_readme = existing_r['sha']
except:
    pass

b64_readme = base64.b64encode(readme.encode()).decode()
readme_data = {
    'message': 'Update README',
    'content': b64_readme,
    'branch': branch
}
if sha_readme:
    readme_data['sha'] = sha_readme

req(f'https://api.github.com/repos/{repo_full}/contents/README.md', readme_data, 'PUT')
print('README updated')

# Enable Pages
try:
    pages_data = {'source': {'branch': branch, 'path': '/'}}
    req(f'https://api.github.com/repos/{repo_full}/pages', pages_data, 'POST')
except Exception as e:
    pass

print()
print('=== LINKS ===')
print(f'Repo:  https://github.com/{repo_full}')
print(f'Pages: https://hadochhassan25-lgtm.github.io/{repo_name}')
print(f'Bot:   https://t.me/yaqeen_manadger_bot')
