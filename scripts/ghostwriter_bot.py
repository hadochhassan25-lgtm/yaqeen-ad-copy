"""
YAQEEN Ghostwriter Telegram Bot
Income stream: $2/request via PayPal
No tunnel needed — Telegram polling
"""
import sys, os, json, time, threading, urllib.request
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

BOT_TOKEN = '8650825564:AAFYAViT-vDUyMOK3x427aGL4WwVD1XzGyI'
GH_TOKEN = os.environ.get('GITHUB_TOKEN', '')
PAYPAL = 'https://paypal.me/lamti'
WALLET = '0xD0366D78055b8c637c44d769D1A1371106d13552'
BASE = os.path.dirname(os.path.dirname(__file__))
STATE_FILE = os.path.join(BASE, 'memory', 'bot_state.json')

def api_url(method):
    return f'https://api.telegram.org/bot{BOT_TOKEN}/{method}'

def gh_ask(system, user):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + GH_TOKEN
    }
    body = json.dumps({
        'model': 'gpt-4o-mini',
        'messages': [
            {'role': 'system', 'content': system},
            {'role': 'user', 'content': user}
        ],
        'max_tokens': 2000
    }).encode()
    req = urllib.request.Request(
        'https://models.inference.ai.azure.com/chat/completions',
        data=body, headers=headers, method='POST'
    )
    r = urllib.request.urlopen(req, timeout=30)
    return json.loads(r.read())['choices'][0]['message']['content']

def telegram(method, data):
    try:
        body = json.dumps(data).encode()
        req = urllib.request.Request(api_url(method), data=body, headers={'Content-Type': 'application/json'}, method='POST')
        urllib.request.urlopen(req, timeout=10)
    except:
        pass

def send_msg(chat_id, text, parse_mode=None):
    d = {'chat_id': chat_id, 'text': text}
    if parse_mode:
        d['parse_mode'] = parse_mode
    telegram('sendMessage', d)

# Load/save user state
def load_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except:
        return {}

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

# Generate posts
def generate_posts(client, industry, platform='linkedin'):
    system = (
        f"You are YAQEEN, a professional LinkedIn ghostwriter. "
        f"Write 7 LinkedIn posts for a {industry} client named {client}. "
        f"Platform: {platform}. Tone: Bold, insightful, professional. "
        f"Each post: short paragraphs, one clear insight. "
        f"Return posts separated by '---POST---' marker. "
        f"Do NOT use emojis in the posts."
    )
    user = f"Generate 7 LinkedIn posts for {client} ({industry}). Make them high-quality and shareable."
    return gh_ask(system, user)

