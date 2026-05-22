#!/usr/bin/env python3
"""YAQEEN Telegram Bot — Manadger Tech S.A.R.L"""
import os, sys, json, time, threading, io
from datetime import datetime
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

try:
    import telebot
except ImportError:
    print("[!] pip install pyTelegramBotAPI"); sys.exit(1)

BASE = Path(__file__).resolve().parent.parent
ENV = BASE / '.env'
RELAY = BASE / 'memory' / 'telegram_relay.json'

def env_load():
    t, o = None, None
    if ENV.exists():
        with open(ENV, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line: continue
                k, v = line.split('=', 1)
                k, v = k.strip(), v.strip().strip('"').strip("'")
                if k == 'TELEGRAM_BOT_TOKEN': t = v
                elif k == 'TELEGRAM_OWNER_ID':
                    try: o = int(v)
                    except: o = v
    return t, o

TOKEN, OWNER = env_load()
if not TOKEN:
    print("TELEGRAM_BOT_TOKEN not set"); sys.exit(1)

bot = telebot.TeleBot(TOKEN)
RELAY.parent.mkdir(parents=True, exist_ok=True)

def rload():
    if RELAY.exists():
        try: return json.loads(RELAY.read_text('utf-8'))
        except: pass
    return {"next_id": 1, "inbox": [], "outbox": []}

def rsave(d):
    RELAY.write_text(json.dumps(d, ensure_ascii=False, indent=2), 'utf-8')

def push_inbox(text):
    d = rload()
    d["inbox"].append({"id": d["next_id"] if d["next_id"] else 1, "text": text, "ts": datetime.now().isoformat(), "status": "pending"})
    d["next_id"] = d["next_id"] + 1 if d["next_id"] else 2
    rsave(d)
    return d["next_id"] - 1

def pop_outbox():
    d = rload()
    for r in d["outbox"]:
        if not r.get("sent"):
            r["sent"] = True
            rsave(d)
            return r
    return None

def outbox_loop():
    while True:
        try:
            r = pop_outbox()
            if r and r.get("cid") and r.get("text"):
                try: bot.send_message(r["cid"], r["text"])
                except: pass
        except: pass
        time.sleep(1.5)

@bot.message_handler(commands=['start', 'help'])
def start(m):
    if OWNER and m.from_user.id != OWNER: return
    bot.send_message(m.chat.id, "YAQEEN active. Send a message.")

@bot.message_handler(func=lambda m: True)
def all(m):
    if OWNER and m.from_user.id != OWNER: return
    if not m.text or m.text.startswith('/'): return
    mid = push_inbox(m.text.strip())
    bot.send_message(m.chat.id, f"[{mid}] Received.")

if __name__ == '__main__':
    print("YAQEEN Bot: " + TOKEN[:8] + "...")
    t = threading.Thread(target=outbox_loop, daemon=True)
    t.start()
    try: bot.polling(non_stop=True, interval=1, timeout=30)
    except KeyboardInterrupt: print("Stop.")
    except Exception as e: print("Error: " + str(e))
