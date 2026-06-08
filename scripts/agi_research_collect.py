#!/usr/bin/env python3
"""
YAQEEN AGI Research Collector
Collects AGI architecture proposals from multiple AI systems for the $3k bounty.
"""
import sys, os, io, json, time
from pathlib import Path
import requests

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = Path(__file__).resolve().parent.parent
RAW_DIR = BASE / 'research' / 'ai_generated_agi_architectures' / 'raw_outputs'
RAW_DIR.mkdir(parents=True, exist_ok=True)

GH_TOKEN = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN', '')
FREE_BASE = "https://aiapiv2.pekpik.com/v1"

PROMPT = (
    "You are an AGI architecture researcher. Propose a detailed AGI architecture "
    "covering these 11 dimensions:\n"
    "1. Memory architecture\n2. Reasoning/planning loop\n"
    "3. Learning or self-improvement mechanism\n4. Tool use and action execution\n"
    "5. World model or representation layer\n6. Safety/governance layer\n"
    "7. Evaluation and benchmark strategy\n8. Persistence/runtime architecture\n"
    "9. Multi-agent or orchestration design\n10. Engineering feasibility\n"
    "11. Originality or non-obvious insight\n\n"
    "Provide a structured, technically specific proposal. Assume unlimited compute "
    "but realistic engineering constraints. Format as a structured research document."
)

SYSTEM = "You are a senior AGI architect. Provide technically detailed, original proposals."

def save_raw(model_name, content):
    safe_name = model_name.lower().replace(' ', '_').replace('/', '_').replace('-', '_')
    path = RAW_DIR / f'{safe_name}.txt'
    path.write_text(content, encoding='utf-8')
    print(f"[OK] {model_name}: {len(content)} chars -> {path.name}")
    return path

def query_github_gpt():
    """Query gpt-4o-mini via GitHub Models"""
    print("[*] Querying GitHub Models (gpt-4o-mini)...", flush=True)
    if not GH_TOKEN:
        print("[!] GITHUB_TOKEN not set, skipping")
        return None
    try:
        resp = requests.post(
            "https://models.inference.ai.azure.com/chat/completions",
            json={
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": SYSTEM},
                    {"role": "user", "content": PROMPT}
                ],
                "max_tokens": 3000,
                "temperature": 0.8
            },
            headers={"Authorization": f"Bearer {GH_TOKEN}"},
            timeout=120
        )
        if resp.status_code == 200:
            content = resp.json()["choices"][0]["message"]["content"].strip()
            save_raw("gpt-4o-mini", content)
            return content
        print(f"[!] GitHub HTTP {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        print(f"[!] GitHub error: {e}")
    return None

def query_deepseek():
    """Query DeepSeek via free keys"""
    print("[*] Querying DeepSeek (free keys)...", flush=True)
    key_file = BASE / 'memory' / 'working_key.json'
    if not key_file.exists():
        print("[!] No working_key.json found")
        return None
    try:
        state = json.loads(key_file.read_text(encoding='utf-8'))
        keys = state.get('free_keys', [])
    except:
        print("[!] Failed to parse working_key.json")
        return None
    
    for key in keys:
        if not key:
            continue
        try:
            resp = requests.post(
                f"{FREE_BASE}/chat/completions",
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": SYSTEM},
                        {"role": "user", "content": PROMPT}
                    ],
                    "max_tokens": 3000,
                    "temperature": 0.8
                },
                headers={"Authorization": f"Bearer {key}"},
                timeout=60
            )
            if resp.status_code == 200:
                content = resp.json()["choices"][0]["message"]["content"].strip()
                save_raw("deepseek-chat", content)
                return content
        except:
            continue
    print("[!] All DeepSeek keys exhausted")
    return None

def query_openrouter(model_name, api_model):
    """Query via OpenRouter with free model"""
    print(f"[*] Querying {model_name} via OpenRouter...", flush=True)
    try:
        resp = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json={
                "model": api_model,
                "messages": [
                    {"role": "system", "content": SYSTEM},
                    {"role": "user", "content": PROMPT}
                ],
                "max_tokens": 2000,
                "temperature": 0.8
            },
            headers={"HTTP-Referer": "https://github.com/yaqeen-research"},
            timeout=60
        )
        if resp.status_code == 200:
            content = resp.json()["choices"][0]["message"]["content"].strip()
            save_raw(model_name, content)
            return content
        print(f"[!] OpenRouter {model_name} HTTP {resp.status_code}")
    except Exception as e:
        print(f"[!] OpenRouter {model_name} error: {e}")
    return None

def query_nova():
    """Try Llama 3.1 via Nova AI (free tier)"""
    print("[*] Querying Nova AI (Llama free)...", flush=True)
    try:
        resp = requests.post(
            "https://api.nova-oss.com/v1/chat/completions",
            json={
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": SYSTEM},
                    {"role": "user", "content": PROMPT}
                ],
                "max_tokens": 2000,
                "temperature": 0.8
            },
            timeout=60
        )
        if resp.status_code == 200:
            content = resp.json()["choices"][0]["message"]["content"].strip()
            save_raw("nova-gpt4o-mini", content)
            return content
        print(f"[!] Nova HTTP {resp.status_code}")
    except Exception as e:
        print(f"[!] Nova error: {e}")
    return None

def query_together():
    """Try together.xyz free models"""
    print("[*] Querying Together AI...", flush=True)
    try:
        resp = requests.post(
            "https://api.together.xyz/v1/chat/completions",
            json={
                "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
                "messages": [
                    {"role": "system", "content": SYSTEM},
                    {"role": "user", "content": PROMPT}
                ],
                "max_tokens": 2000,
                "temperature": 0.8
            },
            timeout=60
        )
        if resp.status_code == 200:
            content = resp.json()["choices"][0]["message"]["content"].strip()
            save_raw("mixtral-8x7b", content)
            return content
        print(f"[!] Together HTTP {resp.status_code}")
    except Exception as e:
        print(f"[!] Together error: {e}")
    return None

def main():
    models = [
        ("GitHub Models (gpt-4o-mini)", query_github_gpt),
        ("DeepSeek Chat", query_deepseek),
        ("OpenChat 7B (OpenRouter)", lambda: query_openrouter("openchat-7b", "openchat/openchat-7b")),
        ("Phi-3 Mini (OpenRouter)", lambda: query_openrouter("phi-3-mini", "microsoft/phi-3-mini-4k-instruct")),
        ("Nova GPT-4o-mini", query_nova),
        ("Mixtral 8x7B (Together)", query_together),
    ]
    results = []
    for name, func in models:
        print(f"\n{'='*60}", flush=True)
        result = func()
        if result:
            results.append((name, result))
        time.sleep(2)
    print(f"\n{'='*60}")
    print(f"Collected {len(results)}/{len(models)} proposals")
    for name, _ in results:
        print(f"  - {name}")
    print(f"\nRaw outputs saved to: {RAW_DIR}")

if __name__ == '__main__':
    main()
