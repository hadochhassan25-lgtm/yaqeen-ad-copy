"""Watch for new Telegram messages in real-time."""
import json, time, sys, io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

RELAY_PATH = Path(__file__).parent / 'memory' / 'telegram_relay.json'
seen = set()

print("Watching for Telegram messages... (Ctrl+C to stop)\n")

while True:
    if RELAY_PATH.exists():
        try:
            with open(RELAY_PATH, 'r') as f:
                data = json.load(f)
            for m in data["inbox"]:
                if m["id"] not in seen and m["status"] == "pending":
                    seen.add(m["id"])
                    print(f"\n[IN #{m['id']}] {m['text']}")
                    print("> python reply.py <id> \"your response\"")
        except: pass
    time.sleep(1.5)
