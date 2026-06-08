import urllib.request, json

token = '8650825564:AAFYAViT-vDUyMOK3x427aGL4WwVD1XzGyI'
r = urllib.request.Request(
    'https://api.telegram.org/bot' + token + '/getUpdates',
    headers={'User-Agent': 'Mozilla/5.0'}
)
resp = urllib.request.urlopen(r, timeout=15)
data = json.loads(resp.read())
results = data.get('result', [])
print('Bot updates count:', len(results))
for update in results[-5:]:
    msg = update.get('message', {})
    chat = msg.get('chat', {})
    username = chat.get('username', '?')
    text = (msg.get('text') or '')[:100]
    print('  From @' + str(username) + ': ' + text)

print()
r2 = urllib.request.Request(
    'https://api.telegram.org/bot' + token + '/getMe',
    headers={'User-Agent': 'Mozilla/5.0'}
)
resp2 = urllib.request.urlopen(r2, timeout=15)
data2 = json.loads(resp2.read())
bot = data2.get('result', {})
print('Bot:', bot.get('first_name'), '@' + bot.get('username'))
