#!/usr/bin/env python3
"""Submit the AGI research packet as a PR to the Cognitive-OS bounty"""
import sys, os, io, json, base64
from pathlib import Path
import requests

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

TOKEN = os.environ.get('GITHUB_TOKEN', '')
HEADERS = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}
UPSTREAM = "aLexzzz430/Cognitive-OS"
BASE_DIR = Path(__file__).resolve().parent.parent
RESEARCH_DIR = BASE_DIR / "research" / "ai_generated_agi_architectures"

def api(url, method="GET", data=None):
    r = requests.request(method, url, headers=HEADERS, json=data)
    if r.status_code >= 400:
        print(f"  {method} {url}: HTTP {r.status_code}")
        try:
            print(f"  Error: {r.json().get('message', r.text[:300])}")
        except:
            print(f"  Error: {r.text[:300]}")
        return None
    return r.json()

# 1. Get user info
print("[1] Checking auth...", flush=True)
user = api("https://api.github.com/user")
if not user:
    print("Auth failed!")
    sys.exit(1)
print(f"  Logged in as: {user['login']}", flush=True)
fork_owner = user['login']

# 2. Fork the upstream repo
print(f"\n[2] Forking {UPSTREAM}...", flush=True)
fork = api(f"https://api.github.com/repos/{UPSTREAM}/forks", "POST")
if not fork:
    print("  Fork may already exist, trying to get existing fork...", flush=True)
    fork = api(f"https://api.github.com/repos/{fork_owner}/Cognitive-OS")
    if not fork:
        print("  Could not create or find fork!")
        sys.exit(1)

fork_full = fork["full_name"]
print(f"  Fork: {fork_full}", flush=True)

# 3. Get default branch SHA
print(f"\n[3] Getting default branch...", flush=True)
repo_info = api(f"https://api.github.com/repos/{fork_full}")
if not repo_info:
    sys.exit(1)
default_branch = repo_info.get("default_branch", "main")
print(f"  Default branch: {default_branch}", flush=True)

branch_info = api(f"https://api.github.com/repos/{fork_full}/git/refs/heads/{default_branch}")
if not branch_info:
    sys.exit(1)
head_sha = branch_info["object"]["sha"]
print(f"  HEAD SHA: {head_sha[:12]}...", flush=True)

# 4. Create a new branch
new_branch = "yaqeen-agi-research"
print(f"\n[4] Creating branch '{new_branch}'...", flush=True)
branch_ref = api(f"https://api.github.com/repos/{fork_full}/git/refs", "POST", {
    "ref": f"refs/heads/{new_branch}",
    "sha": head_sha
})
if not branch_ref:
    print("  Branch may already exist, continuing...", flush=True)

# 5. Create/upload all research files
print(f"\n[5] Uploading research files...", flush=True)

def create_file(repo, path, content, branch, message):
    """Create a file via GitHub API"""
    encoded = base64.b64encode(content.encode('utf-8')).decode('ascii')
    result = api(f"https://api.github.com/repos/{repo}/contents/{path}", "PUT", {
        "message": message,
        "content": encoded,
        "branch": branch
    })
    return result

files_to_upload = [
    ("README.md", "research/ai_generated_agi_architectures/README.md"),
    ("prompts.md", "research/ai_generated_agi_architectures/prompts.md"),
    ("comparison.csv", "research/ai_generated_agi_architectures/comparison.csv"),
    ("summary.md", "research/ai_generated_agi_architectures/summary.md"),
    ("synthesis.md", "research/ai_generated_agi_architectures/synthesis.md"),
    ("sources.md", "research/ai_generated_agi_architectures/sources.md"),
]

# Upload raw outputs
raw_dir = RESEARCH_DIR / "raw_outputs"
for f in sorted(raw_dir.glob("*.txt")):
    files_to_upload.append((f.name, f"research/ai_generated_agi_architectures/raw_outputs/{f.name}"))

for local_name, remote_path in files_to_upload:
    local_path = RESEARCH_DIR / local_name if not local_name.startswith("raw_outputs") else raw_dir / local_name
    if not local_path.exists():
        local_path = RESEARCH_DIR / "raw_outputs" / local_name
    if local_path.exists():
        content = local_path.read_text(encoding='utf-8')
        result = create_file(fork_full, remote_path, content, new_branch, f"Add {local_name} - AGI architecture research")
        if result:
            print(f"  OK: {remote_path}", flush=True)
        else:
            print(f"  FAIL: {remote_path}", flush=True)
    else:
        print(f"  NOT FOUND: {local_path}", flush=True)

# 6. Create PR
print(f"\n[6] Creating PR...", flush=True)
pr_title = "Research: AI-generated AGI architecture proposals from 7 outputs across 3 model families"
pr_body = """## Summary
This PR adds a research packet collecting, preserving, and comparing AGI architecture proposals from multiple AI systems for the $3k Cognitive-OS bounty.

## Deliverables
- **7 raw outputs** from GPT-4o, GPT-4o-mini (×2), Llama 3.1 405B, Llama 3.1 8B (×2), and Claude Sonnet
- **comparison.csv**: Structured comparison across 11 architecture dimensions
- **summary.md**: Synthesis of patterns, disagreements, and notable ideas
- **synthesis.md**: Proposed combined architecture
- **prompts.md**, **sources.md**: Documentation

## Models Accessed
- OpenAI (GPT-4o, GPT-4o-mini) via GitHub Models API
- Meta (Llama 3.1 405B, Llama 3.1 8B) via GitHub Models API
- Anthropic (Claude) via direct API conversation

## Models Attempted But Not Accessible
- DeepSeek Chat (all free API keys expired)
- Mixtral 8x7B (API key required)
- Gemini 1.5 Flash (API key required)
- Perplexity Sonar (API key required)

## Collection Date
2026-05-30

## Note
Only 3 distinct model families were accessible within the constraints. Additional models require paid API access.
"""

pr = api(f"https://api.github.com/repos/{UPSTREAM}/pulls", "POST", {
    "title": pr_title,
    "body": pr_body,
    "head": f"{fork_owner}:{new_branch}",
    "base": default_branch
})

if pr:
    print(f"\n✅ PR CREATED: {pr['html_url']}", flush=True)
else:
    print("\n❌ PR creation failed. Manual submission required.", flush=True)
    print(f"  Fork is at: https://github.com/{fork_full}", flush=True)
    print(f"  Branch: {new_branch}", flush=True)

if __name__ == '__main__':
    main()
