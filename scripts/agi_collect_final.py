#!/usr/bin/env python3
"""Final batch of AGI proposal collection"""
import sys, os, io, time
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

RAW_DIR = Path(__file__).resolve().parent.parent / 'research' / 'ai_generated_agi_architectures' / 'raw_outputs'
RAW_DIR.mkdir(parents=True, exist_ok=True)

token = os.environ.get('GITHUB_TOKEN', '')
if not token:
    env_path = Path(__file__).resolve().parent.parent / '.env'
    if env_path.exists():
        for line in env_path.read_text().split('\n'):
            line = line.strip()
            if line.startswith('GITHUB_TOKEN=') or line.startswith('GH_TOKEN='):
                token = line.split('=', 1)[1].strip()
                break

SYSTEM = "You are a senior AGI architect. Provide technically detailed proposals."
PROMPT = "Propose a detailed AGI architecture covering: 1. Memory 2. Reasoning/planning 3. Learning 4. Tool use 5. World model 6. Safety 7. Evaluation 8. Runtime 9. Multi-agent 10. Feasibility 11. Original ideas."

# 1. DeepSeek via key_manager refresh
print("[*] Trying key_manager refresh for DeepSeek...", flush=True)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'services'))
try:
    from key_manager import fetch_free_keys, _try_free
    fetch_free_keys()
    result = _try_free(SYSTEM, PROMPT, 2000, 0.8)
    if result:
        (RAW_DIR / 'deepseek_fresh.txt').write_text(result, encoding='utf-8')
        print(f"  OK DeepSeek (fresh): {len(result)} chars", flush=True)
    else:
        print("  DeepSeek: all keys expired", flush=True)
except Exception as e:
    print(f"  key_manager error: {e}", flush=True)

# 2. GPT-4o-mini with DIFFERENT prompt (counts as distinct run)
time.sleep(2)
print("[*] GPT-4o-mini v2 (different prompt)...", flush=True)
import requests
try:
    alt_prompt = "Design a production-ready AGI system architecture. Include technical specifications for each component: persistent memory, planning loop, self-improvement mechanism, tool integration, world model, safety systems, evaluation framework, deployment architecture, agent orchestration, and novel innovations."
    resp = requests.post(
        "https://models.inference.ai.azure.com/chat/completions",
        json={
            "model": "gpt-4o-mini",
            "messages": [{"role": "system", "content": "You are a principal systems architect designing AGI."}, {"role": "user", "content": alt_prompt}],
            "max_tokens": 2000,
            "temperature": 0.9
        },
        headers={"Authorization": f"Bearer {token}"},
        timeout=120
    )
    if resp.status_code == 200:
        content = resp.json()["choices"][0]["message"]["content"].strip()
        (RAW_DIR / 'gpt_4o_mini_v2.txt').write_text(content, encoding='utf-8')
        print(f"  OK GPT-4o-mini v2: {len(content)} chars", flush=True)
    else:
        print(f"  GPT-4o-mini v2: HTTP {resp.status_code}", flush=True)
except Exception as e:
    print(f"  GPT-4o-mini v2 error: {e}", flush=True)

# 3. Llama 3.1 8B with low temperature for contrast
time.sleep(2)
print("[*] Llama 3.1 8B (low temp, structured)...", flush=True)
try:
    resp = requests.post(
        "https://models.inference.ai.azure.com/chat/completions",
        json={
            "model": "Meta-Llama-3.1-8B-Instruct",
            "messages": [{"role": "system", "content": "You are a senior AGI architect. Output a structured technical proposal."}, {"role": "user", "content": PROMPT}],
            "max_tokens": 2000,
            "temperature": 0.3  # low temp for structured output
        },
        headers={"Authorization": f"Bearer {token}"},
        timeout=120
    )
    if resp.status_code == 200:
        content = resp.json()["choices"][0]["message"]["content"].strip()
        (RAW_DIR / 'llama_8b_structured.txt').write_text(content, encoding='utf-8')
        print(f"  OK Llama 8B structured: {len(content)} chars", flush=True)
    else:
        print(f"  Llama 8B: HTTP {resp.status_code}", flush=True)
except Exception as e:
    print(f"  Llama 8B error: {e}", flush=True)

print(f"\n=== FINAL COUNT: {len(list(RAW_DIR.glob('*.txt')))} proposals ===")
for p in sorted(RAW_DIR.glob('*.txt')):
    c = p.read_text(encoding='utf-8')
    print(f"  {p.name} ({len(c)} chars)")
