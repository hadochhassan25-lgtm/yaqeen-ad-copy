"""Seed the admin account: sign up, sign in, promote to admin."""
import os, sys, json, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()
from services.supabase_client import sign_up, sign_in, set_admin

EMAIL = os.getenv('ADMIN_EMAIL', 'admin@yaqeen.ma')
PASSWORD = os.getenv('ADMIN_PASSWORD', 'Manadger2026!')

print(f"[seed] Signing up {EMAIL} ...")
r = sign_up(EMAIL, PASSWORD)
if r['success']:
    print("[seed] Signup OK")
else:
    print(f"[seed] Signup (may already exist): {r.get('error','')}")

print("[seed] Signing in...")
r = sign_in(EMAIL, PASSWORD)
if not r['success']:
    print(f"[seed] Signin failed: {r.get('error','')}")
    sys.exit(1)
print("[seed] Signin OK, promoting to admin...")

ok = set_admin(r['access_token'])
if ok:
    print("[seed] Admin privileges granted!")
else:
    print("[seed] Failed to set admin. Try: log in via /login, then POST /api/admin/setup")
    sys.exit(1)

print(f"\nDone. Login at /login with:\n  Email: {EMAIL}\n  Password: {PASSWORD}")
