"""Start YAQEEN services as persistent background processes"""
import subprocess, sys, os, time, threading, json

BASE = r'C:\Users\manadger\Desktop\moltbook-app'
PID_DIR = os.path.join(BASE, 'memory')
os.chdir(BASE)

def start_service(name, script, log_file):
    log_path = os.path.join(PID_DIR, log_file)
    with open(log_path, 'w') as log:
        proc = subprocess.Popen(
            [sys.executable, '-u', script],
            stdout=log, stderr=subprocess.STDOUT, text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
    pid_file = os.path.join(PID_DIR, f'{name}.pid')
    with open(pid_file, 'w') as f:
        f.write(str(proc.pid))
    print(f'[{name}] started PID={proc.pid}')
    return proc

# Kill all old services first
print('Killing old services...')
subprocess.run(['taskkill', '/F', '/IM', 'ssh.exe'], capture_output=True)
# Kill specific PIDs
for pid_file in ['api.pid', 'bot.pid', 'worker.pid']:
    try:
        with open(os.path.join(PID_DIR, pid_file)) as f:
            pid = f.read().strip()
            if pid:
                subprocess.run(['taskkill', '/F', '/PID', pid], capture_output=True)
    except:
        pass
time.sleep(2)

# Start services
services = [
    ('api', 'services/yaqeen_ad_api_deploy.py', 'api_service.log'),
    ('bot', 'scripts/ghostwriter_bot.py', 'bot_service.log'),
]

procs = []
for name, script, log_file in services:
    try:
        p = start_service(name, script, log_file)
        procs.append((name, p))
    except Exception as e:
        print(f'[{name}] FAILED: {e}')

time.sleep(3)

# Verify
print(f'\n{"="*40}')
print('Services status:')
for name, p in procs:
    status = 'RUNNING' if p.poll() is None else f'DIED (rc={p.returncode})'
    print(f'  [{name}] {status}')
    if p.poll() is not None:
        log_path = os.path.join(PID_DIR, f'{name}_service.log'.replace('services/', ''))
        try:
            with open(log_path) as f:
                last = f.readlines()[-5:]
                for line in last:
                    print(f'    {line.strip()}')
        except:
            pass

print(f'\n{"="*40}')
print('Services are running in background.')
print('They will persist until reboot or manual kill.')
print(f'{"="*40}')
