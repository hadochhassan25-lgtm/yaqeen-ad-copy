"""
Yaqeen Tunnel Manager v2 — Uses Pinggy TCP tunnel (confirmed working)
Auto-reconnect, writes public URL to memory/public_url.txt
"""
import pinggy, time, sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
URL_FILE = BASE / "memory" / "public_url.txt"
LOG_FILE = BASE / "memory" / "tunnel_manager.log"

def log(msg):
    t = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{t}] {msg}"
    print(line, flush=True)
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except:
        pass

def keep_tunnel_alive(port=5000):
    while True:
        try:
            log(f"Starting Pinggy TCP tunnel on port {port}...")
            tunnel = pinggy.start_tunnel(port, type="tcp")
            urls = tunnel.urls
            url = urls[0] if urls else str(urls)
            log(f"PUBLIC URL: {url}")
            URL_FILE.write_text(url, encoding="utf-8")
            log("Tunnel UP. Keeping alive...")
            # Free tier: 60 min tunnel
            for _ in range(3540):  # 59 min
                time.sleep(1)
            log("Tunnel time limit approaching, restarting...")
        except Exception as e:
            log(f"Tunnel error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    log("=== Yaqeen Tunnel Manager v2 (TCP mode) ===")
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    keep_tunnel_alive(port)
