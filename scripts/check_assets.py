"""Check PR #16 status and Telegram bot status"""
import urllib.request, json, sys, os

GH_TOKEN = os.environ.get('GITHUB_TOKEN', '')
TG_TOKEN = '8650825564:AAFYAViT-vDUyMOK3x427aGL4WwVD1XzGyI'
TG_BOT_ID = 8650825564

headers = {
    'Accept': 'application/vnd.github.v3+json',
    'Authorization': 'token ' + GH_TOKEN,
    'User-Agent': 'yaqeen-bot'
}

def req(url, h=headers):
    r = urllib.request.Request(url, headers=h)
    return json.loads(urllib.request.urlopen(r, timeout=15).read())

# 1. Check PR #16 status
print("=== PR #16 Status ===")
pr = req('https://api.github.com/repos/aLexzzz430/Cognitive-OS/pulls/16')
print(f"State: {pr['state']}")
print(f"Merged: {pr.get('merged')}")
print(f"Comments: {pr.get('comments', 0)}")
print(f"Reviews: {pr.get('review_comments', 0)}")
print(f"Created: {pr['created_at']}")
print(f"Updated: {pr['updated_at']}")
print()

# Check if anyone commented
comments = req(pr['comments_url'])
if comments:
    for c in comments:
        print(f"Comment by {c['user']['login']}: {c['body'][:150]}")
else:
    print("No comments yet")
print()

# 2. Check Telegram bot status
print("=== Telegram Bot Status ===")
tg_data = urllib.parse.urlencode({'timeout': 5}).encode()
tg_headers = {'Content-Type': 'application/x-www-form-urlencoded'}
try:
    r = urllib.request.Request(
        f'https://api.telegram.org/bot{TG_TOKEN}/getMe',
        headers=tg_headers
    )
    bot_info = json.loads(urllib.request.urlopen(r, timeout=10).read())
    if bot_info.get('ok'):
        bot = bot_info['result']
        print(f"Bot: @{bot['username']}")
        print(f"Name: {bot['first_name']}")
        print(f"ID: {bot['id']}")
        print(f"Can read messages: YES")
    else:
        print("Bot ERROR: " + bot_info.get('description', 'unknown'))
except Exception as e:
    print(f"Bot ERROR: {e}")
print()

# Get webhook/update info
try:
    r2 = urllib.request.Request(
        f'https://api.telegram.org/bot{TG_TOKEN}/getUpdates',
        headers=tg_headers
    )
    updates = json.loads(urllib.request.urlopen(r2, timeout=10).read())
    if updates.get('ok'):
        result = updates['result']
        print(f"Total updates since last poll: {len(result)}")
        if result:
            for u in result:
                msg = u.get('message', {})
                user = msg.get('from', {})
                print(f"  User: {user.get('first_name', '?')} (@{user.get('username', '?')}) | {msg.get('text', '?')[:50]}")
    else:
        print(f"Updates ERROR: {updates.get('description')}")
except Exception as e:
    print(f"Updates ERROR: {e}")

print()
print("=== ACTION PLAN ===")
print("1. Create GitHub repo with landing page")
print("2. Share bot link directly")
print("3. Keep PR #16 alive -- no activity yet")
