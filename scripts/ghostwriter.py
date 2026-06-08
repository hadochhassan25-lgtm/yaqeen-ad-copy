#!/usr/bin/env python3
"""
YAQEEN Ghostwriter — AI-powered LinkedIn/X content generation service
Generates 30 days of content in one API call.
Usage: python scripts/ghostwriter.py <client_name> <industry>
"""
import requests, json, sys, os, io, re
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = Path(__file__).resolve().parent.parent

GH_TOKEN = os.environ.get('GITHUB_TOKEN', '')
if not GH_TOKEN:
    env_path = BASE / '.env'
    if env_path.exists():
        for line in env_path.read_text().split('\n'):
            if line.startswith('GITHUB_TOKEN=') or line.startswith('GH_TOKEN='):
                GH_TOKEN = line.split('=', 1)[1].strip()

INDUSTRY_PROMPTS = {
    "tech": {
        "topics": ["AI transformation", "scaling infrastructure", "developer experience", "tech leadership"],
        "tone": "authoritative, forward-looking, data-driven"
    },
    "marketing": {
        "topics": ["growth strategies", "content marketing", "conversion optimization", "brand building"],
        "tone": "practical, results-oriented, generous"
    },
    "saas": {
        "topics": ["product-led growth", "customer success", "fundraising", "go-to-market"],
        "tone": "strategic, metrics-aware, founder-perspective"
    },
    "consulting": {
        "topics": ["client acquisition", "delivery excellence", "thought leadership", "scaling services"],
        "tone": "authoritative, experience-backed, actionable"
    }
}

def generate_month(client_name, industry):
    info = INDUSTRY_PROMPTS[industry]
    types = ["thought_leadership", "industry_opinion", "personal_story", "tip_tutorial", "trend_analysis", "thread_opener"]
    system = f"You are a LinkedIn ghostwriter for {client_name}, a {industry} leader. Your tone: {info['tone']}."
    prompt = (
        f"Write 30 LinkedIn posts for {client_name}, one per day for a month. "
        f"Each post: 150-250 words, hook + insight + engagement call. "
        f"Topics cycle through: {', '.join(info['topics'])}. "
        f"Types cycle through: {', '.join(types)}. "
        f"Format as JSON array: [{{\"day\":1,\"type\":\"...\",\"topic\":\"...\",\"body\":\"...\"}}, ...]"
    )
    try:
        resp = requests.post(
            "https://models.inference.ai.azure.com/chat/completions",
            json={"model": "gpt-4o-mini", "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ], "max_tokens": 4000, "temperature": 0.7},
            headers={"Authorization": f"Bearer {GH_TOKEN}"},
            timeout=120
        )
        if resp.status_code == 200:
            raw = resp.json()["choices"][0]["message"]["content"].strip()
            m = re.search(r'\[.*\]', raw, re.DOTALL)
            if m:
                return json.loads(m.group(0))
            print(f"Raw: {raw[:500]}", flush=True)
    except Exception as e:
        print(f"Error: {e}", flush=True)
    return None

def export_markdown(posts, client_name):
    md = f"# {client_name} — 30-Day Content Calendar\n\n"
    for p in posts:
        md += f"## Day {p['day']}: {p.get('type','post').replace('_',' ').title()}\n"
        md += f"**Topic**: {p.get('topic','')}\n\n"
        md += f"{p.get('body', p.get('post', ''))}\n\n---\n\n"
    return md

def main():
    if len(sys.argv) < 3:
        print("Usage: python scripts/ghostwriter.py <client_name> <industry>")
        print("Industries: tech, marketing, saas, consulting")
        sys.exit(1)
    client_name = sys.argv[1]
    industry = sys.argv[2].lower()
    if industry not in INDUSTRY_PROMPTS:
        print(f"Unknown industry. Choose from: {', '.join(INDUSTRY_PROMPTS.keys())}")
        sys.exit(1)
    posts = generate_month(client_name, industry)
    if not posts:
        print("Generation failed")
        sys.exit(1)
    output = export_markdown(posts, client_name)
    safe = client_name.lower().replace(" ","_")
    out_file = BASE / 'memory' / f'ghostwriter_{safe}_30day.md'
    out_file.write_text(output, encoding='utf-8')
    print(f"✅ {len(posts)} posts generated for {client_name}")
    print(f"📄 {out_file}")
    print(f"💰 Value: $500-$1,500/month")

if __name__ == '__main__':
    main()
