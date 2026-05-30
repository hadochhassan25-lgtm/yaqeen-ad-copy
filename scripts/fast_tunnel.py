"""
Fast tunnel: localhost.run URL capture
"""
import subprocess, re, time, urllib.request, sys
from pathlib import Path

PORT = 5000
URL_FILE = Path(__file__).resolve().parent.parent / "memory" / "public_url.txt"

cmd = ["ssh", "-o", "StrictHostKeyChecking=no", "-o", "ServerAliveInterval=30",
       "-o", "ExitOnForwardFailure=yes", "-T",
       "-R", f"80:localhost:{PORT}", "nokey@localhost.run"]

proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                        creationflags=subprocess.CREATE_NO_WINDOW)

url = None
for raw in iter(proc.stdout.readline, b""):
    line = raw.decode("utf-8", errors="replace").strip()
    if not line:
        continue
    # Find actual tunnel URL (not admin or docs)
    for m in re.finditer(r'(https?://[a-z0-9]+\.localhost\.run)', line):
        u = m.group(1)
        if "admin" not in u and "docs" not in u and url is None:
            url = u
            print(f"URL: {url}", flush=True)
            URL_FILE.write_text(url, encoding="utf-8")
            break
    if url and "forwarding" in line.lower():
        break

if url:
    print(f"Tunnel UP: {url}", flush=True)
    proc.wait()
