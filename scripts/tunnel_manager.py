"""
Simple tunnel: ssh raw with -T flag + capture URL
"""
import subprocess, time, re, os
from pathlib import Path

PORT = 5000
URL_FILE = Path(__file__).resolve().parent.parent / "memory" / "public_url.txt"
LOG_FILE = Path(__file__).resolve().parent.parent / "memory" / "tunnel.log"

def log(msg):
    t = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{t}] {msg}"
    print(line, flush=True)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def run_tunnel():
    cmd = [
        "ssh", "-p", "443", "-T",
        "-R", f"0:localhost:{PORT}",
        "-o", "StrictHostKeyChecking=no",
        "-o", "ServerAliveInterval=30",
        "-o", "ExitOnForwardFailure=yes",
        "a.pinggy.io"
    ]
    log("Starting raw SSH tunnel (-T mode)...")
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        creationflags=subprocess.CREATE_NO_WINDOW
    )
    url = None
    for raw_line in iter(proc.stdout.readline, b""):
        line = raw_line.decode("utf-8", errors="replace").strip()
        line_clean = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', line)
        if line_clean:
            print(f"  [{time.strftime('%H:%M:%S')}] {line_clean[:120]}", flush=True)
        m = re.search(r'(https?://[^\s]+run\.pinggy-free\.link)', line_clean)
        if m and not url:
            url = m.group(1)
            log(f"PUBLIC URL: {url}")
            URL_FILE.write_text(url, encoding="utf-8")
            log("Tunnel UP!")
    proc.wait()
    return url

def main():
    log("=== Tunnel Manager (Raw SSH) ===")
    while True:
        try:
            url = run_tunnel()
            log(f"Tunnel ended. URL was: {url}")
        except Exception as e:
            log(f"Error: {e}")
        time.sleep(5)

if __name__ == "__main__":
    main()
