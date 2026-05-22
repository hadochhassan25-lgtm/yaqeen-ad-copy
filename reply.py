"""Reply to the latest pending message from Telegram.
Usage: python reply.py <message_id|last> "your response"
"""
import json, sys
from datetime import datetime
from pathlib import Path

RELAY_PATH = Path(__file__).parent / 'memory' / 'telegram_relay.json'

if not RELAY_PATH.exists():
    print("No relay file.")
    sys.exit(1)

if len(sys.argv) < 3:
    print("Usage: python reply.py <id|last> \"your response\"")
    sys.exit(1)

target = sys.argv[1]
response = sys.argv[2]

with open(RELAY_PATH, 'r') as f:
    data = json.load(f)

if target == "last":
    pending = [m for m in data["inbox"] if m["status"] == "pending"]
    if not pending:
        print("No pending messages.")
        sys.exit(1)
    msg = pending[-1]
    mid = msg["id"]
else:
    mid = int(target)
    matches = [m for m in data["inbox"] if m["id"] == mid]
    if not matches:
        print(f"Message {mid} not found.")
        sys.exit(1)
    msg = matches[0]

msg["status"] = "replied"

data["outbox"].append({
    "msg_id": mid,
    "text": response,
    "cid": msg.get("chat_id"),
    "ts": datetime.now().isoformat(),
    "sent": False
})

with open(RELAY_PATH, 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Reply to [{mid}] \"{msg['text']}\" queued: \"{response}\"")
