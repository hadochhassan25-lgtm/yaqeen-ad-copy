#!/usr/bin/env python3
"""Collect more AGI proposals from additional models"""
import sys, os, io, json, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'services'))

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

RAW_DIR = Path(__file__).resolve().parent.parent / 'research' / 'ai_generated_agi_architectures' / 'raw_outputs'
RAW_DIR.mkdir(parents=True, exist_ok=True)

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

def try_key_manager():
    """Test if key_manager's ask_llm works"""
    try:
        from key_manager import ask_llm, fetch_free_keys, _try_free
        print("[*] Refreshing free keys...", flush=True)
        fetch_free_keys()
        print("[*] Trying DeepSeek via key_manager...", flush=True)
        result = _try_free(SYSTEM, PROMPT, 3000, 0.8)
        if result:
            save_raw("deepseek-chat", result)
            return result
        print("[!] DeepSeek via key_manager failed")
    except Exception as e:
        print(f"[!] key_manager import error: {e}")
    return None

def try_ghg():
    """Try another GitHub Models call with different parameters"""
    import requests
    token = os.environ.get('GITHUB_TOKEN', '')
    if not token:
        # search .env
        env_path = Path(__file__).resolve().parent.parent / '.env'
        if env_path.exists():
            for line in env_path.read_text().split('\n'):
                if 'GITHUB_TOKEN' in line or 'GH_TOKEN' in line:
                    token = line.split('=')[-1].strip()
    
    if not token:
        print("[!] No token for GitHub Models")
        return None
    
    # Try different model gpt-4o
    print("[*] Querying GPT-4o (GitHub Models)...", flush=True)
    try:
        resp = requests.post(
            "https://models.inference.ai.azure.com/chat/completions",
            json={
                "model": "gpt-4o",
                "messages": [
                    {"role": "system", "content": SYSTEM},
                    {"role": "user", "content": PROMPT}
                ],
                "max_tokens": 3000,
                "temperature": 0.9
            },
            headers={"Authorization": f"Bearer {token}"},
            timeout=120
        )
        if resp.status_code == 200:
            content = resp.json()["choices"][0]["message"]["content"].strip()
            save_raw("gpt-4o", content)
            return content
        print(f"[!] GPT-4o HTTP {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        print(f"[!] GPT-4o error: {e}")
    return None

def try_phi3_azure():
    """Try Phi-3 via Azure serverless (free tier)"""
    import requests
    token = os.environ.get('GITHUB_TOKEN', '')
    print("[*] Querying Phi-3-mini (GitHub Models)...", flush=True)
    try:
        resp = requests.post(
            "https://models.inference.ai.azure.com/chat/completions",
            json={
                "model": "Phi-3.5-mini-instruct",
                "messages": [
                    {"role": "system", "content": SYSTEM},
                    {"role": "user", "content": PROMPT[:1500]}
                ],
                "max_tokens": 2000,
                "temperature": 0.8
            },
            headers={"Authorization": f"Bearer {token}"},
            timeout=120
        )
        if resp.status_code == 200:
            content = resp.json()["choices"][0]["message"]["content"].strip()
            save_raw("phi-3.5-mini", content)
            return content
        print(f"[!] Phi-3 HTTP {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        print(f"[!] Phi-3 error: {e}")
    return None

def try_cohere():
    """Try Cohere free API trial"""
    import requests
    print("[*] Querying Cohere (free)...", flush=True)
    try:
        resp = requests.post(
            "https://api.cohere.ai/v1/chat",
            json={
                "message": PROMPT,
                "model": "command-r",
                "preamble": SYSTEM
            },
            timeout=30
        )
        if resp.status_code == 200:
            content = resp.json()["text"]
            save_raw("cohere-command-r", content)
            return content
        print(f"[!] Cohere HTTP {resp.status_code}")
    except Exception as e:
        print(f"[!] Cohere error: {e}")
    return None

def main():
    collectors = [
        ("DeepSeek via key_manager", try_key_manager),
        ("GPT-4o (GitHub Models)", try_ghg),
        ("Phi-3.5 Mini (GitHub Models)", try_phi3_azure),
        ("Cohere Command-R", try_cohere),
    ]
    results = []
    for name, func in collectors:
        print(f"\n{'='*60}", flush=True)
        print(f"[*] {name}", flush=True)
        result = func()
        if result:
            results.append((name, result))
        time.sleep(2)
    print(f"\n{'='*60}")
    print(f"New proposals: {len(results)}/{len(collectors)}")
    print(f"Total in raw_outputs: {len(list(RAW_DIR.glob('*.txt')))}")
    for name, _ in results:
        print(f"  + {name}")

if __name__ == '__main__':
    main()
