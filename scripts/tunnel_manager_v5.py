"""
YAQEEN Tunnel Manager v5 — SSH-based Pinggy HTTP tunnel
Uses SSH directly (not Python library) for reliable HTTP mode
"""
import subprocess, time, re, sys, threading
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

def parse_url(line):
    m = re.search(r'https?://[^\s\'"]+\.pinggy[^\s\'"]*', line)
    if m:
        return m.group(0).rstrip("/.")
    m2 = re.search(r'[a-z0-9-]+\.pinggy[a-z-]*\.link[^\s\'"]*', line)
    if m2:
        url = "https://" + m2.group(0).rstrip("/.")
        return url
    return None

def run_tunnel_ssh(port):
    log(f"Starting SSH tunnel on port {port}...")
    proc = subprocess.Popen(
        ["ssh", "-p", "443",
         "-o", "StrictHostKeyChecking=no",
         "-o", "ServerAliveInterval=30",
         "-o", "ExitOnForwardFailure=yes",
         "-R", f"0:localhost:{port}",
         "a.pinggy.io"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        bufsize=0, creationflags=subprocess.CREATE_NO_WINDOW
    )
    url = None
    buf = b""
    while url is None:
        byte = proc.stdout.read(1)
        if not byte:
            break
        if byte == b"\n":
            try:
                line = buf.decode("utf-8", errors="replace").strip()
                if line:
                    log(f"SSH: {line[:120]}")
                    url = parse_url(line)
            except:
                pass
            buf = b""
        else:
            buf += byte
    if url:
        URL_FILE.write_text(url, encoding="utf-8")
        log(f"PUBLIC URL: {url}")
        return url, proc
    return None, proc

def health_check(url, timeout=10):
    try:
        import urllib.request
        r = urllib.request.urlopen(f"{url}/health", timeout=timeout)
        return r.status == 200
    except:
        return False

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    log(f"=== Yaqeen Tunnel v5 (SSH HTTP mode) ===")

    while True:
        try:
            url, proc = run_tunnel_ssh(port)
            if not url:
                log("Failed to get URL, restarting in 10s...")
                proc.terminate()
                time.sleep(10)
                continue

            for minute in range(50):
                time.sleep(60)
                if proc.poll() is not None:
                    log(f"SSH process died at minute {minute+1}")
                    break
                if not health_check(url):
                    log(f"Health check failed at minute {minute+1}")
                    break
                log(f"Tunnel OK at minute {minute+1}")

            log("Cycle complete, restarting tunnel...")
            proc.terminate()
            time.sleep(3)

        except Exception as e:
            log(f"Error: {e}, restarting in 10s...")
            time.sleep(10)