# Bot logic
def process_update(upd, state):
    msg = upd.get('message', {})
    chat_id = msg.get('chat', {}).get('id')
    text = msg.get('text', '').strip()
    user_id = str(chat_id)

    if not chat_id:
        return

    # /start
    if text == '/start':
        send_msg(chat_id,
            '🤖 *YAQEEN Ghostwriter*\n\n'
            'I generate 7 LinkedIn posts for your business in 2 minutes.\n\n'
            'Commands:\n'
            '/generate - Start a new batch\n'
            '/price - Pricing info\n'
            '/pay - Payment link\n'
            '/help - Help',
            parse_mode='Markdown')
        state[user_id] = {'step': 'idle'}
        save_state(state)
        return

    if text == '/price':
        send_msg(chat_id,
            '*Pricing:*\n'
            '• 7 LinkedIn posts: $2.00\n'
            '• 30 LinkedIn posts: $5.00\n'
            '• Custom batch: Contact us\n\n'
            'Pay via PayPal or USDC/ETH',
            parse_mode='Markdown')
        return

    if text == '/pay':
        send_msg(chat_id,
            f'💳 *Payment:*\n'
            f'PayPal: {PAYPAL}\n'
            f'USDC/ETH (Base): `{WALLET}`\n\n'
            f'After payment, send /generate',
            parse_mode='Markdown')
        return

    if text == '/help':
        send_msg(chat_id,
            '*How it works:*\n'
            '1. Send /generate\n'
            '2. Tell me your client name\n'
            '3. Tell me your industry\n'
            '4. I generate 7 posts\n'
            '5. Pay $2 via PayPal\n\n'
            'Built by Manadger Tech SARL',
            parse_mode='Markdown')
        return

    if text == '/generate':
        state[user_id] = {'step': 'awaiting_client'}
        save_state(state)
        send_msg(chat_id, '👋 What is the client name or your name?')
        return

    # Handle conversation steps
    user_state = state.get(user_id, {})
    step = user_state.get('step', 'idle')

    if step == 'awaiting_client':
        state[user_id] = {'step': 'awaiting_industry', 'client': text}
        save_state(state)
        send_msg(chat_id, f'Great! What industry is "{text}" in? (e.g. tech, real estate, consulting, fashion)')

    elif step == 'awaiting_industry':
        client = user_state.get('client', text)
        industry = text
        state[user_id] = {'step': 'generating', 'client': client, 'industry': industry}
        save_state(state)
        send_msg(chat_id, f'⚡ Generating 7 LinkedIn posts for *{client}* ({industry})...\n\nThis takes ~30 seconds.', parse_mode='Markdown')

        try:
            result = generate_posts(client, industry)
            posts = [p.strip() for p in result.split('---POST---') if p.strip()]

            msg_text = f'✅ *Done! 7 posts for {client}*\n\n'
            for i, post in enumerate(posts[:7], 1):
                msg_text += f'*Post {i}:*\n{post[:300]}\n\n---\n\n'
                if len(msg_text) > 3500:
                    break

            msg_text += f'\n💳 *Pay $2 to unlock the full Markdown file:*\n'
            msg_text += f'PayPal: {PAYPAL}\n'
            msg_text += f'Crypto: `{WALLET}`\n\n'
            msg_text += f'After payment, send /paydone and I\'ll deliver the complete file.'

            send_msg(chat_id, msg_text, parse_mode='Markdown')

            # Save full posts for delivery
            state[user_id] = {
                'step': 'awaiting_payment',
                'client': client,
                'industry': industry,
                'posts': posts[:7]
            }
            save_state(state)

        except Exception as e:
            send_msg(chat_id, f'❌ Error generating posts: {str(e)[:100]}\n\nPlease try /generate again.')
            state[user_id] = {'step': 'idle'}
            save_state(state)

    elif step == 'awaiting_payment':
        if text == '/paydone':
            posts = user_state.get('posts', [])
            client = user_state.get('client', 'Client')

            md = f'# LinkedIn Posts for {client}\n\n'
            for i, post in enumerate(posts, 1):
                md += f'## Post {i}\n\n{post}\n\n---\n\n'

            send_msg(chat_id, '📄 *Full Markdown File:*\n\n```\n' + md[:3500] + '\n```\n\nThank you for your payment!', parse_mode='Markdown')

            # Send remaining if too long
            if len(md) > 3500:
                remaining = md[3500:]
                for i in range(0, len(remaining), 3500):
                    send_msg(chat_id, '```\n' + remaining[i:i+3500] + '\n```')

            state[user_id] = {'step': 'idle'}
            save_state(state)
            send_msg(chat_id, 'Use /generate for another batch!')
        else:
            send_msg(chat_id, 'Use /paydone after payment, or /generate for a new batch.')

    else:
        send_msg(chat_id, 'Send /generate to start, or /help for info.')

# Main loop
def main():
    print('YAQEEN Ghostwriter Bot starting...')
    state = load_state()
    last_update = 0

    while True:
        try:
            url = api_url('getUpdates') + f'?timeout=30&offset={last_update}'
            req = urllib.request.Request(url)
            r = urllib.request.urlopen(req, timeout=35)
            data = json.loads(r.read())

            if data.get('ok') and data.get('result'):
                for upd in data['result']:
                    update_id = upd['update_id']
                    if update_id >= last_update:
                        last_update = update_id + 1
                    process_update(upd, state)
        except Exception as e:
            print(f'Poll error: {e}')
            time.sleep(3)

if __name__ == '__main__':
    main()
