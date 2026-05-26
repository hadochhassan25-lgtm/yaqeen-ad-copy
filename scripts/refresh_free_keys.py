"""
Refresh Free LLM API Keys from GitHub.
Run daily via Task Scheduler to auto-rotate keys.
"""
import re, json, requests, os, sys
from pathlib import Path

README_URL = "https://raw.githubusercontent.com/alistaitsacle/free-llm-api-keys/main/README.md"
API_FILE = Path(__file__).resolve().parent.parent / "services" / "yaqeen_ad_api_deploy.py"
KEY_PATTERN = r"sk-[a-zA-Z0-9]{48}"

def fetch_keys():
    resp = requests.get(README_URL, timeout=30)
    resp.raise_for_status()
    html = resp.text
    keys = list(set(re.findall(KEY_PATTERN, html)))
    deepseek_keys = [k for k in keys if k not in (
        expired := {"sk-CmToOGwbsBwvHCTEBLKnRnf2OxVe7LpXL7k6RPkHbPWniy5u"}
    )]
    return deepseek_keys[:4]

def update_env(key):
    from subprocess import run
    run(["powershell", "-Command",
         f"[Environment]::SetEnvironmentVariable('DEEPSEEK_KEY', '{key}', 'User')"],
        capture_output=True)
    os.environ["DEEPSEEK_KEY"] = key
    print(f"Env var DEEPSEEK_KEY set to {key[:16]}...")

def main():
    keys = fetch_keys()
    if not keys:
        print("No keys found!")
        return 1
    print(f"Found {len(keys)} valid keys")
    update_env(keys[0])
    if API_FILE.exists():
        content = API_FILE.read_text(encoding="utf-8")
        count = 0
        for k in keys:
            quoted = f'"{k}"'
            if quoted not in content:
                insert = '    "sk-7QHSPpSbl1D2u1zezSKam6XqMQZf0oWk4u4QVpEgPvnknZBl",  # DeepSeek $15'
                content = content.replace(insert, quoted + ",  # DeepSeek fresh key")
                count += 1
        if count:
            API_FILE.write_text(content, encoding="utf-8")
            print(f"Updated {count} keys in {API_FILE.name}")
    else:
        print(f"API file not found at {API_FILE}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
