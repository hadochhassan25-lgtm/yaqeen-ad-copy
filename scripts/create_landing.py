"""
Create GitHub Pages landing page for YAQEEN Ghostwriter Bot
"""
import os, base64, urllib.request, json

GH_TOKEN = os.environ.get('GITHUB_TOKEN', '')
BASE = r'C:\Users\manadger\Desktop\moltbook-app'

# Create index.html for GitHub Pages
html = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>YAQEEN — AI Ghostwriter</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0a0a0f;color:#e0e0e0;font-family:system-ui,-apple-system,sans-serif;min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:2rem}
.card{background:#12121e;border:1px solid #2a2a3e;border-radius:16px;padding:3rem;max-width:600px;width:100%;text-align:center}
h1{font-size:2.5rem;font-weight:800;background:linear-gradient(135deg,#00d4ff,#7b2ff7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:0.5rem}
.tagline{color:#888;font-size:1.1rem;margin-bottom:2rem}
.features{text-align:left;margin:2rem 0;padding:1rem;background:#0e0e18;border-radius:12px}
.features li{list-style:none;padding:0.5rem 0;color:#b0b0c0}
.features li::before{content:"\\2713\\0020";color:#00d4ff}
.btn{display:inline-block;padding:1rem 2.5rem;background:linear-gradient(135deg,#00d4ff,#7b2ff7);color:white;text-decoration:none;border-radius:8px;font-weight:600;font-size:1.1rem;transition:transform 0.2s;margin:0.5rem}
.btn:hover{transform:translateY(-2px)}
.price{font-size:2rem;font-weight:700;color:#00d4ff;margin:1.5rem 0}
.price small{font-size:1rem;color:#888}
.footer{margin-top:2rem;color:#555;font-size:0.85rem}
</style>
</head>
<body>
<div class="card">
<h1>YAQEEN</h1>
<div class="tagline">AI Ghostwriter — 7 LinkedIn Posts in 2 Minutes</div>
<div class="features">
<ul>
<li>Generate 7 high-quality LinkedIn posts</li>
<li>Tailored to your industry and voice</li>
<li>No subscriptions — pay per batch</li>
<li>Markdown format, ready to post</li>
</ul>
</div>
<div class="price">$2.00 <small>per batch</small></div>
<a class="btn" href="https://t.me/yaqeen_manadger_bot" target="_blank">Open Telegram Bot</a>
<a class="btn" href="https://paypal.me/lamti" target="_blank" style="background:linear-gradient(135deg,#0070ba,#005c99)">PayPal</a>
<div class="features" style="margin-top:1.5rem;font-size:0.9rem">
<p><strong>How it works:</strong></p>
<ol style="padding-left:1.2rem;color:#b0b0c0">
<li style="padding:0.3rem 0">Send /start to @yaqeen_manadger_bot on Telegram</li>
<li style="padding:0.3rem 0">Tell us your name/business and industry</li>
<li style="padding:0.3rem 0">Receive 7 LinkedIn posts in 30 seconds</li>
<li style="padding:0.3rem 0">Pay $2 via PayPal or USDC</li>
</ol>
</div>
<div class="footer">Built by Manadger Tech S.A.R.L &bull; 2026</div>
</div>
</body>
</html>'''

# Create CNAME for custom domain
# Write to memory first
outpath = os.path.join(BASE, 'memory', 'yaqeen_landing.html')
with open(outpath, 'w', encoding='utf-8') as f:
    f.write(html)

print('Landing page created: ' + outpath)
print('Size: ' + str(len(html)) + ' chars')

# Try to create a GitHub repo for this
import subprocess
print('')
print('To publish:')
print('1. Go to github.com/hadochhassan25-lgtm')
print('2. Create repo: yaqeen-ghostwriter')
print('3. Enable GitHub Pages')
print('4. Push index.html')
print('')
print('Or just share the Telegram bot link: https://t.me/yaqeen_manadger_bot')
