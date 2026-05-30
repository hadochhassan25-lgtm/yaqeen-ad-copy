"""
Yaqeen Tunnel Manager v3 — Active health monitoring + auto-reconnect
Uses Pinggy TCP tunnel (confirmed working on this machine)
Checks tunnel health every 30s, reconnects immediately if down
"""
import pinggy, time, socket, json
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
    """Parse tcp://host:port into (host, port)"""
    url = url.replace("tcp://", "").replace("http://", "").replace("https://", "")
    host, port = url.rsplit(":", 1)
    return host, int(port)

def check_tunnel(host, port, timeout=10):
    """Check if tunnel is alive by connecting and sending HTTP health check"""
    try:
        s = socket.socket()
        s.settimeout(timeout)
        s.connect((host, port))
        time.sleep(1)
        s.send(b"GET /health HTTP/1.0\r\nHost: localhost\r\n\r\n")
        d = s.recv(4096)
        s.close()
        if b"200 OK" in d[:50] or b'"status":"ok"' in d:
            return True
        return False
    except Exception as e:
        return False

def start_tunnel(port=5000):
    """Start Pinggy TCP tunnel and return URL"""
    tunnel = pinggy.start_tunnel(port, type="tcp")
    urls = tunnel.urls
    url = urls[0] if urls else str(urls)
    URL_FILE.write_text(url, encoding="utf-8")
    return url, tunnel

def keep_alive(port=5000):
    log(f"=== Tunnel Manager v3 started (port {port}) ===")
    tunnel_obj = None
    current_url = None
    host = port_num = None

    while True:
        try:
            if not tunnel_obj:
                url, tunnel_obj = start_tunnel(port)
                current_url = url
                host, port_num = parse_url(url)
                log(f"Tunnel UP: {url}")

            # Check health every 30 seconds
            alive = check_tunnel(host, port_num)
            if alive:
                time.sleep(30)
                continue

            # Tunnel is down, reconnect
            log("Tunnel DOWN — reconnecting...")
            try:
                # Pinggy SDK doesn't have a close method, replace object
                tunnel_obj = None
            except:
                pass
            tunnel_obj = None

        except Exception as e:
            log(f"Error: {e}")
            tunnel_obj = None
            time.sleep(5)

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    keep_alive(port)
