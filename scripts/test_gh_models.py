"""Test GitHub Models API key"""
import urllib.request, json, os

gh_token = os.environ.get('GITHUB_TOKEN', '')
headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + gh_token
}
body = json.dumps({
    'model': 'gpt-4o-mini',
    'messages': [{'role': 'user', 'content': 'Say hello in one word'}],
    'max_tokens': 10
}).encode()

req = urllib.request.Request(
    'https://models.inference.ai.azure.com/chat/completions',
    data=body,
    headers=headers,
    method='POST'
)
try:
    r = urllib.request.urlopen(req, timeout=15)
    data = json.loads(r.read())
    msg = data['choices'][0]['message']['content']
    print('GitHub Models: OK')
    print('Response: ' + msg)
except Exception as e:
    print('GitHub Models FAIL: ' + str(e))
    if hasattr(e, 'read'):
        print('Body: ' + e.read().decode()[:300])
