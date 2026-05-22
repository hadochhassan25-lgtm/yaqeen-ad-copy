"""Show pending messages from Telegram."""
import json, sys
from pathlib import Path

RELAY_PATH = Path(__file__).parent / 'memory' / 'telegram_relay.json'

if not RELAY_PATH.exists():
    print("No messages.")
    sys.exit(0)

with open(RELAY_PATH, 'r') as f:
    data = json.load(f)

pending = [m for m in data["inbox"] if m["status"] == "pending"]
total = len(data["inbox"])

print(f"Messages: {total} total, {len(pending)} pending")
print("=" * 40)
for m in pending:
    print(f"[{m['id']}] {m['text']}")
