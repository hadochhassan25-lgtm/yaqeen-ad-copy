import subprocess, json, os, sys, time, threading, io
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
BRIDGE_SCRIPT = BASE / 'services' / 'payment-bridge' / 'bridge.js'

_process = None
_lock = threading.Lock()

def _start():
    global _process
    if _process and _process.poll() is None:
        return
    env = os.environ.copy()
    _process = subprocess.Popen(
        ['node', str(BRIDGE_SCRIPT)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        text=True,
        creationflags=subprocess.CREATE_NO_WINDOW
    )
    time.sleep(1.5)

def _send(cmd_dict, timeout=15):
    with _lock:
        _start()
        line = json.dumps(cmd_dict) + '\n'
        _process.stdin.write(line)
        _process.stdin.flush()
        result = _process.stdout.readline()
        if not result:
            raise ConnectionError('Bridge process died')
        try:
            return json.loads(result.strip())
        except json.JSONDecodeError:
            raise ValueError(f'Invalid bridge response: {result}')

def get_address():
    return _send({'cmd': 'address'})

def get_balance():
    return _send({'cmd': 'balance'})

def create_invoice(amount=0.5, token='USDC', chain='base'):
    return _send({'cmd': 'invoice', 'amount': amount, 'token': token, 'chain': chain})

def check_invoice(invoice_id):
    return _send({'cmd': 'check', 'invoiceId': invoice_id})

def check_all_invoices():
    return _send({'cmd': 'check-all'})

def derive_address(private_key):
    return _send({'cmd': 'derive', 'privateKey': private_key})

def stop():
    global _process
    with _lock:
        if _process and _process.poll() is None:
            _process.terminate()
            _process.wait(timeout=5)
        _process = None
