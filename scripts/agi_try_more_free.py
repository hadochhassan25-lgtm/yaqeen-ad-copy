#!/usr/bin/env python3
"""Try more free LLM APIs for AGI collection"""
import sys, os, io, json, time
from pathlib import Path
import requests

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

RAW_DIR = Path(__file__).resolve().parent.parent / 'research' / 'ai_generated_agi_architectures' / 'raw_outputs'
RAW_DIR.mkdir(parents=True, exist_ok=True)

SYSTEM = "You are a senior AGI architect."
PROMPT = "Propose a detailed AGI architecture covering: 1. Memory 2. Reasoning/planning 3. Learning 4. Tool use 5. World model 6. Safety 7. Evaluation 8. Runtime 9. Multi-agent 10. Feasibility 11. Original ideas."

def try_endpoint(name, url, payload_builder, headers=None, timeout=30):
    print(f"[*] {name}...", flush=True)
    try:
        payload = payload_builder()
        resp = requests.post(url, json=payload, headers=headers or {}, timeout=timeout)
        if resp.status_code == 200:
            return resp.json()
        print(f"  HTTP {resp.status_code}", flush=True)
    except Exception as e:
        print(f"  Error: {e}", flush=True)
    return None

# Try multiple free endpoints
results = []

# 1. cloudflare ai (free, no key for some models)
r = try_endpoint("Cloudflare AI (Llama)", "https://api.cloudflare.com/client/v4/ai/run/@cf/meta-llama/llama-3.1-8b-instruct",
    lambda: {"messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": PROMPT}]})
if r:
    text = ""
    if isinstance(r, dict):
        text = r.get("result", {}).get("response", json.dumps(r))
    if text:
        (RAW_DIR / 'cloudflare_llama.txt').write_text(str(text), encoding='utf-8')
        results.append("cloudflare_llama")

# 2. Groq free tier (no key needed for some models?)
time.sleep(1)
r = try_endpoint("Groq (Mixtral)", "https://api.groq.com/openai/v1/chat/completions",
    lambda: {"model": "mixtral-8x7b-32768", "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": PROMPT}], "max_tokens": 2000})
if r:
    text = r.get("choices", [{}])[0].get("message", {}).get("content", "")
    if text:
        (RAW_DIR / 'groq_mixtral.txt').write_text(text, encoding='utf-8')
        results.append("groq_mixtral")

# 3. OctoAI free trial
time.sleep(1)
r = try_endpoint("OctoAI (Llama)", "https://text.octoai.run/v1/chat/completions",
    lambda: {"model": "meta-llama-3.1-8b-instruct", "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": PROMPT}], "max_tokens": 2000})
if r:
    text = r.get("choices", [{}])[0].get("message", {}).get("content", "")
    if text:
        (RAW_DIR / 'octoai_llama.txt').write_text(text, encoding='utf-8')
        results.append("octoai_llama")

# 4. Fireworks AI (free tier)
time.sleep(1)
r = try_endpoint("Fireworks (Llama)", "https://api.fireworks.ai/inference/v1/chat/completions",
    lambda: {"model": "accounts/fireworks/models/llama-v3p1-8b-instruct", "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": PROMPT}], "max_tokens": 2000})
if r:
    text = r.get("choices", [{}])[0].get("message", {}).get("content", "")
    if text:
        (RAW_DIR / 'fireworks_llama.txt').write_text(text, encoding='utf-8')
        results.append("fireworks_llama")

# 5. Lepton AI (free)
time.sleep(1)
r = try_endpoint("Lepton (Llama)", "https://llama3-1-8b.lepton.run/api/v1/chat/completions",
    lambda: {"model": "llama3-1-8b", "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": PROMPT}], "max_tokens": 2000})
if r:
    text = r.get("choices", [{}])[0].get("message", {}).get("content", "")
    if text:
        (RAW_DIR / 'lepton_llama.txt').write_text(text, encoding='utf-8')
        results.append("lepton_llama")

print(f"\nResults: {len(results)} new proposals")
for r in results:
    print(f"  + {r}")
print(f"\nTotal: {len(list(RAW_DIR.glob('*.txt')))} proposals")
