"""Test Telegram bot"""
import urllib.request, json

token = '8650825564:AAFYAViT-vDUyMOK3x427aGL4WwVD1XzGyI'

# Get bot info
r = urllib.request.urlopen('https://api.telegram.org/bot' + token + '/getMe', timeout=10)
data = json.loads(r.read())
print('Bot: @' + data['result']['username'])

# Check if getting updates
r2 = urllib.request.urlopen('https://api.telegram.org/bot' + token + '/getUpdates?limit=1', timeout=10)
updates = json.loads(r2.read())
print('Updates pending: ' + str(len(updates.get('result', []))))
print('Bot is LIVE!')
