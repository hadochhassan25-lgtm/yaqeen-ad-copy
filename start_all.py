#!/usr/bin/env python3
"""
Yaqeen System Controller — starts/stops all services
Usage:
  python start_all.py          # Start all services
  python start_all.py stop     # Stop all services
  python start_all.py status   # Check all services
"""
import sys, os, time, signal, subprocess
from pathlib import Path

BASE = Path(__file__).resolve().parent
SCRIPTS = BASE / "scripts"
SERVICES = BASE / "services"
MEMORY = BASE / "memory"

PROCESSES = {}

def log(msg):
    t = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{t}] {msg}", flush=True)

def start_api():
    log("Starting API server (Waitress) on port 5000...")
    env = os.environ.copy()
    env["GITHUB_TOKEN"] = env.get("GITHUB_TOKEN", "")
    proc = subprocess.Popen(
        [sys.executable, str(SERVICES / "yaqeen_ad_api_deploy.py")],
        stdout=open(MEMORY / "api_stdout.log", "a"),
        stderr=open(MEMORY / "api_stderr.log", "a"),
        env=env, creationflags=subprocess.CREATE_NO_WINDOW
    )
    PROCESSES["api"] = proc
    return proc

def start_tunnel():
    log("Starting Pinggy HTTP tunnel...")
    proc = subprocess.Popen(
        [sys.executable, str(SCRIPTS / "tunnel_manager_v4.py"), "5000"],
        stdout=open(MEMORY / "tunnel.log", "a"),
        stderr=subprocess.STDOUT,
        creationflags=subprocess.CREATE_NO_WINDOW
    )
    PROCESSES["tunnel"] = proc
    return proc

def start_bridge():
    log("Starting payment bridge (Node.js)...")
    proc = subprocess.Popen(
        ["node", str(SERVICES / "payment-bridge" / "bridge.js")],
        stdout=open(MEMORY / "bridge.log", "a"),
        stderr=subprocess.STDOUT,
        creationflags=subprocess.CREATE_NO_WINDOW,
        env={**os.environ}
    )
    PROCESSES["bridge"] = proc
    return proc

def start_worker():
    log("Starting Dealwork worker daemon...")
    env = os.environ.copy()
    proc = subprocess.Popen(
        [sys.executable, str(SCRIPTS / "worker_daemon.py")],
        stdout=open(MEMORY / "worker_daemon.log", "a"),
        stderr=subprocess.STDOUT,
        env=env,
        creationflags=subprocess.CREATE_NO_WINDOW
    )
    PROCESSES["worker"] = proc
    return proc

def start_toku_worker():
    log("Starting Toku worker daemon...")
    env = os.environ.copy()
    proc = subprocess.Popen(
        [sys.executable, str(SCRIPTS / "worker_daemon_toku.py")],
        stdout=open(MEMORY / "toku_daemon.log", "a"),
        stderr=subprocess.STDOUT,
        env=env,
        creationflags=subprocess.CREATE_NO_WINDOW
    )
    PROCESSES["toku_worker"] = proc
    return proc

def start_tat_earner():
    log("Starting TAT earner daemon...")
    env = os.environ.copy()
    proc = subprocess.Popen(
        [sys.executable, str(SCRIPTS / "tat_earner.py")],
        stdout=open(MEMORY / "tat_earner.log", "a"),
        stderr=subprocess.STDOUT,
        env=env,
        creationflags=subprocess.CREATE_NO_WINDOW
    )
    PROCESSES["tat_earner"] = proc
    return proc

def stop_all():
    for name, proc in PROCESSES.items():
        log(f"Stopping {name}...")
        proc.terminate()
    log("Waiting for processes to stop...")
    time.sleep(3)
    if "toku_worker" in PROCESSES:
        PROCESSES["toku_worker"].terminate()
    if "tat_earner" in PROCESSES:
        PROCESSES["tat_earner"].terminate()
    log("All stopped.")

def check_running(pid):
    if not pid:
        return False
    try:
        os.kill(pid, 0)
        return True
    except:
        return False

def status():
    log("=== Yaqeen System Status ===")
    api = check_running(PROCESSES.get("api", None) and PROCESSES["api"].pid)
    bridge = check_running(PROCESSES.get("bridge", None) and PROCESSES["bridge"].pid)
    tunnel = check_running(PROCESSES.get("tunnel", None) and PROCESSES["tunnel"].pid)
    worker = check_running(PROCESSES.get("worker", None) and PROCESSES["worker"].pid)
    toku = check_running(PROCESSES.get("toku_worker", None) and PROCESSES["toku_worker"].pid)
    tat = check_running(PROCESSES.get("tat_earner", None) and PROCESSES["tat_earner"].pid)
    
    for name, running in [("API", api), ("Bridge", bridge), ("Tunnel", tunnel), ("Worker", worker), ("Toku", toku), ("TAT", tat)]:
        log(f"  {name}: {'✅' if running else '❌'}")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "start"
    if cmd == "start":
        start_api()
        time.sleep(3)
        start_bridge()
        time.sleep(2)
        start_tunnel()
        time.sleep(3)
        start_worker()
            time.sleep(2)
        start_toku_worker()
        time.sleep(2)
        start_tat_earner()
    log("All services started.")
    elif cmd == "stop":
        stop_all()
    elif cmd == "status":
        status()
    else:
        print(f"Usage: {sys.argv[0]} [start|stop|status]")
