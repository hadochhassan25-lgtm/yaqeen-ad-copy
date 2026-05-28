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
    host, port = url.rsplit(":", 1)
    return host, int(port)

def is_alive(host, port, timeout=12):
    try:
        s = socket.socket()
        s.settimeout(timeout)
        s.connect((host, port))
        time.sleep(1)
        s.send(b"GET /health HTTP/1.0\r\nHost: localhost\r\n\r\n")
        for _ in range(10):
            try:
                d = s.recv(4096)
                if b"200 OK" in d or b"status" in d:
                    s.close()
                    return True
            except:
                break
        s.close()
        return False
    except:
        return False

def run_tunnel(port):
    log(f"Connecting tunnel on port {port}...")
    tunnel = pinggy.start_tunnel(port, type="tcp")
    urls = tunnel.urls
    url = urls[0] if urls else str(urls)
    URL_FILE.write_text(url, encoding="utf-8")
    host, pnum = parse_url(url)
    log(f"PUBLIC URL: {url}")
    return url, host, pnum, tunnel

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    log(f"=== Yaqeen Tunnel v4 (health-check loop) ===")
    
    while True:
        try:
            url, host, pnum, tunnel = run_tunnel(port)
            
            # Monitor: check every 60s, restart at 50 min or if dead
            for minute in range(50):
                for _ in range(60):  # 60 seconds * 50 minutes = 3000 iterations
                    time.sleep(1)
                
                # Every 60s, check if alive
                if not is_alive(host, pnum):
                    log(f"Tunnel dead at minute {minute+1}, reconnecting...")
                    tunnel = None
                    break
                else:
                    log(f"Tunnel OK at minute {minute+1}")
            
            if tunnel:
                log(f"50-min cycle complete, restarting tunnel...")
                tunnel = None
                
        except Exception as e:
            log(f"Fatal error: {e}, restarting in 10s...")
            time.sleep(10)
