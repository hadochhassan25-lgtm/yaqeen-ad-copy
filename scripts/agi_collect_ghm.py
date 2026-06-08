#!/usr/bin/env python3
"""Collect AGI proposals from all available GitHub Models"""
import sys, os, io, json, time
from pathlib import Path
import requests

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

if not token:
    print("[!] No GITHUB_TOKEN found")
    sys.exit(1)

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

MODELS = [
    ("gpt-4o-mini", "GPT-4o-mini (OpenAI)", 3000),
    ("gpt-4o", "GPT-4o (OpenAI)", 3000),
    ("Meta-Llama-3.1-405B-Instruct", "Llama 3.1 405B (Meta)", 2000),
    ("Meta-Llama-3.1-8B-Instruct", "Llama 3.1 8B (Meta)", 2000),
]

GH_BASE = "https://models.inference.ai.azure.com"
HEADERS = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

def save_raw(model_name, content):
    safe_name = model_name.lower().replace(' ', '_').replace('/', '_').replace('-', '_')
    path = RAW_DIR / f'{safe_name}.txt'
    path.write_text(content, encoding='utf-8')
    print(f"  -> {path.name} ({len(content)} chars)")

for model_id, display_name, max_tok in MODELS:
    print(f"\n[*] {display_name} ({model_id})...", flush=True)
    try:
        resp = requests.post(
            f"{GH_BASE}/chat/completions",
            json={
                "model": model_id,
                "messages": [
                    {"role": "system", "content": SYSTEM},
                    {"role": "user", "content": PROMPT}
                ],
                "max_tokens": max_tok,
                "temperature": 0.8
            },
            headers=HEADERS,
            timeout=120
        )
        if resp.status_code == 200:
            content = resp.json()["choices"][0]["message"]["content"].strip()
            save_raw(model_id, content)
        else:
            print(f"  [!] HTTP {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        print(f"  [!] Error: {e}")
    time.sleep(1)

print(f"\n{'='*50}")
print(f"Total proposals in {RAW_DIR}: {len(list(RAW_DIR.glob('*.txt')))}")
for p in sorted(RAW_DIR.glob('*.txt')):
    print(f"  {p.name}")
