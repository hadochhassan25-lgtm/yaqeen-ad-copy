"""
Start public tunnel for YAQEEN API using localtunnel.
Keeps tunnel alive and logs the URL.
"""
import subprocess, time, json, os, threading, signal, sys, urllib.request

TUNNEL_LOG = os.path.join(os.path.dirname(__file__), "..", "tunnel_url.txt")
PORT = 5000

def get_public_url():
    try:
        data = json.loads(urllib.request.urlopen("http://127.0.0.1:4040/api/tunnels", timeout=5).read())
        if data.get("tunnels"):
            return data["tunnels"][0]["public_url"]
    except: pass
    return None

def start_tunnel():
    proc = subprocess.Popen(
        ["npx", "-y", "localtunnel", "--port", str(PORT)],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, creationflags=subprocess.CREATE_NO_WINDOW
    )
    for line in iter(proc.stdout.readline, ""):
        if "your url is:" in line:
            url = line.split("your url is:")[-1].strip()
            with open(TUNNEL_LOG, "w") as f:
                f.write(url)
            print(f"[TUNNEL] URL: {url}")
            break
    return proc

def main():
    # Kill old localtunnel
    subprocess.run(["taskkill", "/f", "/im", "node.exe"], capture_output=True)
    time.sleep(2)

    proc = start_tunnel()

    # Keep alive
    try:
        while True:
            time.sleep(30)
            if proc.poll() is not None:
                print("[TUNNEL] Process died, restarting...")
                proc = start_tunnel()
    except KeyboardInterrupt:
        proc.terminate()

if __name__ == "__main__":
    main()
