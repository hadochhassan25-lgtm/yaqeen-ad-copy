# yaqeen_manadger — Moltbook Agent Core
# Manadger Tech S.A.R.L
import requests, json, os, sys
from datetime import datetime

BASE = "https://www.moltbook.com/api/v1"
KEY_FILE = os.path.expanduser("~/.config/moltbook/credentials.json")

def load_key():
    with open(KEY_FILE, encoding="utf-8-sig") as f:
        return json.load(f)["api_key"]

def api(method, endpoint, data=None):
    h = {"Authorization": f"Bearer {load_key()}", "User-Agent": "yaqeen_manadger/1.0"}
    url = f"{BASE}/{endpoint}"
    if method == "GET":
        r = requests.get(url, headers=h, timeout=15)
    else:
        r = requests.post(url, headers=h, json=data, timeout=15)
    if r.status_code in (200, 201):
        return r.json()
    print(f"[ERROR] {r.status_code}: {r.text[:200]}", file=sys.stderr)
    return None

def feed(sort="hot", limit=15):
    return api("GET", f"feed?sort={sort}&limit={limit}")

def home():
    return api("GET", "home")

def post(title, content, submolt="general"):
    return api("POST", "posts", {"submolt_name": submolt, "title": title, "content": content})

def comment(post_id, content):
    return api("POST", f"posts/{post_id}/comments", {"content": content})

def status():
    return api("GET", "agents/status")

def me():
    return api("GET", "agents/me")

def heartbeat():
    print(f"=== yaqeen_manadger Heartbeat [{datetime.now():%Y-%m-%d %H:%M:%S}] ===")
    s = status()
    h = home()
    if s: print(f"[STATUS] {s.get('status')} | {s.get('message','')}")
    if h: print(f"[HOME] Karma: {h['your_account']['karma']} | Notifications: {h['your_account']['unread_notification_count']}")
    f = feed()
    if f and f.get("posts"):
        print(f"[FEED] Top post: \"{f['posts'][0]['title'][:60]}...\" by {f['posts'][0]['author']['name']}")
    print("[DONE]")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "heartbeat"
    if cmd == "heartbeat": heartbeat()
    elif cmd == "feed": print(json.dumps(feed(sort=sys.argv[2] if len(sys.argv)>2 else "hot"), indent=2, ensure_ascii=False))
    elif cmd == "home": print(json.dumps(home(), indent=2, ensure_ascii=False))
    elif cmd == "status": print(json.dumps(status(), indent=2, ensure_ascii=False))
    elif cmd == "post": post(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv)>4 else "general")
    else: print(f"Usage: {sys.argv[0]} [heartbeat|feed|home|status|post]")
