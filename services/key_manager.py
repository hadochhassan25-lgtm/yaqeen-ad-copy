"""
YAQEEN Key Manager - Multi-source LLM with auto-refresh
========================================================
Primary:    GitHub Models (gpt-4o-mini) - permanent token, reliable
Backup:     GitHub free keys repo - auto-refresh every 2h
Fallback:   Template (no API)
"""
import os, re, json, time, threading
from pathlib import Path
import requests

BASE = Path(__file__).resolve().parent.parent
KEY_FILE = BASE / "memory" / "working_key.json"
LOG_FILE = BASE / "memory" / "key_manager.log"

# ---------- GitHub Models (Primary) ----------
GH_TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""
GH_BASE = "https://models.inference.ai.azure.com"
GH_MODEL = "gpt-4o-mini"
if not GH_TOKEN:
    print("[KEY_MANAGER] WARNING: GITHUB_TOKEN not set. GitHub Models will fail.", flush=True)

# ---------- Free Keys (Backup) ----------
FREE_BASE = "https://aiapiv2.pekpik.com/v1"
FREE_MODEL = "deepseek-chat"
README_URL = "https://raw.githubusercontent.com/alistaitsacle/free-llm-api-keys/main/README.md"
KEY_PATTERN = r"sk-[a-zA-Z0-9]{48}"

_free_keys = []
_free_idx = 0
_last_refresh = 0

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

def fetch_free_keys():
    global _free_keys, _last_refresh
    try:
        resp = requests.get(README_URL, timeout=30)
        html = resp.text
        keys = list(set(re.findall(KEY_PATTERN, html)))
        _free_keys = keys
        _last_refresh = time.time()
        log(f"Fetched {len(keys)} free keys from GitHub")
        _test_free_keys()
        _save_state()
        return True
    except Exception as e:
        log(f"Failed to fetch free keys: {e}")
        return False

def _test_free_keys():
    global _free_idx
    for key in _free_keys[:6]:
        try:
            resp = requests.post(
                f"{FREE_BASE}/chat/completions",
                json={"model": FREE_MODEL, "messages": [{"role": "user", "content": "Say: OK"}], "max_tokens": 10},
                headers={"Authorization": f"Bearer {key}"},
                timeout=10
            )
            if resp.status_code == 200:
                _free_idx = _free_keys.index(key)
                log(f"Working free key found: {key[:20]}...")
                return
        except:
            continue
    log("No working free keys found (all expired)")

def _save_state():
    state = {
        "free_keys": _free_keys,
        "free_idx": _free_idx,
        "last_refresh": _last_refresh,
        "free_base": FREE_BASE,
        "free_model": FREE_MODEL,
        "gh_base": GH_BASE,
        "gh_model": GH_MODEL,
    }
    try:
        KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
        KEY_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
    except Exception as e:
        log(f"Failed to save state: {e}")

def ask_llm(system, user, max_tokens=500, temp=0.7):
    """Try GitHub Models first, then free keys, then None"""
    result = _try_github(system, user, max_tokens, temp)
    if result:
        log("Used GitHub Models (primary)")
        return result
    log("GitHub Models failed, trying free backup keys")
    result = _try_free(system, user, max_tokens, temp)
    if result:
        log("Used free backup keys")
        return result
    log("All LLM sources failed")
    return None

def _try_github(system, user, max_tokens, temp):
    try:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": user})
        resp = requests.post(
            f"{GH_BASE}/chat/completions",
            json={"model": GH_MODEL, "messages": messages, "max_tokens": max_tokens, "temperature": temp},
            headers={"Authorization": f"Bearer {GH_TOKEN}", "Content-Type": "application/json"},
            timeout=60
        )
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"].strip()
        log(f"GitHub HTTP {resp.status_code}: {resp.text[:120]}")
        if resp.status_code == 429:
            time.sleep(5)
            return _try_github(system, user, max_tokens, temp)
        return None
    except Exception as e:
        log(f"GitHub error: {e}")
        return None

def _try_free(system, user, max_tokens, temp):
    global _free_idx
    if not _free_keys or (time.time() - _last_refresh > 7200):
        fetch_free_keys()
    for attempt in range(len(_free_keys)):
        idx = (_free_idx + attempt) % len(_free_keys)
        key = _free_keys[idx]
        if not key:
            continue
        try:
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": user})
            resp = requests.post(
                f"{FREE_BASE}/chat/completions",
                json={"model": FREE_MODEL, "messages": messages, "max_tokens": max_tokens, "temperature": temp},
                headers={"Authorization": f"Bearer {key}"},
                timeout=30
            )
            if resp.status_code == 200:
                _free_idx = idx
                _save_state()
                return resp.json()["choices"][0]["message"]["content"].strip()
            if resp.status_code == 403:
                continue
            log(f"Free key {idx} HTTP {resp.status_code}: {resp.text[:80]}")
        except Exception as e:
            continue
    log("All free keys exhausted - need refresh")
    if time.time() - _last_refresh > 300:
        fetch_free_keys()
    return None

# ---------- Background Refresh ----------
def _bg_refresh():
    while True:
        time.sleep(7200)
        log("Auto-refreshing free keys (2h interval)")
        fetch_free_keys()

_refresh_thread = threading.Thread(target=_bg_refresh, daemon=True)
_refresh_thread.start()

# Initial fetch
fetch_free_keys()
log("Key manager initialized")
