#!/usr/bin/env python3
"""YAQEEN Relay - bridges Telegram messages to this CLI session."""
import json, time, sys, io
from datetime import datetime
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE_DIR = Path(__file__).resolve().parent.parent
RELAY_PATH = BASE_DIR / 'memory' / 'telegram_relay.json'
SEEN = set()

def load():
    if RELAY_PATH.exists():
        with open(RELAY_PATH, 'r', encoding='utf-8') as f: return json.load(f)
    return {"next_id": 1, "inbox": [], "outbox": []}

def save(data):
    RELAY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(RELAY_PATH, 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=2)

def push(msg_id, text, chat_id=None, thinking_msg_id=None):
    data = load()
    data["outbox"].append({"msg_id": msg_id, "text": text, "chat_id": chat_id,
                           "thinking_msg_id": thinking_msg_id, "timestamp": datetime.now().isoformat(), "sent": False})
    save(data)

def main():
    print("\n" + "=" * 50)
    print("  YAQEEN Relay -- Connected to Telegram")
    print("  Waiting for messages from Iliass...")
    print("  Type 'exit' to quit")
    print("=" * 50)

    while True:
        data = load()
        for m in data["inbox"]:
            if m["id"] in SEEN or m["status"] != "pending": continue
            SEEN.add(m["id"])
            ts = m["timestamp"][11:19] if len(m["timestamp"]) > 19 else m["timestamp"]
            print(f"\n[{ts}] Iliass: {m['text']}")
            print("> ", end="", flush=True)
            reply = sys.stdin.readline().strip()

            if reply.lower() == 'exit':
                print("Relay stopped.")
                return
            if not reply or reply.lower() == 'skip':
                print("[skipped]")
                continue

            push(m["id"], reply, m.get("chat_id"), m.get("thinking_msg_id"))
            print("[sent to Telegram]")

            data = load()
            for im in data["inbox"]:
                if im["id"] == m["id"]: im["status"] = "replied"
            save(data)

        time.sleep(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped.")
