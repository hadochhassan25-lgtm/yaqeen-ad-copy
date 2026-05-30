"""
Yaqeen Tunnel Manager v4 — Simple restart loop for Pinggy TCP tunnel
Restarts every 50 minutes (before free tier 60-min limit)
Health check every 60 seconds — reconnects immediately if dead
"""
import pinggy, time, socket
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

def parse_url(url):
    url = url.replace("tcp://", "").replace("http://", "").replace("https://", "")
    # HTTP mode returns URL like https://prefix.pinggy.link, no port
    if "/" in url:
        url = url.split("/")[0]
    if ":" in url:
        host, port = url.rsplit(":", 1)
        return host, int(port)
    return url, 443

def is_alive(url, timeout=12):
    """HTTP health check via requests"""
    try:
        import requests
        r = requests.get(f"{url}/health", timeout=timeout)
        return r.status_code == 200
    except:
        return False

def run_tunnel(port):
    log(f"Connecting tunnel on port {port}...")
    tunnel = pinggy.start_tunnel(port, type="http")
    urls = tunnel.urls
    url = urls[0] if urls else str(urls)
    URL_FILE.write_text(url, encoding="utf-8")
    log(f"PUBLIC URL: {url}")
    return url, tunnel

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    log(f"=== Yaqeen Tunnel v4 (HTTP mode) ===")
    
    while True:
        try:
            url, tunnel = run_tunnel(port)
            
            for minute in range(50):
                for _ in range(60):
                    time.sleep(1)
                
                if not is_alive(url):
                    log(f"Tunnel dead at minute {minute+1}, reconnecting...")
                    tunnel = None
                    break
                else:
                    log(f"Tunnel OK at minute {minute+1}")
            
            if tunnel:
                log(f"50-min cycle complete, restarting...")
                tunnel = None
                
        except Exception as e:
            log(f"Fatal error: {e}, restarting in 10s...")
            time.sleep(10)
