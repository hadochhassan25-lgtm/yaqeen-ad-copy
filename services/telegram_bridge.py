#!/usr/bin/env python3
"""YAQEEN Telegram Direct Bridge — no files, no threads, pure requests."""
import os, sys, json, time, io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = Path(__file__).resolve().parent.parent
ENV = BASE / '.env'

def get_env(k):
    if ENV.exists():
        with open(ENV) as f:
            for line in f:
                line = line.strip()
                if line.startswith(k + '='): return line.split('=', 1)[1].strip().strip('"').strip("'")
    return None

TOKEN = get_env('TELEGRAM_BOT_TOKEN')
OWNER = get_env('TELEGRAM_OWNER_ID')
if not TOKEN:
    print("TELEGRAM_BOT_TOKEN not set in .env"); sys.exit(1)

API = f"https://api.telegram.org/bot{TOKEN}"
OFFSET = 0

def tg(method, data=None):
    import requests
    url = f"{API}/{method}"
    r = requests.post(url, json=data, timeout=15) if data else requests.get(url, timeout=15)
    return r.json()

def get_updates():
    global OFFSET
    r = tg("getUpdates", {"offset": OFFSET, "timeout": 10})
    if not r.get("ok"): return []
    msgs = []
    for u in r.get("result", []):
        OFFSET = u["update_id"] + 1
        if "message" in u:
            m = u["message"]
            uid = m["from"]["id"]
            if OWNER and str(uid) != OWNER: continue
            msgs.append({"id": m["message_id"], "chat_id": m["chat"]["id"], "text": m.get("text",""), "from_id": uid})
    return msgs

def send_msg(chat_id, text):
    return tg("sendMessage", {"chat_id": chat_id, "text": text})

print("YAQEEN Telegram Bridge")
print("Polling for messages... (Ctrl+C to stop)\n")

seen = set()

try:
    while True:
        msgs = get_updates()
        for m in msgs:
            if m["id"] in seen: continue
            seen.add(m["id"])
            print(f"\n[FROM TELEGRAM] {m['text']}")
            print("TYPE YOUR REPLY (or 'skip'): ", end="", flush=True)
            reply = sys.stdin.readline().strip()
            if reply.lower() == 'exit': print("Done."); sys.exit(0)
            if reply and reply.lower() != 'skip':
                send_msg(m["chat_id"], reply)
                print(f"[SENT] {reply}\n")
            else:
                print("[SKIPPED]\n")
        time.sleep(0.5)
except KeyboardInterrupt:
    print("\nStopped.")
